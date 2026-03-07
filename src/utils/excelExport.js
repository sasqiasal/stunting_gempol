/**
 * Export Excel Service
 * Service untuk generate laporan Excel menggunakan ExcelJS
 */

import ExcelJS from 'exceljs';
import { saveAs } from 'file-saver';
import { formatDate, formatNumber, getJenisKelaminLabel, censorChildName } from '../utils/helpers';

/**
 * Helper untuk menentukan apakah balita terindikasi stunting
 * @param {Object} data - Data pengukuran
 * @returns {boolean}
 */
const isStunting = (data) => {
  // Stunting jika Z-Score TB/U < -2
  return data.zscore_tbu && parseFloat(data.zscore_tbu) < -2;
};

/**
 * Helper untuk styling row stunting dengan warna merah
 * @param {Object} row - Excel row object
 */
const applyStuntingStyle = (row) => {
  row.eachCell({ includeEmpty: true }, (cell) => {
    cell.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFFF0000' }, // Merah
    };
    cell.font = {
      ...cell.font,
      color: { argb: 'FFFFFFFF' }, // Teks putih
      bold: true,
    };
  });
};

/**
 * Export data pengukuran ke Excel dengan sheet per Posyandu
 * @param {Array} data - Data pengukuran
 * @param {Array} posyanduList - Daftar posyandu
 * @param {Object} user - User object (role, posyandu_id)
 * @param {string} filename - Nama file (optional)
 */
