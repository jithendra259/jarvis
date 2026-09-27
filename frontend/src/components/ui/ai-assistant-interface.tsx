"use client";

import * as React from "react";
import { useState, useRef, useEffect, useMemo } from "react";
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
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import AIThinkingBlock from "@/components/ui/ai-thinking-block";
import { ThinkingState, type TraceNode } from "@/components/ui/ai-agent-response";

export interface AIAssistantInterfaceProps {
  messages?: Array<{
    role: "user" | "assistant";
    content: string;
    timestamp?: string;
    actions?: Array<{
      tool: string;
      arguments?: Record<string, unknown>;
      result?: Record<string, unknown>;
    }>;
  }>;
  onSendMessage?: (message: string) => void;
  disabled?: boolean;
  thinkingContent?: string;
  pendingConfirmation?: {
    id: string;
    tool: string;
    reason: string;
    permission_level?: string;
    arguments?: Record<string, unknown>;
  } | null;
  onConfirm?: (actionId: string, approved: boolean) => void;
  events?: Array<{
    type: string;
    timestamp?: string;
    tool?: string;
    arguments?: Record<string, unknown>;
    message?: string;
    plan?: string;
    result?: Record<string, unknown>;
    duration_ms?: number;
    [key: string]: unknown;
  }>;
}

function mapEventsToTrace(events: any[] = []): TraceNode[] {
  return events
    .filter(
      (e) =>
        e &&
        e.type !== "system.status" &&
        e.type !== "pong" &&
        e.type !== "ping"
    )
    .map((e, idx) => {
      const isTool =
        e.type === "tool.started" ||
        e.type === "tool.completed" ||
        e.type === "tool.failed";
      if (isTool) {
        const isCmd =
          e.tool === "execute_command" ||
          (e.arguments && Boolean(e.arguments.command));
        if (isCmd) {
          return {
            id: `trace-${idx}`,
            type: "terminal",
            command: (e.arguments?.command as string) || (e.tool as string),
            output:
              (e.result?.output as string) ||
              (e.message as string) ||
              undefined,
            exitCode: typeof e.result?.exit_code === "number" ? e.result.exit_code : 0,
            durationMs: e.duration_ms,
            status:
              e.type === "tool.failed"
                ? "failed"
                : e.type === "tool.completed"
                ? "completed"
                : "running",
          };
        }
        return {
          id: `trace-${idx}`,
          type: "tool",
          toolName: e.tool || "tool",
          primary: e.tool ? `Run ${e.tool}` : "Tool Execution",
          secondary: e.arguments ? JSON.stringify(e.arguments) : undefined,
          status:
            e.type === "tool.failed"
              ? "failed"
              : e.type === "tool.completed"
              ? "completed"
              : "running",
          args: e.arguments,
          result: e.result,
          details: e.message
            ? [{ text: e.message, tone: e.type === "tool.failed" ? "error" : "ctx" }]
            : undefined,
        };
      }
      if (e.type === "agent.thinking" || e.type === "agent.planned") {
        return {
          id: `trace-${idx}`,
          type: "reasoning",
          sentences: [e.plan || e.message || "Formulating execution plan..."],
          durationSeconds: e.duration_ms ? +(e.duration_ms / 1000).toFixed(1) : 1.5,
        };
      }
      return {
        id: `trace-${idx}`,
        type: "step",
        primary: e.type,
        secondary: e.message || undefined,
        status:
          e.type.includes("error") || e.type.includes("failed")
            ? "failed"
            : "completed",
      };
    });
}

