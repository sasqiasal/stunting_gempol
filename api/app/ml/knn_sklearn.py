"""
K-Nearest Neighbors (KNN) Model untuk Prediksi Stunting
Menggunakan scikit-learn KNeighborsClassifier

Fitur yang digunakan:
1. Jenis Kelamin (encoded: 1=Laki-laki, 0=Perempuan)
2. Usia (bulan)
3. Tinggi Badan (cm)
4. Berat Badan (kg)
5. Lingkar Lengan (cm)
6. Lingkar Kepala (cm)

Target Label (Multi-class, 4 kelas):
- 0: Normal & Gizi Baik
- 1: Normal & Kurang Gizi
- 2: Stunting & Gizi Baik
- 3: Stunting & Kurang Gizi

IMPLEMENTASI MENGGUNAKAN SKLEARN:
- KNeighborsClassifier dengan metric='euclidean'
- StandardScaler dari sklearn untuk normalisasi fitur
- Fitted model disimpan untuk prediksi
"""

import numpy as np
import pickle
import os
from pathlib import Path
from typing import Tuple, Dict, Literal, List, Optional
import math

from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler


def euclidean_distance(point1: np.ndarray, point2: np.ndarray) -> float:
    """
    REFERENSI DOKUMENTASI: Menghitung Euclidean distance manual
    
    Formula: distance = sqrt(sum((x1 - x2)^2))
    
    Catatan: Fungsi ini hanya untuk referensi/dokumentasi.
    Pada implementasi utama, sklearn KNeighborsClassifier menghitung
    jarak ini secara internal dengan metric='euclidean'.
    
    Args:
        point1: Titik pertama (1D array)
        point2: Titik kedua (1D array)
        
    Returns:
        Jarak Euclidean sebagai float
    """
    squared_diff = np.power(point1 - point2, 2)
    distance = math.sqrt(np.sum(squared_diff))
    return distance


