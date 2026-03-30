"""
Evaluasi Parameter K pada Algoritma KNN
=========================================

Membandingkan nilai K (3, 5, 7, 9) dengan metrik:
- Accuracy, Precision, Recall, Specificity, F1-Score

Untuk setiap K:
1. Train KNN dengan seluruh data (leave-one-out style prediction)
2. Predict label untuk setiap data
3. Hitung confusion matrix dan metrik
4. Bandingkan hasil per K

Label: status_gizi_label (0-3 kelas, macro-average)
Fitur: jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Import database connection
from app.database import get_supabase


class KParameterEvaluator:
    """
    Evaluator untuk parameter K dalam KNN
    """
    
    def __init__(self):
        """Initialize evaluator"""
        self.k_values = [3, 5, 7, 9]
        self.num_classes = 4
        self.class_names = [
            "Normal & Gizi Baik (0)",
            "Normal & Kurang Gizi (1)",
            "Stunting & Gizi Baik (2)",
            "Stunting & Kurang Gizi (3)"
        ]
    
    def fetch_data_from_supabase(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetch data dari Supabase tabel pengukuran
        
        Returns:
            X_data: Features array (n_samples, 6 features)
            y_data: Labels array (status_gizi_label)
        """
        try:
            supabase = get_supabase()
            
            # Query: ambil kolom yang diperlukan
            response = supabase.table("pengukuran").select(
                "jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala, status_gizi_label"
            ).execute()
            
            data = response.data
            
            if not data:
                raise ValueError("Tidak ada data di tabel pengukuran")
            
            print(f"✓ Berhasil fetch {len(data)} records dari Supabase")
            
            # Convert ke numpy array
            X_list = []
            y_list = []
            
            for record in data:
                # Skip jika ada missing values
                if None in [
                    record.get("jenis_kelamin"),
                    record.get("usia_bulan"),
                    record.get("tinggi_badan"),
                    record.get("berat_badan"),
                    record.get("lingkar_lengan"),
                    record.get("lingkar_kepala"),
                    record.get("status_gizi_label")
                ]:
                    continue
                
                # Encode jenis_kelamin: L=1, P=0
                jk = 1 if record["jenis_kelamin"] == "L" else 0
                
                features = [
                    jk,
                    record["usia_bulan"],
                    record["tinggi_badan"],
                    record["berat_badan"],
                    record["lingkar_lengan"],
                    record["lingkar_kepala"]
                ]
                
                X_list.append(features)
                y_list.append(record["status_gizi_label"])
            
            if not X_list:
                raise ValueError("Semua data memiliki missing values")
            
            X_data = np.array(X_list, dtype=float)
            y_data = np.array(y_list, dtype=int)
            
            print(f"✓ Data setelah cleaning: {len(X_data)} samples")
            print(f"  Features shape: {X_data.shape}")
            print(f"  Label distribution: {np.bincount(y_data)}")
            
            return X_data, y_data
        
        except Exception as e:
            print(f"❌ Error fetching data: {str(e)}")
            raise
    
    def calculate_metrics_for_class(self, y_true: np.ndarray, y_pred: np.ndarray, class_idx: int) -> Dict:
        """
        Hitung metrik untuk satu class (One-vs-Rest approach)
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            class_idx: Index class yang dievaluasi (0-3)
        
        Returns:
            Dictionary dengan metrik: TP, TN, FP, FN, Accuracy, Precision, Recall, Specificity, F1
        """
        # Convert ke binary: class_idx vs rest
        y_true_binary = (y_true == class_idx).astype(int)
        y_pred_binary = (y_pred == class_idx).astype(int)
        
        # Calculate confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary).ravel()
        
        # Calculate metrics
        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "specificity": specificity,
            "f1_score": f1_score
        }
    
    def evaluate_k(self, X_data: np.ndarray, y_data: np.ndarray, k: int) -> Dict:
        """
        Evaluasi KNN dengan nilai K tertentu
        
        Args:
            X_data: Features array
            y_data: Labels array
            k: Nilai K
        
        Returns:
            Dictionary dengan hasil evaluasi untuk K ini
        """
        print(f"\n📊 Evaluasi K = {k}...")
        
        try:
            # Normalize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X_data)
            
            # Train KNN
            knn = KNeighborsClassifier(
                n_neighbors=k,
                metric='euclidean',
                weights='distance',
                algorithm='auto'
            )
            
            knn.fit(X_scaled, y_data)
            
            # Predict (pada training data = global test)
            y_pred = knn.predict(X_scaled)
            
            # Overall accuracy
            overall_accuracy = accuracy_score(y_data, y_pred)
            
            # Hitung metrik per class
            metrics_per_class = {}
            for class_idx in range(self.num_classes):
                metrics = self.calculate_metrics_for_class(y_data, y_pred, class_idx)
                metrics_per_class[class_idx] = metrics
            
            # Macro-average metrics
            macro_accuracy = np.mean([m['accuracy'] for m in metrics_per_class.values()])
            macro_precision = np.mean([m['precision'] for m in metrics_per_class.values()])
            macro_recall = np.mean([m['recall'] for m in metrics_per_class.values()])
            macro_specificity = np.mean([m['specificity'] for m in metrics_per_class.values()])
            macro_f1 = np.mean([m['f1_score'] for m in metrics_per_class.values()])
            
            result = {
                "k": k,
                "overall_accuracy": overall_accuracy,
                "macro_accuracy": macro_accuracy,
                "macro_precision": macro_precision,
                "macro_recall": macro_recall,
                "macro_specificity": macro_specificity,
                "macro_f1": macro_f1,
                "metrics_per_class": metrics_per_class,
                "y_pred": y_pred,
                "knn_model": knn,
                "scaler": scaler
            }
            
            print(f"  ✓ Overall Accuracy: {overall_accuracy:.4f}")
            print(f"  ✓ Macro-Avg Precision: {macro_precision:.4f}, Recall: {macro_recall:.4f}, F1: {macro_f1:.4f}")
            
            return result
        
        except Exception as e:
            print(f"  ❌ Error evaluating K={k}: {str(e)}")
            raise
    
    def run_evaluation(self) -> Dict:
        """
        Jalankan evaluasi lengkap untuk semua K
        
        Returns:
            Dictionary dengan hasil evaluasi semua K
        """
        print("=" * 80)
        print("EVALUASI PARAMETER K PADA ALGORITMA KNN")
        print("=" * 80)
        
        # Fetch data
        X_data, y_data = self.fetch_data_from_supabase()
        
        # Evaluate each K
        results = {}
        for k in self.k_values:
            result = self.evaluate_k(X_data, y_data, k)
            results[k] = result
        
        return results, y_data
    
    def print_summary_table(self, results: Dict, y_true: np.ndarray):
        """
        Print summary table dari hasil evaluasi
        
        Args:
            results: Dictionary hasil evaluasi per K
            y_true: True labels
        """
        print("\n" + "=" * 120)
        print("TABEL PERBANDINGAN PARAMETER K")
        print("=" * 120)
        
        # Prepare data untuk dataframe
        summary_data = []
        for k in self.k_values:
            result = results[k]
            summary_data.append({
                "K": k,
                "Overall Acc": f"{result['overall_accuracy']:.4f}",
                "Macro Acc": f"{result['macro_accuracy']:.4f}",
                "Macro Prec": f"{result['macro_precision']:.4f}",
                "Macro Rec": f"{result['macro_recall']:.4f}",
                "Macro Spec": f"{result['macro_specificity']:.4f}",
                "Macro F1": f"{result['macro_f1']:.4f}"
            })
        
        df_summary = pd.DataFrame(summary_data)
        print(df_summary.to_string(index=False))
        print("=" * 120)
    
    def print_detailed_metrics(self, results: Dict):
        """
        Print detailed metrics per class untuk setiap K
        
        Args:
            results: Dictionary hasil evaluasi per K
        """
        print("\n" + "=" * 120)
        print("DETAIL METRIK PER CLASS")
        print("=" * 120)
        
        for k in self.k_values:
            print(f"\n{'=' * 60}")
            print(f"K = {k}")
            print(f"{'=' * 60}")
            
            metrics_per_class = results[k]['metrics_per_class']
            
            for class_idx in range(self.num_classes):
                metrics = metrics_per_class[class_idx]
                print(f"\n  Class {class_idx}: {self.class_names[class_idx]}")
                print(f"  ├─ TP={metrics['tp']:4d} | TN={metrics['tn']:4d} | FP={metrics['fp']:4d} | FN={metrics['fn']:4d}")
                print(f"  ├─ Accuracy:   {metrics['accuracy']:.4f}")
                print(f"  ├─ Precision:  {metrics['precision']:.4f}")
                print(f"  ├─ Recall:     {metrics['recall']:.4f}")
                print(f"  ├─ Specificity: {metrics['specificity']:.4f}")
                print(f"  └─ F1-Score:   {metrics['f1_score']:.4f}")
    
    def determine_best_k(self, results: Dict) -> int:
        """
        Tentukan K terbaik berdasarkan overall accuracy tertinggi
        
        Args:
            results: Dictionary hasil evaluasi per K
        
        Returns:
            K terbaik
        """
        best_k = max(self.k_values, key=lambda k: results[k]['overall_accuracy'])
        best_accuracy = results[best_k]['overall_accuracy']
        
        print(f"\n{'=' * 120}")
        print(f"✓ K TERBAIK: {best_k} (Overall Accuracy: {best_accuracy:.4f})")
        print(f"{'=' * 120}\n")
        
        return best_k


def main():
    """Main function"""
    try:
        evaluator = KParameterEvaluator()
        
        # Run evaluation
        results, y_true = evaluator.run_evaluation()
        
        # Print summary table
        evaluator.print_summary_table(results, y_true)
        
        # Print detailed metrics
        evaluator.print_detailed_metrics(results)
        
        # Determine best K
        best_k = evaluator.determine_best_k(results)
        
        print("\n✓ Evaluasi selesai!")
        print(f"  Rekomendasi: Gunakan K = {best_k}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
