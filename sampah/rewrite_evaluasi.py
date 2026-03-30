"""
Rewrite api/app/routes/evaluasi.py with 4-class multi-class support
Usage: python rewrite_evaluasi.py
"""

import os
import re

# New evaluasi.py content with multi-class support
NEW_EVALUASI_CONTENT = '''"""
Routes untuk Evaluasi Kinerja Model KNN MANUAL (tanpa sklearn)
Mengevaluasi model dengan data training dari CSV (80/20 train/test split)
Multi-class classification (4 kelas)

FITUR:
- 4 Kelas: Normal+GiziBaik, Normal+KurangGizi, Stunting+GiziBaik, Stunting+KurangGizi
- Confusion Matrix: 4x4 dengan manual calculation
- Metrics: Accuracy, Precision, Recall, F1-Score per class
- K-Comparison: Evaluasi K=3,5,7,9 pada test set yang sama
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel
from app.utils.auth import get_current_user
from app.database import get_supabase
from app.ml.knn_model import get_knn_model, StuntingKNNModel
from app.ml.knn_manual import (
    calculate_confusion_matrix, 
    calculate_metrics, 
    ManualKNNClassifier,
    ManualStandardScaler
)
from app.services.prediction_service import prediction_service
import numpy as np
import os
import pandas as pd

try:
    from sklearn.model_selection import train_test_split
except ImportError:
    # Fallback if sklearn not available - manual split
    def train_test_split(X, y, test_size=0.2, random_state=None, stratify=None):
        np.random.seed(random_state)
        indices = np.arange(len(X))
        if stratify is not None:
            # Simple stratified split
            split_indices = []
            for class_label in np.unique(stratify):
                class_mask = stratify == class_label
                class_indices = indices[class_mask]
                split_point = int(len(class_indices) * (1 - test_size))
                np.random.shuffle(class_indices)
                split_indices.extend(class_indices[:split_point])
            test_mask = np.isin(indices, split_indices, invert=True)
            train_mask = ~test_mask
        else:
            np.random.shuffle(indices)
            split_point = int(len(indices) * (1 - test_size))
            train_mask = indices[:split_point]
            test_mask = indices[split_point:]
        
        return X[train_mask], X[test_mask], y[train_mask], y[test_mask]

router = APIRouter(prefix="/evaluasi", tags=["Evaluasi Model"])

# CLASS LABELS FOR 4-CLASS CLASSIFICATION
CLASS_LABELS = [
    "Normal & Gizi Baik",
    "Normal & Kurang Gizi", 
    "Stunting & Gizi Baik",
    "Stunting & Kurang Gizi"
]

CLASS_INDICES = {0, 1, 2, 3}


def map_status_to_class(status_stunting: int) -> int:
    """Map CSV status_stunting value to 4-class label"""
    status_int = int(status_stunting) if status_stunting is not None else 0
    return status_int if status_int in CLASS_INDICES else 0


def calculate_metrics_multiclass(y_true: np.ndarray, y_pred: np.ndarray, labels: List[int] = None) -> Dict[str, Any]:
    """
    Calculate multi-class metrics with 4x4 confusion matrix
    
    Returns: Dictionary with accuracy, per-class precision/recall/f1, and confusion matrix
    """
    if labels is None:
        labels = [0, 1, 2, 3]
    
    # Get confusion matrix
    cm = calculate_confusion_matrix(y_true, y_pred, labels=labels)
    
    # Overall accuracy
    accuracy = np.mean(y_true == y_pred)
    
    # Per-class metrics
    per_class_metrics = {}
    macro_precision = []
    macro_recall = []
    macro_f1 = []
    
    for i, label in enumerate(labels):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        per_class_metrics[int(label)] = {
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "support": int(np.sum(y_true == label))
        }
        
        macro_precision.append(precision)
        macro_recall.append(recall)
        macro_f1.append(f1)
    
    return {
        "accuracy": float(accuracy),
        "macro_precision": float(np.mean(macro_precision)),
        "macro_recall": float(np.mean(macro_recall)),
        "macro_f1": float(np.mean(macro_f1)),
        "per_class": per_class_metrics,
        "confusion_matrix": cm
    }


def find_csv_path() -> str:
    """Find data_latih_stunting.csv in possible locations"""
    possible_paths = [
        "backend/data_latih_stunting.csv",
        "../backend/data_latih_stunting.csv",
        "data_latih_stunting.csv",
        os.path.join(os.path.dirname(__file__), "../../backend/data_latih_stunting.csv"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    raise FileNotFoundError("data_latih_stunting.csv tidak ditemukan")


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
    Evaluasi model KNN dengan 4-class multi-class classification.
    
    Data: 80/20 train/test split dari data_latih_stunting.csv
    Classes: Normal+GiziBaik, Normal+KurangGizi, Stunting+GiziBaik, Stunting+KurangGizi
    
    Returns: 4x4 confusion matrix, per-class metrics, accuracy
    """
    if current_user.get("role") not in ["admin", "kader"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin dan Kader yang dapat mengakses evaluasi model"
        )
    
    try:
        print("=" * 80)
        print("📊 EVALUASI MODEL KNN - MULTI-CLASS (4 CLASSES)")
        print("=" * 80)
        
        # LOAD DATA FROM CSV
        csv_path = find_csv_path()
        df = pd.read_csv(csv_path)
        print(f"✅ CSV dimuat: {csv_path}")
        print(f"   Total sampel: {len(df)}")
        
        # PREPARE FEATURES & LABELS
        X_list = []
        y_list = []
        
        for _, row in df.iterrows():
            label = map_status_to_class(row.get("status_stunting", 0))
            y_list.append(label)
            
            jk_enc = 1 if str(row.get("jenis_kelamin", "L")).upper() == "L" else 0
            X_list.append([
                jk_enc,
                float(row.get("usia_bulan", 0)),
                float(row.get("tinggi_badan", 0)),
                float(row.get("berat_badan", 0)),
                float(row.get("lingkar_lengan", 0)),
                float(row.get("lingkar_kepala", 0)),
                float(row.get("zscore_bbu", 0)),
            ])
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        # TRAIN/TEST SPLIT (80/20 STRATIFIED)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=0.2,
            random_state=42,
            stratify=y
        )
        
        print(f"\\n📋 Train/Test Split:")
        print(f"   Train: {len(X_train)} samples")
        print(f"   Test: {len(X_test)} samples")
        
        # SCALING
        scaler = ManualStandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # GENDER WEIGHT
        X_train_scaled[:, 0] *= 5.0
        X_test_scaled[:, 0] *= 5.0
        
        # TRAIN KNN (K=5 default)
        knn = ManualKNNClassifier(n_neighbors=5, weights='distance')
        knn.fit(X_train_scaled, y_train)
        
        # EVALUATE
        y_pred = knn.predict(X_test_scaled)
        metrics = calculate_metrics_multiclass(y_test, y_pred, labels=[0, 1, 2, 3])
        cm = metrics["confusion_matrix"]
        
        print(f"\\n📊 Results (K=5):")
        print(f"   Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        print(f"   Macro F1: {metrics['macro_f1']:.4f}")
        print("=" * 80)
        
        return {
            "status": "success",
            "message": "Model performance evaluation completed",
            "dataset_info": {
                "source": "CSV data_latih_stunting.csv",
                "total_samples": len(df),
                "train_size": len(X_train),
                "test_size": len(X_test),
                "split_method": "stratified 80/20"
            },
            "confusion_matrix": {
                "labels": CLASS_LABELS,
                "matrix": cm.tolist()
            },
            "metrics": {
                "overall": {
                    "accuracy": round(metrics["accuracy"], 4),
                    "accuracy_pct": round(metrics["accuracy"] * 100, 2),
                    "macro_precision": round(metrics["macro_precision"], 4),
                    "macro_recall": round(metrics["macro_recall"], 4),
                    "macro_f1": round(metrics["macro_f1"], 4),
                },
                "per_class": {
                    str(i): {
                        "label": CLASS_LABELS[i],
                        "precision": round(metrics["per_class"][i]["precision"], 4),
                        "recall": round(metrics["per_class"][i]["recall"], 4),
                        "f1_score": round(metrics["per_class"][i]["f1_score"], 4),
                        "support": metrics["per_class"][i]["support"]
                    }
                    for i in range(4)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get("/compare-k-values", response_model=Dict[str, Any])
async def compare_k_values(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase),
    model: StuntingKNNModel = Depends(get_knn_model)
):
    """
    Compare K values (3, 5, 7, 9) on same 80/20 test split.
    4-class multi-class classification.
    """
    if current_user.get("role") not in ["admin", "kader"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin dan Kader yang dapat mengakses evaluasi model"
        )
    
    try:
        print("=" * 80)
        print("🔍 PERBANDINGAN K-VALUES")
        print("=" * 80)
        
        # LOAD & PREPARE DATA
        csv_path = find_csv_path()
        df = pd.read_csv(csv_path)
        
        X_list = []
        y_list = []
        
        for _, row in df.iterrows():
            label = map_status_to_class(row.get("status_stunting", 0))
            y_list.append(label)
            jk_enc = 1 if str(row.get("jenis_kelamin", "L")).upper() == "L" else 0
            X_list.append([
                jk_enc,
                float(row.get("usia_bulan", 0)),
                float(row.get("tinggi_badan", 0)),
                float(row.get("berat_badan", 0)),
                float(row.get("lingkar_lengan", 0)),
                float(row.get("lingkar_kepala", 0)),
                float(row.get("zscore_bbu", 0)),
            ])
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        # SPLIT
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # SCALE
        scaler = ManualStandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        X_train_scaled[:, 0] *= 5.0
        X_test_scaled[:, 0] *= 5.0
        
        # EVALUATE EACH K
        k_values = [3, 5, 7, 9]
        comparison_results = []
        
        print(f"\\nTest set: {len(X_test)} samples\\n")
        print(f"{'K':>3} | {'Accuracy':>8} | {'Macro F1':>8}")
        print("-" * 30)
        
        for k in k_values:
            knn = ManualKNNClassifier(n_neighbors=k, weights='distance')
            knn.fit(X_train_scaled, y_train)
            y_pred = knn.predict(X_test_scaled)
            
            metrics = calculate_metrics_multiclass(y_test, y_pred, labels=[0, 1, 2, 3])
            cm = metrics["confusion_matrix"]
            
            print(f"{k:3d} | {metrics['accuracy']:8.4f} | {metrics['macro_f1']:8.4f}")
            
            comparison_results.append({
                "k_value": k,
                "metrics": {
                    "accuracy": round(metrics["accuracy"], 4),
                    "accuracy_pct": round(metrics["accuracy"] * 100, 2),
                    "macro_f1": round(metrics["macro_f1"], 4),
                    "per_class": {
                        str(i): {
                            "label": CLASS_LABELS[i],
                            "f1_score": round(metrics["per_class"][i]["f1_score"], 4),
                        }
                        for i in range(4)
                    }
                },
                "confusion_matrix": {
                    "labels": CLASS_LABELS,
                    "matrix": cm.tolist()
                }
            })
        
        best = max(comparison_results, key=lambda x: (x["metrics"]["macro_f1"], x["k_value"]))
        
        print(f"\\n🏆 Best K: {best['k_value']} (F1: {best['metrics']['macro_f1']:.4f})")
        print("=" * 80)
        
        return {
            "status": "success",
            "message": "K comparison completed",
            "comparisons": comparison_results,
            "recommendation": {
                "best_k": best["k_value"],
                "macro_f1": best["metrics"]["macro_f1"],
                "accuracy": best["metrics"]["accuracy"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/simulate", response_model=Dict[str, Any])
async def simulate_prediction(
    input_data: SimulationInput,
    current_user: dict = Depends(get_current_user),
    model: StuntingKNNModel = Depends(get_knn_model)
):
    """Single prediction simulation"""
    try:
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
            "message": "Prediction successful",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
'''

