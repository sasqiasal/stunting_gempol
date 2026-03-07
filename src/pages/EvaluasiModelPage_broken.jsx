/**
 * Evaluasi Model Page
 * Halaman untuk menampilkan performa dan metrik evaluasi model KNN
 * Menampilkan Confusion Matrix, Accuracy, Precision, Recall, F1-Score
 */

import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import { useAuthStore } from "../store/authStore";
import { getModelPerformance, compareKValues, getMetricColorClass, getMetricBadgeClass } from "../services/evaluasiService";

// Helper function untuk format nilai metrik agar lebih formal
const formatMetricValue = (value) => {
  // Jika nilai 1 atau 0 (sempurna), tampilkan sebagai integer dengan 2 desimal
  if (value === 1.0 || value === 0.0) {
    return value.toFixed(2);
  }
  // Untuk nilai lainnya, tampilkan 3 desimal untuk presisi
  return value.toFixed(3);
};

const EvaluasiModelPage = () => {
  const { user } = useAuthStore();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [evaluationData, setEvaluationData] = useState(null);
  
  // State untuk perbandingan k-values
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [isLoadingComparison, setIsLoadingComparison] = useState(false);

  useEffect(() => {
    fetchModelPerformance();
  }, []);

  const fetchModelPerformance = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getModelPerformance();
      setEvaluationData(data);
    } catch (err) {
      setError(err.detail || "Gagal mengambil data evaluasi model");
      console.error("Error fetching model performance:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchKComparison = async () => {
    setIsLoadingComparison(true);
    try {
      const data = await compareKValues();
      setComparisonData(data);
      setShowComparison(true);
    } catch (err) {
      alert(err.detail || "Gagal membandingkan nilai k");
      console.error("Error comparing k-values:", err);
    } finally {
      setIsLoadingComparison(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center space-x-4">
              <button onClick={() => setIsSidebarOpen(true)} className="text-gray-500 hover:text-gray-700 focus:outline-none lg:hidden">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Evaluasi Kinerja Model</h1>
                <p className="text-sm text-gray-500 mt-1">Metrik performa model KNN untuk deteksi stunting</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.nama}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                <p className="text-gray-600">Memuat data evaluasi model...</p>
              </div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-start space-x-3">
                <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 className="text-lg font-semibold text-red-900 mb-1">Error</h3>
                  <p className="text-red-700">{error}</p>
                  <button onClick={fetchModelPerformance} className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
                    Coba Lagi
                  </button>
                </div>
              </div>
            </div>
          ) : evaluationData ? (
            <div className="space-y-6">
              {/* Info Model */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">Informasi Model</h2>
                    <p className="text-sm text-gray-500">Detail algoritma dan fitur yang digunakan</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Algoritma</p>
                    <p className="text-lg font-semibold text-gray-900">{evaluationData.model_info.algorithm}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Jumlah Tetangga (K)</p>
                    <p className="text-lg font-semibold text-gray-900">{evaluationData.model_info.n_neighbors}</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-500 mb-1">Total Fitur</p>
                    <p className="text-lg font-semibold text-gray-900">{evaluationData.model_info.total_features} Variabel</p>
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Fitur yang Digunakan:</p>
                  <div className="flex flex-wrap gap-2">
                    {evaluationData.model_info.feature_names.map((feature, index) => (
                      <span key={index} className="px-3 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-full">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Konteks Evaluasi - K Value yang Digunakan */}
              <div className="bg-indigo-50 border-l-4 border-indigo-500 rounded-lg p-5">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-bold text-indigo-900 mb-2">🎯 Parameter Klasifikasi yang Digunakan</h3>
                    <div className="text-sm text-indigo-800 space-y-2">
                      <p>
                        <strong>Nilai K (Jumlah Tetangga Terdekat):</strong> Semua hasil evaluasi dan prediksi menggunakan <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-bold bg-indigo-200 text-indigo-900 ml-1">K = {evaluationData.model_info.n_neighbors}</span>
                      </p>
                      <p className="text-xs text-indigo-700">
                        Artinya: Setiap klasifikasi mempertimbangkan <strong>{evaluationData.model_info.n_neighbors} data balita terdekat</strong> dari data latih untuk menentukan status stunting. Semakin tinggi K, model lebih stabil tapi kurang sensitif terhadap pola lokal.
                      </p>
                      <div className="mt-2 pt-2 border-t border-indigo-200">
                        <p className="text-xs text-indigo-700">
                          💡 <strong>Tips:</strong> Gunakan fitur <em>"Perbandingan Nilai K"</em> di bawah untuk melihat bagaimana performa model berbeda dengan K=3, K=5, dan K=7. Anda dapat memilih K optimal berdasarkan keseimbangan akurasi dan F1-Score.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Perbandingan K-Values */
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">Perbandingan Nilai K</h2>
                      <p className="text-sm text-gray-500">
                        Bandingkan performa model dengan K=3, K=5, dan K=7 
                        <span className="ml-2 px-2 py-0.5 bg-indigo-100 text-indigo-700 text-xs font-medium rounded">
                          Saat ini: K={evaluationData.model_info.n_neighbors}
                        </span>
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={fetchKComparison}
                    disabled={isLoadingComparison}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {isLoadingComparison ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Memuat...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        <span>Bandingkan K-Values</span>
                      </>
                    )}
                  </button>
                </div>

                {showComparison && comparisonData && (
                  <div className="mt-6 space-y-6">
                    {/* Rekomendasi */}
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-start space-x-3">
                        <svg className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div>
                          <h3 className="text-sm font-bold text-green-900">Rekomendasi Nilai K Terbaik</h3>
                          <p className="text-sm text-green-800 mt-1">
                            <strong>K = {comparisonData.recommendation.best_k}</strong> — {comparisonData.recommendation.reason}
                          </p>
                          <p className="text-sm text-green-700 mt-1">
                            F1-Score: <strong>{(comparisonData.recommendation.f1_score * 100).toFixed(2)}%</strong>
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Tabel Perbandingan */}
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nilai K</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Accuracy</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precision</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recall</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Specificity</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">F1-Score</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {comparisonData.comparisons.map((comp) => {
                            const isBest = comp.k_value === comparisonData.recommendation.best_k;
                            const isCurrentlyUsed = comp.k_value === evaluationData.model_info.n_neighbors;
                            return (
                              <tr key={comp.k_value} className={isBest ? 'bg-green-50' : isCurrentlyUsed ? 'bg-indigo-50' : ''}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex items-center">
                                    <span className={`text-sm font-bold ${isBest ? 'text-green-700' : isCurrentlyUsed ? 'text-indigo-700' : 'text-gray-900'}`}>
                                      K = {comp.k_value}
                                    </span>
                                    {isBest && (
                                      <span className="ml-2 px-2 py-1 text-xs font-semibold text-green-800 bg-green-200 rounded-full">
                                        Terbaik
                                      </span>
                                    )}
                                    {isCurrentlyUsed && (
                                      <span className="ml-2 px-2 py-1 text-xs font-semibold text-indigo-800 bg-indigo-200 rounded-full">
                                        Sedang Digunakan
                                      </span>
                                    )}
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {formatMetricValue(comp.metrics.accuracy)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {formatMetricValue(comp.metrics.precision)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {formatMetricValue(comp.metrics.recall)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                  {formatMetricValue(comp.metrics.specificity)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                                  {formatMetricValue(comp.metrics.f1_score)}
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>

                    {/* Info Dataset */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-600">
                        <strong>Dataset:</strong> {comparisonData.dataset_info.total_samples} sampel 
                        ({comparisonData.dataset_info.stunting_count} stunting, {comparisonData.dataset_info.normal_count} normal)
                      </p>
                      <p className="text-xs text-gray-500 mt-2">
                        💡 <strong>Catatan:</strong> Perbandingan ini menunjukkan bagaimana performa model akan berubah jika menggunakan nilai K yang berbeda. 
                        Nilai K yang ditandai "Sedang Digunakan" adalah yang saat ini diterapkan pada semua klasifikasi evaluasi di atas.
                      </p>
                    </div>
                  </div>
                )}

                {!showComparison && (
                  <div className="text-center py-8 text-gray-500">
                    <svg className="w-16 h-16 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <p className="text-sm">Klik tombol "Bandingkan K-Values" untuk melihat perbandingan</p>
                  </div>
                )}
              </div>

              {/* Confusion Matrix */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">Confusion Matrix</h2>
                    <p className="text-sm text-gray-500">Matriks prediksi vs aktual</p>
                  </div>
                </div>

                {/* Grid 2x2 Confusion Matrix */}
                <div className="max-w-2xl mx-auto">
                  {/* Summary Total */}
                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4 mb-4 text-center">
                    <p className="text-sm text-gray-700">
                      <span className="font-bold text-purple-900">Total Data Evaluasi: {evaluationData.confusion_matrix.true_positive + evaluationData.confusion_matrix.true_negative + evaluationData.confusion_matrix.false_positive + evaluationData.confusion_matrix.false_negative}</span>
                      <span className="mx-2">|</span>
                      <span className="text-green-700">Benar: {evaluationData.confusion_matrix.true_positive + evaluationData.confusion_matrix.true_negative}</span>
                      <span className="mx-2">|</span>
                      <span className="text-red-700">Salah: {evaluationData.confusion_matrix.false_positive + evaluationData.confusion_matrix.false_negative}</span>
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    {/* True Negative */}
                    <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6 text-center">
                      <div className="text-sm font-medium text-green-700 mb-2">True Negative (TN)</div>
                      <div className="text-4xl font-bold text-green-900 mb-2">{evaluationData.confusion_matrix.true_negative}</div>
                      <div className="text-xs text-gray-600">Diprediksi Normal, Aktual Normal ✓</div>
                    </div>

                    {/* False Positive */}
                    <div className="bg-orange-50 border-2 border-orange-500 rounded-lg p-6 text-center">
                      <div className="text-sm font-medium text-orange-700 mb-2">False Positive (FP)</div>
                      <div className="text-4xl font-bold text-orange-900 mb-2">{evaluationData.confusion_matrix.false_positive}</div>
                      <div className="text-xs text-gray-600">Diprediksi Stunting, Aktual Normal ✗</div>
                    </div>

                    {/* False Negative */}
                    <div className="bg-yellow-50 border-2 border-yellow-500 rounded-lg p-6 text-center">
                      <div className="text-sm font-medium text-yellow-700 mb-2">False Negative (FN)</div>
                      <div className="text-4xl font-bold text-yellow-900 mb-2">{evaluationData.confusion_matrix.false_negative}</div>
                      <div className="text-xs text-gray-600">Diprediksi Normal, Aktual Stunting ✗</div>
                    </div>

                    {/* True Positive */}
                    <div className="bg-blue-50 border-2 border-blue-500 rounded-lg p-6 text-center">
                      <div className="text-sm font-medium text-blue-700 mb-2">True Positive (TP)</div>
                      <div className="text-4xl font-bold text-blue-900 mb-2">{evaluationData.confusion_matrix.true_positive}</div>
                      <div className="text-xs text-gray-600">Diprediksi Stunting, Aktual Stunting ✓</div>
                    </div>
                  </div>

                  {/* Legend */}
                  <div className="bg-gray-50 rounded-lg p-4 text-center">
                    <p className="text-xs text-gray-600">
                      <span className="font-semibold">Kolom:</span> Prediksi Model |<span className="font-semibold ml-2">Baris:</span> Kondisi Aktual
                    </p>
                  </div>
                </div>
              </div>

              {/* Metrik Evaluasi */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">Metrik Evaluasi</h2>
                    <p className="text-sm text-gray-500">Ukuran performa model</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  {/* Accuracy */}
                  <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.accuracy)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-semibold uppercase tracking-wide">Akurasi</h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.accuracy)}`}>{evaluationData.metrics.accuracy_percentage}%</span>
                    </div>
                    <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.accuracy)}</p>
                    <p className="text-xs leading-tight">{evaluationData.interpretation.accuracy}</p>
                    <div className="mt-3 text-xs opacity-75">
                      <p>Formula: (TP + TN) / Total</p>
                    </div>
                  </div>

                  {/* Precision */}
                  <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.precision)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-semibold uppercase tracking-wide">Presisi</h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.precision)}`}>{evaluationData.metrics.precision_percentage}%</span>
                    </div>
                    <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.precision)}</p>
                    <p className="text-xs leading-tight">{evaluationData.interpretation.precision}</p>
                    <div className="mt-3 text-xs opacity-75">
                      <p>Formula: TP / (TP + FP)</p>
                    </div>
                  </div>

                  {/* Recall */}
                  <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.recall)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-semibold uppercase tracking-wide">Recall</h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.recall)}`}>{evaluationData.metrics.recall_percentage}%</span>
                    </div>
                    <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.recall)}</p>
                    <p className="text-xs leading-tight">{evaluationData.interpretation.recall}</p>
                    <div className="mt-3 text-xs opacity-75">
                      <p>Formula: TP / (TP + FN)</p>
                    </div>
                  </div>

                  {/* Specificity */}
                  <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.specificity)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-semibold uppercase tracking-wide">Specificity</h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.specificity)}`}>{evaluationData.metrics.specificity_percentage}%</span>
                    </div>
                    <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.specificity)}</p>
                    <p className="text-xs leading-tight">{evaluationData.interpretation.specificity}</p>
                    <div className="mt-3 text-xs opacity-75">
                      <p>Formula: TN / (TN + FP)</p>
                    </div>
                  </div>

                  {/* F1 Score */}
                  <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.f1_score)}`}>
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-semibold uppercase tracking-wide">F1-Score</h3>
                      <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.f1_score)}`}>{evaluationData.metrics.f1_percentage}%</span>
                    </div>
                    <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.f1_score)}</p>
                    <p className="text-xs leading-tight">{evaluationData.interpretation.f1_score}</p>
                    <div className="mt-3 text-xs opacity-75">
                      <p>Formula: 2 × (Precision × Recall) / (Precision + Recall)</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Nearest Neighbors Analysis (Sample Explanations) */}
              {evaluationData.sample_explanations && evaluationData.sample_explanations.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                      <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                        />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">Analisis Tetangga Terdekat (Explainability)</h2>
                      <p className="text-sm text-gray-500">{evaluationData.sample_explanations[0]?.is_real_data ? "Data aktual terbaru dari sistem (3 Terakhir)" : "Contoh simulasi berdasarkan data testing acak"}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-8">
                    {evaluationData.sample_explanations.map((sample, index) => (
                      <div key={index} className="border rounded-lg overflow-hidden shadow-sm">
                        {/* Sample Header */}
                        <div className="bg-gray-50 px-4 py-3 border-b flex flex-wrap justify-between items-center gap-2">
                          <div>
                            <span className={`text-xs font-bold uppercase tracking-wider px-2 py-1 rounded ${sample.is_real_data ? "bg-blue-100 text-blue-800" : "bg-gray-200 text-gray-600"}`}>
                              {sample.is_real_data ? "DATA AKTUAL" : `SAMPLE #${index + 1}`}
                            </span>
                            {sample.timestamp && <span className="text-xs text-gray-500 ml-2">{new Date(sample.timestamp).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })}</span>}
                            <div className="flex space-x-4 mt-2 text-sm text-gray-700">
                              {sample.input.nama && <span className="font-semibold text-gray-900">{sample.input.nama}</span>}
                              <span>
                                <span className="font-semibold text-gray-500">JK:</span> {sample.input.jenis_kelamin}
                              </span>
                              <span>
                                <span className="font-semibold text-gray-500">Usia:</span> {sample.input.usia_bulan} bln
                              </span>
                              <span>
                                <span className="font-semibold text-gray-500">TB:</span> {sample.input.tinggi_badan} cm
                              </span>
                              <span>
                                <span className="font-semibold text-gray-500">BB:</span> {sample.input.berat_badan} kg
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center space-x-3 bg-white px-3 py-1 rounded border">
                            <div className="text-right">
                              <span className="block text-xs text-gray-500">Prediksi Model</span>
                              <span className={`font-bold ${sample.prediction === "Stunting" ? "text-red-600" : "text-green-600"}`}>{sample.prediction}</span>
                            </div>
                            {sample.actual && (
                              <>
                                <div className="h-8 border-l border-gray-300"></div>
                                <div className="text-right">
                                  <span className="block text-xs text-gray-500">Status Aktual</span>
                                  <span className={`font-bold ${sample.actual.includes("Stunting") ? "text-red-600" : "text-green-600"}`}>{sample.actual}</span>
                                </div>
                              </>
                            )}
                          </div>
                        </div>

                        {/* Neighbors Table */}
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Rank
                                </th>
                                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Data Latih
                                </th>
                                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Distance
                                </th>
                                <th scope="col" className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Status (Label)
                                </th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {sample.neighbors.map((neighbor, nIdx) => (
                                <tr key={nIdx} className={nIdx === 0 ? "bg-blue-50/50" : ""}>
                                  <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">#{nIdx + 1}</td>
                                  <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">
                                    JK: {neighbor.jenis_kelamin}, {neighbor.usia_bulan} bln, {neighbor.tinggi_badan} cm, {neighbor.berat_badan} kg
                                  </td>
                                  <td className="px-4 py-2 whitespace-nowrap text-xs font-mono text-gray-600">{neighbor.distance}</td>
                                  <td className="px-4 py-2 whitespace-nowrap">
                                    <span className={`px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${neighbor.label.includes("Stunting") ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"}`}>
                                      {neighbor.label}
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        <div className="bg-gray-50 px-4 py-2 border-t">
                          <p className="text-xs text-gray-500 italic">*Distance mendekati 0 berarti data sangat mirip. Mayoritas label tetangga menentukan hasil prediksi.</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Button */
              <div className="flex justify-center">
                <button onClick={fetchModelPerformance} className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-md flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Refresh Data</span>
                </button>
              </div>
            </div>
          ) : null}
        </main>
      </div>
    </div>
  );
};

export default EvaluasiModelPage;
