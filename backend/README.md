# Sistem Deteksi Dini Stunting Desa Gempol - Backend

API backend dikembangkan dengan FastAPI dan menggunakan model Machine Learning (K-Nearest Neighbors) untuk melakukan klasifikasi stunting.

## Fitur Utama

- Autentikasi dan Otorisasi (JWT, Role-Based Access)
- CRUD Data Balita dan Posyandu
- Algoritma Prediksi Stunting dengan KNN
- Kalkulasi Z-Score (BB/U dan TB/U) WHO otomatis
- Dukungan Data Spasial dengan PostGIS

## Persyaratan Lingkungan

- Python 3.10+
- PostgreSQL + PostGIS (atau Supabase)

## Menjalankan Server

1. Buat dan aktifkan virtual environment (venv).
2. Install requirement: pip install -r requirements.txt
3. Salin .env.example menjadi .env dan lengkapi konfigurasi database.
4. Latih model klasifikasi: python train_model.py
5. Jalankan server: uvicorn main:app --reload

Server akan berjalan secara lokal di port 8000. Untuk melihat dokumentasi antarmuka OpenAPI, akses /docs pada browser.
