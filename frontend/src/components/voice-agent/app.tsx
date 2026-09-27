'use client';

import { type ReactNode, useEffect, useMemo } from 'react';
import { usePathname } from 'next/navigation';
import { AudioPresets, Room } from 'livekit-client';
import { useSession } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentSessionProvider } from '@/components/agents-ui/agent-session-provider';
import { StartAudioButton } from '@/components/agents-ui/start-audio-button';
import { ViewController } from '@/components/voice-agent/view-controller';
import { useDebugMode } from '@/hooks/useDebug';
import { getMultiUserTokenSource, getSandboxTokenSource, getDevelopmentTokenSource, LIVEKIT_TOKEN_SERVER_ID } from '@/lib/utils';

// Guard against duplicate topic stream handler crashes in React StrictMode & Turbopack
interface PatchedRoom extends Room {
  __safe_handler_patched?: boolean;
}
type LiveKitTextStreamHandler = Parameters<
  NonNullable<typeof Room.prototype.registerTextStreamHandler>
>[1];
if (typeof window !== 'undefined' && typeof Room !== 'undefined' && Room.prototype) {
  const originalRegister = Room.prototype.registerTextStreamHandler;
  const originalUnregister = Room.prototype.unregisterTextStreamHandler;

  if (originalRegister && !(Room.prototype as PatchedRoom).__safe_handler_patched) {
    (Room.prototype as PatchedRoom).__safe_handler_patched = true;

    const roomSubscribers = new WeakMap<Room, Map<string, Set<LiveKitTextStreamHandler>>>();

    Room.prototype.registerTextStreamHandler = function (
      topic: string,
      callback: LiveKitTextStreamHandler
    ) {
      let topicMap = roomSubscribers.get(this);
      if (!topicMap) {
        topicMap = new Map();
        roomSubscribers.set(this, topicMap);
      }

      let subs = topicMap.get(topic);
      if (!subs) {
        subs = new Set();
        topicMap.set(topic, subs);
      }
      subs.add(callback);

      try {
        this.unregisterTextStreamHandler(topic);
      } catch {
        // ignore
      }

      return originalRegister.call(this, topic, (reader: unknown, participant: unknown) => {
        const currentSubs = topicMap?.get(topic);
        if (currentSubs) {
          for (const sub of Array.from(currentSubs)) {
            try {
              sub(reader as never, participant as never);
            } catch (e) {
              console.warn('Error in text stream handler:', e);
            }
          }
        }
      });
    };

    Room.prototype.unregisterTextStreamHandler = function (topic: string) {
      const topicMap = roomSubscribers.get(this);
      if (topicMap) {
        topicMap.delete(topic);
      }
      try {
        return originalUnregister.call(this, topic);
      } catch {
        // ignore
      }
    };
  }
}

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

function AppSetup() {
  useDebugMode({ enabled: IN_DEVELOPMENT });

  return null;
}

interface AppProps {
  appConfig: AppConfig;
  children?: ReactNode;
}

export function App({ appConfig, children }: AppProps) {
  const pathname = usePathname();
  const tokenSource = useMemo(() => {
    // Priority: 1. Development Token Server, 2. Sandbox, 3. Multi-user (fallback)
    if (LIVEKIT_TOKEN_SERVER_ID) {
      return getDevelopmentTokenSource(appConfig.agentName);
    }
    return typeof process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT === 'string'
      ? getSandboxTokenSource(appConfig)
      : getMultiUserTokenSource();
  }, [appConfig]);

  // Create an explicit Room configured for voice AI clarity.
  // This runs once and is stable across renders (useMemo with no deps).
  const room = useMemo(
    () =>
      new Room({
        // ── Microphone capture defaults ────────────────────────────────
        audioCaptureDefaults: {
          // Keep WebRTC built-ins ON — they run client-side before upload
          // and complement (not conflict with) the agent-side ai-coustics model.
          // The LiveKit docs only warn against enabling a *second* Krisp/ai-coustics
          // model in the frontend, not against standard WebRTC processing.
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
        // ── Microphone publish defaults ────────────────────────────────
        publishDefaults: {
          // DTX (discontinuous transmission): pauses the encoded stream when the
          // user is silent, reducing bandwidth and Deepgram processing load.
          dtx: true,
          // RED (redundant audio encoding): sends each audio frame twice in
          // consecutive packets. Receiver reconstructs dropped packets from
          // the redundant copy — eliminates audio glitches on lossy Wi-Fi.
          // Costs ~2x audio bandwidth but is almost always worth it for STT quality.
          red: true,
          // Standard voice quality — Deepgram nova-3 works best on clean mono voice
          audioPreset: AudioPresets.speech,
        },
      }),
    []
  );

  const session = useSession(
    tokenSource,
    appConfig.agentName ? { agentName: appConfig.agentName, room } : { room }
  );



  useEffect(() => {
    if (!session.isConnected || !room?.localParticipant) return;

    const publishCurrentPage = () => {
      try {
        const payload = JSON.stringify({
          type: 'page_context',
          pathname,
          title: typeof document !== 'undefined' ? document.title : '',
          url: typeof window !== 'undefined' ? window.location.href : pathname,
          hash: typeof window !== 'undefined' ? window.location.hash : '',
          timestamp: Date.now(),
        });
        const encoded = new TextEncoder().encode(payload);
        room.localParticipant
          .publishData(encoded, {
            topic: 'client_context',
            reliable: true,
          })
          .catch((err) => console.warn('Failed to publish client_context:', err));
        room.localParticipant
          .publishData(encoded, {
            topic: 'page_context',
            reliable: true,
          })
          .catch(() => {});
      } catch (e) {
        console.warn('Error serializing page_context:', e);
      }
    };

    // Publish immediately
    publishCurrentPage();

    // Re-publish after 600ms to guarantee server worker receives it if worker setup took a moment
    const timer = setTimeout(publishCurrentPage, 600);

    // Listen for agent's query_page pings
    const handleData = (
      payload: Uint8Array,
      _participant?: unknown,
      _kind?: unknown,
      topic?: string
    ) => {
      if (topic === 'query_page') {
        publishCurrentPage();
      }
    };

    room.on('dataReceived', handleData);

    return () => {
      clearTimeout(timer);
      room.off('dataReceived', handleData);
    };
  }, [pathname, room, session.isConnected]);

  return (
    <AgentSessionProvider session={session} room={room}>
      <AppSetup />
      {children}
      <ViewController appConfig={appConfig} showWelcome={pathname === '/'} />
      <StartAudioButton label="Start Audio" />
    </AgentSessionProvider>
  );
}
