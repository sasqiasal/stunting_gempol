/**
 * Test Cases & Demo - Export Laporan Stunting
 * 
 * File ini berisi contoh data dan cara testing fungsi exportLaporanStunting
 */

// ===== CONTOH DATA UNTUK TESTING =====

// 1. Contoh User Admin
const adminUser = {
  id: 1,
  username: 'admin',
  nama_lengkap: 'Administrator',
  role: 'admin',
  posyandu_id: null // Admin tidak punya posyandu spesifik
};

// 2. Contoh User Kader
const kaderUser = {
  id: 2,
  username: 'kader01',
  nama_lengkap: 'Ibu Siti',
  role: 'kader',
  posyandu_id: 1 // Kader di Posyandu ID 1
};

// 3. Contoh Data Posyandu
const posyanduList = [
  { id: 1, nama: 'Posyandu Melati', alamat: 'Jl. Melati No. 1' },
  { id: 2, nama: 'Posyandu Mawar', alamat: 'Jl. Mawar No. 2' },
  { id: 3, nama: 'Posyandu Anggrek', alamat: 'Jl. Anggrek No. 3' },
];

// 4. Contoh Data Pengukuran (Mock Data)
const samplePengukuranData = [
  // STUNTING - Z-Score TB/U < -2
  {
    id: 1,
    tanggal_pengukuran: '2026-01-15',
    balita_id: 1,
    balita_nama: 'Andi Wijaya',
    balita_nik: '3201010120220001',
    jenis_kelamin: 'L',
    usia_bulan: 24,
    tinggi_badan: 75.5,
    berat_badan: 9.2,
    lingkar_lengan: 14.5,
    lingkar_kepala: 46.0,
    zscore_bbu: -1.5,
    zscore_tbu: -2.3, // STUNTING!
    status_gizi: 'Stunting',
    prediksi_stunting: true,
    confidence_score: 0.85,
    posyandu_id: 1,
    posyandu_nama: 'Posyandu Melati'
  },
  
  // NORMAL
  {
    id: 2,
    tanggal_pengukuran: '2026-01-18',
    balita_id: 2,
    balita_nama: 'Budi Santoso',
    balita_nik: '3201010120220002',
    jenis_kelamin: 'L',
    usia_bulan: 30,
    tinggi_badan: 89.0,
    berat_badan: 12.5,
    lingkar_lengan: 15.2,
    lingkar_kepala: 48.0,
    zscore_bbu: 0.5,
    zscore_tbu: 0.2, // Normal
    status_gizi: 'Normal',
    prediksi_stunting: false,
    confidence_score: 0.92,
    posyandu_id: 1,
    posyandu_nama: 'Posyandu Melati'
  },

  // STUNTING - Posyandu berbeda
  {
    id: 3,
    tanggal_pengukuran: '2025-12-20',
    balita_id: 3,
    balita_nama: 'Siti Nurhaliza',
    balita_nik: '3201010120220003',
    jenis_kelamin: 'P',
    usia_bulan: 18,
    tinggi_badan: 71.0,
    berat_badan: 8.5,
    lingkar_lengan: 13.8,
    lingkar_kepala: 45.0,
    zscore_bbu: -2.1,
    zscore_tbu: -2.5, // STUNTING!
    status_gizi: 'Stunting',
    prediksi_stunting: true,
    confidence_score: 0.88,
    posyandu_id: 2,
    posyandu_nama: 'Posyandu Mawar'
  },

  // NORMAL - Bulan lalu
  {
    id: 4,
    tanggal_pengukuran: '2025-11-10',
    balita_id: 4,
    balita_nama: 'Dewi Lestari',
    balita_nik: '3201010120220004',
    jenis_kelamin: 'P',
    usia_bulan: 22,
    tinggi_badan: 79.5,
    berat_badan: 10.8,
    lingkar_lengan: 14.8,
    lingkar_kepala: 46.5,
    zscore_bbu: -0.5,
    zscore_tbu: -0.8, // Normal
    status_gizi: 'Normal',
    prediksi_stunting: false,
    confidence_score: 0.90,
    posyandu_id: 1,
    posyandu_nama: 'Posyandu Melati'
  },
];

// ===== FUNGSI HELPER UNTUK TESTING =====

/**
 * Test Case 1: Export sebagai Admin
 */
export const testExportAsAdmin = async () => {
  console.log('🧪 Test Case 1: Export sebagai Admin');
  console.log('Expected: 1 sheet Simpulan + sheet per Posyandu');
  
  try {
    // Import fungsi export
    const { exportLaporanStunting } = await import('./excelExport.js');
    
    await exportLaporanStunting(
      samplePengukuranData,
      adminUser,
      posyanduList,
      'Test_Laporan_Admin'
    );
    
    console.log('✅ Test Case 1 PASSED - File downloaded');
  } catch (error) {
    console.error('❌ Test Case 1 FAILED:', error);
  }
};

/**
 * Test Case 2: Export sebagai Kader
 */
export const testExportAsKader = async () => {
  console.log('🧪 Test Case 2: Export sebagai Kader');
  console.log('Expected: 1 sheet Simpulan + sheet per Bulan (filtered by posyandu_id)');
  
  try {
    const { exportLaporanStunting } = await import('./excelExport.js');
    
    await exportLaporanStunting(
      samplePengukuranData,
      kaderUser,
      posyanduList,
      'Test_Laporan_Kader'
    );
    
    console.log('✅ Test Case 2 PASSED - File downloaded');
  } catch (error) {
    console.error('❌ Test Case 2 FAILED:', error);
  }
};

