"""
Routes untuk Evaluasi Kinerja Model KNN
Endpoint untuk menguji akurasi model dengan data training
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel
from app.utils.auth import get_current_user
from app.database import get_supabase
from app.ml.knn_model import get_knn_model, StuntingKNNModel
from app.services.prediction_service import prediction_service
from sklearn.metrics import (
    confusion_matrix, 
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score
)
import numpy as np
import os
import pandas as pd

router = APIRouter(prefix="/evaluasi", tags=["Evaluasi Model"])

class SimulationInput(BaseModel):
    jenis_kelamin: Literal["L", "P"]
    usia_bulan: int
    tinggi_badan: float
    berat_badan: float
    lingkar_lengan: float
    lingkar_kepala: float


@router.get("/model-performance", response_model=Dict[str, Any])
async def evaluate_model_performance(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase),
    model: StuntingKNNModel = Depends(get_knn_model)
):
    """
    Evaluasi kinerja model KNN dengan data training dari database
    
    Menghitung:
    - Confusion Matrix (TP, TN, FP, FN)
    - Akurasi
    - Presisi (Precision)
    - Recall (Sensitivity)
    - F1-Score
    
    Dapat diakses oleh: Admin dan Kader
    """
    # Validasi role (admin dan kader bisa akses)
    if current_user.get("role") not in ["admin", "kader"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin dan Kader yang dapat mengakses evaluasi model"
        )
    
    # Cek apakah model sudah dilatih
    if not model.is_trained:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model belum dilatih."
        )
    
    try:
        y_true = []
        y_pred = []
        total_samples = 0
        using_real_data = True
        X_test = np.array([])

        # ------------------------------------------------------------------
        # EVALUASI YANG BENAR: MENGGUNAKAN DATA PENGUKURAN (DATA UJI)
        # ------------------------------------------------------------------
        # PRINSIP EVALUASI MODEL:
        # 1. Model dilatih dengan data_latih_stunting.csv (DATA TRAIN)
        # 2. Model diuji dengan data pengukuran baru (DATA TEST)
        # 3. Ground truth: z-score TB/U dari pengukuran (< -2 = stunting)
        # 4. Prediksi: Hasil klasifikasi KNN terhadap data pengukuran
        # ------------------------------------------------------------------
        
        print("=" * 80)
        print("📊 EVALUASI MODEL KNN - MENGGUNAKAN DATA PENGUKURAN (DATA UJI)")
        print("=" * 80)
        
        # Ambil data pengukuran yang valid (punya zscore_tbu)
        test_data_response = supabase_client.table("pengukuran")\
            .select("*, balita(jenis_kelamin)")\
            .not_.is_("zscore_tbu", "null")\
            .not_.is_("zscore_bbu", "null")\
            .execute()
        
        if not test_data_response.data or len(test_data_response.data) < 1:
            print("⚠️ Belum ada data pengukuran")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Belum ada data pengukuran. Tambahkan data pengukuran terlebih dahulu."
            )
        
        test_data = test_data_response.data
        print(f"✅ Menggunakan {len(test_data)} data pengukuran sebagai DATA UJI")
        
        X_test_list = []
        
        for record in test_data:
            # ===================================
            # GROUND TRUTH: BERDASARKAN Z-SCORE TB/U
            # ===================================
            zscore_tbu = float(record.get("zscore_tbu", 0))
            
            # Standar WHO: z-score TB/U < -2 = stunting
            is_stunting_actual = 1 if zscore_tbu < -2 else 0
            y_true.append(is_stunting_actual)
            
            # ===================================
            # PREDIKSI: KLASIFIKASI KNN
            # ===================================
            # Ekstrak fitur untuk prediksi KNN
            balita_data = record.get("balita", {}) or {}
            jk = balita_data.get("jenis_kelamin", "L")
            jk_enc = 1 if str(jk).upper() == "L" else 0
            
            features = [
                jk_enc,
                float(record.get("usia_bulan", 0)),
                float(record.get("tinggi_badan", 0)),
                float(record.get("berat_badan", 0)),
                float(record.get("lingkar_lengan", 0)),
                float(record.get("lingkar_kepala", 0)),
                float(record.get("zscore_bbu", 0)),
                float(record.get("zscore_tbu", 0))
            ]
            X_test_list.append(features)
        
        # Lakukan prediksi KNN pada semua data uji
        X_test = np.array(X_test_list)
        X_test_scaled = model.scaler.transform(X_test)
        y_pred_raw = model.model.predict(X_test_scaled)
        
        # Konversi prediksi ke binary (0=normal, 1=stunting)
        # Konversi prediksi ke binary sesuai label mapping:
        # Status 3 (Stunting+GiziBaik) & 4 (Stunting+KurangGizi) → binary 1 (Stunting)
        # Status 0 (Normal+GiziBaik) & 1 (Normal+KurangGizi) → binary 0 (Non-Stunting)
        y_pred = np.array([1 if pred in [3, 4] else 0 for pred in y_pred_raw])
        
        total_samples = len(y_true)
        
        print(f"✅ Evaluasi selesai: {total_samples} sampel")
        print(f"   - Ground Truth dari: Z-score TB/U (< -2 = stunting)")
        print(f"   - Prediksi dari: Model KNN")

        # ------------------------------------------------------------------
        # HITUNG METRIK EVALUASI
        # ------------------------------------------------------------------
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Hitung Confusion Matrix (Binary: 0=Normal, 1=Stunting)
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        
        # Hitung metrik evaluasi
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        # Specificity = TN / (TN + FP)
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # Hitung distribusi data
        stunting_count = int(np.sum(y_true))
        normal_count = total_samples - stunting_count
        
        print("\n📊 HASIL EVALUASI:")
        print(f"   - Akurasi: {accuracy*100:.2f}%")
        print(f"   - Precision: {precision*100:.2f}%")
        print(f"   - Recall: {recall*100:.2f}%")
        print(f"   - Stunting (ground truth): {stunting_count}/{total_samples}")
        print("=" * 80)
        
        # --- SIMULASI NEIGHBORS (Menjawab kenapa hasilnya begitu) ---
        explanation_samples = []
        
        # 1. Coba ambil data REAL dari database (10 Terakhir)
        try:
            real_data_response = supabase_client.table("evaluasi_model_knn")\
                .select("*, pengukuran(id, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala, usia_bulan, zscore_bbu, zscore_tbu, prediksi_stunting, status_gizi, tanggal_pengukuran, balita(nama_lengkap, jenis_kelamin))")\
                .order("created_at", desc=True)\
                .limit(10)\
                .execute()
                
            if real_data_response.data and len(real_data_response.data) > 0:
                from sklearn.neighbors import KNeighborsClassifier

                # Build scaled training data once (reused for K=3,5,7,9)
                knn_train_variants = {}
                if model.X_train_data is not None and model.y_train_data is not None:
                    X_tr_scaled = model.scaler.transform(model.X_train_data).copy()
                    X_tr_scaled[:, 0] *= 5.0  # gender weight, sama seperti model utama
                    for k_val in [3, 5, 7, 9]:
                        knn_tmp = KNeighborsClassifier(n_neighbors=k_val, weights='distance', metric='euclidean')
                        knn_tmp.fit(X_tr_scaled, model.y_train_data)
                        knn_train_variants[k_val] = knn_tmp

                for item in real_data_response.data:
                    p = item.get("pengukuran", {}) or {}
                    b = p.get("balita", {}) or {}

                    pred = p.get("prediksi_stunting")
                    pred_str = "Stunting" if (pred is True or str(pred).lower() == "stunting") else "Normal"

                    # Build feature array for this record (for K=3/5/7 prediction)
                    jk_enc = 1 if str(b.get("jenis_kelamin", "L")).upper() == "L" else 0
                    features_raw = np.array([[
                        jk_enc,
                        float(p.get("usia_bulan", 0)),
                        float(p.get("tinggi_badan", 0)),
                        float(p.get("berat_badan", 0)),
                        float(p.get("lingkar_lengan") or 0),
                        float(p.get("lingkar_kepala") or 0),
                        float(p.get("zscore_bbu") or 0),
                        float(p.get("zscore_tbu") or 0),
                    ]])

                    # Compute k_results for K=3, K=5, K=7, K=9
                    k_results = []
                    for k_val in [3, 5, 7, 9]:
                        neighbors_k = model.find_nearest_neighbors(features_raw, n_neighbors=k_val)
                        k_pred_str = pred_str  # default fallback
                        if k_val in knn_train_variants:
                            X_te_scaled = model.scaler.transform(features_raw).copy()
                            X_te_scaled[:, 0] *= 5.0
                            pred_raw = knn_train_variants[k_val].predict(X_te_scaled)[0]
                            k_pred_str = "Stunting" if int(pred_raw) in [3, 4] else "Normal"
                        k_results.append({
                            "k": k_val,
                            "prediction": k_pred_str,
                            "neighbors": neighbors_k
                        })

                    explanation_samples.append({
                        "is_real_data": True,
                        "timestamp": p.get("tanggal_pengukuran"),
                        "input": {
                            "nama": b.get("nama_lengkap", "Balita"),
                            "jenis_kelamin": b.get("jenis_kelamin", "-"),
                            "usia_bulan": p.get("usia_bulan", 0),
                            "tinggi_badan": p.get("tinggi_badan", 0),
                            "berat_badan": p.get("berat_badan", 0),
                        },
                        "prediction": pred_str,
                        "actual": p.get("status_gizi", "-"),
                        "neighbors": item.get("nearest_neighbors", []),
                        "k_results": k_results
                    })
        except Exception as e:
            print(f"⚠️ Warning: Gagal mengambil data real evaluasi: {e}")
            # Lanjut ke fallback sample

        # 2. Jika tidak ada data real, gunakan data SAMPLE dari test set (pengukuran)
        if len(explanation_samples) == 0 and len(X_test) > 0:
            from sklearn.neighbors import KNeighborsClassifier

            # Bangun knn_train_variants lokal (untuk k_results per sample)
            fallback_knn_variants = {}
            if model.X_train_data is not None and model.y_train_data is not None:
                X_tr_sc = model.scaler.transform(model.X_train_data).copy()
                X_tr_sc[:, 0] *= 5.0  # gender weight
                for k_val in [3, 5, 7, 9]:
                    knn_tmp = KNeighborsClassifier(n_neighbors=k_val, weights='distance', metric='euclidean')
                    knn_tmp.fit(X_tr_sc, model.y_train_data)
                    fallback_knn_variants[k_val] = knn_tmp

            # Ambil max 3 sampel
            sample_indices = np.random.choice(len(X_test), size=min(3, len(X_test)), replace=False)
            
            for idx in sample_indices:
                feat = X_test[idx]
                feat_reshaped = feat.reshape(1, -1)

                true_lbl = int(y_true[idx])   # binary: 0 = Normal, 1 = Stunting
                pred_lbl = int(y_pred[idx])   # binary: 0 = Normal, 1 = Stunting

                true_status = "Stunting" if true_lbl == 1 else "Normal"
                pred_status = "Stunting" if pred_lbl == 1 else "Normal"

                # Hitung k_results untuk K=3,5,7,9
                k_results_fb = []
                for k_val in [3, 5, 7, 9]:
                    neighbors_k = model.find_nearest_neighbors(feat_reshaped, n_neighbors=k_val)
                    kp_str = pred_status  # fallback
                    if k_val in fallback_knn_variants:
                        X_te_sc = model.scaler.transform(feat_reshaped).copy()
                        X_te_sc[:, 0] *= 5.0
                        raw_p = fallback_knn_variants[k_val].predict(X_te_sc)[0]
                        kp_str = "Stunting" if int(raw_p) in [3, 4] else "Normal"
                    k_results_fb.append({"k": k_val, "prediction": kp_str, "neighbors": neighbors_k})
                
                explanation_samples.append({
                    "is_real_data": False,
                    "input": {
                        "jenis_kelamin": "L" if feat[0] == 1 else "P",
                        "usia_bulan": int(feat[1]),
                        "tinggi_badan": round(float(feat[2]), 2),
                        "berat_badan": round(float(feat[3]), 2),
                        "zscore_tbu": round(float(feat[7]), 2)
                    },
                    "prediction": pred_status,
                    "actual": true_status,
                    "is_correct": (true_status == pred_status),
                    "neighbors": model.find_nearest_neighbors(feat_reshaped, n_neighbors=5),
                    "k_results": k_results_fb
                })

        # Susun response
        evaluation_result = {
            "sample_explanations": explanation_samples,
            "status": "success",
            "message": "Evaluasi model berhasil",
            "data_source": "Data Pengukuran (Data Uji)",
            "evaluation_method": "Ground Truth: Z-score TB/U < -2 | Prediksi: Model KNN",
            "model_info": {
                "algorithm": "K-Nearest Neighbors (KNN)",
                "n_neighbors": model.model.n_neighbors,
                "total_features": 8,
                "feature_names": [
                    "Jenis Kelamin",
                    "Usia (bulan)",
                    "Tinggi Badan (cm)",
                    "Berat Badan (kg)",
                    "Lingkar Lengan (cm)",
                    "Lingkar Kepala (cm)",
                    "Z-Score BB/U",
                    "Z-Score TB/U"
                ]
            },
            "dataset_info": {
                "total_samples": total_samples,
                "normal_count": normal_count,
                "stunting_count": stunting_count,
                "normal_percentage": round((normal_count / total_samples) * 100, 2),
                "stunting_percentage": round((stunting_count / total_samples) * 100, 2),
                "data_source": "Data Pengukuran Baru (DB)",
                "training_note": "Model dilatih pada 500 data CSV (100%), diuji pada data pengukuran baru ini"
            },
            "confusion_matrix": {
                "true_positive": int(tp),
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "matrix": cm.tolist(),
                "labels": ["Normal", "Stunting"]
            },
            "metrics": {
                "accuracy": round(float(accuracy), 4),
                "precision": round(float(precision), 4),
                "recall": round(float(recall), 4),
                "specificity": round(float(specificity), 4),
                "f1_score": round(float(f1), 4),
                # Konversi ke persentase
                "accuracy_percentage": round(float(accuracy) * 100, 2),
                "precision_percentage": round(float(precision) * 100, 2),
                "recall_percentage": round(float(recall) * 100, 2),
                "specificity_percentage": round(float(specificity) * 100, 2),
                "f1_percentage": round(float(f1) * 100, 2)
            },
            "interpretation": {
                "accuracy": get_accuracy_interpretation(accuracy),
                "precision": get_precision_interpretation(precision),
                "recall": get_recall_interpretation(recall),
                "specificity": get_specificity_interpretation(specificity),
                "f1_score": get_f1_interpretation(f1)
            }
        }
        
        return evaluation_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat evaluasi model: {str(e)}"
        )

def get_accuracy_interpretation(accuracy: float) -> str:
    """Interpretasi nilai akurasi"""
    if accuracy >= 0.95:
        return "Sangat Baik - Model sangat akurat dalam prediksi"
    elif accuracy >= 0.90:
        return "Baik - Model memiliki akurasi tinggi"
    elif accuracy >= 0.80:
        return "Cukup Baik - Model cukup akurat untuk digunakan"
    elif accuracy >= 0.70:
        return "Sedang - Model perlu perbaikan"
    else:
        return "Kurang - Model perlu dilatih ulang dengan data lebih baik"

def get_precision_interpretation(precision: float) -> str:
    """Interpretasi nilai presisi"""
    if precision >= 0.95:
        return "Sangat Baik - Sangat sedikit false positive (salah deteksi stunting)"
    elif precision >= 0.90:
        return "Baik - Sedikit false positive"
    elif precision >= 0.80:
        return "Cukup Baik - Ada beberapa false positive"
    elif precision >= 0.70:
        return "Sedang - Cukup banyak false positive"
    else:
        return "Kurang - Banyak false positive, model terlalu sensitif"

def get_recall_interpretation(recall: float) -> str:
    """Interpretasi nilai recall (sensitivity)"""
    if recall >= 0.95:
        return "Sangat Baik - Hampir semua kasus stunting terdeteksi"
    elif recall >= 0.90:
        return "Baik - Sebagian besar kasus stunting terdeteksi"
    elif recall >= 0.80:
        return "Cukup Baik - Cukup banyak kasus stunting terdeteksi"
    elif recall >= 0.70:
        return "Sedang - Beberapa kasus stunting mungkin terlewat"
    else:
        return "Kurang - Banyak kasus stunting tidak terdeteksi (false negative tinggi)"

def get_specificity_interpretation(specificity: float) -> str:
    """Interpretasi nilai Specificity"""
    if specificity >= 0.95:
        return "Sangat Baik - Hampir semua kasus normal terdeteksi dengan benar"
    elif specificity >= 0.90:
        return "Baik - Sebagian besar kasus normal terdeteksi dengan benar"
    elif specificity >= 0.80:
        return "Cukup Baik - Cukup banyak kasus normal terdeteksi"
    elif specificity >= 0.70:
        return "Sedang - Beberapa kasus normal salah diklasifikasi"
    else:
        return "Kurang - Banyak false positive, model terlalu sensitif"

def get_f1_interpretation(f1: float) -> str:
    """Interpretasi nilai F1-Score"""
    if f1 >= 0.95:
        return "Sangat Baik - Balance sempurna antara precision dan recall"
    elif f1 >= 0.90:
        return "Baik - Balance baik antara precision dan recall"
    elif f1 >= 0.80:
        return "Cukup Baik - Balance cukup antara precision dan recall"
    elif f1 >= 0.70:
        return "Sedang - Balance sedang, perlu perbaikan"
    else:
        return "Kurang - Model tidak balance, perlu pelatihan ulang"

@router.get("/compare-k-values", response_model=Dict[str, Any])
async def compare_k_values(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase),
    model: StuntingKNNModel = Depends(get_knn_model)
):
    """
    Perbandingan performa KNN untuk K = 3, 5, 7, 9.

    Metodologi (sesuai kebutuhan sistem nyata):
    - Data Latih  : SELURUH 500 data dari data_latih_stunting.csv (tanpa split)
    - Data Uji    : Data balita baru yang diinput melalui sistem (tabel pengukuran)
    - Ground truth: zscore_tbu < -2 = Stunting (Standar WHO)
    - Prediksi    : Hasil klasifikasi KNN terhadap data pengukuran baru

    Ini mencerminkan penggunaan model di dunia nyata:
    model dilatih pada semua data historis, dievaluasi pada data baru yang belum pernah dilihat.

    Metrik: Accuracy, Precision, Recall (Sensitivity), Specificity, F1-Score
    + Confusion Matrix (TP, TN, FP, FN) per K

    Dapat diakses oleh: Admin dan Kader
    """
    if current_user.get("role") not in ["admin", "kader"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin dan Kader yang dapat mengakses evaluasi model"
        )

    try:
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.preprocessing import StandardScaler

        # ----------------------------------------------------------------
        # 1. LOAD SEMUA DATA DARI CSV → DATA LATIH (100%)
        # ----------------------------------------------------------------
        csv_path = "data_latih_stunting.csv"
        if not os.path.exists(csv_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File data_latih_stunting.csv tidak ditemukan"
            )

        df = pd.read_csv(csv_path)
        print(f"=" * 70)
        print(f"📂 Data Latih (CSV): {csv_path}  |  Total: {len(df)} sampel (digunakan 100%)")

        X_train_list, y_train_list = [], []
        for _, row in df.iterrows():
            status_label = int(row.get("status_stunting", 0))
            y_train_list.append(1 if status_label in [3, 4] else 0)
            jk_enc = 1 if str(row.get("jenis_kelamin", "L")).upper() == "L" else 0
            X_train_list.append([
                jk_enc,
                float(row.get("usia_bulan", 0)),
                float(row.get("tinggi_badan", 0)),
                float(row.get("berat_badan", 0)),
                float(row.get("lingkar_lengan", 0)),
                float(row.get("lingkar_kepala", 0)),
                float(row.get("zscore_bbu", 0)),
                float(row.get("zscore_tbu", 0))
            ])

        X_train = np.array(X_train_list)
        y_train = np.array(y_train_list)
        csv_stunting  = int(np.sum(y_train == 1))
        csv_normal    = int(np.sum(y_train == 0))

        # ----------------------------------------------------------------
        # 2. LOAD DATA UJI DARI DB PENGUKURAN (DATA BALITA BARU)
        # ----------------------------------------------------------------
        test_response = supabase_client.table("pengukuran")\
            .select("*, balita(jenis_kelamin)")\
            .not_.is_("zscore_tbu", "null")\
            .not_.is_("zscore_bbu", "null")\
            .execute()

        if not test_response.data or len(test_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Belum ada data pengukuran di sistem. "
                       "Tambahkan data pengukuran balita terlebih dahulu untuk evaluasi model."
            )

        X_test_list, y_test_list = [], []
        for record in test_response.data:
            zscore_tbu_val = float(record.get("zscore_tbu", 0))
            y_test_list.append(1 if zscore_tbu_val < -2 else 0)
            balita_data = record.get("balita", {}) or {}
            jk = balita_data.get("jenis_kelamin", "L")
            jk_enc = 1 if str(jk).upper() == "L" else 0
            X_test_list.append([
                jk_enc,
                float(record.get("usia_bulan", 0)),
                float(record.get("tinggi_badan", 0)),
                float(record.get("berat_badan", 0)),
                float(record.get("lingkar_lengan", 0)),
                float(record.get("lingkar_kepala", 0)),
                float(record.get("zscore_bbu", 0)),
                float(record.get("zscore_tbu", 0))
            ])

        X_test  = np.array(X_test_list)
        y_test  = np.array(y_test_list)
        test_stunting  = int(np.sum(y_test == 1))
        test_normal    = int(np.sum(y_test == 0))

        print(f"📋 Data Uji (DB Pengukuran): {len(y_test)} data baru "
              f"(Stunting={test_stunting}, Normal={test_normal})")

        # ----------------------------------------------------------------
        # 3. PREPROCESSING — StandardScaler + Gender Weight
        #    Fit pada seluruh data latih CSV, transform data uji DB
        # ----------------------------------------------------------------
        scaler = StandardScaler()
        X_train_sc = scaler.fit_transform(X_train)
        X_test_sc  = scaler.transform(X_test)

        # Bobot gender (index 0 × 5.0) — konsisten dengan model produksi
        X_train_sc_w = X_train_sc.copy(); X_train_sc_w[:, 0] *= 5.0
        X_test_sc_w  = X_test_sc.copy();  X_test_sc_w[:, 0]  *= 5.0

        # ----------------------------------------------------------------
        # 4. EVALUASI SETIAP K — train pada ALL data CSV, uji pada DB
        # ----------------------------------------------------------------
        k_values = [3, 5, 7, 9]
        comparison_results = []

        print(f"\n{'K':>4}  {'Acc':>7}  {'Prec':>7}  {'Rec':>7}  {'Spec':>7}  {'F1':>7}  "
              f"{'TP':>4}  {'TN':>4}  {'FP':>4}  {'FN':>4}")
        print("-" * 70)

        for k in k_values:
            knn = KNeighborsClassifier(n_neighbors=k, weights='distance', metric='euclidean')
            knn.fit(X_train_sc_w, y_train)
            y_pred = knn.predict(X_test_sc_w)

            cm_k = confusion_matrix(y_test, y_pred, labels=[0, 1])
            tn, fp, fn, tp = cm_k.ravel()

            acc  = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec  = recall_score(y_test, y_pred, zero_division=0)
            f1   = f1_score(y_test, y_pred, zero_division=0)
            spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0

            print(f"K={k}  {acc:7.4f}  {prec:7.4f}  {rec:7.4f}  {spec:7.4f}  {f1:7.4f}  "
                  f"{tp:4d}  {tn:4d}  {fp:4d}  {fn:4d}")

            comparison_results.append({
                "k_value": k,
                "metrics": {
                    "accuracy":    round(float(acc),  4),
                    "precision":   round(float(prec), 4),
                    "recall":      round(float(rec),  4),
                    "specificity": round(float(spec), 4),
                    "f1_score":    round(float(f1),   4),
                    "accuracy_pct":    round(float(acc)  * 100, 2),
                    "precision_pct":   round(float(prec) * 100, 2),
                    "recall_pct":      round(float(rec)  * 100, 2),
                    "specificity_pct": round(float(spec) * 100, 2),
                    "f1_pct":          round(float(f1)   * 100, 2),
                },
                "confusion_matrix": {
                    "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn)
                }
            })

        # ----------------------------------------------------------------
        # 5. REKOMENDASI K TERBAIK
        #    Prioritas: F1-Score tertinggi → jika sama, pilih K lebih besar
        # ----------------------------------------------------------------
        best = max(comparison_results, key=lambda x: (x["metrics"]["f1_score"], x["k_value"]))
        print(f"\n🏆 K terbaik = {best['k_value']}  (F1={best['metrics']['f1_score']:.4f})")
        print("=" * 70)

        return {
            "status": "success",
            "message": "Perbandingan k-values berhasil (data latih: CSV 100%, data uji: pengukuran DB)",
            "dataset_info": {
                "source": "CSV Data Latih (100%) + Data Pengukuran Baru (DB)",
                "total_csv":           len(df),
                "train_size":          len(y_train),
                "test_size":           len(y_test),
                "stunting_count":      test_stunting,
                "non_stunting_count":  test_normal,
                "stunting_train":      csv_stunting,
                "non_stunting_train":  csv_normal,
                "split_ratio":         None,
                "method": (
                    f"Data latih: {len(df)} sampel dari {csv_path} "
                    f"({csv_stunting} Stunting / {csv_normal} Non-Stunting) — digunakan 100%, tanpa split. "
                    f"Data uji: {len(y_test)} data pengukuran BARU dari sistem "
                    f"({test_stunting} Stunting / {test_normal} Normal). "
                    f"Ground truth: zscore_tbu < -2 = Stunting (Standar WHO). "
                    f"StandardScaler di-fit pada seluruh data CSV. "
                    f"Gender weight ×5.0 diterapkan setelah scaling."
                )
            },
            "comparisons": comparison_results,
            "recommendation": {
                "best_k":   best["k_value"],
                "reason":   "F1-Score tertinggi pada data pengukuran baru dari sistem; jika sama, K lebih besar diprioritaskan",
                "f1_score": best["metrics"]["f1_score"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat membandingkan k-values: {str(e)}"
        )


@router.post("/simulate", response_model=Dict[str, Any])
async def simulate_prediction(
    input_data: SimulationInput,
    current_user: dict = Depends(get_current_user),
    model: StuntingKNNModel = Depends(get_knn_model)
):
    """
    Simulasi prediksi untuk melihat tetangga terdekat (K=5)
    Endpoint ini menjawab pertanyaan "Data apa yang mendekati?"
    """
    try:
        # Gunakan PredictionService yang sudah handle Z-Score dan Neighbors
        result = prediction_service.predict_stunting(
            jenis_kelamin=input_data.jenis_kelamin,
            usia_bulan=input_data.usia_bulan,
            tinggi_badan=input_data.tinggi_badan,
            berat_badan=input_data.berat_badan,
            lingkar_lengan=input_data.lingkar_lengan,
            lingkar_kepala=input_data.lingkar_kepala
        )
        
        return {
            "status": "success",
            "message": "Simulasi berhasil",
            "data": result,
            "explanation": "Result includes 'nearest_neighbors' which shows the closest data points from training set."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saat simulasi: {str(e)}"
        )


@router.get("/training-data/count", response_model=Dict[str, Any])
async def count_training_data_db(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Hitung jumlah data latih yang tersimpan di database (tabel knn_training_data)
    Dapat diakses oleh: Admin dan Kader
    """
    if current_user.get("role") not in ["admin", "kader"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tidak memiliki akses"
        )
    try:
        count_res = supabase_client.table("knn_training_data").select("id", count="exact").execute()
        count = count_res.count if count_res.count is not None else 0
        return {"status": "success", "count": count}
    except Exception:
        return {"status": "success", "count": 0, "note": "Tabel tidak ditemukan atau kosong"}


@router.delete("/training-data", response_model=Dict[str, Any])
async def delete_training_data_db(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Hapus semua data latih dari tabel knn_training_data di database.
    Data latih di CSV tetap aman — hanya data di DB yang dihapus.
    Hanya Admin yang dapat melakukan operasi ini.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin yang dapat menghapus data latih dari database"
        )
    try:
        count_res = supabase_client.table("knn_training_data").select("id", count="exact").execute()
        count_before = count_res.count if count_res.count is not None else 0

        if count_before == 0:
            return {
                "status": "success",
                "message": "Data latih di database sudah kosong (0 data)",
                "deleted_count": 0
            }

        supabase_client.table("knn_training_data").delete().neq("id", 0).execute()

        return {
            "status": "success",
            "message": f"Berhasil menghapus {count_before} data latih dari database",
            "deleted_count": count_before
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghapus data latih: {str(e)}"
        )
