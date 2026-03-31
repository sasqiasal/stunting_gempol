# Pengukuran Balita - Fix Usia Otomatis & Pilih Bulan

## 🎯 Perubahan yang Dibuat

### 1. **Frontend - PengukuranForm.jsx**

**Dari:** Date picker (pilih tanggal per hari)  
**Ke:** Month picker (pilih bulan saja)

```jsx
// LAMA: <input type="date" max={todayStr} />
// BARU: <select bulan_pengukuran (YYYY-MM format) />
```

**Fitur Baru:**
- ✅ Dropdown pilih bulan menggunakan nama bulan Indonesia (Januari, Februari, dll)
- ✅ **Batasan otomatis:** Hanya bisa pilih 4 bulan terakhir
  - Bulan saat ini (Maret 2026)
  - 3 bulan sebelumnya (Februari, Januari 2026, Desember 2025)
- ✅ **Usia OTOMATIS BERUBAH** saat user ganti bulan
  - Dengan formula yang benar dari birthdate ke bulan pengukuran

**Contoh Alur:**
```
Balita:"Budi" lahir 15 Januari 2025
Hari ini: 25 Maret 2026

Skenario 1 - Input data Maret 2026:
  User pilih: Maret 2026
  Usia saat itu: ~14 bulan
  Sistem: Hitung Z-score dengan age=14

Skenario 2 - Lengkapi data Desember 2025 yang hilang:
  User pilih: Desember 2025
  Usia saat itu: ~11 bulan (BUKAN 14!)
  Sistem: Hitung Z-score dengan age=11 (BENAR)
```

### 2. **Backend - pengukuran.py**

**Validasi Tanggal Pengukuran:**
```python
# Batasan range
min_date = first_day_of_3_months_ago  # Desember 1, 2025
max_date = last_day_of_current_month  # Maret 31, 2026

if tgl_ukur < min_date or tgl_ukur > max_date:
    Error: "Tanggal pengukuran harus dalam range ..."
```

**Perhitungan Usia yang Benar:**
```python
# Sebelum: Gunakan usia_bulan dari table balita (SALAH untuk data retroaktif)
# Sesudah: Hitung usia dari birthdate ke tanggal_pengukuran (BENAR)

usia_bulan = calculate_age_in_months(tanggal_lahir, tgl_ukur)
# Kemudian gunakan usia_bulan ini untuk Z-score calculation
```

---

## 🔄 Data Flow

```
Frontend Form:
  1. User pilih Bulan (dropdown): "Desember 2025"
  2. Usia auto-update: "11 bulan" (berdasarkan birth + bulan dipilih)
  3. Input BB, TB, Lingkar, dll
  4. Submit

Backend Processing:
  1. Terima: bulan_pengukuran → konversi ke tanggal_pengukuran (01 bulan tsb)
  2. Validasi: tgl_pengukuran dalam range [min_date, max_date]
  3. Hitung: usia_bulan = age(birthdate, tgl_pengukuran) → 11 bulan
  4. Prediksi: Z-score(age=11, TB, BB, etc)
  5. Simpan: prediksi_stunting dengan usia yang BENAR
```

---

## ✅ Keuntungan

| Masalah Lama | Solusi Baru |
|----------|-----------|
| Z-score salah kalau input retroaktif | ✅ Usia otomatis sesuai bulan pengukuran |
| User bingung dengan date picker | ✅ Dropdown bulan nama Indonesia |
| Bisa input data 1 tahun lalu | ✅ Batasi hanya 3 bulan + bulan ini |
| Prediksi stunting tidak akurat | ✅ Prediksi akurat karena usia tepat |

---

## 🧪 Testing Checklist

- [ ] Pilih bulan saat ini → Usia muncul sesuai usia balita sekarang
- [ ] Pilih 1 bulan lalu → Usia berkurang 1 bulan
- [ ] Pilih 3 bulan lalu → Usia berkurang 3 bulan
- [ ] Coba pilih bulan 4 tahun lalu → Harus disabled/tidak ada di dropdown
- [ ] Coba pilih bulan depan → Harus disabled/tidak ada di dropdown
- [ ] Submit pengukuran lama → Konfirmasi Z-score terupdate dengan usia yang tepat

---

## 📝 Info untuk Kader

> **Catatan:** 
> - Jika ada data pengukuran yang hilang dari bulan sebelumnya, gunakan dropdown "Bulan Pengukuran" untuk memilih bulan tersebut
> - Usia balita akan OTOMATIS BERUBAH sesuai bulan yang dipilih
> - Ini memastikan perhitungan Z-score dan klasifikasi stunting AKURAT
> - Hanya bisa input data dari 3 bulan lalu + bulan sekarang (untuk menjaga kualitas data)

---

## 🔧 Files Modified

- [src/components/PengukuranForm.jsx](#) - Frontend month picker + usia otomatis
- [api/app/routes/pengukuran.py](#) - Backend validasi + perhitungan usia
- [backend/app/routes/pengukuran.py](#) - Backend (duplicate) - same changes
- [backend/app/models/pengukuran.py](#) - Model sudah support tanggal_pengukuran
- [api/app/models/pengukuran.py](#) - Model sudah support tanggal_pengukuran
