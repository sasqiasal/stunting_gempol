/**
 * Service untuk Manajemen Akun (Admin Only)
 * - Get login logs
 * - Create new user
 * - Get account statistics
 */

import api from './api';

/**
 * Get login logs (audit trail)
 */
export const getLoginLogs = async (limit = 100) => {
  try {
    const response = await api.get(`/akun/login-logs?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching login logs:', error);
    throw error.response?.data || { detail: 'Gagal mengambil data login logs' };
  }
};

/**
 * Create new user (Admin only)
 */
export const createNewUser = async (userData) => {
  try {
    const response = await api.post('/akun/create-user', userData);
    return response.data;
  } catch (error) {
    console.error('Error creating user:', error);
    throw error.response?.data || { detail: 'Gagal membuat user baru' };
  }
};

/**
 * Get account statistics
 */
export const getAccountStats = async () => {
  try {
    const response = await api.get('/akun/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching account stats:', error);
    throw error.response?.data || { detail: 'Gagal mengambil statistik akun' };
  }
};

/**
 * Get all users (Admin only)
 */
export const getAllUsers = async () => {
  try {
    const response = await api.get('/akun/users');
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error.response?.data || { detail: 'Gagal mengambil daftar user' };
  }
};

/**
 * Reset user password (Admin only)
 */

/**
 * Delete user (Admin only)
 */

/**
 * Update user (Admin only)
 */
export const updateUser = async (userId, userData) => {
  try {
    const response = await api.put(`/akun/users/${userId}`, userData);
    return response.data;
  } catch (error) {
    console.error('Error updating user:', error);
    throw error.response?.data || { detail: 'Gagal mengupdate user' };
  }
};

export const deleteUser = async (userId) => {
  try {
    const response = await api.delete(`/akun/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting user:', error);
    throw error.response?.data || { detail: 'Gagal menghapus user' };
  }
};

export const resetUserPassword = async (userId, newPassword) => {
  try {
    const response = await api.post('/akun/reset-password', {
      user_id: userId,
      new_password: newPassword
    });
    return response.data;
  } catch (error) {
    console.error('Error resetting password:', error);
    throw error.response?.data || { detail: 'Gagal reset password' };
  }
};

/**
 * Helper untuk format tanggal login
 */
export const formatLoginTime = (timestamp) => {
  const date = new Date(timestamp);
  return new Intl.DateTimeFormat('id-ID', {
    dateStyle: 'medium',
    timeStyle: 'medium'
  }).format(date);
};

/**
 * Helper untuk format relative time (e.g., "2 jam yang lalu")
 */
export const getRelativeTime = (timestamp) => {
  const now = new Date();
  const past = new Date(timestamp);
  const diffMs = now - past;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return 'Baru saja';
  if (diffMin < 60) return `${diffMin} menit yang lalu`;
  if (diffHour < 24) return `${diffHour} jam yang lalu`;
  if (diffDay < 7) return `${diffDay} hari yang lalu`;
  
  return formatLoginTime(timestamp);
};

export default {
  getLoginLogs,
  createNewUser,
  getAccountStats,
  getAllUsers,
  updateUser,
  deleteUser,
  resetUserPassword,
  formatLoginTime,
  getRelativeTime
};
