/**
 * Contoh Implementasi Export Laporan di Page Component
 * File: src/pages/LaporanPage.jsx
 */

import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import LaporanExportButton from '../components/LaporanExportButton';
import { getPengukuranList, getBalitaList, getPosyanduList } from '../services/laporanService';
import { useAuthStore } from '../store/authStore';

export const LaporanPage = () => {
  const { user } = useAuthStore();
  const [pengukuranData, setPengukuranData] = useState([]);
  const [balitaData, setBalitaData] = useState([]);
  const [posyanduList, setPosyanduList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch semua data yang diperlukan
        const [pengukuran, balita, posyandu] = await Promise.all([
          getPengukuranList(),
          getBalitaList(),
          getPosyanduList(),
        ]);

        setPengukuranData(pengukuran);
        setBalitaData(balita);
        setPosyanduList(posyandu);
      } catch (error) {
        console.error('Error fetching data:', error);
        toast.error('Gagal mengambil data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-gray-600">Memuat data...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Laporan Pengukuran</h1>
          <p className="text-gray-600 text-lg">Export laporan pengukuran balita berdasarkan periode</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <LaporanExportButton
            pengukuranData={pengukuranData}
            balitaData={balitaData}
            posyanduList={posyanduList}
            user={user}
          />
        </div>

        <div className="mt-12">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Penjelasan Jenis Laporan</h3>
          
        <div className="bg-white rounded-lg shadow p-6 mb-6 border-l-4 border-blue-500">
          <h4 className="text-xl font-bold text-gray-900 mb-3">Laporan Bulanan</h4>
          <p className="text-gray-700 mb-3">
            Menampilkan data pengukuran dari <strong>semua posyandu</strong> 
            untuk <strong>satu bulan tertentu</strong>.
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
            <li>File: <code className="bg-blue-50 px-2 py-1 rounded">Laporan_Pengukuran_[Bulan]_[Tahun].xlsx</code></li>
            <li>Sheet: 1 sheet bernama "Laporan Bulanan"</li>
            <li>Format tabel: No | Posyandu | Nama | NIK | JK | Data Pengukuran</li>
          </ul>
          <p className="bg-blue-50 p-4 rounded text-sm text-gray-700">
            Contoh: <code>Laporan_Pengukuran_Januari_2026.xlsx</code>
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6 border-l-4 border-green-500">
          <h4 className="text-xl font-bold text-gray-900 mb-3">Laporan H1 (September - Februari)</h4>
          <p className="text-gray-700 mb-3">
            Menampilkan <strong>riwayat pengukuran 6 bulan</strong>.
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
            <li>File: <code className="bg-green-50 px-2 py-1 rounded">Laporan_Pengukuran_H1_[Tahun].xlsx</code></li>
            <li>Data: Pengukuran dari September hingga Februari</li>
            <li>Format: Header bulan di-merge (September | Oktober | ... | Februari)</li>
            <li>Setiap bulan: Usia, TB, BB, Lingkar Lengan, Z-Score BB, Z-Score TB, Status Gizi</li>
          </ul>
          <p className="bg-green-50 p-4 rounded text-sm text-gray-700">
            Contoh: <code>Laporan_Pengukuran_H1_2026.xlsx</code>
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <h4 className="text-xl font-bold text-gray-900 mb-3">Laporan H2 (Maret - Agustus)</h4>
          <p className="text-gray-700 mb-3">
            Menampilkan <strong>riwayat pengukuran 6 bulan</strong>.
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-2 mb-4">
            <li>File: <code className="bg-purple-50 px-2 py-1 rounded">Laporan_Pengukuran_H2_[Tahun].xlsx</code></li>
            <li>Data: Pengukuran dari Maret hingga Agustus</li>
            <li>Format: Header bulan di-merge (Maret | April | ... | Agustus)</li>
            <li>Setiap bulan: Usia, TB, BB, Lingkar Lengan, Z-Score BB, Z-Score TB, Status Gizi</li>
          </ul>
          <p className="bg-purple-50 p-4 rounded text-sm text-gray-700">
            Contoh: <code>Laporan_Pengukuran_H2_2026.xlsx</code>
          </p>
        </div>
        </div>
      </div>
    </div>
  );
};

export default LaporanPage;
