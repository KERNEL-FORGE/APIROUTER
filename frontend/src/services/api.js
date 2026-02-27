import axios from 'axios';

const API_BASE = '/api';

export const apiService = {
  getAll: () => axios.get(`${API_BASE}/apis/`),
  getById: (id) => axios.get(`${API_BASE}/apis/${id}/`),
  create: (data) => axios.post(`${API_BASE}/apis/`, data),
  update: (id, data) => axios.put(`${API_BASE}/apis/${id}/`, data),
  delete: (id) => axios.delete(`${API_BASE}/apis/${id}/`),
  start: (id) => axios.post(`${API_BASE}/apis/${id}/start/`),
  stop: (id) => axios.post(`${API_BASE}/apis/${id}/stop/`),
  getLogs: (id) => axios.get(`${API_BASE}/apis/${id}/logs/`),
  upload: (formData) => axios.post(`${API_BASE}/upload/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};
