# KNN Global Evaluation - API Endpoints Reference

## Overview

Global Evaluation API untuk admin dashboard - retrieve performa KNN secara keseluruhan tanpa filtering.

**Base URL:** `http://localhost:8000/api`

**Authentication:** Tidak diperlukan (admin endpoint)

---

## Endpoints

### 1. Full Global Evaluation

**Route:** `GET /api/evaluation/knn/global`

**Description:** 
Evaluasi lengkap performa KNN dengan semua detail:
- Confusion matrix (TP, TN, FP, FN)
- Semua metrics (accuracy, precision, recall, specificity, f1)
- Label distribution (4-class dan binary)
- Medical interpretation

**Request:**
```bash
curl -X GET http://localhost:8000/api/evaluation/knn/global
```

**Response (Success):**
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
            "f1_score": 0.5097
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
    "interpretation": "🟢 Overall Performance: Excellent (Accuracy: 92.97%)...",
    "timestamp": "2024-11-20T10:30:00"
}
```

**Response (Error):**
```json
{
    "detail": "Error evaluating global KNN: ..."
}
```

**Use Cases:**
- Admin dashboard - full performance report
- Detailed analysis of model behavior
- Understanding confusion matrix & metrics
- Troubleshooting model performance issues

**Response Time:** ~2-5 seconds (depends on data volume)

---

### 2. Quick Summary

**Route:** `GET /api/evaluation/knn/global/summary`

**Description:**
Quick performance summary - hanya key metrics untuk dashboard indicator

**Request:**
```bash
curl -X GET http://localhost:8000/api/evaluation/knn/global/summary
```

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

**Performance Levels:**
```
"performance": "Excellent"  (Accuracy ≥ 85%)
"performance": "Good"       (Accuracy 75-85%)
"performance": "Fair"       (Accuracy 65-75%)
"performance": "Poor"       (Accuracy < 65%)
```

**Use Cases:**
- Admin dashboard - status indicator
- Mobile-friendly quick view
- Performance alerts
- Real-time monitoring

**Response Time:** ~2-5 seconds

---

### 3. Confusion Matrix Only

**Route:** `GET /api/evaluation/knn/global/confusion-matrix`

**Description:**
Hanya confusion matrix & metrics - optimal untuk visualization components

**Request:**
```bash
curl -X GET http://localhost:8000/api/evaluation/knn/global/confusion-matrix
```

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

**Use Cases:**
- Visualization: Confusion matrix heatmap
- Chart components: Bar chart, pie chart
- Comparing TP vs TN vs FP vs FN
- Educational purposes

**Response Time:** ~2-5 seconds

---

## Response Field Definitions

| Field | Type | Description |
|-------|------|---|
| `status` | string | "success" atau error message |
| `data` | object | Evaluation results |
| `interpretation` | string | Medical context explanation (endpoint 1 only) |
| `timestamp` | ISO8601 | Server timestamp |

### Data Object Fields

| Field | Type | Description |
|-------|------|---|
| `k` | int | K value used (always 5) |
| `n_total_samples` | int | Total pengukuran records evaluated |
| `confusion_matrix` | object | TP, TN, FP, FN counts |
| `metrics` | object | Accuracy, Precision, Recall, Specificity, F1-Score |
| `label_distribution` | object | Normal/Stunting true/predicted counts |
| `class_distribution_4class` | object | Classes 0-3 distribution |

### Metrics Details

```
Accuracy   = (TP + TN) / Total
Precision  = TP / (TP + FP)
Recall     = TP / (TP + FN)           ← MOST IMPORTANT in medical context
Specificity = TN / (TN + FP)
F1-Score   = 2 * (P * R) / (P + R)
```

---

## Frontend Integration Examples

### React - Display Full Results

```jsx
import React, { useEffect, useState } from 'react';

