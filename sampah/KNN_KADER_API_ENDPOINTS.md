# API Endpoints: Evaluasi KNN per Kader

## Overview

API endpoints untuk menjalankan evaluasi KNN untuk data kader spesifik melalui HTTP request.

---

## Base URL

```
http://localhost:8000/api/evaluation
```

---

## Endpoints

### 1. Evaluate Kader (Semua Bulan)

**Endpoint:**
```
GET /knn/kader/{user_id}
```

**Parameters:**
- `user_id` (path, required): ID kader/user
- `k` (query, optional): Nilai K (default: 5)
- `year` (query, optional): Tahun (default: 2024)

**Response:**
```json
{
  "status": "success",
  "user_id": 2,
  "k": 5,
  "n_samples": 42,
  "period": "All months / 2024",
  "confusion_matrix": {
    "tp": 13,
    "tn": 27,
    "fp": 1,
    "fn": 1
  },
  "label_distribution": {
    "normal_true": 28,
    "stunting_true": 14,
    "normal_pred": 29,
    "stunting_pred": 13
  },
  "metrics": {
    "accuracy": 0.9524,
    "precision": 0.9286,
    "recall": 0.9286,
    "specificity": 0.9643,
    "f1_score": 0.9286
  },
  "interpretation": "Model performance: Excellent..."
}
```

**Examples:**

```bash
# Default K=5, Year=2024
curl http://localhost:8000/api/evaluation/knn/kader/2

# Custom K=7
curl "http://localhost:8000/api/evaluation/knn/kader/2?k=7"

# Custom year
curl "http://localhost:8000/api/evaluation/knn/kader/2?year=2024&k=5"
```

**JavaScript/Fetch:**

```javascript
fetch('http://localhost:8000/api/evaluation/knn/kader/2')
  .then(res => res.json())
  .then(data => {
    console.log('Accuracy:', data.metrics.accuracy);
    console.log('Recall:', data.metrics.recall);
  });
```

---

### 2. Evaluate Kader (Bulan Spesifik)

**Endpoint:**
```
GET /knn/kader/{user_id}/month/{month}
```

**Parameters:**
- `user_id` (path, required): ID kader
- `month` (path, required): Bulan (1-12)
- `k` (query, optional): Nilai K (default: 5)
- `year` (query, optional): Tahun (default: 2024)

**Response:**
```json
{
  "status": "success",
  "user_id": 2,
  "month": 3,
  "month_name": "March",
  "year": 2024,
  "k": 5,
  "n_samples": 6,
  "confusion_matrix": {
    "tp": 2,
    "tn": 3,
    "fp": 0,
    "fn": 1
  },
  "label_distribution": {
    "normal_true": 4,
    "stunting_true": 2,
    "normal_pred": 4,
    "stunting_pred": 2
  },
  "metrics": {
    "accuracy": 0.8333,
    "precision": 1.0,
    "recall": 0.6667,
    "specificity": 1.0,
    "f1_score": 0.8
  },
  "interpretation": "..."
}
```

**Examples:**

```bash
# Maret 2024
curl "http://localhost:8000/api/evaluation/knn/kader/2/month/3"

# Januari 2024, K=7
curl "http://localhost:8000/api/evaluation/knn/kader/2/month/1?k=7"

# Desember 2023
curl "http://localhost:8000/api/evaluation/knn/kader/2/month/12?year=2023"
```

**JavaScript:**

```javascript
// Bulan Januari (1)
fetch('http://localhost:8000/api/evaluation/knn/kader/2/month/1')
  .then(res => res.json())
  .then(data => {
    console.log(`Accuracy for ${data.month_name}: ${data.metrics.accuracy}`);
  });
```

---

### 3. Get Summary (Quick View)

**Endpoint:**
```
GET /knn/kader/{user_id}/summary
```

**Parameters:**
- `user_id` (path, required): ID kader
- `k` (query, optional): Nilai K (default: 5)
- `year` (query, optional): Tahun (default: 2024)

**Response (Lightweight):**
```json
{
  "status": "success",
  "user_id": 2,
  "k": 5,
  "n_samples": 42,
  "metrics": {
    "accuracy": 0.9524,
    "precision": 0.9286,
    "recall": 0.9286,
    "specificity": 0.9643,
    "f1_score": 0.9286
  }
}
```

