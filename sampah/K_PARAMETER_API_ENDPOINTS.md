# API Endpoints untuk Evaluasi Parameter K

## Overview

Endpoints untuk menjalankan evaluasi parameter K pada algoritma KNN melalui HTTP request.

---

## Endpoints

### 1. Full Evaluation (Summary + Detailed)

**Endpoint:**
```
GET /api/evaluation/k-parameter
```

**Description:**
Evaluasi lengkap untuk semua K values dengan summary tabel dan detailed metrics per class.

**Response Time:** 
~30 detik (tergantung data volume)

**Response Format:**

```json
{
  "status": "success",
  "message": "K parameter evaluation completed",
  "summary": [
    {
      "k": 3,
      "overall_accuracy": 0.7234,
      "macro_accuracy": 0.6145,
      "macro_precision": 0.6234,
      "macro_recall": 0.5892,
      "macro_specificity": 0.8145,
      "macro_f1": 0.6012
    },
    {
      "k": 5,
      "overall_accuracy": 0.7456,
      "macro_accuracy": 0.6423,
      "macro_precision": 0.6512,
      "macro_recall": 0.6234,
      "macro_specificity": 0.8234,
      "macro_f1": 0.6367
    },
    ...
  ],
  "detailed_metrics": {
    "3": [
      {
        "class_idx": 0,
        "class_name": "Normal & Gizi Baik (0)",
        "tp": 345,
        "tn": 2456,
        "fp": 123,
        "fn": 234,
        "accuracy": 0.8923,
        "precision": 0.7372,
        "recall": 0.5950,
        "specificity": 0.9525,
        "f1_score": 0.6572
      },
      ...
    ],
    "5": [...],
    ...
  },
  "best_k": {
    "k": 5,
    "overall_accuracy": 0.7456,
    "recommendation": "Use K=5 for best overall accuracy"
  }
}
```

**Example Usage:**

```bash
# cURL
curl -X GET http://localhost:8000/api/evaluation/k-parameter

# Fetch (JavaScript)
fetch('http://localhost:8000/api/evaluation/k-parameter')
  .then(res => res.json())
  .then(data => console.log(data))
```

---

### 2. Summary Only (Fast)

**Endpoint:**
```
GET /api/evaluation/k-parameter/summary
```

**Description:**
Hanya menampilkan summary tabel (tanpa detailed metrics per class). Lebih cepat jika hanya butuh overview.

**Response Time:**
~30 detik (sama, tapi response size lebih kecil)

**Response Format:**

```json
{
  "status": "success",
  "summary": [
    {
      "k": 3,
      "overall_accuracy": 0.7234,
      "macro_accuracy": 0.6145,
      "macro_precision": 0.6234,
      "macro_recall": 0.5892,
      "macro_specificity": 0.8145,
      "macro_f1": 0.6012
    },
    {
      "k": 5,
      "overall_accuracy": 0.7456,
      "macro_accuracy": 0.6423,
      "macro_precision": 0.6512,
      "macro_recall": 0.6234,
      "macro_specificity": 0.8234,
      "macro_f1": 0.6367
    },
    ...
  ],
  "best_k": 5,
  "best_accuracy": 0.7456
}
```

**Example Usage:**

```bash
# cURL
curl -X GET http://localhost:8000/api/evaluation/k-parameter/summary

# Fetch (JavaScript)
fetch('http://localhost:8000/api/evaluation/k-parameter/summary')
  .then(res => res.json())
  .then(data => console.log(data.summary))
```

---

### 3. Detailed Metrics for Specific K

**Endpoint:**
```
GET /api/evaluation/k-parameter/detailed/{k}
```

**Description:**
Evaluasi untuk satu nilai K tertentu dengan detail metrics per class.

**Parameters:**
- `k` (path param, integer): Nilai K (misal: 3, 5, 7, 9, atau custom nilai lain)

**Response Time:**
~5-15 detik (lebih cepat karena hanya 1 K)

**Response Format:**

