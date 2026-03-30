# KNN Global Evaluasi - Usage Guide

## Deskripsi

**Global KNN Evaluation** adalah sistem evaluasi performa Model KNN yang digunakan untuk admin dashboard & monitoring keseluruhan sistem.

### Karakteristik:
- ✅ Fetch **semua data** dari tabel `pengukuran`
- ✅ Tidak ada filter `user_id` (semua kader)
- ✅ Tidak ada filter bulan (semua waktu)
- ✅ Gunakan K=5 (nilai optimal dari K parameter evaluation)
- ✅ Calculate confusion matrix dan semua metrics
- ✅ Provide interpretasi performa sistem secara global

---

## Kapan Menggunakan Global Evaluation

| Skenario | Gunakan |
|----------|---------|
| Admin ingin lihat performa model secara keseluruhan | ✓ Global |
| Monitoring health sistem ML | ✓ Global |
| KNN masih bagus atau sudah degrade? | ✓ Global |
| Lihat performa staff individual (kader) | ✗ Gunakan Per-Kader Evaluation |
| Compare K values (3, 5, 7, 9) | ✗ Gunakan K Parameter Evaluation |

---

## Backend Usage

### Script Evaluation

```python
from app.ml.evaluate_knn_global import KNNGlobalEvaluator

# Initialize
evaluator = KNNGlobalEvaluator(k=5)

# Run evaluation
result = evaluator.evaluate_global()

# Print results dengan formatting
evaluator.print_results(result)
print(evaluator.get_interpretation(result))
```

### Output Structure

```python
{
    "k": 5,                           # K value yang digunakan
    "n_total_samples": 1234,          # Total record yang dievaluasi
    "confusion_matrix": {
        "tp": 45,                     # True Positive (stunting tercatch)
        "tn": 1100,                   # True Negative (normal dikonfirmasi)
        "fp": 34,                     # False Positive (normal dikira stunting)
        "fn": 55                      # False Negative (stunting terlewat - PENTING!)
    },
    "metrics": {
        "accuracy": 0.9297,           # Overall correctness
        "precision": 0.5697,          # TP/(TP+FP) - akurasi positive prediction
        "recall": 0.4500,             # TP/(TP+FN) - coverage stunting detection
        "specificity": 0.9703,        # TN/(TN+FP) - accuracy normal detection
        "f1_score": 0.5097            # Balance Precision & Recall
    },
    "label_distribution": {
        "normal_true": 1134,          # Actual normal samples
        "stunting_true": 100,         # Actual stunting samples
        "normal_pred": 1100,          # Predicted normal
        "stunting_pred": 134          # Predicted stunting
    },
    "class_distribution_4class": {
        "0": 500,                     # Normal + Gizi Baik
        "1": 634,                     # Normal + Kurang Gizi
        "2": 45,                      # Stunting + Gizi Baik
        "3": 55                       # Stunting + Kurang Gizi
    }
}
```

---

## API Endpoints

### 1. Full Evaluation

**Endpoint:** `GET /api/evaluation/knn/global`

**Response:**
```json
{
    "status": "success",
    "data": { /* result object */ },
    "interpretation": "...",
    "timestamp": "2024-11-20T10:30:00"
}
```

**Interpretation Output:**
```
🟢 Overall Performance: Excellent (Accuracy: 92.97%)

📋 Recall Analysis (Coverage of Stunting Detection):
  ✓ Good: Model detects 75-85% of actual stunting cases

📋 Precision Analysis (True Positive Rate):
  ✓ High: 80%+ of predicted stunting are correct

📋 Specificity Analysis (Normal Detection):
  ✓ Excellent: 85%+ of normal cases correctly identified

📊 Recommendation:
  ✓ Model is ready for production use
```

---

### 2. Quick Summary

**Endpoint:** `GET /api/evaluation/knn/global/summary`

**Use Case:** Cepat check di admin dashboard tanpa full details

**Response:**
```json
{
    "status": "success",
    "data": {
        "accuracy": 0.9297,
        "recall": 0.4500,
        "precision": 0.5697,
        "f1_score": 0.5097,
        "performance": "Good",
        "n_samples": 1234,
        "tp": 45,
        "tn": 1100,
        "fp": 34,
        "fn": 55
    },
    "timestamp": "2024-11-20T10:30:00"
}
```

---

### 3. Confusion Matrix Only

**Endpoint:** `GET /api/evaluation/knn/global/confusion-matrix`

**Use Case:** Visualization components (chart, heatmap)

**Response:**
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

---

## Metrics Explanation

### Accuracy
```
Accuracy = (TP + TN) / Total

45 + 1100 / 1234 = 92.97%

✓ Benar: Model benar prediksi 93% data
⚠ Tidak optimal jika data imbalanced (banyak Normal, dikit Stunting)
```

### Recall (CRITICAL)
```
Recall = TP / (TP + FN)

45 / (45 + 55) = 45%

❌ PENTING: Model hanya catch 45% stunting cases
⚠ Artinya 55% stunting terlewat - ini CRITICAL di healthcare!
```

