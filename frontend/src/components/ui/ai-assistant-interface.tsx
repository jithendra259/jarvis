"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Search,
  Mic,
  ArrowUp,
  Plus,
  FileText,
  Code,
  BookOpen,
  PenTool,
  BrainCircuit,
  Sparkles,
  User,
  Bot,
  Terminal,
  CheckCircle2,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { LiveKitVoiceModal } from "@/components/voice/livekit-voice-modal";

interface ChatMessage {
  id: string;
  sender: "user" | "jarvis";
  text: string;
  actions?: Array<{
    tool: string;
    arguments: string;
    result: any;
  }>;
  timestamp: string;
}

export function AIAssistantInterface() {
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchEnabled, setSearchEnabled] = useState(false);
  const [deepResearchEnabled, setDeepResearchEnabled] = useState(false);
  const [reasonEnabled, setReasonEnabled] = useState(false);
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);
  const [activeCommandCategory, setActiveCommandCategory] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const commandSuggestions = {
    learn: [
      "Explain quantum computing simply",
      "How does the human brain process language?",
      "What are black holes?",
    ],
    code: [
      "Open VS Code",
      "Write a Python function to sort a list",
      "Create a React component for a todo list",
    ],
    write: [
      "Open Notepad",
      "Write a professional email confirming a meeting",
      "Draft a project roadmap outline",
    ],
  };

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const sendPrompt = async (promptText: string) => {
    if (!promptText.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      text: promptText,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    setIsLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: promptText }),
      });

      if (res.ok) {
        const data = await res.json();
        const jarvisMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: "jarvis",
          text: data.reply,
          actions: data.actions || [],
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, jarvisMsg]);
      } else {
        const jarvisMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: "jarvis",
          text: "Could not reach Jarvis backend on http://127.0.0.1:8000.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        };
        setMessages((prev) => [...prev, jarvisMsg]);
      }
    } catch (err: any) {
      const jarvisMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "jarvis",
        text: `Error connecting to Jarvis engine: ${err.message}. Ensure backend is running.`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, jarvisMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommandSelect = (cmd: string) => {
    setActiveCommandCategory(null);
    sendPrompt(cmd);
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* Top Navbar */}
      <header className="sticky top-0 z-20 border-b border-gray-100 bg-white/80 backdrop-blur-md px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-md shadow-blue-500/20">
            J
          </div>
          <div>
            <h2 className="font-semibold text-sm text-gray-900 leading-none">Jarvis Desktop</h2>
            <span className="text-[11px] text-gray-500">Local AI Agent • OmniRoute</span>
          </div>
        </div>

        {/* LiveKit Voice Trigger Button */}
        <button
          onClick={() => setIsVoiceOpen(true)}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 text-xs font-medium transition shadow-sm"
        >
          <Mic className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
          <span>LiveKit Voice Room</span>
        </button>
      </header>

      {/* Main Conversation Stream */}
      <main className="flex-1 max-w-3xl w-full mx-auto p-4 flex flex-col justify-between">
        {/* Welcome State (Shown only when no messages yet) */}
        {!hasMessages && (
          <div className="flex-1 flex flex-col items-center justify-center py-10">
            <div className="mb-6 w-16 h-16 relative">
              <div className="w-full h-full rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <Sparkles className="w-8 h-8 text-white animate-spin-slow" />
              </div>
            </div>

            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-400 mb-2 text-center">
              How can I help you today?
            </h1>
            <p className="text-gray-500 text-sm max-w-md text-center mb-8">
              Ask questions, write documents, or control your computer with local tools.
            </p>

            {/* Quick Command categories */}
            <div className="w-full grid grid-cols-3 gap-3 mb-6">
              <CommandButton
                icon={<BookOpen className="w-4 h-4" />}
                label="Learn"
                isActive={activeCommandCategory === "learn"}
                onClick={() => setActiveCommandCategory(activeCommandCategory === "learn" ? null : "learn")}
              />
              <CommandButton
                icon={<Code className="w-4 h-4" />}
                label="Apps & Code"
                isActive={activeCommandCategory === "code"}
                onClick={() => setActiveCommandCategory(activeCommandCategory === "code" ? null : "code")}
              />
              <CommandButton
                icon={<PenTool className="w-4 h-4" />}
                label="Write"
                isActive={activeCommandCategory === "write"}
                onClick={() => setActiveCommandCategory(activeCommandCategory === "write" ? null : "write")}
              />
            </div>

            {/* Command Suggestions Dropdown */}
            <AnimatePresence>
              {activeCommandCategory && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="w-full mb-6 overflow-hidden"
                >
                  <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                    <ul className="divide-y divide-gray-100">
                      {commandSuggestions[activeCommandCategory as keyof typeof commandSuggestions].map(
                        (suggestion, index) => (
                          <li
                            key={index}
                            onClick={() => handleCommandSelect(suggestion)}
                            className="p-3 hover:bg-blue-50/50 cursor-pointer transition flex items-center gap-3 text-sm text-gray-700"
                          >
                            <span className="text-blue-500 font-bold">›</span>
                            <span>{suggestion}</span>
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}

        {/* Message Thread (Chat Stream) */}
        {hasMessages && (
          <div className="flex-1 overflow-y-auto space-y-4 py-4 pr-1">
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.sender === "jarvis" && (
                  <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-sm">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-2xl p-4 shadow-sm ${
                    msg.sender === "user"
                      ? "bg-blue-600 text-white rounded-br-none"
                      : "bg-gray-50 border border-gray-200/80 text-gray-800 rounded-bl-none"
                  }`}
                >
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>

                  {/* Actions / Tools Executed Badge */}
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-gray-200/60 flex flex-col gap-1.5">
                      {msg.actions.map((act, i) => (
                        <div
                          key={i}
                          className="flex items-center gap-2 text-xs bg-white/90 border border-gray-200 rounded-lg px-2.5 py-1 text-gray-700"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span className="font-medium text-gray-900">{act.tool}:</span>
                          <span className="font-mono text-[11px] text-gray-500">{act.result?.message || "Executed"}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <span
                    className={`block text-[10px] mt-1.5 ${
                      msg.sender === "user" ? "text-blue-100 text-right" : "text-gray-400"
                    }`}
                  >
                    {msg.timestamp}
                  </span>
                </div>

                {msg.sender === "user" && (
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </motion.div>
            ))}

            {/* Thinking / Tool Execution Indicator */}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-3"
              >
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white shrink-0 shadow-sm">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-gray-50 border border-gray-200 rounded-2xl rounded-bl-none px-4 py-3 flex items-center gap-2 text-gray-500 text-sm">
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  <span>Jarvis is thinking...</span>
                </div>
              </motion.div>
            )}

            <div ref={chatBottomRef} />
          </div>
        )}

        {/* Input Bar */}
        <div className="sticky bottom-0 bg-white/95 backdrop-blur-md pt-2 pb-4">
          <div className="w-full bg-white border border-gray-200 rounded-2xl shadow-sm focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all overflow-hidden">
            <div className="p-3">
              <input
                ref={inputRef}
                type="text"
                placeholder="Ask Jarvis anything or type 'Open VS Code'..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    sendPrompt(inputValue);
                  }
                }}
                className="w-full text-gray-800 text-sm outline-none placeholder:text-gray-400 bg-transparent"
              />
            </div>

            {/* Footer Buttons */}
            <div className="px-3 py-2 flex items-center justify-between border-t border-gray-100 bg-gray-50/50">
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setSearchEnabled(!searchEnabled)}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                    searchEnabled ? "bg-blue-100 text-blue-700" : "text-gray-500 hover:bg-gray-200/60"
                  }`}
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>Search</span>
                </button>
                <button
                  onClick={() => setReasonEnabled(!reasonEnabled)}
                  className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                    reasonEnabled ? "bg-blue-100 text-blue-700" : "text-gray-500 hover:bg-gray-200/60"
                  }`}
                >
                  <BrainCircuit className="w-3.5 h-3.5" />
                  <span>Reason</span>
                </button>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsVoiceOpen(true)}
                  className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition"
                  title="Open LiveKit Realtime Voice"
                >
                  <Mic className="w-4 h-4 text-blue-600" />
                </button>

                <button
                  onClick={() => sendPrompt(inputValue)}
                  disabled={!inputValue.trim() || isLoading}
                  className={`w-7 h-7 flex items-center justify-center rounded-full transition-colors ${
                    inputValue.trim() && !isLoading
                      ? "bg-blue-600 text-white hover:bg-blue-700 shadow-sm"
                      : "bg-gray-200 text-gray-400 cursor-not-allowed"
                  }`}
                >
                  <ArrowUp className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* LiveKit Voice Assistant Modal with Visualizer & Controls */}
      <LiveKitVoiceModal
        isOpen={isVoiceOpen}
        onClose={() => setIsVoiceOpen(false)}
      />
    </div>
  );
}

interface CommandButtonProps {
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  onClick: () => void;
}

function CommandButton({ icon, label, isActive, onClick }: CommandButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      className={`flex items-center justify-center gap-2 p-3 rounded-xl border transition-all text-xs font-medium ${
        isActive
          ? "bg-blue-50 border-blue-200 text-blue-700 shadow-sm"
          : "bg-white border-gray-200 text-gray-700 hover:border-gray-300"
      }`}
    >
      {icon}
      <span>{label}</span>
    </motion.button>
  );
}
