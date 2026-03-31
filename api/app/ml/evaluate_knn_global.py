"""
Evaluasi Model KNN dengan 4-Class Classification
=================================================

Evaluasi performa KNN menggunakan 4 kelas:
- Class 0: Normal + Gizi Baik (ZTB >= -2.0 AND ZBB >= -1.0)
- Class 1: Normal + Kurang Gizi (ZTB >= -2.0 AND ZBB < -1.0)
- Class 2: Stunting + Gizi Baik (ZTB < -2.0 AND ZBB >= -1.0)
- Class 3: Stunting + Kurang Gizi (ZTB < -2.0 AND ZBB < -1.0)

Ground truth dihitung dari Z-Score (WHO standard):
- ZTB = Z-Score Tinggi Badan (height-for-age)
- ZBB = Z-Score Berat Badan  (weight-for-age)

Prediksi dari KNN model (Scikit-Learn)
Evaluasi: 4x4 Confusion Matrix + One-vs-Rest metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, multilabel_confusion_matrix
import warnings
warnings.filterwarnings('ignore')

from app.database import get_supabase


class ZScoreCalculator:
    """
    Kalkulator Z-Score menggunakan WHO 2006/2007 LMS Method
    
    PENTING: Menggunakan zscore_calculator yang sudah terimplementasi
    dengan WHO reference data lengkap (0-60 bulan)
    """
    
    @staticmethod
    def calculate_zscore_tbu(jenis_kelamin: str, usia_bulan: int, tinggi_badan: float) -> float:
        """
        Hitung Z-Score Tinggi Badan untuk Usia (Height-for-Age)
        
        Menggunakan WHO 2006/2007 LMS method:
        Z = ((value/M)^L - 1) / (L * S)
        
        Args:
            jenis_kelamin: 'L' atau 'P'
            usia_bulan: umur dalam bulan
            tinggi_badan: tinggi dalam cm
            
        Returns:
            Z-Score ZTB (yang akurat sesuai WHO standard)
        """
        from app.utils.zscore_calculator import calculate_zscore_tbu as calc_tbu
        try:
            return calc_tbu(tinggi_badan, usia_bulan, jenis_kelamin)
        except Exception as e:
            print(f"⚠️ Error dalam calculate_zscore_tbu, fallback ke default: {e}")
            return 0.0
    
    @staticmethod
    def calculate_zscore_bbu(jenis_kelamin: str, usia_bulan: int, berat_badan: float) -> float:
        """
        Hitung Z-Score Berat Badan untuk Usia (Weight-for-Age)
        
        Menggunakan WHO 2006/2007 LMS method
        
        Args:
            jenis_kelamin: 'L' atau 'P'
            usia_bulan: umur dalam bulan
            berat_badan: berat dalam kg
            
        Returns:
            Z-Score ZBB (yang akurat sesuai WHO standard)
        """
        from app.utils.zscore_calculator import calculate_zscore_bbu as calc_bbu
        try:
            return calc_bbu(berat_badan, usia_bulan, jenis_kelamin)
        except Exception as e:
            print(f"⚠️ Error dalam calculate_zscore_bbu, fallback ke default: {e}")
            return 0.0
    
    @staticmethod
    def create_4class_label(usia_dalam_bulan: int, zscore_tbu: float, zscore_bbu: float) -> int:
        """
        Buat label 4-class dari Z-Score berdasarkan WHO standard
        
        WHO standard untuk stunting: ZTB < -2.0
        WHO standard untuk gizi kurang: ZBB < -1.0
        
        Classes:
        - 0: Normal + Gizi Baik    (ZTB >= -2.0 AND ZBB >= -1.0)
        - 1: Normal + Kurang Gizi  (ZTB >= -2.0 AND ZBB < -1.0)
        - 2: Stunting + Gizi Baik  (ZTB < -2.0 AND ZBB >= -1.0)
        - 3: Stunting + Kurang Gizi (ZTB < -2.0 AND ZBB < -1.0)
        
        Args:
            usia_dalam_bulan: Umur dalam bulan (untuk validasi)
            zscore_tbu: Z-Score Tinggi untuk Usia
            zscore_bbu: Z-Score Berat untuk Usia
            
        Returns:
            Class label (0-3)
        """
        is_stunting = zscore_tbu < -2.0
        is_gizi_kurang = zscore_bbu < -1.0
        
        if not is_stunting and not is_gizi_kurang:
            return 0  # Normal + Gizi Baik
        elif not is_stunting and is_gizi_kurang:
            return 1  # Normal + Kurang Gizi
        elif is_stunting and not is_gizi_kurang:
            return 2  # Stunting + Gizi Baik
        else:
            return 3  # Stunting + Kurang Gizi


class KNNGlobalEvaluator4Class:
    """
    Evaluator untuk model KNN dengan 4-class classification
    """
    
    def __init__(self, k: int = 5):
        self.k = k
        self.scaler = StandardScaler()
        self.knn_model = None
        self.zscore_calc = ZScoreCalculator()
        self.class_names = {
            0: "Normal + Gizi Baik",
            1: "Normal + Kurang Gizi",
            2: "Stunting + Gizi Baik",
            3: "Stunting + Kurang Gizi"
        }
    
    def fetch_all_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Fetch semua data dari tabel pengukuran
        
        Returns:
            X_data: Features array
            y_true: Labels dari Z-Score (4-class)
            y_pred_placeholder: Akan diisi nanti
            metadata: Info tambahan
        """
        try:
            supabase = get_supabase()
            
            # Fetch semua data pengukuran
            response = supabase.table("pengukuran").select(
                "id, jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala"
            ).execute()
            
            data = response.data
            
            if not data:
                raise ValueError("Tidak ada data di tabel pengukuran")
            
            print(f"✓ Fetch semua data: {len(data)} records")
            
            # Process data
            X_list = []
            y_true_list = []
            record_ids = []
            
            for record in data:
                # Skip missing values
                if None in [
                    record.get("jenis_kelamin"),
                    record.get("usia_bulan"),
                    record.get("tinggi_badan"),
                    record.get("berat_badan"),
                    record.get("lingkar_lengan"),
                    record.get("lingkar_kepala")
                ]:
                    continue
                
                # Extract features
                jk = record["jenis_kelamin"]
                usia = record["usia_bulan"]
                tinggi = record["tinggi_badan"]
                berat = record["berat_badan"]
                lingkar_lengan = record["lingkar_lengan"]
                lingkar_kepala = record["lingkar_kepala"]
                
                # Encode gender: L=1, P=0
                jk_encoded = 1 if jk == "L" else 0
                
                features = [
                    jk_encoded,
                    usia,
                    tinggi,
                    berat,
                    lingkar_lengan,
                    lingkar_kepala
                ]
                
                # Calculate Z-Scores for ground truth
                zscore_tbu = self.zscore_calc.calculate_zscore_tbu(jk, usia, tinggi)
                zscore_bbu = self.zscore_calc.calculate_zscore_bbu(jk, usia, berat)
                
                # Create 4-class label from Z-Scores
                label_4class = self.zscore_calc.create_4class_label(usia, zscore_tbu, zscore_bbu)
                
                X_list.append(features)
                y_true_list.append(label_4class)
                record_ids.append(record.get("id"))
            
            if not X_list:
                raise ValueError("Semua data memiliki missing values")
            
            X_data = np.array(X_list, dtype=float)
            y_true = np.array(y_true_list, dtype=int)
            
            print(f"✓ Data setelah cleaning: {len(X_data)} samples")
            print(f"  Class distribution:")
            for cls in range(4):
                count = np.sum(y_true == cls)
                pct = (count / len(y_true)) * 100
                print(f"    Class {cls} ({self.class_names[cls]}): {count} ({pct:.1f}%)")
            
            return X_data, y_true, record_ids, None
        
        except Exception as e:
            print(f"❌ Error fetching data: {str(e)}")
            raise
    
    def evaluate_global(self) -> Dict:
        """
        Evaluasi KNN dengan 4-class classification
        
        Returns:
            Dictionary dengan hasil evaluasi lengkap
        """
        print("\n" + "=" * 100)
        print(f"EVALUASI KNN GLOBAL - 4-CLASS CLASSIFICATION (K={self.k})")
        print("=" * 100)
        
        try:
            # Fetch data
            print("\n📊 Step 1: Fetch semua data...")
            X_data, y_true, record_ids, _ = self.fetch_all_data()
            
            # Normalize
            print("\n🔧 Step 2: Normalize features...")
            self.scaler.fit(X_data)
            X_scaled = self.scaler.transform(X_data)
            
            # Train KNN
            print(f"\n🔧 Step 3: Train KNN (K={self.k})...")
            self.knn_model = KNeighborsClassifier(
                n_neighbors=self.k,
                metric='euclidean',
                weights='distance',
                algorithm='auto'
            )
            self.knn_model.fit(X_scaled, y_true)
            
            # Predict
            print("\n🎯 Step 4: Make predictions...")
            y_pred = self.knn_model.predict(X_scaled)
            
            # Calculate 4x4 confusion matrix
            print("\n📈 Step 5: Calculate 4x4 confusion matrix...")
            cm_4x4 = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3])
            
            # Calculate metrics per class (one-vs-rest)
            print("\n📊 Step 6: Calculate per-class metrics...")
            metrics_per_class = {}
            
            for cls in range(4):
                # One-vs-rest: create binary problem
                y_true_binary = (y_true == cls).astype(int)
                y_pred_binary = (y_pred == cls).astype(int)
                
                # Calculate TP, TN, FP, FN
                tp = np.sum((y_true_binary == 1) & (y_pred_binary == 1))
                tn = np.sum((y_true_binary == 0) & (y_pred_binary == 0))
                fp = np.sum((y_true_binary == 0) & (y_pred_binary == 1))
                fn = np.sum((y_true_binary == 1) & (y_pred_binary == 0))
                
                # Calculate metrics
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
                
                metrics_per_class[cls] = {
                    "tp": int(tp),
                    "tn": int(tn),
                    "fp": int(fp),
                    "fn": int(fn),
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "f1_score": round(f1, 4),
                    "support": int(np.sum(y_true == cls))
                }
            
            # Calculate macro-average metrics
            precisions = [metrics_per_class[cls]["precision"] for cls in range(4)]
            recalls = [metrics_per_class[cls]["recall"] for cls in range(4)]
            f1_scores = [metrics_per_class[cls]["f1_score"] for cls in range(4)]
            
            macro_precision = np.mean(precisions)
            macro_recall = np.mean(recalls)
            macro_f1 = np.mean(f1_scores)
            
            # Overall accuracy
            accuracy = np.sum(y_true == y_pred) / len(y_true)
            
            result = {
                "k": self.k,
                "n_total_samples": len(X_data),
                "n_correct": int(np.sum(y_true == y_pred)),
                "n_incorrect": int(np.sum(y_true != y_pred)),
                "accuracy": round(accuracy, 4),
                "confusion_matrix_4x4": cm_4x4.tolist(),
                "metrics_per_class": metrics_per_class,
                "macro_average": {
                    "precision": round(macro_precision, 4),
                    "recall": round(macro_recall, 4),
                    "f1_score": round(macro_f1, 4)
                },
                "class_distribution": {
                    "0": int(np.sum(y_true == 0)),
                    "1": int(np.sum(y_true == 1)),
                    "2": int(np.sum(y_true == 2)),
                    "3": int(np.sum(y_true == 3))
                },
                "prediction_distribution": {
                    "0": int(np.sum(y_pred == 0)),
                    "1": int(np.sum(y_pred == 1)),
                    "2": int(np.sum(y_pred == 2)),
                    "3": int(np.sum(y_pred == 3))
                }
            }
            
            return result
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
    
    def print_results(self, result: Dict):
        """
        Print hasil evaluasi dengan format rapi
        """
        print("\n" + "=" * 120)
        print("HASIL EVALUASI KNN GLOBAL - 4-CLASS CLASSIFICATION")
        print("=" * 120)
        
        print(f"\n📋 SUMMARY:")
        print(f"  K Value: {result['k']}")
        print(f"  Total Samples: {result['n_total_samples']}")
        print(f"  Correct Predictions: {result['n_correct']}")
        print(f"  Incorrect Predictions: {result['n_incorrect']}")
        print(f"  Overall Accuracy: {result['accuracy']:.4f} ({result['accuracy']*100:.2f}%)")
        
        # Class distribution
        print(f"\n📊 CLASS DISTRIBUTION (Actual):")
        for cls in range(4):
            count = result["class_distribution"][str(cls)]
            pct = (count / result['n_total_samples']) * 100
            print(f"  Class {cls}: {self.class_names[cls]:30s} = {count:4d} ({pct:5.2f}%)")
        
        print(f"\n📊 PREDICTION DISTRIBUTION:")
        for cls in range(4):
            count = result["prediction_distribution"][str(cls)]
            pct = (count / result['n_total_samples']) * 100
            print(f"  Class {cls}: {self.class_names[cls]:30s} = {count:4d} ({pct:5.2f}%)")
        
        # 4x4 Confusion Matrix
        print(f"\n🔲 4x4 CONFUSION MATRIX:")
        cm = result["confusion_matrix_4x4"]
        print(f"\n  {'':30s}  {'Predicted Class':^50s}")
        print(f"  {'':30s}  {'0: N+GB':>10s}  {'1: N+KG':>10s}  {'2: S+GB':>10s}  {'3: S+KG':>10s}")
        print(f"  {'-' * 30}  {'-' * 50}")
        for i in range(4):
            row_label = f"Actual {i}: {self.class_names[i]}"
            print(f"  {row_label:30s}  {cm[i][0]:>10d}  {cm[i][1]:>10d}  {cm[i][2]:>10d}  {cm[i][3]:>10d}")
        
        # Per-class metrics
        print(f"\n📈 PER-CLASS METRICS (One-vs-Rest):")
        print(f"\n  {'Class':^20s}  {'Precision':>10s}  {'Recall':>10s}  {'F1-Score':>10s}  {'Support':>10s}")
        print(f"  {'-' * 20}  {'-' * 40}")
        for cls in range(4):
            m = result["metrics_per_class"][cls]
            class_label = f"{cls}: {self.class_names[cls][:20]}"
            print(f"  {class_label:20s}  {m['precision']:>10.4f}  {m['recall']:>10.4f}  {m['f1_score']:>10.4f}  {m['support']:>10d}")
        
        # Macro-average
        macro = result["macro_average"]
        print(f"  {'-' * 20}  {'-' * 40}")
        print(f"  {'MACRO-AVERAGE':20s}  {macro['precision']:>10.4f}  {macro['recall']:>10.4f}  {macro['f1_score']:>10.4f}")
        
        print("\n" + "=" * 120)
    
    def get_interpretation(self, result: Dict) -> str:
        """
        Interpretasi hasil evaluasi
        """
        macro = result["macro_average"]
        
        interpretation = f"🔍 INTERPRETASI HASIL EVALUASI\n\n"
        
        # Accuracy
        if result['accuracy'] >= 0.85:
            interpretation += f"✓ Accuracy sangat baik: {result['accuracy']*100:.2f}%\n"
        elif result['accuracy'] >= 0.75:
            interpretation += f"✓ Accuracy baik: {result['accuracy']*100:.2f}%\n"
        else:
            interpretation += f"⚠ Accuracy perlu ditingkatkan: {result['accuracy']*100:.2f}%\n"
        
        # Recall per class
        interpretation += f"\n📋 RECALL PER KELAS (Coverage):\n"
        for cls in range(4):
            recall = result["metrics_per_class"][cls]["recall"]
            support = result["metrics_per_class"][cls]["support"]
            if recall >= 0.80:
                symbol = "✓"
            elif recall >= 0.60:
                symbol = "⚠"
            else:
                symbol = "❌"
            interpretation += f"  {symbol} Class {cls} ({self.class_names[cls]}): {recall*100:.2f}% (n={support})\n"
        
        # Macro-average interpretation
        interpretation += f"\n🎯 MACRO-AVERAGE METRICS:\n"
        interpretation += f"  Precision: {macro['precision']:.4f}\n"
        interpretation += f"  Recall:    {macro['recall']:.4f}\n"
        interpretation += f"  F1-Score:  {macro['f1_score']:.4f}\n"
        
        # Recommendation
        interpretation += f"\n💡 REKOMENDASI:\n"
        if result['accuracy'] >= 0.80 and macro['f1_score'] >= 0.75:
            interpretation += f"  ✓ Model siap untuk digunakan dalam penelitian\n"
        else:
            interpretation += f"  ⚠ Pertimbangkan untuk melakukan tuning atau penambahan data\n"
        
        return interpretation


def main():
    """Main function"""
    try:
        evaluator = KNNGlobalEvaluator4Class(k=5)
        result = evaluator.evaluate_global()
        evaluator.print_results(result)
        print(f"\n{evaluator.get_interpretation(result)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
