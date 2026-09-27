import { type Room } from 'livekit-client';
import {
  RoomContext,
  RoomAudioRenderer,
  type RoomAudioRendererProps,
  SessionProvider,
  type SessionProviderProps,
  type UseSessionReturn,
} from '@livekit/components-react';

/**
 * Props for the AgentSessionProvider component.
 * Combines SessionProviderProps with RoomAudioRendererProps.
 */
export type AgentSessionProviderProps = SessionProviderProps &
  RoomAudioRendererProps & {
    /**
     * The room to provide.
     */
    room?: Room;
    /**
     * The volume to set for the audio renderer.
     */
    volume?: number;
    /**
     * Whether to mute the audio renderer.
     */
    muted?: boolean;
    /**
     * The session to provide.
     */
    session: UseSessionReturn;
    /**
     * The children to render.
     */
    children: React.ReactNode;
  };

/**
 * A provider component for agent sessions that wraps SessionProvider
 * and includes RoomAudioRenderer for audio playback.
 *
 * @example
 * ```tsx
 * <AgentSessionProvider session={agentSession}>
 *   <AgentControlBar />
 *   <AgentChatTranscript />
 * </AgentSessionProvider>
 * ```
 */
export function AgentSessionProvider({
  session,
  room,
  children,
  ...roomAudioRendererProps
}: AgentSessionProviderProps) {
  const currentRoom = room || session?.room;

  return (
    <SessionProvider session={session}>
      {currentRoom ? (
        <RoomContext.Provider value={currentRoom}>
          {children}
          <RoomAudioRenderer {...roomAudioRendererProps} />
        </RoomContext.Provider>
      ) : (
        <>
          {children}
          <RoomAudioRenderer {...roomAudioRendererProps} />
        </>
      )}
    </SessionProvider>
  );
}