class StuntingKNNModel:
    """
    Model KNN untuk prediksi stunting menggunakan scikit-learn
    
    Menggunakan:
    - KNeighborsClassifier dengan metric='euclidean'
    - StandardScaler untuk normalisasi fitur
    - Multi-class classification (4 kelas)
    """
    
    # Mapping untuk 4-class labels ke deskripsi
    CLASS_LABELS = {
        0: "Normal & Gizi Baik",
        1: "Normal & Kurang Gizi",
        2: "Stunting & Gizi Baik",
        3: "Stunting & Kurang Gizi"
    }
    
    def __init__(self, n_neighbors: int = 5):
        """
        Inisialisasi model KNN dengan sklearn
        
        Args:
            n_neighbors: Jumlah tetangga terdekat (default: 5)
        """
        # Gunakan sklearn KNeighborsClassifier dengan metric Euclidean
        self.model = KNeighborsClassifier(
            n_neighbors=n_neighbors,
            metric='euclidean',
            weights='distance',  # Weighted voting berdasarkan jarak
            algorithm='auto'      # Auto-select best algorithm
        )
        
        # Gunakan sklearn StandardScaler untuk normalisasi
        self.scaler = StandardScaler()
        
        self.is_trained = False
        self.X_train_data = None
        self.y_train_data = None
        self.n_neighbors = n_neighbors
    
    def prepare_features(
        self,
        jenis_kelamin: Literal["L", "P"],
        usia_bulan: int,
        tinggi_badan: float,
        berat_badan: float,
        lingkar_lengan: float,
        lingkar_kepala: float,
        zscore_bbu: float = 0.0,
        zscore_tbu: float = 0.0
    ) -> np.ndarray:
        """
        Menyiapkan fitur untuk prediksi
        
        Menggunakan 6 fitur yang sama dengan training data:
        1. Jenis Kelamin (encoded: 1=L, 0=P)
        2. Usia (bulan)
        3. Berat Badan (kg)
        4. Tinggi Badan (cm)
        5. Lingkar Lengan (cm)
        6. Lingkar Kepala (cm)
        
        Args:
            jenis_kelamin: L untuk laki-laki, P untuk perempuan
            usia_bulan: Usia dalam bulan
            tinggi_badan: Tinggi badan dalam cm
            berat_badan: Berat badan dalam kg
            lingkar_lengan: Lingkar lengan atas dalam cm
            lingkar_kepala: Lingkar kepala dalam cm
            zscore_bbu: Z-Score Berat Badan/Usia (diterima tapi tidak digunakan sebagai fitur)
            zscore_tbu: Tidak dipakai sebagai fitur (hanya untuk ground truth evaluation)
        
        Returns:
            Array numpy dengan 6 fitur yang digunakan dalam training
        """
        # Encode jenis kelamin: L=1, P=0
        jk_encoded = 1 if jenis_kelamin == "L" else 0
        
        # Gabungkan 6 fitur (sesuai dengan training data)
        # Order: JK, Usia, BB, TB, LL, LK
        features = np.array([
            jk_encoded,
            usia_bulan,
            berat_badan,
            tinggi_badan,
            lingkar_lengan,
            lingkar_kepala,
        ]).reshape(1, -1)
        
        return features
    
    def _apply_custom_weights(self, X_scaled: np.ndarray) -> np.ndarray:
        """
        Memberi bobot lebih pada fitur tertentu setelah scaling.
        Terutama Gender agar jarak antar gender menjadi sangat jauh.
        
        Ini memastikan model lebih memilih tetangga dengan gender yang sama.
        
        Args:
            X_scaled: Fitur yang sudah di-scale (normalized)
            
        Returns:
            Fitur dengan custom weights diterapkan
        """
        X_weighted = X_scaled.copy()
        
        # Perbesar bobot Gender (index 0) agar menjadi pembeda utama
        # Nilai 5.0 cukup besar untuk memastikan gender separation yang kuat
        X_weighted[:, 0] *= 5.0
        
        return X_weighted

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, any]:
        """
        Melatih model KNN sklearn menggunakan SELURUH data sebagai training data.

        Metodologi:
        - Tidak ada train_test_split — 100% data digunakan untuk training
        - Model menyimpan semua data training (KNN adalah lazy learning)
        - Evaluasi model dilakukan menggunakan data balita BARU yang diinput
          melalui sistem (tabel pengukuran), bukan dari data latih itu sendiri
        - Ini mencegah evaluasi yang bias karena model tidak diuji pada data
          yang sudah "dilihat" saat training

        Args:
            X: Matriks fitur (n_samples, n_features)
            y: Label target (0, 1, 2, 3 untuk 4-class classification)
            test_size: Tidak digunakan (backward-compatibility)
            random_state: Tidak digunakan (backward-compatibility)

        Returns:
            Dictionary berisi info training
        """
        # Gunakan SEMUA data sebagai data latih
        X_train = X
        y_train = y

        # STEP 1: Standardisasi fitur menggunakan sklearn StandardScaler
        print(f"📊 Standardisasi fitur menggunakan sklearn.preprocessing.StandardScaler...")
        X_train_scaled = self.scaler.fit_transform(X_train)

        # STEP 2: Apply Custom Weights (separasi Gender)
        # Memberi bobot lebih pada fitur jenis_kelamin agar gender separation semakin kuat
        print(f"⚖️  Menerapkan custom weights untuk fitur jenis_kelamin...")
        X_train_weighted = self._apply_custom_weights(X_train_scaled)

        # STEP 3: Simpan seluruh data training sebagai referensi
        self.X_train_data = X_train
        self.y_train_data = y_train

        # STEP 4: Latih model KNN sklearn dengan data berbobot
        print(f"🔧 Training KNeighborsClassifier (k={self.n_neighbors}) dengan {len(X)} sampel...")
        print(f"   Metric: euclidean | Weights: distance | Classes: 4")
        self.model.fit(X_train_weighted, y_train)
        self.is_trained = True

        # STEP 5: Hitung training accuracy (untuk verifikasi)
        train_score = self.model.score(X_train_weighted, y_train)

        return {
            "train_accuracy": round(train_score, 4),
            "n_samples": len(X),
            "n_features": X.shape[1],
            "n_classes": 4,
            "method": "sklearn KNeighborsClassifier",
            "metric": "euclidean",
            "weights": "distance",
            "note": "Seluruh data digunakan untuk training. Evaluasi menggunakan data pengukuran baru dari sistem."
        }
    
    def predict(self, X: np.ndarray) -> Tuple[int, float]:
        """
        Melakukan prediksi menggunakan model KNN sklearn
        
        Args:
            X: Matriks fitur (1, n_features)
        
        Returns:
            Tuple (prediksi, confidence_score)
            - prediksi: Label kelas (0, 1, 2, atau 3)
            - confidence_score: Probabilitas kelas prediksi (0-1)
        """
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Gunakan method train() terlebih dahulu.")
        
        # STEP 1: Standardisasi fitur
        X_scaled = self.scaler.transform(X)
        
        # STEP 2: Apply custom weighting
        X_weighted = self._apply_custom_weights(X_scaled)
        
        # STEP 3: Prediksi class
        predictions = self.model.predict(X_weighted)
        prediction = int(predictions[0])
        
        # STEP 4: Hitung confidence (probability)
        # predict_proba mengembalikan array dengan shape (1, n_classes)
        probabilities = self.model.predict_proba(X_weighted)[0]
        
        # Ambil probabilitas untuk class yang diprediksi
        confidence = float(probabilities[prediction])
        
        return prediction, round(confidence, 4)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Mengembalikan probabilitas prediksi untuk semua kelas
        
        Args:
            X: Matriks fitur (n_samples, n_features)
        
        Returns:
            Array probabilitas dengan shape (n_samples, n_classes=4)
        """
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Gunakan method train() terlebih dahulu.")
        
        # Standardisasi fitur
        X_scaled = self.scaler.transform(X)
        
        # Apply custom weighting
        X_weighted = self._apply_custom_weights(X_scaled)
        
        # Return probabilities dari sklearn model
        return self.model.predict_proba(X_weighted)

    def find_nearest_neighbors(self, X: np.ndarray, n_neighbors: int = 5) -> List[Dict]:
        """
        Mencari tetangga terdekat yang RELEVAN (mempertimbangkan gender dan usia)
        
        Sistem akan mencari lebih banyak kandidat terlebih dahulu (n*10),
        kemudian memfilter kandidat tersebut agar hanya menampilkan:
        1. Gender yang sama (Sangat diprioritaskan)
        2. Usia yang berdekatan
        
        Args:
            X: Fitur sample (1, n_features)
            n_neighbors: Jumlah tetangga yang ingin ditampilkan
        
        Returns:
            List of dictionaries berisi info tetangga terdekat
        """
        if not self.is_trained:
            return []
        
        # Fallback handle if data not loaded
        if self.X_train_data is None or self.y_train_data is None:
            return []
            
        try:
            # 1. Cari lebih banyak kandidat (misal 50 tetangga)
            # Karena kita akan memfilter berdasarkan Gender dan Usia manual
            n_samples = len(self.X_train_data)
            n_candidates = min(n_samples, 50)
            
            # Standardisasi input
            X_scaled = self.scaler.transform(X)
            
            # Apply weighting agar pencarian neighbor konsisten dengan training
            X_weighted = self._apply_custom_weights(X_scaled)
            
            # Cari candidate neighbors menggunakan sklearn's kneighbors method
            distances, indices = self.model.kneighbors(X_weighted, n_neighbors=n_candidates)
            
            # Data Query (Input)
            # [JK, Usia, BB, TB, LL, LK]
            query_jk_val = X[0][0]  # 1 or 0
            query_usia = X[0][1]
            
            # 2. Proses kandidat
            relevant_neighbors = []
            
            candidates_idx = indices[0]
            candidates_dist = distances[0]
            
            for i in range(len(candidates_idx)):
                idx = candidates_idx[i]
                dist = candidates_dist[i]
                
                # Ambil data asli neighbor dari X_train_data
                original_data = self.X_train_data[idx]
                label = int(self.y_train_data[idx])
                
                neighbor_jk_val = original_data[0]
                
                # --- LOGIKA FILTER: HARD FILTER BERDASARKAN GENDER ---
                # Hanya masukkan ke list jika Gender SAMA
                # Agar list tetangga murni relevan secara biologis
                if neighbor_jk_val != query_jk_val:
                    continue
                
                # Label mapping untuk 4-class
                label_text = self.CLASS_LABELS.get(label, f"Unknown ({label})")
                
                neighbor_info = {
                    "distance": round(float(dist), 4),
                    "label": label_text,
                    "label_code": label,
                    "jenis_kelamin": "L" if original_data[0] == 1 else "P",
                    "usia_bulan": int(original_data[1]),
                    "berat_badan": float(original_data[2]),
                    "tinggi_badan": float(original_data[3]),
                    "lingkar_lengan": float(original_data[4]),
                    "lingkar_kepala": float(original_data[5])
                }
                
                relevant_neighbors.append(neighbor_info)
            
            # 3. Urutkan berdasarkan Distance (Ascending / Terkecil paling atas)
            # Ini akan menjamin Rank #1 adalah yang secara matematis paling dekat
            relevant_neighbors.sort(key=lambda x: x["distance"])
            
            # 4. Ambil top N
            return relevant_neighbors[:n_neighbors]
            
        except Exception as e:
            print(f"❌ Error filtering neighbors: {e}")
            return []
    
    def save_model(self, filepath: str = "app/ml/models/knn_stunting_model.pkl"):
        """
        Menyimpan model sklearn KNN ke file menggunakan PICKLE
        
        Args:
            filepath: Path untuk menyimpan model
        """
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Tidak ada yang disimpan.")
        
        # Buat direktori jika belum ada
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Simpan model dan scaler
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "is_trained": self.is_trained,
            "X_train_data": self.X_train_data,
            "y_train_data": self.y_train_data,
            "n_neighbors": self.n_neighbors,
            "method": "sklearn KNeighborsClassifier (euclidean metric)",
            "n_classes": 4
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model sklearn KNN berhasil disimpan di {filepath}")
    
    def load_model(self, filepath: str = "app/ml/models/knn_stunting_model.pkl"):
        """
        Memuat model sklearn KNN dari file
        
        Args:
            filepath: Path file model
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model tidak ditemukan di {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.is_trained = model_data["is_trained"]
        self.X_train_data = model_data.get("X_train_data", None)
        self.y_train_data = model_data.get("y_train_data", None)
        self.n_neighbors = model_data.get("n_neighbors", 5)
        
        print(f"✅ Model sklearn KNN berhasil dimuat dari {filepath}")


# Instance global model
knn_model = StuntingKNNModel(n_neighbors=5)


def get_knn_model() -> StuntingKNNModel:
    """
    Dependency untuk mendapatkan instance model KNN global
    
    Returns:
        Instance StuntingKNNModel yang sudah dilatih
    """
    return knn_model