```json
{
  "status": "success",
  "k": 5,
  "overall_accuracy": 0.7456,
  "macro_accuracy": 0.6423,
  "macro_precision": 0.6512,
  "macro_recall": 0.6234,
  "detailed_metrics": [
    {
      "class_idx": 0,
      "class_name": "Normal & Gizi Baik (0)",
      "confusion_matrix": {
        "tp": 345,
        "tn": 2456,
        "fp": 123,
        "fn": 234
      },
      "metrics": {
        "accuracy": 0.8923,
        "precision": 0.7372,
        "recall": 0.5950,
        "specificity": 0.9525,
        "f1_score": 0.6572
      }
    },
    {
      "class_idx": 1,
      "class_name": "Normal & Kurang Gizi (1)",
      "confusion_matrix": {
        "tp": 123,
        "tn": 2678,
        "fp": 89,
        "fn": 110
      },
      "metrics": {
        "accuracy": 0.9456,
        "precision": 0.5803,
        "recall": 0.5275,
        "specificity": 0.9679,
        "f1_score": 0.5527
      }
    },
    ...
  ]
}
```

**Example Usage:**

```bash
# cURL - Evaluasi K=5
curl -X GET http://localhost:8000/api/evaluation/k-parameter/detailed/5

# Fetch (JavaScript)
fetch('http://localhost:8000/api/evaluation/k-parameter/detailed/7')
  .then(res => res.json())
  .then(data => console.log(data.detailed_metrics))
```

---

## Integrasi dengan Main App

Untuk mengaktifkan endpoints ini, tambahkan router ke `app/main.py`:

```python
from app.routes.k_parameter_evaluation import router as k_evaluation_router

app.include_router(k_evaluation_router)
```

---

## Interpretasi Response

### Summary Tabel

| Field | Arti |
|-------|------|
| k | Nilai K yang ditest |
| overall_accuracy | Seberapa akurat prediksi untuk semua class |
| macro_accuracy | Rata-rata accuracy per class (macro-average) |
| macro_precision | Rata-rata precision per class |
| macro_recall | Rata-rata recall per class |
| macro_specificity | Rata-rata specificity per class |
| macro_f1 | Rata-rata F1-Score per class |

**Higher is better** untuk semua metrics ini.

### Per-Class Metrics

| Field | Arti |
|-------|------|
| TP (True Positive) | Prediksi benar class X |
| TN (True Negative) | Prediksi benar bukan class X |
| FP (False Positive) | Prediksi salah class X (seharusnya bukan) |
| FN (False Negative) | Prediksi salah bukan class X (seharusnya class X) |
| Precision | TP / (TP + FP) - Keakuratan positive predictions |
| Recall | TP / (TP + FN) - Coverage dari positive cases |
| Specificity | TN / (TN + FP) - Coverage dari negative cases |
| F1-Score | Kombinasi precision dan recall |

### Contoh Interpretasi

Jika response menunjukkan:

```json
{
  "k": 5,
  "overall_accuracy": 0.7456,
  "best_k": 5
}
```

**Artinya:**
- K=5 adalah yang terbaik dengan accuracy 74.56%
- Untuk setiap 100 prediksi, model benar ~75 kali

---

## Frontend Integration Example

### React Component

```jsx
import React, { useState } from 'react';

export default function KParameterEvaluation() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const runEvaluation = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/evaluation/k-parameter/summary');
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={runEvaluation} disabled={loading}>
        {loading ? 'Evaluating...' : 'Run K Parameter Evaluation'}
      </button>

      {results && (
        <table>
          <thead>
            <tr>
              <th>K</th>
              <th>Accuracy</th>
              <th>Precision</th>
              <th>Recall</th>
              <th>F1-Score</th>
            </tr>
          </thead>
          <tbody>
            {results.summary.map((row) => (
              <tr key={row.k}>
                <td>{row.k}</td>
                <td>{row.overall_accuracy.toFixed(4)}</td>
                <td>{row.macro_precision.toFixed(4)}</td>
                <td>{row.macro_recall.toFixed(4)}</td>
                <td>{row.macro_f1.toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {results && (
        <p>
          ✓ Best K: {results.best_k} (Accuracy: {results.best_accuracy.toFixed(4)})
        </p>
      )}
    </div>
  );
}
```

---

## Performance Notes

- **First run:** ~30 detik (tergantung data volume)
- **Subsequent runs:** Sama (tidak ada caching karena fetch fresh dari DB setiap kali)

Jika ingin optimize:
1. Implementasi caching (Redis)
2. Run evaluation async di background
3. Schedule evaluasi di off-peak hours

---

## Error Handling

### Possible Errors

**400 Bad Request:**
```json
{
  "detail": "Tidak ada data di tabel pengukuran"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Evaluation failed: [error message]"
}
```

---

## File Lokasi

- **Routes:** `backend/app/routes/k_parameter_evaluation.py`
- **Logic:** `backend/app/ml/evaluate_k_parameter.py`
- **Documentation:** `EVALUASI_K_PARAMETER_USAGE_GUIDE.md`