export function AIAssistantInterface({
  messages,
  onSendMessage,
  disabled = false,
  thinkingContent,
  pendingConfirmation,
  onConfirm,
  events,
}: AIAssistantInterfaceProps = {}) {
  const [inputValue, setInputValue] = useState("");
  const [searchEnabled, setSearchEnabled] = useState(false);
  const [deepResearchEnabled, setDeepResearchEnabled] = useState(false);
  const [reasonEnabled, setReasonEnabled] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [showUploadAnimation, setShowUploadAnimation] = useState(false);
  const [activeCommandCategory, setActiveCommandCategory] = useState<
    string | null
  >(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const liveTrace = React.useMemo(() => mapEventsToTrace(events), [events]);

  const commandSuggestions = {
    learn: [
      "Explain the Big Bang theory",
      "How does photosynthesis work?",
      "What are black holes?",
      "Explain quantum computing",
      "How does the human brain work?",
    ],
    code: [
      "Create a React component for a todo list",
      "Write a Python function to sort a list",
      "How to implement authentication in Next.js",
      "Explain async/await in JavaScript",
      "Create a CSS animation for a button",
    ],
    write: [
      "Write a professional email to a client",
      "Create a product description for a smartphone",
      "Draft a blog post about AI",
      "Write a creative story about space exploration",
      "Create a social media post about sustainability",
    ],
  };

  useEffect(() => {
    if (messages && messages.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleUploadFile = () => {
    setShowUploadAnimation(true);

    // Simulate file upload with timeout
    setTimeout(() => {
      const newFile = `Document.pdf`;
      setUploadedFiles((prev) => [...prev, newFile]);
      setShowUploadAnimation(false);
    }, 1500);
  };

  const handleCommandSelect = (command: string) => {
    setInputValue(command);
    setActiveCommandCategory(null);

    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleSendMessage = () => {
    const trimmed = inputValue.trim();
    if (!trimmed || disabled) return;

    if (onSendMessage) {
      onSendMessage(trimmed);
    } else {
      console.log("Sending message:", trimmed);
    }
    setInputValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const hasMessages = Boolean(messages && messages.length > 0);

  return (
    <div className="min-h-full w-full flex flex-col items-center justify-between bg-white text-gray-900 rounded-xl overflow-y-auto p-6 shadow-sm">
      <div className="w-full max-w-3xl mx-auto flex-1 flex flex-col items-center justify-center">
        {/* Logo with animated gradient */}
        {!hasMessages && (
          <div className="mb-8 w-20 h-20 relative">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 200 200"
              width="100%"
              height="100%"
              className="w-full h-full"
            >
              <g clipPath="url(#cs_clip_1_ellipse-12)">
                <mask
                  id="cs_mask_1_ellipse-12"
                  style={{ maskType: "alpha" }}
                  width="200"
                  height="200"
                  x="0"
                  y="0"
                  maskUnits="userSpaceOnUse"
                >
                  <path
                    fill="#fff"
                    fillRule="evenodd"
                    d="M100 150c27.614 0 50-22.386 50-50s-22.386-50-50-50-50 22.386-50 50 22.386 50 50 50zm0 50c55.228 0 100-44.772 100-100S155.228 0 100 0 0 44.772 0 100s44.772 100 100 100z"
                    clipRule="evenodd"
                  ></path>
                </mask>
                <g mask="url(#cs_mask_1_ellipse-12)">
                  <path fill="#fff" d="M200 0H0v200h200V0z"></path>
                  <path
                    fill="#0066FF"
                    fillOpacity="0.33"
                    d="M200 0H0v200h200V0z"
                  ></path>
                  <g
                    filter="url(#filter0_f_844_2811)"
                    className="animate-gradient"
                  >
                    <path fill="#0066FF" d="M110 32H18v68h92V32z"></path>
                    <path fill="#0044FF" d="M188-24H15v98h173v-98z"></path>
                    <path fill="#0099FF" d="M175 70H5v156h170V70z"></path>
                    <path fill="#00CCFF" d="M230 51H100v103h130V51z"></path>
                  </g>
                </g>
              </g>
              <defs>
                <filter
                  id="filter0_f_844_2811"
                  width="385"
                  height="410"
                  x="-75"
                  y="-104"
                  colorInterpolationFilters="sRGB"
                  filterUnits="userSpaceOnUse"
                >
                  <feFlood floodOpacity="0" result="BackgroundImageFix"></feFlood>
                  <feBlend
                    in="SourceGraphic"
                    in2="BackgroundImageFix"
                    result="shape"
                  ></feBlend>
                  <feGaussianBlur
                    result="effect1_foregroundBlur_844_2811"
                    stdDeviation="40"
                  ></feGaussianBlur>
                </filter>
                <clipPath id="cs_clip_1_ellipse-12">
                  <path fill="#fff" d="M0 0H200V200H0z"></path>
                </clipPath>
              </defs>
              <g
                style={{ mixBlendMode: "overlay" }}
                mask="url(#cs_mask_1_ellipse-12)"
              >
                <path
                  fill="gray"
                  stroke="transparent"
                  d="M200 0H0v200h200V0z"
                  filter="url(#cs_noise_1_ellipse-12)"
                ></path>
              </g>
              <defs>
                <filter
                  id="cs_noise_1_ellipse-12"
                  width="100%"
                  height="100%"
                  x="0%"
                  y="0%"
                  filterUnits="objectBoundingBox"
                >
                  <feTurbulence
                    baseFrequency="0.6"
                    numOctaves="5"
                    result="out1"
                    seed="4"
                  ></feTurbulence>
                  <feComposite
                    in="out1"
                    in2="SourceGraphic"
                    operator="in"
                    result="out2"
                  ></feComposite>
                  <feBlend
                    in="SourceGraphic"
                    in2="out2"
                    mode="overlay"
                    result="out3"
                  ></feBlend>
                </filter>
              </defs>
            </svg>
          </div>
        )}

        {/* Welcome message */}
        {!hasMessages && (
          <div className="mb-10 text-center">
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col items-center"
            >
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-400 mb-2">
                Ready to assist you
              </h1>
              <p className="text-gray-500 max-w-md">
                Ask me anything or try one of the suggestions below
              </p>
            </motion.div>
          </div>
        )}

        {/* Live Conversation Thread when active */}
        {hasMessages && (
          <div className="w-full flex-1 overflow-y-auto mb-6 space-y-4 max-h-[50vh] pr-2">
            {messages!.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-3 ${
                  msg.role === "user" ? "flex-row-reverse" : "flex-row"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0 ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-blue-100 text-blue-700"
                  }`}
                >
                  {msg.role === "user" ? "U" : "J"}
                </div>
                <div
                  className={`max-w-[78%] rounded-2xl px-4 py-2.5 text-sm ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.actions && msg.actions.length > 0 && (
                    <details className="mt-2 text-xs opacity-75">
                      <summary className="cursor-pointer font-mono">
                        Tool executions ({msg.actions.length})
                      </summary>
                      <pre className="mt-1 p-2 bg-black/10 rounded overflow-x-auto text-[11px]">
                        {JSON.stringify(msg.actions, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            ))}
            {(disabled || reasonEnabled) && (
              <div className="flex gap-3 flex-row">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0 bg-blue-100 text-blue-700">
                  J
                </div>
                <div className="w-full max-w-[85%]">
                  <AIThinkingBlock
                    title="JARVIS is thinking"
                    content={thinkingContent}
                  />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Active thinking block when reasoning is engaged without prior messages */}
        {!hasMessages && (disabled || reasonEnabled) && (
          <div className="w-full max-w-xl mb-4">
            <AIThinkingBlock
              title="JARVIS is thinking"
              content={thinkingContent}
            />
          </div>
        )}

        {/* Real-time Agent Execution Trace & Events */}
        {liveTrace.length > 0 && (
          <div className="w-full max-w-3xl mb-4 bg-gray-50/80 border border-gray-200/80 rounded-xl p-3 shadow-xs">
            <ThinkingState
              nodes={liveTrace}
              autoPlay={false}
              defaultExpanded={disabled}
              workingLabel="JARVIS is working..."
            />
          </div>
        )}

        {/* Pending Confirmation Banner */}
        {pendingConfirmation && onConfirm && (
          <div className="w-full mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between text-xs text-amber-900">
            <div>
              <span className="font-semibold uppercase tracking-wider text-amber-700 mr-2">
                Action confirmation:
              </span>
              <span>
                {pendingConfirmation.tool} - {pendingConfirmation.reason}
              </span>
            </div>
            <div className="flex gap-2 ml-4">
              <button
                onClick={() => onConfirm(pendingConfirmation.id, true)}
                className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-md font-medium transition-colors"
              >
                Allow
              </button>
              <button
                onClick={() => onConfirm(pendingConfirmation.id, false)}
                className="px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-md font-medium transition-colors"
              >
                Deny
              </button>
            </div>
          </div>
        )}

        {/* Input area with integrated functions and file upload */}
        <div className="w-full bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mb-4">
          <div className="p-4">
            <input
              ref={inputRef}
              type="text"
              placeholder={disabled ? "Processing..." : "Ask me anything..."}
              value={inputValue}
              disabled={disabled}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full text-gray-700 text-base outline-none placeholder:text-gray-400 bg-transparent"
            />
          </div>

          {/* Uploaded files */}
          {uploadedFiles.length > 0 && (
            <div className="px-4 pb-3">
              <div className="flex flex-wrap gap-2">
                {uploadedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 bg-gray-50 py-1 px-2 rounded-md border border-gray-200"
                  >
                    <FileText className="w-3 h-3 text-blue-600" />
                    <span className="text-xs text-gray-700">{file}</span>
                    <button
                      onClick={() =>
                        setUploadedFiles((prev) =>
                          prev.filter((_, i) => i !== index)
                        )
                      }
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Search, Deep Research, Reason functions and actions */}
          <div className="px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setSearchEnabled(!searchEnabled)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  searchEnabled
                    ? "bg-blue-50 text-blue-600 hover:bg-blue-100"
                    : "bg-gray-100 text-gray-400 hover:bg-gray-200"
                }`}
              >
                <Search className="w-4 h-4" />
                <span>Search</span>
              </button>
              <button
                type="button"
                onClick={() => setDeepResearchEnabled(!deepResearchEnabled)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  deepResearchEnabled
                    ? "bg-blue-50 text-blue-600 hover:bg-blue-100"
                    : "bg-gray-100 text-gray-400 hover:bg-gray-200"
                }`}
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className={
                    deepResearchEnabled ? "text-blue-600" : "text-gray-400"
                  }
                >
                  <circle
                    cx="8"
                    cy="8"
                    r="7"
                    stroke="currentColor"
                    strokeWidth="2"
                  />
                  <circle cx="8" cy="8" r="3" fill="currentColor" />
                </svg>
                <span>Deep Research</span>
              </button>
              <button
                type="button"
                onClick={() => setReasonEnabled(!reasonEnabled)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  reasonEnabled
                    ? "bg-blue-50 text-blue-600 hover:bg-blue-100"
                    : "bg-gray-100 text-gray-400 hover:bg-gray-200"
                }`}
              >
                <BrainCircuit
                  className={`w-4 h-4 ${
                    reasonEnabled ? "text-blue-600" : "text-gray-400"
                  }`}
                />
                <span>Reason</span>
              </button>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                type="button"
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || disabled}
                className={`w-8 h-8 flex items-center justify-center rounded-full transition-colors ${
                  inputValue.trim() && !disabled
                    ? "bg-blue-600 text-white hover:bg-blue-700"
                    : "bg-gray-100 text-gray-400 cursor-not-allowed"
                }`}
              >
                <ArrowUp className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Upload files */}
          <div className="px-4 py-2 border-t border-gray-100">
            <button
              type="button"
              onClick={handleUploadFile}
              className="flex items-center gap-2 text-gray-600 text-sm hover:text-gray-900 transition-colors"
            >
              {showUploadAnimation ? (
                <motion.div
                  className="flex space-x-1"
                  initial="hidden"
                  animate="visible"
                  variants={{
                    hidden: {},
                    visible: {
                      transition: {
                        staggerChildren: 0.1,
                      },
                    },
                  }}
                >
                  {[...Array(3)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="w-1.5 h-1.5 bg-blue-600 rounded-full"
                      variants={{
                        hidden: { opacity: 0, y: 5 },
                        visible: {
                          opacity: 1,
                          y: 0,
                          transition: {
                            duration: 0.4,
                            repeat: Infinity,
                            repeatType: "mirror",
                            delay: i * 0.1,
                          },
                        },
                      }}
                    />
                  ))}
                </motion.div>
              ) : (
                <Plus className="w-4 h-4" />
              )}
              <span>Upload Files</span>
            </button>
          </div>
        </div>

        {/* Command categories */}
        {!hasMessages && (
          <div className="w-full grid grid-cols-3 gap-4 mb-4">
            <CommandButton
              icon={<BookOpen className="w-5 h-5" />}
              label="Learn"
              isActive={activeCommandCategory === "learn"}
              onClick={() =>
                setActiveCommandCategory(
                  activeCommandCategory === "learn" ? null : "learn"
                )
              }
            />
            <CommandButton
              icon={<Code className="w-5 h-5" />}
              label="Code"
              isActive={activeCommandCategory === "code"}
              onClick={() =>
                setActiveCommandCategory(
                  activeCommandCategory === "code" ? null : "code"
                )
              }
            />
            <CommandButton
              icon={<PenTool className="w-5 h-5" />}
              label="Write"
              isActive={activeCommandCategory === "write"}
              onClick={() =>
                setActiveCommandCategory(
                  activeCommandCategory === "write" ? null : "write"
                )
              }
            />
          </div>
        )}

        {/* Command suggestions */}
        <AnimatePresence>
          {!hasMessages && activeCommandCategory && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="w-full mb-6 overflow-hidden"
            >
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <div className="p-3 border-b border-gray-100">
                  <h3 className="text-sm font-medium text-gray-700">
                    {activeCommandCategory === "learn"
                      ? "Learning suggestions"
                      : activeCommandCategory === "code"
                      ? "Coding suggestions"
                      : "Writing suggestions"}
                  </h3>
                </div>
                <ul className="divide-y divide-gray-100">
                  {commandSuggestions[
                    activeCommandCategory as keyof typeof commandSuggestions
                  ].map((suggestion, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.03 }}
                      onClick={() => handleCommandSelect(suggestion)}
                      className="p-3 hover:bg-gray-50 cursor-pointer transition-colors duration-75"
                    >
                      <div className="flex items-center gap-3">
                        {activeCommandCategory === "learn" ? (
                          <BookOpen className="w-4 h-4 text-blue-600" />
                        ) : activeCommandCategory === "code" ? (
                          <Code className="w-4 h-4 text-blue-600" />
                        ) : (
                          <PenTool className="w-4 h-4 text-blue-600" />
                        )}
                        <span className="text-sm text-gray-700">
                          {suggestion}
                        </span>
                      </div>
                    </motion.li>
                  ))}
                </ul>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
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
      type="button"
      onClick={onClick}
      className={`flex flex-col items-center justify-center gap-2 p-4 rounded-xl border transition-all ${
        isActive
          ? "bg-blue-50 border-blue-200 shadow-sm"
          : "bg-white border-gray-200 hover:border-gray-300"
      }`}
    >
      <div className={`${isActive ? "text-blue-600" : "text-gray-500"}`}>
        {icon}
      </div>
      <span
        className={`text-sm font-medium ${
          isActive ? "text-blue-700" : "text-gray-700"
        }`}
      >
        {label}
      </span>
    </motion.button>
  );
}
