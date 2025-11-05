import axios from 'axios';

const API_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,  // ВАЖНО: для отправки куков
});

api.interceptors.request.use(
  (config) => {
    const accessToken = getCookie('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = getCookie('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/api/token/refresh`, {}, {
            withCredentials: true
          });
          const newAccessToken = response.data.access;
          if (newAccessToken) {
            setCookie('access_token', newAccessToken, 15);
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return api(originalRequest);
          }
        } catch (refreshError) {
          logout();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }

    return Promise.reject(error);
  }
);

export const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
};

export const setCookie = (name, value, minutes) => {
  const date = new Date();
  date.setTime(date.getTime() + (minutes * 60 * 1000));
  document.cookie = `${name}=${value}; expires=${date.toUTCString()}; path=/; samesite=Lax`;
};

export const deleteCookie = (name) => {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
};

export const logout = () => {
  deleteCookie('access_token');
  deleteCookie('refresh_token');
  window.location.href = '/';
};

export const apiService = {
  get: (url) => api.get(url).then(response => response.data),
  post: (url, data) => api.post(url, data).then(response => response.data),
  put: (url, data) => api.put(url, data).then(response => response.data),
  delete: (url) => api.delete(url).then(response => response.data),
};

export const authAPI = {
  login: (credentials) => apiService.post('/api/login', credentials),
  register: (userData) => apiService.post('/api/register', userData),
  logout: () => apiService.post('/api/logout'),
  refreshToken: () => apiService.post('/api/token/refresh'),
  getMe: () => apiService.get('/api/me'),
};

export const blogAPI = {
  getArticles: () => apiService.get('/articles/'),
  getArticle: (id) => apiService.get(`/articles/${id}/`),
};

export default api;