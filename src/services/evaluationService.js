/**
 * Evaluation Service - Frontend
 * Calls backend evaluation API and handles data
 */

import apiClient from './api';

class EvaluationService {
  /**
   * Fetch real-time evaluation data from backend
   * @param {string} bulan - Filter bulan dalam format YYYY-MM (optional)
   * @returns {Promise<Object>} Evaluation results
   */
  async getRealtimeEvaluation(bulan = null) {
    try {
      const params = {};
      if (bulan) {
        params.bulan = bulan;
      }
      
      const response = await apiClient.get('/evaluasi/realtime', { params });
      
      if (response.data.status === 'success') {
        // Return data regardless of success field - let page handle success: false
        return response.data.data;
      } else {
        throw new Error(response.data.data?.error || 'Evaluation failed');
      }
    } catch (error) {
      console.error('Error fetching evaluation data:', error);
      throw error;
    }
  }

  /**
   * Fetch prediction history with child names
   * @param {number} limit - Maximum number of records to fetch
   * @param {string} bulan - Filter bulan dalam format YYYY-MM (optional)
   * @returns {Promise<Array>} Prediction history
   */
  async getPredictionHistory(limit = 100, bulan = null) {
    try {
      const params = { limit };
      if (bulan) {
        params.bulan = bulan;
      }
      
      const response = await apiClient.get('/evaluasi/prediction-history', {
        params
      });
      
      if (response.data.status === 'success') {
        return response.data.data.predictions || [];
      } else {
        throw new Error('Failed to fetch prediction history');
      }
    } catch (error) {
      console.error('Error fetching prediction history:', error);
      throw error;
    }
  }

  /**
   * Fetch available months with data for kader
   * @returns {Promise<Array>} Array of {value: YYYY-MM, label: "Nama Bulan Tahun"}
   */
  async getAvailableMonths() {
    try {
      const response = await apiClient.get('/evaluasi/available-months');
      
      if (response.data.status === 'success') {
        return response.data.data || [];
      } else {
        throw new Error('Failed to fetch available months');
      }
    } catch (error) {
      console.error('Error fetching available months:', error);
      return [];
    }
  }

  /**
   * Parse binary confusion matrix to readable format
   * @param {Array} cm - Confusion matrix [[TN, FP], [FN, TP]]
   * @returns {Object} Parsed confusion matrix
   */
  parseBinaryConfusionMatrix(cm) {
    if (!cm || cm.length !== 2) return null;
    
    return {
      tn: cm[0][0],  // True Negative
      fp: cm[0][1],  // False Positive
      fn: cm[1][0],  // False Negative
      tp: cm[1][1],  // True Positive
    };
  }

  /**
   * Parse 4-class confusion matrix
   * @param {Array} cm - 4x4 confusion matrix
   * @returns {Object} Parsed with proper labels
   */
  parse4ClassConfusionMatrix(cm) {
    if (!cm || cm.length !== 4) return null;

    const labels = {
      0: 'Normal + Baik',
      1: 'Normal + Kurang',
      2: 'Stunting + Baik',
      3: 'Stunting + Kurang'
    };

    const parsed = {
      matrix: cm,
      labels: labels,
      rows: []
    };

    cm.forEach((row, i) => {
      parsed.rows.push({
        actualLabel: i,
        actualName: labels[i],
        predictions: row.map((count, j) => ({
          predictedLabel: j,
          predictedName: labels[j],
          count: count,
          isCorrect: i === j
        }))
      });
    });

    return parsed;
  }

  /**
   * Format metrics for display
   * @param {Object} metrics - Raw metrics from backend
   * @returns {Object} Formatted metrics
   */
  formatMetrics(metrics) {
    return {
      accuracy: `${(metrics.accuracy_percent || 0).toFixed(2)}%`,
      precision: `${(metrics.precision_percent || 0).toFixed(2)}%`,
      recall: `${(metrics.recall_percent || 0).toFixed(2)}%`,
      specificity: `${(metrics.specificity_percent || 0).toFixed(2)}%`,
      f1_score: `${(metrics.f1_score_percent || 0).toFixed(2)}%`,
    };
  }

  /**
   * Get K comparison data for table
   * @param {Array} kComparison - K comparison data
   * @returns {Array} Formatted for table display
   */
  formatKComparison(kComparison) {
    return kComparison.map(item => ({
      k: item.k,
      accuracy: `${(item.accuracy_percent || 0).toFixed(2)}%`,
      precision: `${(item.precision_percent || 0).toFixed(2)}%`,
      recall: `${(item.recall_percent || 0).toFixed(2)}%`,
      f1_score: `${(item.f1_score_percent || 0).toFixed(2)}%`,
      specificity: `${(item.specificity_percent || 0).toFixed(2)}%`,
    }));
  }
}

export default new EvaluationService();