export const exportPengukuranToExcel = async (data, posyanduList = [], user = null, filename = null) => {
  try {
    // Determine export scope based on user role
    const isKader = user && (user.role === 'kader' || user.role === 'Kader' || user.role === 'KADER');
    const kaderPosyanduId = user?.posyandu_id;
    
    // Find kader's posyandu name
    let kaderPosyandu = null;
    if (isKader && kaderPosyanduId) {
      kaderPosyandu = posyanduList.find(p => p.id === kaderPosyanduId);
      console.log('🔍 Kader Posyandu:', kaderPosyandu?.nama);
    }
    
    // Set filename based on role
    if (!filename) {
      if (isKader && kaderPosyandu) {
        filename = `Laporan_${kaderPosyandu.nama.replace(/\s+/g, '_')}`;
        console.log('✅ Kader filename:', filename);
      } else {
        filename = 'Laporan_Posyandu_Desa_Gempol';
        console.log('✅ Admin filename:', filename);
      }
    }
    
    // Filter data for kader (only their posyandu)
    const filteredData = isKader && kaderPosyanduId 
      ? data.filter(item => item.posyandu_id === kaderPosyanduId)
      : data;
    
    // Create workbook
    const workbook = new ExcelJS.Workbook();
    workbook.creator = 'Sistem Deteksi Dini Stunting';
    workbook.created = new Date();

    // Calculate summary statistics
    const totalData = filteredData.length;
    const totalStunting = filteredData.filter(d => d.prediksi_stunting === true || d.prediksi_stunting === 1).length;
    const totalNormal = totalData - totalStunting;
    const persentaseStunting = totalData > 0 ? ((totalStunting / totalData) * 100).toFixed(2) : 0;
    const persentaseNormal = totalData > 0 ? ((totalNormal / totalData) * 100).toFixed(2) : 0;

    // Add summary worksheet (first sheet)
    const summarySheet = workbook.addWorksheet('Ringkasan Data Stunting');
    
    // Title
    summarySheet.mergeCells('A1:D1');
    summarySheet.getCell('A1').value = 'RINGKASAN DATA STUNTING';
    summarySheet.getCell('A1').font = { bold: true, size: 16 };
    summarySheet.getCell('A1').alignment = { horizontal: 'center', vertical: 'middle' };
    summarySheet.getCell('A1').fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF0284C7' },
    };
    summarySheet.getCell('A1').font = { ...summarySheet.getCell('A1').font, color: { argb: 'FFFFFFFF' } };
    summarySheet.getRow(1).height = 30;

    // Date range
    summarySheet.getCell('A2').value = 'Tanggal Cetak:';
    summarySheet.getCell('B2').value = new Date().toLocaleDateString('id-ID', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
    summarySheet.getRow(2).font = { italic: true };
    
    // Empty row
    summarySheet.getRow(3).height = 5;

    // Statistics section
    summarySheet.getCell('A4').value = 'STATISTIK KESELURUHAN';
    summarySheet.getCell('A4').font = { bold: true, size: 14 };
    summarySheet.getCell('A4').fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FFE5E7EB' },
    };
    summarySheet.mergeCells('A4:D4');
    summarySheet.getRow(4).height = 25;

    // Data rows
    const statsData = [
      { label: 'Total Balita (Pengukuran)', value: totalData, color: 'FF3B82F6' },
      { label: 'Balita Stunting', value: totalStunting, color: 'FFEF4444' },
      { label: 'Balita Normal', value: totalNormal, color: 'FF10B981' },
      { label: 'Persentase Stunting', value: `${persentaseStunting}%`, color: 'FFF59E0B' },
      { label: 'Persentase Normal', value: `${persentaseNormal}%`, color: 'FF10B981' },
    ];

    let currentRow = 5;
    statsData.forEach((stat) => {
      summarySheet.getCell(`A${currentRow}`).value = stat.label;
      summarySheet.getCell(`A${currentRow}`).font = { bold: true };
      summarySheet.getCell(`C${currentRow}`).value = stat.value;
      summarySheet.getCell(`C${currentRow}`).font = { bold: true, size: 14 };
      summarySheet.getCell(`C${currentRow}`).fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: stat.color },
      };
      summarySheet.getCell(`C${currentRow}`).font = { 
        ...summarySheet.getCell(`C${currentRow}`).font, 
        color: { argb: 'FFFFFFFF' } 
      };
      summarySheet.getCell(`C${currentRow}`).alignment = { horizontal: 'center', vertical: 'middle' };
      summarySheet.getRow(currentRow).height = 25;
      currentRow++;
    });

    // Set column widths for summary sheet
    summarySheet.getColumn(1).width = 30;
    summarySheet.getColumn(2).width = 5;
    summarySheet.getColumn(3).width = 20;
    summarySheet.getColumn(4).width = 20;

    // Add border to all cells with content
    for (let i = 1; i <= currentRow - 1; i++) {
      ['A', 'B', 'C', 'D'].forEach(col => {
        const cell = summarySheet.getCell(`${col}${i}`);
        if (cell.value !== null && cell.value !== undefined) {
          cell.border = {
            top: { style: 'thin' },
            left: { style: 'thin' },
            bottom: { style: 'thin' },
            right: { style: 'thin' },
          };
        }
      });
    }

    // Add additional info
    summarySheet.getCell(`A${currentRow + 2}`).value = 'Keterangan:';
    summarySheet.getCell(`A${currentRow + 2}`).font = { bold: true };
    summarySheet.getCell(`A${currentRow + 3}`).value = '• Data berdasarkan pengukuran yang tercatat dalam sistem';
    summarySheet.getCell(`A${currentRow + 4}`).value = '• Balita dikategorikan stunting jika Z-Score TB/U < -2';
    summarySheet.getCell(`A${currentRow + 5}`).value = '• Detail lengkap tersedia pada sheet per posyandu';
    
    for (let i = currentRow + 3; i <= currentRow + 5; i++) {
      summarySheet.getCell(`A${i}`).font = { italic: true, size: 10 };
    }

    // Create helper function for adding posyandu sheet
    const addPosyanduSheet = (sheetName, posyanduData) => {
      const worksheet = workbook.addWorksheet(sheetName);

      // Set column widths
      worksheet.columns = [
        { header: 'No', key: 'no', width: 5 },
        { header: 'Tanggal', key: 'tanggal', width: 12 },
        { header: 'Nama Balita', key: 'nama', width: 25 },
        { header: 'NIK', key: 'nik', width: 18 },
        { header: 'Jenis Kelamin', key: 'jk', width: 15 },
        { header: 'Usia (bulan)', key: 'usia', width: 12 },
        { header: 'TB (cm)', key: 'tb', width: 10 },
        { header: 'BB (kg)', key: 'bb', width: 10 },
        { header: 'Lingkar Lengan (cm)', key: 'll', width: 18 },
        { header: 'Lingkar Kepala (cm)', key: 'lk', width: 18 },
        { header: 'Z-Score BB/U', key: 'zbb', width: 14 },
        { header: 'Z-Score TB/U', key: 'ztb', width: 14 },
        { header: 'Status Gizi', key: 'status', width: 20 },
        { header: 'Prediksi', key: 'prediksi', width: 12 },
        { header: 'Confidence', key: 'confidence', width: 12 },
      ];

      // Style header
      worksheet.getRow(1).font = { bold: true, size: 12 };
      worksheet.getRow(1).fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FF0284C7' },
      };
      worksheet.getRow(1).font = { ...worksheet.getRow(1).font, color: { argb: 'FFFFFFFF' } };
      worksheet.getRow(1).alignment = { vertical: 'middle', horizontal: 'center' };

      // Add data
      posyanduData.forEach((item, index) => {
        worksheet.addRow({
          no: index + 1,
          tanggal: formatDate(item.tanggal_pengukuran),
          nama: item.balita_nama || '-',
          nik: item.balita_nik || '-',
          jk: getJenisKelaminLabel(item.jenis_kelamin),
          usia: item.usia_bulan,
          tb: formatNumber(item.tinggi_badan, 1),
          bb: formatNumber(item.berat_badan, 2),
          ll: formatNumber(item.lingkar_lengan, 1),
          lk: formatNumber(item.lingkar_kepala, 1),
          zbb: formatNumber(item.zscore_bbu, 2),
          ztb: formatNumber(item.zscore_tbu, 2),
          status: item.status_gizi,
          prediksi: item.prediksi_stunting ? 'STUNTING' : 'NORMAL',
          confidence: `${formatNumber(item.confidence_score * 100, 1)}%`,
        });
      });

      // Add border to all cells
      worksheet.eachRow({ includeEmpty: false }, (row) => {
        row.eachCell({ includeEmpty: true }, (cell) => {
          cell.border = {
            top: { style: 'thin' },
            left: { style: 'thin' },
            bottom: { style: 'thin' },
            right: { style: 'thin' },
          };
        });
      });
    };

    // Create sheets per posyandu
    if (isKader && kaderPosyandu) {
      // KADER: Only create sheet for their posyandu
      const sheetName = kaderPosyandu.nama.substring(0, 31);
      addPosyanduSheet(sheetName, filteredData);
    } else {
      // ADMIN: Create sheets for all posyandu
      posyanduList.forEach((posyandu) => {
        // Filter data for this posyandu (use original data, not filteredData)
        const posyanduData = data.filter(item => {
          const posyanduId = posyandu.id || posyandu.posyandu_id;
          const itemPosyanduId = item.posyandu_id;
          const itemPosyanduNama = item.posyandu_nama;
          
          const matchById = posyanduId && itemPosyanduId && itemPosyanduId === posyanduId;
          const matchByName = posyandu.nama && itemPosyanduNama && itemPosyanduNama === posyandu.nama;
          
          return matchById || matchByName;
        });
        
        // Create sheet with posyandu name (limit to 31 chars for Excel)
        const sheetName = posyandu.nama.substring(0, 31);
        addPosyanduSheet(sheetName, posyanduData);
      });
    }

    // Generate file
    const buffer = await workbook.xlsx.writeBuffer();
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(blob, `${filename}_${new Date().getTime()}.xlsx`);
  } catch (error) {
    console.error('Error exporting to Excel:', error);
    throw new Error('Gagal membuat file Excel: ' + error.message);
  }
};

