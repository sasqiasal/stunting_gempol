/**
 * Evaluasi Global Model Page
 * Admin: Evaluasi performa model KNN pada semua data
 * Menampilkan 4x4 Confusion Matrix dan metrics (Precision, Recall, F1-Score)
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import Sidebar from '../components/Sidebar';
import { toast } from 'react-hot-toast';

const EvaluasiGlobalPage = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingKComparison, setLoadingKComparison] = useState(false);
  const [error, setError] = useState(null);
  const [evaluasi, setEvaluasi] = useState(null);
  const [kComparison, setKComparison] = useState([]);
  const [selectedK, setSelectedK] = useState(5);
  const [bestK, setBestK] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [availableMonths, setAvailableMonths] = useState([]);
  const [loadingMonths, setLoadingMonths] = useState(true);

  // Redirect jika bukan admin
  useEffect(() => {
    if (user?.role !== 'admin') {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  // Fetch available months
  const fetchAvailableMonths = async () => {
    try {
      setLoadingMonths(true);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';
      const response = await fetch(
        `${apiUrl}/evaluasi/available-months`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setAvailableMonths(data.data || []);
      }
    } catch (err) {
      console.error('Error fetching available months:', err);
      setAvailableMonths([]);
    } finally {
      setLoadingMonths(false);
    }
  };

  // Fetch evaluasi global
  const fetchEvaluasi = async (bulan = null) => {
    try {
      setLoading(true);
      setError(null);

      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';
      const bulanParam = bulan ? `?bulan=${bulan}` : '';
      const response = await fetch(
        `${apiUrl}/evaluasi/global${bulanParam}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Check if data has success or is null
      if (data.data === null || !data.status || data.status !== 'success') {
        setError(data.message || 'Tidak ada data pengukuran untuk dievaluasi');
        setEvaluasi(null);
        if (data.message) toast.error(data.message);
      } else {
        setEvaluasi(data.data);
        setError(null);
        if (!bulan) toast.success('Data evaluasi global berhasil dimuat');
      }
    } catch (err) {
      console.error('Error fetching global evaluasi:', err);
      const errorMsg = err.message || 'Gagal mengambil data evaluasi global';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // Fetch K comparison data
  const fetchKComparison = async () => {
    const bulan = selectedMonth?.value;
    try {
      setLoadingKComparison(true);
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1';
      const bulanParam = bulan ? `?bulan=${bulan}` : '';
      const response = await fetch(
        `${apiUrl}/evaluasi/global-k-comparison${bulanParam}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.data && data.data.k_comparison) {
        setKComparison(data.data.k_comparison);
        if (data.data.best_k) {
          setBestK(data.data.best_k);
          setSelectedK(data.data.best_k.k);
        }
      }
    } catch (err) {
      console.error('Error fetching K comparison:', err);
    } finally {
      setLoadingKComparison(false);
    }
  };

  // Initialize: fetch months then data
  useEffect(() => {
    fetchAvailableMonths();
    fetchEvaluasi();
  }, []);

  // Re-fetch evaluation when month changes
  useEffect(() => {
    if (selectedMonth !== null) {
      fetchEvaluasi(selectedMonth.value);
      fetchKComparison();
    }
  }, [selectedMonth]);

  const handleMonthChange = (monthValue) => {
    setSelectedMonth(monthValue ? { value: monthValue, label: availableMonths.find(m => m.value === monthValue)?.label } : null);
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  if (!user || user.role !== 'admin') {
    return null;
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-2 rounded-md text-gray-700 hover:bg-gray-100 lg:hidden"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Evaluasi Global Model</h1>
            </div>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              Refresh
            </button>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {error && (
            <div className="p-4 mb-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-800">{error}</p>
                  </div>
                  <button
                    onClick={() => setError(null)}
                    className="ml-auto text-red-400 hover:text-red-500"
                  >
                    <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          )}

          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-500">Memuat data evaluasi...</p>
              </div>
            </div>
          ) : evaluasi ? (
            <div className="max-w-6xl mx-auto p-4 space-y-6">
              {/* Month Filter */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Filter Bulan</label>
                <select
                  value={selectedMonth?.value || ''}
                  onChange={(e) => handleMonthChange(e.target.value)}
                  className="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  disabled={loadingMonths}
                >
                  <option value="">Semua Bulan</option>
                  {availableMonths.map((month) => (
                    <option key={month.value} value={month.value}>
                      {month.label}
                    </option>
                  ))}
                </select>
                {selectedMonth && (
                  <p className="text-xs text-gray-500 mt-1">Data ditampilkan untuk: {selectedMonth.label}</p>
                )}
              </div>

              {/* Overview Section - Metrics dan Confusion Matrix Data */}
              <div className="space-y-4">
                {/* Row 1: Main Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                  <div className="bg-white rounded-lg shadow p-6">
                    <p className="text-gray-600 text-sm font-medium">Total Sampel</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {evaluasi.metadata?.total_data || evaluasi.n_testing_samples || 0}
                    </p>
                    <p className="text-xs text-gray-500 mt-2">Semua Data Admin</p>
                  </div>
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow p-6">
                    <p className="text-gray-700 text-sm font-medium">Accuracy</p>
                    <p className="text-3xl font-bold text-blue-600 mt-2">
                      {((evaluasi.binary_classification?.metrics?.accuracy || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow p-6">
                    <p className="text-gray-700 text-sm font-medium">Precision</p>
                    <p className="text-3xl font-bold text-green-600 mt-2">
                      {((evaluasi.binary_classification?.metrics?.precision || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg shadow p-6">
                    <p className="text-gray-700 text-sm font-medium">Recall</p>
                    <p className="text-3xl font-bold text-orange-600 mt-2">
                      {((evaluasi.binary_classification?.metrics?.recall || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg shadow p-6">
                    <p className="text-gray-700 text-sm font-medium">Specificity</p>
                    <p className="text-3xl font-bold text-purple-600 mt-2">
                      {((evaluasi.binary_classification?.metrics?.specificity || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg shadow p-6">
                    <p className="text-gray-700 text-sm font-medium">F1 Score</p>
                    <p className="text-3xl font-bold text-red-600 mt-2">
                      {((evaluasi.binary_classification?.metrics?.f1_score || 0) * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                {/* Row 2: Confusion Matrix Values */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white border border-gray-200 rounded-lg shadow p-6">
                    <p className="text-gray-600 text-sm font-medium">TP</p>
                    <p className="text-4xl font-bold text-green-600 mt-3">
                      {evaluasi.binary_classification?.metrics?.tp || 0}
                    </p>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg shadow p-6">
                    <p className="text-gray-600 text-sm font-medium">TN</p>
                    <p className="text-4xl font-bold text-blue-600 mt-3">
                      {evaluasi.binary_classification?.metrics?.tn || 0}
                    </p>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg shadow p-6">
                    <p className="text-gray-600 text-sm font-medium">FP</p>
                    <p className="text-4xl font-bold text-orange-600 mt-3">
                      {evaluasi.binary_classification?.metrics?.fp || 0}
                    </p>
                  </div>
                  <div className="bg-white border border-gray-200 rounded-lg shadow p-6">
                    <p className="text-gray-600 text-sm font-medium">FN</p>
                    <p className="text-4xl font-bold text-red-600 mt-3">
                      {evaluasi.binary_classification?.metrics?.fn || 0}
                    </p>
                  </div>
                </div>
              </div>

              {/* Perbandingan K Values */}
              {!loadingKComparison && kComparison.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">
                    Perbandingan K Values (3, 5, 7, 9)
                  </h2>
                  {bestK && (
                    <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
                      <p className="text-sm text-blue-800">
                        <span className="font-semibold">✓ K Terbaik: </span>
                        {bestK.recommendation}
                      </p>
                    </div>
                  )}
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm border-collapse">
                      <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                          <th className="border border-gray-300 p-2 text-left font-bold">K</th>
                          <th className="border border-gray-300 p-2 text-center font-bold">Akurasi</th>
                          <th className="border border-gray-300 p-2 text-center font-bold">Precision</th>
                          <th className="border border-gray-300 p-2 text-center font-bold">Recall</th>
                          <th className="border border-gray-300 p-2 text-center font-bold">Specificity</th>
                          <th className="border border-gray-300 p-2 text-center font-bold">F1-Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {kComparison.map((item) => (
                          <tr
                            key={item.k}
                            onClick={() => setSelectedK(item.k)}
                            className={`border-b border-gray-100 cursor-pointer ${
                              selectedK === item.k ? 'bg-blue-50' : 'hover:bg-gray-50'
                            }`}
                          >
                            <td className="border border-gray-300 p-2 font-bold">{item.k}</td>
                            <td className="border border-gray-300 p-2 text-center">{(item.accuracy_percent || 0).toFixed(2)}%</td>
                            <td className="border border-gray-300 p-2 text-center">{(item.precision_percent || 0).toFixed(2)}%</td>
                            <td className="border border-gray-300 p-2 text-center">{(item.recall_percent || 0).toFixed(2)}%</td>
                            <td className="border border-gray-300 p-2 text-center">{(item.specificity_percent || 0).toFixed(2)}%</td>
                            <td className="border border-gray-300 p-2 text-center">{(item.f1_score_percent || 0).toFixed(2)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <p className="text-xs text-gray-500 mt-3">💡 Klik pada baris untuk memilih K value</p>
                </div>
              )}

              {/* Confusion Matrix */}
              {evaluasi.confusion_matrix && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">
                    4x4 Confusion Matrix
                  </h2>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm border-collapse">
                      <thead>
                        <tr>
                          <th className="border border-gray-300 bg-gray-100 p-2">
                            Prediksi / Aktual
                          </th>
                          <th className="border border-gray-300 bg-gray-100 p-2">
                            Normal + GB
                          </th>
                          <th className="border border-gray-300 bg-gray-100 p-2">
                            Normal + KG
                          </th>
                          <th className="border border-gray-300 bg-gray-100 p-2">
                            Stunting + GB
                          </th>
                          <th className="border border-gray-300 bg-gray-100 p-2">
                            Stunting + KG
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {evaluasi.confusion_matrix.map((row, idx) => (
                          <tr key={idx}>
                            <td className="border border-gray-300 bg-gray-100 p-2 font-semibold">
                              {['Normal + GB', 'Normal + KG', 'Stunting + GB', 'Stunting + KG'][idx]}
                            </td>
                            {row.map((val, colIdx) => (
                              <td
                                key={colIdx}
                                className={`border border-gray-300 p-2 text-center font-semibold ${
                                  idx === colIdx
                                    ? 'bg-green-100 text-green-900'
                                    : 'bg-gray-50 text-gray-700'
                                }`}
                              >
                                {val}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    GB = Gizi Baik | KG = Kurang Gizi
                  </p>
                </div>
              )}


              {/* Model Info */}
              {evaluasi.model_info && (
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Informasi Model</h2>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Algoritma</p>
                      <p className="font-semibold text-gray-900">
                        {evaluasi.model_info.algorithm || 'KNeighborsClassifier'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">K Value</p>
                      <p className="font-semibold text-gray-900">
                        {evaluasi.model_info.k_value || 5}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">Metric Distance</p>
                      <p className="font-semibold text-gray-900">
                        {evaluasi.model_info.metric || 'euclidean'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-600">Weights</p>
                      <p className="font-semibold text-gray-900">
                        {evaluasi.model_info.weights || 'distance'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="mt-2 text-lg font-medium text-gray-900">Tidak Ada Data Pengukuran</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {error || 'Silakan tambahkan data pengukuran balita terlebih dahulu sebelum melakukan evaluasi model.'}
                </p>
                <button
                  onClick={handleRefresh}
                  className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                >
                  Coba Lagi
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default EvaluasiGlobalPage;
