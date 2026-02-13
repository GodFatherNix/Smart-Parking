import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';
const API_KEY_HEADER = import.meta.env.VITE_API_KEY_HEADER || 'X-API-Key';
const API_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 10000);
const RETRY_ATTEMPTS = Number(import.meta.env.VITE_API_RETRY_ATTEMPTS || 2);
const RETRY_DELAY_MS = Number(import.meta.env.VITE_API_RETRY_DELAY_MS || 500);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
    ...(API_KEY ? { [API_KEY_HEADER]: API_KEY } : {}),
  },
});

// Request interceptor with retry metadata.
apiClient.interceptors.request.use(
  (config) => {
    config.metadata = {
      startTime: Date.now(),
      retryCount: config.metadata?.retryCount || 0,
    };

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for latency visibility and retry behavior.
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const config = error.config || {};
    const method = (config.method || 'get').toLowerCase();
    const status = error.response?.status;
    const isRetryableMethod = ['get', 'head', 'options'].includes(method) || config.retryable === true;
    const isRetryableStatus = !status || status >= 500 || status === 429;
    const currentRetryCount = config.metadata?.retryCount || 0;

    if (isRetryableMethod && isRetryableStatus && currentRetryCount < RETRY_ATTEMPTS) {
      config.metadata = { ...(config.metadata || {}), retryCount: currentRetryCount + 1 };
      const backoffMs = RETRY_DELAY_MS * (currentRetryCount + 1);

      await new Promise((resolve) => setTimeout(resolve, backoffMs));
      return apiClient(config);
    }

    const userMessage =
      error.response?.data?.detail ||
      error.response?.data?.error ||
      error.message ||
      'Request failed';

    error.userMessage = userMessage;

    return Promise.reject(error);
  }
);

export default apiClient;
