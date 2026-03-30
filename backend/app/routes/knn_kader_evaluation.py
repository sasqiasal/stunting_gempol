"""
FastAPI Routes untuk Evaluasi KNN per Kader
Endpoint untuk menjalankan evaluasi KNN untuk data kader tertentu
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
import asyncio
from app.ml.evaluate_knn_per_kader import KNNKaderEvaluator

router = APIRouter(prefix="/api/evaluation", tags=["knn_kader"])


@router.get("/knn/kader/{user_id}", summary="Evaluate KNN for Specific Kader")
async def evaluate_knn_kader(
    user_id: int,
    k: int = Query(5, description="Nilai K untuk KNN (default: 5)"),
    year: int = Query(2024, description="Tahun untuk evaluasi (default: 2024)")
) -> Dict:
    """
    Evaluasi model KNN untuk kader tertentu (semua bulan)
    
    Parameters:
    - user_id: ID kader/user
    - k: Nilai K untuk KNN (default: 5)
    - year: Tahun (default: 2024)
    
    Returns:
    - Confusion matrix
    - Metrik: Accuracy, Precision, Recall, Specificity, F1-Score
    - Label distribution
    - Interpretation
    """
    try:
        evaluator = KNNKaderEvaluator(k=k)
        
        # Run evaluation in background
        result = await asyncio.to_thread(
            evaluator.evaluate_kader,
            user_id=user_id,
            month=None,
            year=year
        )
        
        # Get interpretation
        interpretation = evaluator.get_interpretation(result)
        
        return {
            "status": "success",
            "user_id": user_id,
            "k": k,
            "n_samples": result['n_samples'],
            "period": f"All months / {year}",
            "confusion_matrix": result['confusion_matrix'],
            "label_distribution": result['label_distribution'],
            "metrics": {
                "accuracy": round(result['metrics']['accuracy'], 4),
                "precision": round(result['metrics']['precision'], 4),
                "recall": round(result['metrics']['recall'], 4),
                "specificity": round(result['metrics']['specificity'], 4),
                "f1_score": round(result['metrics']['f1_score'], 4)
            },
            "interpretation": interpretation.strip()
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/knn/kader/{user_id}/month/{month}", summary="Evaluate KNN for Kader in Specific Month")
async def evaluate_knn_kader_monthly(
    user_id: int,
    month: int = 1,
    k: int = Query(5, description="Nilai K untuk KNN (default: 5)"),
    year: int = Query(2024, description="Tahun (default: 2024)")
) -> Dict:
    """
    Evaluasi model KNN untuk kader tertentu di bulan spesifik
    
    Parameters:
    - user_id: ID kader/user
    - month: Bulan (1-12)
    - k: Nilai K untuk KNN (default: 5)
    - year: Tahun (default: 2024)
    
    Returns:
    - Confusion matrix
    - Metrik: Accuracy, Precision, Recall, Specificity, F1-Score
    - Label distribution
    - Interpretation
    """
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    
    try:
        evaluator = KNNKaderEvaluator(k=k)
        
        # Run evaluation in background
        result = await asyncio.to_thread(
            evaluator.evaluate_kader,
            user_id=user_id,
            month=month,
            year=year
        )
        
        # Get interpretation
        interpretation = evaluator.get_interpretation(result)
        
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        return {
            "status": "success",
            "user_id": user_id,
            "month": month,
            "month_name": month_names[month],
            "year": year,
            "k": k,
            "n_samples": result['n_samples'],
            "confusion_matrix": result['confusion_matrix'],
            "label_distribution": result['label_distribution'],
            "metrics": {
                "accuracy": round(result['metrics']['accuracy'], 4),
                "precision": round(result['metrics']['precision'], 4),
                "recall": round(result['metrics']['recall'], 4),
                "specificity": round(result['metrics']['specificity'], 4),
                "f1_score": round(result['metrics']['f1_score'], 4)
            },
            "interpretation": interpretation.strip()
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/knn/kader/{user_id}/summary", summary="Get KNN Summary for Kader (All Months)")
async def get_knn_kader_summary(
    user_id: int,
    k: int = Query(5, description="Nilai K untuk KNN (default: 5)"),
    year: int = Query(2024, description="Tahun (default: 2024)")
) -> Dict:
    """
    Get summary hasil evaluasi KNN untuk kader (semua bulan)
    Hanya menampilkan metrik utama, tanpa detail per-class
    
    Parameters:
    - user_id: ID kader/user
    - k: Nilai K untuk KNN (default: 5)
    - year: Tahun (default: 2024)
    """
    try:
        evaluator = KNNKaderEvaluator(k=k)
        
        result = await asyncio.to_thread(
            evaluator.evaluate_kader,
            user_id=user_id,
            month=None,
            year=year
        )
        
        return {
            "status": "success",
            "user_id": user_id,
            "k": k,
            "n_samples": result['n_samples'],
            "metrics": {
                "accuracy": round(result['metrics']['accuracy'], 4),
                "precision": round(result['metrics']['precision'], 4),
                "recall": round(result['metrics']['recall'], 4),
                "specificity": round(result['metrics']['specificity'], 4),
                "f1_score": round(result['metrics']['f1_score'], 4)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knn/kader/{user_id}/evaluate-all-months", summary="Evaluate KNN for All Months")
async def evaluate_knn_all_months(
    user_id: int,
    k: int = Query(5, description="Nilai K untuk KNN (default: 5)"),
    year: int = Query(2024, description="Tahun (default: 2024)")
) -> Dict:
    """
    Batch evaluate KNN untuk kader di semua bulan (1-12)
    Menampilkan hasil per-bulan dalam satu response
    
    Parameters:
    - user_id: ID kader/user
    - k: Nilai K untuk KNN (default: 5)
    - year: Tahun (default: 2024)
    
    Returns:
    - Dictionary dengan results per-bulan
    - Summary untuk semua bulan
    """
    try:
        evaluator = KNNKaderEvaluator(k=k)
        
        results_by_month = {}
        successful_months = []
        failed_months = []
        
        for month in range(1, 13):
            try:
                result = await asyncio.to_thread(
                    evaluator.evaluate_kader,
                    user_id=user_id,
                    month=month,
                    year=year
                )
                
                results_by_month[month] = {
                    "n_samples": result['n_samples'],
                    "metrics": {
                        "accuracy": round(result['metrics']['accuracy'], 4),
                        "precision": round(result['metrics']['precision'], 4),
                        "recall": round(result['metrics']['recall'], 4),
                        "specificity": round(result['metrics']['specificity'], 4),
                        "f1_score": round(result['metrics']['f1_score'], 4)
                    },
                    "confusion_matrix": result['confusion_matrix']
                }
                
                successful_months.append(month)
            
            except ValueError:
                # No data for this month
                failed_months.append(month)
            except Exception as e:
                failed_months.append(month)
        
        # Calculate average metrics
        if successful_months:
            avg_metrics = {}
            for metric_name in ['accuracy', 'precision', 'recall', 'specificity', 'f1_score']:
                values = [
                    results_by_month[m]['metrics'][metric_name]
                    for m in successful_months
                ]
                avg_metrics[metric_name] = round(sum(values) / len(values), 4)
        else:
            avg_metrics = None
        
        return {
            "status": "success",
            "user_id": user_id,
            "k": k,
            "year": year,
            "successful_months": successful_months,
            "failed_months": failed_months,
            "results_by_month": results_by_month,
            "average_metrics": avg_metrics
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch evaluation failed: {str(e)}")


@router.get("/knn/kader/{user_id}/best-month", summary="Get Best Performance Month")
async def get_best_month(
    user_id: int,
    k: int = Query(5, description="Nilai K untuk KNN (default: 5)"),
    year: int = Query(2024, description="Tahun (default: 2024)"),
    metric: str = Query("accuracy", description="Metrik untuk ranking (accuracy, recall, f1_score)")
) -> Dict:
    """
    Dapatkan bulan dengan performa terbaik untuk kader tertentu
    
    Parameters:
    - user_id: ID kader/user
    - k: Nilai K untuk KNN (default: 5)
    - year: Tahun (default: 2024)
    - metric: Metrik untuk ranking (accuracy, recall, f1_score)
    """
    if metric not in ['accuracy', 'recall', 'f1_score', 'precision', 'specificity']:
        raise HTTPException(
            status_code=400,
            detail="Metric must be one of: accuracy, precision, recall, specificity, f1_score"
        )
    
    try:
        evaluator = KNNKaderEvaluator(k=k)
        
        results_by_month = {}
        
        for month in range(1, 13):
            try:
                result = await asyncio.to_thread(
                    evaluator.evaluate_kader,
                    user_id=user_id,
                    month=month,
                    year=year
                )
                
                results_by_month[month] = result['metrics'][metric]
            
            except ValueError:
                pass
        
        if not results_by_month:
            raise HTTPException(status_code=400, detail="No valid data found for any month")
        
        best_month = max(results_by_month, key=results_by_month.get)
        best_value = results_by_month[best_month]
        
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        return {
            "status": "success",
            "user_id": user_id,
            "best_month": best_month,
            "best_month_name": month_names[best_month],
            "metric": metric,
            "value": round(best_value, 4),
            "all_months": {m: round(v, 4) for m, v in sorted(results_by_month.items())}
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
