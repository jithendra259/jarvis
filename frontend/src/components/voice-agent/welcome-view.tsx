'use client';

import React from 'react';

interface WelcomeViewProps {
  startButtonText?: string;
  onStartCall: () => void;
  isConnected?: boolean;
  isConnecting?: boolean;
}

export const WelcomeView = React.forwardRef<
  HTMLDivElement,
  React.ComponentProps<'div'> & WelcomeViewProps
>(({ ...props }, ref) => {
  return null;
});

WelcomeView.displayName = 'WelcomeView';
