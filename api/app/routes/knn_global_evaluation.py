"""
API Routes untuk KNN Global Evaluation (API Folder)
====================================================

Endpoint untuk admin dashboard - evaluasi performa KNN secara global
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

try:
    from app.ml.evaluate_knn_global import KNNGlobalEvaluator
except ImportError:
    from ..ml.evaluate_knn_global import KNNGlobalEvaluator


router = APIRouter(
    prefix="/api/evaluation/knn",
    tags=["KNN Evaluation - Global"]
)


@router.get("/global")
async def evaluate_global_knn() -> Dict[str, Any]:
    """
    Evaluasi KNN secara global (semua data)
    
    Endpoint untuk admin dashboard:
    - Fetch semua data dari tabel pengukuran
    - No user filtering
    - No month filtering
    - Report keseluruhan performa model
    
    Response format:
    ```json
    {
        "status": "success",
        "data": {
            "k": 5,
            "n_total_samples": 1234,
            "confusion_matrix": {
                "tp": 45,
                "tn": 1100,
                "fp": 34,
                "fn": 55
            },
            "metrics": {
                "accuracy": 0.9297,
                "precision": 0.5697,
                "recall": 0.4500,
                "specificity": 0.9703,
                "f1_score": 0.0000
            },
            "label_distribution": {
                "normal_true": 1134,
                "stunting_true": 100,
                "normal_pred": 1100,
                "stunting_pred": 134
            },
            "class_distribution_4class": {
                "0": 500,
                "1": 634,
                "2": 45,
                "3": 55
            }
        },
        "interpretation": "...",
        "timestamp": "2024-11-20T10:30:00"
    }
    ```
    
    Returns:
        JSON response dengan confusion matrix, metrics, dan interpretasi
    """
    try:
        evaluator = KNNGlobalEvaluator(k=5)
        result = evaluator.evaluate_global()
        interpretation = evaluator.get_interpretation(result)
        
        from datetime import datetime
        
        return {
            "status": "success",
            "data": result,
            "interpretation": interpretation,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating global KNN: {str(e)}"
        )


@router.get("/global/summary")
async def evaluate_global_knn_summary() -> Dict[str, Any]:
    """
    Quick summary dari global KNN evaluation
    
    Hanya return: accuracy, recall, f1_score, status
    Untuk quick check di admin panel
    
    Response:
    ```json
    {
        "status": "success",
        "data": {
            "accuracy": 0.9297,
            "recall": 0.4500,
            "f1_score": 0.5097,
            "performance": "Good",
            "n_samples": 1234,
            "tp": 45,
            "fn": 55
        },
        "timestamp": "2024-11-20T10:30:00"
    }
    ```
    """
    try:
        evaluator = KNNGlobalEvaluator(k=5)
        result = evaluator.evaluate_global()
        
        m = result['metrics']
        cm = result['confusion_matrix']
        
        # Determine performance level
        if m['accuracy'] >= 0.85:
            performance = "Excellent"
        elif m['accuracy'] >= 0.75:
            performance = "Good"
        elif m['accuracy'] >= 0.65:
            performance = "Fair"
        else:
            performance = "Poor"
        
        from datetime import datetime
        
        return {
            "status": "success",
            "data": {
                "accuracy": m['accuracy'],
                "recall": m['recall'],
                "precision": m['precision'],
                "f1_score": m['f1_score'],
                "performance": performance,
                "n_samples": result['n_total_samples'],
                "tp": cm['tp'],
                "tn": cm['tn'],
                "fp": cm['fp'],
                "fn": cm['fn']
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting global KNN summary: {str(e)}"
        )


@router.get("/global/confusion-matrix")
async def get_global_confusion_matrix() -> Dict[str, Any]:
    """
    Get confusion matrix dari global evaluation
    
    Useful untuk visualization di frontend
    
    Response:
    ```json
    {
        "status": "success",
        "data": {
            "confusion_matrix": {
                "tp": 45,
                "tn": 1100,
                "fp": 34,
                "fn": 55
            },
            "label_distribution": {
                "normal_true": 1134,
                "stunting_true": 100,
                "normal_pred": 1100,
                "stunting_pred": 134
            },
            "metrics": {
                "accuracy": 0.9297,
                "precision": 0.5697,
                "recall": 0.4500,
                "specificity": 0.9703,
                "f1_score": 0.5097
            }
        },
        "timestamp": "2024-11-20T10:30:00"
    }
    ```
    """
    try:
        evaluator = KNNGlobalEvaluator(k=5)
        result = evaluator.evaluate_global()
        
        from datetime import datetime
        
        return {
            "status": "success",
            "data": {
                "confusion_matrix": result['confusion_matrix'],
                "label_distribution": result['label_distribution'],
                "metrics": result['metrics']
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting global confusion matrix: {str(e)}"
        )