**Examples:**

```bash
curl http://localhost:8000/api/evaluation/knn/kader/2/summary

curl "http://localhost:8000/api/evaluation/knn/kader/2/summary?k=7"
```

**Use Case:** Dashboard / quick metrics display

---

### 4. Batch Evaluate All Months

**Endpoint:**
```
POST /knn/kader/{user_id}/evaluate-all-months
```

**Parameters:**
- `user_id` (path, required): ID kader
- `k` (query, optional): Nilai K (default: 5)
- `year` (query, optional): Tahun (default: 2024)

**Response:**
```json
{
  "status": "success",
  "user_id": 2,
  "k": 5,
  "year": 2024,
  "successful_months": [1, 2, 3, 5, 7, 9, 10, 11],
  "failed_months": [4, 6, 8, 12],
  "results_by_month": {
    "1": {
      "n_samples": 5,
      "metrics": {
        "accuracy": 0.8,
        "precision": 0.75,
        "recall": 0.75,
        "specificity": 0.83,
        "f1_score": 0.75
      },
      "confusion_matrix": {"tp": 3, "tn": 5, "fp": 1, "fn": 1}
    },
    "2": {...},
    "3": {...}
  },
  "average_metrics": {
    "accuracy": 0.8923,
    "precision": 0.8234,
    "recall": 0.7945,
    "specificity": 0.9123,
    "f1_score": 0.8067
  }
}
```

**Examples:**

```bash
curl -X POST http://localhost:8000/api/evaluation/knn/kader/2/evaluate-all-months

curl -X POST "http://localhost:8000/api/evaluation/knn/kader/2/evaluate-all-months?k=7"
```

**JavaScript:**

```javascript
fetch('http://localhost:8000/api/evaluation/knn/kader/2/evaluate-all-months', {
  method: 'POST'
})
  .then(res => res.json())
  .then(data => {
    console.log('Successful months:', data.successful_months);
    console.log('Average accuracy:', data.average_metrics.accuracy);
    
    // Plot per-month metrics
    Object.entries(data.results_by_month).forEach(([month, result]) => {
      console.log(`Month ${month}: Acc=${result.metrics.accuracy}`);
    });
  });
```

---

### 5. Get Best Performance Month

**Endpoint:**
```
GET /knn/kader/{user_id}/best-month
```

**Parameters:**
- `user_id` (path, required): ID kader
- `k` (query, optional): Nilai K (default: 5)
- `year` (query, optional): Tahun (default: 2024)
- `metric` (query, optional): Metrik untuk ranking (default: "accuracy")
  - Options: accuracy, precision, recall, specificity, f1_score

**Response:**
```json
{
  "status": "success",
  "user_id": 2,
  "best_month": 3,
  "best_month_name": "March",
  "metric": "recall",
  "value": 0.9286,
  "all_months": {
    "1": 0.75,
    "2": 0.8,
    "3": 0.9286,
    "5": 0.85,
    "7": 0.78,
    "9": 0.82,
    "10": 0.88,
    "11": 0.8
  }
}
```

**Examples:**

```bash
# Best by accuracy (default)
curl "http://localhost:8000/api/evaluation/knn/kader/2/best-month"

# Best by recall (coverage)
curl "http://localhost:8000/api/evaluation/knn/kader/2/best-month?metric=recall"

# Best by F1-score
curl "http://localhost:8000/api/evaluation/knn/kader/2/best-month?metric=f1_score"
```

**JavaScript:**

```javascript
// Find best month by recall (most important for medical)
fetch('http://localhost:8000/api/evaluation/knn/kader/2/best-month?metric=recall')
  .then(res => res.json())
  .then(data => {
    console.log(`Best month: ${data.best_month_name} with recall ${data.value}`);
    console.log(`All months performance:`, data.all_months);
  });
```

---

## Integration Examples

### React Component: Single Kader Evaluation

