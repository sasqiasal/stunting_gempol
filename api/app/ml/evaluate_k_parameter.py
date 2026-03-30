"""
Evaluasi Parameter K untuk KNN dengan 4-Class Classification
=============================================================

Membandingkan performa KNN dengan berbagai K values (3, 5, 7, 9)
Menggunakan 4-class classification berbasis Z-Score
Untuk menentukan K value yang paling optimal
"""

import numpy as np
from typing import Dict, List
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
import warnings
warnings.filterwarnings('ignore')

from app.database import get_supabase
from app.ml.evaluate_knn_global_4class import ZScoreCalculator


class KNNKParameterEvaluator4Class:
    """
    Evaluator untuk menentukan K value optimal menggunakan 4-class classification
    """
    
    def __init__(self):
        self.zscore_calc = ZScoreCalculator()
        self.class_names = {
            0: "Normal + Gizi Baik",
            1: "Normal + Kurang Gizi",
            2: "Stunting + Gizi Baik",
            3: "Stunting + Kurang Gizi"
        }
    
    def fetch_all_data(self) -> tuple:
        """
        Fetch semua data dari tabel pengukuran
        
        Returns:
            X: Features array
            y: Labels array (4-class dari Z-Score)
        """
        try:
            supabase = get_supabase()
            response = supabase.table("pengukuran").select(
                "jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala"
            ).execute()
            
            data = response.data
            if not data:
                raise ValueError("Tidak ada data")
            
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
            
            X = np.array(X_list, dtype=float)
            y = np.array(y_list, dtype=int)
            
            return X, y
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
    
    def evaluate_k(self, X: np.ndarray, y: np.ndarray, k: int) -> Dict:
        """
        Evaluasi single K value
        
        Args:
            X: Features
            y: Labels
            k: K value to test
            
        Returns:
            Dictionary dengan hasil evaluasi
        """
        # Normalize
        scaler = StandardScaler()
        scaler.fit(X)
        X_scaled = scaler.transform(X)
        
        # Train KNN
        model = KNeighborsClassifier(
            n_neighbors=k,
            metric='euclidean',
            weights='distance'
        )
        model.fit(X_scaled, y)
        
        # Predict
        y_pred = model.predict(X_scaled)
        
        # Calculate metrics
        cm_4x4 = confusion_matrix(y, y_pred, labels=[0, 1, 2, 3])
        accuracy = np.sum(y == y_pred) / len(y)
        
        # Per-class metrics
        metrics_per_class = {}
        for cls in range(4):
            y_binary = (y == cls).astype(int)
            y_pred_binary = (y_pred == cls).astype(int)
            
            tp = np.sum((y_binary == 1) & (y_pred_binary == 1))
            tn = np.sum((y_binary == 0) & (y_pred_binary == 0))
            fp = np.sum((y_binary == 0) & (y_pred_binary == 1))
            fn = np.sum((y_binary == 1) & (y_pred_binary == 0))
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            metrics_per_class[cls] = {
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4)
            }
        
        # Macro-average
        precisions = [metrics_per_class[cls]["precision"] for cls in range(4)]
        recalls = [metrics_per_class[cls]["recall"] for cls in range(4)]
        f1_scores = [metrics_per_class[cls]["f1_score"] for cls in range(4)]
        
        return {
            "k": k,
            "n_samples": len(X),
            "accuracy": round(accuracy, 4),
            "metrics_per_class": metrics_per_class,
            "macro_average": {
                "precision": round(np.mean(precisions), 4),
                "recall": round(np.mean(recalls), 4),
                "f1_score": round(np.mean(f1_scores), 4)
            }
        }
    
    def evaluate_all_k_values(self, k_values: List[int] = None) -> List[Dict]:
        """
        Evaluasi semua K values
        
        Args:
            k_values: List of K values ke test (default: [3, 5, 7, 9])
            
        Returns:
            List of evaluation results
        """
        if k_values is None:
            k_values = [3, 5, 7, 9]
        
        print("\n" + "=" * 100)
        print("EVALUASI K PARAMETER - 4-CLASS CLASSIFICATION")
        print("=" * 100)
        
        print("\n📊 Fetch data...")
        X, y = self.fetch_all_data()
        
        print(f"✓ Total samples: {len(X)}")
        print(f"  Class distribution:")
        for cls in range(4):
            count = np.sum(y == cls)
            pct = (count / len(y)) * 100
            print(f"    Class {cls} ({self.class_names[cls]}): {count} ({pct:.1f}%)")
        
        print(f"\n🔍 Testing K values: {k_values}")
        results = []
        
        for k in k_values:
            print(f"\n  Testing K={k}...")
            result = self.evaluate_k(X, y, k)
            results.append(result)
            print(f"    Accuracy: {result['accuracy']:.4f}")
        
        return results
    
    def determine_best_k(self, results: List[Dict]) -> int:
        """
        Tentukan K value terbaik berdasarkan accuracy
        
        Args:
            results: List of evaluation results
            
        Returns:
            Best K value
        """
        best_k = results[0]["k"]
        best_accuracy = results[0]["accuracy"]
        
        for result in results[1:]:
            if result["accuracy"] > best_accuracy:
                best_accuracy = result["accuracy"]
                best_k = result["k"]
        
        return best_k
    
    def print_summary_table(self, results: List[Dict]):
        """
        Print summary table of K values evaluation
        """
        print("\n" + "=" * 120)
        print("SUMMARY TABEL - PERBANDINGAN K VALUES (4-CLASS CLASSIFICATION)")
        print("=" * 120)
        
        print(f"\n{'K':>3s}  {'Accuracy':>10s}  {'Macro Precision':>15s}  {'Macro Recall':>15s}  {'Macro F1':>15s}")
        print("-" * 70)
        
        for result in results:
            macro = result["macro_average"]
            print(
                f"{result['k']:>3d}  "
                f"{result['accuracy']:>10.4f}  "
                f"{macro['precision']:>15.4f}  "
                f"{macro['recall']:>15.4f}  "
                f"{macro['f1_score']:>15.4f}"
            )
        
        # Find best K
        best_k = self.determine_best_k(results)
        best_result = next(r for r in results if r['k'] == best_k)
        
        print("-" * 70)
        print(f"\n✓ BEST K: {best_k} (Accuracy: {best_result['accuracy']:.4f})")
        print("\n" + "=" * 120)
    
    def print_detailed_results(self, results: List[Dict]):
        """
        Print detailed results per K value
        """
        for result in results:
            print(f"\n{'='*100}")
            print(f"DETAILED RESULTS - K={result['k']}")
            print(f"{'='*100}")
            
            print(f"\nAccuracy: {result['accuracy']:.4f} ({result['accuracy']*100:.2f}%)")
            
            print(f"\nPER-CLASS METRICS:")
            print(f"{'Class':^20s}  {'Precision':>10s}  {'Recall':>10s}  {'F1-Score':>10s}")
            print("-" * 55)
            for cls in range(4):
                m = result["metrics_per_class"][cls]
                class_label = f"{cls}: {self.class_names[cls][:16]}"
                print(
                    f"{class_label:20s}  "
                    f"{m['precision']:>10.4f}  "
                    f"{m['recall']:>10.4f}  "
                    f"{m['f1_score']:>10.4f}"
                )
            
            macro = result["macro_average"]
            print("-" * 55)
            print(
                f"{'MACRO-AVERAGE':20s}  "
                f"{macro['precision']:>10.4f}  "
                f"{macro['recall']:>10.4f}  "
                f"{macro['f1_score']:>10.4f}"
            )


def main():
    """Main function"""
    try:
        evaluator = KNNKParameterEvaluator4Class()
        
        # Test K values
        results = evaluator.evaluate_all_k_values([3, 5, 7, 9])
        
        # Print summary
        evaluator.print_summary_table(results)
        
        # Print detailed results
        evaluator.print_detailed_results(results)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
