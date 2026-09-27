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
  companyName: 'Jithendra Subramanyam',
  pageTitle: 'Kandula Jithendra Subramanyam | Agentic AI Developer',
  pageDescription: 'Agentic AI & Multi-Agent Systems Developer — M.Tech AI & Data Science researcher. Builder of LangGraph swarms, CVXPY solvers, and real-time WebRTC voice pipelines. Author of 3 research papers (Elsevier EAAI, Springer LNCS).',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#002cf2',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#1fd5f9',
  startButtonText: 'Start call',

  // optional: audio visualization configuration
  // audioVisualizerType: 'bar',
  // audioVisualizerColor: '#002cf2',
  // audioVisualizerColorDark: '#1fd5f9',
  // audioVisualizerColorShift: 0.3,
  // audioVisualizerBarCount: 5,
  // audioVisualizerType: 'radial',
  // audioVisualizerRadialBarCount: 24,
  // audioVisualizerRadialRadius: 100,
  // audioVisualizerType: 'grid',
  // audioVisualizerGridRowCount: 25,
  // audioVisualizerGridColumnCount: 25,
  // audioVisualizerType: 'wave',
  // audioVisualizerWaveLineWidth: 3,
  audioVisualizerType: 'aura',

  // agent dispatch configuration
  agentName: process.env.NEXT_PUBLIC_AGENT_NAME ?? process.env.AGENT_NAME ?? 'my-agent',

  // LiveKit Cloud Sandbox configuration
  sandboxId: undefined,

  // LiveKit connection mode
  livekitMode: (process.env.NEXT_PUBLIC_LIVEKIT_MODE as 'cloud' | 'local') || 'cloud',
};