/**
 * Export data balita ke Excel
 * @param {Array} data - Data balita
 * @param {string} filename - Nama file
 */
export const exportBalitaToExcel = async (data, filename = 'Data_Balita') => {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('Data Balita');

  worksheet.columns = [
    { header: 'No', key: 'no', width: 5 },
    { header: 'Nama Lengkap', key: 'nama', width: 25 },
    { header: 'NIK', key: 'nik', width: 18 },
    { header: 'Jenis Kelamin', key: 'jk', width: 15 },
    { header: 'Tanggal Lahir', key: 'tgl_lahir', width: 12 },
    { header: 'Usia (bulan)', key: 'usia', width: 12 },
    { header: 'Nama Orang Tua', key: 'ortu', width: 25 },
    { header: 'Alamat', key: 'alamat', width: 30 },
    { header: 'Status Terkini', key: 'status', width: 20 },
  ];

  // Style header
  worksheet.getRow(1).font = { bold: true };
  worksheet.getRow(1).fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FF0284C7' },
  };
  worksheet.getRow(1).font = { ...worksheet.getRow(1).font, color: { argb: 'FFFFFFFF' } };

  // Add data
  data.forEach((item, index) => {
    worksheet.addRow({
      no: index + 1,
      nama: item.nama_lengkap,
      nik: item.nik,
      jk: getJenisKelaminLabel(item.jenis_kelamin),
      tgl_lahir: formatDate(item.tanggal_lahir),
      usia: item.usia_bulan,
      ortu: item.nama_orang_tua,
      alamat: item.alamat,
      status: item.status_terkini || 'Belum ada pengukuran',
    });
  });

  // Generate and save
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  saveAs(blob, `${filename}_${new Date().getTime()}.xlsx`);
};

