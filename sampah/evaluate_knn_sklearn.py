"""
Evaluasi Model KNN sklearn dengan Confusion Matrix 4x4
dan Perhitungan TP, TN, FP, FN per Kelas (One-vs-Rest)

Fitur:
- Confusion Matrix 4x4 untuk multi-class classification
- Perhitungan TP, TN, FP, FN per kelas menggunakan OvR (One-vs-Rest)
- Visualisasi matriks dengan format tabel yang rapi
- Metrik evaluasi: Accuracy, Precision, Recall, F1-Score per kelas
"""

import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from typing import Tuple, Dict, List
import pandas as pd


# ============================================================================
# 1. KONFIGURASI & KONSTANTA
# ============================================================================

CLASS_LABELS = {
    0: "Normal + Gizi Baik",
    1: "Normal + Kurang Gizi",
    2: "Stunting + Gizi Baik",
    3: "Stunting + Kurang Gizi"
}

CLASS_NAMES = [
    "Normal + Gizi Baik",
    "Normal + Kurang Gizi",
    "Stunting + Gizi Baik",
    "Stunting + Kurang Gizi"
]


# ============================================================================
# 2. FUNGSI PERHITUNGAN CONFUSION MATRIX
# ============================================================================

def calculate_confusion_matrix_sklearn(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """
    Menghitung confusion matrix 4x4 menggunakan sklearn
    
    Args:
        y_true: Label aktual (ground truth) dari Z-Score
        y_pred: Hasil prediksi dari model KNN
        
    Returns:
        Confusion matrix dengan shape (4, 4)
        
    Struktur matriks:
        [TP0  FP0  FP0  FP0]  ← Predicted as class 0
        [FN1  TP1  FP1  FP1]  ← Predicted as class 1
        [FN2  FP2  TP2  FP2]  ← Predicted as class 2
        [FN3  FP3  FP3  TP3]  ← Predicted as class 3
        
        Actual labels: 0, 1, 2, 3 (vertical)
    """
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3])
    return cm


# ============================================================================
# 3. FUNGSI PERHITUNGAN TP, TN, FP, FN PER KELAS (ONE-VS-REST)
# ============================================================================

def calculate_ovr_metrics(cm: np.ndarray, class_idx: int) -> Dict[str, int]:
    """
    Menghitung TP, TN, FP, FN untuk satu kelas menggunakan One-vs-Rest (OvR)
    
    OvR approach:
    - Kelas yang ditargetkan = Positive
    - Tiga kelas lainnya = Negative
    
    Args:
        cm: Confusion matrix 4x4
        class_idx: Index kelas yang dievaluasi (0, 1, 2, atau 3)
        
    Returns:
        Dictionary dengan TP, TN, FP, FN
    """
    # Ekstrak nilai dari confusion matrix
    tp = cm[class_idx, class_idx]  # Diagonal = True Positive
    
    # False Positive: prediksi sebagai class_idx tapi aktualnya bukan
    fp = cm[:, class_idx].sum() - tp
    
    # False Negative: aktualnya class_idx tapi prediksi bukan
    fn = cm[class_idx, :].sum() - tp
    
    # True Negative: tidak class_idx dan tidak diprediksi class_idx
    tn = cm.sum() - tp - fp - fn
    
    return {
        "TP": int(tp),
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn)
    }


def calculate_metrics_for_all_classes(cm: np.ndarray) -> Dict[int, Dict[str, int]]:
    """
    Menghitung TP, TN, FP, FN untuk semua 4 kelas
    
    Args:
        cm: Confusion matrix 4x4
        
    Returns:
        Dictionary dengan metrik untuk setiap kelas
    """
    metrics_all = {}
    for class_idx in range(4):
        metrics_all[class_idx] = calculate_ovr_metrics(cm, class_idx)
    return metrics_all


# ============================================================================
# 4. FUNGSI VISUALISASI
# ============================================================================

def display_confusion_matrix(cm: np.ndarray) -> str:
    """
    Menampilkan confusion matrix dalam format tabel yang rapi
    
    Args:
        cm: Confusion matrix 4x4
        
    Returns:
        String yang sudah diformat untuk print
    """
    df_cm = pd.DataFrame(
        cm,
        index=[f"Actual\n{CLASS_NAMES[i]}" for i in range(4)],
        columns=[f"Pred\n{CLASS_NAMES[i]}" for i in range(4)]
    )
    
    output = "\n" + "=" * 100 + "\n"
    output += "CONFUSION MATRIX 4x4 (sklearn)\n"
    output += "=" * 100 + "\n"
    output += str(df_cm) + "\n"
    output += "=" * 100 + "\n"
    
    return output


def display_ovr_metrics(metrics_all: Dict[int, Dict[str, int]]) -> str:
    """
    Menampilkan TP, TN, FP, FN untuk semua kelas dalam format tabel
    
    Args:
        metrics_all: Dictionary berisi metrik semua kelas
        
    Returns:
        String yang sudah diformat untuk print
    """
    output = "\n" + "=" * 100 + "\n"
    output += "TP, TN, FP, FN PER KELAS (One-vs-Rest/OvR) APPROACH\n"
    output += "=" * 100 + "\n\n"
    
    # Buat DataFrame untuk tampilan yang rapi
    data = []
    for class_idx in range(4):
        metrics = metrics_all[class_idx]
        data.append({
            "Kelas": f"{class_idx}: {CLASS_NAMES[class_idx]}",
            "TP": metrics["TP"],
            "TN": metrics["TN"],
            "FP": metrics["FP"],
            "FN": metrics["FN"]
        })
    
    df_metrics = pd.DataFrame(data)
    output += df_metrics.to_string(index=False) + "\n"
    output += "\n" + "=" * 100 + "\n"
    
    return output


