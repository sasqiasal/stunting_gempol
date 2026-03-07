"""
Model Machine Learning KNN (K-Nearest Neighbors) untuk Prediksi Stunting

Menggunakan 8 variabel:
1. Jenis Kelamin (encoded: L=1, P=0)
2. Usia (bulan)
3. Tinggi Badan (cm)
4. Berat Badan (kg)
5. Lingkar Lengan (cm)
6. Lingkar Kepala (cm)
7. Z-Score BB/U (Berat Badan/Usia)
8. Z-Score TB/U (Tinggi Badan/Usia)
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, Literal, List
import joblib
import os
from pathlib import Path

class StuntingKNNModel:
    """
    Model KNN untuk prediksi stunting dengan 8 variabel
    """
    
    def __init__(self, n_neighbors: int = 5):
        """
        Inisialisasi model KNN
        
        Args:
            n_neighbors: Jumlah tetangga terdekat (default: 5)
        """
        self.model = KNeighborsClassifier(
            n_neighbors=n_neighbors,
            weights='distance',  # Weight berdasarkan jarak
            metric='euclidean'
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.X_train_data = None
        self.y_train_data = None
        
    def prepare_features(
        self,
        jenis_kelamin: Literal["L", "P"],
        usia_bulan: int,
        tinggi_badan: float,
        berat_badan: float,
        lingkar_lengan: float,
        lingkar_kepala: float,
        zscore_bbu: float,
        zscore_tbu: float
    ) -> np.ndarray:
        """
        Menyiapkan fitur untuk prediksi
        
        Args:
            jenis_kelamin: L untuk laki-laki, P untuk perempuan
            usia_bulan: Usia dalam bulan
            tinggi_badan: Tinggi badan dalam cm
            berat_badan: Berat badan dalam kg
            lingkar_lengan: Lingkar lengan atas dalam cm
            lingkar_kepala: Lingkar kepala dalam cm
            zscore_bbu: Z-Score Berat Badan/Usia
            zscore_tbu: Z-Score Tinggi Badan/Usia
        
        Returns:
            Array numpy dengan 8 fitur
        """
        # Encode jenis kelamin: L=1, P=0
        jk_encoded = 1 if jenis_kelamin == "L" else 0
        
        # Gabungkan semua fitur
        features = np.array([
            jk_encoded,
            usia_bulan,
            tinggi_badan,
            berat_badan,
            lingkar_lengan,
            lingkar_kepala,
            zscore_bbu,
            zscore_tbu
        ]).reshape(1, -1)
        
        return features
    
    def _apply_custom_weights(self, X_scaled: np.ndarray) -> np.ndarray:
        """
        Memberi bobot lebih pada fitur tertentu setelah scaling.
        Terutama Gender agar jarak antar gender menjadi sangat jauh.
        Ini memastikan model lebih memilih tetangga dengan gender yang sama.
        """
        X_weighted = X_scaled.copy()
        # Perbesar bobot Gender (index 0) agar menjadi pembeda utama
        # Nilai 4.0 cukup besar (sekitar 8 standar deviasi bedanya)
        # Sehingga jarak Euclidean antar beda gender akan sangat jauh
        X_weighted[:, 0] *= 5.0 
        return X_weighted

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,   # Diabaikan — semua data digunakan sebagai training
        random_state: int = 42    # Diabaikan — tidak ada split
    ) -> Dict[str, float]:
        """
        Melatih model KNN menggunakan SELURUH data sebagai data latih.

        Metodologi:
        - Tidak ada train_test_split — 100% data digunakan untuk training.
        - Evaluasi model dilakukan menggunakan data balita BARU yang diinput
          melalui sistem (tabel pengukuran), bukan dari data latih itu sendiri.
        - Ini mencegah evaluasi yang bias karena model tidak diuji pada data
          yang sudah "dilihat" saat training.

        Args:
            X: Matriks fitur (n_samples, 8)
            y: Label target (0: Normal+GB, 1: Normal+KG, 3: Stunting+GB, 4: Stunting+KG)
            test_size: Tidak digunakan (disimpan untuk backward-compatibility)
            random_state: Tidak digunakan (disimpan untuk backward-compatibility)

        Returns:
            Dictionary berisi info training
        """
        # Gunakan SEMUA data sebagai data latih
        X_train = X
        y_train = y

        # Standardisasi fitur — fit pada seluruh data training
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Apply Custom Weights (FORCE GENDER SEPARATION)
        X_train_weighted = self._apply_custom_weights(X_train_scaled)

        # Simpan seluruh data training sebagai referensi neighbors
        self.X_train_data = X_train
        self.y_train_data = y_train

        # Latih model dengan data berbobot
        self.model.fit(X_train_weighted, y_train)
        self.is_trained = True

        # Skor pada data latih (bukan evaluasi; hanya untuk verifikasi training berhasil)
        train_score = self.model.score(X_train_weighted, y_train)

        return {
            "train_accuracy": round(train_score, 4),
            "n_samples": len(X),
            "n_features": X.shape[1],
            "note": "Seluruh data digunakan untuk training. Evaluasi menggunakan data pengukuran baru dari sistem."
        }
    
    def predict(self, X: np.ndarray) -> Tuple[int, float]:
        """
        Melakukan prediksi
        
        Args:
            X: Matriks fitur (1, 8)
        
        Returns:
            Tuple (prediksi, confidence_score)
            - prediksi: 0 (Normal) atau 1 (Stunting)
            - confidence_score: Probabilitas kelas prediksi (0-1)
        """
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Gunakan method train() terlebih dahulu.")
        
        # Standardisasi fitur
        X_scaled = self.scaler.transform(X)
        
        # Apply weighting
        X_weighted = self._apply_custom_weights(X_scaled)
        
        # Prediksi
        prediction = self.model.predict(X_weighted)[0]
        
        # Probabilitas (confidence score)
        probabilities = self.model.predict_proba(X_weighted)[0]
        
        # Get class labels yang ada di model
        class_labels = self.model.classes_
        
        # Find index dari prediction di class_labels
        pred_idx = list(class_labels).index(prediction)
        confidence = probabilities[pred_idx]
        
        return int(prediction), round(float(confidence), 4)

    def find_nearest_neighbors(self, X: np.ndarray, n_neighbors: int = 5) -> List[Dict]:
        """
        Mencari tetangga terdekat yang RELEVAN (mempertimbangkan gender dan usia)
        
        Sistem akan mencari lebih banyak kandidat terlebih dahulu (n*10),
        kemudian memfilter kandidat tersebut agar hanya menampilkan:
        1. Gender yang sama (Sangat diprioritaskan)
        2. Usia yang berdekatan
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
            
            # Cari kandidat neighbors
            distances, indices = self.model.kneighbors(X_weighted, n_neighbors=n_candidates)
            
            # Data Query (Input)
            # [JK, Usia, TB, BB, LL, LK, Z-BBU, Z-TBU]
            query_jk_val = X[0][0] # 1 or 0
            query_usia = X[0][1]
            
            # 2. Proses kandidat
            relevant_neighbors = []
            
            candidates_idx = indices[0]
            candidates_dist = distances[0]
            
            for i in range(len(candidates_idx)):
                idx = candidates_idx[i]
                dist = candidates_dist[i]
                
                # Ambil data asli neighbor
                original_data = self.X_train_data[idx]
                label = self.y_train_data[idx]
                
                neighbor_jk_val = original_data[0]
                
                # --- LOGIKA BARU: HARD FILTER ---
                # Hanya masukkan ke list jika Gender SAMA
                # Agar list tetangga murni relevan secara biologis
                if neighbor_jk_val != query_jk_val:
                    continue
                
                # Label Mapping
                label_map = {
                    0: "Normal + Gizi Baik",
                    1: "Normal + Kurang Gizi",
                    3: "Stunting + Gizi Baik",
                    4: "Stunting + Kurang Gizi"
                }
                
                neighbor_info = {
                    "distance": round(float(dist), 4),
                    # Kita tidak lagi pakai relevance_score yang kompleks
                    # Cukup distance sebagai penentu urutan utama
                    "jenis_kelamin": "L" if original_data[0] == 1 else "P",
                    "usia_bulan": int(original_data[1]),
                    "tinggi_badan": float(original_data[2]),
                    "berat_badan": float(original_data[3]),
                    "label": label_map.get(int(label), f"Unknown ({label})")
                }
                
                relevant_neighbors.append(neighbor_info)
            
            # 3. Urutkan berdasarkan Distance (Ascending / Terkecil paling atas)
            # Ini akan menjamin Rank #1 adalah yang secara matematika paling dekat
            relevant_neighbors.sort(key=lambda x: x["distance"])
            
            # 4. Ambil top N
            return relevant_neighbors[:n_neighbors]
            
        except Exception as e:
            print(f"Error filtering neighbors: {e}")
            return []
    
    def save_model(self, filepath: str = "app/ml/models/knn_stunting_model.pkl"):
        """
        Menyimpan model ke file
        
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
            "y_train_data": self.y_train_data
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model berhasil disimpan di {filepath}")
    
    def load_model(self, filepath: str = "app/ml/models/knn_stunting_model.pkl"):
        """
        Memuat model dari file
        
        Args:
            filepath: Path file model
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model tidak ditemukan di {filepath}")
        
        # Load model dan scaler
        model_data = joblib.load(filepath)
        
        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.is_trained = model_data["is_trained"]
        # Load training data jika ada (backward compatibility)
        self.X_train_data = model_data.get("X_train_data", None)
        self.y_train_data = model_data.get("y_train_data", None)
        
        print(f"Model berhasil dimuat dari {filepath}")

