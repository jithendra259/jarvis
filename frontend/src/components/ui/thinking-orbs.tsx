'use client';

import React, { useEffect, useState } from 'react';
import { ThinkingOrb as BaseThinkingOrb } from 'thinking-orbs';
import type { ThinkingOrbProps } from 'thinking-orbs';

export function ThinkingOrb(props: ThinkingOrbProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span className="inline-block size-12 animate-pulse rounded-full bg-white/5" />;
  }

  return <BaseThinkingOrb {...props} />;
}

export type { ThinkingOrbProps, OrbState, OrbSize, OrbTheme } from 'thinking-orbs';

export default ThinkingOrb;
