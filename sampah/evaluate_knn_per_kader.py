"""
Evaluasi Model KNN per Kader
=============================

Mengevaluasi performa KNN untuk data pengukuran dari kader tertentu:
- Filter berdasarkan user_id (kader)
- Filter berdasarkan bulan (opsional)
- Gunakan K=5 (nilai terbaik dari evaluasi sebelumnya)
- Hitung confusion matrix dan metrik

Fitur:
- Semua bulan (default)
- Per bulan spesifik

Ground truth: status_gizi_label
Binary conversion: 0,1=Normal(0), 2,3=Stunting(1)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')

from app.database import get_supabase


class KNNKaderEvaluator:
    """
    Evaluator untuk model KNN per kader (user)
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
        self.training_data_X = None
        self.training_data_y = None
    
    def fetch_all_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetch semua data untuk training/fitting scaler
        
        Returns:
            X_data: Features array
            y_data: Labels array
        """
        try:
            supabase = get_supabase()
            
            # Fetch semua data (untuk training model)
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
            
            return X_data, y_data
        
        except Exception as e:
            print(f"❌ Error fetching all data: {str(e)}")
            raise
    
    def fetch_kader_data(
        self,
        user_id: int,
        month: Optional[int] = None,
        year: int = 2024
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetch data untuk kader tertentu
        
        Args:
            user_id: ID kader/user
            month: Bulan (1-12), None=semua bulan
            year: Tahun (default: 2024)
        
        Returns:
            X_data: Features array untuk kader
            y_data: Labels array untuk kader
        """
        try:
            supabase = get_supabase()
            
            # Query data berdasarkan user_id
            query = supabase.table("pengukuran").select(
                "id, jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala, status_gizi_label, tanggal_pengukuran"
            ).eq("kader_id", user_id)  # Filter by kader_id (user_id)
            
            response = query.execute()
            data = response.data
            
            if not data:
                raise ValueError(f"Tidak ada data untuk kader_id={user_id}")
            
            print(f"✓ Fetch data kader_id={user_id}: {len(data)} records")
            
            # Filter by bulan jika specified
            if month is not None:
                data_filtered = []
                for record in data:
                    try:
                        if isinstance(record['tanggal_pengukuran'], str):
                            date_obj = datetime.fromisoformat(record['tanggal_pengukuran'].replace('Z', '+00:00'))
                        else:
                            date_obj = record['tanggal_pengukuran']
                        
                        if date_obj.month == month and date_obj.year == year:
                            data_filtered.append(record)
                    except:
                        pass
                
                data = data_filtered
                print(f"✓ Filter bulan={month}/{year}: {len(data)} records")
            
            if not data:
                raise ValueError(f"Tidak ada data untuk bulan={month}")
            
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
                raise ValueError("Semua data kader memiliki missing values")
            
            X_data = np.array(X_list, dtype=float)
            y_data = np.array(y_list, dtype=int)
            
            print(f"✓ Data kader setelah cleaning: {len(X_data)} samples")
            
            return X_data, y_data
        
        except Exception as e:
            print(f"❌ Error fetching kader data: {str(e)}")
            raise
    
    def prepare_model(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Prepare KNN model dengan training data
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        # Normalize features
        self.scaler.fit(X_train)
        X_scaled = self.scaler.transform(X_train)
        
        # Initialize dan train KNN
        self.knn_model = KNeighborsClassifier(
            n_neighbors=self.k,
            metric='euclidean',
            weights='distance',
            algorithm='auto'
        )
        
        self.knn_model.fit(X_scaled, y_train)
        self.training_data_X = X_train
        self.training_data_y = y_train
        
        print(f"✓ Model KNN (K={self.k}) sudah trained dengan {len(X_train)} samples")
    
    def convert_to_binary(self, labels: np.ndarray) -> np.ndarray:
        """
        Convert 4-class labels to binary (stunting/normal)
        
        Args:
            labels: Array dari status_gizi_label (0-3)
        
        Returns:
            Binary array: 0=Normal(0,1), 1=Stunting(2,3)
        """
        # 0,1 -> Normal (0), 2,3 -> Stunting (1)
        return (labels >= 2).astype(int)
    
    def evaluate_kader(
        self,
        user_id: int,
        month: Optional[int] = None,
        year: int = 2024
    ) -> Dict:
        """
        Evaluasi KNN untuk kader tertentu
        
        Args:
            user_id: ID kader
            month: Bulan (opsional)
            year: Tahun
        
        Returns:
            Dictionary dengan hasil evaluasi
        """
        print("\n" + "=" * 80)
        print(f"EVALUASI KNN UNTUK KADER (user_id={user_id}, K={self.k})")
        print("=" * 80)
        
        try:
            # Fetch semua data untuk training
            print("\n📊 Step 1: Fetch data training (semua data)...")
            X_train, y_train = self.fetch_all_data()
            
            # Prepare model
            print("\n🔧 Step 2: Prepare KNN model...")
            self.prepare_model(X_train, y_train)
            
            # Fetch data kader
            print(f"\n📊 Step 3: Fetch data kader (user_id={user_id})...")
            X_kader, y_kader = self.fetch_kader_data(user_id, month=month, year=year)
            
            # Predict
            print("\n🎯 Step 4: Make predictions...")
            X_kader_scaled = self.scaler.transform(X_kader)
            y_pred = self.knn_model.predict(X_kader_scaled)
            
            # Convert to binary
            y_true_binary = self.convert_to_binary(y_kader)
            y_pred_binary = self.convert_to_binary(y_pred)
            
            # Calculate confusion matrix
            print("\n📈 Step 5: Calculate confusion matrix...")
            tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary).ravel()
            
            # Calculate metrics
            total = tp + tn + fp + fn
            accuracy = (tp + tn) / total if total > 0 else 0.0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            result = {
                "user_id": user_id,
                "month": month,
                "year": year,
                "k": self.k,
                "n_samples": len(X_kader),
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
                }
            }
            
            return result
        
        except Exception as e:
            print(f"❌ Error evaluating kader: {str(e)}")
            raise
    
    def print_results(self, result: Dict):
        """
        Print hasil evaluasi
        
        Args:
            result: Dictionary hasil evaluasi
        """
        print("\n" + "=" * 100)
        print("HASIL EVALUASI KNN PER KADER")
        print("=" * 100)
        
        # Header
        month_str = f"Bulan {result['month']}" if result['month'] else "Semua Bulan"
        print(f"\nKader: user_id={result['user_id']}")
        print(f"Period: {month_str}/{result['year']}")
        print(f"Parameter: K={result['k']}")
        print(f"Total Samples: {result['n_samples']}")
        
        # Label Distribution
        print(f"\n📊 LABEL DISTRIBUTION:")
        print(f"  Actual:  Normal={result['label_distribution']['normal_true']}, Stunting={result['label_distribution']['stunting_true']}")
        print(f"  Predicted: Normal={result['label_distribution']['normal_pred']}, Stunting={result['label_distribution']['stunting_pred']}")
        
        # Confusion Matrix
        cm = result['confusion_matrix']
        print(f"\n🔲 CONFUSION MATRIX:")
        print(f"  ┌─────────────────────────────────────────┐")
        print(f"  │              Predicted                  │")
        print(f"  │      Normal (0)    │    Stunting (1)    │")
        print(f"  ├─────────────────────────────────────────┤")
        print(f"  │ Actual   Normal (0)│  TN={cm['tn']:4d}  │  FP={cm['fp']:4d}    │")
        print(f"  │ Stunting (1)│  FN={cm['fn']:4d}  │  TP={cm['tp']:4d}    │")
        print(f"  └─────────────────────────────────────────┘")
        
        # Metrics
        m = result['metrics']
        print(f"\n📈 METRICS:")
        print(f"  ├─ Accuracy:    {m['accuracy']:.4f} ({m['accuracy']*100:.2f}%)")
        print(f"  ├─ Precision:   {m['precision']:.4f} (dari {cm['tp']+cm['fp']} predicted positive)")
        print(f"  ├─ Recall:      {m['recall']:.4f} (deteksi dari {cm['tp']+cm['fn']} actual positive)")
        print(f"  ├─ Specificity: {m['specificity']:.4f} (deteksi dari {cm['tn']+cm['fp']} actual negative)")
        print(f"  └─ F1-Score:    {m['f1_score']:.4f}")
        
        print("\n" + "=" * 100)
    
    def get_interpretation(self, result: Dict) -> str:
        """
        Get interpretasi hasil evaluasi
        
        Args:
            result: Dictionary hasil evaluasi
        
        Returns:
            String interpretasi
        """
        m = result['metrics']
        
        if m['accuracy'] >= 0.85:
            performance = "Excellent"
        elif m['accuracy'] >= 0.75:
            performance = "Good"
        elif m['accuracy'] >= 0.65:
            performance = "Fair"
        else:
            performance = "Poor"
        
        interpretation = f"Model performance: {performance} (Accuracy: {m['accuracy']*100:.2f}%)\n"
        
        # Check recall (most important in medical context)
        if m['recall'] >= 0.80:
            interpretation += "✓ Recall tinggi: Model berhasil mendeteksi stunting dengan baik\n"
        elif m['recall'] >= 0.60:
            interpretation += "⚠ Recall sedang: Ada beberapa stunting yang terlewat\n"
        else:
            interpretation += "❌ Recall rendah: Banyak stunting yang tidak terdeteksi\n"
        
        # Check precision
        if m['precision'] >= 0.80:
            interpretation += "✓ Precision tinggi: Prediksi stunting cukup akurat\n"
        elif m['precision'] >= 0.60:
            interpretation += "⚠ Precision sedang: Ada false positive\n"
        else:
            interpretation += "❌ Precision rendah: Banyak false positive\n"
        
        return interpretation


def main():
    """Main function"""
    try:
        # Example usage
        evaluator = KNNKaderEvaluator(k=5)
        
        # Evaluate untuk user_id=1 (kader pertama), semua bulan
        result = evaluator.evaluate_kader(user_id=1)
        
        # Print results
        evaluator.print_results(result)
        
        # Print interpretation
        print("\n💡 INTERPRETASI:")
        print(evaluator.get_interpretation(result))
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
