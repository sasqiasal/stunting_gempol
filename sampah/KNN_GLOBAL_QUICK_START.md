# KNN Global Evaluation - Quick Start (30 seconds)

## What is Global Evaluation?

Evaluasi performa KNN **untuk ADMIN DASHBOARD** menggunakan **semua data** dari tabel pengukuran.

**Key Points:**
- ✅ K = 5 (fixed, tidak bisa custom)
- ✅ Evaluate: ALL measurements (no filters)
- ✅ Return: Confusion matrix + all metrics
- ✅ Purpose: Monitor overall system health

---

## Quickest Start (Python)

```python
from app.ml.evaluate_knn_global import KNNGlobalEvaluator

# Run evaluation
evaluator = KNNGlobalEvaluator()
result = evaluator.evaluate_global()

# Print results
evaluator.print_results(result)
print(evaluator.get_interpretation(result))
```

---

## Quickest Start (API)

```bash
# Full evaluation (detail)
curl http://localhost:8000/api/evaluation/knn/global

# Summary only (quick)
curl http://localhost:8000/api/evaluation/knn/global/summary

# Confusion matrix only (chart)
curl http://localhost:8000/api/evaluation/knn/global/confusion-matrix
```

---

## Expected Output Example

```
accuracy:    92.97%
recall:      45.00%  ⚠️ CRITICAL - Only catch 45% stunting
precision:   56.97%
specificity: 97.03%
f1_score:    50.97%

Performance: Good
```

---

## Metrics Explained (Simple)

| Metric | Meaning |
|--------|---------|
| **Accuracy** | % correct predictions overall |
| **Recall** | % stunting cases detected ⚠️ **MOST IMPORTANT** |
| **Precision** | % of positive predictions that are correct |
| **Specificity** | % normal cases detected |
| **F1-Score** | Balance of Precision & Recall |

---

## Confusion Matrix

```
              Predicted
         Normal  Stunting
Actual
Normal:   TN      FP
Stunting: FN      TP ✓

KEY:
✓ TP = Stunting correctly detected (WANT HIGH)
✗ FN = Stunting missed (WANT LOW) ⚠️
```

---

## When to Worry 🚨

| Metric | Red Flag |
|--------|----------|
| Recall < 80% | ❌ Too many stunting cases missed |
| FN > 50 | ❌ More than 50 stunting cases undetected |
| Accuracy < 65% | ❌ Model quality degraded |

---

## API Response Format

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
        "metrics": {
            "accuracy": 0.9297,
            "recall": 0.4500,
            "precision": 0.5697,
            "specificity": 0.9703,
            "f1_score": 0.5097
        }
    },
    "interpretation": "..."
}
```

---

## 3 Ways to Use

### 1. Full Evaluation (Detailed Analysis)
```bash
GET /api/evaluation/knn/global
```
**When:** Deep dive analysis, troubleshooting
**Response:** All metrics, interpretation, class distribution

### 2. Summary Only (Quick Check)
```bash
GET /api/evaluation/knn/global/summary
```
**When:** Dashboard indicator, status check
**Response:** Just accuracy, recall, performance level

### 3. Confusion Matrix (Visualization)
```bash
GET /api/evaluation/knn/global/confusion-matrix
```
**When:** Charts, heatmaps
**Response:** TP/TN/FP/FN only

---

## Files Reference

| File | Purpose |
|------|---------|
| `backend/app/ml/evaluate_knn_global.py` | Main logic |
| `backend/app/routes/knn_global_evaluation.py` | API routes |
| `api/app/ml/evaluate_knn_global.py` | Duplicate (API folder) |
| `api/app/routes/knn_global_evaluation.py` | API routes (API folder) |

---

## Common Questions

**Q: Can I use different K values?**
A: No, K is fixed at 5 (proven optimal from K parameter evaluation)

**Q: Can I filter by user_id or month?**
A: No, global evaluation covers ALL data (no filters)

**Q: How often should I run this?**
A: Once per day or weekly for monitoring

**Q: What if Recall is low?**
A: Run K Parameter Evaluation to re-test K values, or check data quality

**Q: How long does it take?**
A: ~2-5 seconds depending on data volume

---

## Performance Health Check

Run this to check model health:

```python
from app.ml.evaluate_knn_global import KNNGlobalEvaluator

evaluator = KNNGlobalEvaluator()
result = evaluator.evaluate_global()

m = result['metrics']

# Traffic light status
if m['accuracy'] >= 0.85 and m['recall'] >= 0.80:
    print("🟢 GOOD - Model is healthy")
elif m['recall'] >= 0.75:
    print("🟡 CAUTION - Monitor closely")
else:
    print("🔴 ALERT - Model needs review")
```

---

## Next Steps

- 📖 Read full guide: **KNN_GLOBAL_EVALUASI_USAGE_GUIDE.md**
- 🔧 Check API reference: **KNN_GLOBAL_API_ENDPOINTS.md**
- 🔍 Compare K values: Use **K_PARAMETER_EVALUATION** for retesting
- 📊 Check per-staff: Use **PER-KADER EVALUATION** for individual kader performance
