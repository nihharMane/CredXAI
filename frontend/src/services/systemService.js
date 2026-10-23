
import apiClient from './apiClient';
import { createCorrelationId, logger } from '../utils/logger';

/**
 * Check the health of a deployed ML service.
 * The service URL must come from the frontend environment variables.
 */
async function checkMlHealth(baseUrl) {
  if (!baseUrl) {
    return {
      status: 'UNREACHABLE',
      error: 'ML service URL is missing from environment variables',
    };
  }

  try {
    const url = `${baseUrl.replace(/\/+$/, '')}/health`;
    const correlationId = createCorrelationId();

    const response = await fetch(url, {
      signal: AbortSignal.timeout(10000),
      headers: { 'X-Correlation-ID': correlationId },
    });

    if (!response.ok) {
      logger.warn('health.ml.unavailable', { status: response.status, correlationId });
      return {
        status: 'OFFLINE',
        error: `Health check returned HTTP ${response.status}`,
      };
    }

    const text = await response.text();
    let data = text;

    try {
      data = JSON.parse(text);
    } catch {
      // Support plain-text health responses.
    }

    const isHealthy =
      data === true ||
      data === 'true' ||
      (typeof data === 'string' &&
        ['ok', 'healthy'].includes(data.trim().toLowerCase())) ||
      data?.model_loaded === true ||
      ['healthy', 'ok'].includes(
        String(data?.status ?? '').toLowerCase()
      );

    logger.debug('health.ml.checked', { status: isHealthy ? 'ONLINE' : 'OFFLINE', correlationId });
    return {
      status: isHealthy ? 'ONLINE' : 'OFFLINE',
      details: data,
    };
  } catch (error) {
    logger.warn('health.ml.unreachable', { errorType: error?.name || 'Error' });
    return {
      status: 'UNREACHABLE',
      error: error.message,
    };
  }
}

/**
 * Service to check Spring Boot and ML service health.
 */
const systemService = {
  /**
   * Check Spring Boot backend health.
   */
  async checkBackend() {
    try {
      const start = Date.now();

      await apiClient.get('/api/auth/health', {
        timeout: 3000,
      });

      return {
        status: 'ONLINE',
        latency: Date.now() - start,
      };
    } catch (err) {
      if (
        err.response &&
        [401, 403].includes(err.response.status)
      ) {
        return {
          status: 'ONLINE',
          port: 8080,
        };
      }

      return {
        status: 'OFFLINE',
        error: err.message,
      };
    }
  },

  /**
   * Check deployed Traditional ML service.
   */
  async checkTraditionalMl() {
    return checkMlHealth(
      import.meta.env.VITE_TRADITIONAL_ML_URL
    );
  },

  /**
   * Check deployed Alternative ML service.
   */
  async checkAlternativeMl() {
    return checkMlHealth(
      import.meta.env.VITE_ALTERNATIVE_ML_URL
    );
  },
};

export default systemService;
