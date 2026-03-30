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
        
        # 3. Cek stunting berdasarkan Z-Score saja (-2 atau kurang dianggap stunting)
        is_stunting_zscore = zscore_tbu < -2
        
        # 4. Prediksi menggunakan model KNN (PRIMARY - dari 500 data training)
        nearest_neighbors = []
        try:
            model = get_knn_model()
            
            # Siapkan fitur (sekarang termasuk z-score)
            features = model.prepare_features(
                jenis_kelamin=jenis_kelamin,
                usia_bulan=usia_bulan,
                berat_badan=berat_badan,
                tinggi_badan=tinggi_badan,
                lingkar_lengan=lingkar_lengan,
                lingkar_kepala=lingkar_kepala,
                zscore_bbu=zscore_bbu,
                zscore_tbu=zscore_tbu
            )
            
            print(f"\n--- DEBUG PREDIKSI ---")
            print(f"Input features: {features}")
            print("----------------------\n")
            
            # ========================================
            # STEP 1: PREDIKSI MENGGUNAKAN K=5
            # (Model KNN internal menggunakan k=5 untuk klasifikasi)
            # ========================================
            prediction, confidence = model.predict(features)
            confidence_score = confidence
            
            print(f" PREDICTION DEBUG:")
            print(f"   Input: JK={jenis_kelamin}, Usia={usia_bulan}bln, TB={tinggi_badan}cm, BB={berat_badan}kg")
            print(f"   Z-Scores: BB/U={zscore_bbu:.2f}, TB/U={zscore_tbu:.2f}")
            print(f"   Model Prediction (4-class: 0-3, K=5): {prediction}")
            print(f"   Confidence: {confidence_score:.2%}")
            
            # ========================================
            # STEP 2: CARI 10 TETANGGA UNTUK DISPLAY
            # (Disimpan di database untuk fleksibilitas UI)
            # ========================================
            nearest_neighbors = model.find_nearest_neighbors(features, n_neighbors=10)
            
            if nearest_neighbors:
                print(f"   === DEBUGGING PREDIKSI: DATA DATASET ===")
                try:
                    print(f"   [!] Jumlah training terbaca: {len(model.X_train_data) if model.X_train_data is not None else 0}")
                    if model.X_train_data is not None and len(model.X_train_data) >= 5:
                        print(f"   [!] 5 Baris Pertama Dataset Fitur:")
                        for idx_5 in range(5):
                            print(f"       {model.X_train_data[idx_5].tolist()} -> Label: {model.y_train_data[idx_5]}")
                except Exception as eval_e:
                    print(f"       Could not read training data stats: {eval_e}")
                    
                print(f"   [!] Data Input ORIGINAL : {features.tolist()}")
                
                # Tampilkan scaled input juga untuk perbandingan
                try:
                    features_scaled = model.scaler.transform(features).tolist()[0]
                    print(f"   [!] Data Input SCALED : {[round(x, 6) for x in features_scaled]}")
                except:
                    pass
                    
                print(f"   [!] Fitur yang digunakan untuk perhitungan distance: [jenis_kelamin, usia_bulan, berat_badan, tinggi_badan, lingkar_lengan, lingkar_kepala]")
                print(f"   [!] Nearest Neighbors untuk display (k={len(nearest_neighbors)}):")
                for i, n in enumerate(nearest_neighbors):
                    print(f"     {i+1}. Dist: {n['distance']:.4f} - {n['label']} - JK:{n['jenis_kelamin']} - Usia:{n['usia_bulan']}bln - TB:{n['tinggi_badan']}cm - BB:{n['berat_badan']}kg")
                    if 'scaled' in n:
                        scaled_vals = n['scaled']
                        print(f"        (Scaled) JK:{scaled_vals['jenis_kelamin']:.6f} - Usia:{scaled_vals['usia_bulan']:.6f} - BB:{scaled_vals['berat_badan']:.6f} - TB:{scaled_vals['tinggi_badan']:.6f}")
            
            # 4-class prediction: 0=Normal+Baik, 1=Normal+Kurang, 2=Stunting+Baik, 3=Stunting+Kurang
            prediksi_stunting = int(prediction)  # Keep 0-3 numeric value
            
            # Map 4-class to descriptive status
            class_to_status = {
                0: "Normal + Gizi Baik",
                1: "Normal + Kurang Gizi",
                2: "Stunting + Gizi Baik",
                3: "Stunting + Kurang Gizi"
            }
            status_gizi = class_to_status.get(int(prediction), "Unknown")
            
            print(f"   ✅ Klasifikasi (dari model K=5): {status_gizi}")
            
        except Exception as e:
            # Jika model belum dilatih, gunakan Z-Score saja
            print(f"⚠️ Model prediction failed: {e}. Using Z-Score fallback.")
            # Map Z-score fallback to 4-class
            is_stunting = zscore_tbu < -2
            is_kurang_gizi = zscore_bbu < -2
            prediksi_stunting = (2 if is_stunting else 0) + (1 if is_kurang_gizi else 0)  # 0-3
            confidence_score = 1.0 if (is_stunting or is_kurang_gizi) else 0.9
            
            class_to_status = {
                0: "Normal + Gizi Baik",
                1: "Normal + Kurang Gizi",
                2: "Stunting + Gizi Baik",
                3: "Stunting + Kurang Gizi"
            }
            status_gizi = class_to_status.get(prediksi_stunting, "Unknown")
        
        # 5. Return hasil - Convert semua ke native Python types untuk JSON serialization
        return {
            "zscore_bbu": float(zscore_bbu),
            "zscore_tbu": float(zscore_tbu),
            "status_gizi": str(status_gizi),
            "prediksi_stunting": int(prediksi_stunting),  # Return 0-3 numeric, not boolean
            "confidence_score": float(confidence_score),
            "is_stunting_zscore": bool(is_stunting_zscore),
            "tanggal_prediksi": datetime.now(),
            "nearest_neighbors": nearest_neighbors
        }

# Instance global
prediction_service = PredictionService()
