"use client";

import React, { useEffect, useState, useRef } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  BarVisualizer,
  VoiceAssistantControlBar,
  useVoiceAssistant,
  useLocalParticipant,
} from "@livekit/components-react";
import "@livekit/components-styles";
import { Mic, MicOff, PhoneOff, Volume2 } from "lucide-react";

interface LiveKitVoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  serverUrl?: string;
  roomName?: string;
}

export function LiveKitVoiceModal({
  isOpen,
  onClose,
  serverUrl = "ws://127.0.0.1:7880",
  roomName = "jarvis-room",
}: LiveKitVoiceModalProps) {
  const [token, setToken] = useState<string>("");
  const [url, setUrl] = useState<string>(serverUrl);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    async function fetchToken() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/livekit/token?room=${roomName}&identity=user-${Math.floor(Math.random()*1000)}`);
        if (!res.ok) {
          throw new Error("Failed to fetch LiveKit token from Jarvis backend");
        }
        const data = await res.json();
        setToken(data.token);
        if (data.url) setUrl(data.url);
      } catch (err: any) {
        setError(err.message || "Failed to connect to LiveKit voice backend");
      } finally {
        setLoading(false);
      }
    }

    fetchToken();
  }, [isOpen, roomName]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-lg bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-2xl flex flex-col items-center">
        {/* Header */}
        <div className="w-full flex items-center justify-between pb-4 border-b border-zinc-800 mb-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-emerald-500 animate-ping" />
            <h3 className="text-white font-semibold text-lg">Jarvis Live Voice Session</h3>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-white p-1 rounded-lg hover:bg-zinc-800 transition"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        {loading && (
          <div className="py-16 text-zinc-400 flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p>Initializing voice channel...</p>
          </div>
        )}

        {error && (
          <div className="py-8 text-center flex flex-col items-center gap-3">
            <p className="text-rose-400 text-sm max-w-xs">{error}</p>
            <p className="text-xs text-zinc-500">Ensure `python server.py` is running on port 8000</p>
            <button
              onClick={onClose}
              className="mt-4 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg text-sm transition"
            >
              Close
            </button>
          </div>
        )}

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
            <VoiceSessionView onClose={onClose} />
            <RoomAudioRenderer />
          </LiveKitRoom>
        )}
      </div>
    </div>
  );
}

function VoiceSessionView({ onClose }: { onClose: () => void }) {
  const { state, audioTrack } = useVoiceAssistant();
  const { isMicrophoneEnabled } = useLocalParticipant();

  return (
    <div className="w-full flex flex-col items-center gap-6 py-4">
      {/* Audio Visualizer */}
      <div className="w-full h-36 flex items-center justify-center bg-zinc-950/80 rounded-xl p-4 border border-zinc-800/80">
        <BarVisualizer
          state={state}
          barCount={15}
          trackRef={audioTrack}
          className="h-24 w-full flex items-center justify-center gap-1.5"
        />
      </div>

      {/* Voice Status Pill */}
      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-800 text-xs font-medium text-zinc-300">
        <Volume2 className="w-3.5 h-3.5 text-blue-400" />
        <span className="capitalize">{state || "Listening..."}</span>
      </div>

      {/* Controls */}
      <div className="w-full flex items-center justify-center gap-4 pt-2">
        <VoiceAssistantControlBar controls={{ leave: false }} />
        <button
          onClick={onClose}
          className="flex items-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-sm font-medium rounded-full shadow-lg transition"
        >
          <PhoneOff className="w-4 h-4" />
          <span>Disconnect</span>
        </button>
      </div>
    </div>
  );
}
