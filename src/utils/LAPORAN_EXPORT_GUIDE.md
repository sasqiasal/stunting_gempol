# Panduan Export Laporan Pengukuran

File ini menjelaskan cara menggunakan fungsi `exportLaporanPengukuranByPeriod` yang baru untuk membuat laporan dengan format berdasarkan periode (Bulanan, H1, H2).

## 📋 Struktur Format Laporan

### 1. Laporan Bulanan
- **File:** `Laporan_Pengukuran_[NamaBulan]_[Tahun].xlsx`
- **Contoh:** `Laporan_Pengukuran_Januari_2026.xlsx`
- **Sheet:** 1 sheet bernama "Laporan Bulanan"
- **Format:** Satu tabel untuk semua posyandu
- **Kolom:** No | Posyandu | Nama Balita | NIK | Jenis Kelamin | Usia | TB | BB | Lingkar Lengan | Z-Score BB | Z-Score TB | Status Gizi

### 2. Laporan H1 (Januari-Juni)
- **File:** `Laporan_Pengukuran_H1_[Tahun].xlsx`
- **Contoh:** `Laporan_Pengukuran_H1_2026.xlsx`
- **Sheet:** 1 sheet per posyandu (nama sheet = nama posyandu)
- **Data:** Riwayat 6 bulan (Januari s/d Juni)
- **Format:** Header bulan di-merge untuk setiap bulan

### 3. Laporan H2 (Juli-Desember)
- **File:** `Laporan_Pengukuran_H2_[Tahun].xlsx`
- **Contoh:** `Laporan_Pengukuran_H2_2026.xlsx`
- **Sheet:** 1 sheet per posyandu (nama sheet = nama posyandu)
- **Data:** Riwayat 6 bulan (Juli s/d Desember)
- **Format:** Header bulan di-merge untuk setiap bulan

## 🔧 Cara Penggunaan

### Import Fungsi
```javascript
import { exportLaporanPengukuranByPeriod } from '../utils/excelExport';
```

### Contoh 1: Export Laporan Bulanan (Januari 2026)
```javascript
const handleExportBulanan = async () => {
  try {
    await exportLaporanPengukuranByPeriod(
      pengukuranData,         // Array data pengukuran
      balitaData,             // Array data balita
      posyanduList,           // Array daftar posyandu
      'bulanan',              // Period: 'bulanan', 'H1', atau 'H2'
      1,                      // Month: 1-12 (hanya untuk bulanan)
      2026,                   // Year
      user                    // User object (role, posyandu_id)
    );
  } catch (error) {
    console.error('Export Error:', error);
  }
};
```

### Contoh 2: Export Laporan H1 (Januari-Juni 2026)
```javascript
const handleExportH1 = async () => {
  try {
    await exportLaporanPengukuranByPeriod(
      pengukuranData,
      balitaData,
      posyanduList,
      'H1',                   // Period
      null,                   // Month: null untuk H1/H2
      2026,
      user
    );
  } catch (error) {
    console.error('Export Error:', error);
  }
};
```

### Contoh 3: Export Laporan H2 (Juli-Desember 2026)
```javascript
const handleExportH2 = async () => {
  try {
    await exportLaporanPengukuranByPeriod(
      pengukuranData,
      balitaData,
      posyanduList,
      'H2',                   // Period
      null,
      2026,
      user
    );
  } catch (error) {
    console.error('Export Error:', error);
  }
};
```

## 📦 Parameter Fungsi

| Parameter | Type | Deskripsi | Required |
|-----------|------|-----------|----------|
| `pengukuranData` | Array | Data pengukuran dari API | ✅ |
| `balitaData` | Array | Data balita dari API | ✅ |
| `posyanduList` | Array | Daftar posyandu | ✅ |
| `period` | String | 'bulanan', 'H1', atau 'H2' | ✅ |
| `month` | Number | 1-12 (hanya untuk 'bulanan') | ❌ |
| `year` | Number | Tahun laporan (default: tahun sekarang) | ❌ |
| `user` | Object | User object dengan role dan posyandu_id | ❌ |

## 📊 Struktur Data yang Diharapkan

### Data Pengukuran (pengukuranData)
```javascript
{
  id: 1,
  balita_id: 1,
  posyandu_id: 1,
  tanggal_pengukuran: '2026-01-15',
  usia_bulan: 12,
  tinggi_badan: 85.5,
  berat_badan: 10.5,
  lingkar_lengan: 15.0,
  lingkar_kepala: 45.0,
  zscore_bbu: -0.5,
  zscore_tbu: -1.2,
  status_gizi: 'Normal'
}
```

### Data Balita (balitaData)
```javascript
{
  id: 1,
  nama_lengkap: 'Ahmad Doni',
  nik: '123456789012345',
  jenis_kelamin: 'L', // 'L' atau 'P'
  tanggal_lahir: '2025-01-15',
  posyandu_id: 1
}
```