/**
 * Export Laporan Stunting Lengkap dengan Multi-Sheet
 * - Admin: 1 sheet Simpulan + 13 sheet per Posyandu (bulan berjalan)
 * - Kader: 1 sheet Simpulan + 6 sheet per bulan (6 bulan terakhir, filter posyandu kader)
 * 
 * @param {Array} data - Data pengukuran lengkap
 * @param {Object} user - User data (role, posyandu_id)
 * @param {Array} posyanduList - Daftar posyandu
 * @param {string} filename - Nama file
 */
export const exportLaporanStunting = async (data, user, posyanduList = [], filename = 'Laporan_Stunting') => {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'Sistem Deteksi Dini Stunting';
  workbook.created = new Date();

  const isAdmin = user?.role === 'admin';
  const kaderPosyanduId = user?.posyandu_id;

  // Filter data berdasarkan role
  let filteredData = [...data];
  if (!isAdmin && kaderPosyanduId) {
    // Kader: hanya data posyandu-nya
    filteredData = data.filter(d => d.posyandu_id === kaderPosyanduId);
  }

  // ==== SHEET 1: SIMPULAN ====
  const simpulanSheet = workbook.addWorksheet('Simpulan');
  
  if (isAdmin) {
    // Admin: Rekap per Posyandu bulan ini
    simpulanSheet.columns = [
      { header: 'No', key: 'no', width: 5 },
      { header: 'Nama Posyandu', key: 'posyandu', width: 30 },
      { header: 'Total Pengukuran', key: 'total', width: 18 },
      { header: 'Jumlah Stunting', key: 'stunting', width: 18 },
      { header: 'Persentase (%)', key: 'persen', width: 15 },
    ];

    // Style header
    simpulanSheet.getRow(1).font = { bold: true, size: 12 };
    simpulanSheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF0284C7' },
    };
    simpulanSheet.getRow(1).font = { ...simpulanSheet.getRow(1).font, color: { argb: 'FFFFFFFF' } };
    simpulanSheet.getRow(1).alignment = { vertical: 'middle', horizontal: 'center' };

    // Group by posyandu
    const posyanduStats = {};
    filteredData.forEach(d => {
      const posyanduName = d.posyandu_nama || 'Tidak Diketahui';
      if (!posyanduStats[posyanduName]) {
        posyanduStats[posyanduName] = { total: 0, stunting: 0 };
      }
      posyanduStats[posyanduName].total++;
      if (isStunting(d)) {
        posyanduStats[posyanduName].stunting++;
      }
    });

    // Add data
    let rowIndex = 1;
    Object.keys(posyanduStats).sort().forEach((posyanduName) => {
      const stat = posyanduStats[posyanduName];
      const persen = stat.total > 0 ? ((stat.stunting / stat.total) * 100).toFixed(2) : 0;
      
      simpulanSheet.addRow({
        no: rowIndex++,
        posyandu: posyanduName,
        total: stat.total,
        stunting: stat.stunting,
        persen: persen,
      });
    });

  } else {
    // Kader: Rekap per Bulan (6 bulan terakhir)
    simpulanSheet.columns = [
      { header: 'No', key: 'no', width: 5 },
      { header: 'Bulan', key: 'bulan', width: 20 },
      { header: 'Total Pengukuran', key: 'total', width: 18 },
      { header: 'Jumlah Stunting', key: 'stunting', width: 18 },
      { header: 'Persentase (%)', key: 'persen', width: 15 },
    ];

    // Style header
    simpulanSheet.getRow(1).font = { bold: true, size: 12 };
    simpulanSheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF0284C7' },
    };
    simpulanSheet.getRow(1).font = { ...simpulanSheet.getRow(1).font, color: { argb: 'FFFFFFFF' } };
    simpulanSheet.getRow(1).alignment = { vertical: 'middle', horizontal: 'center' };

    // Group by month (format: YYYY-MM)
    const monthStats = {};
    filteredData.forEach(d => {
      const date = new Date(d.tanggal_pengukuran);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      
      if (!monthStats[monthKey]) {
        monthStats[monthKey] = { total: 0, stunting: 0 };
      }
      monthStats[monthKey].total++;
      if (isStunting(d)) {
        monthStats[monthKey].stunting++;
      }
    });

    // Sort by month (newest first) and take last 6 months
    const sortedMonths = Object.keys(monthStats).sort().reverse().slice(0, 6);
    
    sortedMonths.forEach((monthKey, index) => {
      const stat = monthStats[monthKey];
      const persen = stat.total > 0 ? ((stat.stunting / stat.total) * 100).toFixed(2) : 0;
      const [year, month] = monthKey.split('-');
      const monthNames = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
      const monthName = `${monthNames[parseInt(month) - 1]} ${year}`;
      
      simpulanSheet.addRow({
        no: index + 1,
        bulan: monthName,
        total: stat.total,
        stunting: stat.stunting,
        persen: persen,
      });
    });
  }

  // Add borders to simpulan sheet
  simpulanSheet.eachRow({ includeEmpty: false }, (row) => {
    row.eachCell({ includeEmpty: true }, (cell) => {
      cell.border = {
        top: { style: 'thin' },
        left: { style: 'thin' },
        bottom: { style: 'thin' },
        right: { style: 'thin' },
      };
    });
  });

  // ==== SHEET 2-N: DATA DETAIL ====
  
  if (isAdmin) {
    // Admin: 1 sheet per Posyandu
    const posyanduGroups = {};
    filteredData.forEach(d => {
      const posyanduName = d.posyandu_nama || 'Tidak Diketahui';
      if (!posyanduGroups[posyanduName]) {
        posyanduGroups[posyanduName] = [];
      }
      posyanduGroups[posyanduName].push(d);
    });

    // Create sheet for each posyandu
    Object.keys(posyanduGroups).sort().forEach((posyanduName) => {
      const posyanduData = posyanduGroups[posyanduName];
      createDetailSheet(workbook, posyanduData, posyanduName);
    });

  } else {
    // Kader: 1 sheet per bulan (6 bulan terakhir)
    const monthGroups = {};
    filteredData.forEach(d => {
      const date = new Date(d.tanggal_pengukuran);
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      
      if (!monthGroups[monthKey]) {
        monthGroups[monthKey] = [];
      }
      monthGroups[monthKey].push(d);
    });

    // Sort and take last 6 months
    const sortedMonths = Object.keys(monthGroups).sort().reverse().slice(0, 6);
    const monthNames = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
    
    sortedMonths.forEach((monthKey) => {
      const monthData = monthGroups[monthKey];
      const [year, month] = monthKey.split('-');
      const sheetName = `${monthNames[parseInt(month) - 1]} ${year}`;
      createDetailSheet(workbook, monthData, sheetName);
    });
  }

  // Generate and save file
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  saveAs(blob, `${filename}_${timestamp}.xlsx`);
};

