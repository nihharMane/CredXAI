import apiClient from './apiClient';

const adminService = {
  async dashboard() { return (await apiClient.get('/api/admin/dashboard')).data; },
  async applications(params) { return (await apiClient.get('/api/admin/applications', { params })).data; },
  async detail(id) { return (await apiClient.get(`/api/admin/applications/${id}`)).data; },
  async reviews(id) { return (await apiClient.get(`/api/admin/applications/${id}/reviews`)).data; },
  async addReview(id, payload) { return (await apiClient.post(`/api/admin/applications/${id}/reviews`, payload)).data; },
};
export default adminService;
