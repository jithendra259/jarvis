'use client';

import React, { useState } from 'react';
import { useTheme } from 'next-themes';
import { Minimize2, Wifi, Server } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { toast } from 'sonner';
import { useSessionContext, useSessionMessages } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentSessionView_01 } from '@/components/agents-ui/blocks/agent-session-view-01';
import { ThinkingOrb } from '@/components/ui/thinking-orbs';
import { DockedVoiceHUD } from '@/components/voice-agent/docked-voice-hud';
import { WelcomeView } from '@/components/voice-agent/welcome-view';
import { useVoiceAutoNavigation } from '@/hooks/useVoiceAutoNavigation';
import { cn } from '@/lib/utils';

const MotionSessionView = motion.create(AgentSessionView_01);

/** Floating ASK button with an animated listening orb — active on every page. */
function AskButton({ onStartCall }: { onStartCall: () => void }) {
  return (
    <div className="fixed right-5 bottom-5 z-40">
      <button
        type="button"
        onClick={onStartCall}
        className={cn(
          'group inline-flex h-[60px] cursor-pointer items-center gap-2 rounded-full border border-white/10 bg-[#1d1d1d]/80 pr-5 pl-1.5 text-white/70 shadow-2xl shadow-black/30 backdrop-blur-xl transition-all duration-300 hover:scale-[1.03] hover:bg-[#252525] focus:ring-2 focus:ring-white/20 focus:outline-none'
        )}
        aria-label="Ask the voice agent"
      >
        <span className="flex size-12 shrink-0 items-center justify-center overflow-hidden rounded-full [&_canvas]:!size-12">
          <ThinkingOrb state="composing" size={64} theme="dark" />
        </span>
        <span className="text-base leading-5 whitespace-nowrap">Ask</span>
      </button>
    </div>
  );
}

const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
    },
    hidden: {
      opacity: 0,
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    ease: 'easeInOut',
  },
} as const;

interface ViewControllerProps {
  appConfig: AppConfig;
  showWelcome?: boolean;
}

export function ViewController({ appConfig, showWelcome = true }: ViewControllerProps) {
  const session = useSessionContext();
  const { isConnected, start } = session;
  const { messages } = useSessionMessages(session);
  const { resolvedTheme } = useTheme();

  // Mode: 'docked' keeps the portfolio page fully visible and auto-navigating.
  // 'full' expands into the immersive full-screen audio visualizer tile.
  const [viewMode, setViewMode] = useState<'docked' | 'full'>('docked');

  // Activate real-time voice-driven auto navigation
  const { activeTarget, navigateTo } = useVoiceAutoNavigation(session, messages);

  // Connection mode indicator
  const isLocalMode = appConfig.livekitMode === 'local';

  const handleStartCall = React.useCallback(async () => {
    if (isConnected) {
      session.end();
      return;
    }

    // Connect directly to Python LiveKit backend worker on Render
    try {
      await start();
    } catch (error) {
      console.error('Failed to connect to LiveKit backend:', error);
      const err = error as Error;
      if (
        err?.name === 'NotReadableError' ||
        err?.message?.includes('Could not start audio source')
      ) {
        toast.error('Microphone In Use or Blocked', {
          description:
            'Windows could not start your audio source. Please check if another browser tab, Zoom, Teams, or Discord is locking your mic.',
        });
      }
    }
  }, [isConnected, session, start]);

  const isConnecting = session.connectionState === 'connecting';
  const isHUDVisible = (isConnected || isConnecting) && viewMode === 'docked';

  return (
    <div className={showWelcome ? 'relative min-h-screen w-full' : 'relative w-full'}>
      {/* Portfolio page: Always rendered and interactive */}
      {showWelcome && (
        <WelcomeView
          startButtonText={appConfig.startButtonText}
          onStartCall={handleStartCall}
          isConnected={isConnected}
          isConnecting={isConnecting}
        />
      )}

      {!isConnected && !isConnecting && <AskButton onStartCall={handleStartCall} />}

      {/* Connection Mode Indicator */}
      <div className="fixed left-5 bottom-5 z-40 flex items-center gap-2 rounded-full border border-white/10 bg-[#1d1d1d]/80 px-3 py-1.5 text-xs font-mono text-white/70 shadow-2xl shadow-black/30 backdrop-blur-xl">
        {isLocalMode ? (
          <>
            <Server className="size-3 text-green-400" />
            <span>LOCAL</span>
          </>
        ) : (
          <>
            <Wifi className="size-3 text-blue-400" />
            <span>CLOUD</span>
          </>
        )}
      </div>

      {/* Floating Live Voice HUD */}
      <AnimatePresence>
        {isHUDVisible && (
          <DockedVoiceHUD
            key="docked-hud"
            onExpand={() => setViewMode('full')}
            activeTarget={activeTarget}
            messages={messages}
            onManualNavigate={(target) => {
              navigateTo(target, 'data_channel');
            }}
          />
        )}
      </AnimatePresence>

      {/* When Connected & in Full Immersion Mode: Fullscreen Visualizer Tile */}
      <AnimatePresence>
        {isConnected && viewMode === 'full' && (
          <motion.div
            key="full-session-view"
            {...VIEW_MOTION_PROPS}
            className="bg-background/95 fixed inset-0 z-50 backdrop-blur-3xl"
          >
            {/* Minimize to Dock button */}
            <div className="absolute top-4 right-4 z-60">
              <button
                type="button"
                onClick={() => setViewMode('docked')}
                className="flex cursor-pointer items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3.5 py-2 font-mono text-xs text-white shadow-lg backdrop-blur-xl transition-all hover:bg-white/20"
                title="Minimize to Dock (View Portfolio Page)"
              >
                <Minimize2 className="size-3.5" />
                <span>Dock / View Page</span>
              </button>
            </div>

            <MotionSessionView
              supportsChatInput={appConfig.supportsChatInput}
              supportsVideoInput={appConfig.supportsVideoInput}
              supportsScreenShare={appConfig.supportsScreenShare}
              isPreConnectBufferEnabled={appConfig.isPreConnectBufferEnabled}
              audioVisualizerType={appConfig.audioVisualizerType}
              audioVisualizerColor={
                resolvedTheme === 'dark'
                  ? appConfig.audioVisualizerColorDark
                  : appConfig.audioVisualizerColor
              }
              audioVisualizerColorShift={appConfig.audioVisualizerColorShift}
              audioVisualizerBarCount={appConfig.audioVisualizerBarCount}
              audioVisualizerGridRowCount={appConfig.audioVisualizerGridRowCount}
              audioVisualizerGridColumnCount={appConfig.audioVisualizerGridColumnCount}
              audioVisualizerRadialBarCount={appConfig.audioVisualizerRadialBarCount}
              audioVisualizerRadialRadius={appConfig.audioVisualizerRadialRadius}
              audioVisualizerWaveLineWidth={appConfig.audioVisualizerWaveLineWidth}
              className="h-full w-full"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
