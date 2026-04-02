/**
 * Dashboard Page dengan Peta GIS dan Statistik
 * Mobile-First Responsive Design
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { censorChildName } from "../utils/helpers";
import StuntingMap from "../components/StuntingMap";
import Sidebar from "../components/Sidebar";
import StuntingHistoryChart from "../components/StuntingHistoryChart";
import { pengukuranService } from "../services/pengukuranService";
import { posyanduService } from "../services/posyanduService";
import { balitaService } from "../services/balitaService";
import { exportPengukuranToExcel, exportStatistikPosyanduToExcel } from "../utils/excelExport";
import toast from "react-hot-toast";

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [statistik, setStatistik] = useState(null);
  const [recentPengukuran, setRecentPengukuran] = useState([]);
  const [allPengukuranForSebaranStatus, setAllPengukuranForSebaranStatus] = useState([]);
  const [balitaList, setBalitaList] = useState([]);
  const [showFullNames, setShowFullNames] = useState({});
  const [posyanduList, setPosyanduList] = useState([]);
  const [selectedPosyandu, setSelectedPosyandu] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // State untuk Grafik Riwayat Stunting
  const [chartData, setChartData] = useState(null);
  const [chartLoading, setChartLoading] = useState(true);
  const [chartError, setChartError] = useState(null);
  
  // State untuk Export Modal
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportPeriod, setExportPeriod] = useState('bulanan');
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [exportLoading, setExportLoading] = useState(false);
  
  // Pagination untuk data table admin
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;

  useEffect(() => {
    loadData();
    loadChartData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      // Get current month and previous month
      const today = new Date();
      const currentMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
      
      // Calculate previous month
      const prevDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      const previousMonth = `${prevDate.getFullYear()}-${String(prevDate.getMonth() + 1).padStart(2, '0')}`;

      // Load statistik
      const stats = await pengukuranService.getStatistik();
      setStatistik(stats);

      // Load recent pengukuran (tanpa filter bulan, ambil yang paling terbaru saja)
      const pengukuranLimit = user?.role === "admin" ? 500 : 10;
      const pengukuran = await pengukuranService.getAll({ 
        limit: pengukuranLimit
        // Tidak filter bulan - ambil pengukuran terbaru dari kapan saja
      });
      setRecentPengukuran(pengukuran);

      // Load ALL pengukuran (2 bulan: kemarin + terkini) untuk Sebaran Status Gizi
      const allPengukuran = await pengukuranService.getAll({ limit: 1000 });
      setAllPengukuranForSebaranStatus(allPengukuran);

      // Load posyandu
      const posyandu = await posyanduService.getAll();
      setPosyanduList(posyandu);

      // Load balita (untuk resume dashboard kader)
      const balita = await balitaService.getAll({ limit: 500 });
      setBalitaList(balita);
    } catch (error) {
      console.error("Error loading data:", error);
      toast.error("Gagal memuat data");
    } finally {
      setLoading(false);
    }
  };

  const loadChartData = async () => {
    try {
      setChartLoading(true);
      setChartError(null);
      const data = await pengukuranService.getRiwayatStunting();
      setChartData(data);
    } catch (error) {
      console.error("Error loading chart data:", error);
      setChartError(error.message || "Gagal memuat data grafik");
    } finally {
      setChartLoading(false);
    }
  };

  const toggleShowName = (balitaId) => {
    setShowFullNames((prev) => ({
      ...prev,
      [balitaId]: !prev[balitaId],
    }));
  };

  const handleExportWithPeriod = async () => {
    try {
      setExportLoading(true);
      const toastId = toast.loading('Generating laporan...');

      // Fetch fresh user data from backend for all kader users
      let userData = user;
      if (user?.role === "kader") {
        try {
          const token = localStorage.getItem("access_token");
          const response = await fetch("http://localhost:8000/api/v1/auth/me", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (response.ok) {
            const freshUser = await response.json();
            localStorage.setItem("user", JSON.stringify(freshUser));
            userData = freshUser;
          }
        } catch (err) {
          console.error("Fetch error:", err);
        }
      }

      // Reload data
      const posyandu = await posyanduService.getAll();
      const pengukuran = await pengukuranService.getAll({ limit: 500 });
      const balita = await balitaService.getAll({ limit: 500 });

      // Import fungsi export yang sesuai
      const { exportLaporanByPeriod } = await import('../utils/excelExport');
      
      await exportLaporanByPeriod(
        pengukuran,
        balita,
        posyandu,
        exportPeriod,
        selectedMonth,
        new Date().getFullYear(),
        userData
      );

      toast.dismiss();
      toast.success('Laporan berhasil diexport!');
      setShowExportModal(false);
    } catch (error) {
      console.error('Export error:', error);
      toast.dismiss();
      toast.error('Gagal export laporan: ' + (error.message || 'Unknown error'));
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportStatistikPosyandu = async () => {
    try {
      toast.loading("Generating statistik...");
      await exportStatistikPosyanduToExcel(posyanduList);
      toast.dismiss();
      toast.success("Statistik berhasil diexport!");
    } catch (error) {
      toast.dismiss();
      toast.error("Gagal export statistik");
    }
  };

  // Hitung statistik berdasarkan data pengukuran real-time (bukan balita list)
  const totalBalita = balitaList.length;
  
  // Total balita yang sudah diukur = unique balita dalam recentPengukuran
  const balitaSudahDiukur = new Set(recentPengukuran.map(p => p.balita_id)).size;
  const totalSudahDiukur = Math.min(balitaSudahDiukur, totalBalita);
  const totalBelumDiukur = Math.max(totalBalita - totalSudahDiukur, 0);

  // Sebaran status gizi: gunakan data bulan kemarin, kecuali ada pengukuran baru bulan terkini
  const getSebaranStatusGiziData = () => {
    const today = new Date();
    const currentMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    const currentMonthDate = new Date(today.getFullYear(), today.getMonth(), 1);
    
    // Check apakah ada pengukuran di bulan terkini
    const hasMeasurementThisMonth = allPengukuranForSebaranStatus.some(item => {
      const itemDate = new Date(item.tanggal_pengukuran);
      return itemDate.getFullYear() === today.getFullYear() && 
             itemDate.getMonth() === today.getMonth();
    });
    
    // Filter data berdasarkan apakah ada pengukuran bulan terkini
    let dataForSebaran = [];
    if (hasMeasurementThisMonth) {
      // Ada pengukuran bulan terkini → gunakan data bulan terkini
      dataForSebaran = recentPengukuran;
    } else {
      // Tidak ada pengukuran bulan terkini → gunakan data bulan kemarin
      dataForSebaran = allPengukuranForSebaranStatus.filter(item => {
        const itemDate = new Date(item.tanggal_pengukuran);
        return itemDate.getFullYear() === currentMonthDate.getFullYear() && 
               itemDate.getMonth() === currentMonthDate.getMonth() - 1;
      });
    }
    
    // Get latest measurement per balita
    const latestMeasurementPerBalita = dataForSebaran.reduce((acc, item) => {
      if (!acc[item.balita_id] || new Date(item.tanggal_pengukuran) > new Date(acc[item.balita_id].tanggal_pengukuran)) {
        acc[item.balita_id] = item;
      }
      return acc;
    }, {});

    return Object.values(latestMeasurementPerBalita).reduce(
      (acc, item) => {
        if (item.prediksi_stunting) {
          acc.stunting += 1;
        } else {
          acc.normal += 1;
        }
        return acc;
      },
      { normal: 0, stunting: 0 }
    );
  };

  const sebaranStatusGizi = getSebaranStatusGiziData();

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar - Mobile */}
        <header className="lg:hidden bg-white shadow-sm sticky top-0 z-30">
          <div className="flex items-center justify-between px-4 py-3">
            <button onClick={() => setSidebarOpen(true)} className="p-2 rounded-md text-gray-700 hover:bg-gray-100">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-lg font-bold text-gray-900">Dashboard Stunting</h1>
            <div className="w-10"></div> {/* Spacer for alignment */}
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          {user?.role === "kader" ? (
            <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
              <div className="bg-white rounded-lg shadow p-4 sm:p-6 mb-4 sm:mb-6">
                <p className="text-sm text-gray-600 mb-2">Resume Balita Posyandu</p>
                <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">{totalSudahDiukur} / {totalBalita}</h2>
                <p className="text-sm text-gray-500">Total sudah diukur / total balita keseluruhan</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                <div className="bg-white rounded-lg shadow p-4 sm:p-6">
                  <h2 className="text-base sm:text-lg font-bold mb-4">Data Pengukuran Terbaru</h2>

                  <div className="space-y-3 max-h-[500px] overflow-y-auto">
                    {recentPengukuran.length === 0 ? (
                      <p className="text-sm text-gray-500 text-center py-8">Belum ada data pengukuran</p>
                    ) : (
                      recentPengukuran.slice(0, 5).map((item) => (
                        <div key={item.id} className="border-b pb-3 last:border-0">
                          <div className="flex items-center gap-2">
                            <p className="font-medium text-sm">{showFullNames[item.balita_id] ? item.balita_nama : censorChildName(item.balita_nama)}</p>
                            <button onClick={() => toggleShowName(item.balita_id)} className="text-gray-500 hover:text-gray-700 focus:outline-none p-1" title={showFullNames[item.balita_id] ? "Sembunyikan nama" : "Tampilkan nama"}>
                              {showFullNames[item.balita_id] ? (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                              ) : (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                                  />
                                </svg>
                              )}
                            </button>
                          </div>
                          <p className="text-xs text-gray-600 mt-1">
                            {item.jenis_kelamin === "L" ? "Laki-laki" : "Perempuan"}, {item.usia_bulan} bulan
                          </p>
                          <div className="flex justify-between items-center mt-2 gap-2">
                            <span className={`text-xs px-2 py-1 rounded font-medium ${item.prediksi_stunting ? "bg-danger-100 text-danger-700" : "bg-success-100 text-success-700"}`}>{item.prediksi_stunting ? "STUNTING" : "NORMAL"}</span>
                            <span className="text-xs text-gray-500">{new Date(item.tanggal_pengukuran).toLocaleDateString("id-ID", { day: "2-digit", month: "short" })}</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="space-y-4 sm:space-y-6">
                  <div className="bg-white rounded-lg shadow p-4 sm:p-6">
                    <h2 className="text-base sm:text-lg font-bold mb-2">Perlu Diperhatikan</h2>
                    <p className="text-sm text-gray-600 mb-2">Total balita yang belum diukur</p>
                    <p className="text-3xl sm:text-4xl font-bold text-yellow-600">{totalBelumDiukur}</p>
                  </div>

                  <div className="bg-white rounded-lg shadow p-4 sm:p-6">
                    <h2 className="text-base sm:text-lg font-bold mb-4">Sebaran Status Gizi</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="rounded-lg bg-green-50 p-3">
                        <p className="text-sm text-gray-600">Normal</p>
                        <p className="text-2xl font-bold text-success-700">{sebaranStatusGizi.normal}</p>
                      </div>
                      <div className="rounded-lg bg-red-50 p-3">
                        <p className="text-sm text-gray-600">Stunting</p>
                        <p className="text-2xl font-bold text-danger-700">{sebaranStatusGizi.stunting}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
            {/* Statistik Cards - Mobile Optimized */}
            {statistik && (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 mb-4 sm:mb-8">
                <div className="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
                  <p className="text-xs sm:text-sm text-gray-600 mb-1">Total Pengukuran</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">{statistik.total_pengukuran}</p>
                </div>

                <div className="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
                  <p className="text-xs sm:text-sm text-gray-600 mb-1">Balita Stunting</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-danger-600">{statistik.total_stunting}</p>
                </div>

                <div className="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
                  <p className="text-xs sm:text-sm text-gray-600 mb-1">Balita Normal</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-success-600">{statistik.total_normal}</p>
                </div>

                <div className="bg-white rounded-lg shadow p-3 sm:p-4 lg:p-6">
                  <p className="text-xs sm:text-sm text-gray-600 mb-1">Persentase Stunting</p>
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-yellow-600">{statistik.persentase_stunting}%</p>
                </div>
              </div>
            )}

            {/* Map - Full Width GIS Focus */}
            <div className="bg-white rounded-lg shadow mb-4 sm:mb-8" style={{ height: window.innerWidth < 640 ? "400px" : "600px" }}>
              <div className="p-3 sm:p-4 border-b">
                <h2 className="text-base sm:text-lg font-bold">Peta Sebaran Stunting</h2>
              </div>
              <div style={{ height: window.innerWidth < 640 ? "calc(400px - 52px)" : "calc(600px - 60px)" }}>
                <StuntingMap onPosyanduSelect={setSelectedPosyandu} />
              </div>
            </div>

            {/* Data Analysis - Two Columns */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-4 sm:mb-8">
              {/* Recent Measurements */}
              <div className="bg-white rounded-lg shadow p-4 sm:p-6">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 gap-2">
                  <h2 className="text-base sm:text-lg font-bold">Pengukuran Terbaru</h2>
                  <button onClick={() => setShowExportModal(true)} className="text-xs sm:text-sm text-white bg-green-600 hover:bg-green-700 px-3 py-2 rounded-md touch-manipulation">
                    Export Laporan
                  </button>
                </div>

                <div className="space-y-3 max-h-[400px] overflow-y-auto">
                  {recentPengukuran.length === 0 ? (
                    <p className="text-sm text-gray-500 text-center py-8">Belum ada data pengukuran</p>
                  ) : (
                    recentPengukuran.slice(0, 5).map((item) => (
                      <div key={item.id} className="border-b pb-3 last:border-0">
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-sm">{showFullNames[item.balita_id] ? item.balita_nama : censorChildName(item.balita_nama)}</p>
                          <button onClick={() => toggleShowName(item.balita_id)} className="text-gray-500 hover:text-gray-700 focus:outline-none p-1" title={showFullNames[item.balita_id] ? "Sembunyikan nama" : "Tampilkan nama"}>
                            {showFullNames[item.balita_id] ? (
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                              </svg>
                            ) : (
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                                />
                              </svg>
                            )}
                          </button>
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          {item.jenis_kelamin === "L" ? "Laki-laki" : "Perempuan"}, {item.usia_bulan} bulan
                        </p>
                        <div className="flex justify-between items-center mt-2 gap-2">
                          <span className={`text-xs px-2 py-1 rounded font-medium ${item.prediksi_stunting ? "bg-danger-100 text-danger-700" : "bg-success-100 text-success-700"}`}>{item.prediksi_stunting ? "STUNTING" : "NORMAL"}</span>
                          <span className="text-xs text-gray-500">{new Date(item.tanggal_pengukuran).toLocaleDateString("id-ID", { day: "2-digit", month: "short" })}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Stunting History Chart */}
              <div>
                <StuntingHistoryChart data={chartData} isLoading={chartLoading} error={chartError} userRole={user?.role} />
              </div>
            </div>



            {/* Export Modal */}
            {showExportModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-lg">
                  <h2 className="text-xl font-bold mb-4">Export Laporan</h2>
                  
                  <div className="space-y-4">
                    {/* Bulanan */}
                    <div>
                      <label className="flex items-center mb-3">
                        <input
                          type="radio"
                          name="period"
                          value="bulanan"
                          checked={exportPeriod === 'bulanan'}
                          onChange={(e) => setExportPeriod(e.target.value)}
                          className="mr-3"
                        />
                        <span className="font-medium">Bulanan</span>
                      </label>
                      {exportPeriod === 'bulanan' && (
                        <div className="ml-6 mb-3">
                          <select
                            value={selectedMonth}
                            onChange={(e) => setSelectedMonth(parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                          >
                            {['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'].map((month, idx) => (
                              <option key={idx} value={idx + 1}>{month}</option>
                            ))}
                          </select>
                          <p className="text-xs text-gray-600 mt-1">Data semua posyandu untuk 1 bulan</p>
                        </div>
                      )}
                    </div>

                    {/* H1 */}
                    <div>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="period"
                          value="H1"
                          checked={exportPeriod === 'H1'}
                          onChange={(e) => setExportPeriod(e.target.value)}
                          className="mr-3"
                        />
                        <span className="font-medium">H1 (Sep - Feb)</span>
                      </label>
                      {exportPeriod === 'H1' && (
                        <p className="text-xs text-gray-600 ml-6 mt-1">Riwayat 6 bulan per posyandu</p>
                      )}
                    </div>

                    {/* H2 */}
                    <div>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          name="period"
                          value="H2"
                          checked={exportPeriod === 'H2'}
                          onChange={(e) => setExportPeriod(e.target.value)}
                          className="mr-3"
                        />
                        <span className="font-medium">H2 (Mar - Agu)</span>
                      </label>
                      {exportPeriod === 'H2' && (
                        <p className="text-xs text-gray-600 ml-6 mt-1">Riwayat 6 bulan per posyandu</p>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-3 mt-6">
                    <button
                      onClick={() => setShowExportModal(false)}
                      disabled={exportLoading}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                    >
                      Batal
                    </button>
                    <button
                      onClick={handleExportWithPeriod}
                      disabled={exportLoading}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 disabled:opacity-50"
                    >
                      {exportLoading ? 'Loading...' : 'Export'}
                    </button>
                  </div>
                </div>
              </div>
            )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;
