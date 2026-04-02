import React, { useState, useEffect } from 'react';
import Sidebar from "../components/Sidebar";
import { useAuthStore } from "../store/authStore";
import evaluationService from '@/services/evaluationService';

const CLASS_NAMES = {
  0: 'Normal + Gizi Baik',
  1: 'Normal + Kurang Gizi',
  2: 'Stunting + Gizi Baik',
  3: 'Stunting + Kurang Gizi'
};

const EvaluasiModelPage = () => {
  const { user } = useAuthStore();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [evaluationData, setEvaluationData] = useState(null);
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('ringkasan'); // 'ringkasan' or 'riwayat'
  const [expandedNeighbors, setExpandedNeighbors] = useState(null); // Track expanded neighbor row
  const [selectedMonth, setSelectedMonth] = useState(null); // Month filter state
  const [availableMonths, setAvailableMonths] = useState([]); // Dynamic months from DB
  const [loadingMonths, setLoadingMonths] = useState(true); // Loading state for months
  const [searchNamaBalita, setSearchNamaBalita] = useState(''); // Search filter for balita name
  
  // K-value selector states
  const [selectedKForPrediction, setSelectedKForPrediction] = useState({}); // {predictionId: kValue}
  const [loadingNeighborsFor, setLoadingNeighborsFor] = useState(null); // Track which prediction is loading neighbors
  const [neighborsData, setNeighborsData] = useState({}); // {predictionId: neighbors}

  useEffect(() => {
    fetchAvailableMonths();
    fetchAllData();
  }, []);

  // Fetch available months from backend
  const fetchAvailableMonths = async () => {
    setLoadingMonths(true);
    try {
      const months = await evaluationService.getAvailableMonths();
      setAvailableMonths(months);
    } catch (err) {
      console.error('Error fetching available months:', err);
      setAvailableMonths([]);
    } finally {
      setLoadingMonths(false);
    }
  };

  const fetchAllData = async (bulan = null) => {
    setLoading(true);
    setError(null);
    try {
      const [evalData, historyData] = await Promise.all([
        evaluationService.getRealtimeEvaluation(bulan),
        evaluationService.getPredictionHistory(100, bulan)
      ]);
      
      // Check if evaluation was successful
      if (evalData && !evalData.success) {
        setError(evalData.message || 'Tidak ada data pengukuran untuk dievaluasi');
        setEvaluationData(null);
      } else {
        setEvaluationData(evalData);
      }
      
      // Sort prediction history by tanggal DESC (newest first)
      const sortedHistory = (historyData || []).sort((a, b) => {
        if (!a.tanggal || !b.tanggal) return 0;
        return new Date(b.tanggal) - new Date(a.tanggal);
      });
      setPredictionHistory(sortedHistory);
    } catch (err) {
      setError(err.message || 'Gagal memuat data');
    } finally {
      setLoading(false);
    }
  };

  const handleMonthChange = (monthValue) => {
    setSelectedMonth(monthValue ? { value: monthValue, label: availableMonths.find(m => m.value === monthValue)?.label } : null);
    fetchAllData(monthValue);
  };

  // Fetch neighbors dengan k value tertentu
  const fetchNeighborsByK = async (pengukuranId, kValue) => {
    setLoadingNeighborsFor(pengukuranId);
    try {
      const response = await fetch(`/api/v1/neighbors/by-k/${pengukuranId}?k=${kValue}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Gagal mengambil data tetangga terdekat');
      }
      
      const data = await response.json();
      
      if (data.status === 'success') {
        // Update neighbors data dan selected K untuk prediksi ini
        setNeighborsData(prev => ({
          ...prev,
          [pengukuranId]: data.data.neighbors
        }));
        setSelectedKForPrediction(prev => ({
          ...prev,
          [pengukuranId]: kValue
        }));
      }
    } catch (err) {
      console.error('Error fetching neighbors:', err);
      alert('Gagal mengambil data tetangga terdekat');
    } finally {
      setLoadingNeighborsFor(null);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen bg-white">
        <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
        <div className="flex-1 flex flex-col">
          <header className="bg-white border-b border-gray-200">
            <div className="flex items-center justify-between px-6 py-4">
              <h1 className="text-2xl font-bold">Evaluasi Model</h1>
            </div>
          </header>
          <main className="flex-1 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-2 border-blue-600 border-t-transparent"></div>
          </main>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen bg-white">
        <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
        <div className="flex-1 flex flex-col">
          <header className="bg-white border-b border-gray-200">
            <div className="flex items-center justify-between px-6 py-4">
              <h1 className="text-2xl font-bold">Evaluasi Model</h1>
            </div>
          </header>
          <main className="flex-1 flex items-center justify-center p-6">
            <div className="bg-red-50 border border-red-200 rounded p-6 max-w-sm">
              <p className="text-red-800 mb-4">{error}</p>
              <button onClick={() => fetchAllData()} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Coba Lagi
              </button>
            </div>
          </main>
        </div>
      </div>
    );
  }

  if (!evaluationData) return null;

  const binaryMetrics = evaluationData.binary_classification?.metrics || {};
  const multiclassMetrics = evaluationData.multiclass_classification?.metrics || {};
  const kComparison = evaluationData.k_comparison || [];

  // Calculate correct/wrong predictions
  const totalData = binaryMetrics.total || 0;
  const correctPredictions = (binaryMetrics.tp || 0) + (binaryMetrics.tn || 0);
  const wrongPredictions = (binaryMetrics.fp || 0) + (binaryMetrics.fn || 0);

  // Get 4x4 confusion matrix
  const confusionMatrix = multiclassMetrics.confusion_matrix || [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ];

  return (
    <div className="flex h-screen bg-white">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white border-b border-gray-200">
          <div className="flex items-center justify-between px-6 py-4">
            <button onClick={() => setIsSidebarOpen(true)} className="lg:hidden">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-2xl font-bold">Evaluasi Model KNN</h1>
            <div className="text-right">
              <p className="text-sm font-medium">{user?.nama}</p>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6 bg-white">
          <div className="max-w-7xl mx-auto space-y-6">
            
            {/* ===== MONTH FILTER ===== */}
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
            
            {/* ===== TABS ===== */}
            <div className="flex border-b border-gray-200 mb-4 gap-2">
              <button
                onClick={() => setActiveTab('ringkasan')}
                className={`px-6 py-3 font-semibold border-b-2 transition-colors text-lg ${
                  activeTab === 'ringkasan'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Ringkasan Performa
              </button>
              <button
                onClick={() => setActiveTab('riwayat')}
                className={`px-6 py-3 font-semibold border-b-2 transition-colors text-lg ${
                  activeTab === 'riwayat'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Riwayat Prediksi
              </button>
            </div>

            {/* ===== TAB 1: RINGKASAN PERFORMA ===== */}
            {activeTab === 'ringkasan' && (
            <section>
              <div className="mb-6 space-y-6">
              
              {/* Row 1: Main Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-4">
                <div className="bg-white rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm font-medium">Total Sampel</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {totalData}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">Data Kader</p>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow p-6">
                  <p className="text-gray-700 text-sm font-medium">Accuracy</p>
                  <p className="text-3xl font-bold text-blue-600 mt-2">
                    {((binaryMetrics.accuracy || 0) * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow p-6">
                  <p className="text-gray-700 text-sm font-medium">Precision</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">
                    {((binaryMetrics.precision || 0) * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg shadow p-6">
                  <p className="text-gray-700 text-sm font-medium">Recall</p>
                  <p className="text-3xl font-bold text-orange-600 mt-2">
                    {((binaryMetrics.recall || 0) * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg shadow p-6">
                  <p className="text-gray-700 text-sm font-medium">Specificity</p>
                  <p className="text-3xl font-bold text-purple-600 mt-2">
                    {((binaryMetrics.specificity || 0) * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg shadow p-6">
                  <p className="text-gray-700 text-sm font-medium">F1 Score</p>
                  <p className="text-3xl font-bold text-red-600 mt-2">
                    {((binaryMetrics.f1_score || 0) * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              {/* Row 2: Confusion Matrix Values */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-white border border-gray-200 rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm font-medium">TP</p>
                  <p className="text-4xl font-bold text-green-600 mt-3">
                    {binaryMetrics.tp || 0}
                  </p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm font-medium">TN</p>
                  <p className="text-4xl font-bold text-blue-600 mt-3">
                    {binaryMetrics.tn || 0}
                  </p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm font-medium">FP</p>
                  <p className="text-4xl font-bold text-orange-600 mt-3">
                    {binaryMetrics.fp || 0}
                  </p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm font-medium">FN</p>
                  <p className="text-4xl font-bold text-red-600 mt-3">
                    {binaryMetrics.fn || 0}
                  </p>
                </div>
              </div>




            </div>
            </section>
            )}

            {/* ===== TAB 2: RIWAYAT PREDIKSI ===== */}
            {activeTab === 'riwayat' && (
            <section>
              {/* Search Filter */}
              <div className="mb-4">
                <input
                  type="text"
                  placeholder="🔍 Cari nama balita..."
                  value={searchNamaBalita}
                  onChange={(e) => setSearchNamaBalita(e.target.value.toLowerCase())}
                  className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                />
              </div>
              
              <div className="bg-white border border-gray-200 rounded overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left font-bold">Nama Balita</th>
                      <th className="px-4 py-3 text-left font-bold">Status Aktual</th>
                      <th className="px-4 py-3 text-left font-bold">Status Prediksi</th>
                      <th className="px-4 py-3 text-center font-bold">Z-Score TB</th>
                      <th className="px-4 py-3 text-center font-bold">Z-Score BB</th>
                      <th className="px-4 py-3 text-center font-bold">Hasil</th>
                      <th className="px-4 py-3 text-left font-bold">Tanggal</th>
                      <th className="px-4 py-3 text-center font-bold">Tetangga</th>
                    </tr>
                  </thead>
                  <tbody>
                    {predictionHistory.length > 0 ? (
                      predictionHistory.filter(pred => 
                        searchNamaBalita === '' || 
                        (pred.nama_balita && pred.nama_balita.toLowerCase().includes(searchNamaBalita))
                      ).map((pred, idx) => (
                        <React.Fragment key={idx}>
                          <tr className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium">{pred.nama_balita}</td>
                            <td className="px-4 py-3 text-gray-700 text-xs">{pred.actual_status}</td>
                            <td className="px-4 py-3 text-gray-700 text-xs">{pred.predicted_status}</td>
                            <td className="px-4 py-3 text-center text-gray-600">
                              <span className={pred.zscore_tbu < -2.0 ? "font-bold text-orange-600" : ""}>{pred.zscore_tbu}</span>
                            </td>
                            <td className="px-4 py-3 text-center text-gray-600">
                              <span className={pred.zscore_bbu < -1.0 ? "font-bold text-orange-600" : ""}>{pred.zscore_bbu}</span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              {pred.is_correct ? (
                                <span className="text-green-600 font-bold">Benar</span>
                              ) : (
                                <span className="text-red-600 font-bold">Salah</span>
                              )}
                            </td>
                            <td className="px-4 py-3 text-gray-600">{pred.tanggal ? new Date(pred.tanggal).toLocaleDateString('id-ID') : '-'}</td>
                            <td className="px-4 py-3 text-center">
                              <button
                                onClick={() => setExpandedNeighbors(expandedNeighbors === idx ? null : idx)}
                                className="px-3 py-1 bg-blue-100 text-blue-600 rounded text-xs font-semibold hover:bg-blue-200"
                              >
                                {pred.nearest_neighbors ? `${pred.nearest_neighbors.length}` : '0'}
                              </button>
                            </td>
                          </tr>
                          
                          {/* Expanded neighbor rows */}
                          {expandedNeighbors === idx && pred.nearest_neighbors && pred.nearest_neighbors.length > 0 && (
                            <tr className="bg-blue-50 border-b border-gray-100">
                              <td colSpan="8" className="px-4 py-4">
                                <div className="bg-white border border-blue-200 rounded p-4">
                                  <div className="flex items-center justify-between mb-3">
                                    <h4 className="font-bold text-blue-700">Tetangga Terdekat (Database: K=10)</h4>
                                    <div className="flex gap-2">
                                      {[3, 5, 7, 9, 10].map(k => (
                                        <button
                                          key={k}
                                          onClick={() => fetchNeighborsByK(pred.id, k)}
                                          disabled={loadingNeighborsFor === pred.id}
                                          className={`px-3 py-1 rounded font-semibold text-xs transition-colors ${
                                            selectedKForPrediction[pred.id] === k
                                              ? 'bg-blue-600 text-white'
                                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                          } ${loadingNeighborsFor === pred.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                                        >
                                          {loadingNeighborsFor === pred.id ? '...' : `K=${k}`}
                                        </button>
                                      ))}
                                    </div>
                                  </div>
                                  
                                  <table className="w-full text-xs border-collapse">
                                    <thead>
                                      <tr>
                                        <th className="border border-gray-200 p-2 bg-gray-100 text-center">No</th>
                                        <th className="border border-gray-200 p-2 bg-gray-100 text-center">Distance</th>
                                        <th className="border border-gray-200 p-2 bg-gray-100 text-center">JK</th>
                                        <th className="border border-gray-200 p-2 bg-gray-100 text-center">Usia (bln)</th>
                                        <th className="border border-gray-200 p-2 bg-gray-100 text-center">BB (kg)</th>
                                        <th className="border border-gray-200 p-2 bg-gray-100 text-center">TB (cm)</th>
                                        <th className="border border-gray-200 p-2 bg-gray-100 text-center">Z-BB</th>
                                        <th className="border border-gray-200 p-2 bg-gray-100 text-center">Z-TB</th>
                                        <th className="border border-gray-200 p-2 bg-gray-100 text-left">Status Stunting</th>
                                      </tr>
                                    </thead>
                                    <tbody>
                                      {(neighborsData[pred.id] || pred.nearest_neighbors).map((neighbor, nidx) => (
                                        <tr key={nidx} className="hover:bg-gray-50">
                                          <td className="border border-gray-200 p-2 text-center font-medium">{nidx + 1}</td>
                                          <td className="border border-gray-200 p-2 text-center font-bold text-blue-600">{neighbor.distance ?? '-'}</td>
                                          <td className="border border-gray-200 p-2 text-center">{neighbor.jenis_kelamin === 'L' ? 'Laki-laki' : 'Perempuan'}</td>
                                          <td className="border border-gray-200 p-2 text-center">{neighbor.usia_bulan || '-'}</td>
                                          <td className="border border-gray-200 p-2 text-center">{(neighbor.berat_badan || 0).toFixed(1)}</td>
                                          <td className="border border-gray-200 p-2 text-center">{(neighbor.tinggi_badan || 0).toFixed(1)}</td>
                                          <td className="border border-gray-200 p-2 text-center">{neighbor.z_score_bb ?? '-'}</td>
                                          <td className="border border-gray-200 p-2 text-center">{neighbor.z_score_tb ?? '-'}</td>
                                          <td className="border border-gray-200 p-2">
                                            <span className={`px-2 py-1 rounded font-semibold text-white whitespace-nowrap inline-block ${
                                              neighbor.label_code === 0 ? 'bg-green-600' :
                                              neighbor.label_code === 1 ? 'bg-yellow-500' :
                                              neighbor.label_code === 2 ? 'bg-orange-500' :
                                              neighbor.label_code === 3 ? 'bg-red-600' :
                                              'bg-gray-400'
                                            }`}>
                                              {CLASS_NAMES[neighbor.label_code] || CLASS_NAMES[neighbor.label] || 'Unknown'}
                                            </span>
                                          </td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="8" className="px-4 py-6 text-center text-gray-500">
                          Tidak ada data prediksi
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>


            </section>
            )}

            {/* Refresh Button */}
            <div className="flex justify-end">
              <button
                onClick={() => fetchAllData()}
                className="px-6 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700 transition-colors"
              >
                Refresh
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default EvaluasiModelPage;
