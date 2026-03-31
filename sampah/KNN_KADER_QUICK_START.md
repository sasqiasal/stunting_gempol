# Quick Start: Evaluasi KNN per Kader

## Ringkasan

Fitur evaluasi KNN untuk mengevaluasi performa model KNN pada data kader tertentu:
- Filter berdasarkan `user_id` (kader)
- Filter berdasarkan bulan (opsional)
- Gunakan K=5 (nilai terbaik dari evaluasi sebelumnya)
- Hitung confusion matrix dan metrik dalam format binary (Normal vs Stunting)

---

## ⚡ Quick Start

### 1. Run Script Langsung

**Backend:**
```bash
cd backend
python -m app.ml.evaluate_knn_per_kader
```

Ini akan evaluate `user_id=1`, semua bulan.

### 2. Evaluate Spesifik Kader (Python Snippet)

```python
from app.ml.evaluate_knn_per_kader import KNNKaderEvaluator

evaluator = KNNKaderEvaluator(k=5)

# Semua bulan
result = evaluator.evaluate_kader(user_id=2)
evaluator.print_results(result)

# Bulan spesifik (Maret)
result = evaluator.evaluate_kader(user_id=2, month=3)
evaluator.print_results(result)
```

### 3. Via API Endpoint

**Semua bulan:**
```bash
curl http://localhost:8000/api/evaluation/knn/kader/2
```

**Bulan spesifik (Maret):**
```bash
curl http://localhost:8000/api/evaluation/knn/kader/2/month/3
```

**Batch semua bulan:**
```bash
curl -X POST http://localhost:8000/api/evaluation/knn/kader/2/evaluate-all-months
```

**Best month (by recall):**
```bash
curl "http://localhost:8000/api/evaluation/knn/kader/2/best-month?metric=recall"
```

---

## 📊 Output Contoh

### Console Output

```
Kader: user_id=2
Period: Semua Bulan/2024
Parameter: K=5
Total Samples: 42

📊 LABEL DISTRIBUTION:
  Actual:  Normal=28, Stunting=14
  Predicted: Normal=29, Stunting=13

🔲 CONFUSION MATRIX:
  TN=27, FP=1
  FN=1,  TP=13

📈 METRICS:
  ├─ Accuracy:    0.9524 (95.24%)
  ├─ Precision:   0.9286
  ├─ Recall:      0.9286
  ├─ Specificity: 0.9643
  └─ F1-Score:    0.9286

💡 Model performance: Excellent
✓ Recall tinggi: Model berhasil mendeteksi stunting
✓ Precision tinggi: Prediksi stunting cukup akurat
```

### API Response

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
  },
  "confusion_matrix": {
    "tp": 13, "tn": 27, "fp": 1, "fn": 1
  }
}
```

---

## 📁 Files

| File | Lokasi | Fungsi |
|------|--------|--------|
| `evaluate_knn_per_kader.py` | `backend/app/ml/` & `api/app/ml/` | Main logic |
| `knn_kader_evaluation.py` | `backend/app/routes/` | API endpoints |
| Usage Guide | `KNN_KADER_EVALUASI_USAGE_GUIDE.md` | Detailed docs |
| API Reference | `KNN_KADER_API_ENDPOINTS.md` | Endpoints docs |

---

## 🔧 Requirements

```bash
pip install numpy pandas scikit-learn
```

**Supabase Config** di `.env`:
```
SUPABASE_URL=your_url
SUPABASE_SERVICE_KEY=your_key
```

---

## 📈 Key Metrics

| Metric | Arti | Ideal |
|--------|------|-------|
| **Accuracy** | % prediksi benar | ≥85% |
| **Recall** | % stunting terdeteksi | ≥80% (crucial!) |
| **Precision** | % prediksi stunting akurat | ≥80% |
| **F1-Score** | Balance precision & recall | ≥0.80 |

> ⚠️ **Recall adalah yang paling penting** dalam medical context - hindari False Negative!

---

## 💡 Use Cases

### 1. Evaluate Kader Tertentu
```bash
curl http://localhost:8000/api/evaluation/knn/kader/3
```

### 2. Track Monthly Performance
```bash
curl http://localhost:8000/api/evaluation/knn/kader/3/month/6
```

### 3. Batch Analysis (Semua Bulan)
```bash
curl -X POST http://localhost:8000/api/evaluation/knn/kader/3/evaluate-all-months
```

### 4. Find Best Performance Month
```bash
curl "http://localhost:8000/api/evaluation/knn/kader/3/best-month?metric=recall"
```

---

## ✅ Checklist

- [x] Script untuk evaluasi per-kader ✓
- [x] Filter by `user_id` ✓
- [x] Filter by bulan (optional) ✓
- [x] Gunakan K=5 terbaik ✓
- [x] Hitung TP, TN, FP, FN ✓
- [x] Hitung semua metrik ✓
- [x] Tampilkan confusion matrix ✓
- [x] API endpoints ✓
- [x] Dokumentasi lengkap ✓

---

## Next Steps

1. **Register routes** di `app/main.py`:
   ```python
   from app.routes.knn_kader_evaluation import router
   app.include_router(router)
   ```

2. **Test endpoints**:
   ```bash
   curl http://localhost:8000/api/evaluation/knn/kader/1
   ```

3. **Integrate dengan frontend** untuk dashboard

4. **Monitor performance** per-kader secara periodik

---

## Dokumentasi Lengkap

- **Usage Guide:** `KNN_KADER_EVALUASI_USAGE_GUIDE.md`
- **API Reference:** `KNN_KADER_API_ENDPOINTS.md`
- **Database Schema:** `DATABASE_SCHEMA_AND_GROUND_TRUTH.md`

