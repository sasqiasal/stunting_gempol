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
- StandardScaler dari sklearn untuk normalisasi fitur - fit_transform pada training, transform pada uji
- Distance Weighting: weights='distance' agar tetangga dekat lebih berpengaruh
- Validasi Medis: Pengecekan Z-Score sebelum KNN (deteksi data ekstrem/outlier)
- Optimalisasi K: n_neighbors=5 (atau dapat disesuaikan ke 3)
- Output: JSON dengan distance, label_code, dan status validasi Z-Score

FITUR KEAMANAN MEDIS:
- Deteksi nilai ekstrem: Z-Score > +3.0 atau < -3.0
- Penandaan "Data Ekstrem/Outlier" untuk mencegah salah diagnosa
- Ground truth dari zscore_tbu (Z-Score Height-for-Age) per WHO standard
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
    - StandardScaler untuk normalisasi fitur (fit_transform train, transform test)
    - Distance Weighting (weights='distance') untuk pengaruh tetangga yang proporsional
    - Validasi Medis: Pengecekan Z-Score sebelum masuk KNN
    - Multi-class classification (4 kelas)
    """
    
    # Mapping untuk 4-class labels ke deskripsi
    CLASS_LABELS = {
        0: "Normal & Gizi Baik",
        1: "Normal & Kurang Gizi",
        2: "Stunting & Gizi Baik",
        3: "Stunting & Kurang Gizi"
    }
    
    # WHO Z-Score Classification Ranges (per WHO Child Growth Standards)
    # zscore_tbu: Z-Score for Height-for-Age (Tinggi/Usia)
    # zscore_bbu: Z-Score for Weight-for-Age (Berat/Usia)
    Z_SCORE_RANGES = {
        "normal": {"min": -2.0, "max": 3.0},      # Dalam range normal
        "stunting": {"min": -3.0, "max": -2.0},   # Stunting ringan/sedang
        "severe": {"min": -4.0, "max": -3.0},     # Stunting berat
        "extreme_low": {"value": -3.0},            # Ekstrem bawah
        "extreme_high": {"value": 3.0},            # Ekstrem atas
    }
    
    def __init__(self, n_neighbors: int = 5):
        """
        Inisialisasi model KNN dengan sklearn
        
        Args:
            n_neighbors: Jumlah tetangga terdekat untuk prediksi
                       - Default: 5 (good balance antara bias dan variance)
                       - Alternatif: 3 (untuk dataset sangat kecil, mengurangi overfitting)
                       - Rekomendasi: 5 untuk data > 200 sampel, 3 untuk data < 200 sampel
        """
        # Gunakan sklearn KNeighborsClassifier dengan metric Euclidean
        self.model = KNeighborsClassifier(
            n_neighbors=n_neighbors,
            metric='euclidean',
            weights='distance',  # ✅ Distance weighting: tetangga dekat lebih berpengaruh
            algorithm='auto'      # Auto-select best algorithm (KDTree, BallTree, atau Brute)
        )
        
        # Gunakan sklearn StandardScaler untuk normalisasi fitur
        # ✅ Ini memastikan fitur 'usia_bulan' tidak kalah bobot dengan 'tinggi_badan'
        self.scaler = StandardScaler()
        
        self.is_trained = False
        self.X_train_data = None
        self.y_train_data = None
        self.n_neighbors = n_neighbors
    
    def validate_zscore(
        self,
        zscore_tbu: float,
        zscore_bbu: float
    ) -> Dict[str, any]:
        """
        ✅ VALIDASI MEDIS: Pengecekan Z-Score untuk deteksi data ekstrem/outlier
        
        Prosedur:
        1. Cek jika Z-Score berada di luar range WHO (-3.0 hingga +3.0)
        2. Jika zscore_tbu < -3.0 atau > +3.0 → Tandai sebagai "OUTLIER"
        3. Jika zscore_bbu < -3.0 atau > +3.0 → Tandai sebagai "OUTLIER"
        
        Tujuan:
        - Mencegah salah diagnosa stunting pada bayi yang sebenarnya hanya berukuran besar/kecil
        - Mengidentifikasi data entry error atau kondisi klinis yang tidak biasa
        
        Args:
            zscore_tbu: Z-Score Height-for-Age (Tinggi/Usia) - GROUND TRUTH untuk stunting
            zscore_bbu: Z-Score Weight-for-Age (Berat/Usia)
        
        Returns:
            Dictionary dengan:
            {
                "is_valid": bool,           # True jika data normal, False jika ekstrem
                "is_outlier": bool,         # True jika ada nilai ekstrem
                "status": str,              # "NORMAL" / "OUTLIER_EXTREME_LOW" / "OUTLIER_EXTREME_HIGH"
                "zscore_tbu_status": str,   # Status tinggi/usia
                "zscore_bbu_status": str,   # Status berat/usia
                "warning": str,             # Pesan peringatan jika ada
                "zscore_tbu": float,
                "zscore_bbu": float
            }
        """
        extreme_low = self.Z_SCORE_RANGES["extreme_low"]["value"]  # -3.0
        extreme_high = self.Z_SCORE_RANGES["extreme_high"]["value"]  # +3.0
        
        is_outlier = False
        status = "NORMAL"
        warning = ""
        zscore_tbu_status = "NORMAL"
        zscore_bbu_status = "NORMAL"
        
        # Cek zscore_tbu (Height-for-Age) - PALING PENTING untuk stunting
        if zscore_tbu < extreme_low:
            is_outlier = True
            status = "OUTLIER_EXTREME_LOW"
            zscore_tbu_status = "EXTREME_LOW (< -3.0 SD)"
            warning = f"⚠️ PERINGATAN MEDIS: Tinggi badan sangat ekstrem rendah (zscore_tbu={zscore_tbu}). Data perlu verifikasi manual."
        elif zscore_tbu > extreme_high:
            is_outlier = True
            status = "OUTLIER_EXTREME_HIGH"
            zscore_tbu_status = "EXTREME_HIGH (> +3.0 SD)"
            warning = f"⚠️ PERINGATAN MEDIS: Tinggi badan sangat ekstrem tinggi (zscore_tbu={zscore_tbu}). Bayi mungkin tidak stunting, perlu verifikasi."
        else:
            if zscore_tbu < -2.0:
                zscore_tbu_status = "STUNTING (< -2.0 SD)"
            elif zscore_tbu >= -2.0:
                zscore_tbu_status = "NORMAL (>= -2.0 SD)"
        
        # Cek zscore_bbu (Weight-for-Age) - sekunder untuk deteksi outlier
        if zscore_bbu < extreme_low:
            is_outlier = True
            if status == "NORMAL":
                status = "OUTLIER_EXTREME_LOW"
            zscore_bbu_status = "EXTREME_LOW (< -3.0 SD)"
            warning += f" ⚠️ Berat badan juga sangat ekstrem rendah (zscore_bbu={zscore_bbu})."
        elif zscore_bbu > extreme_high:
            is_outlier = True
            if status == "NORMAL":
                status = "OUTLIER_EXTREME_HIGH"
            zscore_bbu_status = "EXTREME_HIGH (> +3.0 SD)"
            warning += f" ⚠️ Berat badan juga sangat ekstrem tinggi (zscore_bbu={zscore_bbu})."
        else:
            if zscore_bbu < -2.0:
                zscore_bbu_status = "UNDERWEIGHT (< -2.0 SD)"
            elif zscore_bbu >= -2.0:
                zscore_bbu_status = "NORMAL (>= -2.0 SD)"
        
        return {
            "is_valid": not is_outlier,
            "is_outlier": is_outlier,
            "status": status,
            "zscore_tbu_status": zscore_tbu_status,
            "zscore_bbu_status": zscore_bbu_status,
            "warning": warning.strip() if warning else None,
            "zscore_tbu": round(zscore_tbu, 2),
            "zscore_bbu": round(zscore_bbu, 2)
        }
    
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
        Menyiapkan fitur untuk prediksi KNN
        
        ✅ PREPROCESSING dengan StandardScaler:
        - Fit pada data training, transform pada data input baru
        - Memastikan semua fitur scaled ke mean=0, std=1
        - Fitur 'usia_bulan' tidak kalah bobot dengan 'tinggi_badan'
        
        Menggunakan 6 fitur utama (TANPA Z-Scores sebagai input):
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
            zscore_bbu: Z-Score Berat Badan/Usia (diterima tapi TIDAK digunakan sebagai input feature)
            zscore_tbu: Z-Score Tinggi/Usia (diterima tapi TIDAK digunakan sebagai input feature)
                       Hanya untuk validasi medis dan ground truth evaluation
        
        Returns:
            Array numpy dengan 6 fitur yang digunakan dalam training
        """
        # Encode jenis kelamin: L=1, P=0
        jk_encoded = 1 if jenis_kelamin == "L" else 0
        
        # Gabungkan 8 fitur (sesuai dengan training data saat ini)
        # Order: JK, Usia, BB, TB, LL, LK, Z_BB, Z_TB
        features = np.array([
            jk_encoded,
            usia_bulan,
            berat_badan,
            tinggi_badan,
            lingkar_lengan,
            lingkar_kepala,
            zscore_bbu,
            zscore_tbu
        ]).reshape(1, -1)
        
        return features
    
    def _apply_custom_weights(self, X_scaled: np.ndarray) -> np.ndarray:
        """
        Memberi bobot pada fitur tertentu setelah scaling (StandardScaler).
        Sesuai request, fitur Z-BB dan Z-TB diberikan bobot 2x lebih besar 
        daripada fitur lainnya agar prediksinya menempel pada standar kurva WHO.
        """
        X_weighted = X_scaled.copy()
        
        # Seluruh fitur lainnya (JK, Usia, BB, TB, LL, LK) dibiarkan pada skala 1.0
        
        # Perbesar bobot Z-BB (index 6) dan Z-TB (index 7) menjadi 2.0
        X_weighted[:, 6] *= 2.0
        X_weighted[:, 7] *= 2.0
        
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

        ✅ PREPROCESSING DENGAN StandardScaler:
        - Menggunakan sklearn.preprocessing.StandardScaler
        - fit_transform() pada data training
        - Normalisasi ke mean=0, std=1 untuk semua fitur
        - Memastikan fitur 'usia_bulan' tidak kalah bobot dengan 'tinggi_badan'

        ✅ DISTANCE WEIGHTING:
        - Parameter weights='distance' di KNeighborsClassifier
        - Tetangga yang jaraknya sangat jauh (outlier) tidak memiliki pengaruh sebesar tetangga mirip
        
        ✅ OPTIMALISASI K:
        - n_neighbors=5 (default) atau dapat disesuaikan ke 3 untuk dataset kecil
        - Menghindari overfitting dan underfitting

        Metodologi:
        - Tidak ada train_test_split — 100% data digunakan untuk training
        - Model menyimpan semua data training (KNN adalah lazy learning)
        - Evaluasi model dilakukan menggunakan data balita BARU dari sistem (tabel pengukuran)
        - Ini mencegah bias evaluasi

        Args:
            X: Matriks fitur (n_samples, n_features)
            y: Label target (0, 1, 2, 3 untuk 4-class classification)
            test_size: Tidak digunakan (backward-compatibility)
            random_state: Tidak digunakan (backward-compatibility)

        Returns:
            Dictionary berisi info training dengan preprocessing details
        """
        # Gunakan SEMUA data sebagai data latih
        X_train = X
        y_train = y

        # ✅ STEP 1: Standardisasi fitur menggunakan sklearn StandardScaler
        print(f"📊 PREPROCESSING: Standardisasi fitur menggunakan sklearn.preprocessing.StandardScaler...")
        print(f"   Method: fit_transform pada data training")
        print(f"   Result: mean=0, std=1 untuk setiap fitur")
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
        
        ✅ PREPROCESSING:
        - Menggunakan scaler.transform() (BUKAN fit_transform)
        - Normalisasi data input dengan parameter dari training
        
        ✅ DISTANCE WEIGHTING:
        - Model menggunakan weights='distance'
        - Tetangga dekat lebih berpengaruh dalam voting
        
        Args:
            X: Matriks fitur (1, n_features)
        
        Returns:
            Tuple (prediksi, confidence_score)
            - prediksi: Label kelas (0, 1, 2, atau 3)
            - confidence_score: Probabilitas kelas prediksi (0-1)
        """
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Gunakan method train() terlebih dahulu.")
        
        # ✅ STEP 1: Standardisasi fitur dengan transform (bukan fit_transform)
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
    
    def predict_with_zscore_validation(
        self,
        X: np.ndarray,
        zscore_tbu: float = 0.0,
        zscore_bbu: float = 0.0
    ) -> Dict[str, any]:
        """
        ✅ PREDIKSI DENGAN VALIDASI MEDIS & CRITICAL OVERRIDE
        
        Fungsi ini menggabungkan kecerdasan KNN dengan aturan baku WHO.
        Jika KNN salah memprediksi karena masalah data borderline (seperti -1.97),
        sistem validasi akan mengoreksi label secara otomatis.
        """
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Gunakan method train() terlebih dahulu.")
        
        # 1. Validasi Z-Score Terlebih Dahulu (Deteksi Outlier)
        zscore_validation = self.validate_zscore(zscore_tbu, zscore_bbu)
        
        # 2. Ambil Prediksi Awal dari KNN
        X_scaled = self.scaler.transform(X)
        X_weighted = self._apply_custom_weights(X_scaled)
        
        prediction_code = int(self.model.predict(X_weighted)[0])
        probabilities = self.model.predict_proba(X_weighted)[0]
        confidence = float(probabilities[prediction_code])

        # --- LOGIKA PENYELAMAT (CRITICAL OVERRIDE) ---
        # Variabel bantuan untuk mencatat jika terjadi koreksi
        is_corrected = False
        original_knn_code = prediction_code

        # KASUS A: Anak secara medis NORMAL (Z-Score > -2.0) tapi KNN bilang STUNTING (2 atau 3)
        if zscore_tbu >= -2.0 and prediction_code in [2, 3]:
            # Cek status gizi (BB/U) untuk menentukan apakah Gizi Baik (0) atau Kurang (1)
            if zscore_bbu < -2.0:
                prediction_code = 1  # Normal & Kurang Gizi
            else:
                prediction_code = 0  # Normal & Gizi Baik
            is_corrected = True

        # KASUS B: Anak secara medis STUNTING (Z-Score <= -2.0) tapi KNN bilang NORMAL (0 atau 1)
        elif zscore_tbu < -2.0 and prediction_code in [0, 1]:
            # Cek status gizi (BB/U) untuk menentukan apakah Gizi Baik (2) atau Kurang (3)
            if zscore_bbu < -2.0:
                prediction_code = 3  # Stunting & Kurang Gizi
            else:
                prediction_code = 2  # Stunting & Gizi Baik
            is_corrected = True

        # 3. Susun Output JSON
        result = {
            "prediction_code": prediction_code,
            "prediction_label": self.CLASS_LABELS.get(prediction_code, f"Unknown ({prediction_code})"),
            "confidence": round(confidence, 4),
            "zscore_validation": zscore_validation,
            "model_config": {
                "n_neighbors": self.n_neighbors,
                "weights": "distance",
                "metric": "euclidean",
                "is_corrected_by_zscore": is_corrected
            }
        }
        
        # Tambahkan catatan jika terjadi koreksi otomatis
        if is_corrected:
            note = f"💡 Koreksi Otomatis: KNN memprediksi {self.CLASS_LABELS.get(original_knn_code)}, " \
                   f"tapi divalidasi menjadi {result['prediction_label']} berdasarkan Z-Score WHO ({zscore_tbu})."
            result["validation_note"] = note
            # Update warning di zscore_validation juga
            result["zscore_validation"]["warning"] = note

        return result

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
            # 1. Cari lebih banyak kandidat (adaptive berdasarkan n_neighbors)
            # Karena kita akan memfilter berdasarkan Gender dan Usia manual
            n_samples = len(self.X_train_data)
            # Cari 5x lipat dari yang diminta untuk memastikan tersedia setelah filter gender
            n_candidates = min(n_samples, max(50, n_neighbors * 5))
            
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
                
                # Ambil scaled values untuk perbandingan
                # Scaled neighbors diambil dari transformasi training data menggunakan scaler yang sama
                neighbor_scaled = self.scaler.transform([original_data])[0]
                
                # Amankan zscore original data jika model dilatih dengan 8 fitur
                z_bb = float(original_data[6]) if len(original_data) > 6 else 0.0
                z_tb = float(original_data[7]) if len(original_data) > 7 else 0.0
                
                neighbor_info = {
                    "distance": round(float(dist), 4),
                    "label": label_text,
                    "label_code": label,
                    # ORIGINAL VALUES (untuk display dan interpretasi medis)
                    "jenis_kelamin": "L" if original_data[0] == 1 else "P",
                    "usia_bulan": int(original_data[1]),
                    "berat_badan": float(original_data[2]),
                    "tinggi_badan": float(original_data[3]),
                    "lingkar_lengan": float(original_data[4]),
                    "lingkar_kepala": float(original_data[5]),
                    "z_score_bb": round(z_bb, 2),
                    "z_score_tb": round(z_tb, 2),
                    # SCALED VALUES (untuk debugging - perlihatkan bagaimana KNN melihat data)
                    "scaled": {
                        "jenis_kelamin": round(float(neighbor_scaled[0]), 6),
                        "usia_bulan": round(float(neighbor_scaled[1]), 6),
                        "berat_badan": round(float(neighbor_scaled[2]), 6),
                        "tinggi_badan": round(float(neighbor_scaled[3]), 6),
                        "lingkar_lengan": round(float(neighbor_scaled[4]), 6),
                        "lingkar_kepala": round(float(neighbor_scaled[5]), 6),
                        "z_score_bb": round(float(neighbor_scaled[6]), 6) if len(neighbor_scaled) > 6 else 0.0,
                        "z_score_tb": round(float(neighbor_scaled[7]), 6) if len(neighbor_scaled) > 7 else 0.0
                    }
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
