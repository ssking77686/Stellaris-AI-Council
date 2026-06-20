import { useEffect, useRef } from 'react';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type WSHandler = (data: any) => void;

export type { WSHandler };

const listeners = new Map<string, Set<WSHandler>>();
let ws: WebSocket | null = null;
let retryCount = 0;
const MAX_RETRIES = 3;

function connect() {
  if (ws && ws.readyState === WebSocket.OPEN) return;
  ws = new WebSocket('ws://localhost:8001/ws');

  ws.onopen = () => { retryCount = 0; };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === 'pong') return;
      listeners.forEach((handlers) => handlers.forEach((h) => h(msg)));
    } catch { /* ignore parse errors */ }
  };

  ws.onclose = () => {
    if (retryCount < MAX_RETRIES) {
      retryCount++;
      setTimeout(connect, 5000);
    }
  };

  ws.onerror = () => {
    ws?.close();
  };
}

export function useWebSocket(onMessage: WSHandler) {
  const handlerRef = useRef(onMessage);

  useEffect(() => {
    handlerRef.current = onMessage;
  });

  useEffect(() => {
    const key = Symbol('ws');
    const handlerSet = new Set<WSHandler>();
    handlerSet.add((data) => handlerRef.current(data));
    listeners.set(key.toString(), handlerSet);

    if (!ws || ws.readyState !== WebSocket.OPEN) connect();

    return () => {
      listeners.delete(key.toString());
    };
  }, []);
}
