export const API_BASE = process.env.NEXT_PUBLIC_JARVIS_API_URL || 'http://127.0.0.1:8000';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  actions?: ToolAction[];
  requiresConfirmation?: boolean;
  confirmation?: ConfirmationInfo;
}

export interface ToolAction {
  tool: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface ConfirmationInfo {
  id: string;
  tool: string;
  arguments: Record<string, unknown>;
  permission_level: string;
  reason: string;
}

export interface ActivityEvent {
  type: string;
  timestamp: string;
  sequence: number;
  conversation_id?: string;
  // Common event fields
  tool?: string;
  arguments?: Record<string, unknown>;
  message?: string;
  reply?: string;
  plan?: string;
  reason?: string;
  error_code?: string;
  duration_ms?: number;
  success?: boolean;
  code?: string;
  [key: string]: unknown;
}

export interface SystemStatus {
  hardware: {
    cpu_count_logical?: number;
    cpu_count_physical?: number;
    ram_total_gb?: number;
    ram_available_gb?: number;
    ram_percent?: number;
    gpu_available?: boolean;
    gpu_name?: string;
    gpu_vram_gb?: number;
    cuda_available?: boolean;
    recommended_inference?: string;
    os?: string;
    cpu_percent?: number;
    [key: string]: unknown;
  };
  runtime: {
    process_count?: number;
    load_percent?: number;
  };
  services: Array<{
    name: string;
    online: boolean;
    models: string[];
    default_model: string;
  }>;
  websocket_clients: number;
  pending_confirmations: number;
}

export async function sendChat(
  message: string,
  conversationId: string = 'default'
): Promise<ChatMessage> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Failed to send message');
  }
  const data = await response.json();
  return {
    role: 'assistant',
    content: data.reply,
    timestamp: new Date().toISOString(),
    actions: data.actions,
    requiresConfirmation: data.requires_confirmation,
    confirmation: data.confirmation,
  };
}

export async function confirmAction(actionId: string, approved: boolean): Promise<ChatMessage> {
  const response = await fetch(`${API_BASE}/api/agent/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_id: actionId, approved }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Failed to confirm action');
  }
  const data = await response.json();
  return {
    role: 'assistant',
    content: data.reply,
    timestamp: new Date().toISOString(),
    actions: data.actions,
  };
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const response = await fetch(`${API_BASE}/api/system/status`);
  if (!response.ok) throw new Error('Failed to fetch system status');
  return response.json();
}

export async function fetchHealth(): Promise<{ status: string; llm: { online: boolean } }> {
  const response = await fetch(`${API_BASE}/api/health`);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}

export function createWebSocket(
  onMessage: (event: ActivityEvent) => void,
  onOpen?: () => void,
  onClose?: () => void,
  onError?: (error: Event) => void
): WebSocket {
  const ws = new WebSocket(`ws://127.0.0.1:8000/ws`);
  ws.onopen = () => onOpen?.();
  ws.onclose = () => onClose?.();
  ws.onerror = (error) => onError?.(error);
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      // ignore parse errors
    }
  };
  return ws;
}

export function sendWsMessage(ws: WebSocket, type: string, payload: Record<string, unknown>) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type, ...payload }));
  }
}