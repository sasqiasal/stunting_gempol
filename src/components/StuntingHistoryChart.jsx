/**
 * Grafik Riwayat Stunting Component
 * 
 * Menampilkan visualisasi tren kasus stunting dalam 6 bulan terakhir
 * - Admin: Data global dari seluruh Posyandu
 * - Kader: Data hanya dari Posyandu tempat kader bertugas
 * - Empty State: Jika tidak ada data, tampilkan alert
 */

import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const StuntingHistoryChart = ({ data, isLoading, error, userRole }) => {
  // Check if data is empty
  const isEmpty = !data || !data.data || data.data.length === 0 || data.total === 0;
  const hasNoStuntingCases = data && data.data && data.data.every(item => item.jumlah === 0);

  // Loading state
  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Gagal memuat data grafik</span>
          </div>
        </div>
      </div>
    );
  }

  // Empty state - No stunting cases in 6 months
  if (isEmpty || hasNoStuntingCases) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          📊 Grafik Riwayat Stunting
          <span className="text-sm font-normal text-gray-500">
            ({userRole === 'admin' ? 'Semua Posyandu' : 'Posyandu Saya'})
          </span>
        </h2>
        
        {/* Alert - No data */}
        <div className="bg-green-50 border-2 border-green-500 rounded-lg p-6 text-center">
          <div className="flex flex-col items-center gap-3">
            <div className="bg-green-100 rounded-full p-3">
              <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-lg sm:text-xl font-bold text-green-800 mb-2">
                🎉 Kabar Baik!
              </p>
              <p className="text-base sm:text-lg font-semibold text-green-700">
                Tidak ada riwayat balita terkena stunting pada periode ini
              </p>
              <p className="text-sm text-green-600 mt-2">
                {data?.periode || '6 bulan terakhir'}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Chart data available
  return (
    <div className="bg-white rounded-lg shadow p-4 sm:p-6">
      {/* Header */}
      <div className="mb-4 sm:mb-6">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 mb-2">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 flex items-center gap-2">
            📊 Grafik Riwayat Stunting
          </h2>
          <span className="text-xs sm:text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
            {userRole === 'admin' ? '🌐 Semua Posyandu' : '📍 Posyandu Saya'}
          </span>
        </div>
        <p className="text-xs sm:text-sm text-gray-600">
          Periode: <span className="font-semibold">{data.periode}</span>
          {' • '}
          Total Kasus: <span className="font-semibold text-red-600">{data.total}</span>
        </p>
      </div>

      {/* Chart - Mobile Responsive */}
      <div className="w-full" style={{ height: window.innerWidth < 640 ? '300px' : '400px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart 
            data={data.data}
            margin={{ top: 5, right: 10, left: -20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="bulan" 
              tick={{ fontSize: window.innerWidth < 640 ? 10 : 12 }}
              angle={window.innerWidth < 640 ? -45 : 0}
              textAnchor={window.innerWidth < 640 ? 'end' : 'middle'}
              height={window.innerWidth < 640 ? 80 : 60}
            />
            <YAxis 
              tick={{ fontSize: window.innerWidth < 640 ? 10 : 12 }}
              allowDecimals={false}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: window.innerWidth < 640 ? '12px' : '14px'
              }}
              labelStyle={{ fontWeight: 'bold', color: '#1f2937' }}
              formatter={(value) => [`${value} kasus`, 'Jumlah Stunting']}
            />
            <Legend 
              wrapperStyle={{ fontSize: window.innerWidth < 640 ? '12px' : '14px' }}
              iconType="rect"
            />
            <Bar 
              dataKey="jumlah" 
              name="Kasus Stunting"
              fill="#dc2626" 
              radius={[8, 8, 0, 0]}
              maxBarSize={60}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Line Chart Alternative (Optional - uncomment to use) */}
      {/* <div className="w-full mt-6" style={{ height: window.innerWidth < 640 ? '300px' : '400px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart 
            data={data.data}
            margin={{ top: 5, right: 10, left: -20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="bulan" 
              tick={{ fontSize: window.innerWidth < 640 ? 10 : 12 }}
              angle={window.innerWidth < 640 ? -45 : 0}
              textAnchor={window.innerWidth < 640 ? 'end' : 'middle'}
              height={window.innerWidth < 640 ? 80 : 60}
            />
            <YAxis 
              tick={{ fontSize: window.innerWidth < 640 ? 10 : 12 }}
              allowDecimals={false}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: window.innerWidth < 640 ? '12px' : '14px'
              }}
            />
            <Legend wrapperStyle={{ fontSize: window.innerWidth < 640 ? '12px' : '14px' }} />
            <Line 
              type="monotone" 
              dataKey="jumlah" 
              name="Kasus Stunting"
              stroke="#dc2626" 
              strokeWidth={3}
              dot={{ fill: '#dc2626', r: 5 }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div> */}

      {/* Summary Info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-3 sm:gap-4">
          <div className="bg-red-50 rounded-lg p-3 text-center">
            <p className="text-xs sm:text-sm text-red-600 font-medium">Total Kasus</p>
            <p className="text-2xl sm:text-3xl font-bold text-red-700">{data.total}</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <p className="text-xs sm:text-sm text-blue-600 font-medium">Rata-rata/Bulan</p>
            <p className="text-2xl sm:text-3xl font-bold text-blue-700">
              {(data.total / 6).toFixed(1)}
            </p>
          </div>
        </div>
      </div>

      {/* Info Footer */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          ℹ️ Data diperbarui secara real-time berdasarkan hasil pengukuran terbaru
        </p>
      </div>
    </div>
  );
};

export default StuntingHistoryChart;
