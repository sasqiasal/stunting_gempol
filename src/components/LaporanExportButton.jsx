/**
 * Komponen Export Laporan Pengukuran
 * Menampilkan tombol untuk export laporan dengan berbagai periode
 */

import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { exportLaporanPengukuranByPeriod } from '../utils/excelExport';

export const LaporanExportButton = ({ 
  pengukuranData, 
  balitaData, 
  posyanduList, 
  user 
}) => {
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const currentYear = new Date().getFullYear();

  const monthNames = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
  ];

  const handleExport = async (period, month = null) => {
    setLoading(true);
    const toastId = toast.loading('Membuat laporan...');
    
    try {
      await exportLaporanPengukuranByPeriod(
        pengukuranData,
        balitaData,
        posyanduList,
        period,
        month,
        currentYear,
        user
      );
      
      let filename = '';
      if (period === 'bulanan') {
        filename = `Laporan_Pengukuran_${monthNames[month - 1]}_${currentYear}.xlsx`;
      } else {
        filename = `Laporan_Pengukuran_${period}_${currentYear}.xlsx`;
      }
      
      toast.success(`Laporan ${filename} berhasil dibuat!`, { id: toastId });
      setShowModal(false);
    } catch (error) {
      console.error('Export Error:', error);
      toast.error(error.message || 'Gagal membuat laporan', { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Tombol Utama */}
      <button
        onClick={() => setShowModal(true)}
        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        disabled={loading || !pengukuranData?.length}
      >
        Export Laporan
      </button>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Pilih Jenis Laporan</h2>
              <button 
                className="close-btn" 
                onClick={() => setShowModal(false)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              {/* Section Laporan Bulanan */}
              <div className="export-section">
                <h3>Laporan Bulanan</h3>
                <p className="section-desc">
                  Data pengukuran untuk bulan tertentu dari semua posyandu
                </p>
                <div className="button-grid">
                  {monthNames.map((month, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleExport('bulanan', idx + 1)}
                      disabled={loading}
                      className="month-btn"
                      title={`Export Laporan Bulanan ${month} ${currentYear}`}
                    >
                      {month.substring(0, 3)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Section Laporan Periode */}
              <div className="export-section">
                <h3>Laporan Periode</h3>
                <p className="section-desc">
                  Riwayat pengukuran 6 bulan per posyandu
                </p>
                <div className="period-buttons">
                  <button
                    onClick={() => handleExport('H1')}
                    disabled={loading}
                    className="period-btn"
                    title="Export Laporan H1 September-Februari"
                  >
                    <div className="period-label">H1</div>
                    <div className="period-desc">September - Februari</div>
                  </button>

                  <button
                    onClick={() => handleExport('H2')}
                    disabled={loading}
                    className="period-btn"
                    title="Export Laporan H2 Maret-Agustus"
                  >
                    <div className="period-label">H2</div>
                    <div className="period-desc">Maret - Agustus</div>
                  </button>
                </div>
              </div>

              {/* Info Box */}
              <div className="info-box">
                <h4>Informasi Laporan</h4>
                <ul>
                  <li><strong>Laporan Bulanan:</strong> Data seluruh posyandu untuk 1 bulan</li>
                  <li><strong>Laporan H1:</strong> Riwayat 6 bulan (Sep-Feb) per posyandu</li>
                  <li><strong>Laporan H2:</strong> Riwayat 6 bulan (Mar-Agu) per posyandu</li>
                  <li><strong>Format Data:</strong> Riwayat pengukuran diurutkan dari tanggal terlama</li>
                  {user?.role === 'kader' && (
                    <li><strong>✓ Anda hanya dapat mengekspor data posyandu Anda</strong></li>
                  )}
                </ul>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                onClick={() => setShowModal(false)}
                className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading}
              >
                Batal
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          background: white;
          border-radius: 8px;
          max-width: 600px;
          width: 90%;
          max-height: 90vh;
          overflow-y: auto;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid #e5e7eb;
        }

        .modal-header h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #1f2937;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #6b7280;
          padding: 0;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          transition: background 0.2s;
        }

        .close-btn:hover {
          background: #f3f4f6;
        }

        .modal-body {
          padding: 20px;
        }

        .export-section {
          margin-bottom: 30px;
        }

        .export-section h3 {
          margin: 0 0 8px 0;
          font-size: 1.1rem;
          color: #1f2937;
          font-weight: 600;
        }

        .section-desc {
          margin: 0 0 15px 0;
          font-size: 0.9rem;
          color: #6b7280;
        }

        .button-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
          gap: 10px;
        }

        .month-btn {
          padding: 10px;
          border: 2px solid #e5e7eb;
          border-radius: 6px;
          background: white;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.2s;
          color: #374151;
        }

        .month-btn:hover:not(:disabled) {
          border-color: #0284c7;
          background: #f0f9ff;
          color: #0284c7;
        }

        .month-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .period-buttons {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 15px;
        }

        .period-btn {
          padding: 20px;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          transition: all 0.2s;
          text-align: center;
        }

        .period-btn:hover:not(:disabled) {
          border-color: #10b981;
          background: #f0fdf4;
        }

        .period-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .period-label {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 8px;
        }

        .period-desc {
          font-size: 0.9rem;
          color: #6b7280;
        }

        .info-box {
          background: #f0f9ff;
          border-left: 4px solid #0284c7;
          padding: 15px;
          border-radius: 6px;
          margin-top: 20px;
        }

        .info-box h4 {
          margin: 0 0 10px 0;
          color: #1f2937;
          font-size: 1rem;
        }

        .info-box ul {
          margin: 0;
          padding-left: 20px;
          color: #4b5563;
          font-size: 0.9rem;
          line-height: 1.6;
        }

        .info-box li {
          margin-bottom: 6px;
        }

        .modal-footer {
          padding: 15px 20px;
          border-top: 1px solid #e5e7eb;
          background: #f9fafb;
          display: flex;
          justify-content: flex-end;
          gap: 10px;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #0284c7;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #0369a1;
        }

        .btn-secondary {
          background: #e5e7eb;
          color: #374151;
        }

        .btn-secondary:hover:not(:disabled) {
          background: #d1d5db;
        }

        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        @media (max-width: 600px) {
          .modal-content {
            width: 95%;
            max-height: 95vh;
          }

          .button-grid {
            grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
            gap: 8px;
          }

          .period-buttons {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </>
  );
};

export default LaporanExportButton;
