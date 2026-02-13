const toWebSocketUrl = (baseUrl) => {
  if (!baseUrl) {
    return '';
  }
  if (baseUrl.startsWith('https://')) {
    return baseUrl.replace('https://', 'wss://');
  }
  if (baseUrl.startsWith('http://')) {
    return baseUrl.replace('http://', 'ws://');
  }
  return baseUrl;
};

export const createRealtimeClient = ({ onMessage, onOpen, onClose, onError }) => {
  const enabled = (import.meta.env.VITE_WS_ENABLED || 'false').toLowerCase() === 'true';
  const baseApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const wsBase = import.meta.env.VITE_WS_URL || toWebSocketUrl(baseApiUrl);
  const wsPath = import.meta.env.VITE_WS_PATH || '/ws';
  const reconnectMs = Number(import.meta.env.VITE_WS_RECONNECT_MS || 3000);

  if (!enabled) {
    return {
      enabled: false,
      connect: () => {},
      close: () => {},
    };
  }

  let socket = null;
  let reconnectTimer = null;
  let shouldReconnect = true;

  const scheduleReconnect = () => {
    if (!shouldReconnect) {
      return;
    }
    reconnectTimer = setTimeout(connect, reconnectMs);
  };

  const connect = () => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      socket = new WebSocket(`${wsBase}${wsPath}`);
    } catch (err) {
      onError?.(err);
      scheduleReconnect();
      return;
    }

    socket.onopen = () => {
      onOpen?.();
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        onMessage?.(payload);
      } catch (err) {
        onError?.(err);
      }
    };

    socket.onclose = () => {
      onClose?.();
      scheduleReconnect();
    };

    socket.onerror = (err) => {
      onError?.(err);
    };
  };

  const close = () => {
    shouldReconnect = false;
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    if (socket) {
      socket.close();
      socket = null;
    }
  };

  return {
    enabled: true,
    connect,
    close,
  };
};
