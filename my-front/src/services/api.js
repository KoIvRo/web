import axios from 'axios';

const API_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Функции для работы с куками
export const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
};

export const setCookie = (name, value, minutes) => {
  const date = new Date();
  date.setTime(date.getTime() + (minutes * 60 * 1000));
  document.cookie = `${name}=${value}; expires=${date.toUTCString()}; path=/; samesite=lax`;
};

export const deleteCookie = (name) => {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
};

export const logout = () => {
  deleteCookie('access_token');
  deleteCookie('refresh_token');
  window.location.href = '/';
};

// Перехватчик для автоматического refresh токена
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Если ошибка 401 и это не запрос на refresh
    if (error.response?.status === 401 && 
        !originalRequest._retry && 
        !originalRequest.url.includes('/api/token/refresh')) {
      
      originalRequest._retry = true;
      
      const refreshToken = getCookie('refresh_token');
      if (refreshToken) {
        try {
          console.log('Access token expired, trying to refresh...');
          
          // Пытаемся обновить токен
          const response = await axios.post(`${API_URL}/api/token/refresh`, {}, {
            withCredentials: true
          });
          
          const newAccessToken = response.data.access;
          if (newAccessToken) {
            setCookie('access_token', newAccessToken, 15);
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            console.log('Token refreshed successfully');
            return api(originalRequest);
          }
        } catch (refreshError) {
          console.error('Refresh token failed:', refreshError);
          logout();
          return Promise.reject(refreshError);
        }
      } else {
        logout();
      }
    }

    return Promise.reject(error);
  }
);

// Перехватчик для добавления токена в запросы
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

// API методы
export const apiService = {
  get: (url) => api.get(url).then(response => response.data),
  post: (url, data) => api.post(url, data).then(response => response.data),
  put: (url, data) => api.put(url, data).then(response => response.data),
  delete: (url) => api.delete(url).then(response => response.data),
};

// Аутентификация
export const authAPI = {
  login: (credentials) => apiService.post('/api/login', credentials),
  register: (userData) => apiService.post('/api/register', userData),
  logout: () => apiService.post('/api/logout'),
  refreshToken: () => apiService.post('/api/token/refresh'),
  getMe: () => apiService.get('/api/me'),
};

// Посты и комментарии
export const blogAPI = {
  getArticles: () => apiService.get('/articles/'),
  getArticle: (id) => apiService.get(`/articles/${id}`),
  getArticlesByCategory: (category) => apiService.get(`/articles/category/${category}`),
  createArticle: (data) => apiService.post('/articles/', data),
  updateArticle: (id, data) => apiService.put(`/articles/${id}`, data),
  deleteArticle: (id) => apiService.delete(`/articles/${id}`),
  
  getComments: (postId) => apiService.get(`/articles/${postId}/comments`),
  createComment: (data) => apiService.post('/comments/', data),
  updateComment: (id, data) => apiService.put(`/comments/${id}`, data),
  deleteComment: (id) => apiService.delete(`/comments/${id}`),
  
  getCategories: () => apiService.get('/categories/'),
};

export default api;