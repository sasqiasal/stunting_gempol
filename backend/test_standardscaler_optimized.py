import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

print("="*70)
print("🧪 PENGUJIAN STANDARDSCALER + CUSTOM WEIGHTS OPTIMIZATION")
print("="*70)
print()

# DATA LATIH
data_latih = np.array([
    [1, 30, 11.7, 84.0, 14.8, 49.1],  # Anak A: 30 bln, Stunting
    [1, 28, 11.1, 81.5, 14.7, 48.9],  # Anak B: 28 bln, Stunting
    [1, 21, 12.5, 85.0, 15.5, 48.5],  # Anak C: 21 bln, NORMAL (IDEAL)
    [1, 20, 12.0, 84.5, 15.0, 48.2],  # Anak D: 20 bln, NORMAL
])
labels = np.array([2, 2, 0, 0])

# INPUT TEST: Baby D yang mirip dengan Anak C (sama usia 21bln)
baby_test = np.array([[1, 21, 11.48, 85.1, 15.2, 48.0]])

print("📌 DATA LATIH:")
print("  [0] Anak A: Usia 30bln, TB 84.0cm   (Stunting)")
print("  [1] Anak B: Usia 28bln, TB 81.5cm   (Stunting)")
print("  [2] Anak C: Usia 21bln, TB 85.0cm   (Normal) ← IDEAL: Seumuran!")
print("  [3] Anak D: Usia 20bln, TB 84.5cm   (Normal)")
print()
print("👶 INPUT TEST: Baby (Usia 21bln, TB 85.1cm)")
print("   Expected: Neighbor = Anak C (Index 2) karena seumuran")
print()
print("="*70)
print()

# TEST 1: DENGAN STANDARDSCALER
print("TEST 1️⃣: StandardScaler (BASIC)")
print("-"*70)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(data_latih)
baby_scaled = scaler.transform(baby_test)

print(f"Mean training: {scaler.mean_}")
print(f"Std training:  {scaler.scale_}")
print()

knn1 = KNeighborsClassifier(n_neighbors=1, weights='distance')
knn1.fit(X_train_scaled, labels)
pred1 = knn1.predict(baby_scaled)[0]
dist1, idx1 = knn1.kneighbors(baby_scaled)

print(f"Tetangga terdekat: Index {idx1[0][0]} (Anak {'ABCD'[idx1[0][0]]})")
print(f"Jarak: {dist1[0][0]:.4f}")
print(f"Prediksi: {['Normal', 'Stunting'][pred1//2]}")
print()

if idx1[0][0] == 2:
    print("✅ BENAR: Neighbor adalah Anak C (usia 21bln) - SESUAI HARAPAN!")
else:
    print(f"❌ SALAH: Neighbor adalah Anak {chr(65 + idx1[0][0])} bukan Anak C")
print()
print()

# TEST 2: DENGAN CUSTOM WEIGHT (USIA x2)
print("TEST 2️⃣: StandardScaler + Custom Weight (Usia x2)")
print("-"*70)

X_train_weighted = X_train_scaled.copy()
baby_weighted = baby_scaled.copy()

# Amplify fitur Usia (index 1) untuk membuat usia lebih berpengaruh
X_train_weighted[:, 1] *= 2.0
baby_weighted[:, 1] *= 2.0

print("Weight Usia: 2.0x (agar usia lebih penting)")
print()

knn2 = KNeighborsClassifier(n_neighbors=1, weights='distance')
knn2.fit(X_train_weighted, labels)
pred2 = knn2.predict(baby_weighted)[0]
dist2, idx2 = knn2.kneighbors(baby_weighted)

print(f"Tetangga terdekat: Index {idx2[0][0]} (Anak {'ABCD'[idx2[0][0]]})")
print(f"Jarak: {dist2[0][0]:.4f}")
print(f"Prediksi: {['Normal', 'Stunting'][pred2//2]}")
print()

if idx2[0][0] == 2:
    print("✅ BENAR: Neighbor adalah Anak C (usia 21bln) - SESUAI HARAPAN!")
else:
    print(f"❌ SALAH: Neighbor adalah Anak {chr(65 + idx2[0][0])} bukan Anak C")
