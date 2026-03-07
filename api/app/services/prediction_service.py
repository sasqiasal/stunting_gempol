"""
Service untuk Prediksi Stunting
Menggabungkan kalkulasi Z-Score dengan prediksi model KNN
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

class PredictionService:
    """
    Service untuk melakukan prediksi stunting
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
        Melakukan prediksi stunting lengkap dengan Z-Score dan model KNN
        
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
            - status_gizi: Status gizi berdasarkan Z-Score
            - prediksi_stunting: Boolean hasil prediksi model
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
        
        # 4. Prediksi menggunakan model KNN (PRIMARY - dari 500 data training)
        nearest_neighbors = []
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
            
            # Prediksi (model mengembalikan 0, 1, 3, atau 4 dari 500 data training)
            prediction, confidence = model.predict(features)
            confidence_score = confidence

            # Cari tetangga terdekat (Interpretability)
            nearest_neighbors = model.find_nearest_neighbors(features, n_neighbors=5)
            
            # DEBUG: Log prediction details
            print(f" PREDICTION DEBUG:")
            print(f"   Input: JK={jenis_kelamin}, Usia={usia_bulan}bln, TB={tinggi_badan}cm, BB={berat_badan}kg")
            print(f"   Z-Scores: BB/U={zscore_bbu:.2f}, TB/U={zscore_tbu:.2f}")
            print(f"   Model Prediction (dari 500 data): {prediction}")
            print(f"   Confidence: {confidence_score:.2%}")
            
            if nearest_neighbors:
                print(f"   Nearest Neighbors (k=5):")
                for i, n in enumerate(nearest_neighbors):
                    print(f"     {i+1}. Dist: {n['distance']:.4f} - {n['label']} (Usia: {n['usia_bulan']} bln, TB: {n['tinggi_badan']} cm, BB: {n['berat_badan']} kg)")
            
            # Mapping dari 4 kelas ke Status Gizi (BERDASAR DATA LATIH):
            # 0 = Normal + Gizi Baik
            # 1 = Normal + Kurang Gizi
            # 3 = Stunting + Gizi Baik
            # 4 = Stunting + Kurang Gizi
            
            # Prediksi Stunting: 3 atau 4 = Stunting
            prediksi_stunting = bool(prediction in [3, 4])
            
            # Status Gizi dari model (4 kategori dari data training)
            if prediction == 0:
                status_gizi = "Normal + Gizi Baik"
            elif prediction == 1:
                status_gizi = "Normal + Kurang Gizi"
            elif prediction == 3:
                status_gizi = "Stunting + Gizi Baik"
            else:  # prediction == 4
                status_gizi = "Stunting + Kurang Gizi"
            
            print(f"   ✅ Status Gizi (dari model): {status_gizi}")
            
        except Exception as e:
            # Jika model belum dilatih, gunakan Z-Score saja
            print(f"⚠️ Model prediction failed: {e}. Using Z-Score fallback.")
            prediksi_stunting = is_stunting_zscore
            confidence_score = 1.0 if is_stunting_zscore else 0.9
            status_gizi = status_gizi_zscore
            # status_gizi sudah di-set dari determine_nutrition_status()
        
        # 5. Return hasil - Convert semua ke native Python types untuk JSON serialization
        return {
            "zscore_bbu": float(zscore_bbu),
            "zscore_tbu": float(zscore_tbu),
            "status_gizi": str(status_gizi),
            "prediksi_stunting": bool(prediksi_stunting),
            "confidence_score": float(confidence_score),
            "is_stunting_zscore": bool(is_stunting_zscore),
            "tanggal_prediksi": datetime.now(),
            "nearest_neighbors": nearest_neighbors
        }

# Instance global
prediction_service = PredictionService()
