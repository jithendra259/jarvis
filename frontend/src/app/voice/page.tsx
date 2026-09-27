'use client';

import { App as VoiceAgentApp } from '@/components/voice-agent/app';
import { APP_CONFIG_DEFAULTS } from '@/app-config';

export default function VoicePage() {
  return (
    <div className="h-screen w-full">
      <VoiceAgentApp appConfig={APP_CONFIG_DEFAULTS} />
    </div>
  );
}