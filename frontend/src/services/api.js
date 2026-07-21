import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('DEBUG API REQUEST:', config.method?.toUpperCase(), config.url, config.data);
    return config;
  },
  (error) => {
    console.log('DEBUG API REQUEST ERROR:', error);
    return Promise.reject(error);
  }
);

// Handle token refresh
api.interceptors.response.use(
  (response) => {
    console.log('DEBUG API RESPONSE:', response.config.url, response.status, response.data);
    return response;
  },
  async (error) => {
    console.log('DEBUG API ERROR:', error.config?.url, error.response?.status, error.response?.data, error.message);
    const originalRequest = error.config;
    // Don't attempt refresh on login endpoint or if already retried
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/login/')) {
      console.log('DEBUG: Attempting token refresh');
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      try {
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        console.log('DEBUG: Token refresh failed', refreshError);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login/', { username, password }),
  logout: (refresh) =>
    api.post('/auth/logout/', { refresh }),
  changePassword: (oldPassword, newPassword) =>
    api.post('/auth/change-password/', { old_password: oldPassword, new_password: newPassword }),
  forgotPassword: (username, currentPassword, newPassword) =>
    api.post('/auth/forgot-password/', { username, current_password: currentPassword, new_password: newPassword }),
  resetDriverPassword: (driverId, newPassword) =>
    api.post('/auth/reset-driver-password/', { driver_id: driverId, new_password: newPassword }),
  getCurrentUser: () => api.get('/auth/me/'),
};

export const driverAPI = {
  list: () => api.get('/drivers/'),
  create: (data) => api.post('/drivers/', data),
  get: (id) => api.get(`/drivers/${id}/`),
  update: (id, data) => api.put(`/drivers/${id}/`, data),
  delete: (id) => api.delete(`/drivers/${id}/`),
};

export const tripAPI = {
  list: (params) => api.get('/trips/', { params }),
  create: (data) => api.post('/trips/', data),
  get: (id) => api.get(`/trips/${id}/`),
  update: (id, data) => api.put(`/trips/${id}/`, data),
  delete: (id) => api.delete(`/trips/${id}/`),
};

export const salaryAPI = {
  list: () => api.get('/salary/'),
  create: (data) => api.post('/salary/', data),
  get: (id) => api.get(`/salary/${id}/`),
  update: (id, data) => api.put(`/salary/${id}/`, data),
  delete: (id) => api.delete(`/salary/${id}/`),
};

export const billAPI = {
  list: () => api.get('/bills/'),
  create: (data) => api.post('/bills/', data),
  get: (id) => api.get(`/bills/${id}/`),
  generatePDF: (tripId) => api.get(`/bills/generate/${tripId}/`, { responseType: 'blob' }),
};

export const reportAPI = {
  summary: (range) => api.get('/reports/summary/', { params: { range } }),
};

export const auditLogAPI = {
  list: (params) => api.get('/audit-logs/', { params }),
};

export default api;
