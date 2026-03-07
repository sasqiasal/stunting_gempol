/**
 * Balita Page - Halaman Kelola Data Balita
 * - Admin: 2 Tabs (Data Pengukuran & Data Balita) - Read-only view
 * - Kader: Single View with Full CRUD
 * Mobile-First Responsive Design
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Select from "react-select";
import Sidebar from "../components/Sidebar";
import BalitaForm from "../components/BalitaForm";
import { balitaService } from "../services/balitaService";
import { pengukuranService } from "../services/pengukuranService";
import { posyanduService } from "../services/posyanduService";
import { useAuthStore } from "../store/authStore";
import { formatDate, getJenisKelaminLabel, getStatusBadge, censorChildName, censorParentName } from "../utils/helpers";
import { exportBalitaToExcel } from "../utils/excelExport";
import toast from "react-hot-toast";

const BalitaPage = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const isAdmin = user?.role === "admin";
  const isKader = user?.role === "kader";

  // Tab state (only for admin)
  const [activeTab, setActiveTab] = useState("pengukuran"); // 'pengukuran' or 'balita'

  // Data states
  const [balitaList, setBalitaList] = useState([]);
  const [pengukuranList, setPengukuranList] = useState([]);
  const [posyanduList, setPosyanduList] = useState([]);

  // Loading states
  const [loading, setLoading] = useState(true);
  const [loadingPengukuran, setLoadingPengukuran] = useState(false);

  // Filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("aktif");
  const [selectedPosyandu, setSelectedPosyandu] = useState(null);

  // UI states
  const [viewMode, setViewMode] = useState("table"); // 'table' or 'cards'
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showFormModal, setShowFormModal] = useState(false);
  const [showFullNames, setShowFullNames] = useState({}); // State untuk toggle nama per balita
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    loadBalita();
    if (isAdmin) {
      loadPosyandu();
      loadPengukuran();
    }
  }, [isAdmin]);

  // Reload data when posyandu filter changes
  useEffect(() => {
    if (isAdmin && activeTab === "pengukuran") {
      loadPengukuran();
    }
  }, [selectedPosyandu, isAdmin, activeTab]);

  const loadBalita = async () => {
    try {
      setLoading(true);
      const data = await balitaService.getAll({ limit: 500 });
      setBalitaList(data);
    } catch (error) {
      console.error("Error loading balita:", error);
      toast.error("Gagal memuat data balita");
    } finally {
      setLoading(false);
    }
  };

  const loadPengukuran = async () => {
    try {
      setLoadingPengukuran(true);
      const params = { limit: 500 };
      // Filter by posyandu if selected
      if (selectedPosyandu?.value) {
        params.posyandu_id = selectedPosyandu.value;
      }
      const data = await pengukuranService.getAll(params);
      setPengukuranList(data);
    } catch (error) {
      console.error("Error loading pengukuran:", error);
      toast.error("Gagal memuat data pengukuran");
    } finally {
      setLoadingPengukuran(false);
    }
  };

  const loadPosyandu = async () => {
    try {
      const data = await posyanduService.getAll();
      setPosyanduList(data);
    } catch (error) {
      console.error("Error loading posyandu:", error);
    }
  };

  const handleExport = async () => {
    try {
      toast.loading("Generating Excel...");
      if (activeTab === "pengukuran" && isAdmin) {
        // Export pengukuran data
        // TODO: Implement export pengukuran
        toast.dismiss();
        toast.success("Export pengukuran akan segera tersedia!");
      } else {
        await exportBalitaToExcel(filteredBalita);
        toast.dismiss();
        toast.success("Data berhasil diexport!");
      }
    } catch (error) {
      toast.dismiss();
      toast.error("Gagal export data");
    }
  };

  const handleFormSuccess = () => {
    setShowFormModal(false);
    loadBalita();
  };

  const toggleShowName = (balitaId) => {
    setShowFullNames((prev) => ({
      ...prev,
      [balitaId]: !prev[balitaId],
    }));
  };

  const handleStatusChange = async (balitaId, newStatus) => {
    try {
      await balitaService.update(balitaId, { status: newStatus });
      toast.success(`Status berhasil diubah menjadi ${newStatus}`);
      loadBalita();
    } catch (error) {
      toast.error("Gagal mengubah status");
    }
  };

  // Posyandu options for react-select
  const posyanduOptions = [{ value: null, label: "Semua Posyandu" }, ...posyanduList.map((p) => ({ value: p.id, label: p.nama }))];

  // Filter pengukuran data
  const filteredPengukuran = pengukuranList.filter((p) => {
    // Filter by posyandu
    if (selectedPosyandu?.value && p.posyandu_id !== selectedPosyandu.value) {
      return false;
    }

    // Filter by search (nama balita)
    if (searchTerm) {
      const balita = balitaList.find((b) => b.id === p.balita_id);
      const nama = balita?.nama_lengkap || "";
      if (!nama.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }
    }

    return true;
  });

  // Filter balita data
  const filteredBalita = balitaList
    .filter((balita) => {
      // Filter by posyandu
      if (selectedPosyandu?.value && balita.posyandu_id !== selectedPosyandu.value) {
        return false;
      }

      // Filter by search
      const search = searchTerm.toLowerCase();
      const matchesSearch = balita.nama_lengkap.toLowerCase().includes(search) || balita.nik.includes(search) || balita.nama_orang_tua.toLowerCase().includes(search);

      // Filter by status
      const matchesStatus = statusFilter === "semua" || (balita.status || "aktif") === statusFilter;

      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      if ((a.status || "aktif") === "aktif" && (b.status || "aktif") !== "aktif") return -1;
      if ((a.status || "aktif") !== "aktif" && (b.status || "aktif") === "aktif") return 1;
      return 0;
    });

  // Helper to get balita name by id
  const getBalitaName = (balitaId) => {
    const balita = balitaList.find((b) => b.id === balitaId);
    return balita?.nama_lengkap || "-";
  };

  // Helper to get posyandu name by id
  const getPosyanduName = (posyanduId) => {
    const posyandu = posyanduList.find((p) => p.id === posyanduId);
    return posyandu?.nama || "-";
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
            <h1 className="text-lg font-bold text-gray-900">{isAdmin ? (activeTab === "pengukuran" ? "Data Pengukuran" : "Data Balita") : "Data Balita"}</h1>
            <div className="flex gap-2">
              {isKader && (
                <button onClick={() => setShowFormModal(true)} className="p-2 rounded-md text-blue-700 hover:bg-blue-50">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </button>
              )}
              <button onClick={handleExport} className="p-2 rounded-md text-gray-700 hover:bg-gray-100">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
            {/* Header Desktop */}
            <div className="hidden lg:flex justify-between items-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900">{isAdmin ? (activeTab === "pengukuran" ? "Data Pengukuran" : "Data Balita") : "Data Balita"}</h1>
              <div className="flex gap-3">
                {isKader && (
                  <button onClick={() => setShowFormModal(true)} className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Tambah Balita
                  </button>
                )}
                <button onClick={handleExport} className="px-4 py-2 bg-success-600 text-white text-sm rounded-md hover:bg-success-700">
                  Export Excel
                </button>
              </div>
            </div>

            {/* Tabs for Admin - Data Pengukuran & Data Balita */}
            {isAdmin && (
              <div className="border-b border-gray-200 mb-6">
                <nav className="-mb-px flex space-x-8">
                  <button
                    onClick={() => setActiveTab("pengukuran")}
                    className={`${
                      activeTab === "pengukuran" ? "border-blue-500 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
                  >
                    Data Pengukuran
                  </button>
                  <button
                    onClick={() => setActiveTab("balita")}
                    className={`${
                      activeTab === "balita" ? "border-blue-500 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors`}
                  >
                    Data Balita
                  </button>
                </nav>
              </div>
            )}

            {/* Search & Filters */}
            <div className="mb-4 sm:mb-6 space-y-3">
              {/* Search bar - full width */}
              <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
                <div className="relative flex-1 w-full">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z" />
                    </svg>
                  </div>
                  <input
                    type="text"
                    placeholder="Cari nama balita, NIK, atau nama orang tua..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 touch-manipulation"
                  />
                </div>

                <div className="flex flex-wrap gap-2 items-center w-full md:w-auto">
                  {/* Status Filter Buttons */}
                  <button onClick={() => setStatusFilter("semua")} className={`px-3 py-2 rounded text-sm font-medium transition-colors ${statusFilter === "semua" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300"}`}>
                    Semua
                  </button>
                  <button
                    onClick={() => setStatusFilter("aktif")}
                    className={`px-3 py-2 rounded text-sm font-medium transition-colors ${statusFilter === "aktif" ? "bg-green-500 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300"}`}
                  >
                    Aktif
                  </button>
                  <button
                    onClick={() => setStatusFilter("lulus")}
                    className={`px-3 py-2 rounded text-sm font-medium transition-colors ${statusFilter === "lulus" ? "bg-yellow-500 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300"}`}
                  >
                    Lulus
                  </button>
                  <button
                    onClick={() => setStatusFilter("pindah")}
                    className={`px-3 py-2 rounded text-sm font-medium transition-colors ${statusFilter === "pindah" ? "bg-red-500 text-white" : "bg-gray-200 text-gray-700 hover:bg-gray-300"}`}
                  >
                    Pindah
                  </button>

                  {/* Posyandu Dropdown - RIGHT SIDE */}
                  {isAdmin && (
                    <div className="ml-auto min-w-[200px]">
                      <Select
                        options={posyanduOptions}
                        value={selectedPosyandu}
                        onChange={setSelectedPosyandu}
                        isClearable
                        placeholder="Filter Posyandu..."
                        className="text-sm"
                        styles={{
                          control: (base) => ({
                            ...base,
                            minHeight: "38px",
                            borderRadius: "0.375rem",
                          }),
                        }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Summary - shown after filters, only for balita tab or kader */}
            {(activeTab === "balita" || isKader) && (
              <div className="mb-4 sm:mb-6 bg-white rounded-lg shadow p-4 sm:p-5">
                <h3 className="font-bold text-base sm:text-lg mb-3 sm:mb-4 flex items-center gap-2">
                  <svg className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Ringkasan
                </h3>
                <div className="grid grid-cols-3 gap-3 sm:gap-4">
                  <div className="bg-gray-50 p-3 sm:p-4 rounded-lg">
                    <p className="text-xs sm:text-sm text-gray-600 mb-1">Total Balita</p>
                    <p className="text-xl sm:text-2xl font-bold text-gray-900">{filteredBalita.length}</p>
                  </div>
                  <div className="bg-blue-50 p-3 sm:p-4 rounded-lg">
                    <p className="text-xs sm:text-sm text-gray-600 mb-1 flex items-center gap-1">
                      <svg className="h-4 w-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      Laki-laki
                    </p>
                    <p className="text-xl sm:text-2xl font-bold text-primary-600">{filteredBalita.filter((b) => b.jenis_kelamin === "L").length}</p>
                  </div>
                  <div className="bg-pink-50 p-3 sm:p-4 rounded-lg">
                    <p className="text-xs sm:text-sm text-gray-600 mb-1 flex items-center gap-1">
                      <svg className="h-4 w-4 text-pink-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      Perempuan
                    </p>
                    <p className="text-xl sm:text-2xl font-bold text-pink-600">{filteredBalita.filter((b) => b.jenis_kelamin === "P").length}</p>
                  </div>
                </div>
              </div>
            )}

            {/* View Mode Toggle - Mobile (only for balita tab or kader) */}
            {(activeTab === "balita" || isKader) && (
              <div className="sm:hidden flex gap-2 mb-4">
                <button onClick={() => setViewMode("cards")} className={`flex-1 px-4 py-2 rounded-md text-sm font-medium touch-manipulation ${viewMode === "cards" ? "bg-primary-600 text-white" : "bg-gray-200 text-gray-700"}`}>
                  Cards
                </button>
                <button onClick={() => setViewMode("table")} className={`flex-1 px-4 py-2 rounded-md text-sm font-medium touch-manipulation ${viewMode === "table" ? "bg-primary-600 text-white" : "bg-gray-200 text-gray-700"}`}>
                  Table
                </button>
              </div>
            )}

            {/* TAB CONTENT - DATA PENGUKURAN (Admin Only) */}
            {isAdmin && activeTab === "pengukuran" && (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">No</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tanggal</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nama Balita</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">TB (cm)</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">BB (kg)</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">LL (cm)</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">LK (cm)</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Z-Score BB/U</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Z-Score TB/U</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status Gizi</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prediksi</th>
                        <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {loadingPengukuran ? (
                        <tr>
                          <td colSpan="12" className="px-6 py-4 text-center text-gray-500 text-sm">
                            Loading...
                          </td>
                        </tr>
                      ) : filteredPengukuran.length === 0 ? (
                        <tr>
                          <td colSpan="12" className="px-6 py-4 text-center text-gray-500 text-sm">
                            Tidak ada data pengukuran
                          </td>
                        </tr>
                      ) : (
                        filteredPengukuran.map((pengukuran, index) => (
                          <tr key={pengukuran.id} className="hover:bg-gray-50">
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-900">{index + 1}</td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{formatDate(pengukuran.tanggal_pengukuran)}</td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-gray-900">
                              <div className="flex items-center gap-2">
                                <span>{showFullNames[pengukuran.balita_id] ? getBalitaName(pengukuran.balita_id) : censorChildName(getBalitaName(pengukuran.balita_id))}</span>
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
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{pengukuran.tinggi_badan}</td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{pengukuran.berat_badan}</td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{pengukuran.lingkar_lengan || "-"}</td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{pengukuran.lingkar_kepala || "-"}</td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm font-medium">
                              {pengukuran.zscore_bbu != null ? (
                                <span className={pengukuran.zscore_bbu < -2 ? "text-red-600" : pengukuran.zscore_bbu < -1 ? "text-yellow-600" : "text-green-600"}>{pengukuran.zscore_bbu.toFixed(2)}</span>
                              ) : (
                                <span className="text-gray-400">-</span>
                              )}
                            </td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm font-medium">
                              {pengukuran.zscore_tbu != null ? (
                                <span className={pengukuran.zscore_tbu < -2 ? "text-red-600 font-bold" : pengukuran.zscore_tbu < -1 ? "text-yellow-600" : "text-green-600"}>{pengukuran.zscore_tbu.toFixed(2)}</span>
                              ) : (
                                <span className="text-gray-400">-</span>
                              )}
                            </td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs">
                              {pengukuran.status_gizi ? <span className={getStatusBadge(pengukuran.status_gizi)}>{pengukuran.status_gizi}</span> : <span className="text-gray-400">-</span>}
                            </td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs">
                              {pengukuran.prediksi_stunting != null ? (
                                <span className={getStatusBadge(pengukuran.prediksi_stunting === true || pengukuran.prediksi_stunting === "Stunting" ? "STUNTING" : "NORMAL")}>
                                  {pengukuran.prediksi_stunting === true || pengukuran.prediksi_stunting === "Stunting" ? "Iya" : "Tidak"}
                                </span>
                              ) : (
                                <span className="text-gray-400">-</span>
                              )}
                            </td>
                            <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{pengukuran.confidence_score ? `${(pengukuran.confidence_score * 100).toFixed(1)}%` : "-"}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* TAB CONTENT - DATA BALITA (Admin) or Main Content (Kader) */}
            {(activeTab === "balita" || isKader) && (
              <>
                {/* Cards View (Mobile) */}
                {viewMode === "cards" && (
                  <div className="space-y-3">
                    {loading ? (
                      <div className="text-center py-8 text-gray-500">Loading...</div>
                    ) : filteredBalita.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">Tidak ada data</div>
                    ) : (
                      filteredBalita.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage).map((balita, index) => (
                        <div key={balita.id} className="bg-white rounded-lg shadow p-4 border-l-4 border-primary-500">
                          <div className="flex justify-between items-start mb-2">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <h3 className="font-bold text-base text-gray-900">{showFullNames[balita.id] ? balita.nama_lengkap : censorChildName(balita.nama_lengkap)}</h3>
                                <button onClick={() => toggleShowName(balita.id)} className="text-gray-500 hover:text-gray-700 focus:outline-none p-1" title={showFullNames[balita.id] ? "Sembunyikan nama" : "Tampilkan nama"}>
                                  {showFullNames[balita.id] ? (
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
                              <p className="text-xs text-gray-500 mt-1">NIK: {balita.nik}</p>
                            </div>
                            <span className="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-1 rounded">#{(currentPage - 1) * itemsPerPage + index + 1}</span>
                          </div>

                          <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                            <div>
                              <span className="text-gray-500">Jenis Kelamin:</span>
                              <p className="font-medium mt-1 flex items-center gap-1">
                                <svg className={`h-4 w-4 ${balita.jenis_kelamin === "L" ? "text-blue-500" : "text-pink-500"}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                                {balita.jenis_kelamin === "L" ? "Laki-laki" : "Perempuan"}
                              </p>
                            </div>
                            <div>
                              <span className="text-gray-500">Usia:</span>
                              <p className="font-medium mt-1">⏱️ {balita.usia_bulan} bulan</p>
                            </div>
                            <div>
                              <span className="text-gray-500">Lahir:</span>
                              <p className="font-medium mt-1">📅 {formatDate(balita.tanggal_lahir)}</p>
                            </div>
                            <div className="col-span-2">
                              <span className="text-gray-500">Orang Tua:</span>
                              <div className="flex items-center gap-2 mt-1">
                                <p className="font-medium truncate">👨‍👩‍👧 {showFullNames[balita.id] ? balita.nama_orang_tua : censorParentName(balita.nama_orang_tua)}</p>
                              </div>
                            </div>
                          </div>

                          <div className="mt-3 pt-3 border-t">
                            <span className="text-xs text-gray-500">Status Balita:</span>
                            {isKader ? (
                              <select value={balita.status || "aktif"} onChange={(e) => handleStatusChange(balita.id, e.target.value)} className="mt-1 w-full px-2 py-1 border rounded text-sm">
                                <option value="aktif">Aktif</option>
                                <option value="lulus">Lulus</option>
                                <option value="pindah">Pindah</option>
                              </select>
                            ) : (
                              <div className="mt-1">
                                <span
                                  className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                                    (balita.status || "aktif") === "aktif" ? "bg-green-100 text-green-800" : (balita.status || "aktif") === "lulus" ? "bg-yellow-100 text-yellow-800" : "bg-red-100 text-red-800"
                                  }`}
                                >
                                  {(balita.status || "aktif").charAt(0).toUpperCase() + (balita.status || "aktif").slice(1)}
                                </span>
                              </div>
                            )}
                          </div>

                          {balita.status_terkini && (
                            <div className="mt-3 pt-3 border-t">
                              <span className="text-xs text-gray-500">Status Terkini:</span>
                              <div className="mt-1">
                                <span className={getStatusBadge(balita.status_terkini) + " text-xs"}>{balita.status_terkini}</span>
                              </div>
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                )}

                {/* Table View (Desktop & Mobile Toggle) */}
                {viewMode === "table" && (
                  <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">No</th>
                            <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nama Balita</th>
                            <th className="hidden sm:table-cell px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">NIK</th>
                            <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">JK</th>
                            <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usia</th>
                            <th className="hidden md:table-cell px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Orang Tua</th>
                            <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status Balita</th>
                            <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status Stunting</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {loading ? (
                            <tr>
                              <td colSpan="8" className="px-6 py-4 text-center text-gray-500 text-sm">
                                Loading...
                              </td>
                            </tr>
                          ) : filteredBalita.length === 0 ? (
                            <tr>
                              <td colSpan="8" className="px-6 py-4 text-center text-gray-500 text-sm">
                                Tidak ada data
                              </td>
                            </tr>
                          ) : (
                            filteredBalita.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage).map((balita, index) => (
                              <tr key={balita.id} className="hover:bg-gray-50">
                                <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-900">{(currentPage - 1) * itemsPerPage + index + 1}</td>
                                <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm font-medium text-gray-900">
                                  <div className="flex items-center gap-2">
                                    <span>{showFullNames[balita.id] ? balita.nama_lengkap : censorChildName(balita.nama_lengkap)}</span>
                                    <button onClick={() => toggleShowName(balita.id)} className="text-gray-500 hover:text-gray-700 focus:outline-none p-1" title={showFullNames[balita.id] ? "Sembunyikan nama" : "Tampilkan nama"}>
                                      {showFullNames[balita.id] ? (
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
                                <td className="hidden sm:table-cell px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{balita.nik}</td>
                                <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{getJenisKelaminLabel(balita.jenis_kelamin)}</td>
                                <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">{balita.usia_bulan} bulan</td>
                                <td className="hidden md:table-cell px-6 py-4 whitespace-nowrap text-xs sm:text-sm text-gray-500">
                                  <div className="flex items-center gap-2">
                                    <span>{showFullNames[balita.id] ? balita.nama_orang_tua : censorParentName(balita.nama_orang_tua)}</span>
                                    <button onClick={() => toggleShowName(balita.id)} className="text-gray-500 hover:text-gray-700 focus:outline-none p-1" title={showFullNames[balita.id] ? "Sembunyikan nama" : "Tampilkan nama"}>
                                      {showFullNames[balita.id] ? (
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
                                <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs">
                                  {isKader ? (
                                    <select value={balita.status || "aktif"} onChange={(e) => handleStatusChange(balita.id, e.target.value)} className="px-2 py-1 border rounded text-sm">
                                      <option value="aktif">Aktif</option>
                                      <option value="lulus">Lulus</option>
                                      <option value="pindah">Pindah</option>
                                    </select>
                                  ) : (
                                    <span
                                      className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                                        (balita.status || "aktif") === "aktif" ? "bg-green-100 text-green-800" : (balita.status || "aktif") === "lulus" ? "bg-yellow-100 text-yellow-800" : "bg-red-100 text-red-800"
                                      }`}
                                    >
                                      {(balita.status || "aktif").charAt(0).toUpperCase() + (balita.status || "aktif").slice(1)}
                                    </span>
                                  )}
                                </td>
                                <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-xs">
                                  {balita.status_terkini ? (
                                    <span className={getStatusBadge(balita.status_terkini)}>
                                      {balita.status_terkini?.toLowerCase().includes("stunt") ? "Stunting" : "Tidak"}
                                    </span>
                                  ) : (
                                    <span className="text-gray-400 text-xs">-</span>
                                  )}
                                </td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Pagination */}
                {filteredBalita.length > itemsPerPage && (
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
                        onClick={() => setCurrentPage(Math.min(Math.ceil(filteredBalita.length / itemsPerPage), currentPage + 1))}
                        disabled={currentPage >= Math.ceil(filteredBalita.length / itemsPerPage)}
                        className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                      >
                        Next
                      </button>
                    </div>
                    <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm text-gray-700">
                          Menampilkan <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> sampai{" "}
                          <span className="font-medium">{Math.min(currentPage * itemsPerPage, filteredBalita.length)}</span> dari{" "}
                          <span className="font-medium">{filteredBalita.length}</span> hasil
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
                          {[...Array(Math.ceil(filteredBalita.length / itemsPerPage))].map((_, i) => (
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
                            onClick={() => setCurrentPage(Math.min(Math.ceil(filteredBalita.length / itemsPerPage), currentPage + 1))}
                            disabled={currentPage >= Math.ceil(filteredBalita.length / itemsPerPage)}
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

              </>
            )}
          </div>
        </main>
      </div>

      {/* Modal Form Tambah Balita - Only for Kader */}
      {isKader && showFormModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <BalitaForm onSuccess={handleFormSuccess} onCancel={() => setShowFormModal(false)} />
          </div>
        </div>
      )}
    </div>
  );
};

export default BalitaPage;
