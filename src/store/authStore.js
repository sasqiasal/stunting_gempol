/**
 * Auth Store
 * Global state untuk authentication menggunakan Zustand
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '../services/authService';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      /**
       * Initialize auth from localStorage
       */
      initialize: () => {
        const token = localStorage.getItem('access_token');
        const user = authService.getUser();
        
        if (token && user) {
          set({ user, isAuthenticated: true });
        } else {
          set({ user: null, isAuthenticated: false });
        }
      },

      /**
       * Login action
       */
      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const data = await authService.login(credentials);
          set({ 
            user: data.user, 
            isAuthenticated: true, 
            isLoading: false,
            error: null
          });
          return data;
        } catch (error) {
          const status = error.response?.status;
          const detail = error.response?.data?.detail;
          let message;
          if (status === 401 || status === 400) {
            message = "Password salah. Silakan coba lagi atau hubungi admin.";
          } else if (detail) {
            message = detail;
          } else {
            message = "Login gagal. Silakan hubungi admin.";
          }
          set({ 
            user: null,
            isAuthenticated: false,
            error: message, 
            isLoading: false 
          });
          throw error;
        }
      },

      /**
       * Logout action
       */
      logout: () => {
        authService.logout();
        set({ user: null, isAuthenticated: false });
      },

      /**
       * Refresh user data
       */
      refreshUser: async () => {
        try {
          const user = await authService.getCurrentUser();
          set({ user, isAuthenticated: true });
        } catch (error) {
          console.error('Failed to refresh user:', error);
          set({ user: null, isAuthenticated: false });
        }
      },

      /**
       * Clear error
       */
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
