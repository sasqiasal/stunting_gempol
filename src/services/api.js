/**
 * Axios Client untuk API Backend
 * Base URL dari environment variable atau auto-detect
 */

import axios from 'axios';

// Smart detection: Jika di production (Vercel), gunakan relative path
// Jika di development (lokal), gunakan environment variable
const API_BASE_URL = 
  import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.PROD ? '/api/v1' : 'http://localhost:8000/api/v1'); 

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor untuk menambahkan token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor untuk handle error
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
      // Unauthorized - redirect to login (only for protected endpoints, not login itself)
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