print()
print()

# TEST 3: DENGAN CUSTOM WEIGHT (USIA x3 + GENDER x5)
print("TEST 3️⃣: StandardScaler + Custom Weights (Gender x5, Usia x3)")
print("-"*70)

X_train_weighted3 = X_train_scaled.copy()
baby_weighted3 = baby_scaled.copy()

# Amplify fitur Gender (index 0) x5 dan Usia (index 1) x3
X_train_weighted3[:, 0] *= 5.0  # Gender
X_train_weighted3[:, 1] *= 3.0  # Usia
baby_weighted3[:, 0] *= 5.0     # Gender
baby_weighted3[:, 1] *= 3.0     # Usia

print("Weight Gender: 5.0x | Weight Usia: 3.0x")
print()

knn3 = KNeighborsClassifier(n_neighbors=1, weights='distance')
knn3.fit(X_train_weighted3, labels)
pred3 = knn3.predict(baby_weighted3)[0]
dist3, idx3 = knn3.kneighbors(baby_weighted3)

print(f"Tetangga terdekat: Index {idx3[0][0]} (Anak {'ABCD'[idx3[0][0]]})")
print(f"Jarak: {dist3[0][0]:.4f}")
print(f"Prediksi: {['Normal', 'Stunting'][pred3//2]}")
print()

if idx3[0][0] == 2:
    print("✅ BENAR: Neighbor adalah Anak C (usia 21bln) - SESUAI HARAPAN!")
else:
    print(f"❌ SALAH: Neighbor adalah Anak {chr(65 + idx3[0][0])} bukan Anak C")
print()
print()

# RINGKASAN HASIL
print("="*70)
print("📊 RINGKASAN & ANALISIS")
print("="*70)
print()

results = [
    ("Test 1: StandardScaler (Basic)", idx1[0][0], dist1[0][0], pred1),
    ("Test 2: + Usia Weight x2", idx2[0][0], dist2[0][0], pred2),
    ("Test 3: + Gender x5, Usia x3", idx3[0][0], dist3[0][0], pred3),
]

print(f"{'No':<5} | {'Strategi':<35} | {'Neighbor':<12} | {'Jarak':<8} | {'Prediksi':<10} | {'Status':<12}")
print("-"*100)
for i, (nama, neighbor_idx, jarak, pred) in enumerate(results, 1):
    status = "✅ BENAR" if neighbor_idx == 2 else "❌ SALAH"
    neighbor_name = f"Anak {chr(65 + neighbor_idx)}"
    print(f"{i:<5} | {nama:<35} | {neighbor_name:<12} | {jarak:<8.4f} | {['Normal', 'Stunting'][pred//2]:<10} | {status:<12}")

print()
print()

# KESIMPULAN
print("="*70)
print("🎯 KESIMPULAN & REKOMENDASI")
print("="*70)
print()

success_tests = sum(1 for _, idx, _, _ in results if idx == 2)

if success_tests >= 2:
    print("✅ StandardScaler BERFUNGSI BAIK dengan Custom Weights!")
    print()
    print("Rekomendasi Implementasi di knn_model.py:")
    print("  1. Gunakan StandardScaler untuk normalisasi fitur")
    print("  2. Berikan weight TAMBAHAN untuk fitur penting:")
    print("     - Gender (JK): 5.0x (pisahkan boy/girl)")
    print("     - Usia (Usia): 2-3x (usia=faktor kritis)")
    print("  3. Gunakan weights='distance' di KNeighborsClassifier")
    print()
    print("Implementasi:")
    print("  X_scaled = scaler.transform(X)")
    print("  X_scaled[:, 0] *= 5.0  # Gender weight")
    print("  X_scaled[:, 1] *= 3.0  # Usia weight")
    print("  model.fit(X_scaled, y)")
else:
    print("⚠️  StandardScaler memerlukan OPTIMALISASI lebih lanjut")
    print()
    print("Saran:")
    print("  1. Coba Usia weight lebih tinggi (x4-5)")
    print("  2. Atau gunakan preprocessing lain (MinMaxScaler, RobustScaler)")
    print("  3. Atau adjust fitur engineering (normalize usia ke 0-1)")

print()
print("="*70)
