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
        Fetch semua data dari tabel pengukuran untuk training
        
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
        Evaluasi KNN dengan 4-class classification menggunakan Train-Test Split
        
        Data flow:
        1. Fetch semua data dari pengukuran table (503 sampel)
        2. Split: Training 80% (402) + Testing 20% (101)
        3. Train KNN pada Training set
        4. Evaluate pada Test set (terpisah)
        5. Hitung confusion matrix, accuracy, precision, recall, specificity, F1-score
        
        Returns:
            Dictionary dengan hasil evaluasi lengkap
        """
        print("\n" + "=" * 100)
        print(f"EVALUASI KNN GLOBAL - 4-CLASS CLASSIFICATION (K={self.k})")
        print("=" * 100)
        
        try:
            # Fetch data
            print("\n📊 Step 1: Fetch semua data dari pengukuran table...")
            X_data, y_true, record_ids, _ = self.fetch_all_data()
            print(f"✓ Total sampel: {len(X_data)}")
            
            # Train-Test Split: 80-20
            print("\n📊 Step 2: Split data menjadi Training (80%) dan Testing (20%)...")
            from sklearn.model_selection import train_test_split
            
            # Check if we have enough samples for stratified split
            total_samples = len(X_data)
            n_test_samples = max(1, int(total_samples * 0.2))
            use_stratify = n_test_samples >= 4  # Need at least 4 samples for 4 classes
            
            # If test set is too small, use larger split or non-stratified
            if not use_stratify and n_test_samples < 4:
                # Adjust test_size to ensure minimum 4 samples, or use non-stratified
                if total_samples >= 8:
                    test_size = 0.4  # 40% test to get at least 4 samples
                else:
                    # Too few samples total - use minimal split
                    test_size = 0.3 if total_samples >= 5 else 0.2
                    use_stratify = False
            else:
                test_size = 0.2
            
            print(f"Split settings: test_size={test_size}, stratify={use_stratify}, total_samples={total_samples}")
            
            X_train, X_test, y_train, y_test, train_indices, test_indices = train_test_split(
                X_data, y_true, np.arange(len(X_data)),
                test_size=test_size,  # Dynamic test size
                random_state=42,  # Untuk reproducibility
                stratify=y_true if use_stratify else None  # Preserve class distribution if possible
            )
            
            print(f"✓ Training set: {len(X_train)} samples")
            print(f"  Class distribution:")
            for cls in range(4):
                count = np.sum(y_train == cls)
                pct = (count / len(y_train)) * 100
                print(f"    Class {cls}: {count} ({pct:.1f}%)")
            
            print(f"✓ Testing set: {len(X_test)} samples")
            print(f"  Class distribution:")
            for cls in range(4):
                count = np.sum(y_test == cls)
                pct = (count / len(y_test)) * 100
                print(f"    Class {cls}: {count} ({pct:.1f}%)")
            
            # Normalize Training data
            print("\n🔧 Step 3: Normalize features on Training set...")
            self.scaler.fit(X_train)  # Fit scaler HANYA on training data
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)  # Transform test using training scaler
            print("✓ Normalization complete")
            
            # Train KNN on Training set
            print(f"\n🔧 Step 4: Train KNN (K={self.k}) on Training set...")
            self.knn_model = KNeighborsClassifier(
                n_neighbors=self.k,
                metric='euclidean',
                weights='distance',
                algorithm='auto'
            )
            self.knn_model.fit(X_train_scaled, y_train)
            print(f"✓ Model trained on {len(X_train_scaled)} samples")
            
            # Make predictions on Test set
            print("\n🎯 Step 5: Make predictions on Test set...")
            y_pred = self.knn_model.predict(X_test_scaled)
            print(f"✓ Predictions made for {len(y_pred)} test samples")
            
            # Calculate 4x4 confusion matrix on Test set (untuk referensi)
            print("\n📈 Step 6: Calculate 4x4 confusion matrix on Test set...")
            cm_4x4 = confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3])
            print(f"✓ Confusion Matrix created")
            
            # Calculate ONE-VS-REST untuk Class 3 (Stunting + Kurang Gizi)
            # Ini memberikan metrik keseluruhan untuk mendeteksi kasus paling kritis
            print("\n📊 Step 7: Calculate metrics fokus pada Class 3 (Stunting + Kurang Gizi)...")
            
            # Convert ke binary: Class 3 (positive) vs Others (negative)
            y_test_binary = (y_test == 3).astype(int)
            y_pred_binary = (y_pred == 3).astype(int)
            
            # Calculate TP, TN, FP, FN
            tp = np.sum((y_test_binary == 1) & (y_pred_binary == 1))
            tn = np.sum((y_test_binary == 0) & (y_pred_binary == 0))
            fp = np.sum((y_test_binary == 0) & (y_pred_binary == 1))
            fn = np.sum((y_test_binary == 1) & (y_pred_binary == 0))
            
            # Calculate metrics
            accuracy = (tp + tn) / len(y_test) if len(y_test) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"✓ Metrics calculated:")
            print(f"  TP (True Positive): {int(tp)}")
            print(f"  TN (True Negative): {int(tn)}")
            print(f"  FP (False Positive): {int(fp)}")
            print(f"  FN (False Negative): {int(fn)}")
            
            result = {
                "k": self.k,
                "evaluation_focus": {
                    "target_class": 3,
                    "target_class_name": "Stunting + Kurang Gizi",
                    "description": "One-vs-Rest approach: mengukur performa sistem dalam mendeteksi kasus paling kritis"
                },
                "n_training_samples": len(X_train),
                "n_testing_samples": len(X_test),
                "n_total_samples": len(X_data),
                "confusion_matrix_4x4": cm_4x4.tolist(),
                "class_3_metrics": {
                    "tp": int(tp),
                    "tn": int(tn),
                    "fp": int(fp),
                    "fn": int(fn),
                    "tp_percent": round(float(tp / len(y_test) * 100), 2) if len(y_test) > 0 else 0,
                    "tn_percent": round(float(tn / len(y_test) * 100), 2) if len(y_test) > 0 else 0,
                    "fp_percent": round(float(fp / len(y_test) * 100), 2) if len(y_test) > 0 else 0,
                    "fn_percent": round(float(fn / len(y_test) * 100), 2) if len(y_test) > 0 else 0,
                    "class_distribution": {
                        "actual_class_3": int(np.sum(y_test_binary == 1)),
                        "actual_other": int(np.sum(y_test_binary == 0)),
                        "predicted_class_3": int(np.sum(y_pred_binary == 1)),
                        "predicted_other": int(np.sum(y_pred_binary == 0))
                    }
                },
                "overall_metrics": {
                    "accuracy": round(accuracy, 4),
                    "accuracy_percent": round(float(accuracy) * 100, 2),
                    "precision": round(precision, 4),
                    "precision_percent": round(float(precision) * 100, 2),
                    "recall": round(recall, 4),
                    "recall_percent": round(float(recall) * 100, 2),
                    "specificity": round(specificity, 4),
                    "specificity_percent": round(float(specificity) * 100, 2),
                    "f1_score": round(f1, 4),
                    "f1_score_percent": round(float(f1) * 100, 2)
                },
                "test_class_distribution": {
                    "0": int(np.sum(y_test == 0)),
                    "1": int(np.sum(y_test == 1)),
                    "2": int(np.sum(y_test == 2)),
                    "3": int(np.sum(y_test == 3))
                },
                "test_prediction_distribution": {
                    "0": int(np.sum(y_pred == 0)),
                    "1": int(np.sum(y_pred == 1)),
                    "2": int(np.sum(y_pred == 2)),
                    "3": int(np.sum(y_pred == 3))
                },
                "evaluation_note": "One-vs-Rest untuk Class 3 (Stunting + Kurang Gizi) pada TEST SET (20% dari total data). Model dilatih pada TRAINING SET (80%). Metrik tunggal ini mengukur performa sistem dalam mendeteksi kasus paling kritis."
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


# Alias for backward compatibility with routes
KNNGlobalEvaluator = KNNGlobalEvaluator4Class


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
