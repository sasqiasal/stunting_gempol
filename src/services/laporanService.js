/**
 * Laporan Service
 * Service untuk mengambil data laporan dari endpoint /api/v1/laporan/*
 */

import apiClient from './api';

/**
 * Get data pengukuran untuk export laporan
 * @returns {Promise<Array>} Array of pengukuran data
 */
export const getPengukuranList = async () => {
  try {
    const response = await apiClient.get('/laporan/pengukuran');
    return response.data || [];
  } catch (error) {
    console.error('Error fetching pengukuran list:', error);
    return [];
  }
};

/**
 * Get data balita untuk export laporan
 * @returns {Promise<Array>} Array of balita data
 */
export const getBalitaList = async () => {
  try {
    const response = await apiClient.get('/laporan/balita');
    return response.data || [];
  } catch (error) {
    console.error('Error fetching balita list:', error);
    return [];
  }
};

/**
 * Get data posyandu untuk export laporan
 * @returns {Promise<Array>} Array of posyandu data
 */
export const getPosyanduList = async () => {
  try {
    const response = await apiClient.get('/laporan/posyandu');
    return response.data || [];
  } catch (error) {
    console.error('Error fetching posyandu list:', error);
    return [];
  }
};

export default {
  getPengukuranList,
  getBalitaList,
  getPosyanduList,
};
