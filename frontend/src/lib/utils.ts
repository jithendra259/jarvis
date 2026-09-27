import { cache } from 'react';
import { TokenSource } from 'livekit-client';
import { APP_CONFIG_DEFAULTS } from '@/app-config';
import type { AppConfig } from '@/app-config';

export { cn } from '@/lib/shadcn/utils';

export const CONFIG_ENDPOINT = process.env.NEXT_PUBLIC_APP_CONFIG_ENDPOINT;
export const SANDBOX_ID = process.env.SANDBOX_ID;
export const LIVEKIT_TOKEN_SERVER_ID = process.env.NEXT_PUBLIC_LIVEKIT_TOKEN_SERVER_ID;

export interface SandboxConfig {
  [key: string]:
    | { type: 'string'; value: string }
    | { type: 'number'; value: number }
    | { type: 'boolean'; value: boolean }
    | null;
}

/**
 * Get the app configuration
 * @param headers - The headers of the request
 * @returns The app configuration
 *
 * @note React will invalidate the cache for all memoized functions for each server request.
 * https://react.dev/reference/react/cache#caveats
 */
export const getAppConfig = cache(async (headers?: Headers): Promise<AppConfig> => {
  if (CONFIG_ENDPOINT) {
    const sandboxId = SANDBOX_ID ?? headers?.get('x-sandbox-id') ?? '';

    try {
      if (!sandboxId) {
        throw new Error('Sandbox ID is required');
      }

      const response = await fetch(CONFIG_ENDPOINT, {
        cache: 'no-store',
        headers: { 'X-Sandbox-ID': sandboxId },
      });

      if (response.ok) {
        const remoteConfig: SandboxConfig = await response.json();

        const config: AppConfig = { ...APP_CONFIG_DEFAULTS, sandboxId };

        for (const [key, entry] of Object.entries(remoteConfig)) {
          if (entry === null) continue;
          // Only include app config entries that are declared in defaults and, if set,
          // share the same primitive type as the default value.
          if (
            (key in APP_CONFIG_DEFAULTS &&
              APP_CONFIG_DEFAULTS[key as keyof AppConfig] === undefined) ||
            (typeof config[key as keyof AppConfig] === entry.type &&
              typeof config[key as keyof AppConfig] === typeof entry.value)
          ) {
            // @ts-expect-error I'm not sure quite how to appease TypeScript, but we've thoroughly checked types above
            config[key as keyof AppConfig] = entry.value as AppConfig[keyof AppConfig];
          }
        }

        return config;
      } else {
        console.error(
          `ERROR: querying config endpoint failed with status ${response.status}: ${response.statusText}`
        );
      }
    } catch (error) {
      console.error('ERROR: getAppConfig() - lib/utils.ts', error);
    }
  }

  return APP_CONFIG_DEFAULTS;
});

/**
 * Get styles for the app
 * @param appConfig - The app configuration
 * @returns A string of styles
 */
export function getStyles(appConfig: AppConfig) {
  const { accent, accentDark } = appConfig;

  return [
    accent
      ? `:root { --primary: ${accent}; --primary-hover: color-mix(in srgb, ${accent} 80%, #000); }`
      : '',
    accentDark
      ? `.dark { --primary: ${accentDark}; --primary-hover: color-mix(in srgb, ${accentDark} 80%, #000); }`
      : '',
  ]
    .filter(Boolean)
    .join('\n');
}

/**
 * Get a token source using LiveKit's Development Token Server
 * Uses TokenSource.endpoint() with the development token server URL
 * @param agentName - Optional agent name to dispatch
 * @returns A token source for LiveKit development sessions
 */
export function getDevelopmentTokenSource(agentName?: string) {
  if (!LIVEKIT_TOKEN_SERVER_ID) {
    throw new Error('NEXT_PUBLIC_LIVEKIT_TOKEN_SERVER_ID is not configured');
  }
  // Development token server URL format: https://<token-server-id>.sandbox.livekit.io/token
  const url = new URL(`https://${LIVEKIT_TOKEN_SERVER_ID}.sandbox.livekit.io/token`);
  if (agentName) {
    url.searchParams.set('agentName', agentName);
  }
  return TokenSource.endpoint(url.toString());
}

/**
 * Get a token source for a sandboxed LiveKit session
 * @param appConfig - The app configuration
 * @returns A token source for a sandboxed LiveKit session
 */
export function getSandboxTokenSource(appConfig: AppConfig) {
  return TokenSource.custom(async () => {
    const url = new URL(process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT!, window.location.origin);
    const sandboxId = appConfig.sandboxId ?? '';
    const roomConfig = appConfig.agentName
      ? {
          agents: [{ agent_name: appConfig.agentName }],
        }
      : undefined;

    try {
      const res = await fetch(url.toString(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Sandbox-Id': sandboxId,
        },
        body: JSON.stringify({
          room_config: roomConfig,
        }),
      });
      return await res.json();
    } catch (error) {
      console.error('Error fetching connection details:', error);
      throw new Error('Error fetching connection details!');
    }
  });
}

/**
 * Get a token source for multi-user LiveKit sessions
 * First calls backend /create_room to get a unique room UUID,
 * then gets a token for that room from /api/token
 * Falls back to client-side UUID generation if backend is unreachable
 * @returns A token source for multi-user LiveKit sessions
 */
export function getMultiUserTokenSource() {
  return TokenSource.custom(async () => {
    // Generate room UUID client-side with fallback
    const roomName = (typeof crypto !== 'undefined' && crypto.randomUUID)
      ? crypto.randomUUID()
      : `room_${Math.random().toString(36).substring(2, 15)}`;

    // Step 2: Get a token for that specific room
    const tokenResp = await fetch(`/api/token?room=${encodeURIComponent(roomName)}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!tokenResp.ok) {
      throw new Error('Failed to get token for room');
    }
    const tokenData = await tokenResp.json();

    // Return connection details in the format expected by livekit-client
    return {
      serverUrl: tokenData.serverUrl || tokenData.server_url,
      roomName: tokenData.roomName || tokenData.room_name,
      participantToken: tokenData.participantToken || tokenData.participant_token,
      participantName: tokenData.participantName || tokenData.participant_name,
    };
  });
}