```jsx
import React, { useState } from 'react';

export default function KaderEvaluation({ kaderId }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const evaluate = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `http://localhost:8000/api/evaluation/knn/kader/${kaderId}`
      );
      const data = await res.json();
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={evaluate} disabled={loading}>
        {loading ? 'Evaluating...' : 'Evaluate KNN'}
      </button>

      {result && (
        <div>
          <h3>Results for Kader {result.user_id}</h3>
          <p>Samples: {result.n_samples}</p>
          
          <table>
            <tr><td>Accuracy</td><td>{(result.metrics.accuracy * 100).toFixed(2)}%</td></tr>
            <tr><td>Recall</td><td>{(result.metrics.recall * 100).toFixed(2)}%</td></tr>
            <tr><td>Precision</td><td>{(result.metrics.precision * 100).toFixed(2)}%</td></tr>
            <tr><td>F1-Score</td><td>{result.metrics.f1_score.toFixed(4)}</td></tr>
          </table>

          <pre>{result.interpretation}</pre>
        </div>
      )}
    </div>
  );
}
```

### Vue Component: Batch Monthly Evaluation

```vue
<template>
  <div>
    <button @click="evaluateAllMonths" :disabled="loading">
      {{ loading ? 'Loading...' : 'Evaluate All Months' }}
    </button>

    <div v-if="results">
      <h3>Monthly Performance</h3>
      <chart :data="chartData" type="line"></chart>

      <p>Average Accuracy: {{ results.average_metrics.accuracy }}</p>
      <p>Best Months: {{ results.successful_months.join(', ') }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      results: null,
      loading: false
    };
  },
  computed: {
    chartData() {
      if (!this.results) return null;
      return {
        labels: Object.keys(this.results.results_by_month),
        datasets: [
          {
            label: 'Accuracy',
            data: Object.values(this.results.results_by_month)
              .map(r => r.metrics.accuracy)
          },
          {
            label: 'Recall',
            data: Object.values(this.results.results_by_month)
              .map(r => r.metrics.recall)
          }
        ]
      };
    }
  },
  methods: {
    async evaluateAllMonths() {
      this.loading = true;
      try {
        const res = await fetch(
          `/api/evaluation/knn/kader/2/evaluate-all-months`,
          { method: 'POST' }
        );
        this.results = await res.json();
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

## Error Handling

### 400 Bad Request

**Scenario:** Invalid month or no data

```json
{
  "detail": "Tidak ada data untuk kader_id=999"
}
```

### 500 Internal Server Error

**Scenario:** Database error, missing configuration

```json
{
  "detail": "Evaluation failed: [error details]"
}
```

---

## Performance Notes

- **First run:** ~5-10 detik (tergantung data volume)
- **Batch evaluate:** ~30-60 detik (untuk 12 bulan)
- **Summary endpoint:** ~5 detik (lebih cepat, data minimal)

---

## Integration Checklist

- [ ] Routes sudah di-include di `app/main.py`
- [ ] Supabase credentials sudah di `.env`
- [ ] K=5 disetup sebagai default
- [ ] Error handling sudah implemented
- [ ] API testing sudah dilakukan

---

## Konfigurasi untuk Production

**Update `backend/app/main.py`:**

```python
from app.routes.knn_kader_evaluation import router as knn_kader_router

app.include_router(knn_kader_router)
```

**Restart server:**

```bash
python -m app.main
# atau
uvicorn app.main:app --reload
```

---

## Troubleshooting

### Endpoint not found (404)

**Issue:** Routes tidak registered

**Solution:**
```python
# Add to main.py
from app.routes.knn_kader_evaluation import router as knn_kader_router
app.include_router(knn_kader_router)
```

### No data error

**Issue:** Kader tidak punya data pengukuran

**Solution:**
1. Verifikasi `user_id` valid
2. Check apakah ada data di database
3. Try dengan kader yang punya banyak data

### Timeout (evaluation lama)

**Issue:** Batch evaluate 12 bulan memakan waktu

**Solution:**
- Use summary endpoint untuk quick view
- Evaluate per-month secara on-demand
- Implement caching dengan Redis

---

## File Lokasi

- **Routes:** `backend/app/routes/knn_kader_evaluation.py`
- **Logic:** `backend/app/ml/evaluate_knn_per_kader.py`
- **Dokumentasi:** Semua file `.md` di root workspace

