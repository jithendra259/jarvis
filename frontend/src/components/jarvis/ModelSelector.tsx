'use client';

import { useState, useMemo, useRef, useEffect } from 'react';
import { ChevronDown, Search, Check, Cpu, Sparkles, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ModelSelectorProps {
  models: string[];
  selectedModel: string;
  onSelectModel: (model: string) => void;
  onRefresh?: () => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function ModelSelector({
  models,
  selectedModel,
  onSelectModel,
  onRefresh,
  isLoading = false,
  disabled = false,
}: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const filteredModels = useMemo(() => {
    const query = search.toLowerCase().trim();
    if (!query) return models;
    return models.filter((m) => m.toLowerCase().includes(query));
  }, [models, search]);

  const popularModels = useMemo(() => {
    const list = [
      'oc/space-bunny-free',
      'auto/best-chat',
      'auto/best-fast',
      'auto/best-coding',
      'auto/best-reasoning',
      'auto/best-free',
      'qwen2.5:7b-instruct',
      'llama3.2:3b',
    ];
    return list.filter((m) => models.includes(m) || m.startsWith('auto/') || m.includes('free'));
  }, [models]);

  const displayLabel = useMemo(() => {
    if (!selectedModel) return 'Select Model';
    return selectedModel;
  }, [selectedModel]);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        type="button"
        disabled={disabled}
        onClick={() => setIsOpen((prev) => !prev)}
        className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/10 bg-black/40 hover:bg-black/60 text-xs font-mono text-white/90 transition-all duration-150 backdrop-blur-sm',
          isOpen && 'border-cyan-500/50 ring-1 ring-cyan-500/30',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        title={selectedModel ? `Active Model: ${selectedModel}` : 'Select an LLM model'}
      >
        <Cpu className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
        <span className="max-w-[160px] sm:max-w-[200px] truncate text-left font-medium">
          {displayLabel}
        </span>
        <ChevronDown
          className={cn(
            'w-3.5 h-3.5 text-white/40 transition-transform duration-200 flex-shrink-0',
            isOpen && 'transform rotate-180 text-cyan-400'
          )}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl border border-white/15 bg-neutral-950/95 text-white shadow-2xl backdrop-blur-md z-50 overflow-hidden flex flex-col max-h-[420px] animate-in fade-in-0 zoom-in-95 duration-100">
          {/* Header & Search */}
          <div className="p-3 border-b border-white/10 space-y-2 bg-black/30">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-white/60 font-semibold flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                OmniRoute / Local Models
              </span>
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-white/40">{models.length} available</span>
                {onRefresh && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRefresh();
                    }}
                    className="p-1 hover:bg-white/10 rounded text-white/60 hover:text-white transition-colors"
                    title="Refresh model list"
                  >
                    <RefreshCw className={cn('w-3 h-3', isLoading && 'animate-spin text-cyan-400')} />
                  </button>
                )}
              </div>
            </div>

            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-white/40" />
              <input
                ref={inputRef}
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search models (e.g. gpt, claude, auto, llama)..."
                className="w-full pl-8 pr-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs font-mono text-white placeholder:text-white/30 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30"
              />
              {search && (
                <button
                  type="button"
                  onClick={() => setSearch('')}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-white/40 hover:text-white"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Model List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-1 divide-y divide-white/5">
            {/* Quick Picks / Popular (only when not searching) */}
            {!search && popularModels.length > 0 && (
              <div className="pb-2 space-y-1">
                <div className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-cyan-400/80 font-semibold">
                  Recommended & Virtual Routes
                </div>
                {popularModels.map((model) => (
                  <button
                    key={`pop-${model}`}
                    type="button"
                    onClick={() => {
                      onSelectModel(model);
                      setIsOpen(false);
                    }}
                    className={cn(
                      'w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-mono text-left transition-colors',
                      selectedModel === model
                        ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30'
                        : 'hover:bg-white/5 text-white/80'
                    )}
                  >
                    <span className="truncate">{model}</span>
                    {selectedModel === model && <Check className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />}
                  </button>
                ))}
              </div>
            )}

            {/* All Models */}
            <div className="pt-2 space-y-1">
              {!search && (
                <div className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-white/40">
                  All Available Models ({filteredModels.length})
                </div>
              )}
              {filteredModels.length === 0 ? (
                <div className="p-4 text-center text-xs text-white/40 font-mono">
                  No models matching &quot;{search}&quot;
                </div>
              ) : (
                filteredModels.map((model) => (
                  <button
                    key={model}
                    type="button"
                    onClick={() => {
                      onSelectModel(model);
                      setIsOpen(false);
                    }}
                    className={cn(
                      'w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-mono text-left transition-colors',
                      selectedModel === model
                        ? 'bg-cyan-500/20 text-cyan-300 font-semibold border border-cyan-500/30'
                        : 'hover:bg-white/5 text-white/70 hover:text-white'
                    )}
                  >
                    <span className="truncate">{model}</span>
                    {selectedModel === model && <Check className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />}
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
