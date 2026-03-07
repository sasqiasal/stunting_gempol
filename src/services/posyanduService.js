/**
 * Posyandu Service
 * Service untuk CRUD data posyandu dan data spasial
 */

import apiClient from "./api";

export const posyanduService = {
  /**
   * Get all posyandu
   * @param {Object} params - Query params
   * @returns {Promise}
   */
  getAll: async (params = {}) => {
    const response = await apiClient.get("/posyandu/", { params });
    return response.data;
  },

  /**
   * Get posyandu by ID
   * @param {number} id - Posyandu ID
   * @returns {Promise}
   */
  getById: async (id) => {
    const response = await apiClient.get(`/posyandu/${id}`);
    return response.data;
  },

  /**
   * Get posyandu data dalam format GeoJSON
   * @returns {Promise}
   */
  getGeoJSON: async () => {
    const response = await apiClient.get("/posyandu/geojson");
    return response.data;
  },

  /**
   * Create posyandu baru (Admin only)
   * @param {Object} data - Data posyandu
   * @returns {Promise}
   */
  create: async (data) => {
    const response = await apiClient.post("/posyandu/", data);
    return response.data;
  },

  /**
   * Update posyandu (Admin only)
   * @param {number} id - Posyandu ID
   * @param {Object} data - Data posyandu
   * @returns {Promise}
   */
  update: async (id, data) => {
    const response = await apiClient.put(`/posyandu/${id}`, data);
    return response.data;
  },

  /**
   * Delete posyandu (Admin only)
   * @param {number} id - Posyandu ID
   * @returns {Promise}
   */
  delete: async (id) => {
    const response = await apiClient.delete(`/posyandu/${id}`);
    return response.data;
  },
};
