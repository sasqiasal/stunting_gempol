# Sistem Deteksi Dini Stunting Desa Gempol - Frontend

Antarmuka pengguna dibangun menggunakan React dan Vite. Aplikasi berfokus pada visualisasi pemetaan GIS dan manajemen pendataan oleh kader maupun admin.

## Fitur Utama

- Antarmuka Responsif (Desktop & Mobile)
- Peta Interaktif Sebaran Stunting (Leaflet.js)
- Formulir Pendataan Pengukuran Balita
- Ekspor Laporan berformat Excel (ExcelJS)
- Real-time Fetching dari Backend API

## Persyaratan Lingkungan

- Node.js 18+
- Akses ke backend API yang sudah beroperasi

## Menjalankan Frontend

1. Pindah ke direktori frontend: cd frontend
2. Hubungkan dependency: npm install
3. Salin .env.example menjadi .env dengan merujuk alamat API (VITE_API_BASE_URL).
4. Mulai development server: npm run dev

Frontend dapat diakses via browser pada port 5173 (secara default).
