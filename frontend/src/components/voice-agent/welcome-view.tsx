'use client';

import React from 'react';
import { AIAssistantInterface } from '@/components/ui/ai-assistant-interface';

interface WelcomeViewProps {
  startButtonText?: string;
  onStartCall: () => void;
  isConnected?: boolean;
  isConnecting?: boolean;
}

export const WelcomeView = React.forwardRef<
  HTMLDivElement,
  React.ComponentProps<'div'> & WelcomeViewProps
>(({ onStartCall, isConnected, isConnecting, ...props }, ref) => {
  return (
    <div ref={ref} {...props} className="w-full h-full">
      <AIAssistantInterface />
    </div>
  );
});

WelcomeView.displayName = 'WelcomeView';
