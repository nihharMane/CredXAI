import apiClient from './apiClient';

/**
 * Prediction Service calling Spring Boot endpoints:
 * - POST /api/predictions/traditional
 * - POST /api/predictions/alternative
 */
export const predictionService = {
  /**
   * Run traditional credit prediction
    * @param {Object} payload TraditionalPredictionRequest
   */
  async predictTraditional(payload) {
    const response = await apiClient.post('/api/predictions/traditional', payload);
    return response.data;
  },

  /**
   * Run alternative-data credit prediction
    * @param {Object} payload AlternativePredictionRequest
   */
  async predictAlternative(payload) {
    const response = await apiClient.post('/api/predictions/alternative', payload);
    return response.data;
  },

  /**
   * Fetch authenticated user's credit application history
   * Calls GET /api/predictions/history (requires Bearer token)
   */
  async getHistory() {
    const response = await apiClient.get('/api/predictions/history');
    return response.data;
  },

  async getApplication(applicationId) {
    const response = await apiClient.get(`/api/predictions/history/${applicationId}`);
    return response.data;
  },

  async getReviewUpdates(applicationId) {
    const response = await apiClient.get(`/api/predictions/history/${applicationId}/reviews`);
    return response.data;
  },
};

export default predictionService;