def main():
    # Paths
    output_path = "api/app/routes/evaluasi.py"
    backup_path = output_path + ".backup"
    
    # Create backup if file exists
    if os.path.exists(output_path):
        print(f"📦 Creating backup: {backup_path}")
        with open(output_path, 'r', encoding='utf-8') as f:
            with open(backup_path, 'w', encoding='utf-8') as bf:
                bf.write(f.read())
    
    # Write new file
    print(f"✍️  Writing new file: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(NEW_EVALUASI_CONTENT)
    
    # Verify
    with open(output_path, 'r', encoding='utf-8') as f:
        lines = len(f.readlines())
    
    print(f"✅ Success!")
    print(f"   File: {output_path}")
    print(f"   Lines: {lines}")
    print(f"   Size: {os.path.getsize(output_path)} bytes")
    print(f"\n📝 Changes:")
    print(f"   ✓ Added 4-class multi-class support")
    print(f"   ✓ Removed pengukuran table fetch")
    print(f"   ✓ Added 80/20 train/test split from CSV")
    print(f"   ✓ Added calculate_metrics_multiclass()")
    print(f"   ✓ Updated /model-performance endpoint")
    print(f"   ✓ Updated /compare-k-values endpoint")
    print(f"   ✓ 4x4 confusion matrix support")

if __name__ == "__main__":
    main()
