'use client';

import { useImperativeHandle, forwardRef, useRef } from 'react';
import { ChatMessage, ConfirmationInfo } from '@/lib/jarvis-api';
import { AIAssistantInterface } from '@/components/ui/ai-assistant-interface';

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  onConfirm: (actionId: string, approved: boolean) => void;
  disabled?: boolean;
  thinkingContent?: string;
  pendingConfirmation?: ConfirmationInfo | null;
}

export interface ChatPanelRef {
  scrollToBottom: () => void;
}

export const ChatPanel = forwardRef<ChatPanelRef, ChatPanelProps>(
  ({ messages, onSendMessage, onConfirm, disabled, thinkingContent, pendingConfirmation }, ref) => {
    const containerRef = useRef<HTMLDivElement>(null);

    useImperativeHandle(ref, () => ({
      scrollToBottom: () => {
        if (containerRef.current) {
          containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
      },
    }));

    return (
      <div ref={containerRef} className="flex-1 flex flex-col h-full overflow-hidden">
        <AIAssistantInterface
          messages={messages}
          onSendMessage={onSendMessage}
          onConfirm={onConfirm}
          disabled={disabled}
          thinkingContent={thinkingContent}
          pendingConfirmation={pendingConfirmation}
        />
      </div>
    );
  }
);

ChatPanel.displayName = 'ChatPanel';