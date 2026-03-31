/**
 * Authentication Service
 * Service untuk login, register, dan get current user
 * Dioptimalkan untuk sistem Stunting Desa Gempol
 */

import apiClient from './api';

export const authService = {
  /**
   * Login user
   * @param {Object} credentials - Email dan password
   */
  login: async (credentials) => {
    try {
      console.log('🔐 Login attempt:', { email: credentials.email });
      console.log('📡 API Base URL:', apiClient.defaults.baseURL);
      
      const response = await apiClient.post('/auth/login', credentials);
      
      const { access_token, user } = response.data;

      // 1. Simpan token dan data user ke localStorage jika login berhasil
      if (access_token && user) {
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
        
        console.log('✅ Login Berhasil:', user.nama_lengkap);

        /**
         * 2. Log login activity ke database (Background Process)
         * Kunci: Jangan gunakan 'await' di sini agar tidak menghambat loading dashboard
         */
        apiClient.post('/akun/login-logs', {
          user_id: user.id,
          user_name: user.nama_lengkap,
          user_email: user.email,
          user_role: user.role
        }).catch(err => {
          console.warn('⚠️ Log aktivitas gagal (abaikan):', err.message);
        });

      } else {
        throw new Error("Data user tidak ditemukan dalam respon server.");
      }
      
      return response.data;

    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      console.error('❌ Login Error:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        detail: errorMsg,
        fullUrl: error.config?.url,
        method: error.config?.method
      });
      throw error; // Lempar error agar bisa ditangkap oleh UI (LoginPage)
    }
  },

  /**
   * Register user baru
   */
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  /**
   * Mendapatkan data user terbaru dari server
   */
  getCurrentUser: async () => {
    try {
      const response = await apiClient.get('/auth/me');
      if (response.data) {
        localStorage.setItem('user', JSON.stringify(response.data));
      }
      return response.data;
    } catch (error) {
      console.error('Gagal mengambil data user:', error);
      return null;
    }
  },

  /**
   * Logout user dan bersihkan session
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    // Redirect langsung ke login
    window.location.href = '/login';
  },

  /**
   * Cek status autentikasi
   */
  isAuthenticated: () => {
    const token = localStorage.getItem('access_token');
    return !!token;
  },

  /**
   * Ambil data user dari penyimpanan lokal
   */
  getUser: () => {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch (e) {
      return null;
    }
  },
};