def display_detailed_metrics(y_true: np.ndarray, y_pred: np.ndarray, cm: np.ndarray) -> str:
    """
    Menampilkan metrik detail untuk setiap kelas (Precision, Recall, F1-Score)
    
    Args:
        y_true: Label aktual
        y_pred: Prediksi
        cm: Confusion matrix
        
    Returns:
        String yang sudah diformat untuk print
    """
    output = "\n" + "=" * 100 + "\n"
    output += "METRIK EVALUASI DETAIL PER KELAS\n"
    output += "=" * 100 + "\n"
    
    output += "Classification Report (sklearn):\n\n"
    output += classification_report(
        y_true, y_pred,
        target_names=CLASS_NAMES,
        labels=[0, 1, 2, 3]
    )
    
    output += "\n" + "=" * 100 + "\n"
    output += f"Overall Accuracy: {accuracy_score(y_true, y_pred):.4f} ({accuracy_score(y_true, y_pred)*100:.2f}%)\n"
    output += "=" * 100 + "\n"
    
    return output


def calculate_and_display_metrics_per_class(cm: np.ndarray, metrics_all: Dict) -> str:
    """
    Menghitung dan menampilkan metrik per kelas dari confusion matrix
    
    Precision = TP / (TP + FP)
    Recall = TP / (TP + FN)
    F1-Score = 2 * (Precision * Recall) / (Precision + Recall)
    
    Args:
        cm: Confusion matrix
        metrics_all: Dictionary metrik per kelas
        
    Returns:
        String yang sudah diformat
    """
    output = "\n" + "=" * 100 + "\n"
    output += "PERHITUNGAN METRIK PER KELAS (One-vs-Rest)\n"
    output += "=" * 100 + "\n\n"
    
    data = []
    for class_idx in range(4):
        metrics = metrics_all[class_idx]
        tp = metrics["TP"]
        tn = metrics["TN"]
        fp = metrics["FP"]
        fn = metrics["FN"]
        
        # Hitung Precision, Recall, F1
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        data.append({
            "Kelas": f"{class_idx}: {CLASS_NAMES[class_idx][:20]}...",
            "Precision": f"{precision:.4f}",
            "Recall": f"{recall:.4f}",
            "F1-Score": f"{f1:.4f}",
            "Specificity": f"{specificity:.4f}"
        })
    
    df_detailed = pd.DataFrame(data)
    output += df_detailed.to_string(index=False) + "\n"
    output += "=" * 100 + "\n"
    
    return output


# ============================================================================
# 5. FUNGSI UTAMA - EVALUASI LENGKAP
# ============================================================================

def evaluate_knn_model(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    """
    Melakukan evaluasi lengkap model KNN dengan confusion matrix dan metrik per kelas
    
    Args:
        y_true: Label aktual (ground truth) dari Z-Score
        y_pred: Hasil prediksi dari model KNN (0, 1, 2, 3)
    """
    
    # STEP 1: Hitung confusion matrix
    print("\n" + "🔄 Calculating confusion matrix...")
    cm = calculate_confusion_matrix_sklearn(y_true, y_pred)
    print("✅ Confusion matrix calculated")
    
    # STEP 2: Tampilkan confusion matrix
    print(display_confusion_matrix(cm))
    
    # STEP 3: Hitung metrik per kelas (OvR)
    print("🔄 Calculating OvR metrics for all classes...")
    metrics_all = calculate_metrics_for_all_classes(cm)
    print("✅ OvR metrics calculated")
    
    # STEP 4: Tampilkan TP, TN, FP, FN
    print(display_ovr_metrics(metrics_all))
    
    # STEP 5: Tampilkan metrik per kelas (Precision, Recall, F1)
    print(display_detailed_metrics(y_true, y_pred, cm))
    
    # STEP 6: Tampilkan perhitungan detail
    print(calculate_and_display_metrics_per_class(cm, metrics_all))
    
    return cm, metrics_all


# ============================================================================
# 6. CONTOH PENGGUNAAN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("EVALUASI MODEL KNN SKLEARN - MULTI-CLASS CLASSIFICATION (4 KELAS)")
    print("=" * 100)
    
    # Contoh data (simulasi hasil dari model KNN)
    # Ground truth dari Z-Score (ZTB < -2.0 = Stunting, label 0/1/2/3)
    y_true_sample = np.array([
        0, 0, 1, 1, 2, 2, 3, 3,  # 8 samples
        0, 1, 2, 3, 0, 1, 2, 3,  # 8 samples
        0, 0, 0, 1, 1, 1, 2, 2,  # 8 samples
        2, 3, 3, 3, 0, 0, 1, 1   # 8 samples
    ])
    
    # Prediksi dari model KNN
    y_pred_sample = np.array([
        0, 0, 1, 1, 2, 2, 3, 3,  # Predictions
        0, 1, 2, 3, 1, 1, 2, 3,  # Some errors
        0, 0, 1, 1, 1, 2, 2, 3,  # Some errors
        2, 3, 3, 2, 0, 1, 1, 2   # Some errors
    ])
    
    print("\n📊 Data:")
    print(f"Total samples: {len(y_true_sample)}")
    print(f"Ground truth distribution: {np.bincount(y_true_sample)}")
    print(f"Prediction distribution: {np.bincount(y_pred_sample)}")
    
    # Jalankan evaluasi lengkap
    cm, metrics_all = evaluate_knn_model(y_true_sample, y_pred_sample)
    
    print("\n" + "=" * 100)
    print("EVALUASI SELESAI")
    print("=" * 100)
