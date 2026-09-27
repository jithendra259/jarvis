'use client';

import type { ActivityEvent } from '@/lib/jarvis-api';
import { cn } from '@/lib/utils';

const EVENT_ICONS: Record<string, string> = {
  'agent.started': '▶',
  'agent.thinking': '⟳',
  'agent.planned': '📋',
  'agent.completed': '✓',
  'agent.error': '✗',
  'agent.cancelled': '◼',
  'tool.started': '⚡',
  'tool.completed': '✓',
  'tool.failed': '✗',
  'confirmation.required': '?',
  'confirmation.resolved': '✓',
  'voice.listening': '🎤',
  'voice.transcribing': '📝',
  'voice.generating': '🔊',
  'voice.speaking': '🗣',
  'voice.interrupted': '⚠',
  'system.status': '📊',
};

const EVENT_COLORS: Record<string, string> = {
  'agent.started': 'text-cyan-400',
  'agent.thinking': 'text-yellow-400',
  'agent.planned': 'text-blue-400',
  'agent.completed': 'text-green-400',
  'agent.error': 'text-red-400',
  'agent.cancelled': 'text-gray-400',
  'tool.started': 'text-purple-400',
  'tool.completed': 'text-green-400',
  'tool.failed': 'text-red-400',
  'confirmation.required': 'text-orange-400',
  'confirmation.resolved': 'text-green-400',
  'voice.listening': 'text-cyan-400',
  'voice.transcribing': 'text-yellow-400',
  'voice.generating': 'text-blue-400',
  'voice.speaking': 'text-green-400',
  'voice.interrupted': 'text-red-400',
  'system.status': 'text-gray-400',
};

function formatEvent(event: ActivityEvent): string {
  const icon = EVENT_ICONS[event.type] || '●';
  const time = event.timestamp && !isNaN(new Date(event.timestamp).getTime())
    ? new Date(event.timestamp).toLocaleTimeString()
    : new Date().toLocaleTimeString();
  const details = formatDetails(event);
  return `${time} ${icon} ${event.type}${details ? ` ${details}` : ''}`;
}

function formatDetails(event: ActivityEvent): string {
  switch (event.type) {
    case 'tool.started':
      return event.tool ? `→ ${event.tool}(${JSON.stringify(event.arguments)})` : '';
    case 'tool.completed':
      return event.tool ? `→ ${event.tool} ✓` : '';
    case 'tool.failed':
      return event.tool ? `→ ${event.tool} ✗ ${event.message || ''}` : '';
    case 'agent.planned':
      return event.plan ? `→ ${event.plan}` : '';
    case 'agent.completed':
      return event.reply ? `→ "${event.reply.slice(0, 60)}${event.reply.length > 60 ? '...' : ''}"` : '';
    case 'agent.error':
      return event.message ? `→ ${event.message}` : '';
    case 'confirmation.required':
      return event.tool ? `→ ${event.tool} needs confirmation: ${event.reason}` : '';
    default:
      return '';
  }
}

interface ActivityFeedProps {
  events: ReadonlyArray<ActivityEvent>;
  maxEvents?: number;
}

export function ActivityFeed({ events, maxEvents = 50 }: ActivityFeedProps) {
  const displayEvents = [...events].slice(-maxEvents);

  return (
    <div className="flex flex-col h-full bg-black/20 rounded-lg border border-white/10 overflow-hidden">
      <div className="px-3 py-2 border-b border-white/10 bg-white/5 flex items-center justify-between">
        <h3 className="text-xs font-mono text-white/70 uppercase tracking-wider">Activity</h3>
        <span className="text-xs text-white/40 font-mono">{displayEvents.length} events</span>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {displayEvents.length === 0 ? (
          <div className="text-center text-white/30 text-xs py-8">
            No activity yet. Send a message to start.
          </div>
        ) : (
          displayEvents.map((event, index) => (
            <div
              key={`${event.sequence}-${index}`}
              className={cn(
                'text-xs font-mono transition-colors',
                EVENT_COLORS[event.type] || 'text-white/60'
              )}
              title={JSON.stringify(event, null, 2)}
            >
              {formatEvent(event)}
            </div>
          ))
        )}
      </div>
    </div>
  );
}