import axios from 'axios';
import { createCorrelationId, logger } from '../utils/logger';

// Use environment variable if provided, otherwise default to relative path leveraging Vite proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to attach JWT Bearer token
apiClient.interceptors.request.use(
  (config) => {
    const correlationId = createCorrelationId();
    config.headers['X-Correlation-ID'] = correlationId;
    try {
      const storedAuth = localStorage.getItem('credxai_auth');
      if (storedAuth) {
        const parsed = JSON.parse(storedAuth);
        if (parsed?.token) {
          config.headers.Authorization = `Bearer ${parsed.token}`;
        }
      }
    } catch (e) {
      logger.warn('auth.storage.read_failed', { errorType: e?.name || 'Error' });
    }
    logger.debug('api.request.started', { method: String(config.method || 'get').toUpperCase(), correlationId });
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401 Unauthorized (expired or invalid token)
apiClient.interceptors.response.use(
  (response) => {
    const correlationId = response.headers?.['x-correlation-id']
      || response.config?.headers?.['X-Correlation-ID'];
    logger.debug('api.request.succeeded', {
      method: String(response.config?.method || 'get').toUpperCase(),
      status: response.status,
      ...(correlationId ? { correlationId } : {}),
    });
    return response;
  },
  (error) => {
    if (error && typeof error === 'object') error.__credxaiLogged = true;
    const status = error.response?.status;
    const correlationId = error.response?.headers?.['x-correlation-id']
      || error.config?.headers?.['X-Correlation-ID']
      || error.config?.headers?.['x-correlation-id'];
    const metadata = {
      method: String(error.config?.method || 'unknown').toUpperCase(),
      status: status || 0,
      code: error.code || 'HTTP_ERROR',
      ...(correlationId ? { correlationId } : {}),
    };
    if (status === 401 || status === 403) logger.warn('api.request.rejected', metadata);
    else logger.error('api.request.failed', metadata);
    if (error.response && error.response.status === 401) {
      // Clear credentials if token is invalid or expired
      const isAuthRequest = error.config?.url?.includes('/api/auth/');
      if (!isAuthRequest) {
        localStorage.removeItem('credxai_auth');
        // Dispatch custom event so AuthContext can cleanly trigger unauthenticated state
        window.dispatchEvent(new CustomEvent('credxai:unauthorized'));
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
