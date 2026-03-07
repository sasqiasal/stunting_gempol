/**
 * Service untuk Evaluasi Model KNN
 * Mengambil data performa model dari backend
 */

import api from './api';

/**
 * Get performa model KNN
 * Menghitung confusion matrix, accuracy, precision, recall, F1-score
 */
export const getModelPerformance = async () => {
  try {
    const response = await api.get('/evaluasi/model-performance');
    return response.data;
  } catch (error) {
    console.error('Error fetching model performance:', error);
    throw error.response?.data || { detail: 'Gagal mengambil data evaluasi model' };
  }
};

/**
 * Bandingkan performa model dengan nilai k berbeda (k=3, k=5, k=7)
 */
export const compareKValues = async () => {
  try {
    const response = await api.get('/evaluasi/compare-k-values');
    return response.data;
  } catch (error) {
    console.error('Error comparing k-values:', error);
    throw error.response?.data || { detail: 'Gagal membandingkan nilai k' };
  }
};

/**
 * Hitung jumlah data latih yang tersimpan di database
 */
export const countTrainingData = async () => {
  try {
    const response = await api.get('/evaluasi/training-data/count');
    return response.data;
  } catch (error) {
    console.error('Error counting training data:', error);
    throw error.response?.data || { detail: 'Gagal menghitung data latih' };
  }
};

/**
 * Hapus semua data latih dari database (hanya Admin)
 */
export const deleteTrainingData = async () => {
  try {
    const response = await api.delete('/evaluasi/training-data');
    return response.data;
  } catch (error) {
    console.error('Error deleting training data:', error);
    throw error.response?.data || { detail: 'Gagal menghapus data latih' };
  }
};

/**
 * Helper untuk format persentase
 */
export const formatPercentage = (value) => {
  return `${(value * 100).toFixed(2)}%`;
};

/**
 * Helper untuk interpretasi warna berdasarkan nilai metrik
 */
export const getMetricColorClass = (value) => {
  if (value >= 0.95) return 'text-green-600 bg-green-50 border-green-200';
  if (value >= 0.90) return 'text-green-600 bg-green-50 border-green-200';
  if (value >= 0.80) return 'text-blue-600 bg-blue-50 border-blue-200';
  if (value >= 0.70) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  return 'text-red-600 bg-red-50 border-red-200';
};

/**
 * Helper untuk badge warna
 */
export const getMetricBadgeClass = (value) => {
  if (value >= 0.95) return 'bg-green-100 text-green-800';
  if (value >= 0.90) return 'bg-green-100 text-green-800';
  if (value >= 0.80) return 'bg-blue-100 text-blue-800';
  if (value >= 0.70) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
};

export default {
  getModelPerformance,
  formatPercentage,
  getMetricColorClass,
  getMetricBadgeClass
};
