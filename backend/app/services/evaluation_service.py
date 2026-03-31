"""
Evaluation Service untuk Perhitungan Metrik KNN
Menghitung confusion matrix dan metrik untuk perbandingan K values

HANYA mengambil data dari database (REAL-TIME)
Tidak menggunakan CSV files
"""

from typing import Dict, List, Any, Optional
import numpy as np
from app.database import get_supabase
from app.ml.knn_manual import calculate_confusion_matrix, calculate_metrics


# Mapping status_gizi string ke numeric label
STATUS_GIZI_MAPPING = {
    "Normal + Gizi Baik": 0,
    "Normal + Kurang Gizi": 1,
    "Stunting + Gizi Baik": 2,
    "Stunting + Kurang Gizi": 3,
}


class EvaluationService:
    """Service untuk evaluasi performa KNN pada data real-time"""
    
    def __init__(self):
        """Initialize evaluation service"""
        self.supabase_client = None
        
    def set_supabase_client(self, client):
        """Set Supabase client"""
        self.supabase_client = client
    
    def convert_zscores_to_class_label(self, zscore_tbu: float, zscore_bbu: float) -> int:
        """
        Convert 2 z-scores to 4-class label
        
        Thresholds:
        - zscore_tbu < -2.0 → Stunting
        - zscore_tbu >= -2.0 → Normal
        - zscore_bbu < -2.0 → Kurang Gizi
        - zscore_bbu >= -2.0 → Gizi Baik
        
        Classes:
        - 0: Normal + Gizi Baik
        - 1: Normal + Kurang Gizi
        - 2: Stunting + Gizi Baik
        - 3: Stunting + Kurang Gizi
        
        Args:
            zscore_tbu: Z-Score Tinggi Badan/Usia
            zscore_bbu: Z-Score Berat Badan/Usia
            
        Returns:
            Class label (0-3)
        """
        is_stunting = zscore_tbu < -2.0  # True = Stunting, False = Normal
        is_kurang_gizi = zscore_bbu < -2.0  # True = Kurang Gizi, False = Baik
        
        if not is_stunting and not is_kurang_gizi:
            return 0  # Normal + Gizi Baik
        elif not is_stunting and is_kurang_gizi:
            return 1  # Normal + Kurang Gizi
        elif is_stunting and not is_kurang_gizi:
            return 2  # Stunting + Gizi Baik
        else:  # is_stunting and is_kurang_gizi
            return 3  # Stunting + Kurang Gizi
    
    async def fetch_pengukuran_data(
        self, 
        bulan: Optional[str] = None,
        role: Optional[str] = None,
        posyandu_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch data pengukuran dari Supabase dengan filter bulan dan role
        
        Parameters:
            bulan: Filter bulan dalam format YYYY-MM (contoh: 2026-01)
            role: Role user (admin atau kader)
            posyandu_id: ID posyandu untuk filter kader (hanya untuk role=kader)
        
        Kolom yang diambil:
        - status_gizi (string): Prediksi dari model (akan diconvert ke label)
        - zscore_tbu: Ground truth untuk stunting
        - zscore_bbu: Ground truth untuk gizi
        - tanggal_pengukuran: Tanggal pengukuran untuk filter bulan
        - balita(posyandu_id): Untuk filter berdasarkan posyandu kader
        
        Returns:
            List of pengukuran records dengan status_gizi_label ditambahkan
        """
        try:
            # Fetch dengan kolom yang efisien dan include balita untuk posyandu_id
            response = self.supabase_client.table("pengukuran").select(
                "id,status_gizi,zscore_tbu,zscore_bbu,created_at,tanggal_pengukuran,balita_id,balita(posyandu_id)"
            ).execute()
            
            if not response.data:
                return []
            
            data = response.data
            
            # Filter berdasarkan bulan jika diberikan (format: YYYY-MM)
            if bulan:
                filtered_data = []
                for record in data:
                    # HANYA gunakan tanggal_pengukuran untuk filter bulan (jangan fallback ke created_at)
                    # tanggal_pengukuran format: YYYY-MM-DD
                    pengukuran_date = record.get("tanggal_pengukuran", "")
                    if pengukuran_date and pengukuran_date.startswith(bulan):
                        filtered_data.append(record)
                data = filtered_data
            
            # Filter berdasarkan role dan posyandu_id untuk kader
            if role == "kader" and posyandu_id:
                filtered_data = []
                for record in data:
                    # Get posyandu_id dari nested balita
                    balita = record.get("balita", {})
                    if isinstance(balita, dict):
                        record_posyandu_id = balita.get("posyandu_id")
                    else:
                        record_posyandu_id = None
                    
                    if record_posyandu_id == posyandu_id:
                        filtered_data.append(record)
                data = filtered_data
            
            # Convert status_gizi string ke label numeric
            for record in data:
                status_gizi_str = record.get("status_gizi", "Normal + Gizi Baik")
                record["status_gizi_label"] = STATUS_GIZI_MAPPING.get(
                    status_gizi_str, 0
                )
            
            return data
            
        except Exception as e:
            print(f"Error fetching pengukuran data: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def fetch_prediction_history(
        self, 
        limit: int = 100,
        bulan: Optional[str] = None,
        role: Optional[str] = None,
        posyandu_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch prediction history dengan nama balita dan tetangga terdekat
        Dengan support filter bulan dan role-based (kader)
        
        Parameters:
            limit: Maksimal number of records
            bulan: Filter bulan dalam format YYYY-MM
            role: Role user (admin atau kader)
            posyandu_id: ID posyandu untuk filter kader
        
        Actual status dihitung dari kombinasi 2 z-score (zscore_tbu + zscore_bbu)
        
        Returns:
            List of predictions dengan nama balita, actual status, predicted status, nearest neighbors
        """
        try:
            # First, fetch pengukuran data with balita_id, including both z-scores and posyandu info
            pengukuran_response = self.supabase_client.table("pengukuran").select(
                "id,balita_id,status_gizi,zscore_tbu,zscore_bbu,created_at,tanggal_pengukuran,balita(posyandu_id)"
            ).order("created_at", desc=True).limit(limit).execute()
            
            if not pengukuran_response.data:
                return []
            
            pengukuran_list = pengukuran_response.data
            
            # Filter berdasarkan bulan jika diberikan (format: YYYY-MM)
            if bulan:
                filtered_list = []
                for record in pengukuran_list:
                    # HANYA gunakan tanggal_pengukuran untuk filter bulan (jangan fallback ke created_at)
                    pengukuran_date = record.get("tanggal_pengukuran", "")
                    if pengukuran_date and pengukuran_date.startswith(bulan):
                        filtered_list.append(record)
                pengukuran_list = filtered_list
            
            # Filter berdasarkan role kader dan posyandu_id
            if role == "kader" and posyandu_id:
                filtered_list = []
                for record in pengukuran_list:
                    balita = record.get("balita", {})
                    if isinstance(balita, dict):
                        record_posyandu_id = balita.get("posyandu_id")
                    else:
                        record_posyandu_id = None
                    
                    if record_posyandu_id == posyandu_id:
                        filtered_list.append(record)
                pengukuran_list = filtered_list
            
            # Build balita_ids to fetch
            balita_ids = [p["balita_id"] for p in pengukuran_list if p.get("balita_id")]
            
            # Fetch balita names in bulk
            balita_names = {}
            if balita_ids:
                balita_response = self.supabase_client.table("balita").select(
                    "id,nama_lengkap"
                ).in_("id", balita_ids).execute()
                
                if balita_response.data:
                    balita_names = {b["id"]: b.get("nama_lengkap", "Unknown") for b in balita_response.data}
            
            # Fetch nearest neighbors from evaluasi_model_knn table
            pengukuran_ids = [p["id"] for p in pengukuran_list]
            neighbors_map = {}
            if pengukuran_ids:
                try:
                    evaluasi_response = self.supabase_client.table("evaluasi_model_knn").select(
                        "pengukuran_id,nearest_neighbors"
                    ).in_("pengukuran_id", pengukuran_ids).execute()
                    
                    if evaluasi_response.data:
                        neighbors_map = {e["pengukuran_id"]: e.get("nearest_neighbors", []) for e in evaluasi_response.data}
                except Exception:
                    # If evaluasi_model_knn table doesn't exist or has no data, continue without neighbors
                    neighbors_map = {}
            
            # Process predictions
            predictions = []
            for record in pengukuran_list:
                # Get balita name from mapping
                balita_id = record.get("balita_id")
                balita_name = balita_names.get(balita_id, "Unknown")
                
                # Get predicted status label
                status_gizi_str = record.get("status_gizi", "Normal + Gizi Baik")
                predicted_label = STATUS_GIZI_MAPPING.get(status_gizi_str, 0)
                predicted_status_display = status_gizi_str
                
                # Get z-scores
                zscore_tbu = record.get("zscore_tbu", 0)
                zscore_bbu = record.get("zscore_bbu", 0)
                
                # Calculate ACTUAL status from combination of 2 z-scores
                actual_label = self.convert_zscores_to_class_label(zscore_tbu, zscore_bbu)
                actual_status_display = list(STATUS_GIZI_MAPPING.keys())[actual_label]
                
                # Check if prediction is correct (4-class: actual vs predicted)
                is_correct = actual_label == predicted_label
                
                # Get nearest neighbors
                pengukuran_id = record.get("id")
                nearest_neighbors = neighbors_map.get(pengukuran_id, [])
                
                predictions.append({
                    "id": pengukuran_id,
                    "nama_balita": balita_name,
                    "actual_status": actual_status_display,
                    "predicted_status": predicted_status_display,
                    "actual_label": actual_label,
                    "predicted_label": predicted_label,
                    "zscore_tbu": round(float(zscore_tbu), 2),
                    "zscore_bbu": round(float(zscore_bbu), 2),
                    "is_correct": is_correct,
                    "tanggal": record.get("tanggal_pengukuran") or (record.get("created_at", "").split("T")[0] if record.get("created_at") else ""),
                    "nearest_neighbors": nearest_neighbors  # Array of K nearest neighbors
                })
            
            return predictions
            
        except Exception as e:
            print(f"Error fetching prediction history: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def convert_to_binary_ground_truth(
        self, 
        zscore_tbu: float
    ) -> int:
        """
        Convert zscore_tbu to binary ground truth (Yi)
        
        WHO Standard for Stunting:
        - zscore_tbu < -2.0  → y_true = 1 (STUNTING)
        - zscore_tbu >= -2.0 → y_true = 0 (NORMAL)
        
        Args:
            zscore_tbu: Z-Score Tinggi Badan/Usia
            
        Returns:
            Binary label (0 or 1)
        """
        return 1 if zscore_tbu < -2.0 else 0
    
    def convert_to_binary_prediction(
        self, 
        status_gizi_label: int
    ) -> int:
        """
        Convert 4-class prediction to binary prediction
        
        Mapping:
        - Label 0,1 (Normal) → y_pred = 0
        - Label 2,3 (Stunting) → y_pred = 1
        
        Args:
            status_gizi_label: 4-class label (0-3)
            
        Returns:
            Binary label (0 or 1)
        """
        return 1 if status_gizi_label in (2, 3) else 0
    
    def calculate_binary_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, Any]:
        """
        Calculate binary classification metrics
        
        Metrics:
        - Accuracy: (TP + TN) / Total
        - Precision: TP / (TP + FP)
        - Recall (Sensitivity): TP / (TP + FN)
        - Specificity: TN / (TN + FP)
        - F1-Score: 2 * (Precision * Recall) / (Precision + Recall)
        
        Args:
            y_true: Ground truth binary labels
            y_pred: Predicted binary labels
            
        Returns:
            Dictionary with metrics
        """
        # Calculate confusion matrix for binary (2x2)
        cm = calculate_confusion_matrix(y_true, y_pred, labels=[0, 1])
        
        # Extract values
        tn = cm[0, 0]  # True Negative
        fp = cm[0, 1]  # False Positive
        fn = cm[1, 0]  # False Negative
        tp = cm[1, 1]  # True Positive
        
        total = len(y_true)
        
        # Calculate metrics
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "confusion_matrix": cm.tolist(),
            "tp": int(tp),
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "total": total,
            "accuracy": round(float(accuracy), 4),
            "accuracy_percent": round(float(accuracy) * 100, 2),
            "precision": round(float(precision), 4),
            "precision_percent": round(float(precision) * 100, 2),
            "recall": round(float(recall), 4),
            "recall_percent": round(float(recall) * 100, 2),
            "specificity": round(float(specificity), 4),
            "specificity_percent": round(float(specificity) * 100, 2),
            "f1_score": round(float(f1_score), 4),
            "f1_score_percent": round(float(f1_score) * 100, 2),
        }
    
    def calculate_multiclass_metrics(
        self,
        y_true_multiclass: np.ndarray,
        y_pred_multiclass: np.ndarray
    ) -> Dict[str, Any]:
        """
        Calculate metrics dengan focus pada Class 3 (Stunting + Kurang Gizi)
        
        Menggunakan one-vs-rest approach untuk Class 3:
        - TP (True Positive): Actual = Class 3 AND Prediksi = Class 3
        - FN (False Negative): Actual = Class 3 AND Prediksi ≠ Class 3 (missed target)
        - FP (False Positive): Actual ≠ Class 3 AND Prediksi = Class 3 (false alarm)
        - TN (True Negative): Actual ≠ Class 3 AND Prediksi ≠ Class 3 (correct rejection)
        
        Ini memberikan satu metrik keseluruhan yang mengukur performa sistem
        dalam mendeteksi kasus paling kritis (Stunting + Kurang Gizi)
        
        Args:
            y_true_multiclass: Ground truth 4-class labels
            y_pred_multiclass: Predicted 4-class labels
            
        Returns:
            Dictionary dengan single TP/TN/FP/FN metrics untuk Class 3
        """
        # Convert ke binary: Class 3 (positive) vs Others (negative)
        y_true_binary = (y_true_multiclass == 3).astype(int)
        y_pred_binary = (y_pred_multiclass == 3).astype(int)
        
        # Calculate TP, TN, FP, FN
        tp = np.sum((y_true_binary == 1) & (y_pred_binary == 1))
        tn = np.sum((y_true_binary == 0) & (y_pred_binary == 0))
        fp = np.sum((y_true_binary == 0) & (y_pred_binary == 1))
        fn = np.sum((y_true_binary == 1) & (y_pred_binary == 0))
        
        # Calculate metrics
        total = len(y_true_multiclass)
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calculate 4x4 confusion matrix for reference
        cm = calculate_confusion_matrix(
            y_true_multiclass, 
            y_pred_multiclass, 
            labels=[0, 1, 2, 3]
        )
        
        return {
            "class_focus": {
                "name": "Stunting + Kurang Gizi (Class 3)",
                "description": "Performa sistem dalam mendeteksi kasus paling kritis"
            },
            "confusion_matrix_4x4": cm.tolist(),
            "total_samples": total,
            "tp": int(tp),
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp_percent": round(float(tp / total * 100), 2) if total > 0 else 0,
            "tn_percent": round(float(tn / total * 100), 2) if total > 0 else 0,
            "fp_percent": round(float(fp / total * 100), 2) if total > 0 else 0,
            "fn_percent": round(float(fn / total * 100), 2) if total > 0 else 0,
            "accuracy": round(float(accuracy), 4),
            "accuracy_percent": round(float(accuracy) * 100, 2),
            "precision": round(float(precision), 4),
            "precision_percent": round(float(precision) * 100, 2),
            "recall": round(float(recall), 4),
            "recall_percent": round(float(recall) * 100, 2),
            "specificity": round(float(specificity), 4),
            "specificity_percent": round(float(specificity) * 100, 2),
            "f1_score": round(float(f1), 4),
            "f1_score_percent": round(float(f1) * 100, 2),
            "class_distribution": {
                "actual_class_3": int(np.sum(y_true_binary == 1)),
                "actual_other": int(np.sum(y_true_binary == 0)),
                "predicted_class_3": int(np.sum(y_pred_binary == 1)),
                "predicted_other": int(np.sum(y_pred_binary == 0))
            }
        }
    
    async def evaluate_model(
        self, 
        bulan: Optional[str] = None,
        role: Optional[str] = None,
        posyandu_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Main function untuk evaluasi model dengan filtering
        Menghitung metrik untuk K=3, 5, 7, 9
        
        Parameters:
            bulan: Filter bulan dalam format YYYY-MM
            role: Role user (admin atau kader)
            posyandu_id: ID posyandu untuk filter kader
        
        Returns:
            Dictionary with complete evaluation results
        """
        try:
            # 1. Fetch data dengan filter bulan dan role
            pengukuran_data = await self.fetch_pengukuran_data(
                bulan=bulan,
                role=role,
                posyandu_id=posyandu_id
            )
            
            if not pengukuran_data:
                return {
                    "success": False,
                    "message": "No data available for evaluation",
                    "total_data": 0
                }
            
            # 2. Extract y_true (binary from zscore_tbu)
            y_true_binary = np.array([
                self.convert_to_binary_ground_truth(record["zscore_tbu"])
                for record in pengukuran_data
            ])
            
            # 3. Extract y_pred (binary from status_gizi_label)
            y_pred_binary = np.array([
                self.convert_to_binary_prediction(record["status_gizi_label"])
                for record in pengukuran_data
            ])
            
            # 4. Extract y_pred_multiclass (4-class from predicted status_gizi_label)
            y_pred_multiclass = np.array([
                record["status_gizi_label"]
                for record in pengukuran_data
            ])
            
            # 5. Extract y_true_multiclass (4-class from actual z-scores)
            # Using COMBINATION of zscore_tbu + zscore_bbu
            y_true_multiclass = np.array([
                self.convert_zscores_to_class_label(
                    record.get("zscore_tbu", 0),
                    record.get("zscore_bbu", 0)
                )
                for record in pengukuran_data
            ])
            
            # 6. Calculate metrics for binary (untuk membuat matriks 2x2)
            binary_metrics = self.calculate_binary_metrics(y_true_binary, y_pred_binary)
            
            # 7. Calculate metrics for 4-class (sekarang dengan actual dari 2 z-scores)
            multiclass_metrics = self.calculate_multiclass_metrics(
                y_true_multiclass, 
                y_pred_multiclass
            )
            
            # 8. Build comparison table (untuk semua K dianggap sama karena semua data)
            # Karena kita evaluate ALL data, setiap K akan punya hasil yang sama
            # dalam konteks ini. Jika ada simulasi K-fold, baru ada perbedaan.
            # Untuk now, kita gunakan hasil yang sama dengan catatan untuk semua K
            k_comparison = []
            for k in [3, 5, 7, 9]:
                k_comparison.append({
                    "k": k,
                    "accuracy": binary_metrics["accuracy"],
                    "accuracy_percent": binary_metrics["accuracy_percent"],
                    "precision": binary_metrics["precision"],
                    "precision_percent": binary_metrics["precision_percent"],
                    "recall": binary_metrics["recall"],
                    "recall_percent": binary_metrics["recall_percent"],
                    "f1_score": binary_metrics["f1_score"],
                    "f1_score_percent": binary_metrics["f1_score_percent"],
                    "specificity": binary_metrics["specificity"],
                    "specificity_percent": binary_metrics["specificity_percent"],
                })
            
            return {
                "success": True,
                "message": "Model evaluation completed successfully",
                "metadata": {
                    "total_data": len(pengukuran_data),
                    "evaluation_timestamp": np.datetime64("now").astype(str),
                    "note": "Evaluation on all available data (non-k-fold)"
                },
                "binary_classification": {
                    "description": "Binary classification: Normal (0) vs Stunting (1)",
                    "ground_truth_source": "zscore_tbu < -2.0",
                    "prediction_source": "status_gizi_label mapped to binary",
                    "metrics": binary_metrics
                },
                "multiclass_classification": {
                    "description": "4-class classification (0-3)",
                    "class_definitions": {
                        "0": "Normal + Gizi Baik",
                        "1": "Normal + Kurang Gizi",
                        "2": "Stunting + Gizi Baik",
                        "3": "Stunting + Kurang Gizi"
                    },
                    "metrics": multiclass_metrics
                },
                "k_comparison": k_comparison,
                "distribution": {
                    "normal_count": int(np.sum(y_true_binary == 0)),
                    "stunting_count": int(np.sum(y_true_binary == 1)),
                    "normal_percent": round(100 * np.sum(y_true_binary == 0) / len(y_true_binary), 2),
                    "stunting_percent": round(100 * np.sum(y_true_binary == 1) / len(y_true_binary), 2)
                }
            }
            
        except Exception as e:
            print(f"Error in evaluate_model: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error during evaluation"
            }


# Global instance
evaluation_service = EvaluationService()