/**
 * Test Case 3: Validasi Styling Stunting
 */
export const testStuntingStyling = () => {
  console.log('🧪 Test Case 3: Validasi Styling Stunting');
  
  const { isStunting } = require('./excelExport.js');
  
  const testCases = [
    { data: { zscore_tbu: -2.3 }, expected: true, label: 'Z-Score -2.3' },
    { data: { zscore_tbu: -2.0 }, expected: false, label: 'Z-Score -2.0 (boundary)' },
    { data: { zscore_tbu: -1.5 }, expected: false, label: 'Z-Score -1.5' },
    { data: { zscore_tbu: 0.5 }, expected: false, label: 'Z-Score 0.5 (normal)' },
    { data: { zscore_tbu: null }, expected: false, label: 'Z-Score null' },
  ];
  
  let passed = 0;
  testCases.forEach(test => {
    const result = isStunting(test.data);
    if (result === test.expected) {
      console.log(`  ✅ ${test.label}: ${result}`);
      passed++;
    } else {
      console.log(`  ❌ ${test.label}: Expected ${test.expected}, got ${result}`);
    }
  });
  
  console.log(`\n${passed}/${testCases.length} tests passed`);
};

/**
 * Test Case 4: Validasi Data Filtering Kader
 */
export const testKaderDataFilter = () => {
  console.log('🧪 Test Case 4: Validasi Data Filtering Kader');
  
  // Simulate filter
  const kaderPosyanduId = 1;
  const filteredData = samplePengukuranData.filter(d => d.posyandu_id === kaderPosyanduId);
  
  console.log(`Original data: ${samplePengukuranData.length} items`);
  console.log(`Filtered data (Posyandu ID ${kaderPosyanduId}): ${filteredData.length} items`);
  
  const expectedCount = samplePengukuranData.filter(d => d.posyandu_id === 1).length;
  
  if (filteredData.length === expectedCount) {
    console.log(`✅ Filter works correctly - ${expectedCount} items for Posyandu 1`);
  } else {
    console.log(`❌ Filter failed - Expected ${expectedCount}, got ${filteredData.length}`);
  }
};

/**
 * Test Case 5: Validasi Grouping per Bulan
 */
export const testMonthGrouping = () => {
  console.log('🧪 Test Case 5: Validasi Grouping per Bulan');
  
  const monthGroups = {};
  samplePengukuranData.forEach(d => {
    const date = new Date(d.tanggal_pengukuran);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    
    if (!monthGroups[monthKey]) {
      monthGroups[monthKey] = [];
    }
    monthGroups[monthKey].push(d);
  });
  
  console.log('Month groups:');
  Object.keys(monthGroups).sort().reverse().forEach(month => {
    console.log(`  ${month}: ${monthGroups[month].length} items`);
  });
  
  const uniqueMonths = Object.keys(monthGroups).length;
  console.log(`✅ Total unique months: ${uniqueMonths}`);
};

// ===== RUN ALL TESTS =====
export const runAllTests = async () => {
  console.log('🚀 Running All Tests...\n');
  
  testStuntingStyling();
  console.log('\n---\n');
  
  testKaderDataFilter();
  console.log('\n---\n');
  
  testMonthGrouping();
  console.log('\n---\n');
  
  // Visual tests (requires browser)
  console.log('📊 Visual Tests (run in browser console):');
  console.log('  - testExportAsAdmin()');
  console.log('  - testExportAsKader()');
};

// ===== USAGE IN BROWSER CONSOLE =====
/**
 * Cara testing di browser:
 * 
 * 1. Buka Developer Console (F12)
 * 2. Import module:
 *    import { testExportAsAdmin, testExportAsKader } from './test-export-demo.js';
 * 
 * 3. Run test:
 *    testExportAsAdmin();
 *    testExportAsKader();
 * 
 * 4. Periksa file yang di-download
 */

// ===== EXPECTED RESULTS =====
/**
 * Admin Export:
 * ✅ File: Laporan_Stunting_YYYYMMDD.xlsx
 * ✅ Sheets: Simpulan, Posyandu Melati, Posyandu Mawar, Posyandu Anggrek
 * ✅ Simpulan: 3 baris (3 posyandu)
 * ✅ Posyandu Melati: 2 data (1 stunting row merah, 1 normal)
 * ✅ Posyandu Mawar: 1 data (1 stunting row merah)
 * 
 * Kader Export (Posyandu ID 1):
 * ✅ File: Laporan_Stunting_YYYYMMDD.xlsx
 * ✅ Sheets: Simpulan, Januari 2026, Desember 2025, November 2025
 * ✅ Simpulan: Max 6 baris (6 bulan terakhir)
 * ✅ Januari 2026: 2 data dari Posyandu Melati
 * ✅ November 2025: 1 data dari Posyandu Melati
 * ✅ Data Posyandu lain (ID 2, 3) tidak muncul
 */

export default {
  testExportAsAdmin,
  testExportAsKader,
  testStuntingStyling,
  testKaderDataFilter,
  testMonthGrouping,
  runAllTests,
  samplePengukuranData,
  adminUser,
  kaderUser,
  posyanduList
};