def generate_synthetic_training_data(n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate data training sintetik untuk keperluan demonstrasi
    
    NOTE: Pada produksi, gunakan data real dari pengukuran balita
    
    Args:
        n_samples: Jumlah sampel yang akan digenerate
    
    Returns:
        Tuple (X, y)
        - X: Matriks fitur (n_samples, 8)
        - y: Label target (0: Normal, 1: Stunting)
    """
    np.random.seed(42)
    
    X = []
    y = []
    
    for _ in range(n_samples):
        # Random jenis kelamin
        jk = np.random.choice([0, 1])  # 0: Perempuan, 1: Laki-laki
        
        # Random usia (6-60 bulan)
        usia = np.random.randint(6, 61)
        
        # Tentukan apakah stunting atau normal (50-50)
        is_stunting = np.random.choice([0, 1])
        
        if is_stunting:
            # Data untuk stunting (nilai lebih rendah)
            tinggi = np.random.uniform(60, 95)  # Lebih pendek
            berat = np.random.uniform(5, 13)    # Lebih ringan
            lingkar_lengan = np.random.uniform(11, 14)  # Lebih kecil
            lingkar_kepala = np.random.uniform(42, 48)  # Lebih kecil
            zscore_bbu = np.random.uniform(-3.5, -1.5)  # Negatif
            zscore_tbu = np.random.uniform(-3.5, -2.0)  # Stunting threshold
        else:
            # Data untuk normal
            tinggi = np.random.uniform(70, 110)  # Normal
            berat = np.random.uniform(7, 18)     # Normal
            lingkar_lengan = np.random.uniform(13, 17)  # Normal
            lingkar_kepala = np.random.uniform(45, 52)  # Normal
            zscore_bbu = np.random.uniform(-1.5, 2)     # Normal range
            zscore_tbu = np.random.uniform(-1.5, 2)     # Normal range
        
        X.append([jk, usia, tinggi, berat, lingkar_lengan, lingkar_kepala, zscore_bbu, zscore_tbu])
        y.append(is_stunting)
    
    return np.array(X), np.array(y)

# Instance global model (akan diload saat startup)
knn_model = StuntingKNNModel(n_neighbors=5)

def get_knn_model() -> StuntingKNNModel:
    """
    Dependency untuk mendapatkan model KNN
    """
    return knn_model
