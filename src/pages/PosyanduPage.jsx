/**
 * Posyandu Page - Halaman Kelola Posyandu (Admin Only)
 */

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { posyanduService } from "../services/posyanduService";
import apiClient from "../services/api";
import toast from "react-hot-toast";

const PosyanduPage = () => {
  const navigate = useNavigate();
  const [posyanduList, setPosyanduList] = useState([]);
  const [kaderList, setKaderList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedPosyandu, setSelectedPosyandu] = useState(null);
  const [editForm, setEditForm] = useState({
    nama: "",
    alamat: "",
    kelurahan: "",
    kecamatan: "",
    kader_penanggungjawab: "",
  });
  const [viewMode, setViewMode] = useState("cards"); // 'cards' or 'table'
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;

  // Get current month name in Indonesian
  const getCurrentMonthName = () => {
    const months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"];
    return months[new Date().getMonth()];
  };

  useEffect(() => {
    loadPosyandu();
    loadKader();
  }, []);

  const loadPosyandu = async () => {
    try {
      setLoading(true);
      const data = await posyanduService.getAll();
      setPosyanduList(data);
    } catch (error) {
      console.error("Error loading posyandu:", error);
      toast.error("Gagal memuat data posyandu");
    } finally {
      setLoading(false);
    }
  };

  const loadKader = async () => {
    try {
      const response = await apiClient.get("/akun/users");
      setKaderList(response.data.filter((user) => user.role === "kader"));
    } catch (error) {
      console.error("Error loading kader:", error);
    }
  };

  const handleEditClick = (posyandu) => {
    setSelectedPosyandu(posyandu);
    setEditForm({
      nama: posyandu.nama,
      alamat: posyandu.alamat,
      kelurahan: posyandu.kelurahan || "Gempol",
      kecamatan: posyandu.kecamatan || "Gempol",
      kader_penanggungjawab: posyandu.kader_penanggungjawab || "",
    });
    setShowEditModal(true);
  };

  const handleUpdatePosyandu = async (e) => {
    e.preventDefault();
    
    try {
      await posyanduService.update(selectedPosyandu.id, editForm);
      toast.success("Data posyandu berhasil diupdate");
      setShowEditModal(false);
      loadPosyandu();
    } catch (error) {
      console.error("Error updating posyandu:", error);
      toast.error("Gagal update data posyandu");
    }
  };

  const handleCloseModal = () => {
    setShowEditModal(false);
    setSelectedPosyandu(null);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center gap-4">
              <button onClick={() => setSidebarOpen(true)} className="lg:hidden p-2 rounded-md hover:bg-gray-100">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>

              <h1 className="text-2xl font-bold text-gray-900">Kelola Posyandu</h1>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* View Mode Toggle */}
            <div className="flex justify-end mb-4">
              <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1">
                <button
                  onClick={() => setViewMode("cards")}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    viewMode === "cards" ? "bg-primary-600 text-white" : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <svg className="w-5 h-5 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                  Cards
                </button>
                <button
                  onClick={() => setViewMode("table")}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    viewMode === "table" ? "bg-primary-600 text-white" : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  <svg className="w-5 h-5 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Tabel
                </button>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="spinner mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading...</p>
              </div>
            ) : posyanduList.length === 0 ? (
              <div className="text-center py-12 text-gray-500">Belum ada data posyandu</div>
            ) : viewMode === "table" ? (
              // Table View
              <>
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">No</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nama Posyandu</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lokasi</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ketua Kader</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nama Akun</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider text-center">Jumlah Balita</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aksi</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {posyanduList.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage).map((posyandu, index) => {
                          const kader = kaderList.find((k) => k.posyandu_id === posyandu.id);
                          return (
                            <tr key={posyandu.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{(currentPage - 1) * itemsPerPage + index + 1}</td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="font-medium text-gray-900">{posyandu.nama}</div>
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">{posyandu.alamat}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{posyandu.kader_penanggungjawab || "-"}</td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                {kader ? (
                                  <div>
                                    <div className="font-medium text-gray-900">{kader.nama_lengkap}</div>
                                    <div className="text-xs text-gray-500">{kader.email}</div>
                                  </div>
                                ) : (
                                  <span className="text-gray-400 italic">Belum ditugaskan</span>
                                )}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                                <span className="font-bold text-blue-600">{posyandu.jumlah_balita || 0}</span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <button
                                  onClick={() => handleEditClick(posyandu)}
                                  className="text-primary-600 hover:text-primary-900 font-medium"
                                >
                                  Kelola
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Pagination */}
                {posyanduList.length > itemsPerPage && (
                  <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 rounded-b-lg">
                    <div className="flex-1 flex justify-between sm:hidden">
                      <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setCurrentPage(Math.min(Math.ceil(posyanduList.length / itemsPerPage), currentPage + 1))}
                        disabled={currentPage >= Math.ceil(posyanduList.length / itemsPerPage)}
                        className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                      >
                        Next
                      </button>
                    </div>
                    <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm text-gray-700">
                          Menampilkan <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> sampai{" "}
                          <span className="font-medium">{Math.min(currentPage * itemsPerPage, posyanduList.length)}</span> dari{" "}
                          <span className="font-medium">{posyanduList.length}</span> hasil
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
                          {[...Array(Math.ceil(posyanduList.length / itemsPerPage))].map((_, i) => (
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
                            onClick={() => setCurrentPage(Math.min(Math.ceil(posyanduList.length / itemsPerPage), currentPage + 1))}
                            disabled={currentPage >= Math.ceil(posyanduList.length / itemsPerPage)}
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
            ) : (
              // Cards View
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {posyanduList.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage).map((posyandu) => {
                    // Find kader for this posyandu
                    const kader = kaderList.find((k) => k.posyandu_id === posyandu.id);

                  return (
                    <div key={posyandu.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h3 className="font-bold text-xl text-gray-900 mb-1">{posyandu.nama}</h3>
                          <p className="text-sm text-gray-600 flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            {posyandu.alamat}
                          </p>
                        </div>
                      </div>

                      <div className="space-y-2 mb-4">
                        <div className="flex justify-between items-center bg-blue-50 p-3 rounded-lg border border-blue-100">
                          <span className="text-sm text-blue-700 font-medium">Total Balita</span>
                          <span className="font-bold text-blue-900 text-xl">{posyandu.jumlah_balita || 0}</span>
                        </div>
                        <div className="flex justify-between items-center bg-red-50 p-3 rounded-lg border border-red-100">
                          <span className="text-sm text-red-700 font-medium">Kasus Stunting</span>
                          <span className="font-bold text-red-900 text-xl">{posyandu.jumlah_stunting || 0}</span>
                        </div>
                      </div>

                      {/* Kader Info Section */}
                      <div className="pt-3 border-t mb-4">
                        <p className="text-xs text-gray-500 mb-2">Ketua Kader / Nama Akun:</p>
                        {kader ? (
                          <div className="bg-green-50 rounded-lg p-3 border border-green-100">
                            <p className="font-semibold text-sm text-gray-900">{kader.nama_lengkap}</p>
                            <p className="text-xs text-gray-600 mt-1 flex items-center gap-1">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                              </svg>
                              {kader.email}
                            </p>
                          </div>
                        ) : (
                          <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                            <p className="text-xs text-gray-500 italic">Belum ada kader ditugaskan</p>
                          </div>
                        )}
                      </div>

                      {/* Button Kelola Unit */}
                      <button
                        onClick={() => handleEditClick(posyandu)}
                        className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        Kelola Unit
                      </button>
                    </div>
                  );
                })}
                </div>

                {/* Pagination untuk Cards */}
                {posyanduList.length > itemsPerPage && (
                  <div className="mt-6 bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 rounded-lg shadow">
                    <div className="flex-1 flex justify-between sm:hidden">
                      <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setCurrentPage(Math.min(Math.ceil(posyanduList.length / itemsPerPage), currentPage + 1))}
                        disabled={currentPage >= Math.ceil(posyanduList.length / itemsPerPage)}
                        className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                      >
                        Next
                      </button>
                    </div>
                    <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm text-gray-700">
                          Menampilkan <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> sampai{" "}
                          <span className="font-medium">{Math.min(currentPage * itemsPerPage, posyanduList.length)}</span> dari{" "}
                          <span className="font-medium">{posyanduList.length}</span> hasil
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
                          {[...Array(Math.ceil(posyanduList.length / itemsPerPage))].map((_, i) => (
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
                            onClick={() => setCurrentPage(Math.min(Math.ceil(posyanduList.length / itemsPerPage), currentPage + 1))}
                            disabled={currentPage >= Math.ceil(posyanduList.length / itemsPerPage)}
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

        {/* Modal Edit Posyandu */}
        {showEditModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-900">Kelola Unit Posyandu</h2>
                <button onClick={handleCloseModal} className="text-gray-400 hover:text-gray-600 transition-colors">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={handleUpdatePosyandu} className="p-6 space-y-6">
                {/* Nama Posyandu */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Nama Posyandu</label>
                  <input
                    type="text"
                    value={editForm.nama}
                    onChange={(e) => setEditForm({ ...editForm, nama: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* Lokasi/Alamat */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Lokasi / Alamat</label>
                  <input
                    type="text"
                    value={editForm.alamat}
                    onChange={(e) => setEditForm({ ...editForm, alamat: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Contoh: Gempol Joyo RW. 12"
                    required
                  />
                </div>

                {/* Kelurahan */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Kelurahan</label>
                  <input
                    type="text"
                    value={editForm.kelurahan}
                    onChange={(e) => setEditForm({ ...editForm, kelurahan: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                {/* Kecamatan */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Kecamatan</label>
                  <input
                    type="text"
                    value={editForm.kecamatan}
                    onChange={(e) => setEditForm({ ...editForm, kecamatan: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                {/* Ketua Kader */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Ketua Kader / Penanggung Jawab</label>
                  <input
                    type="text"
                    value={editForm.kader_penanggungjawab}
                    onChange={(e) => setEditForm({ ...editForm, kader_penanggungjawab: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Nama ketua kader"
                  />
                </div>

                {/* Info Akun Kader */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-blue-900 mb-2">Info Akun Kader Terdaftar:</p>
                  {kaderList.find((k) => k.posyandu_id === selectedPosyandu?.id) ? (
                    <div className="text-sm text-blue-800">
                      <p className="font-semibold">{kaderList.find((k) => k.posyandu_id === selectedPosyandu?.id)?.nama_lengkap}</p>
                      <p className="text-xs mt-1">{kaderList.find((k) => k.posyandu_id === selectedPosyandu?.id)?.email}</p>
                    </div>
                  ) : (
                    <p className="text-sm text-blue-700 italic">Belum ada akun kader yang ditugaskan ke posyandu ini</p>
                  )}
                </div>

                {/* Info Statistik */}
                <div className="grid grid-cols-2 gap-4 bg-gray-50 rounded-lg p-4">
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Total Balita</p>
                    <p className="text-2xl font-bold text-gray-900">{selectedPosyandu?.jumlah_balita || 0}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 mb-1">Kasus Stunting</p>
                    <p className="text-2xl font-bold text-red-600">{selectedPosyandu?.jumlah_stunting || 0}</p>
                  </div>
                </div>

                {/* Buttons */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="flex-1 px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
                  >
                    Batal
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium transition-colors"
                  >
                    Simpan Perubahan
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PosyanduPage;
