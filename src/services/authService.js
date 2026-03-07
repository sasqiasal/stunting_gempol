/**
 * Authentication Service
 * Service untuk login, register, dan get current user
 */

import apiClient from './api';

export const authService = {
  /**
   * Login user
   * @param {Object} credentials - Email dan password
   * @returns {Promise}
   */
  login: async (credentials) => {
    const response = await apiClient.post('/auth/login', credentials);
    
    console.log('🔐 LOGIN RESPONSE from backend:', response.data);
    console.log('🔐 User object:', response.data.user);
    console.log('🔐 User posyandu_id:', response.data.user?.posyandu_id);
    
    // Simpan token dan user data
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      console.log('💾 Saved to localStorage:', JSON.parse(localStorage.getItem('user')));
      
      // Log login activity ke database
      try {
        await apiClient.post('/akun/login-logs', {
          user_id: response.data.user.id,
          user_name: response.data.user.nama_lengkap,
          user_email: response.data.user.email,
          user_role: response.data.user.role
        });
      } catch (error) {
        // Jangan fail login jika log gagal
        console.warn('Failed to log login activity:', error);
      }
    }
    
    return response.data;
  },

  /**
   * Register user baru
   * @param {Object} userData - Data user
   * @returns {Promise}
   */
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  /**
   * Get current user
   * @returns {Promise}
   */
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },

  /**
   * Logout user
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  /**
   * Get user from localStorage
   * @returns {Object|null}
   */
  getUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};
