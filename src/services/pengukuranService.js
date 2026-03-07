/**
 * Pengukuran Service
 * Service untuk CRUD data pengukuran dan prediksi stunting
 */

import apiClient from "./api";

export const pengukuranService = {
  /**
   * Get all pengukuran
   * @param {Object} params - Query params
   * @returns {Promise}
   */
  getAll: async (params = {}) => {
    const response = await apiClient.get("/pengukuran/", { params });
    return response.data;
  },

  /**
   * Get pengukuran by balita ID
   * @param {number} balitaId - Balita ID
   * @returns {Promise}
   */
  getByBalita: async (balitaId) => {
    const response = await apiClient.get(`/pengukuran/balita/${balitaId}`);
    return response.data;
  },

  /**
   * Create pengukuran baru (dengan prediksi otomatis)
   * @param {Object} data - Data pengukuran
   * @returns {Promise}
   */
  create: async (data) => {
    const response = await apiClient.post("/pengukuran/", data);
    return response.data;
  },

  /**
   * Update pengukuran dan recalculate prediksi/evaluasi
   * @param {number} id - Pengukuran ID
   * @param {Object} data - Data yang diupdate (tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala, catatan)
   * @returns {Promise}
   */
  update: async (id, data) => {
    const response = await apiClient.put(`/pengukuran/${id}`, data);
    return response.data;
  },

  /**
   * Get statistik summary
   * @param {Object} params - Query params
   * @returns {Promise}
   */
  getStatistik: async (params = {}) => {
    const response = await apiClient.get("/pengukuran/statistik/summary", { params });
    return response.data;
  },

  /**
   * Get detail evaluasi (neareset neighbors) untuk pengukuran tertentu
   * @param {number} id - Pengukuran ID
   * @returns {Promise}
   */
  getDetailEvaluasi: async (id) => {
    const response = await apiClient.get(`/pengukuran/${id}/detail-evaluasi`);
    return response.data;
  },

  /**
   * Get riwayat stunting 6 bulan terakhir
   * Role-based: Admin = global, Kader = filter posyandu
   * @returns {Promise}
   */
  getRiwayatStunting: async () => {
    const response = await apiClient.get("/pengukuran/riwayat-stunting");
    return response.data;
  },
};
