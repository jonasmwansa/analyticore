import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/signin';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  verifyEmail: (token) => api.get(`/auth/verify-email?token=${token}`),
  getMe: () => api.get('/auth/me'),
  googleAuthCallback: (sessionId) => api.get(`/auth/session?session_id=${sessionId}`),
};

export const projectsAPI = {
  list: () => api.get('/projects/'),
  create: (data) => api.post('/projects/', data),
  get: (id) => api.get(`/projects/${id}/`),
  update: (id, data) => api.patch(`/projects/${id}/`, data),
  delete: (id) => api.delete(`/projects/${id}/`),
  uploadFile: (id, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/projects/${id}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getData: (id) => api.get(`/projects/${id}/data`),
  analyze: (id) => api.post(`/analysis/${id}/analyze`),
  transform: (id, rules) => api.post(`/analysis/${id}/transform`, { rules }),
};

export const exportsAPI = {
  exportData: (id, format) => api.get(`/exports/${id}/export?format=${format}`, { responseType: 'blob' }),
  getCharts: (id, type = 'all') => api.get(`/exports/${id}/charts?type=${type}`),
};

export const adminAPI = {
  getDashboard: () => api.get('/saas-admin/dashboard'),
  getUsers: () => api.get('/saas-admin/users'),
  getProjects: () => api.get('/saas-admin/projects'),
};

export const notificationsAPI = {
  list: (params = {}) => api.get('/notifications/', { params }),
  getSummary: () => api.get('/notifications/summary'),
  markRead: (notificationId) => api.post(`/notifications/${notificationId}/read`),
  markAllRead: () => api.post('/notifications/read-all'),
  delete: (notificationId) => api.delete(`/notifications/${notificationId}`),
  getPreferences: () => api.get('/notifications/preferences'),
  updatePreferences: (data) => api.put('/notifications/preferences', data),
  subscribePush: (subscription) => api.post('/notifications/push/subscribe', subscription),
  unsubscribePush: (endpoint) => api.delete('/notifications/push/unsubscribe', { data: { endpoint } }),
  getVapidKey: () => api.get('/notifications/push/vapid-key'),
  test: (type = 'system', sendEmail = false, sendPush = false) => 
    api.post('/notifications/test', { type, send_email: sendEmail, send_push: sendPush }),
};

export default api;
