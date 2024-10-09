import axios from 'axios';
import { refreshToken, logout } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const newToken = await refreshToken();
        if (newToken) {
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          return axiosInstance(originalRequest);
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        logout();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export const alerts = {
  getAll: async () => {
    const response = await axiosInstance.get('/alerts/');
    return response.data;
  },
};

export const iocs = {
  getAll: async () => {
    const response = await axiosInstance.get('/iocs/');
    return response.data;
  },
};

export const anomalies = {
  getAll: async () => {
    const response = await axiosInstance.get('/anomalies/');
    return response.data;
  },
  getDetails: async (id) => {
    const response = await axiosInstance.get(`/anomalies/${id}/`);
    return response.data;
  },
};

export const correlation = {
  run: async (timeWindow) => {
    const response = await axiosInstance.post('/correlation/run-correlation/', { time_window: timeWindow });
    return response.data;
  },
};

export const reports = {
  generate: async (reportType, emailNotification) => {
    const response = await axiosInstance.post('/data-processing/reports/generate/', { 
      report_type: reportType,
      email_notification: emailNotification
    });
    return response.data;
  },
  getAll: async () => {
    const response = await axiosInstance.get('/reports/');
    return response.data;
  },
  getById: async (id) => {
    const response = await axiosInstance.get(`/reports/${id}/`);
    return response.data;
  },
};

export const settings = {
  update: async (settingsData) => {
    const response = await axiosInstance.post('/settings/update/', settingsData);
    return response.data;
  },
};

export const securityEvents = {
  getAll: async () => {
    const response = await axiosInstance.get('/security-events/');
    return response.data;
  },
  getRecent: async () => {
    const response = await axiosInstance.get('/security-events/recent/');
    return response.data;
  },
  getSummary: async () => {
    const response = await axiosInstance.get('/security-events/summary/');
    return response.data;
  },
  runMLAnomalyDetection: async () => {
    const response = await axiosInstance.post('/run-ml-anomaly-detection/');
    return response.data;
  },
  initiateLogCollection: async () => {
    const response = await axiosInstance.post('/data-processing/initiate-log-collection/');
    return response.data;
  },
  stopLogCollection: async (taskId) => {
    const response = await axiosInstance.post('/data-processing/stop-log-collection/', { task_id: taskId });
    return response.data;
  },
  checkTaskStatus: async (taskId) => {
    const response = await axiosInstance.get(`/data-processing/check-task-status/${taskId}/`);
    return response.data;
  },
};

export const threatIntelligence = {
  updateFeed: async () => {
    const response = await axiosInstance.post('/threat-feeds/update/');
    return response.data;
  },
  getAll: async () => {
    const response = await axiosInstance.get('/threat-feeds/');
    return response.data;
  },
  search: async (value) => {
    const response = await axiosInstance.get(`/threat-feeds/search/?value=${value}`);
    return response.data;
  },
};

export default axiosInstance;