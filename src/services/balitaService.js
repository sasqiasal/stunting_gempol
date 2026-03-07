/**
 * Balita Service
 * Service untuk CRUD data balita
 */

import apiClient from "./api";

export const balitaService = {
  /**
   * Get all balita
   * @param {Object} params - Query params (skip, limit, posyandu_id, status_terkini)
   * @returns {Promise}
   */
  getAll: async (params = {}) => {
    const response = await apiClient.get("/balita/", { params });
    return response.data;
  },

  /**
   * Get balita by ID
   * @param {number} id - Balita ID
   * @returns {Promise}
   */
  getById: async (id) => {
    const response = await apiClient.get(`/balita/${id}`);
    return response.data;
  },

  /**
   * Create balita baru
   * @param {Object} data - Data balita
   * @returns {Promise}
   */
  create: async (data) => {
    const response = await apiClient.post("/balita/", data);
    return response.data;
  },

  /**
   * Update balita
   * @param {number} id - Balita ID
   * @param {Object} data - Data balita
   * @returns {Promise}
   */
  update: async (id, data) => {
    const response = await apiClient.put(`/balita/${id}`, data);
    return response.data;
  },

  /**
   * Delete balita
   * @param {number} id - Balita ID
   * @returns {Promise}
   */
  delete: async (id) => {
    const response = await apiClient.delete(`/balita/${id}`);
    return response.data;
  },
};