### Precision
```
Precision = TP / (TP + FP)

45 / (45 + 34) = 56.97%

⚠ Dari 79 positive predictions, hanya 45 yang benar
```

### Specificity
```
Specificity = TN / (TN + FP)

1100 / (1100 + 34) = 97.03%

✓ Model sangat baik mengenali Normal cases
```

### F1-Score
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)

2 * (0.5697 * 0.45) / (0.5697 + 0.45) = 0.5097

⚠ Balance antara Precision dan Recall
```

---

## Performance Levels

| Level | Accuracy Range | Status |
|-------|---|---|
| 🟢 Excellent | ≥ 85% | Ready for production |
| 🟡 Good | 75-85% | Good, monitor closely |
| 🟠 Fair | 65-75% | Needs improvement |
| 🔴 Poor | < 65% | Critical - review model |

---

## Interpretation Guidelines

### Recall adalah PRIORITAS #1 (Healthcare Context)

```
Recall < 80% = RISK!
❌ Terlalu banyak stunting yang terlewat
❌ Anak stunting tidak terdeteksi = Tidak ditangani
```

### False Negatives (FN) adalah yang PALING BERBAHAYA

```
FN = Stunting sebenarnya tapi diprediksi Normal
Artinya: Anak stunting tidak terdeteksi & tidak ditangani!
⚠ Medical context: This is CRITICAL
```

### False Positives (FP) BISA DIHANDLE

```
FP = Normal sebenarnya tapi diprediksi Stunting
Artinya: Kader melakukan pemeriksaan lebih dalam = OK
✓ Better safe than sorry di healthcare
```

---

## Troubleshooting

### Problem: Empty Data or Connection Error

```python
❌ Error fetching all data: Tidak ada data di tabel pengukuran
```

**Solution:**
1. Check Supabase connection
2. Verify `pengukuran` table exists
3. Verify data has values in all 6 features

### Problem: All Metrics = 0

```python
❌ Error: Semua metric zero division
```

**Solution:**
1. Model tidak melakukan prediksi stunting sama sekali (all pred = 0)
2. Check data labeling - apakah status_gizi_label benar?

### Problem: Recall sangat rendah

```python
⚠ Recall = 0.15 (hanya 15% stunting terdeteksi)
```

**Solution:**
1. Check K value - mungkin K=5 tidak optimal di versi data baru
2. Gunakan K Parameter Evaluation untuk re-test K values
3. Check feature engineering - apakah ada data leakage?

---

## Frontend Integration Example

### React Component

```jsx
import { useEffect, useState } from 'react';

export function GlobalEvaluationDashboard() {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/evaluation/knn/global')
            .then(res => res.json())
            .then(data => {
                setResult(data.data);
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading...</div>;
    if (!result) return <div>Error</div>;

    const m = result.metrics;
    const cm = result.confusion_matrix;

    return (
        <div className="admin-dashboard">
            <h1>🏥 Global KNN Performance</h1>
            
            <div className="metrics-row">
                <MetricCard 
                    label="Accuracy" 
                    value={(m.accuracy * 100).toFixed(2) + '%'}
                    color={m.accuracy >= 0.85 ? 'green' : 'orange'}
                />
                <MetricCard 
                    label="Recall" 
                    value={(m.recall * 100).toFixed(2) + '%'}
                    color={m.recall >= 0.80 ? 'green' : 'red'}
                    critical="CRITICAL"
                />
                <MetricCard 
                    label="Precision" 
                    value={(m.precision * 100).toFixed(2) + '%'}
                />
            </div>

            <ConfusionMatrixChart cm={cm} />
        </div>
    );
}

function MetricCard({ label, value, color, critical }) {
    return (
        <div style={{ borderColor: color }} className="metric-card">
            <h3>{label}</h3>
            <p>{value}</p>
            {critical && <span className="badge">{critical}</span>}
        </div>
    );
}
```

---

## Quick Checklist

- [ ] K value = 5 (verified dari K parameter evaluation)
- [ ] Data dari tabel `pengukuran` (no filtering)
- [ ] All 6 features: jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala
- [ ] Binary conversion: 0,1→Normal(0), 2,3→Stunting(1)
- [ ] Recall ≥ 80% (critical for medical context)
- [ ] No data leakage (no Z-Scores as input)
- [ ] Confusion matrix calculated dengan sklearn.metrics.confusion_matrix

---

## Reference

- Backend: `backend/app/ml/evaluate_knn_global.py`
- API: `api/app/ml/evaluate_knn_global.py`
- Routes: `backend/app/routes/knn_global_evaluation.py`
- Class: `KNNGlobalEvaluator`

---

## Contact

Untuk pertanyaan tentang global evaluation:
- Check `KNN_GLOBAL_QUICK_START.md` untuk quick reference
- Check `KNN_GLOBAL_API_ENDPOINTS.md` untuk API details