### Data Posyandu (posyanduList)
```javascript
{
  id: 1,
  nama: 'Posyandu Maju',
  alamat: 'Jl. Merdeka No. 1'
}
```

### User Object
```javascript
{
  id: 1,
  role: 'admin', // 'admin' atau 'kader'
  posyandu_id: 1 // diperlukan jika role = 'kader'
}
```

## 🎨 Format Tampilan Excel

### Laporan H1 / H2 - Sheet per Posyandu
```
┌─────┬──────────────┬────────┬────────────┬──────────┬──────────┬──────────┬───────────┬───────────┬──────────┬──────────┬────────────┬──────────┬──────────┐
│ No  │ Nama Balita  │  NIK   │ Jenis K.   │ Januari  │ Februari │  Maret   │  April    │ Mei      │ Juni     │ Juli     │ Agustus    │  ...     │ Desember │
├─────┼──────────────┼────────┼────────────┼───────────────────────────────┼──────────────────────────────┼───────────────────────────────┤
│     │              │        │            │ U │TB│BB│LL│ZB│ZT│ST │ U │TB│BB│LL│ZB│ZT│ST │ U │TB│BB│LL│ZB│ZT│ST │
├─────┼──────────────┼────────┼────────────┼───────────────────────────────┼──────────────────────────────┼───────────────────────────────┤
│ 1   │ Ahmad Doni   │ 123... │ Laki-laki  │12│85│10│15│-0.5│-1.2│Normal│13│86│10.5│15│-0.3│-1.0│Normal│...│
│ 2   │ Budi Santoso │ 234... │ Laki-laki  │12│84│10│14│-0.6│-1.3│Normal│12│85│10│14.5│-0.5│-1.1│Normal│...│
│ 3   │ Citra Dewi   │ 345... │ Perempuan  │11│82│9.5│14│-0.7│-1.4│Normal│12│83│9.8│14│-0.6│-1.2│Normal│...│
└─────┴──────────────┴────────┴────────────┴───────────────────────────────┴──────────────────────────────┴───────────────────────────────┘

Keterangan:
- U: Usia (bulan)
- TB: Tinggi Badan (cm)
- BB: Berat Badan (kg)
- LL: Lingkar Lengan (cm)
- ZB: Z-Score BB
- ZT: Z-Score TB
- ST: Status Gizi
```

## 🔐 Kontrol Akses

- **Admin:** Dapat mengekspor semua posyandu
- **Kader:** Hanya dapat mengekspor data posyandu mereka sendiri

Sistem otomatis memfilter data berdasarkan `user.posyandu_id`

## ⚙️ Integrasi dengan React Component

### Contoh Komponen Export
```jsx
import React, { useState } from 'react';
import { exportLaporanPengukuranByPeriod } from '../utils/excelExport';

export const LaporanExport = ({ 
  pengukuranData, 
  balitaData, 
  posyanduList, 
  user 
}) => {
  const [loading, setLoading] = useState(false);
  const currentYear = new Date().getFullYear();

  const handleExport = async (period, month = null) => {
    setLoading(true);
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
      // Tampilkan success toast
    } catch (error) {
      // Tampilkan error toast
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="export-buttons">
      {/* Tombol Bulanan */}
      <div className="monthly-section">
        <h3>Laporan Bulanan</h3>
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(month => (
          <button
            key={month}
            onClick={() => handleExport('bulanan', month)}
            disabled={loading}
          >
            {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month - 1]}
          </button>
        ))}
      </div>

      {/* Tombol Periode */}
      <div className="period-section">
        <button 
          onClick={() => handleExport('H1')} 
          disabled={loading}
        >
          Laporan H1 (Jan-Jun)
        </button>
        <button 
          onClick={() => handleExport('H2')} 
          disabled={loading}
        >
          Laporan H2 (Jul-Des)
        </button>
      </div>
    </div>
  );
};
```

## 🐛 Troubleshooting

### File tidak terbuat
- Pastikan `pengukuranData` tidak kosong
- Periksa bahwa ada data pengukuran di periode yang dipilih

### Sheet kosong
- Verifikasi `balitaData` dan `pengukuranData` ada referensi yang sama (balita_id)
- Pastikan periode dipilih dengan benar

### Header bulan tidak merge
- Pastikan browser mendukung fitur merge cell di ExcelJS
- Update library `exceljs` ke versi terbaru: `npm install exceljs@latest`

## 📝 Catatan Penting

1. **Data harus lengkap:** Pastikan semua data referensi (pengukuran, balita, posyandu) tersedia
2. **Format tanggal:** Gunakan format `YYYY-MM-DD` untuk `tanggal_pengukuran`
3. **User role:** Sistem akan otomatis memfilter berdasarkan role user
4. **Performa:** Jika data sangat besar (>10000 record), pertimbangkan pagination

## 📞 Support

Jika ada pertanyaan atau error, cek:
1. Console browser (F12 > Console tab)
2. Network tab untuk melihat data yang dikirim
3. Struktur data pengukuran dan balita
