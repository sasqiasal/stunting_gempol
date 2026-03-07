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
  const [activeTab, setActiveTab] = useState("evaluasi"); // "evaluasi" | "klasifikasi"
  const [kComparisonData, setKComparisonData] = useState(null);
  const [activeEvalK, setActiveEvalK] = useState(5);

  // State untuk K-tab aktif per sample (index → k value)
  const [sampleKTabs, setSampleKTabs] = useState({});
  const [klasifikasiPage, setKlasifikasiPage] = useState(1);
  const ITEMS_PER_PAGE = 5;

  useEffect(() => {
    fetchModelPerformance();
  }, []);

  const fetchModelPerformance = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [data, kData] = await Promise.all([
        getModelPerformance(),
        compareKValues().catch(() => null),
      ]);
      setEvaluationData(data);
      if (kData) setKComparisonData(kData);
    } catch (err) {
      setError(err.detail || "Gagal mengambil data evaluasi model");
      console.error("Error fetching model performance:", err);
    } finally {
      setIsLoading(false);
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

          {/* Tabs */}
          <div className="px-6 mt-2">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab("evaluasi")}
                className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "evaluasi"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Evaluasi Model
              </button>
              <button
                onClick={() => setActiveTab("klasifikasi")}
                className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "klasifikasi"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Analisis Klasifikasi (K-NN)
              </button>
            </nav>
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
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Belum Ada Data Evaluasi</h3>
              <p className="text-gray-500 max-w-md mx-auto mb-6">
                {error.includes("Belum ada data") || error.includes("tidak cukup")
                  ? "Belum ada data pengukuran. Tambahkan data pengukuran balita terlebih dahulu agar evaluasi model dapat dilakukan." 
                  : error}
              </p>
              <div className="flex justify-center space-x-4">
                <button onClick={fetchModelPerformance} className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition flex items-center space-x-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Coba Lagi</span>
                </button>
                <a href="/pengukuran" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center space-x-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Tambah Pengukuran</span>
                </a>
              </div>
            </div>
          ) : evaluationData ? (
            <div className="space-y-6">
              {activeTab === "evaluasi" && (
                <>
                  {/* Info Card: Data Sumber */}
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-9 h-9 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                        </svg>
                      </div>
                      <div>
                        <h2 className="text-base font-bold text-gray-900">Informasi Data Evaluasi</h2>
                        <p className="text-xs text-gray-500">Sumber, lokasi, dan komposisi data yang digunakan</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Data Latih */}
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <svg className="w-4 h-4 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <span className="text-xs font-bold text-blue-800 uppercase tracking-wide">Data Latih (Training)</span>
                        </div>
                        <div className="space-y-1.5 text-sm text-gray-700">
                          <div className="flex justify-between">
                            <span className="text-gray-500">Sumber file</span>
                            <span className="font-mono font-semibold text-blue-700">data_latih_stunting.csv</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Lokasi</span>
                            <span className="font-medium text-gray-700">Backend server (lokal)</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Jumlah data</span>
                            <span className="font-bold text-blue-800">
                              {kComparisonData?.dataset_info?.total_csv ?? evaluationData?.model_info?.training_note?.match(/\d+/)?.[0] ?? "500"} sampel
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Proporsi digunakan</span>
                            <span className="font-semibold text-green-700">100% (tanpa split)</span>
                          </div>
                          {kComparisonData?.dataset_info && (
                            <div className="flex justify-between">
                              <span className="text-gray-500">Stunting / Normal</span>
                              <span className="font-medium">
                                <span className="text-red-600">{kComparisonData.dataset_info.stunting_train} stunting</span>
                                {" / "}
                                <span className="text-green-600">{kComparisonData.dataset_info.non_stunting_train} normal</span>
                              </span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Data Uji */}
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <svg className="w-4 h-4 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                          <span className="text-xs font-bold text-green-800 uppercase tracking-wide">Data Uji (Testing)</span>
                        </div>
                        <div className="space-y-1.5 text-sm text-gray-700">
                          <div className="flex justify-between">
                            <span className="text-gray-500">Sumber</span>
                            <span className="font-medium text-green-700">Tabel pengukuran (DB)</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Lokasi</span>
                            <span className="font-medium text-gray-700">Supabase (cloud)</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Jumlah data</span>
                            <span className="font-bold text-green-800">
                              {kComparisonData?.dataset_info?.test_size ?? evaluationData?.dataset_info?.total_samples ?? "-"} sampel
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">Ground truth</span>
                            <span className="font-medium text-gray-700">Z-score TB/U &lt; -2 (WHO)</span>
                          </div>
                          {(kComparisonData?.dataset_info ?? evaluationData?.dataset_info) && (
                            <div className="flex justify-between">
                              <span className="text-gray-500">Stunting / Normal</span>
                              <span className="font-medium">
                                <span className="text-red-600">{kComparisonData?.dataset_info?.stunting_count ?? evaluationData?.dataset_info?.stunting_count} stunting</span>
                                {" / "}
                                <span className="text-green-600">{kComparisonData?.dataset_info?.non_stunting_count ?? evaluationData?.dataset_info?.normal_count} normal</span>
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Model info */}
                    <div className="mt-3 bg-gray-50 border border-gray-200 rounded-lg px-4 py-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-gray-600">
                      <span><span className="font-semibold text-gray-700">Algoritma:</span> K-Nearest Neighbors (KNN)</span>
                      <span><span className="font-semibold text-gray-700">Fitur:</span> Jenis Kelamin, Usia, TB, BB, Lingkar Lengan, Lingkar Kepala, Z-Score BB/U, Z-Score TB/U</span>
                      <span><span className="font-semibold text-gray-700">K digunakan sistem:</span> K=5</span>
                      <span><span className="font-semibold text-gray-700">Scaler:</span> StandardScaler (Fit pada CSV, Transform pada data uji)</span>
                    </div>
                  </div>

                  {/* K-Value Comparison Section */}
                  {kComparisonData && kComparisonData.comparisons ? (
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                      <div className="flex items-center justify-between mb-5">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                            <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                          </div>
                          <div>
                            <h2 className="text-xl font-bold text-gray-900">Confusion Matrix & Metrik Evaluasi</h2>
                            <p className="text-sm text-gray-500">Perbandingan performa model untuk setiap nilai K</p>
                          </div>
                        </div>
                        {kComparisonData.recommendation && (
                          <div className="hidden sm:flex items-center space-x-2 bg-indigo-50 border border-indigo-200 rounded-lg px-3 py-2">
                            <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                            </svg>
                            <span className="text-xs font-semibold text-indigo-700">K Terbaik: K={kComparisonData.recommendation.best_k} (F1={kComparisonData.recommendation.f1_score.toFixed(3)})</span>
                          </div>
                        )}
                      </div>

                      {/* K Selector Tabs */}
                      <div className="flex items-center gap-2 mb-6 flex-wrap">
                        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mr-1">Pilih K:</span>
                        {kComparisonData.comparisons.map((comp) => {
                          const isBest = kComparisonData.recommendation?.best_k === comp.k_value;
                          const isActive = activeEvalK === comp.k_value;
                          return (
                            <button
                              key={comp.k_value}
                              onClick={() => setActiveEvalK(comp.k_value)}
                              className={`relative px-5 py-2 rounded-full text-sm font-bold border transition-all ${
                                isActive
                                  ? "bg-indigo-600 text-white border-indigo-600 shadow-md"
                                  : "bg-white text-gray-600 border-gray-300 hover:border-indigo-400 hover:text-indigo-600"
                              }`}
                            >
                              K = {comp.k_value}
                              {isBest && (
                                <span className="ml-1.5 text-[9px] bg-yellow-300 text-yellow-900 px-1 py-0.5 rounded font-bold leading-none">terbaik</span>
                              )}
                              {comp.k_value === 5 && !isBest && (
                                <span className="ml-1.5 text-[9px] bg-indigo-200 text-indigo-800 px-1 py-0.5 rounded font-bold leading-none">digunakan</span>
                              )}
                              {isActive && (
                                <span className={`ml-2 text-[10px] font-semibold text-white/80`}>
                                  {comp.metrics.accuracy_pct}%
                                </span>
                              )}
                            </button>
                          );
                        })}
                      </div>

                      {/* Content for selected K */}
                      {(() => {
                        const selected = kComparisonData.comparisons.find((c) => c.k_value === activeEvalK);
                        if (!selected) return null;
                        const { tp, tn, fp, fn } = selected.confusion_matrix;
                        const m = selected.metrics;
                        return (
                          <div className="space-y-6">
                            {/* Confusion Matrix */}
                            <div className="max-w-2xl mx-auto">
                              <h3 className="text-sm font-semibold text-gray-700 mb-3 text-center uppercase tracking-wide">Confusion Matrix — K={activeEvalK}</h3>
                              <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4 mb-4 text-center">
                                <p className="text-sm text-gray-700">
                                  <span className="font-bold text-purple-900">Total Data Evaluasi: {tp + tn + fp + fn}</span>
                                  <span className="mx-2">|</span>
                                  <span className="text-green-700">Benar: {tp + tn}</span>
                                  <span className="mx-2">|</span>
                                  <span className="text-red-700">Salah: {fp + fn}</span>
                                </p>
                              </div>
                              <div className="grid grid-cols-2 gap-4 mb-4">
                                <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6 text-center">
                                  <div className="text-sm font-medium text-green-700 mb-2">True Negative (TN)</div>
                                  <div className="text-4xl font-bold text-green-900 mb-2">{tn}</div>
                                  <div className="text-xs text-gray-600">Diprediksi Normal, Aktual Normal ✓</div>
                                </div>
                                <div className="bg-orange-50 border-2 border-orange-500 rounded-lg p-6 text-center">
                                  <div className="text-sm font-medium text-orange-700 mb-2">False Positive (FP)</div>
                                  <div className="text-4xl font-bold text-orange-900 mb-2">{fp}</div>
                                  <div className="text-xs text-gray-600">Diprediksi Stunting, Aktual Normal ✗</div>
                                </div>
                                <div className="bg-yellow-50 border-2 border-yellow-500 rounded-lg p-6 text-center">
                                  <div className="text-sm font-medium text-yellow-700 mb-2">False Negative (FN)</div>
                                  <div className="text-4xl font-bold text-yellow-900 mb-2">{fn}</div>
                                  <div className="text-xs text-gray-600">Diprediksi Normal, Aktual Stunting ✗</div>
                                </div>
                                <div className="bg-blue-50 border-2 border-blue-500 rounded-lg p-6 text-center">
                                  <div className="text-sm font-medium text-blue-700 mb-2">True Positive (TP)</div>
                                  <div className="text-4xl font-bold text-blue-900 mb-2">{tp}</div>
                                  <div className="text-xs text-gray-600">Diprediksi Stunting, Aktual Stunting ✓</div>
                                </div>
                              </div>
                              <div className="bg-gray-50 rounded-lg p-4 text-center">
                                <p className="text-xs text-gray-600">
                                  <span className="font-semibold">Kolom:</span> Prediksi Model |<span className="font-semibold ml-2">Baris:</span> Kondisi Aktual
                                </p>
                              </div>
                            </div>

                            {/* Metrik Evaluasi */}
                            <div>
                              <h3 className="text-sm font-semibold text-gray-700 mb-3 text-center uppercase tracking-wide">Metrik Evaluasi — K={activeEvalK}</h3>
                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                                <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(m.accuracy)}`}>
                                  <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-sm font-semibold uppercase tracking-wide">Akurasi</h3>
                                    <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(m.accuracy)}`}>{m.accuracy_pct}%</span>
                                  </div>
                                  <p className="text-3xl font-bold mb-2">{formatMetricValue(m.accuracy)}</p>
                                  <div className="mt-3 text-xs opacity-75"><p>Formula: (TP + TN) / Total</p></div>
                                </div>
                                <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(m.precision)}`}>
                                  <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-sm font-semibold uppercase tracking-wide">Presisi</h3>
                                    <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(m.precision)}`}>{m.precision_pct}%</span>
                                  </div>
                                  <p className="text-3xl font-bold mb-2">{formatMetricValue(m.precision)}</p>
                                  <div className="mt-3 text-xs opacity-75"><p>Formula: TP / (TP + FP)</p></div>
                                </div>
                                <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(m.recall)}`}>
                                  <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-sm font-semibold uppercase tracking-wide">Recall</h3>
                                    <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(m.recall)}`}>{m.recall_pct}%</span>
                                  </div>
                                  <p className="text-3xl font-bold mb-2">{formatMetricValue(m.recall)}</p>
                                  <div className="mt-3 text-xs opacity-75"><p>Formula: TP / (TP + FN)</p></div>
                                </div>
                                <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(m.specificity)}`}>
                                  <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-sm font-semibold uppercase tracking-wide">Specificity</h3>
                                    <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(m.specificity)}`}>{m.specificity_pct}%</span>
                                  </div>
                                  <p className="text-3xl font-bold mb-2">{formatMetricValue(m.specificity)}</p>
                                  <div className="mt-3 text-xs opacity-75"><p>Formula: TN / (TN + FP)</p></div>
                                </div>
                                <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(m.f1_score)}`}>
                                  <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-sm font-semibold uppercase tracking-wide">F1-Score</h3>
                                    <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(m.f1_score)}`}>{m.f1_pct}%</span>
                                  </div>
                                  <p className="text-3xl font-bold mb-2">{formatMetricValue(m.f1_score)}</p>
                                  <div className="mt-3 text-xs opacity-75"><p>Formula: 2 × (P × R) / (P + R)</p></div>
                                </div>
                              </div>
                            </div>

                            {/* Perbandingan Ringkas semua K */}
                            <div className="overflow-x-auto">
                              <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">Tabel Perbandingan Semua K</h3>
                              <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg overflow-hidden">
                                <thead className="bg-gray-50">
                                  <tr>
                                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">K</th>
                                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Akurasi</th>
                                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Presisi</th>
                                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Recall</th>
                                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Specificity</th>
                                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">F1-Score</th>
                                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">TP</th>
                                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">TN</th>
                                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">FP</th>
                                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">FN</th>
                                  </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                  {kComparisonData.comparisons.map((comp) => {
                                    const isBest = kComparisonData.recommendation?.best_k === comp.k_value;
                                    const isActvRow = activeEvalK === comp.k_value;
                                    return (
                                      <tr
                                        key={comp.k_value}
                                        onClick={() => setActiveEvalK(comp.k_value)}
                                        className={`cursor-pointer transition-colors ${
                                          isActvRow ? "bg-indigo-50" : "hover:bg-gray-50"
                                        }`}
                                      >
                                        <td className="px-4 py-3 whitespace-nowrap">
                                          <div className="flex items-center gap-2">
                                            <span className={`font-bold text-sm ${ isActvRow ? "text-indigo-700" : "text-gray-800"}`}>K={comp.k_value}</span>
                                            {isBest && <span className="text-[9px] bg-yellow-300 text-yellow-900 px-1.5 py-0.5 rounded font-bold">terbaik</span>}
                                            {comp.k_value === 5 && <span className="text-[9px] bg-indigo-200 text-indigo-800 px-1.5 py-0.5 rounded font-bold">dipakai</span>}
                                          </div>
                                        </td>
                                        <td className="px-4 py-3 text-center text-sm font-mono">{comp.metrics.accuracy_pct}%</td>
                                        <td className="px-4 py-3 text-center text-sm font-mono">{comp.metrics.precision_pct}%</td>
                                        <td className="px-4 py-3 text-center text-sm font-mono">{comp.metrics.recall_pct}%</td>
                                        <td className="px-4 py-3 text-center text-sm font-mono">{comp.metrics.specificity_pct}%</td>
                                        <td className="px-4 py-3 text-center">
                                          <span className={`text-sm font-mono font-bold ${ isBest ? "text-indigo-700" : "text-gray-700"}`}>{comp.metrics.f1_pct}%</span>
                                        </td>
                                        <td className="px-4 py-3 text-center text-sm text-blue-700 font-semibold">{comp.confusion_matrix.tp}</td>
                                        <td className="px-4 py-3 text-center text-sm text-green-700 font-semibold">{comp.confusion_matrix.tn}</td>
                                        <td className="px-4 py-3 text-center text-sm text-orange-700 font-semibold">{comp.confusion_matrix.fp}</td>
                                        <td className="px-4 py-3 text-center text-sm text-yellow-700 font-semibold">{comp.confusion_matrix.fn}</td>
                                      </tr>
                                    );
                                  })}
                                </tbody>
                              </table>
                              <p className="text-xs text-gray-400 mt-2">*Klik baris untuk memilih K. Data latih: 500 sampel CSV. Data uji: pengukuran dari sistem.</p>
                            </div>
                          </div>
                        );
                      })()}
                    </div>
                  ) : (
                    // Fallback: tampilkan data dari model-performance biasa jika compare-k gagal
                    <>
                  {/* Confusion Matrix */}
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center space-x-3 mb-6">
                      <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                        <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-gray-900">Confusion Matrix</h2>
                        <p className="text-sm text-gray-500">Matriks prediksi vs aktual</p>
                      </div>
                    </div>
                    <div className="max-w-2xl mx-auto">
                      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4 mb-4 text-center">
                        <p className="text-sm text-gray-700">
                          <span className="font-bold text-purple-900">Total: {evaluationData.confusion_matrix.true_positive + evaluationData.confusion_matrix.true_negative + evaluationData.confusion_matrix.false_positive + evaluationData.confusion_matrix.false_negative}</span>
                          <span className="mx-2">|</span>
                          <span className="text-green-700">Benar: {evaluationData.confusion_matrix.true_positive + evaluationData.confusion_matrix.true_negative}</span>
                          <span className="mx-2">|</span>
                          <span className="text-red-700">Salah: {evaluationData.confusion_matrix.false_positive + evaluationData.confusion_matrix.false_negative}</span>
                        </p>
                      </div>
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6 text-center">
                          <div className="text-sm font-medium text-green-700 mb-2">True Negative (TN)</div>
                          <div className="text-4xl font-bold text-green-900 mb-2">{evaluationData.confusion_matrix.true_negative}</div>
                          <div className="text-xs text-gray-600">Diprediksi Normal, Aktual Normal ✓</div>
                        </div>
                        <div className="bg-orange-50 border-2 border-orange-500 rounded-lg p-6 text-center">
                          <div className="text-sm font-medium text-orange-700 mb-2">False Positive (FP)</div>
                          <div className="text-4xl font-bold text-orange-900 mb-2">{evaluationData.confusion_matrix.false_positive}</div>
                          <div className="text-xs text-gray-600">Diprediksi Stunting, Aktual Normal ✗</div>
                        </div>
                        <div className="bg-yellow-50 border-2 border-yellow-500 rounded-lg p-6 text-center">
                          <div className="text-sm font-medium text-yellow-700 mb-2">False Negative (FN)</div>
                          <div className="text-4xl font-bold text-yellow-900 mb-2">{evaluationData.confusion_matrix.false_negative}</div>
                          <div className="text-xs text-gray-600">Diprediksi Normal, Aktual Stunting ✗</div>
                        </div>
                        <div className="bg-blue-50 border-2 border-blue-500 rounded-lg p-6 text-center">
                          <div className="text-sm font-medium text-blue-700 mb-2">True Positive (TP)</div>
                          <div className="text-4xl font-bold text-blue-900 mb-2">{evaluationData.confusion_matrix.true_positive}</div>
                          <div className="text-xs text-gray-600">Diprediksi Stunting, Aktual Stunting ✓</div>
                        </div>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-4 text-center">
                        <p className="text-xs text-gray-600"><span className="font-semibold">Kolom:</span> Prediksi Model |<span className="font-semibold ml-2">Baris:</span> Kondisi Aktual</p>
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
                      <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.accuracy)}`}>
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-semibold uppercase tracking-wide">Akurasi</h3>
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.accuracy)}`}>{evaluationData.metrics.accuracy_percentage}%</span>
                        </div>
                        <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.accuracy)}</p>
                        <p className="text-xs leading-tight">{evaluationData.interpretation.accuracy}</p>
                        <div className="mt-3 text-xs opacity-75"><p>Formula: (TP + TN) / Total</p></div>
                      </div>
                      <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.precision)}`}>
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-semibold uppercase tracking-wide">Presisi</h3>
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.precision)}`}>{evaluationData.metrics.precision_percentage}%</span>
                        </div>
                        <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.precision)}</p>
                        <p className="text-xs leading-tight">{evaluationData.interpretation.precision}</p>
                        <div className="mt-3 text-xs opacity-75"><p>Formula: TP / (TP + FP)</p></div>
                      </div>
                      <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.recall)}`}>
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-semibold uppercase tracking-wide">Recall</h3>
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.recall)}`}>{evaluationData.metrics.recall_percentage}%</span>
                        </div>
                        <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.recall)}</p>
                        <p className="text-xs leading-tight">{evaluationData.interpretation.recall}</p>
                        <div className="mt-3 text-xs opacity-75"><p>Formula: TP / (TP + FN)</p></div>
                      </div>
                      <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.specificity)}`}>
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-semibold uppercase tracking-wide">Specificity</h3>
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.specificity)}`}>{evaluationData.metrics.specificity_percentage}%</span>
                        </div>
                        <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.specificity)}</p>
                        <p className="text-xs leading-tight">{evaluationData.interpretation.specificity}</p>
                        <div className="mt-3 text-xs opacity-75"><p>Formula: TN / (TN + FP)</p></div>
                      </div>
                      <div className={`rounded-lg border-2 p-5 ${getMetricColorClass(evaluationData.metrics.f1_score)}`}>
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-sm font-semibold uppercase tracking-wide">F1-Score</h3>
                          <span className={`px-2 py-1 text-xs font-semibold rounded ${getMetricBadgeClass(evaluationData.metrics.f1_score)}`}>{evaluationData.metrics.f1_percentage}%</span>
                        </div>
                        <p className="text-3xl font-bold mb-2">{formatMetricValue(evaluationData.metrics.f1_score)}</p>
                        <p className="text-xs leading-tight">{evaluationData.interpretation.f1_score}</p>
                        <div className="mt-3 text-xs opacity-75"><p>Formula: 2 × (P × R) / (P + R)</p></div>
                      </div>
                    </div>
                  </div>
                    </>
                  )}
                </>
              )}

              {activeTab === "klasifikasi" && (
                <>
                  {/* Nearest Neighbors Analysis (Sample Explanations) */}
                  {evaluationData.sample_explanations && evaluationData.sample_explanations.length > 0 ? (
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
                      <p className="text-sm text-gray-500">{evaluationData.sample_explanations[0]?.is_real_data ? "Data aktual terbaru dari sistem (10 Terakhir) — prediksi ditampilkan untuk K=3, K=5, K=7" : "Contoh simulasi berdasarkan data testing acak"}</p>
                    </div>
                  </div>

                  {/* Datatable info bar */}
                  {evaluationData.sample_explanations.length > ITEMS_PER_PAGE && (
                    <div className="flex items-center justify-between mb-4 px-1">
                      <p className="text-sm text-gray-500">
                        Menampilkan{" "}
                        <span className="font-semibold text-gray-700">
                          {(klasifikasiPage - 1) * ITEMS_PER_PAGE + 1}–{Math.min(klasifikasiPage * ITEMS_PER_PAGE, evaluationData.sample_explanations.length)}
                        </span>{" "}
                        dari{" "}
                        <span className="font-semibold text-gray-700">{evaluationData.sample_explanations.length}</span> data
                      </p>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => setKlasifikasiPage(1)}
                          disabled={klasifikasiPage === 1}
                          className="px-2 py-1 text-xs rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-100 transition"
                          title="Halaman pertama"
                        >«</button>
                        <button
                          onClick={() => setKlasifikasiPage((p) => Math.max(1, p - 1))}
                          disabled={klasifikasiPage === 1}
                          className="px-2 py-1 text-xs rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-100 transition"
                        >‹</button>
                        {Array.from({ length: Math.ceil(evaluationData.sample_explanations.length / ITEMS_PER_PAGE) }, (_, i) => i + 1).map((pg) => (
                          <button
                            key={pg}
                            onClick={() => setKlasifikasiPage(pg)}
                            className={`px-2.5 py-1 text-xs rounded border transition ${
                              pg === klasifikasiPage
                                ? "bg-indigo-600 text-white border-indigo-600 font-bold"
                                : "border-gray-300 hover:bg-gray-100"
                            }`}
                          >{pg}</button>
                        ))}
                        <button
                          onClick={() => setKlasifikasiPage((p) => Math.min(Math.ceil(evaluationData.sample_explanations.length / ITEMS_PER_PAGE), p + 1))}
                          disabled={klasifikasiPage === Math.ceil(evaluationData.sample_explanations.length / ITEMS_PER_PAGE)}
                          className="px-2 py-1 text-xs rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-100 transition"
                        >›</button>
                        <button
                          onClick={() => setKlasifikasiPage(Math.ceil(evaluationData.sample_explanations.length / ITEMS_PER_PAGE))}
                          disabled={klasifikasiPage === Math.ceil(evaluationData.sample_explanations.length / ITEMS_PER_PAGE)}
                          className="px-2 py-1 text-xs rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-100 transition"
                          title="Halaman terakhir"
                        >»</button>
                      </div>
                    </div>
                  )}

                  <div className="grid grid-cols-1 gap-8">
                    {evaluationData.sample_explanations
                      .slice((klasifikasiPage - 1) * ITEMS_PER_PAGE, klasifikasiPage * ITEMS_PER_PAGE)
                      .map((sample, pageIdx) => {
                      const index = (klasifikasiPage - 1) * ITEMS_PER_PAGE + pageIdx;
                      const activeK = sampleKTabs[index] ?? 5;
                      // Pick the k_result for the active K, or fall back to top-level neighbors (K=5)
                      const kResult = sample.k_results
                        ? sample.k_results.find((r) => r.k === activeK)
                        : { k: 5, prediction: sample.prediction, neighbors: sample.neighbors };
                      const displayNeighbors = kResult ? kResult.neighbors : sample.neighbors;
                      const displayPrediction = kResult ? kResult.prediction : sample.prediction;

                      return (
                      <div key={index} className="border rounded-lg overflow-hidden shadow-sm">
                        {/* Sample Header */}
                        <div className="bg-gray-50 px-4 py-3 border-b flex flex-wrap justify-between items-center gap-2">
                          <div>
                            <span className={`text-xs font-bold uppercase tracking-wider px-2 py-1 rounded ${sample.is_real_data ? "bg-blue-100 text-blue-800" : "bg-gray-200 text-gray-600"}`}>
                              {sample.is_real_data ? "DATA AKTUAL" : `SAMPLE #${index + 1}`}
                            </span>
                            {sample.timestamp && <span className="text-xs text-gray-500 ml-2">{new Date(sample.timestamp).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })}</span>}
                            <div className="flex flex-wrap space-x-4 mt-2 text-sm text-gray-700">
                              {sample.input.nama && <span className="font-semibold text-gray-900">{sample.input.nama}</span>}
                              <span><span className="font-semibold text-gray-500">JK:</span> {sample.input.jenis_kelamin}</span>
                              <span><span className="font-semibold text-gray-500">Usia:</span> {sample.input.usia_bulan} bln</span>
                              <span><span className="font-semibold text-gray-500">TB:</span> {sample.input.tinggi_badan} cm</span>
                              <span><span className="font-semibold text-gray-500">BB:</span> {sample.input.berat_badan} kg</span>
                            </div>
                          </div>
                          {sample.actual && (
                            <div className="flex items-center space-x-2 bg-white px-3 py-1 rounded border text-right">
                              <div>
                                <span className="block text-xs text-gray-500">Status Aktual</span>
                                <span className={`font-bold ${sample.actual.includes("Stunting") ? "text-red-600" : "text-green-600"}`}>{sample.actual}</span>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* K Selector Tabs + Prediction per K */}
                        {sample.k_results ? (
                          <div className="px-4 pt-4 pb-2 bg-white border-b">
                            <div className="flex items-center gap-2 mb-3 flex-wrap">
                              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Hasil per Nilai K:</span>
                              {sample.k_results.map((kr) => (
                                <button
                                  key={kr.k}
                                  onClick={() => setSampleKTabs((prev) => ({ ...prev, [index]: kr.k }))}
                                  className={`relative px-4 py-1.5 rounded-full text-xs font-bold border transition-all ${
                                    activeK === kr.k
                                      ? kr.prediction === "Stunting"
                                        ? "bg-red-600 text-white border-red-600 shadow"
                                        : "bg-green-600 text-white border-green-600 shadow"
                                      : "bg-white text-gray-600 border-gray-300 hover:border-gray-400"
                                  }`}
                                >
                                  K = {kr.k}
                                  {kr.k === 5 && (
                                    <span className="ml-1.5 text-[9px] bg-indigo-200 text-indigo-800 px-1 py-0.5 rounded font-bold leading-none">digunakan</span>
                                  )}
                                  <span className={`ml-2 text-[10px] font-semibold ${activeK === kr.k ? "text-white/90" : kr.prediction === "Stunting" ? "text-red-500" : "text-green-600"}`}>
                                    → {kr.prediction}
                                  </span>
                                </button>
                              ))}
                            </div>
                            <div className="text-xs text-gray-500 italic">
                              Menampilkan <strong>{activeK}</strong> tetangga terdekat.{" "}
                              {displayPrediction === "Stunting"
                                ? <span className="text-red-600 font-semibold">Prediksi: Stunting</span>
                                : <span className="text-green-600 font-semibold">Prediksi: Normal</span>}
                            </div>
                          </div>
                        ) : null}

                        {/* Neighbors Table */}
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data Latih</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Distance</th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status (Label)</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {(displayNeighbors || []).map((neighbor, nIdx) => (
                                <tr key={nIdx} className={nIdx === 0 ? "bg-blue-50/50" : ""}>
                                  <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">#{nIdx + 1}</td>
                                  <td className="px-4 py-2 whitespace-nowrap text-xs text-gray-500">
                                    JK: {neighbor.jenis_kelamin}, {neighbor.usia_bulan} bln, {neighbor.tinggi_badan} cm, {neighbor.berat_badan} kg
                                  </td>
                                  <td className="px-4 py-2 whitespace-nowrap text-xs font-mono text-gray-600">{neighbor.distance}</td>
                                  <td className="px-4 py-2 whitespace-nowrap">
                                    <span className={`px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full ${(neighbor.label || "").includes("Stunting") ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"}`}>
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
                      );
                    })}
                  </div>

                  {/* Pagination bottom */}
                  {evaluationData.sample_explanations.length > ITEMS_PER_PAGE && (
                    <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-100">
                      <p className="text-sm text-gray-500">
                        Halaman <span className="font-semibold text-gray-700">{klasifikasiPage}</span> dari{" "}
                        <span className="font-semibold text-gray-700">{Math.ceil(evaluationData.sample_explanations.length / ITEMS_PER_PAGE)}</span>
                      </p>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setKlasifikasiPage((p) => Math.max(1, p - 1))}
                          disabled={klasifikasiPage === 1}
                          className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg border border-gray-300 disabled:opacity-40 hover:bg-gray-50 transition font-medium"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                          Sebelumnya
                        </button>
                        <button
                          onClick={() => setKlasifikasiPage((p) => Math.min(Math.ceil(evaluationData.sample_explanations.length / ITEMS_PER_PAGE), p + 1))}
                          disabled={klasifikasiPage === Math.ceil(evaluationData.sample_explanations.length / ITEMS_PER_PAGE)}
                          className="flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg border border-gray-300 disabled:opacity-40 hover:bg-gray-50 transition font-medium"
                        >
                          Berikutnya
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
                  ) : (
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
                      <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                      </svg>
                      <h3 className="text-lg font-medium text-gray-900 mb-1">Belum Ada Data Klasifikasi</h3>
                      <p className="text-gray-500">Lakukan prediksi/klasifikasi pada menu Data Balita terlebih dahulu untuk melihat analisis tetangga terdekat.</p>
                    </div>
                  )}
                </>
              )}

              {/* Action Button */}
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

