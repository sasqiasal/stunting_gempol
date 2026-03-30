"""
Service untuk Prediksi Stunting
Menggabungkan kalkulasi Z-Score dengan prediksi model KNN (4 Kelas)

Label Klasifikasi (4 Kelas):
- 0: Normal + Gizi Baik
- 1: Normal + Kurang Gizi
- 2: Stunting + Gizi Baik
- 3: Stunting + Kurang Gizi
"""

from typing import Dict, Literal
from datetime import datetime
from app.utils.zscore_calculator import (
    calculate_zscore_bbu,
    calculate_zscore_tbu,
    determine_nutrition_status,
    is_stunting
)
from app.ml.knn_model import get_knn_model

# Mapping label integer ke deskripsi 4 kelas
CLASSIFICATION_MAPPING = {
    0: "Normal + Gizi Baik",
    1: "Normal + Kurang Gizi",
    2: "Stunting + Gizi Baik",
    3: "Stunting + Kurang Gizi"
}

class PredictionService:
    """
    Service untuk melakukan prediksi stunting dengan 4 kelas klasifikasi
    """
    
    @staticmethod
    def predict_stunting(
        jenis_kelamin: Literal["L", "P"],
        usia_bulan: int,
        tinggi_badan: float,
        berat_badan: float,
        lingkar_lengan: float,
        lingkar_kepala: float
    ) -> Dict:
        """
        Melakukan prediksi stunting lengkap dengan Z-Score dan model KNN (4 kelas)
        
        Args:
            jenis_kelamin: L untuk laki-laki, P untuk perempuan
            usia_bulan: Usia dalam bulan
            tinggi_badan: Tinggi badan dalam cm
            berat_badan: Berat badan dalam kg
            lingkar_lengan: Lingkar lengan atas dalam cm
            lingkar_kepala: Lingkar kepala dalam cm
        
        Returns:
            Dictionary berisi:
            - zscore_bbu: Z-Score Berat Badan/Usia
            - zscore_tbu: Z-Score Tinggi Badan/Usia
            - status_gizi: Status gizi 4 kelas (Normal+Baik, Normal+Kurang, Stunting+Baik, Stunting+Kurang)
            - status_gizi_label: Label integer (0, 1, 2, 3)
            - confidence_score: Confidence score dari model
            - is_stunting_zscore: Boolean stunting berdasarkan Z-Score saja
        """
        # 1. Hitung Z-Score BB/U dan TB/U
        zscore_bbu = calculate_zscore_bbu(berat_badan, usia_bulan, jenis_kelamin)
        zscore_tbu = calculate_zscore_tbu(tinggi_badan, usia_bulan, jenis_kelamin)
        
        # 2. Tentukan status gizi berdasarkan Z-Score (fallback only)
        status_gizi_zscore = determine_nutrition_status(zscore_bbu, zscore_tbu)
        
        # 3. Cek stunting berdasarkan Z-Score saja
        is_stunting_zscore = is_stunting(zscore_tbu)
        
        # 4. Prediksi menggunakan model KNN (PRIMARY - 4 kelas dari 500 data training)
        nearest_neighbors = []
        status_gizi = "Normal + Gizi Baik"  # default
        status_gizi_label = 0  # default
        confidence_score = 0.0
        
        try:
            model = get_knn_model()
            
            # Siapkan fitur
            features = model.prepare_features(
                jenis_kelamin=jenis_kelamin,
                usia_bulan=usia_bulan,
                tinggi_badan=tinggi_badan,
                berat_badan=berat_badan,
                lingkar_lengan=lingkar_lengan,
                lingkar_kepala=lingkar_kepala,
                zscore_bbu=zscore_bbu,
                zscore_tbu=zscore_tbu
            )
            
            # ========================================
            # STEP 1: PREDIKSI MENGGUNAKAN K=5
            # (Model KNN internal menggunakan k=5 untuk klasifikasi)
            # ========================================
            prediction, confidence = model.predict(features)
            confidence_score = confidence
            status_gizi_label = int(prediction)
            
            # Map label integer ke deskripsi 4 kelas
            status_gizi = CLASSIFICATION_MAPPING.get(status_gizi_label, "Unknown")

            # ========================================
            # STEP 2: CARI 10 TETANGGA UNTUK DISPLAY
            # (Disimpan di database untuk fleksibilitas UI)
            # ========================================
            nearest_neighbors = model.find_nearest_neighbors(features, n_neighbors=10)
            
            # DEBUG: Log prediction details
            print(f"[DEBUG] PREDICTION:")
            print(f"   Input: JK={jenis_kelamin}, Usia={usia_bulan}bln, TB={tinggi_badan}cm, BB={berat_badan}kg")
            print(f"   Z-Scores: BB/U={zscore_bbu:.2f}, TB/U={zscore_tbu:.2f}")
            print(f"   Model Prediction (4 kelas, K=5): Label {prediction} = {status_gizi}")
            print(f"   Confidence: {confidence_score:.2%}")
            
            if nearest_neighbors:
                print(f"   Nearest Neighbors untuk display (k={len(nearest_neighbors)}):")
                for i, n in enumerate(nearest_neighbors):
                    print(f"     {i+1}. Dist: {n['distance']:.4f} - {n['label']} (Usia: {n['usia_bulan']} bln, TB: {n['tinggi_badan']} cm, BB: {n['berat_badan']} kg)")
            
            print(f"   [OK] Status Gizi (4 Kelas, K=5): {status_gizi}")
            
        except Exception as e:
            # Jika model belum dilatih, gunakan Z-Score saja
            print(f"[WARNING] Model prediction failed: {e}. Using Z-Score fallback.")
            status_gizi = status_gizi_zscore
            status_gizi_label = 0 if not is_stunting_zscore else 2  # Assume good nutrition if fallback
            confidence_score = 0.0
        
        # 5. Return hasil - Convert semua ke native Python types untuk JSON serialization
        return {
            "zscore_bbu": float(zscore_bbu),
            "zscore_tbu": float(zscore_tbu),
            "status_gizi": str(status_gizi),
            "status_gizi_label": int(status_gizi_label),
            "confidence_score": float(confidence_score),
            "is_stunting_zscore": bool(is_stunting_zscore),
            "tanggal_prediksi": datetime.now(),
            "nearest_neighbors": nearest_neighbors
        }

# Instance global
prediction_service = PredictionService()
