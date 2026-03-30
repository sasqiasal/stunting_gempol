"""
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
    """Find data_latih_stunting.csv using multiple strategies for path resolution"""
    
    # Strategy 1: Check environment variable (KNN_DATA_PATH)
    csv_env = os.getenv('KNN_DATA_PATH')
    if csv_env and os.path.exists(csv_env):
        print(f"✅ CSV path from environment: {csv_env}")
        return os.path.abspath(csv_env)
    
    # Strategy 2: Resolve from current working directory
    current_dir = os.getcwd()
    
    # Strategy 3: Resolve from script location (__file__)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # From /api/app/routes/ → go up to /api/ → then to / → then to /backend/
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    
    possible_paths = [
        # Absolute from project root
        os.path.join(project_root, "backend", "data_latih_stunting.csv"),
        
        # Relative to current working directory
        os.path.join(current_dir, "backend", "data_latih_stunting.csv"),
        os.path.join(current_dir, "data_latih_stunting.csv"),
        
        # Relative to script
        "backend/data_latih_stunting.csv",
        "../backend/data_latih_stunting.csv",
        "../../backend/data_latih_stunting.csv",
        os.path.join(script_dir, "../../../backend/data_latih_stunting.csv"),
    ]
    
    # Try each path
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            print(f"✅ CSV found at: {abs_path}")
            return abs_path
    
    # If still not found, provide detailed error
    error_msg = (
        f"❌ data_latih_stunting.csv not found.\n"
        f"Project root: {project_root}\n"
        f"Current dir: {current_dir}\n"
        f"Tried paths:\n"
    )
    for path in possible_paths:
        error_msg += f"  - {os.path.abspath(path)}\n"
    error_msg += f"\nPlease set KNN_DATA_PATH environment variable or ensure file exists."
    
    print(error_msg)
    raise FileNotFoundError(error_msg)


class SimulationInput(BaseModel):
    jenis_kelamin: Literal["L", "P"]
    usia_bulan: int
    tinggi_badan: float
    berat_badan: float
    lingkar_lengan: float
    lingkar_kepala: float


def calculate_confusion_matrix_from_measurements(
    supabase_client
) -> Dict[str, Any]:
    """
    Calculate confusion matrix from actual pengukuran records in database.
    
    Ground truth: zscore_tbu < -2.0 untuk stunting (WHO standard)
    Prediction: status_gizi string converted to binary (Stunting* = 1, Normal* = 0)
    
    Returns:
    - y_true: array of actual status (0=normal, 1=stunting)
    - y_pred: array of predicted status (0=normal, 1=stunting)
    - measurements_count: jumlah pengukuran yang dievaluasi
    - metrics: TP, TN, FP, FN, accuracy, precision, recall, specificity, f1
    """
    
    print("=" * 80)
    print("📊 CALCULATING CONFUSION MATRIX FROM REAL MEASUREMENTS")
    print("=" * 80)
    
    try:
        # 1. FETCH ALL PENGUKURAN FROM DATABASE
        # Select * to get all columns including status_gizi (not status_gizi_label which is calculated)
        pengukuran_response = supabase_client.table("pengukuran").select("*").execute()
        
        if not pengukuran_response.data:
            print("⚠️ No measurements found in database")
            return {
                "y_true": np.array([]),
                "y_pred": np.array([]),
                "measurements_count": 0,
                "metrics": None,
                "error": "No measurements found"
            }
        
        pengukuran_list = pengukuran_response.data
        print(f"✅ Fetched {len(pengukuran_list)} measurements from database")
        
        # 2. PREPARE GROUND TRUTH AND PREDICTIONS
        y_true = []  # 0 = normal, 1 = stunting (from zscore_tbu)
        y_pred = []  # 0 = normal, 1 = stunting (from status_gizi)
        
        # Status gizi mapping
        STATUS_GIZI_MAPPING = {
            "Normal + Gizi Baik": 0,
            "Normal + Kurang Gizi": 0,  # Both map to normal (0)
            "Stunting + Gizi Baik": 1,
            "Stunting + Kurang Gizi": 1,  # Both map to stunting (1)
        }
        
        for pengukuran in pengukuran_list:
            # GROUND TRUTH: zscore_tbu < -2.0 indicates stunting (WHO standard)
            zscore_tbu = pengukuran.get("zscore_tbu", 0) or 0
            actual_status = 1 if zscore_tbu < -2.0 else 0
            y_true.append(actual_status)
            
            # PREDICTION: status_gizi string (from model prediction)
            # Map to binary: "Stunting*" → 1, "Normal*" → 0
            status_gizi = pengukuran.get("status_gizi", "Normal + Gizi Baik") or "Normal + Gizi Baik"
            pred_status = STATUS_GIZI_MAPPING.get(status_gizi, 0)
            y_pred.append(pred_status)
        
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        print(f"\n📊 Data Summary:")
        print(f"   Total measurements: {len(y_true)}")
        print(f"   Actual stunting: {np.sum(y_true)} ({np.mean(y_true)*100:.1f}%)")
        print(f"   Predicted stunting: {np.sum(y_pred)} ({np.mean(y_pred)*100:.1f}%)")
        
        # 3. CALCULATE CONFUSION MATRIX (BINARY: stunting vs normal)
        cm = calculate_confusion_matrix(y_true, y_pred, labels=[0, 1])
        
        # Extract TP, TN, FP, FN
        # cm[0,0] = TN (actual=0, pred=0)
        # cm[0,1] = FP (actual=0, pred=1)
        # cm[1,0] = FN (actual=1, pred=0)
        # cm[1,1] = TP (actual=1, pred=1)
        tn = int(cm[0, 0])
        fp = int(cm[0, 1])
        fn = int(cm[1, 0])
        tp = int(cm[1, 1])
        
        # 4. CALCULATE METRICS
        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n📊 Confusion Matrix (Binary: Normal vs Stunting):")
        print(f"   Rows=Actual, Cols=Predicted")
        print(f"     Normal  Stunt")
        print(f"Norm {tn:5d}  {fp:5d}")
        print(f"Stun {fn:5d}  {tp:5d}")
        
        print(f"\n📊 Metrics:")
        print(f"   TP={tp}, TN={tn}, FP={fp}, FN={fn}")
        print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"   Precision: {precision:.4f} ({precision*100:.2f}%)")
        print(f"   Recall:    {recall:.4f} ({recall*100:.2f}%)")
        print(f"   Specificity: {specificity:.4f} ({specificity*100:.2f}%)")
        print(f"   F1-Score:  {f1_score:.4f} ({f1_score*100:.2f}%)")
        print("=" * 80)
        
        return {
            "y_true": y_true,
            "y_pred": y_pred,
            "measurements_count": len(y_true),
            "confusion_matrix": {
                "tp": tp,
                "tn": tn,
                "fp": fp,
                "fn": fn
            },
            "metrics": {
                "accuracy": round(accuracy, 4),
                "accuracy_percentage": round(accuracy * 100, 2),
                "precision": round(precision, 4),
                "precision_percentage": round(precision * 100, 2),
                "recall": round(recall, 4),
                "recall_percentage": round(recall * 100, 2),
                "specificity": round(specificity, 4),
                "specificity_percentage": round(specificity * 100, 2),
                "f1_score": round(f1_score, 4),
                "f1_score_percentage": round(f1_score * 100, 2),
            }
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error calculating metrics from measurements: {str(e)}")
        print(f"Traceback:\n{error_trace}")
        return {
            "y_true": np.array([]),
            "y_pred": np.array([]),
            "measurements_count": 0,
            "metrics": None,
            "error": str(e)
        }


def calculate_k_comparison_from_measurements(
    supabase_client,
    csv_path: str
) -> List[Dict[str, Any]]:
    """
    Calculate K-comparison (K=3,5,7,9) using real pengukuran data from database.
    
    Untuk setiap pengukuran:
    1. Ekstrak features (jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala)
    2. Prediksi menggunakan KNN dengan k berbeda
    3. Compare dengan actual status (zscore_tbu < -2.0)
    4. Hitung TP, TN, FP, FN untuk masing-masing K
    
    Returns: List of k_comparison objects dengan TP/TN/FP/FN per K value
    """
    
    print("\n" + "=" * 80)
    print("📊 CALCULATING K-COMPARISON FROM REAL PENGUKURAN DATA")
    print("=" * 80)
    
    try:
        # LOAD TRAINING DATA FOR SCALING
        df_train = pd.read_csv(csv_path)
        X_train_list = []
        y_train_list = []
        
        for _, row in df_train.iterrows():
            label_col = "status_stunting"
            label_val = row.get(label_col)
            if pd.isna(label_val):
                continue
            label = map_status_to_class(label_val)
            y_train_list.append(label)
            
            jk_enc = 1 if str(row.get("jenis_kelamin", "L")).upper() == "L" else 0
            X_train_list.append([
                jk_enc,
                float(row.get("usia_bulan", 0)),
                float(row.get("tinggi_badan", 0)),
                float(row.get("berat_badan", 0)),
                float(row.get("lingkar_lengan", 0)),
                float(row.get("lingkar_kepala", 0)),
            ])
        
        X_train = np.array(X_train_list)
        y_train = np.array(y_train_list)
        
        # FIT SCALER ON TRAINING DATA
        scaler = ManualStandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        # FETCH REAL PENGUKURAN DATA
        pengukuran_response = supabase_client.table("pengukuran").select("*").execute()
        
        if not pengukuran_response.data:
            print("⚠️ No measurements found")
            return []
        
        pengukuran_list = pengukuran_response.data
        print(f"✅ Fetched {len(pengukuran_list)} measurements")
        
        # PREPARE MEASUREMENT FEATURES & GROUND TRUTH
        X_measure = []
        y_true = []
        
        for pengukuran in pengukuran_list:
            # Ground truth: zscore_tbu < -2.0 = stunting
            zscore_tbu = pengukuran.get("zscore_tbu", 0) or 0
            actual_status = 1 if zscore_tbu < -2.0 else 0
            y_true.append(actual_status)
            
            # Extract features
            jk_enc = 1 if str(pengukuran.get("jenis_kelamin", "L")).upper() == "L" else 0
            X_measure.append([
                jk_enc,
                float(pengukuran.get("usia_bulan", 0) or 0),
                float(pengukuran.get("tinggi_badan", 0) or 0),
                float(pengukuran.get("berat_badan", 0) or 0),
                float(pengukuran.get("lingkar_lengan", 0) or 0),
                float(pengukuran.get("lingkar_kepala", 0) or 0),
            ])
        
        X_measure = np.array(X_measure)
        y_true = np.array(y_true)
        
        # SCALE MEASUREMENT DATA
        X_measure_scaled = scaler.transform(X_measure)
        
        print(f"   Extracted {len(X_measure)} measurement samples")
        print(f"   Actual stunting: {np.sum(y_true)} ({np.mean(y_true)*100:.1f}%)")
        
        # CALCULATE K-COMPARISON FOR K=3,5,7,9
        k_values = [3, 5, 7, 9]
        k_comparisons = []
        
        for k in k_values:
            print(f"\n   🔄 Training KNN with K={k}...")
            
            # Train KNN on training data
            knn_k = ManualKNNClassifier(n_neighbors=k, weights='distance')
            knn_k.fit(X_train_scaled, y_train)
            
            # Predict on measurement data (multi-class: 0-3)
            y_pred_multiclass = knn_k.predict(X_measure_scaled)
            
            # Convert to binary: stunting (2,3) = 1, normal (0,1) = 0
            y_pred_binary = np.where((y_pred_multiclass == 2) | (y_pred_multiclass == 3), 1, 0)
            
            # Calculate binary confusion matrix
            cm_binary = calculate_confusion_matrix(y_true, y_pred_binary, labels=[0, 1])
            
            # Extract TP, TN, FP, FN
            tn = int(cm_binary[0, 0])
            fp = int(cm_binary[0, 1])
            fn = int(cm_binary[1, 0])
            tp = int(cm_binary[1, 1])
            
            # Calculate metrics
            accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"      TP={tp}, TN={tn}, FP={fp}, FN={fn}")
            print(f"      Accuracy={accuracy:.4f}, F1={f1_score:.4f}")
            
            k_comparisons.append({
                "k": k,
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "specificity": round(specificity, 4),
                "f1_score": round(f1_score, 4),
                "tp": tp,
                "tn": tn,
                "fp": fp,
                "fn": fn
            })
        
        print("\n✅ K-comparison calculated from real measurement data")
        print("=" * 80)
        return k_comparisons
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error calculating k-comparison: {str(e)}")
        print(f"Traceback:\n{error_trace}")
        return []


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
        
        # PREPARE FEATURES & LABELS (6 FEATURES AS PER REQUIREMENT)
        X_list = []
        y_list = []
        
        for _, row in df.iterrows():
            # Read label from CSV (status_stunting: 0-3 for 4 classes)
            label_col = "status_stunting"
            label_val = row.get(label_col)
            if pd.isna(label_val):
                continue
            label = map_status_to_class(label_val)
            y_list.append(label)
            
            # Encode features (6 features as requirement)
            jk_enc = 1 if str(row.get("jenis_kelamin", "L")).upper() == "L" else 0
            X_list.append([
                jk_enc,                                          # 1. jenis_kelamin (L=1, P=0)
                float(row.get("usia_bulan", 0)),                # 2. usia_bulan
                float(row.get("tinggi_badan", 0)),              # 3. tinggi_badan
                float(row.get("berat_badan", 0)),               # 4. berat_badan
                float(row.get("lingkar_lengan", 0)),            # 5. lingkar_lengan
                float(row.get("lingkar_kepala", 0)),            # 6. lingkar_kepala
            ])
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        # Validate data
        if len(X) == 0 or len(y) == 0:
            raise ValueError("Dataset kosong atau tidak ada data valid")
        
        print(f"\n📊 Dataset loaded: {len(X)} samples, {X.shape[1]} features")
        print(f"   Classes distribution: {np.unique(y, return_counts=True)}")
        
        # TRAIN/TEST SPLIT (80/20 STRATIFIED)
        # Menggunakan stratified split untuk maintain class distribution
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=0.2,
            random_state=42,
            stratify=y
        )
        
        print(f"\n📋 Train/Test Split (Stratified 80/20):")
        print(f"   Train: {len(X_train)} samples")
        print(f"   Test: {len(X_test)} samples")
        print(f"   Train classes: {np.unique(y_train, return_counts=True)}")
        print(f"   Test classes: {np.unique(y_test, return_counts=True)}")
        
        # SCALING (Normalize features)
        # StandardScaler: z = (x - mean) / std
        scaler = ManualStandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        print(f"\n📏 Feature Scaling: Z-score normalization applied")
        
        # TRAIN KNN (K=5 default, distance-weighted voting)
        # Model pembelajaran: store training data and labels
        knn = ManualKNNClassifier(n_neighbors=5, weights='distance')
        knn.fit(X_train_scaled, y_train)
        print(f"\n🔧 Model trained: K=5, distance-weighted voting, {len(X_train)} training samples")
        
        # EVALUATE ON TEST SET (Exclude self by using train/test split)
        # Test set samples are NOT in training set, so self-distance issue is avoided
        y_pred = knn.predict(X_test_scaled)
        
        # Validate predictions
        if len(y_pred) != len(y_test):
            raise ValueError(f"Prediction size mismatch: {len(y_pred)} vs expected {len(y_test)}")
        
        # CALCULATE METRICS
        metrics = calculate_metrics_multiclass(y_test, y_pred, labels=[0, 1, 2, 3])
        cm = metrics["confusion_matrix"]
        
        # Validate confusion matrix not empty
        if np.sum(cm) == 0:
            raise ValueError("Confusion matrix is empty - no predictions made")
        
        print(f"\n📊 Evaluation Results (K=5):")
        print(f"   Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        print(f"   Macro Precision: {metrics['macro_precision']:.4f}")
        print(f"   Macro Recall: {metrics['macro_recall']:.4f}")
        print(f"   Macro F1: {metrics['macro_f1']:.4f}")
        print(f"\n📊 Confusion Matrix (4x4):")
        print(f"   Rows=Actual, Cols=Predicted")
        labels_short = ["N+GB", "N+KG", "S+GB", "S+KG"]
        print(f"     {' '.join(f'{lbl:>6}' for lbl in labels_short)}")
        for i, row in enumerate(cm):
            print(f"{labels_short[i]:3s} {' '.join(f'{val:6d}' for val in row)}")
        print("=" * 80)
        
        # CALCULATE K COMPARISONS FROM REAL PENGUKURAN DATA (NOT FROM TRAINING SET)
        # This ensures confusion matrix reflects actual model performance on real data
        k_comparisons = calculate_k_comparison_from_measurements(supabase_client, csv_path)
        
        # Get confusion matrix from real measurements or use training set as fallback
        measurement_eval = calculate_confusion_matrix_from_measurements(supabase_client)
        
        # Use real measurement data if available, otherwise use training set
        if measurement_eval.get("measurements_count", 0) > 0:
            # Use binary confusion matrix from real measurements
            # But we need to create a response that's compatible with frontend
            measurement_metrics = measurement_eval.get("metrics", {})
            measurement_cm = measurement_eval.get("confusion_matrix", {})
            
            # For the 4x4 confusion matrix in response, we'll use training data
            # but the k_comparisons will be from real data
            print(f"\n✅ Using real measurement data for K-comparison evaluation")
            print(f"   Measurements evaluated: {measurement_eval.get('measurements_count', 0)}")
        
        # FETCH ACTUAL PENGUKURAN DATA FOR SAMPLE EXPLANATIONS
        sample_explanations = []
        try:
            pengukuran_response = supabase_client.table("pengukuran")\
                .select("id, balita_id, balita(nama_lengkap), jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala, status_gizi, tanggal_pengukuran")\
                .order("created_at", desc=True)\
                .limit(10)\
                .execute()
            
            if pengukuran_response.data:
                for pengukuran in pengukuran_response.data:
                    # Skip if no balita data
                    if not pengukuran.get("balita"):
                        continue
                    
                    # Get evaluasi data for this pengukuran
                    evaluasi_response = supabase_client.table("evaluasi_model_knn")\
                        .select("nearest_neighbors")\
                        .eq("pengukuran_id", pengukuran["id"])\
                        .execute()
                    
                    # Determine prediction from status_gizi
                    status_gizi = pengukuran.get("status_gizi", "Normal")
                    is_stunting = "Stunting" in status_gizi
                    prediction = "Stunting" if is_stunting else "Normal"
                    
                    # Get neighbors from evaluasi or use empty list
                    neighbors = []
                    if evaluasi_response.data and evaluasi_response.data[0].get("nearest_neighbors"):
                        neighbors = evaluasi_response.data[0]["nearest_neighbors"]
                    
                    sample_explanations.append({
                        "id": pengukuran["id"],
                        "is_real_data": True,
                        "timestamp": pengukuran.get("tanggal_pengukuran"),
                        "input": {
                            "nama": pengukuran.get("balita", {}).get("nama_lengkap", ""),
                            "jenis_kelamin": pengukuran.get("jenis_kelamin", "L"),
                            "usia_bulan": pengukuran.get("usia_bulan", 0),
                            "tinggi_badan": pengukuran.get("tinggi_badan", 0),
                            "berat_badan": pengukuran.get("berat_badan", 0),
                        },
                        "prediction": prediction,
                        "actual": status_gizi,
                        "neighbors": neighbors,
                        # Support multiple k values if available
                        "k_results": None
                    })
        except Exception as e:
            print(f"⚠️  Warning: Could not fetch pengukuran data for sample explanations: {e}")
            # Continue without sample_explanations rather than failing
        
        
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
                "accuracy": round(metrics["accuracy"], 4),
                "accuracy_percentage": round(metrics["accuracy"] * 100, 2),
                "macro_avg_precision": round(metrics["macro_precision"], 4),
                "macro_avg_precision_percentage": round(metrics["macro_precision"] * 100, 2),
                "macro_avg_recall": round(metrics["macro_recall"], 4),
                "macro_avg_recall_percentage": round(metrics["macro_recall"] * 100, 2),
                "macro_avg_f1": round(metrics["macro_f1"], 4),
                "macro_avg_f1_percentage": round(metrics["macro_f1"] * 100, 2),
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
            },
            "k_comparisons": k_comparisons,
            "sample_explanations": sample_explanations
        }
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        print(f"❌ File Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSV file not found: {str(e)}"
        )
    except ValueError as e:
        print(f"❌ Data Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data validation error: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Unexpected Error: {str(e)}")
        print(f"   Traceback:\n{error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/compare-k-values", response_model=Dict[str, Any])
async def compare_k_values(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase),
    model: StuntingKNNModel = Depends(get_knn_model)
):
    """
    Compare K values (3, 5, 7, 9) using REAL pengukuran data from database.
    NOT from training test set - uses actual measurement records.
    """
    if current_user.get("role") not in ["admin", "kader"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin dan Kader yang dapat mengakses evaluasi model"
        )
    
    try:
        print("=" * 80)
        print("🔍 PERBANDINGAN K-VALUES (REAL MEASUREMENT DATA)")
        print("=" * 80)
        
        # LOAD & PREPARE DATA (for training the scaler)
        csv_path = find_csv_path()
        df = pd.read_csv(csv_path)
        
        X_list = []
        y_list = []
        
        for _, row in df.iterrows():
            # Read label from CSV
            label_col = "status_stunting"
            label_val = row.get(label_col)
            if pd.isna(label_val):
                continue
            label = map_status_to_class(label_val)
            y_list.append(label)
            jk_enc = 1 if str(row.get("jenis_kelamin", "L")).upper() == "L" else 0
            X_list.append([
                jk_enc,
                float(row.get("usia_bulan", 0)),
                float(row.get("tinggi_badan", 0)),
                float(row.get("berat_badan", 0)),
                float(row.get("lingkar_lengan", 0)),
                float(row.get("lingkar_kepala", 0)),
            ])
        
        X_train = np.array(X_list)
        y_train = np.array(y_list)
        
        # SCALE on training data
        scaler = ManualStandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        
        # FETCH REAL MEASUREMENT DATA
        pengukuran_response = supabase_client.table("pengukuran").select("*").execute()
        
        if not pengukuran_response.data:
            # Return empty comparison results if no measurements
            return {
                "status": "success",
                "message": "No measurement data available",
                "comparisons": []
            }
        
        # Prepare measurement data
        X_measure = []
        y_true = []
        
        for pengukuran in pengukuran_response.data:
            zscore_tbu = pengukuran.get("zscore_tbu", 0) or 0
            actual_status = 1 if zscore_tbu < -2.0 else 0
            y_true.append(actual_status)
            
            jk_enc = 1 if str(pengukuran.get("jenis_kelamin", "L")).upper() == "L" else 0
            X_measure.append([
                jk_enc,
                float(pengukuran.get("usia_bulan", 0) or 0),
                float(pengukuran.get("tinggi_badan", 0) or 0),
                float(pengukuran.get("berat_badan", 0) or 0),
                float(pengukuran.get("lingkar_lengan", 0) or 0),
                float(pengukuran.get("lingkar_kepala", 0) or 0),
            ])
        
        X_measure = np.array(X_measure)
        y_true = np.array(y_true)
        X_measure_scaled = scaler.transform(X_measure)
        
        # EVALUATE EACH K
        k_values = [3, 5, 7, 9]
        comparison_results = []
        
        print(f"\nMeasurement set: {len(X_measure)} samples")
        print(f"Stunting: {np.sum(y_true)} ({np.mean(y_true)*100:.1f}%)\n")
        print(f"{'K':>3} | {'Accuracy':>8} | {'F1-Score':>8}")
        print("-" * 30)
        
        for k in k_values:
            print(f"Training KNN with K={k} on measurement data...")
            knn = ManualKNNClassifier(n_neighbors=k, weights='distance')
            knn.fit(X_train_scaled, y_train)
            
            # Predict on measurement data (multiclass: 0-3)
            y_pred_multiclass = knn.predict(X_measure_scaled)
            
            # Convert to binary: stunting (2,3) = 1, normal (0,1) = 0
            y_pred_binary = np.where((y_pred_multiclass == 2) | (y_pred_multiclass == 3), 1, 0)
            
            # Calculate binary confusion matrix
            cm_binary = calculate_confusion_matrix(y_true, y_pred_binary, labels=[0, 1])
            
            # Extract TP, TN, FP, FN
            tn = int(cm_binary[0, 0])
            fp = int(cm_binary[0, 1])
            fn = int(cm_binary[1, 0])
            tp = int(cm_binary[1, 1])
            
            # Calculate binary metrics
            accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            print(f"{k:3d} | {accuracy:8.4f} | {f1_score:8.4f}")
            
            comparison_results.append({
                "k": k,
                "k_value": k,
                "accuracy": round(accuracy, 4),
                "accuracy_pct": round(accuracy * 100, 2),
                "accuracy_percentage": round(accuracy * 100, 2),
                "precision": round(precision, 4),
                "precision_pct": round(precision * 100, 2),
                "recall": round(recall, 4),
                "recall_pct": round(recall * 100, 2),
                "specificity": round(specificity, 4),
                "specificity_pct": round(specificity * 100, 2),
                "f1_score": round(f1_score, 4),
                "f1_pct": round(f1_score * 100, 2),
                "confusion_matrix": {
                    "tp": tp,
                    "tn": tn,
                    "fp": fp,
                    "fn": fn
                },
                "metrics": {
                    "accuracy": round(accuracy, 4),
                    "accuracy_percentage": round(accuracy * 100, 2),
                    "accuracy_pct": round(accuracy * 100, 2),
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "f1_score": round(f1_score, 4),
                    "f1_pct": round(f1_score * 100, 2)
                }
            })
        
        best = max(comparison_results, key=lambda x: (x["f1_score"], x["k"]))
        
        print(f"\n✅ Best K: {best['k']} (F1: {best['f1_score']:.4f})")
        print("=" * 80)
        
        return {
            "status": "success",
            "message": "K comparison from real measurement data",
            "comparisons": comparison_results,
            "k_comparisons": comparison_results,  # Also return as k_comparisons for compatibility
            "recommendation": {
                "best_k": best["k"],
                "f1_score": best["f1_score"],
                "accuracy": best["accuracy"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/real-performance", response_model=Dict[str, Any])
async def evaluate_real_performance(
    current_user: dict = Depends(get_current_user),
    supabase_client = Depends(get_supabase)
):
    """
    Evaluasi model KNN menggunakan DATA PENGUKURAN REAL dari database.
    
    Ground truth: zscore_tbu < -2.0 (WHO standard untuk stunting)
    Prediction: status_gizi_label dari model KNN
    
    Metrics dihitung dari pengukuran yang sudah dilakukan, bukan dari training data.
    """
    if current_user.get("role") not in ["admin", "kader"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya Admin dan Kader yang dapat mengakses evaluasi model"
        )
    
    try:
        # Calculate confusion matrix from real measurements
        result = calculate_confusion_matrix_from_measurements(supabase_client)
        
        # Check if there was any error
        if "error" in result:
            return {
                "status": "warning",
                "message": "No real measurements found yet",
                "measurements_count": 0,
                "confusion_matrix": {
                    "tp": 0,
                    "tn": 0,
                    "fp": 0,
                    "fn": 0
                },
                "metrics": None,
                "data_source": "Real pengukuran from database"
            }
        
        # Success case
        measurements_count = result["measurements_count"]
        cm = result["confusion_matrix"]
        metrics = result["metrics"]
        
        return {
            "status": "success",
            "message": f"Real performance evaluation from {measurements_count} measurements",
            "measurements_count": measurements_count,
            "confusion_matrix": cm,
            "metrics": {
                "accuracy": metrics["accuracy"],
                "accuracy_percentage": metrics["accuracy_percentage"],
                "precision": metrics["precision"],
                "precision_percentage": metrics["precision_percentage"],
                "recall": metrics["recall"],
                "recall_percentage": metrics["recall_percentage"],
                "specificity": metrics["specificity"],
                "specificity_percentage": metrics["specificity_percentage"],
                "f1_score": metrics["f1_score"],
                "f1_score_percentage": metrics["f1_score_percentage"],
            },
            "data_source": "Real pengukuran from database",
            "ground_truth_method": "zscore_tbu < -2.0 (WHO standard)"
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error in real performance evaluation: {str(e)}")
        print(f"Traceback:\n{error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating real performance: {str(e)}"
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
