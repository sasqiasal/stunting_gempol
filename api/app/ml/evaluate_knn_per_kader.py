"""
Evaluasi KNN Per-Kader dengan 4-Class Classification
======================================================

Evaluasi performa KNN untuk individual staff (kader) dengan dukungan filtering per bulan
Menggunakan 4-class classification berbasis Z-Score WHO standard
"""

import numpy as np
from typing import Dict, Optional, Tuple
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
import warnings
warnings.filterwarnings('ignore')

from app.database import get_supabase
from app.ml.evaluate_knn_global import ZScoreCalculator


class KNNKaderEvaluator4Class:
    """
    Evaluator untuk KNN per individual kader dengan 4-class classification
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
    
    def fetch_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetch semua data untuk training KNN
        
        Returns:
            X_train: Training features
            y_train: Training labels (4-class dari Z-Score)
        """
        try:
            supabase = get_supabase()
            response = supabase.table("pengukuran").select(
                "jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala"
            ).execute()
            
            data = response.data
            if not data:
                raise ValueError("Tidak ada data training")
            
            X_list = []
            y_list = []
            
            for record in data:
                if None in [
                    record.get("jenis_kelamin"),
                    record.get("usia_bulan"),
                    record.get("tinggi_badan"),
                    record.get("berat_badan"),
                    record.get("lingkar_lengan"),
                    record.get("lingkar_kepala")
                ]:
                    continue
                
                jk = record["jenis_kelamin"]
                usia = record["usia_bulan"]
                tinggi = record["tinggi_badan"]
                berat = record["berat_badan"]
                
                jk_encoded = 1 if jk == "L" else 0
                features = [
                    jk_encoded,
                    usia,
                    tinggi,
                    berat,
                    record["lingkar_lengan"],
                    record["lingkar_kepala"]
                ]
                
                zscore_tbu = self.zscore_calc.calculate_zscore_tbu(jk, usia, tinggi)
                zscore_bbu = self.zscore_calc.calculate_zscore_bbu(jk, usia, berat)
                label = self.zscore_calc.create_4class_label(usia, zscore_tbu, zscore_bbu)
                
                X_list.append(features)
                y_list.append(label)
            
            X_train = np.array(X_list, dtype=float)
            y_train = np.array(y_list, dtype=int)
            
            return X_train, y_train
        
        except Exception as e:
            print(f"❌ Error fetch training data: {str(e)}")
            raise
    
    def fetch_kader_data(self, user_id: int, month: Optional[int] = None, year: int = 2024) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetch data untuk specific kader dengan optional month filtering
        
        Args:
            user_id: ID dari kader
            month: Bulan spesifik (1-12), None untuk semua bulan
            year: Tahun (default: 2024)
            
        Returns:
            X_test: Features array
            y_test: Labels array
        """
        try:
            supabase = get_supabase()
            
            # Build query
            query = supabase.table("pengukuran").select(
                "jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala, tanggal_pengukuran"
            ).eq("kader_id", user_id)
            
            response = query.execute()
            data = response.data
            
            if not data:
                raise ValueError(f"Tidak ada data untuk kader {user_id}")
            
            X_list = []
            y_list = []
            
            for record in data:
                if None in [
                    record.get("jenis_kelamin"),
                    record.get("usia_bulan"),
                    record.get("tinggi_badan"),
                    record.get("berat_badan"),
                    record.get("lingkar_lengan"),
                    record.get("lingkar_kepala"),
                    record.get("tanggal_pengukuran")
                ]:
                    continue
                
                # Filter by month if specified
                if month is not None:
                    tanggal = record["tanggal_pengukuran"]
                    if isinstance(tanggal, str):
                        tanggal_month = int(tanggal.split('-')[1])
                        if tanggal_month != month:
                            continue
                
                jk = record["jenis_kelamin"]
                usia = record["usia_bulan"]
                tinggi = record["tinggi_badan"]
                berat = record["berat_badan"]
                
                jk_encoded = 1 if jk == "L" else 0
                features = [
                    jk_encoded,
                    usia,
                    tinggi,
                    berat,
                    record["lingkar_lengan"],
                    record["lingkar_kepala"]
                ]
                
                zscore_tbu = self.zscore_calc.calculate_zscore_tbu(jk, usia, tinggi)
                zscore_bbu = self.zscore_calc.calculate_zscore_bbu(jk, usia, berat)
                label = self.zscore_calc.create_4class_label(usia, zscore_tbu, zscore_bbu)
                
                X_list.append(features)
                y_list.append(label)
            
            if not X_list:
                raise ValueError(f"Tidak ada data untuk kader {user_id} pada bulan {month}")
            
            X_test = np.array(X_list, dtype=float)
            y_test = np.array(y_list, dtype=int)
            
            return X_test, y_test
        
        except Exception as e:
            print(f"❌ Error fetch kader data: {str(e)}")
            raise
    
    def evaluate_kader(self, user_id: int, month: Optional[int] = None) -> Dict:
        """
        Evaluasi KNN untuk specific kader
        
        Args:
            user_id: ID kader
            month: Bulan spesifik (optional)
            
        Returns:
            Dictionary dengan hasil evaluasi
        """
        try:
            # Load training data
            X_train, y_train = self.fetch_training_data()
            
            # Normalize training data
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            
            # Train KNN
            self.knn_model = KNeighborsClassifier(
                n_neighbors=self.k,
                metric='euclidean',
                weights='distance'
            )
            self.knn_model.fit(X_train_scaled, y_train)
            
            # Load test data (kader data)
            X_test, y_test = self.fetch_kader_data(user_id, month)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Predict
            y_pred = self.knn_model.predict(X_test_scaled)
            
            # Calculate confusion matrix
            cm_4x4 = confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3])
            
            # Per-class metrics
            metrics_per_class = {}
            for cls in range(4):
                y_test_binary = (y_test == cls).astype(int)
                y_pred_binary = (y_pred == cls).astype(int)
                
                tp = np.sum((y_test_binary == 1) & (y_pred_binary == 1))
                tn = np.sum((y_test_binary == 0) & (y_pred_binary == 0))
                fp = np.sum((y_test_binary == 0) & (y_pred_binary == 1))
                fn = np.sum((y_test_binary == 1) & (y_pred_binary == 0))
                
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
                    "support": int(np.sum(y_test == cls))
                }
            
            # Macro-average
            precisions = [metrics_per_class[cls]["precision"] for cls in range(4)]
            recalls = [metrics_per_class[cls]["recall"] for cls in range(4)]
            f1_scores = [metrics_per_class[cls]["f1_score"] for cls in range(4)]
            
            accuracy = np.sum(y_test == y_pred) / len(y_test)
            
            result = {
                "user_id": user_id,
                "month": month,
                "k": self.k,
                "n_samples": len(X_test),
                "accuracy": round(accuracy, 4),
                "confusion_matrix_4x4": cm_4x4.tolist(),
                "metrics_per_class": metrics_per_class,
                "macro_average": {
                    "precision": round(np.mean(precisions), 4),
                    "recall": round(np.mean(recalls), 4),
                    "f1_score": round(np.mean(f1_scores), 4)
                },
                "class_distribution": {
                    "0": int(np.sum(y_test == 0)),
                    "1": int(np.sum(y_test == 1)),
                    "2": int(np.sum(y_test == 2)),
                    "3": int(np.sum(y_test == 3))
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
            raise
    
    def print_results(self, result: Dict):
        """
        Print hasil evaluasi per-kader
        """
        print("\n" + "=" * 120)
        print(f"HASIL EVALUASI KNN KADER {result['user_id']} - 4-CLASS CLASSIFICATION")
        if result['month']:
            print(f"BULAN: {result['month']}")
        print("=" * 120)
        
        print(f"\n📋 SUMMARY:")
        print(f"  Kader ID: {result['user_id']}")
        print(f"  Total Samples: {result['n_samples']}")
        print(f"  Accuracy: {result['accuracy']:.4f} ({result['accuracy']*100:.2f}%)")
        
        print(f"\n📊 CLASS DISTRIBUTION:")
        for cls in range(4):
            count = result["class_distribution"][str(cls)]
            print(f"  Class {cls} ({self.class_names[cls]}): {count}")
        
        # Confusion matrix
        print(f"\n🔲 4x4 CONFUSION MATRIX:")
        cm = result["confusion_matrix_4x4"]
        print(f"\n  {'':30s}  {'Predicted':^50s}")
        print(f"  {'Actual':30s}  {'0: N+GB':>10s}  {'1: N+KG':>10s}  {'2: S+GB':>10s}  {'3: S+KG':>10s}")
        for i in range(4):
            row_label = f"{i}: {self.class_names[i]}"
            print(f"  {row_label:30s}  {cm[i][0]:>10d}  {cm[i][1]:>10d}  {cm[i][2]:>10d}  {cm[i][3]:>10d}")
        
        # Per-class metrics
        print(f"\n📈 PER-CLASS METRICS:")
        print(f"\n  {'Class':^20s}  {'Precision':>10s}  {'Recall':>10s}  {'F1-Score':>10s}  {'Support':>10s}")
        print(f"  {'-' * 20}  {'-' * 40}")
        for cls in range(4):
            m = result["metrics_per_class"][cls]
            class_label = f"{cls}: {self.class_names[cls][:18]}"
            print(f"  {class_label:20s}  {m['precision']:>10.4f}  {m['recall']:>10.4f}  {m['f1_score']:>10.4f}  {m['support']:>10d}")
        
        # Macro-average
        macro = result["macro_average"]
        print(f"  {'-' * 20}  {'-' * 40}")
        print(f"  {'MACRO-AVERAGE':20s}  {macro['precision']:>10.4f}  {macro['recall']:>10.4f}  {macro['f1_score']:>10.4f}")
        
        print("\n" + "=" * 120)


def main():
    """Main function"""
    try:
        evaluator = KNNKaderEvaluator4Class(k=5)
        # Example: evaluate kader with ID 1
        result = evaluator.evaluate_kader(user_id=1)
        evaluator.print_results(result)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
