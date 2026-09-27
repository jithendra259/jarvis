"use client";

import React, { useEffect, useState } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  BarVisualizer,
  VoiceAssistantControlBar,
  useVoiceAssistant,
  useLocalParticipant,
  useRoomContext,
} from "@livekit/components-react";
import { RoomEvent } from "livekit-client";
import "@livekit/components-styles";
import { Mic, MicOff, PhoneOff, Volume2, Minimize2, Maximize2, Sparkles } from "lucide-react";
import { AgentAudioVisualizerAura } from "@/components/agents-ui/agent-audio-visualizer-aura";
import { cn } from "@/lib/utils";

interface LiveKitVoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAction?: (actionData: any) => void;
  serverUrl?: string;
  roomName?: string;
}

export function LiveKitVoiceModal({
  isOpen,
  onClose,
  onAction,
  serverUrl = "ws://127.0.0.1:7880",
  roomName = "jarvis-room",
}: LiveKitVoiceModalProps) {
  const [token, setToken] = useState<string>("");
  const [url, setUrl] = useState<string>(serverUrl);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDocked, setIsDocked] = useState(false);

  useEffect(() => {
    if (!isOpen) return;

    async function fetchToken() {
      setLoading(true);
      setError(null);
      try {
        // Try local Next.js proxy route first, fallback to FastAPI backend directly
        let res = await fetch(`/api/token?room=${encodeURIComponent(roomName)}&identity=user-${Math.floor(Math.random() * 1000)}`);
        if (!res.ok) {
          res = await fetch(`http://127.0.0.1:8000/api/livekit/token?room=${encodeURIComponent(roomName)}&identity=user-${Math.floor(Math.random() * 1000)}`);
        }

        if (!res.ok) {
          throw new Error("Failed to fetch LiveKit token from Jarvis backend");
        }
        const data = await res.json();
        const jwtToken = data.participantToken || data.token;
        const livekitUrl = data.serverUrl || data.url || serverUrl;
        
        if (!jwtToken) {
          throw new Error("Invalid token payload returned from server");
        }

        setToken(jwtToken);
        if (livekitUrl) setUrl(livekitUrl);
      } catch (err: any) {
        console.error("Token error:", err);
        setError(err.message || "Failed to connect to LiveKit voice backend");
      } finally {
        setLoading(false);
      }
    }

    fetchToken();
  }, [isOpen, roomName, serverUrl]);

  if (!isOpen) return null;

  return (
    <div
      className={cn(
        isDocked
          ? "fixed right-6 bottom-6 z-50 transition-all duration-300"
          : "fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      )}
    >
      <div
        className={cn(
          "relative bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl flex flex-col transition-all duration-300",
          isDocked ? "w-80 p-4 border-cyan-500/30" : "w-full max-w-lg p-6"
        )}
      >
        {/* Header */}
        <div className="w-full flex items-center justify-between pb-3 border-b border-zinc-800 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <h3 className="text-white font-semibold text-sm tracking-wide flex items-center gap-1.5">
              <span>JARVIS Voice</span>
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            </h3>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setIsDocked((prev) => !prev)}
              className="text-zinc-400 hover:text-white p-1 rounded-lg hover:bg-zinc-800 transition"
              title={isDocked ? "Expand" : "Dock to Corner"}
            >
              {isDocked ? <Maximize2 className="w-3.5 h-3.5" /> : <Minimize2 className="w-3.5 h-3.5" />}
            </button>
            <button
              onClick={onClose}
              className="text-zinc-400 hover:text-white p-1 rounded-lg hover:bg-zinc-800 transition"
              title="Close Voice Session"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Loading / Error States */}
        {loading && (
          <div className="py-12 text-zinc-400 flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs font-mono">Initializing voice stream...</p>
          </div>
        )}

        {error && (
          <div className="py-6 text-center flex flex-col items-center gap-2">
            <p className="text-rose-400 text-xs max-w-xs">{error}</p>
            <p className="text-[11px] text-zinc-500 font-mono">Ensure `python server.py` is running on port 8000</p>
            <button
              onClick={onClose}
              className="mt-3 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg text-xs transition"
            >
              Close
            </button>
          </div>
        )}

        {/* LiveKit Connected Room */}
        {!loading && !error && token && (
          <LiveKitRoom
            token={token}
            serverUrl={url}
            connect={true}
            audio={true}
            video={false}
            onDisconnected={onClose}
            className="w-full flex flex-col items-center"
          >
            <VoiceSessionView onClose={onClose} onAction={onAction} isDocked={isDocked} />
            <RoomAudioRenderer />
          </LiveKitRoom>
        )}
      </div>
    </div>
  );
}

function VoiceSessionView({
  onClose,
  onAction,
  isDocked,
}: {
  onClose: () => void;
  onAction?: (actionData: any) => void;
  isDocked?: boolean;
}) {
  const { state, audioTrack } = useVoiceAssistant();
  const room = useRoomContext();

  // Listen for agent actions published over LiveKit WebRTC Data Channel
  useEffect(() => {
    if (!room) return;

    const handleDataReceived = (payload: Uint8Array, participant: any, kind: any, topic?: string) => {
      try {
        const text = new TextDecoder().decode(payload);
        const data = JSON.parse(text);
        if (topic === "assistant_action" || data?.type === "assistant_action") {
          console.log("[Jarvis Voice Data Channel Action]:", data);
          onAction?.(data);
        }
      } catch (err) {
        console.warn("Failed to decode data packet:", err);
      }
    };

    room.on(RoomEvent.DataReceived, handleDataReceived);
    return () => {
      room.off(RoomEvent.DataReceived, handleDataReceived);
    };
  }, [room, onAction]);

  const auraColor: `#${string}` =
    state === "speaking"
      ? "#34d399"
      : state === "thinking"
        ? "#fbbf24"
        : state === "listening"
          ? "#22d3ee"
          : "#818cf8";

  return (
    <div className={cn("w-full flex flex-col items-center gap-4", isDocked ? "py-1" : "py-4")}>
      {/* Visualizer Tile */}
      <div
        className={cn(
          "w-full flex items-center justify-center bg-zinc-950/80 rounded-xl border border-zinc-800/80 relative overflow-hidden",
          isDocked ? "h-24 p-2" : "h-36 p-4"
        )}
      >
        <div className="absolute inset-0 flex items-center justify-center opacity-80 pointer-events-none">
          <AgentAudioVisualizerAura
            state={state}
            audioTrack={audioTrack}
            color={auraColor}
            colorShift={0.05}
            className="w-full h-full"
          />
        </div>

        <BarVisualizer
          state={state}
          barCount={isDocked ? 12 : 20}
          trackRef={audioTrack}
          className="h-16 w-full flex items-center justify-center gap-1 z-10 opacity-70"
        />
      </div>

      {/* Voice Status Pill */}
      <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-800/90 text-xs font-mono text-zinc-300 border border-zinc-700/50">
        <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
        <span className="capitalize">{state || "Listening..."}</span>
      </div>

      {/* Controls */}
      <div className="w-full flex items-center justify-center gap-3 pt-1">
        <VoiceAssistantControlBar controls={{ leave: false }} />
        <button
          onClick={onClose}
          className="flex items-center gap-1.5 px-3.5 py-1.5 bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium rounded-full shadow-lg transition"
        >
          <PhoneOff className="w-3.5 h-3.5" />
          <span>Disconnect</span>
        </button>
      </div>
    </div>
  );
}
