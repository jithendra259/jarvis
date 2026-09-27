export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura';
  audioVisualizerColor?: `#${string}`;
  audioVisualizerColorDark?: `#${string}`;
  audioVisualizerColorShift?: number;
  audioVisualizerBarCount?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;
  audioVisualizerRadialBarCount?: number;
  audioVisualizerRadialRadius?: number;
  audioVisualizerWaveLineWidth?: number;

  // agent dispatch configuration
  agentName?: string;

  // LiveKit Cloud Sandbox configuration
  sandboxId?: string;

  // LiveKit connection mode: "cloud" | "local"
  livekitMode?: 'cloud' | 'local';
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'JARVIS',
  pageTitle: 'JARVIS | Local Desktop AI Assistant',
  pageDescription: 'Fully local Windows desktop AI assistant with voice, chat, and computer control.',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: false,

  logo: '/icon.ico',
  accent: '#00d4ff',
  logoDark: '/icon.ico',
  accentDark: '#00d4ff',
  startButtonText: 'Start Voice',

  audioVisualizerType: 'aura',

  // agent dispatch configuration
  agentName: process.env.NEXT_PUBLIC_AGENT_NAME ?? process.env.AGENT_NAME ?? 'jarvis',

  // LiveKit Cloud Sandbox configuration
  sandboxId: undefined,

  // LiveKit connection mode - default to local for fully local operation
  livekitMode: (process.env.NEXT_PUBLIC_LIVEKIT_MODE as 'cloud' | 'local') || 'local',
};