export function GlobalEvaluationPage() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('/api/evaluation/knn/global')
            .then(res => res.json())
            .then(data => {
                setData(data);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="loading">Loading...</div>;
    if (error) return <div className="error">Error: {error}</div>;
    if (!data) return <div>No data</div>;

    const result = data.data;
    const m = result.metrics;
    const cm = result.confusion_matrix;

    return (
        <div className="evaluation-container">
            <h1>🏥 Global Model Performance</h1>
            
            <div className="stats-grid">
                <StatCard 
                    title="Accuracy"
                    value={(m.accuracy * 100).toFixed(2) + '%'}
                    icon="📊"
                />
                <StatCard 
                    title="Recall (CRITICAL)"
                    value={(m.recall * 100).toFixed(2) + '%'}
                    icon="🎯"
                    warning={m.recall < 0.80}
                />
                <StatCard 
                    title="Precision"
                    value={(m.precision * 100).toFixed(2) + '%'}
                    icon="✅"
                />
                <StatCard 
                    title="Specificity"
                    value={(m.specificity * 100).toFixed(2) + '%'}
                    icon="✔️"
                />
            </div>

            <ConfusionMatrixDisplay cm={cm} />

            <InterpretationBox 
                content={data.interpretation}
            />
        </div>
    );
}

function StatCard({ title, value, icon, warning }) {
    return (
        <div className={`stat-card ${warning ? 'warning' : ''}`}>
            <h3>{icon} {title}</h3>
            <p className="value">{value}</p>
            {warning && <span className="red-badge">⚠️ Below threshold</span>}
        </div>
    );
}

function ConfusionMatrixDisplay({ cm }) {
    const total = cm.tp + cm.tn + cm.fp + cm.fn;
    return (
        <table className="confusion-matrix">
            <thead>
                <tr>
                    <th></th>
                    <th>Predicted: Normal</th>
                    <th>Predicted: Stunting</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Actual: Normal</strong></td>
                    <td className="tn">{cm.tn} (TN)</td>
                    <td className="fp">{cm.fp} (FP)</td>
                </tr>
                <tr>
                    <td><strong>Actual: Stunting</strong></td>
                    <td className="fn">{cm.fn} (FN) ⚠️</td>
                    <td className="tp">{cm.tp} (TP) ✓</td>
                </tr>
            </tbody>
        </table>
    );
}

function InterpretationBox({ content }) {
    return (
        <div className="interpretation-box">
            <h3>💡 Medical Interpretation</h3>
            <pre>{content}</pre>
        </div>
    );
}
```

### React - Summary Card Only

```jsx
export function PerformanceIndicator() {
    const [summary, setSummary] = useState(null);

    useEffect(() => {
        fetch('/api/evaluation/knn/global/summary')
            .then(res => res.json())
            .then(data => setSummary(data.data));
    }, []);

    if (!summary) return <div>Loading...</div>;

    const getColor = (perf) => {
        const colors = {
            'Excellent': '#10b981',
            'Good': '#f59e0b',
            'Fair': '#ef7f5f',
            'Poor': '#ef4444'
        };
        return colors[perf] || '#888';
    };

    return (
        <div 
            className="performance-card"
            style={{ borderColor: getColor(summary.performance) }}
        >
            <h3>🏥 Model Status</h3>
            <p className="performance" style={{ color: getColor(summary.performance) }}>
                {summary.performance}
            </p>
            <div className="metrics-mini">
                <span>Accuracy: {(summary.accuracy * 100).toFixed(1)}%</span>
                <span>Recall: {(summary.recall * 100).toFixed(1)}%</span>
            </div>
        </div>
    );
}
```

### Vue.js - Chart Component

```vue
<template>
    <div class="global-eval-chart">
        <h2>Model Performance Metrics</h2>
        <div ref="chartContainer" class="chart"></div>
    </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
    async mounted() {
        const response = await fetch('/api/evaluation/knn/global/summary');
        const data = await response.json();
        const metrics = data.data;

        const ctx = this.$refs.chartContainer.getContext('2d');
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Accuracy', 'Precision', 'Recall', 'Specificity', 'F1'],
                datasets: [{
                    label: 'Global KNN Performance',
                    data: [
                        metrics.accuracy,
                        metrics.precision,
                        metrics.recall,
                        metrics.specificity,
                        metrics.f1_score
                    ],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)'
                }]
            }
        });
    }
}
</script>
```

---

## Error Handling

### Network Error

```json
{
    "detail": "Error evaluating global KNN: Connection timeout"
}
```

**Response Code:** 500

**Solution:**
1. Check backend server is running
2. Check database connection
3. Verify table `pengukuran` exists

---

### No Data

```json
{
    "detail": "Error evaluating global KNN: Tidak ada data di tabel pengukuran"
}
```

**Response Code:** 500

**Solution:**
1. Verify `pengukuran` table has data
2. Check feature columns exist: jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala
3. Check status_gizi_label column exists

---

### Missing Values

```
✓ Data setelah cleaning: 1100 samples (dari 1234 total)
```

**Note:** Script automatically skips records dengan missing values

---

## Performance Considerations

| Metric | Value |
|--------|-------|
| Response Time | ~2-5 seconds |
| Data Volume | Scales with total `pengukuran` records |
| Caching | No caching (always fresh evaluation) |
| Concurrent Requests | Recommended: max 3 simultaneous |

**Optimization Tips:**
- Use `/summary` endpoint untuk quick checks
- Don't poll global evaluation more than once per hour
- Cache responses di frontend untuk repeated views

---

## Quick Reference

```bash
# Full evaluation - detailed results
GET /api/evaluation/knn/global

# Quick summary - for dashboard indicators
GET /api/evaluation/knn/global/summary

# Just confusion matrix - for charts
GET /api/evaluation/knn/global/confusion-matrix
```

---

## Related Endpoints

- K Parameter Evaluation: `/api/evaluation/k-parameter`
- Per-Kader Evaluation: `/api/evaluation/knn/kader/{user_id}`

---

## Documentation

- Full Guide: `KNN_GLOBAL_EVALUASI_USAGE_GUIDE.md`
- Quick Start: `KNN_GLOBAL_QUICK_START.md`
- Per-Kader API: `KNN_KADER_API_ENDPOINTS.md`
