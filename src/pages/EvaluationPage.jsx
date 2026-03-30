/**
 * Model Evaluation Page Component
 * Displays real-time KNN model evaluation metrics and confusion matrices
 */

import { useState, useEffect } from 'react';
import evaluationService from '@/services/evaluationService';
import './EvaluationPage.css';

const classLabels = {
  0: 'Normal + Gizi Baik',
  1: 'Normal + Kurang Gizi',
  2: 'Stunting + Gizi Baik',
  3: 'Stunting + Kurang Gizi'
};

export default function EvaluationPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [evaluationData, setEvaluationData] = useState(null);
  const [selectedK, setSelectedK] = useState(5);

  // Fetch evaluation data on component mount
  useEffect(() => {
    fetchEvaluationData();
  }, []);

  const fetchEvaluationData = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await evaluationService.getRealtimeEvaluation();
      
      // Check if evaluation was successful
      if (data && !data.success) {
        setError(data.message || 'Tidak ada data pengukuran untuk dievaluasi');
        setEvaluationData(null);
      } else {
        setEvaluationData(data);
      }
    } catch (err) {
      console.error('Failed to fetch evaluation data:', err);
      setError(err.message || 'Gagal memuat data evaluasi');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="evaluation-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Memuat data evaluasi...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="evaluation-page">
        <div className="error-container">
          <h2>❌ Error</h2>
          <p>{error}</p>
          <button onClick={fetchEvaluationData} className="btn-retry">
            Coba Lagi
          </button>
        </div>
      </div>
    );
  }

  if (!evaluationData) {
    return (
      <div className="evaluation-page">
        <div className="no-data-container">
          <p>Tidak ada data untuk ditampilkan</p>
        </div>
      </div>
    );
  }

  const binaryMetrics = evaluationData.binary_classification?.metrics || {};
  const multiclassMetrics = evaluationData.multiclass_classification?.metrics || {};
  const kComparison = evaluationData.k_comparison || [];
  const distribution = evaluationData.distribution || {};
  const totalData = evaluationData.metadata?.total_data || 0;

  // Parse 4x4 confusion matrix
  const parsedCM4x4 = evaluationService.parse4ClassConfusionMatrix(
    multiclassMetrics.confusion_matrix
  );

  // Get selected K metrics
  const selectedKData = kComparison.find(item => item.k === selectedK);
  const formattedKMetrics = selectedKData
    ? evaluationService.formatMetrics(selectedKData)
    : {};

  return (
    <div className="evaluation-page">
      {/* Header */}
      <div className="eval-header">
        <h1>📊 Evaluasi Model KNN</h1>
        <p className="subtitle">Real-time Evaluation dari Database Pengukuran</p>
        <div className="header-stats">
          <div className="stat">
            <span className="label">Total Data</span>
            <span className="value">{totalData}</span>
          </div>
          <div className="stat">
            <span className="label">Normal</span>
            <span className="value">{distribution.normal_count || 0}</span>
          </div>
          <div className="stat">
            <span className="label">Stunting</span>
            <span className="value">{distribution.stunting_count || 0}</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="eval-content">
        {/* Section 1: K Comparison Table */}
        <section className="eval-section">
          <h2>📈 Perbandingan Akurasi K</h2>
          <p className="section-description">
            Perbandingan metrik evaluasi untuk nilai K yang berbeda (K=3,5,7,9)
          </p>
          <div className="k-comparison-table-wrapper">
            <table className="k-comparison-table">
              <thead>
                <tr>
                  <th>K</th>
                  <th>Accuracy</th>
                  <th>Precision</th>
                  <th>Recall</th>
                  <th>F1-Score</th>
                  <th>Specificity</th>
                </tr>
              </thead>
              <tbody>
                {kComparison.map((item) => (
                  <tr
                    key={item.k}
                    className={selectedK === item.k ? 'selected' : ''}
                    onClick={() => setSelectedK(item.k)}
                  >
                    <td><strong>{item.k}</strong></td>
                    <td>{(item.accuracy_percent || 0).toFixed(2)}%</td>
                    <td>{(item.precision_percent || 0).toFixed(2)}%</td>
                    <td>{(item.recall_percent || 0).toFixed(2)}%</td>
                    <td>{(item.f1_score_percent || 0).toFixed(2)}%</td>
                    <td>{(item.specificity_percent || 0).toFixed(2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 2: Selected K Metrics Dashboard */}
        <section className="eval-section">
          <h2>📊 Metrik K={selectedK} (Binary Classification)</h2>
          <p className="section-description">
            Metrik binary classification (Normal vs Stunting)
          </p>
          
          {/* 2x2 Confusion Matrix */}
          <div className="metrics-grid">
            <div className="metrics-box confusion-matrix">
              <h3>Confusion Matrix 2×2</h3>
              <table className="cm-2x2">
                <tbody>
                  <tr>
                    <td colSpan="2" className="header-cell"></td>
                    <th colSpan="2">Predicted</th>
                  </tr>
                  <tr>
                    <td className="header-cell"></td>
                    <td className="header-cell">Normal</td>
                    <td className="header-cell">Stunting</td>
                  </tr>
                  <tr>
                    <th className="header-cell">Actual Normal</th>
                    <td className="tn">{binaryMetrics.tn || 0}</td>
                    <td className="fp">{binaryMetrics.fp || 0}</td>
                  </tr>
                  <tr>
                    <th className="header-cell">Actual Stunting</th>
                    <td className="fn">{binaryMetrics.fn || 0}</td>
                    <td className="tp">{binaryMetrics.tp || 0}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Key Metrics Cards */}
            <div className="metrics-box metrics-cards">
              <h3>Metrik Kinerja</h3>
              <div className="metric-item">
                <strong>Accuracy (Akurasi)</strong>
                <span className="metric-value">
                  {selectedKData ? (selectedKData.accuracy_percent || 0).toFixed(2) : 0}%
                </span>
              </div>
              <div className="metric-item">
                <strong>Precision (Presisi)</strong>
                <span className="metric-value">
                  {selectedKData ? (selectedKData.precision_percent || 0).toFixed(2) : 0}%
                </span>
              </div>
              <div className="metric-item">
                <strong>Recall (Sensitifitas)</strong>
                <span className="metric-value">
                  {selectedKData ? (selectedKData.recall_percent || 0).toFixed(2) : 0}%
                </span>
              </div>
              <div className="metric-item">
                <strong>Specificity (Spesifisitas)</strong>
                <span className="metric-value">
                  {selectedKData ? (selectedKData.specificity_percent || 0).toFixed(2) : 0}%
                </span>
              </div>
              <div className="metric-item">
                <strong>F1-Score</strong>
                <span className="metric-value">
                  {selectedKData ? (selectedKData.f1_score_percent || 0).toFixed(2) : 0}%
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: 4-Class Confusion Matrix */}
        <section className="eval-section">
          <h2>🔢 Confusion Matrix 4-Kelas</h2>
          <p className="section-description">
            Matriks kebingungan untuk klasifikasi 4-kelas
          </p>
          
          {parsedCM4x4 && (
            <div className="cm-4x4-wrapper">
              <table className="cm-4x4">
                <thead>
                  <tr>
                    <th className="label-cell">Actual \ Predicted</th>
                    {[0, 1, 2, 3].map((i) => (
                      <th key={i} className="label-cell">
                        {classLabels[i]}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {parsedCM4x4.rows.map((row, i) => (
                    <tr key={i}>
                      <th className="label-cell">{row.actualName}</th>
                      {row.predictions.map((pred, j) => (
                        <td
                          key={`${i}-${j}`}
                          className={`cm-cell ${
                            pred.isCorrect ? 'correct' : 'incorrect'
                          }`}
                        >
                          {pred.count}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Section 4: Per-Class Metrics */}
        <section className="eval-section">
          <h2>🎯 Metrik Per-Kelas</h2>
          <p className="section-description">
            Precision, Recall, dan F1-Score untuk setiap kelas
          </p>

          <div className="per-class-metrics">
            {multiclassMetrics.per_class_metrics &&
              multiclassMetrics.per_class_metrics.map((metric, i) => (
                <div key={i} className="class-card">
                  <h4>{classLabels[metric.class]}</h4>
                  <div className="metric-row">
                    <span>Precision:</span>
                    <strong>{(metric.precision * 100).toFixed(2)}%</strong>
                  </div>
                  <div className="metric-row">
                    <span>Recall:</span>
                    <strong>{(metric.recall * 100).toFixed(2)}%</strong>
                  </div>
                  <div className="metric-row">
                    <span>F1-Score:</span>
                    <strong>{(metric.f1 * 100).toFixed(2)}%</strong>
                  </div>
                </div>
              ))}
          </div>
        </section>

        {/* Section 5: Legend & Definitions */}
        <section className="eval-section legend">
          <h2>📚 Definisi & Interpretasi</h2>
          <div className="definitions">
            <div className="def-item">
              <strong>Accuracy (Akurasi)</strong>
              <p>
                Persentase prediksi yang benar dari total prediksi.
                Formula: (TP + TN) / Total
              </p>
            </div>
            <div className="def-item">
              <strong>Precision (Presisi)</strong>
              <p>
                Dari prediksi positif (Stunting), berapa persen yang benar-benar stunting.
                Formula: TP / (TP + FP)
              </p>
            </div>
            <div className="def-item">
              <strong>Recall (Sensitifitas/Recall)</strong>
              <p>
                Dari actual positif (Stunting), berapa persen yang terdeteksi.
                Formula: TP / (TP + FN)
              </p>
            </div>
            <div className="def-item">
              <strong>Specificity (Spesifisitas)</strong>
              <p>
                Dari actual negatif (Normal), berapa persen yang terdeteksi benar.
                Formula: TN / (TN + FP)
              </p>
            </div>
            <div className="def-item">
              <strong>F1-Score</strong>
              <p>
                Harmonic mean dari Precision dan Recall.
                Formula: 2 × (Precision × Recall) / (Precision + Recall)
              </p>
            </div>
            <div className="def-item">
              <strong>Confusion Matrix</strong>
              <p>
                Tabel yang menunjukkan True Positive (TP), True Negative (TN),
                False Positive (FP), dan False Negative (FN).
              </p>
            </div>
          </div>
        </section>
      </div>

      {/* Refresh Button */}
      <div className="action-buttons">
        <button onClick={fetchEvaluationData} className="btn btn-primary">
          🔄 Refresh Data
        </button>
      </div>
    </div>
  );
}
