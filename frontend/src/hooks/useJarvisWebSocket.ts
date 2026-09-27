'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { createWebSocket, ActivityEvent, sendWsMessage } from '@/lib/jarvis-api';

export function useJarvisWebSocket(
  onEvent: (event: ActivityEvent) => void,
  conversationId: string = 'default'
) {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const onEventRef = useRef(onEvent);
  const isIntentionalCloseRef = useRef(false);

  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  const connect = useCallback(() => {
    // If socket is already open or actively connecting, do not create duplicate
    if (
      wsRef.current &&
      (wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    isIntentionalCloseRef.current = false;

    try {
      const ws = createWebSocket(
        (event) => onEventRef.current(event),
        () => {
          setConnected(true);
          setError(null);
          reconnectAttempts.current = 0;
          // Send lightweight keepalive ping handshake
          sendWsMessage(ws, 'ping', { timestamp: Date.now() });
        },
        () => {
          setConnected(false);
          if (!isIntentionalCloseRef.current) {
            // Attempt reconnect with exponential backoff
            const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 15000);
            reconnectAttempts.current += 1;
            if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = setTimeout(connect, delay);
          }
        },
        () => {
          // Standard browser WebSocket error events contain no message properties.
          // Log a clean warning and allow onclose to manage backoff reconnection.
          setError('WebSocket offline or reconnecting');
          console.warn('[JARVIS WS] Connection notice: server offline or socket closed, retrying...');
        }
      );
      wsRef.current = ws;
    } catch (err) {
      setError('Failed to initialize WebSocket');
      console.warn('[JARVIS WS] Failed to create WebSocket:', err);
    }
  }, []);

  const sendMessage = useCallback(
    (message: string, model?: string) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        sendWsMessage(wsRef.current, 'chat', {
          message,
          conversation_id: conversationId,
          ...(model ? { model } : {}),
        });
      }
    },
    [conversationId]
  );

  const selectModelWs = useCallback((model: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      sendWsMessage(wsRef.current, 'model.select', { model });
    }
  }, []);

  const sendConfirm = useCallback(
    (actionId: string, approved: boolean) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        sendWsMessage(wsRef.current, 'confirm', { action_id: actionId, approved });
      }
    },
    []
  );

  const disconnect = useCallback(() => {
    isIntentionalCloseRef.current = true;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { connected, error, sendMessage, selectModelWs, sendConfirm, disconnect };
}