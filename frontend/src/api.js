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

export const analysisAPI = {
  getStatistics: (id) => api.get(`/analysis/${id}/statistics`),
  getCorrelation: (id, method = 'pearson') => api.get(`/analysis/${id}/correlation?method=${method}`),
  getDistribution: (id, column = null, bins = 20) => {
    const params = new URLSearchParams({ bins });
    if (column) params.append('column', column);
    return api.get(`/analysis/${id}/distribution?${params}`);
  },
  getChartData: (id, type, options = {}) => {
    const params = new URLSearchParams({ type, ...options });
    return api.get(`/analysis/${id}/chart?${params}`);
  },
  getColumnInfo: (id, column) => api.get(`/analysis/${id}/column?column=${column}`),
  getColumns: (id) => api.get(`/analysis/${id}/columns`),
  getQuickInsights: (id) => api.get(`/analysis/${id}/insights`),
  getColumnActions: (id, column = null) => {
    const url = column 
      ? `/analysis/${id}/column-actions?column=${column}`
      : `/analysis/${id}/column-actions`;
    return api.get(url);
  },
  applyColumnAction: (id, data) => api.post(`/analysis/${id}/apply-action`, data),
  
  // Magic Analysis - One-Click Analysis
  runMagicAnalysis: (id) => api.get(`/analysis/${id}/magic-analyze`),
  applyMagicCleaning: (id, actions) => api.post(`/analysis/${id}/magic-apply-cleaning`, { actions }),
  exportAnalysisReport: (id, format = 'excel') => api.get(`/analysis/${id}/magic-export?format=${format}`),
};

export const mlAPI = {
  // ML Info
  getMLInfo: (id) => api.get(`/analysis/${id}/ml/info`),
  
  // Model Training
  trainModel: (id, data) => api.post(`/analysis/${id}/ml/train`, data),
  listModels: (id) => api.get(`/analysis/${id}/ml/models`),
  deleteModel: (id, modelId) => api.delete(`/analysis/${id}/ml/models/${modelId}`),
  predict: (id, modelId) => api.post(`/analysis/${id}/ml/predict`, { model_id: modelId }),
  
  // Auto-ML
  autoML: (id, data) => api.post(`/analysis/${id}/ml/auto`, data),
  
  // Clustering
  findOptimalClusters: (id, features = [], maxK = 10) => {
    const params = new URLSearchParams({ max_k: maxK });
    features.forEach(f => params.append('features', f));
    return api.get(`/analysis/${id}/ml/cluster/optimal?${params}`);
  },
  runClustering: (id, data) => api.post(`/analysis/${id}/ml/cluster`, data),
  
  // PCA
  runPCA: (id, nComponents = null, features = []) => {
    const params = new URLSearchParams();
    if (nComponents) params.append('n_components', nComponents);
    features.forEach(f => params.append('features', f));
    return api.get(`/analysis/${id}/ml/pca?${params}`);
  },
};

export const exportsAPI = {
  exportData: (id, format) => api.get(`/exports/${id}/export?format=${format}`, { responseType: 'blob' }),
  getCharts: (id, type = 'all') => api.get(`/exports/${id}/charts?type=${type}`),
};

export const adminAPI = {
  getDashboard: () => api.get('/saas-admin/dashboard'),
  getUsers: () => api.get('/saas-admin/users'),
  getProjects: () => api.get('/saas-admin/projects'),
  
  // Enhanced Analytics APIs
  getSummary: () => api.get('/saas-admin/analytics/summary'),
  getUserMetrics: () => api.get('/saas-admin/analytics/users'),
  getUserGrowth: (days = 30) => api.get(`/saas-admin/analytics/user-growth?days=${days}`),
  getActivityAnalytics: (days = 30) => api.get(`/saas-admin/analytics/activity?days=${days}`),
  getProjectAnalytics: (days = 30) => api.get(`/saas-admin/analytics/projects?days=${days}`),
  getPipelineAnalytics: (days = 30) => api.get(`/saas-admin/analytics/pipelines?days=${days}`),
  getSubscriptionAnalytics: () => api.get('/saas-admin/analytics/subscriptions'),
  getRetentionAnalytics: () => api.get('/saas-admin/analytics/retention'),
  getFunnelAnalytics: () => api.get('/saas-admin/analytics/funnel'),
  getActivityFeed: (limit = 50) => api.get(`/saas-admin/analytics/feed?limit=${limit}`),
  getSystemHealth: () => api.get('/saas-admin/analytics/health'),
  
  // Alert Settings
  getAlertSettings: () => api.get('/saas-admin/settings/alerts'),
  updateAlertSettings: (data) => api.put('/saas-admin/settings/alerts/update', data),
  testAlertEmail: () => api.post('/saas-admin/settings/alerts/test-email'),
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

export const integrationsAPI = {
  // Google Sheets
  getSheetsStatus: () => api.get('/integrations/google-sheets/status'),
  getSheetsAuthUrl: () => api.get('/integrations/google-sheets/auth'),
  disconnectSheets: () => api.post('/integrations/google-sheets/disconnect'),
  listSpreadsheets: () => api.get('/integrations/google-sheets/list'),
  getSpreadsheetMetadata: (spreadsheetId) => api.get(`/integrations/google-sheets/${spreadsheetId}/metadata`),
  previewSpreadsheet: (spreadsheetId, data) => api.post(`/integrations/google-sheets/${spreadsheetId}/preview`, data),
  importFromSheets: (projectId, data) => api.post(`/integrations/google-sheets/${projectId}/import`, data),
  
  // Database Connections
  testMySQLConnection: (data) => api.post('/integrations/mysql/test', data),
  testPostgreSQLConnection: (data) => api.post('/integrations/postgresql/test', data),
  importFromDatabase: (projectId, data) => api.post(`/integrations/database/${projectId}/import`, data),
  
  // Data Sources
  listDataSources: () => api.get('/integrations/sources'),
  createDataSource: (data) => api.post('/integrations/sources/create', data),
  deleteDataSource: (sourceId) => api.delete(`/integrations/sources/${sourceId}`),
};

export const pipelinesAPI = {
  // Schedules
  listSchedules: () => api.get('/pipelines/schedules/'),
  createSchedule: (data) => api.post('/pipelines/schedules/create/', data),
  getSchedule: (scheduleId) => api.get(`/pipelines/schedules/${scheduleId}/`),
  updateSchedule: (scheduleId, data) => api.put(`/pipelines/schedules/${scheduleId}/update/`, data),
  deleteSchedule: (scheduleId) => api.delete(`/pipelines/schedules/${scheduleId}/delete/`),
  toggleSchedule: (scheduleId) => api.post(`/pipelines/schedules/${scheduleId}/toggle/`),
  runNow: (scheduleId) => api.post(`/pipelines/schedules/${scheduleId}/run/`),
  getStats: () => api.get('/pipelines/schedules/stats/'),
  
  // Runs
  listRuns: () => api.get('/pipelines/runs/'),
  getRunDetails: (runId) => api.get(`/pipelines/runs/${runId}/`),
};

export default api;
