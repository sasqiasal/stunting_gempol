"""
Evaluasi Model KNN Global (Admin Dashboard)
=============================================

Evaluasi performa KNN secara global menggunakan semua data:
- Fetch semua data dari tabel `pengukuran`
- Jangan filter user_id atau bulan
- Gunakan K=5 (nilai terbaik dari evaluasi sebelumnya)
- Hitung confusion matrix dan metrik dalam format binary (Normal vs Stunting)

Ground truth: status_gizi_label
Binary conversion: 0,1=Normal(0), 2,3=Stunting(1)

Untuk: Admin dashboard / ringkasan performa model keseluruhan
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')

from app.database import get_supabase


class KNNGlobalEvaluator:
    """
    Evaluator untuk model KNN secara global (semua data)
    """
    
    def __init__(self, k: int = 5):
        """
        Initialize evaluator
        
        Args:
            k: Nilai K untuk KNN (default: 5)
        """
        self.k = k
        self.scaler = StandardScaler()
        self.knn_model = None
    
    def fetch_all_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetch semua data dari tabel pengukuran
        
        Returns:
            X_data: Features array
            y_data: Labels array
        """
        try:
            supabase = get_supabase()
            
            # Fetch semua data
            response = supabase.table("pengukuran").select(
                "jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala, status_gizi_label"
            ).execute()
            
            data = response.data
            
            if not data:
                raise ValueError("Tidak ada data di tabel pengukuran")
            
            print(f"✓ Fetch semua data: {len(data)} records")
            
            # Convert ke numpy array
            X_list = []
            y_list = []
            
            for record in data:
                # Skip missing values
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
            print(f"  Label distribution: Normal={np.sum(y_data < 2)}, Stunting={np.sum(y_data >= 2)}")
            
            return X_data, y_data
        
        except Exception as e:
            print(f"❌ Error fetching all data: {str(e)}")
            raise
    
    def convert_to_binary(self, labels: np.ndarray) -> np.ndarray:
        """
        Convert 4-class labels to binary (stunting/normal)
        
        Args:
            labels: Array dari status_gizi_label (0-3)
        
        Returns:
            Binary array: 0=Normal(0,1), 1=Stunting(2,3)
        """
        return (labels >= 2).astype(int)
    
    def evaluate_global(self) -> Dict:
        """
        Evaluasi KNN secara global
        
        Returns:
            Dictionary dengan hasil evaluasi
        """
        print("\n" + "=" * 80)
        print(f"EVALUASI KNN GLOBAL (K={self.k})")
        print("=" * 80)
        
        try:
            # Fetch semua data
            print("\n📊 Step 1: Fetch semua data...")
            X_data, y_data = self.fetch_all_data()
            
            # Normalize features
            print("\n🔧 Step 2: Normalize features dan prepare model...")
            self.scaler.fit(X_data)
            X_scaled = self.scaler.transform(X_data)
            
            # Initialize dan train KNN
            self.knn_model = KNeighborsClassifier(
                n_neighbors=self.k,
                metric='euclidean',
                weights='distance',
                algorithm='auto'
            )
            
            self.knn_model.fit(X_scaled, y_data)
            print(f"✓ Model KNN (K={self.k}) trained dengan {len(X_data)} samples")
            
            # Predict
            print("\n🎯 Step 3: Make predictions...")
            y_pred = self.knn_model.predict(X_scaled)
            
            # Convert to binary
            y_true_binary = self.convert_to_binary(y_data)
            y_pred_binary = self.convert_to_binary(y_pred)
            
            # Calculate confusion matrix
            print("\n📈 Step 4: Calculate confusion matrix...")
            tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary).ravel()
            
            # Calculate metrics
            total = tp + tn + fp + fn
            accuracy = (tp + tn) / total if total > 0 else 0.0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            result = {
                "k": self.k,
                "n_total_samples": len(X_data),
                "confusion_matrix": {
                    "tp": int(tp),
                    "tn": int(tn),
                    "fp": int(fp),
                    "fn": int(fn)
                },
                "metrics": {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "specificity": specificity,
                    "f1_score": f1_score
                },
                "label_distribution": {
                    "normal_true": int(np.sum(y_true_binary == 0)),
                    "stunting_true": int(np.sum(y_true_binary == 1)),
                    "normal_pred": int(np.sum(y_pred_binary == 0)),
                    "stunting_pred": int(np.sum(y_pred_binary == 1))
                },
                "class_distribution_4class": {
                    "0": int(np.sum(y_data == 0)),
                    "1": int(np.sum(y_data == 1)),
                    "2": int(np.sum(y_data == 2)),
                    "3": int(np.sum(y_data == 3))
                }
            }
            
            return result
        
        except Exception as e:
            print(f"❌ Error evaluating: {str(e)}")
            raise
    
    def print_results(self, result: Dict):
        """
        Print hasil evaluasi
        
        Args:
            result: Dictionary hasil evaluasi
        """
        print("\n" + "=" * 100)
        print("HASIL EVALUASI KNN GLOBAL (ADMIN DASHBOARD)")
        print("=" * 100)
        
        # Header
        print(f"\nParameter: K={result['k']}")
        print(f"Total Samples: {result['n_total_samples']}")
        
        # 4-Class Distribution
        print(f"\n📊 4-CLASS LABEL DISTRIBUTION:")
        class_names = {
            0: "Normal & Gizi Baik",
            1: "Normal & Kurang Gizi",
            2: "Stunting & Gizi Baik",
            3: "Stunting & Kurang Gizi"
        }
        for i in range(4):
            count = result['class_distribution_4class'][str(i)]
            pct = (count / result['n_total_samples']) * 100
            print(f"  Class {i}: {class_names[i]:30s} = {count:4d} ({pct:5.2f}%)")
        
        # Binary Distribution
        print(f"\n📊 BINARY LABEL DISTRIBUTION:")
        print(f"  Actual:     Normal={result['label_distribution']['normal_true']:4d}, Stunting={result['label_distribution']['stunting_true']:4d}")
        print(f"  Predicted:  Normal={result['label_distribution']['normal_pred']:4d}, Stunting={result['label_distribution']['stunting_pred']:4d}")
        
        # Confusion Matrix
        cm = result['confusion_matrix']
        print(f"\n🔲 CONFUSION MATRIX (Binary):")
        print(f"  ┌─────────────────────────────────────────────┐")
        print(f"  │              PREDICTED                      │")
        print(f"  │      Normal (0)      │      Stunting (1)    │")
        print(f"  ├─────────────────────────────────────────────┤")
        print(f"  │ A              │              │              │")
        print(f"  │ C Normal (0)   │  TN={cm['tn']:5d}  │  FP={cm['fp']:5d}    │")
        print(f"  │ T              │              │              │")
        print(f"  │ U Stunting (1) │  FN={cm['fn']:5d}  │  TP={cm['tp']:5d}    │")
        print(f"  │ A              │              │              │")
        print(f"  │ L              │              │              │")
        print(f"  └─────────────────────────────────────────────┘")
        
        # Metrics
        m = result['metrics']
        print(f"\n📈 METRICS (Global):")
        print(f"  ├─ Accuracy:    {m['accuracy']:.4f} ({m['accuracy']*100:.2f}%)")
        print(f"  │  └─ Benar prediksi dari {cm['tp']+cm['tn']} dari total {result['n_total_samples']}")
        print(f"  │")
        print(f"  ├─ Precision:   {m['precision']:.4f}")
        print(f"  │  └─ Dari {cm['tp']+cm['fp']} prediksi Stunting, {cm['tp']} yang benar")
        print(f"  │")
        print(f"  ├─ Recall:      {m['recall']:.4f} (PENTING!)")
        print(f"  │  └─ Dari {cm['tp']+cm['fn']} Stunting aktual, {cm['tp']} yang terdeteksi")
        print(f"  │")
        print(f"  ├─ Specificity: {m['specificity']:.4f}")
        print(f"  │  └─ Dari {cm['tn']+cm['fp']} Normal aktual, {cm['tn']} yang terdeteksi")
        print(f"  │")
        print(f"  └─ F1-Score:    {m['f1_score']:.4f}")
        print(f"     └─ Balance antara Precision dan Recall")
        
        print("\n" + "=" * 100)
    
    def get_interpretation(self, result: Dict) -> str:
        """
        Get interpretasi hasil evaluasi global
        
        Args:
            result: Dictionary hasil evaluasi
        
        Returns:
            String interpretasi
        """
        m = result['metrics']
        
        # Performance level
        if m['accuracy'] >= 0.85:
            performance = "Excellent"
            performance_emoji = "🟢"
        elif m['accuracy'] >= 0.75:
            performance = "Good"
            performance_emoji = "🟡"
        elif m['accuracy'] >= 0.65:
            performance = "Fair"
            performance_emoji = "🟠"
        else:
            performance = "Poor"
            performance_emoji = "🔴"
        
        interpretation = f"{performance_emoji} Overall Performance: {performance} (Accuracy: {m['accuracy']*100:.2f}%)\n\n"
        
        # Recall analysis (most critical)
        interpretation += "📋 Recall Analysis (Coverage of Stunting Detection):\n"
        if m['recall'] >= 0.85:
            interpretation += "  ✓ Excellent: Model detects 85%+ of actual stunting cases\n"
        elif m['recall'] >= 0.75:
            interpretation += "  ✓ Good: Model detects 75-85% of actual stunting cases\n"
        elif m['recall'] >= 0.65:
            interpretation += "  ⚠ Fair: Model detects 65-75% of stunting cases (needs improvement)\n"
        else:
            interpretation += "  ❌ Poor: Model misses 30%+ of stunting cases (critical issue)\n"
        
        # Precision analysis
        interpretation += "\n📋 Precision Analysis (True Positive Rate):\n"
        if m['precision'] >= 0.80:
            interpretation += "  ✓ High: 80%+ of predicted stunting are correct\n"
        elif m['precision'] >= 0.60:
            interpretation += "  ⚠ Moderate: 60-80% of predicted stunting are correct\n"
        else:
            interpretation += "  ❌ Low: Less than 60% accuracy in positive predictions\n"
        
        # Specificity
        interpretation += "\n📋 Specificity Analysis (Normal Detection):\n"
        if m['specificity'] >= 0.85:
            interpretation += "  ✓ Excellent: 85%+ of normal cases correctly identified\n"
        else:
            interpretation += "  ⚠ Check: Less than 85% accuracy for normal cases\n"
        
        # Overall recommendation
        interpretation += "\n📊 Recommendation:\n"
        if m['accuracy'] >= 0.85 and m['recall'] >= 0.80:
            interpretation += "  ✓ Model is ready for production use\n"
        elif m['recall'] >= 0.75:
            interpretation += "  ⚠ Model can be used with monitoring on false negatives\n"
        else:
            interpretation += "  ❌ Model needs improvement before production deployment\n"
        
        return interpretation


def main():
    """Main function"""
    try:
        # Initialize evaluator
        evaluator = KNNGlobalEvaluator(k=5)
        
        # Run evaluation
        result = evaluator.evaluate_global()
        
        # Print results
        evaluator.print_results(result)
        
        # Print interpretation
        print("\n💡 INTERPRETASI & REKOMENDASI:")
        print(evaluator.get_interpretation(result))
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
