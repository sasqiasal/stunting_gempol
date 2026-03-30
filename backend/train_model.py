"""
Script untuk melatih model KNN MANUAL (tanpa sklearn) dengan klasifikasi biner (0=Normal, 1=Stunting)
dan menyimpannya sebagai file .pkl.

Implementasi:
- Menggunakan Manual KNN dengan Euclidean Distance
- Manual Z-score normalization untuk feature scaling
- Majority voting untuk klasifikasi

Konversi label dari CSV:
  0 (Normal + Gizi Baik)    → 0 (Normal)
  1 (Normal + Kurang Gizi)  → 0 (Normal)
  3 (Stunting + Gizi Baik)  → 1 (Stunting)
  4 (Stunting + Kurang Gizi)→ 1 (Stunting)

Jalankan dengan:
    cd backend
    python train_model.py
"""

import pandas as pd
import numpy as np
import os
import sys

# Tambahkan path agar app module bisa diimport
sys.path.insert(0, os.path.dirname(__file__))

from app.ml.knn_model import StuntingKNNModel

CSV_PATH = "data_latih_stunting.csv"
MODEL_PATH = "app/ml/models/knn_stunting_model.pkl"


def load_and_preprocess_csv(csv_path: str):
    """
    Membaca CSV dengan 4 kelas label (Multi-class).
    Label dari CSV (0, 1, 2, 3):
    - 0 = Normal + Gizi Baik
    - 1 = Normal + Kurang Gizi
    - 2 = Stunting + Gizi Baik
    - 3 = Stunting + Kurang Gizi
    """
    df = pd.read_csv(csv_path)
    print(f"✅ CSV dimuat: {len(df)} sampel")

    print(f"\n📊 Distribusi label (dari CSV):")
    label_counts = df["status_stunting"].value_counts().sort_index()
    label_names = {
        0: "Normal + Gizi Baik",
        1: "Normal + Kurang Gizi",
        2: "Stunting + Gizi Baik",
        3: "Stunting + Kurang Gizi"
    }
    for lbl, cnt in label_counts.items():
        name = label_names.get(int(lbl), "Unknown")
        print(f"   Kelas {lbl} ({name}): {cnt} sampel ({cnt/len(df)*100:.1f}%)")

    X_list, y_list = [], []
    for _, row in df.iterrows():
        # Tetap gunakan label asli dari CSV (0, 1, 2, 3)
        label = int(row["status_stunting"])
        y_list.append(label)

        jk_enc = 1 if int(float(row["jenis_kelamin"])) == 1 else 0
        X_list.append([
            jk_enc,
            float(row["usia_bulan"]),
            float(row["berat_badan"]),
            float(row["tinggi_badan"]),
            float(row["lingkar_lengan"]),
            float(row["lingkar_kepala"]),
            float(row["z_score_bb"]),
            float(row["z_score_tb"])
        ])

    X = np.array(X_list)
    y = np.array(y_list)
    
    print("\n--- DEBUG FITUR ---")
    print(f"Dataset columns: {df.columns.tolist()}")
    print(f"Sample training row X[0]: {X[0]}")
    print("-------------------\n")

    # Hitung distribusi untuk 4 kelas
    class_counts = {}
    for i in range(4):
        class_counts[i] = int(np.sum(y == i))
    
    print(f"   → Distribusi:")
    print(f"      Kelas 0 (Normal + Gizi Baik)     : {class_counts[0]} sampel")
    print(f"      Kelas 1 (Normal + Kurang Gizi)   : {class_counts[1]} sampel")
    print(f"      Kelas 2 (Stunting + Gizi Baik)   : {class_counts[2]} sampel")
    print(f"      Kelas 3 (Stunting + Kurang Gizi) : {class_counts[3]} sampel")

    return X, y


def train_and_save(n_neighbors: int = 5):
    if not os.path.exists(CSV_PATH):
        print(f"❌ File CSV tidak ditemukan: {CSV_PATH}")
        sys.exit(1)

    print("=" * 60)
    print("  Training MANUAL KNN Model (No sklearn)")
    print("  Multi-Class Klasifikasi (4 Kelas)")
    print("=" * 60)

    X, y = load_and_preprocess_csv(CSV_PATH)

    model = StuntingKNNModel(n_neighbors=n_neighbors)
    print(f"\n🔧 Training MANUAL KNN (k={n_neighbors}) dengan {len(X)} sampel...")
    result = model.train(X, y)

    print(f"\n✅ Training selesai!")
    print(f"   Method           : {result.get('method', 'Manual KNN')}")
    print(f"   Train Accuracy   : {result['train_accuracy'] * 100:.2f}%")
    print(f"   Jumlah sampel    : {result['n_samples']}")
    print(f"   Jumlah fitur     : {result['n_features']}")

    # Simpan model
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save_model(MODEL_PATH)
    print(f"\n💾 Model MANUAL disimpan di: {MODEL_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    train_and_save(n_neighbors=5)
