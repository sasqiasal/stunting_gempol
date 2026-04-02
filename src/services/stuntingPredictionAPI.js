/**
 * Stunting Prediction Service
 * Untuk memanggil KNN Model API dari React
 */

const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api/v1' : 'http://localhost:8000/api/v1');

export const stuntingPredictionAPI = {
  /**
   * Get informasi tentang model KNN
   */
  getModelInfo: async () => {
    try {
      const response = await fetch(`${API_BASE}/model-info`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching model info:', error);
      throw error;
    }
  },

  /**
   * Prediksi stunting untuk satu sampel
   * 
   * @param {Object} patientData - Input data dengan structure:
   *   {
   *     jenis_kelamin: 1,      // 0 = Perempuan, 1 = Laki-laki
   *     usia_bulan: 24,
   *     berat_badan: 12.5,
   *     tinggi_badan: 89.0,
   *     lingkar_lengan: 18.0,
   *     lingkar_kepala: 53.0
   *   }
   * @returns {Object} Response dengan predicted_class, label, confidence, dll
   */
  predictStunting: async (patientData) => {
    try {
      const response = await fetch(`${API_BASE}/predict-stunting`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Prediction error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error predicting stunting:', error);
      throw error;
    }
  },

  /**
   * Prediksi stunting untuk multiple sampel (batch)
   * 
   * @param {Array} samples - Array of patient data
   * @returns {Object} Response dengan summary dan per-sample predictions
   */
  predictBatch: async (samples) => {
    try {
      const response = await fetch(`${API_BASE}/predict-stunting-batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ samples }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Batch prediction error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error in batch prediction:', error);
      throw error;
    }
  },

  /**
   * Dapatkan K-nearest neighbors untuk explainability
   * 
   * @param {Object} patientData - Input data
   * @returns {Object} Response dengan neighbors information
   */
  getNeighbors: async (patientData) => {
    try {
      const response = await fetch(`${API_BASE}/get-neighbors`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Get neighbors error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting neighbors:', error);
      throw error;
    }
  },
};

/**
 * Format hasil prediksi untuk display yang lebih user-friendly
 */
export const formatPredictionResult = (result) => {
  if (!result.success || !result.data) {
    return null;
  }

  const { data } = result;
  return {
    class: data.predicted_class,
    label: data.predicted_label,
    confidence: `${data.confidence_score.toFixed(2)}%`,
    isStunting: data.is_stunting,
    status: data.is_stunting ? '🔴 STUNTING' : '🟢 NORMAL',
    recommendation: data.recommendation,
    color: data.is_stunting ? '#F44336' : '#4CAF50', // Red or Green
  };
};

/**
 * Validate input sebelum mengirim ke API
 */
export const validatePredictionInput = (data) => {
  const errors = [];

  if (typeof data.jenis_kelamin !== 'number' || ![0, 1].includes(data.jenis_kelamin)) {
    errors.push('Jenis kelamin harus 0 (Perempuan) atau 1 (Laki-laki)');
  }

  if (typeof data.usia_bulan !== 'number' || data.usia_bulan < 0 || data.usia_bulan > 60) {
    errors.push('Usia bulan harus antara 0-60');
  }

  const numericFields = ['berat_badan', 'tinggi_badan', 'lingkar_lengan', 'lingkar_kepala'];
  for (const field of numericFields) {
    if (typeof data[field] !== 'number' || data[field] <= 0) {
      errors.push(`${field} harus angka positif`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
};
