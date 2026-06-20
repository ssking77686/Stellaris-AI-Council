import { useEffect, useRef } from 'react';

type WSHandler = (data: any) => void;

const listeners = new Map<string, Set<WSHandler>>();
let ws: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
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
      reconnectTimer = setTimeout(connect, 5000);
    }
  };

  ws.onerror = () => {
    ws?.close();
  };
}

export function useWebSocket(onMessage: WSHandler) {
  const handlerRef = useRef(onMessage);
  handlerRef.current = onMessage;

  useEffect(() => {
    const key = Symbol('ws');
    const handlerSet = new Set<WSHandler>();
    const wrapped: WSHandler = (data) => handlerSet.forEach((h) => h(data));
    handlerSet.add((data) => handlerRef.current(data));
    listeners.set(key.toString(), handlerSet);

    if (!ws || ws.readyState !== WebSocket.OPEN) connect();

    return () => {
      listeners.delete(key.toString());
    };
  }, []);
}
