import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiService = {
  async checkHealth() {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },

  async processImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(`${API_BASE_URL}/process-image`, formData);
    return response.data;
  },

  async downloadReport(reportId) {
    const response = await axios.get(`${API_BASE_URL}/download-report/${reportId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  getImageUrl(relativeUrl) {
    if (!relativeUrl) return '';
    if (relativeUrl.startsWith('http://') || relativeUrl.startsWith('https://')) {
      return relativeUrl;
    }
    return `${API_BASE_URL}${relativeUrl}`;
  },
};