/**
 * Helper: Create detail sheet dengan data pengukuran
 * @param {Object} workbook - ExcelJS workbook
 * @param {Array} data - Data pengukuran
 * @param {string} sheetName - Nama sheet
 */
const createDetailSheet = (workbook, data, sheetName) => {
  // Sanitize sheet name (max 31 chars, no special chars)
  const sanitizedName = sheetName
    .replace(/[:\\\/\?\*\[\]]/g, '')
    .slice(0, 31);
  
  const sheet = workbook.addWorksheet(sanitizedName);

  // Define columns
  sheet.columns = [
    { header: 'No', key: 'no', width: 5 },
    { header: 'Tanggal', key: 'tanggal', width: 12 },
    { header: 'Nama', key: 'nama', width: 25 },
    { header: 'Jenis Kelamin', key: 'jk', width: 15 },
    { header: 'Usia (bulan)', key: 'usia', width: 12 },
    { header: 'Tinggi (cm)', key: 'tinggi', width: 12 },
    { header: 'Berat (kg)', key: 'berat', width: 12 },
    { header: 'Lingkar Lengan (cm)', key: 'll', width: 18 },
    { header: 'Lingkar Kepala (cm)', key: 'lk', width: 18 },
    { header: 'Z-Score BB/U', key: 'zbb', width: 14 },
    { header: 'Z-Score TB/U', key: 'ztb', width: 14 },
  ];

  // Style header
  sheet.getRow(1).font = { bold: true, size: 12 };
  sheet.getRow(1).fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FF0284C7' },
  };
  sheet.getRow(1).font = { ...sheet.getRow(1).font, color: { argb: 'FFFFFFFF' } };
  sheet.getRow(1).alignment = { vertical: 'middle', horizontal: 'center' };

  // Add data
  data.forEach((item, index) => {
    const row = sheet.addRow({
      no: index + 1,
      tanggal: formatDate(item.tanggal_pengukuran),
      nama: item.balita_nama || '-',
      jk: getJenisKelaminLabel(item.jenis_kelamin),
      usia: item.usia_bulan,
      tinggi: formatNumber(item.tinggi_badan, 1),
      berat: formatNumber(item.berat_badan, 2),
      ll: formatNumber(item.lingkar_lengan, 1),
      lk: formatNumber(item.lingkar_kepala, 1),
      zbb: formatNumber(item.zscore_bbu, 2),
      ztb: formatNumber(item.zscore_tbu, 2),
    });

    // Apply red styling if stunting
    if (isStunting(item)) {
      applyStuntingStyle(row);
    }
  });

  // Add borders
  sheet.eachRow({ includeEmpty: false }, (row) => {
    row.eachCell({ includeEmpty: true }, (cell) => {
      cell.border = {
        top: { style: 'thin' },
        left: { style: 'thin' },
        bottom: { style: 'thin' },
        right: { style: 'thin' },
      };
    });
  });

  // Add summary at bottom
  const summaryRow = sheet.rowCount + 2;
  sheet.getCell(`A${summaryRow}`).value = 'RINGKASAN';
  sheet.getCell(`A${summaryRow}`).font = { bold: true, size: 11 };
  
  const totalData = data.length;
  const totalStunting = data.filter(d => isStunting(d)).length;
  const totalNormal = totalData - totalStunting;
  const persentaseStunting = totalData > 0 ? ((totalStunting / totalData) * 100).toFixed(2) : 0;

  sheet.getCell(`A${summaryRow + 1}`).value = `Total Pengukuran: ${totalData}`;
  sheet.getCell(`A${summaryRow + 2}`).value = `Total Stunting: ${totalStunting} (${persentaseStunting}%)`;
  sheet.getCell(`A${summaryRow + 3}`).value = `Total Normal: ${totalNormal}`;
};

