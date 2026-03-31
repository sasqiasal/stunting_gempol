"""
FastAPI Routes untuk Evaluasi Parameter K
Endpoint untuk menjalankan evaluasi K parameter melalui HTTP request
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import asyncio
from app.ml.evaluate_k_parameter import KParameterEvaluator

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.get("/k-parameter", summary="Evaluate KNN Parameter K")
async def evaluate_k_parameter() -> Dict:
    """
    Evaluasi parameter K pada algoritma KNN
    
    Returns:
    - Summary tabel perbandingan K
    - Detailed metrics per class per K
    - Best K recommendation
    
    Proses ini mungkin memakan waktu beberapa detik tergantung jumlah data
    """
    try:
        evaluator = KParameterEvaluator()
        
        # Run evaluation in background (non-blocking)
        results, y_true = await asyncio.to_thread(evaluator.run_evaluation)
        
        # Prepare summary for response
        summary = []
        for k in evaluator.k_values:
            result = results[k]
            summary.append({
                "k": k,
                "overall_accuracy": round(result['overall_accuracy'], 4),
                "macro_accuracy": round(result['macro_accuracy'], 4),
                "macro_precision": round(result['macro_precision'], 4),
                "macro_recall": round(result['macro_recall'], 4),
                "macro_specificity": round(result['macro_specificity'], 4),
                "macro_f1": round(result['macro_f1'], 4)
            })
        
        # Determine best K
        best_k = max(evaluator.k_values, key=lambda k: results[k]['overall_accuracy'])
        best_accuracy = results[best_k]['overall_accuracy']
        
        # Prepare detailed metrics
        detailed_metrics = {}
        for k in evaluator.k_values:
            detailed_metrics[k] = []
            metrics_per_class = results[k]['metrics_per_class']
            
            for class_idx in range(evaluator.num_classes):
                metrics = metrics_per_class[class_idx]
                detailed_metrics[k].append({
                    "class_idx": class_idx,
                    "class_name": evaluator.class_names[class_idx],
                    "tp": int(metrics['tp']),
                    "tn": int(metrics['tn']),
                    "fp": int(metrics['fp']),
                    "fn": int(metrics['fn']),
                    "accuracy": round(metrics['accuracy'], 4),
                    "precision": round(metrics['precision'], 4),
                    "recall": round(metrics['recall'], 4),
                    "specificity": round(metrics['specificity'], 4),
                    "f1_score": round(metrics['f1_score'], 4)
                })
        
        return {
            "status": "success",
            "message": "K parameter evaluation completed",
            "summary": summary,
            "detailed_metrics": detailed_metrics,
            "best_k": {
                "k": best_k,
                "overall_accuracy": round(best_accuracy, 4),
                "recommendation": f"Use K={best_k} for best overall accuracy"
            }
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/k-parameter/summary", summary="Get Summary Table Only")
async def get_k_parameter_summary() -> Dict:
    """
    Get summary table dari evaluasi K parameter (tanpa detailed metrics)
    Lebih cepat jika hanya butuh overview
    """
    try:
        evaluator = KParameterEvaluator()
        results, y_true = await asyncio.to_thread(evaluator.run_evaluation)
        
        # Prepare summary
        summary = []
        for k in evaluator.k_values:
            result = results[k]
            summary.append({
                "k": k,
                "overall_accuracy": round(result['overall_accuracy'], 4),
                "macro_accuracy": round(result['macro_accuracy'], 4),
                "macro_precision": round(result['macro_precision'], 4),
                "macro_recall": round(result['macro_recall'], 4),
                "macro_specificity": round(result['macro_specificity'], 4),
                "macro_f1": round(result['macro_f1'], 4)
            })
        
        best_k = max(evaluator.k_values, key=lambda k: results[k]['overall_accuracy'])
        best_accuracy = results[best_k]['overall_accuracy']
        
        return {
            "status": "success",
            "summary": summary,
            "best_k": best_k,
            "best_accuracy": round(best_accuracy, 4)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/k-parameter/detailed/{k}", summary="Get Detailed Metrics for Specific K")
async def get_k_parameter_detailed(k: int) -> Dict:
    """
    Get detailed metrics untuk nilai K tertentu
    
    Args:
    - k: Nilai K (3, 5, 7, 9, atau custom)
    """
    try:
        evaluator = KParameterEvaluator()
        X_data, y_data = await asyncio.to_thread(evaluator.fetch_data_from_supabase)
        result = await asyncio.to_thread(evaluator.evaluate_k, X_data, y_data, k)
        
        # Prepare detailed metrics
        detailed_metrics = []
        metrics_per_class = result['metrics_per_class']
        
        for class_idx in range(evaluator.num_classes):
            metrics = metrics_per_class[class_idx]
            detailed_metrics.append({
                "class_idx": class_idx,
                "class_name": evaluator.class_names[class_idx],
                "confusion_matrix": {
                    "tp": int(metrics['tp']),
                    "tn": int(metrics['tn']),
                    "fp": int(metrics['fp']),
                    "fn": int(metrics['fn'])
                },
                "metrics": {
                    "accuracy": round(metrics['accuracy'], 4),
                    "precision": round(metrics['precision'], 4),
                    "recall": round(metrics['recall'], 4),
                    "specificity": round(metrics['specificity'], 4),
                    "f1_score": round(metrics['f1_score'], 4)
                }
            })
        
        return {
            "status": "success",
            "k": k,
            "overall_accuracy": round(result['overall_accuracy'], 4),
            "macro_accuracy": round(result['macro_accuracy'], 4),
            "macro_precision": round(result['macro_precision'], 4),
            "macro_recall": round(result['macro_recall'], 4),
            "detailed_metrics": detailed_metrics
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
