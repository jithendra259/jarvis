'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { ChatMessage, ActivityEvent, SystemStatus, ConfirmationInfo } from '@/lib/jarvis-api';
import { useJarvisWebSocket } from '@/hooks/useJarvisWebSocket';
import {
  sendChat,
  confirmAction,
  fetchSystemStatus,
  fetchHealth,
  fetchModels,
  selectModel,
} from '@/lib/jarvis-api';
import { ChatPanel, ChatPanelRef } from '@/components/jarvis/ChatPanel';
import { StatusBar } from '@/components/jarvis/StatusBar';
import { ModelSelector } from '@/components/jarvis/ModelSelector';
import { Button } from '@/components/ui/primitives/button';
import { cn } from '@/lib/utils';

export default function Dashboard() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activityEvents, setActivityEvents] = useState<ActivityEvent[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [llmOnline, setLlmOnline] = useState(false);
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('auto/best-chat');
  const [loadingModels, setLoadingModels] = useState(false);
  const [sending, setSending] = useState(false);
  const [pendingConfirmation, setPendingConfirmation] = useState<ConfirmationInfo | null>(null);
  const [thinkingText, setThinkingText] = useState<string | undefined>(undefined);
  const conversationId = 'default';
  const chatPanelRef = useRef<ChatPanelRef>(null);

  const handleEvent = useCallback((event: ActivityEvent) => {
    setActivityEvents((prev) => [...prev, event]);

    // Handle specific events
    if (event.type === 'agent.thinking') {
      setThinkingText(event.message || 'Analyzing query, formulating execution plan...');
    } else if (event.type === 'agent.planned') {
      setThinkingText(event.plan || event.message || 'Executing plan...');
    } else if (event.type === 'tool.started') {
      setThinkingText(`Calling tool: ${event.tool || 'system'}...`);
    } else if (event.type === 'agent.completed' || event.type === 'agent.response') {
      setSending(false);
      setThinkingText(undefined);
      const replyContent = (event.reply as string) || (event.type === 'agent.response' ? (event.message as string) : undefined);
      if (replyContent) {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last && last.role === 'assistant' && last.content === replyContent) {
            return prev;
          }
          return [
            ...prev,
            {
              role: 'assistant',
              content: replyContent,
              timestamp: new Date().toISOString(),
              actions: (event.actions || event.tool_history) as any,
              plan: event.plan as string | undefined,
              observations: event.observations as any,
            },
          ];
        });
      }
      setTimeout(() => chatPanelRef.current?.scrollToBottom(), 50);
    } else if (event.type === 'agent.error') {
      setSending(false);
      setThinkingText(undefined);
      // Add error as a message
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${event.message || 'Unknown error'}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } else if (event.type === 'confirmation.required') {
      setPendingConfirmation({
        id: event.confirmation_id as string,
        tool: event.tool as string,
        arguments: (event.arguments as Record<string, unknown>) || {},
        permission_level: event.permission_level as string,
        reason: event.reason as string,
      });
    } else if (event.type === 'confirmation.resolved' || event.type === 'agent.cancelled') {
      setPendingConfirmation(null);
    }
  }, []);

  const { connected, error: wsError, sendMessage, selectModelWs, sendConfirm } = useJarvisWebSocket(
    handleEvent,
    conversationId
  );

  const loadModels = useCallback(() => {
    setLoadingModels(true);
    fetchModels()
      .then((data) => {
        if (data?.models && Array.isArray(data.models)) {
          setModels(data.models);
        }
        if (data?.current_model) {
          setSelectedModel(data.current_model);
        }
      })
      .catch(() => {
        // Fallback to basic list if offline
        setModels([
          'auto/best-chat',
          'auto/best-fast',
          'auto/best-coding',
          'auto/best-reasoning',
          'auto/best-free',
        ]);
      })
      .finally(() => setLoadingModels(false));
  }, []);

  const handleSelectModel = useCallback(
    async (model: string) => {
      setSelectedModel(model);
      try {
        selectModelWs(model);
        await selectModel(model);
      } catch (err) {
        console.warn('Could not persist model selection:', err);
      }
    },
    [selectModelWs]
  );

  const checkHealthAndStatus = useCallback(() => {
    fetchHealth()
      .then((data: any) => {
        const isOnline = Boolean(data?.llm?.online ?? data?.llm_online ?? false);
        setLlmOnline(isOnline);
        if (data?.llm?.model) {
          setSelectedModel((prev) => (prev ? prev : data.llm.model));
        }
      })
      .catch(() => setLlmOnline(false));

    fetchSystemStatus()
      .then((status) => {
        setSystemStatus(status);
        if (status?.services && Array.isArray(status.services)) {
          const anyOnline = status.services.some((s) => s.online);
          if (anyOnline) {
            setLlmOnline(true);
          }
          const allSvcModels = status.services.flatMap((s) => s.models || []);
          if (allSvcModels.length > 0) {
            setModels((prev) => (prev.length === 0 ? allSvcModels : prev));
          }
        }
      })
      .catch(() => setSystemStatus(null));
  }, []);

  // Initial health check and model loading
  useEffect(() => {
    checkHealthAndStatus();
    loadModels();

    // Refresh health and system status periodically
    const interval = setInterval(() => {
      checkHealthAndStatus();
    }, 10000);

    return () => clearInterval(interval);
  }, [checkHealthAndStatus, loadModels]);

  const handleSendMessage = useCallback(
    async (message: string) => {
      setSending(true);
      const userMsg: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setPendingConfirmation(null);

      try {
        if (connected) {
          sendMessage(message, selectedModel);
        } else {
          const resp = await sendChat(message, conversationId, selectedModel);
          setSending(false);
          setThinkingText(undefined);
          if (resp?.content) {
            setMessages((prev) => [...prev, resp]);
          }
        }
      } catch (err) {
        setSending(false);
        setThinkingText(undefined);
        console.error('Failed to send message:', err);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `Failed to send: ${err instanceof Error ? err.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    },
    [connected, sendMessage, selectedModel, conversationId]
  );

  const handleConfirm = useCallback(
    async (actionId: string, approved: boolean) => {
      setSending(true);
      try {
        sendConfirm(actionId, approved);
        // Response comes via WebSocket
      } catch (err) {
        setSending(false);
        console.error('Failed to confirm:', err);
      }
    },
    [sendConfirm]
  );

  return (
    <div className="h-screen flex flex-col bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/30 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">J</span>
          </div>
          <div>
            <h1 className="text-lg font-mono font-bold tracking-tight">JARVIS</h1>
            <p className="text-xs text-white/50">Local Desktop AI Assistant</p>
          </div>
        </div>

        <div className="flex items-center gap-3 sm:gap-4">
          {/* Model Selector Dropdown */}
          <ModelSelector
            models={models}
            selectedModel={selectedModel}
            onSelectModel={handleSelectModel}
            onRefresh={loadModels}
            isLoading={loadingModels}
          />

          <div className="hidden sm:flex items-center gap-2 text-xs">
            <span
              className={cn(
                'w-2 h-2 rounded-full',
                llmOnline ? 'bg-green-400' : 'bg-red-400'
              )}
            />
            <span className="font-mono">{llmOnline ? 'LLM Online' : 'LLM Offline'}</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span
              className={cn(
                'w-2 h-2 rounded-full',
                connected ? 'bg-cyan-400' : 'bg-gray-400'
              )}
            />
            <span className="font-mono">{connected ? 'WS Connected' : 'WS Disconnected'}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden p-4 gap-4">
        {/* Left Column - Chat */}
        <div className="flex-1 flex flex-col min-w-0 h-full">
          <ChatPanel
            ref={chatPanelRef}
            messages={messages}
            onSendMessage={handleSendMessage}
            onConfirm={handleConfirm}
            disabled={sending}
            thinkingContent={thinkingText}
            pendingConfirmation={pendingConfirmation}
            events={activityEvents}
          />
        </div>

        {/* Right Column - Status */}
        <div className="w-80 flex-shrink-0 flex flex-col gap-4">
          <StatusBar
            status={systemStatus}
            wsConnected={connected}
            llmOnline={llmOnline}
          />

          <div className="flex-1 bg-black/20 rounded-lg border border-white/10 p-3 overflow-y-auto">
            <h3 className="text-xs font-mono text-white/70 uppercase tracking-wider mb-3">
              Quick Actions
            </h3>
            <div className="space-y-2">
              {[
                'Open Notepad',
                'Open Calculator',
                'Open VS Code',
                'Open Terminal',
                'Open File Explorer',
              ].map((cmd) => (
                <Button
                  key={cmd}
                  variant="outline"
                  className="w-full justify-start text-left text-xs"
                  onClick={() => handleSendMessage(cmd)}
                  disabled={sending}
                >
                  {cmd}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </main>

      {wsError && (
        <div className="fixed bottom-4 right-4 bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-2 rounded text-sm font-mono">
          {wsError}
        </div>
      )}
    </div>
  );
}