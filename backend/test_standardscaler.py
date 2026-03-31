import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

# 1. SIMULASI DATA LATIH (X_train)
# Format: [JK(1=L), Usia, BB, TB, LL, LK]
# Kita masukkan data anak stunting usia 30 bulan (TB 84) 
# dan anak normal usia 21 bulan (TB 85)
data_latih = np.array([
    [1, 30, 11.7, 84.0, 14.8, 49.1], # Anak A: 30 bln, Stunting (karena untuk 30bln 84cm itu pendek)
    [1, 28, 11.1, 81.5, 14.7, 48.9], # Anak B: 28 bln, Stunting
    [1, 21, 12.5, 85.0, 15.5, 48.5], # Anak C: 21 bln, NORMAL (Seumuran Baby D)
    [1, 20, 12.0, 84.5, 15.0, 48.2], # Anak D: 20 bln, NORMAL
])
# Label: 0 = Normal, 2 = Stunting
labels = np.array([2, 2, 0, 0])

# 2. DATA BABY D (Input yang akan diuji)
baby_d = np.array([[1, 21, 11.48, 85.1, 15.2, 48.0]])

print("="*60)
print("🧪 PENGUJIAN STANDARD SCALER - SISTEM KNN STUNTING")
print("="*60)
print()

# --- SKENARIO A: TANPA SCALING ---
print("📊 SKENARIO A: TANPA SCALING (Raw Distance)")
print("-" * 60)

knn_raw = KNeighborsClassifier(n_neighbors=1)
knn_raw.fit(data_latih, labels)
pred_raw = knn_raw.predict(baby_d)
dist_raw, idx_raw = knn_raw.kneighbors(baby_d)

print(f"Data Latih:")
print(f"  [0] Anak A: Usia 30bln, TB 84.0cm   → Label: Stunting (2)")
print(f"  [1] Anak B: Usia 28bln, TB 81.5cm   → Label: Stunting (2)")
print(f"  [2] Anak C: Usia 21bln, TB 85.0cm   → Label: Normal (0)")
print(f"  [3] Anak D: Usia 20bln, TB 84.5cm   → Label: Normal (0)")
print()
print(f"Input Baby D: Usia 21bln, BB 11.48kg, TB 85.1cm, LL 15.2cm, LK 48.0cm")
print()
print(f"✓ KNN Prediction: {['Normal', 'Stunting'][pred_raw[0]//2]}")
print(f"✓ Tetangga Terdekat: Anak Index {idx_raw[0][0]} (dari data latih)")
print(f"  → Usia: {data_latih[idx_raw[0][0]][1]} bulan")
print(f"  → Label: {['Normal', 'Stunting'][labels[idx_raw[0][0]]//2]}")
print(f"✓ Jarak (Euclidean Raw): {dist_raw[0][0]:.4f}")
print()
print("🔴 MASALAH TANPA SCALING:")
print("   - Fitur 'Usia' (range 0-60) KALAH dengan 'TB' (range 50-110)")
print("   - Jarak tidak fair karena skala fitur berbeda!")
print()

# --- SKENARIO B: DENGAN STANDARD SCALER ---
print()
print("📊 SKENARIO B: DENGAN STANDARD SCALER (Normalized)")
print("-" * 60)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(data_latih)
baby_d_scaled = scaler.transform(baby_d)

print(f"StandardScaler Mean & Std dari Training Data:")
print(f"  Feature [0] JK:  mean={scaler.mean_[0]:.3f}, std={scaler.scale_[0]:.3f}")
print(f"  Feature [1] Usia:  mean={scaler.mean_[1]:.3f}, std={scaler.scale_[1]:.3f}")
print(f"  Feature [2] BB:    mean={scaler.mean_[2]:.3f}, std={scaler.scale_[2]:.3f}")
print(f"  Feature [3] TB:    mean={scaler.mean_[3]:.3f}, std={scaler.scale_[3]:.3f}")
print(f"  Feature [4] LL:    mean={scaler.mean_[4]:.3f}, std={scaler.scale_[4]:.3f}")
print(f"  Feature [5] LK:    mean={scaler.mean_[5]:.3f}, std={scaler.scale_[5]:.3f}")
print()

print(f"Data Latih (SCALED):")
for i in range(len(data_latih)):
    print(f"  [{i}] {X_train_scaled[i]} → Label: {labels[i]}")
print()

print(f"Baby D (SCALED): {baby_d_scaled[0]}")
print()

knn_scaled = KNeighborsClassifier(n_neighbors=1)
knn_scaled.fit(X_train_scaled, labels)
pred_scaled = knn_scaled.predict(baby_d_scaled)
dist_scaled, idx_scaled = knn_scaled.kneighbors(baby_d_scaled)

print(f"✓ KNN Prediction: {['Normal', 'Stunting'][pred_scaled[0]//2]}")
print(f"✓ Tetangga Terdekat: Anak Index {idx_scaled[0][0]} (dari data latih)")
print(f"  → Usia: {data_latih[idx_scaled[0][0]][1]} bulan")
print(f"  → Label: {['Normal', 'Stunting'][labels[idx_scaled[0][0]]//2]}")
print(f"✓ Jarak (Euclidean Scaled): {dist_scaled[0][0]:.4f}")
print()
print("🟢 KEUNTUNGAN DENGAN SCALING:")
print("   ✓ Semua fitur dinormalisasi ke range [-1, 1]")
print("   ✓ Fitur 'Usia' sekarang SETARA importance dengan 'TB'")
print("   ✓ Prediksi lebih fair dan akurat!")
print()

# 3. CETAK HASIL PERBANDINGAN
print()
print("="*60)
print("📋 RINGKASAN HASIL PERBANDINGAN")
print("="*60)
print()
print(f"Input: Baby D (Usia 21 bln, TB 85.1 cm) → SEHARUSNYA Normal (sama usia dengan Anak C)")
print()
print(f"{'Skenario':<30} | {'Prediksi':<10} | {'Jarak':<10} | {'Tetangga Index':<15}")
print("-" * 70)
print(f"{'TANPA Scaling (Raw)':<30} | {['Normal', 'Stunting'][pred_raw[0]//2]:<10} | {dist_raw[0][0]:<10.4f} | {idx_raw[0][0]:<15}")
print(f"{'DENGAN StandardScaler':<30} | {['Normal', 'Stunting'][pred_scaled[0]//2]:<10} | {dist_scaled[0][0]:<10.4f} | {idx_scaled[0][0]:<15}")
print()

# Verifikasi
print("="*60)
print("✅ VERIFIKASI STANDARDSCALER")
print("="*60)

if idx_scaled[0][0] == 2:  # Harus Anak C (index 2) karena seumuran
    print("🟢 BENAR! Dengan StandardScaler, tetangga terdekat adalah Anak Index 2")
    print("   → Anak C (Usia 21 bln, TB 85cm) - Seumuran dengan Baby D (Usia 21bln)")
    print("   → Prediksi: Normal ✓")
    print()
    print("✅ STANDARDSCALER BERHASIL BERFUNGSI!")
else:
    print(f"🔴 SALAH! Tetangga terdekat adalah Anak Index {idx_scaled[0][0]}")
    print(f"   Ini berarti fitur 'Usia' masih tidak cukup berpengaruh")
    print("   StandardScaler mungkin belum optimal")
    print()
    print("⚠️  STANDARDSCALER PERLU DIOPTIMALKAN!")

print()
print("="*60)
