'use client';

import { SystemStatus } from '@/lib/jarvis-api';
import { cn } from '@/lib/utils';

interface StatusItemProps {
  label: string;
  value: string | number | boolean | undefined;
  unit?: string;
  warnThreshold?: number;
  warnWhenAbove?: boolean;
}

function StatusItem({ label, value, unit = '', warnThreshold, warnWhenAbove = true }: StatusItemProps) {
  const isWarn =
    typeof value === 'number' &&
    warnThreshold !== undefined &&
    (warnWhenAbove ? value > warnThreshold : value < warnThreshold);

  const displayValue = value === undefined || value === null ? '—' : String(value);

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-white/40 font-mono">{label}</span>
      <span
        className={cn(
          'font-mono tabular-nums',
          isWarn ? 'text-orange-400' : 'text-white/80'
        )}
      >
        {displayValue}{unit && <span className="text-white/40 ml-0.5">{unit}</span>}
      </span>
    </div>
  );
}

interface StatusBarProps {
  status: SystemStatus | null;
  wsConnected: boolean;
  llmOnline: boolean;
}

export function StatusBar({ status, wsConnected, llmOnline }: StatusBarProps) {
  if (!status) return null;

  // Defensive fallback: support both nested status and legacy flat payloads
  const rawStatus = status as unknown as Record<string, any>;
  const hardware = status.hardware ?? rawStatus ?? {};
  const runtime = status.runtime ?? rawStatus ?? {};
  const services = Array.isArray(status.services) ? status.services : [];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-3 bg-black/20 rounded-lg border border-white/10 text-xs">
      <div className="space-y-1">
        <div className="text-white/40 font-mono uppercase tracking-wider">System</div>
        <StatusItem label="OS" value={hardware?.os} />
        <StatusItem
          label="CPU"
          value={hardware?.cpu_count_logical}
          unit=" cores"
        />
        <StatusItem
          label="RAM"
          value={
            hardware?.ram_total_gb && hardware?.ram_available_gb
              ? `${hardware.ram_available_gb.toFixed(1)} / ${hardware.ram_total_gb.toFixed(1)}`
              : undefined
          }
          unit=" GB"
          warnThreshold={hardware?.ram_total_gb ? hardware.ram_total_gb * 0.15 : undefined}
          warnWhenAbove={false}
        />
        <StatusItem
          label="GPU"
          value={hardware?.gpu_name || (hardware?.gpu_available ? 'Yes' : 'No')}
        />
      </div>

      <div className="space-y-1">
        <div className="text-white/40 font-mono uppercase tracking-wider">Runtime</div>
        <StatusItem
          label="Processes"
          value={runtime?.process_count}
        />
        <StatusItem
          label="CPU Load"
          value={runtime?.load_percent ?? hardware?.cpu_percent}
          unit="%"
          warnThreshold={85}
        />
        <StatusItem
          label="Inference"
          value={hardware?.recommended_inference?.toUpperCase() || 'CPU'}
        />
        <StatusItem label="WS Clients" value={status.websocket_clients ?? 0} />
      </div>

      <div className="space-y-1 md:col-span-2">
        <div className="text-white/40 font-mono uppercase tracking-wider mb-1">Services</div>
        <div className="flex flex-wrap gap-2">
          {services.length > 0 ? (
            services.map((svc, idx) => (
              <span
                key={idx}
                className={cn(
                  'px-2 py-1 rounded text-xs font-mono border',
                  svc.online
                    ? 'bg-green-500/10 border-green-500/30 text-green-400'
                    : 'bg-red-500/10 border-red-500/30 text-red-400'
                )}
              >
                {svc.name} {svc.online ? '●' : '○'} {svc.default_model}
              </span>
            ))
          ) : (
            <span className="text-white/40 font-mono text-xs">No active services</span>
          )}
        </div>
      </div>

      <div className="space-y-1 md:col-span-2">
        <div className="text-white/40 font-mono uppercase tracking-wider mb-1">Connections</div>
        <div className="flex flex-wrap gap-2">
          <span
            className={cn(
              'px-2 py-1 rounded text-xs font-mono border',
              wsConnected
                ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
                : 'bg-gray-500/10 border-gray-500/30 text-gray-400'
            )}
          >
            WebSocket {wsConnected ? '● Connected' : '○ Disconnected'}
          </span>
          <span
            className={cn(
              'px-2 py-1 rounded text-xs font-mono border',
              llmOnline
                ? 'bg-green-500/10 border-green-500/30 text-green-400'
                : 'bg-red-500/10 border-red-500/30 text-red-400'
            )}
          >
            LLM {llmOnline ? '● Online' : '○ Offline'}
          </span>
          <span className="px-2 py-1 rounded text-xs font-mono border border-white/10 text-white/50">
            Pending: {status.pending_confirmations ?? 0}
          </span>
        </div>
      </div>
    </div>
  );
}