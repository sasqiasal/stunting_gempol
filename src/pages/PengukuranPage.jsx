/**
 * Pengukuran Page - Halaman List Data Pengukuran
 * Simple Table View Only - Responsive dengan Horizontal Scroll
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CreatableSelect from "react-select/creatable";
import Sidebar from "../components/Sidebar";
import PengukuranForm from "../components/PengukuranForm";
import { pengukuranService } from "../services/pengukuranService";
import { balitaService } from "../services/balitaService";
import { posyanduService } from "../services/posyanduService";
import { formatDate, formatDateTime, censorChildName } from "../utils/helpers";
import { useAuthStore } from "../store/authStore";
import toast from "react-hot-toast";

const PengukuranPage = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [pengukuranList, setPengukuranList] = useState([]);
  const [balitaList, setBalitaList] = useState([]);
  const [posyanduList, setPosyanduList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showFormModal, setShowFormModal] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [searchNamaBalita, setSearchNamaBalita] = useState(''); // Filter pencarian nama balita
  const [showFullNames, setShowFullNames] = useState({});
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [evaluasiDetail, setEvaluasiDetail] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingPengukuran, setEditingPengukuran] = useState(null);
  const [loadingUpdate, setLoadingUpdate] = useState(false);
  const [editForm, setEditForm] = useState({ tinggi_badan: "", berat_badan: "", lingkar_lengan: "", lingkar_kepala: "", catatan: "" });
  
  // State untuk Export Modal
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportPeriod, setExportPeriod] = useState('bulanan');
  const [exportSelectedMonth, setExportSelectedMonth] = useState(new Date().getMonth() + 1);
  const [exportLoading, setExportLoading] = useState(false);

  const getLast6MonthsOptions = () => {
    const months = [];
    const today = new Date();
    for (let i = 0; i < 6; i++) {
      const date = new Date(today.getFullYear(), today.getMonth() - i, 1);
      const monthName = date.toLocaleDateString("id-ID", { month: "long", year: "numeric" });
      const value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
      months.push({ value, label: monthName });
    }
    return months;
  };

  useEffect(() => {
    loadBalita();
    loadPengukuran();
  }, []);

  useEffect(() => {
    if (!loading) {
      loadPengukuran();
    }
  }, [selectedMonth]);

  const loadBalita = async () => {
    try {
      const data = await balitaService.getAll();
      setBalitaList(data);
      const posyandu = await posyanduService.getAll();
      setPosyanduList(posyandu);
    } catch (error) {
      console.error("Error loading balita:", error);
    }
  };

  const loadPengukuran = async () => {
    try {
      setLoading(true);
      const params = { limit: 500 };
      if (selectedMonth?.value) {
        params.bulan = selectedMonth.value;
      }
      const data = await pengukuranService.getAll(params);
      
      // Sort by created_at DESC (newest input first) atau tanggal_pengukuran + id
      const sortedData = data.sort((a, b) => {
        // Primary: tanggal_pengukuran DESC
        const dateA = new Date(a.tanggal_pengukuran);
        const dateB = new Date(b.tanggal_pengukuran);
        const dateCompare = dateB - dateA;
        
        if (dateCompare !== 0) return dateCompare;
        
        // Secondary: created_at DESC (jika tanggal sama, yang terbaru di atas)
        if (a.created_at && b.created_at) {
          return new Date(b.created_at) - new Date(a.created_at);
        }
        
        // Tertiary: id DESC (fallback jika created_at null)
        return b.id - a.id;
      });
      
      console.log("📊 Sorted data (first 3):", sortedData.slice(0, 3).map(d => ({ id: d.id, tanggal: d.tanggal_pengukuran, created: d.created_at, nama: d.balita_nama })));
      
      setPengukuranList(sortedData);
    } catch (error) {
      console.error("Error loading pengukuran:", error);
      toast.error("Gagal memuat data pengukuran");
    } finally {
      setLoading(false);
    }
  };

  const getNamaBalita = (balitaId) => {
    const balita = balitaList.find((b) => b.id === balitaId);
    return balita ? balita.nama_lengkap : "Unknown";
  };

  const toggleShowName = (balitaId) => {
    setShowFullNames((prev) => ({
      ...prev,
      [balitaId]: !prev[balitaId],
    }));
  };

  // Badge color berdasarkan status_gizi
  const getStatusGiziBadgeClass = (statusGizi) => {
    if (!statusGizi) return "px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800";
    
    const status = statusGizi.toLowerCase();
    
    if (status.includes("normal") && status.includes("baik")) {
      return "px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800";      // Normal + Baik - Green
    }
    
    if (status.includes("normal") && status.includes("kurang")) {
      return "px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800";    // Normal + Kurang - Yellow
    }
    
    if (status.includes("stunting") && status.includes("baik")) {
      return "px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800";    // Stunting + Baik - Orange
    }
    
    if (status.includes("stunting") && status.includes("kurang")) {
      return "px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800";          // Stunting + Kurang - Red
    }
    
    return "px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800";
  };

  const getStuntingBadgeClass = (prediksi) => {
    // Backward compatibility: prediksi bisa boolean atau string
    const isStunting = prediksi === true || prediksi === "Stunting" || prediksi === 1;
    if (isStunting) {
      return "px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800";
    }
    return "px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800";
  };

  const getStatusGiziBadge = (statusGizi) => {
    if (!statusGizi) return "px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800";

    const status = statusGizi.toLowerCase();

    if (status.includes("stunting") || status.includes("kurang")) {
      return "px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800";
    }

    if (status.includes("normal") && status.includes("baik")) {
      return "px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800";
    }

    return "px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800";
  };

  const handleEditOpen = (pengukuran) => {
    setEditingPengukuran(pengukuran);
    setEditForm({
      tinggi_badan: pengukuran.tinggi_badan ?? "",
      berat_badan: pengukuran.berat_badan ?? "",
      lingkar_lengan: pengukuran.lingkar_lengan ?? "",
      lingkar_kepala: pengukuran.lingkar_kepala ?? "",
      catatan: pengukuran.catatan ?? "",
    });
    setEditModalOpen(true);
  };

  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    if (!editingPengukuran) return;
    setLoadingUpdate(true);
    try {
      await pengukuranService.update(editingPengukuran.id, {
        tinggi_badan: parseFloat(editForm.tinggi_badan),
        berat_badan: parseFloat(editForm.berat_badan),
        lingkar_lengan: parseFloat(editForm.lingkar_lengan),
        lingkar_kepala: parseFloat(editForm.lingkar_kepala),
        catatan: editForm.catatan || null,
      });
      toast.success("Data pengukuran berhasil diupdate dan prediksi diperbarui!");
      setEditModalOpen(false);
      setEditingPengukuran(null);
      loadPengukuran();
    } catch (error) {
      console.error("Error updating pengukuran:", error);
      toast.error(error?.response?.data?.detail || "Gagal mengupdate data pengukuran");
    } finally {
      setLoadingUpdate(false);
    }
  };

  const handleShowDetail = async (id) => {
    setLoadingDetail(true);
    setDetailModalOpen(true);
    setEvaluasiDetail(null);
    try {
      const data = await pengukuranService.getDetailEvaluasi(id);
      setEvaluasiDetail(data);
    } catch (error) {
      console.error("Error loading detail evaluasi:", error);
      toast.error("Gagal memuat detail evaluasi");
    } finally {
      setLoadingDetail(false);
    }
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

      const data = await pengukuranService.getAll({ limit: 999999 });
      const balita = await balitaService.getAll({ limit: 999999 });
      const posyandu = await posyanduService.getAll();

      // Import fungsi export yang sesuai
      const { exportLaporanByPeriod } = await import('../utils/excelExport');

      await exportLaporanByPeriod(
        data,
        balita,
        posyandu,
        exportPeriod,
        exportSelectedMonth,
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

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar - Mobile */}
        <header className="lg:hidden bg-white shadow-sm sticky top-0 z-30">
          <div className="flex items-center justify-between px-4 py-3">
            <button onClick={() => setSidebarOpen(true)} className="p-2 rounded-md text-gray-700 hover:bg-gray-100">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h1 className="text-lg font-bold text-gray-900">Data Pengukuran</h1>
            <button onClick={() => setShowFormModal(true)} className="p-2 rounded-md text-blue-700 hover:bg-blue-50">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
            {/* Header Desktop */}
            <div className="hidden lg:flex justify-between items-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900">Data Pengukuran</h1>
              <div className="flex gap-3">
                <button onClick={() => setShowExportModal(true)} className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Export Laporan
                </button>
                <button onClick={() => setShowFormModal(true)} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Tambah Pengukuran
                </button>
              </div>
            </div>

            {/* Filter Controls - Top Right */}
            <div className="mb-6 grid grid-cols-12 gap-3">
              {/* Search Filter - Col 9 */}
              <div className="col-span-9">
                <label className="block text-xs font-medium text-gray-700 mb-1">Cari Nama</label>
                <input
                  type="text"
                  placeholder="Nama balita..."
                  value={searchNamaBalita}
                  onChange={(e) => setSearchNamaBalita(e.target.value.toLowerCase())}
                  className="w-full px-3 py-0 h-9 border border-gray-300 rounded-md text-xs focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                />
              </div>
              
              {/* Month Filter - Col 3 */}
              <div className="col-span-3">
                <label className="block text-xs font-medium text-gray-700 mb-1">Filter Bulan</label>
                <CreatableSelect
                  isClearable
                  options={getLast6MonthsOptions()}
                  value={selectedMonth}
                  onChange={setSelectedMonth}
                  placeholder="Pilih bulan"
                  className="text-xs"
                  styles={{
                    control: (base) => ({
                      ...base,
                      minHeight: "36px",
                      fontSize: "12px",
                    }),
                  }}
                />
              </div>
            </div>

            {/* Table View */}
            <div className="bg-white rounded-lg shadow-sm">
              <div className="overflow-x-auto">
                <table className="w-full min-w-[800px]">
                  <thead className="bg-gray-50 sticky top-0">
                    <tr>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">No</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tanggal</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nama Balita</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Usia Saat Diukur</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">TB (cm)</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">BB (kg)</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">LL (cm)</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">LK (cm)</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Z-Score BB/U</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Z-Score TB/U</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Klasifikasi Status Gizi</th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {loading ? (
                      <tr>
                        <td colSpan="12" className="px-4 py-8 text-center text-gray-500 text-sm">
                          Loading...
                        </td>
                      </tr>
                    ) : pengukuranList.length === 0 ? (
                      <tr>
                        <td colSpan="12" className="px-4 py-8 text-center text-gray-500 text-sm">
                          Tidak ada data pengukuran
                        </td>
                      </tr>
                    ) : (
                      pengukuranList
                        .filter(pengukuran => {
                          const namaBalita = getNamaBalita(pengukuran.balita_id).toLowerCase();
                          return searchNamaBalita === '' || namaBalita.includes(searchNamaBalita);
                        })
                        .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                        .map((pengukuran, index) => {
                          const nomor = (currentPage - 1) * itemsPerPage + index + 1;
                          return (
                        <tr key={pengukuran.id} className="hover:bg-gray-50 even:bg-gray-50/50">
                          <td className="px-4 py-3 text-center text-sm text-gray-900">{nomor}</td>
                          <td className="px-4 py-3 text-sm text-gray-900">{formatDate(pengukuran.tanggal_pengukuran)}</td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-gray-900">{showFullNames[pengukuran.balita_id] ? getNamaBalita(pengukuran.balita_id) : censorChildName(getNamaBalita(pengukuran.balita_id))}</span>
                              <button
                                onClick={() => toggleShowName(pengukuran.balita_id)}
                                className="text-gray-500 hover:text-gray-700 focus:outline-none p-1"
                                title={showFullNames[pengukuran.balita_id] ? "Sembunyikan nama" : "Tampilkan nama"}
                              >
                                {showFullNames[pengukuran.balita_id] ? (
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
                          </td>
                          <td className="px-4 py-3 text-center text-sm text-gray-900">{pengukuran.usia_bulan} bulan</td>
                          <td className="px-4 py-3 text-center text-sm text-gray-900">{pengukuran.tinggi_badan}</td>
                          <td className="px-4 py-3 text-center text-sm text-gray-900">{pengukuran.berat_badan}</td>
                          <td className="px-4 py-3 text-center text-sm text-gray-900">{pengukuran.lingkar_lengan || "-"}</td>
                          <td className="px-4 py-3 text-center text-sm text-gray-900">{pengukuran.lingkar_kepala}</td>
                          <td className="px-4 py-3 text-center text-sm">
                            {pengukuran.zscore_bbu != null ? (
                              <span className={pengukuran.zscore_bbu < -2 ? "text-red-600 font-bold" : pengukuran.zscore_bbu < -1 ? "text-yellow-600" : "text-green-600"}>{pengukuran.zscore_bbu.toFixed(2)}</span>
                            ) : (
                              "-"
                            )}
                          </td>
                          <td className="px-4 py-3 text-center text-sm">
                            {pengukuran.zscore_tbu != null ? (
                              <span className={pengukuran.zscore_tbu < -2 ? "text-red-600 font-bold" : pengukuran.zscore_tbu < -1 ? "text-yellow-600" : "text-green-600"}>{pengukuran.zscore_tbu.toFixed(2)}</span>
                            ) : (
                              "-"
                            )}
                          </td>
                          <td className="px-4 py-3">
                            {pengukuran.status_gizi ? (
                              <span className={getStatusGiziBadgeClass(pengukuran.status_gizi)}>
                                {pengukuran.status_gizi}
                              </span>
                            ) : (
                              "-"
                            )}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <button onClick={() => handleEditOpen(pengukuran)} className="text-orange-600 hover:text-orange-900 text-xs font-semibold border border-orange-500 px-2 py-1 rounded">
                              Update Data
                            </button>
                          </td>
                        </tr>
                        );
                        })
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            {pengukuranList.length > itemsPerPage && (
              <div className="mt-4 bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 rounded-lg shadow">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setCurrentPage(Math.min(Math.ceil(pengukuranList.length / itemsPerPage), currentPage + 1))}
                    disabled={currentPage >= Math.ceil(pengukuranList.length / itemsPerPage)}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Menampilkan <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> sampai{" "}
                      <span className="font-medium">{Math.min(currentPage * itemsPerPage, pengukuranList.length)}</span> dari{" "}
                      <span className="font-medium">{pengukuranList.length}</span> hasil
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                      <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        <span className="sr-only">Previous</span>
                        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </button>
                      {[...Array(Math.ceil(pengukuranList.length / itemsPerPage))].map((_, i) => (
                        <button
                          key={i}
                          onClick={() => setCurrentPage(i + 1)}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            currentPage === i + 1
                              ? "z-10 bg-primary-50 border-primary-500 text-primary-600"
                              : "bg-white border-gray-300 text-gray-500 hover:bg-gray-50"
                          }`}
                        >
                          {i + 1}
                        </button>
                      ))}
                      <button
                        onClick={() => setCurrentPage(Math.min(Math.ceil(pengukuranList.length / itemsPerPage), currentPage + 1))}
                        disabled={currentPage >= Math.ceil(pengukuranList.length / itemsPerPage)}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        <span className="sr-only">Next</span>
                        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}

            {/* Summary Info */}
            {!loading && pengukuranList.length > 0 && (
              <div className="mt-4 text-sm text-gray-600 text-center">
                Total: <span className="font-semibold">{pengukuranList.length}</span> data pengukuran
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Modal Edit Pengukuran */}
      {editModalOpen && editingPengukuran && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">Update Data Pengukuran</h2>
              <button onClick={() => setEditModalOpen(false)} className="text-gray-500 hover:text-gray-700">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <form onSubmit={handleUpdateSubmit} className="p-6 space-y-4">
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-sm text-orange-800">
                Setelah diupdate, z-score, klasifikasi, prediksi KNN, dan evaluasi akan dikalkulasi ulang secara otomatis.
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Berat Badan (kg)</label>
                  <input
                    type="number"
                    step="0.1"
                    inputMode="decimal"
                    required
                    value={editForm.berat_badan}
                    onChange={(e) => setEditForm((f) => ({ ...f, berat_badan: e.target.value }))}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tinggi Badan (cm)</label>
                  <input
                    type="number"
                    step="0.1"
                    inputMode="decimal"
                    required
                    value={editForm.tinggi_badan}
                    onChange={(e) => setEditForm((f) => ({ ...f, tinggi_badan: e.target.value }))}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Lingkar Lengan (cm)</label>
                  <input
                    type="number"
                    step="0.1"
                    inputMode="decimal"
                    required
                    value={editForm.lingkar_lengan}
                    onChange={(e) => setEditForm((f) => ({ ...f, lingkar_lengan: e.target.value }))}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Lingkar Kepala (cm)</label>
                  <input
                    type="number"
                    step="0.1"
                    inputMode="decimal"
                    required
                    value={editForm.lingkar_kepala}
                    onChange={(e) => setEditForm((f) => ({ ...f, lingkar_kepala: e.target.value }))}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Catatan (opsional)</label>
                <textarea
                  rows={3}
                  value={editForm.catatan}
                  onChange={(e) => setEditForm((f) => ({ ...f, catatan: e.target.value }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                  placeholder="Catatan tambahan..."
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setEditModalOpen(false)}
                  className="px-4 py-2 text-sm bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={loadingUpdate}
                  className="px-4 py-2 text-sm bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-60 flex items-center gap-2"
                >
                  {loadingUpdate && <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block"></span>}
                  {loadingUpdate ? "Menyimpan..." : "Simpan & Kalkulasi Ulang"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Detail Evaluasi */}
      {detailModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center z-10">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Analisis K Tetangga Terdekat (K-NN)
              </h2>
              <button onClick={() => setDetailModalOpen(false)} className="text-gray-500 hover:text-gray-700">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6">
              {loadingDetail ? (
                <div className="flex justify-center items-center h-48">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
                </div>
              ) : evaluasiDetail ? (
                <div>
                  {/* Info Header */}
                  <div className="bg-blue-50 p-4 rounded-lg mb-6 border border-blue-100">
                    <p className="text-sm text-blue-800 mb-1">
                      Algoritma KNN memprediksi berdasarkan <b>{evaluasiDetail.k_value || 5} data latih</b> yang paling mirip ("tetangga terdekat").
                    </p>
                    <p className="text-xs text-blue-600 mt-1">Jika mayoritas tetangga adalah "Stunting", maka hasil prediksi adalah "Stunting".</p>
                  </div>

                  {!evaluasiDetail.nearest_neighbors || evaluasiDetail.nearest_neighbors.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <p>Tidak ada data evaluasi detail tersimpan untuk pengukuran ini.</p>
                      <p className="text-xs mt-2">(Data mungkin dibuat sebelum fitur evaluasi aktif)</p>
                    </div>
                  ) : (
                    <div className="border rounded-lg overflow-hidden">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Jarak (Similarity)</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status (Label)</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data Latih (Mirip)</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {evaluasiDetail.nearest_neighbors.map((neighbor, idx) => (
                            <tr key={idx} className={idx === 0 ? "bg-blue-50/30" : ""}>
                              <td className="px-4 py-3 text-sm text-gray-500">#{idx + 1}</td>
                              <td className="px-4 py-3 text-sm font-mono text-gray-600">{neighbor.distance}</td>
                              <td className="px-4 py-3">
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${(neighbor.label || "").includes("Stunting") ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"}`}>{neighbor.label}</span>
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-500">
                                <div className="grid grid-cols-3 gap-x-4 gap-y-1 text-xs">
                                  <span>
                                    JK: <b>{neighbor.jenis_kelamin}</b>
                                  </span>
                                  <span>
                                    Usia: <b>{neighbor.usia_bulan} bln</b>
                                  </span>
                                  <span>
                                    TB: <b>{neighbor.tinggi_badan} cm</b>
                                  </span>
                                  <span>
                                    BB: <b>{neighbor.berat_badan} kg</b>
                                  </span>
                                  <span>
                                    Z-BB: <b>{neighbor.z_score_bb ?? '-'}</b>
                                  </span>
                                  <span>
                                    Z-TB: <b>{neighbor.z_score_tb ?? '-'}</b>
                                  </span>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  <div className="mt-4 text-xs text-gray-500 text-right">*Semakin kecil nilai jarak (mendekati 0), semakin mirip data balita dengan data latih ini.</div>
                </div>
              ) : (
                <div className="text-center py-8 text-red-500">Gagal memuat data atau data tidak ditemukan.</div>
              )}
            </div>
            <div className="bg-gray-50 px-6 py-4 flex justify-end">
              <button onClick={() => setDetailModalOpen(false)} className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300">
                Tutup
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal for Form */}
      {showFormModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-5xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
              <h2 className="text-xl font-bold">Input Data Pengukuran</h2>
              <button onClick={() => setShowFormModal(false)} className="text-gray-500 hover:text-gray-700">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6">
              <PengukuranForm
                onSuccess={() => {
                  setShowFormModal(false);
                  loadPengukuran();
                }}
              />
            </div>
          </div>
        </div>
      )}

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
                      value={exportSelectedMonth}
                      onChange={(e) => setExportSelectedMonth(parseInt(e.target.value))}
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
  );
};

export default PengukuranPage;