/**
 * Export statistik posyandu ke Excel
 * @param {Array} data - Data posyandu dengan statistik
 * @param {string} filename - Nama file
 */
export const exportStatistikPosyanduToExcel = async (data, filename = 'Statistik_Posyandu') => {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('Statistik Posyandu');

  worksheet.columns = [
    { header: 'No', key: 'no', width: 5 },
    { header: 'Nama Posyandu', key: 'nama', width: 25 },
    { header: 'Alamat', key: 'alamat', width: 30 },
    { header: 'Jumlah Balita', key: 'total', width: 15 },
    { header: 'Jumlah Stunting', key: 'stunting', width: 15 },
    { header: 'Persentase Stunting', key: 'persen', width: 18 },
  ];

  // Style header
  worksheet.getRow(1).font = { bold: true };
  worksheet.getRow(1).fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FF0284C7' },
  };
  worksheet.getRow(1).font = { ...worksheet.getRow(1).font, color: { argb: 'FFFFFFFF' } };

  // Add data
  data.forEach((item, index) => {
    const persentase = item.jumlah_balita > 0 
      ? (item.jumlah_stunting / item.jumlah_balita * 100).toFixed(2)
      : 0;
    
    worksheet.addRow({
      no: index + 1,
      nama: item.nama,
      alamat: item.alamat,
      total: item.jumlah_balita || 0,
      stunting: item.jumlah_stunting || 0,
      persen: `${persentase}%`,
    });
  });

  // Generate and save
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  saveAs(blob, `${filename}_${new Date().getTime()}.xlsx`);
};
