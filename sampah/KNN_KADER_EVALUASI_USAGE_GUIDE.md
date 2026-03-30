# Evaluasi Model KNN per Kader - Usage Guide

## Deskripsi

Script evaluasi KNN untuk mengevaluasi performa model KNN pada data pengukuran dari kader tertentu.

**Fitur:**
- Filter data berdasarkan `user_id` (kader)
- Filter berdasarkan bulan (opsional)
- Gunakan K=5 (nilai terbaik dari evaluasi sebelumnya)
- Hitung confusion matrix dan metrik dalam format binary (Normal vs Stunting)

**Status Ground Truth:**
- `status_aktual` = `status_gizi_label` (0-3 kelas)
- Binary conversion:
  - Label 0, 1 → Normal (0)
  - Label 2, 3 → Stunting (1)

---

## Cara Menggunakan

### 1. Run Script Langsung (Python)

**Backend:**

```bash
cd d:\development\stunting_gempol\backend
python -m app.ml.evaluate_knn_per_kader
```

Ini akan evaluate data untuk `user_id=1` dengan semua bulan.

**API:**

```bash
cd d:\development\stunting_gempol\api
python -m app.ml.evaluate_knn_per_kader
```

### 2. Evaluate Spesifik Kader (Custom Script)

Buat file `test_kader_evaluation.py`:

```python
from app.ml.evaluate_knn_per_kader import KNNKaderEvaluator

# Initialize evaluator dengan K=5
evaluator = KNNKaderEvaluator(k=5)

# Evaluate kader dengan user_id=2, semua bulan tahun 2024
result = evaluator.evaluate_kader(user_id=2, month=None, year=2024)

# Print hasil
evaluator.print_results(result)

# Print interpretasi
print("\n💡 INTERPRETASI:")
print(evaluator.get_interpretation(result))
```

Jalankan:

```bash
python test_kader_evaluation.py
```

### 3. Evaluate Spesifik Bulan

```python
from app.ml.evaluate_knn_per_kader import KNNKaderEvaluator

evaluator = KNNKaderEvaluator(k=5)

# Evaluate kader dengan user_id=2, Maret 2024 saja
result = evaluator.evaluate_kader(user_id=2, month=3, year=2024)

evaluator.print_results(result)
```

### 4. Via HTTP API (FastAPI)

**Evaluate Semua Bulan:**

```bash
curl http://localhost:8000/api/evaluation/knn/kader/2
```

**Evaluate Bulan Spesifik:**

```bash
curl "http://localhost:8000/api/evaluation/knn/kader/2/month/3"
```

**Evaluate Semua Bulan (Batch):**

```bash
curl -X POST http://localhost:8000/api/evaluation/knn/kader/2/evaluate-all-months
```

**Get Summary:**

```bash
curl http://localhost:8000/api/evaluation/knn/kader/2/summary
```

**Get Best Month (berdasarkan accuracy):**

```bash
curl "http://localhost:8000/api/evaluation/knn/kader/2/best-month?metric=accuracy"
```

---

## Output

### 1. Console Output

Ketika menjalankan script, akan menampilkan:

```
================================================================================
EVALUASI KNN UNTUK KADER (user_id=2, K=5)
================================================================================

📊 Step 1: Fetch data training (semua data)...
✓ Fetch semua data: 1234 records
✓ Data setelah cleaning: 1200 samples

🔧 Step 2: Prepare KNN model...
✓ Model KNN (K=5) sudah trained dengan 1200 samples

📊 Step 3: Fetch data kader (user_id=2)...
✓ Fetch data kader_id=2: 45 records
✓ Data kader setelah cleaning: 42 samples

🎯 Step 4: Make predictions...

📈 Step 5: Calculate confusion matrix...

====================================================================================================
HASIL EVALUASI KNN PER KADER
====================================================================================================

Kader: user_id=2
Period: Semua Bulan/2024
Parameter: K=5
Total Samples: 42

📊 LABEL DISTRIBUTION:
  Actual:  Normal=28, Stunting=14
  Predicted: Normal=29, Stunting=13

🔲 CONFUSION MATRIX:
  ┌─────────────────────────────────────────┐
  │              Predicted                  │
  │      Normal (0)    │    Stunting (1)    │
  ├─────────────────────────────────────────┤
  │ Actual   Normal (0)│  TN=  27  │  FP=   1    │
  │ Stunting (1)│  FN=   1  │  TP=  13    │
  └─────────────────────────────────────────┘

📈 METRICS:
  ├─ Accuracy:    0.9524 (95.24%)
  ├─ Precision:   0.9286 (dari 14 predicted positive)
  ├─ Recall:      0.9286 (deteksi dari 14 actual positive)
  ├─ Specificity: 0.9643 (deteksi dari 28 actual negative)
  └─ F1-Score:    0.9286

====================================================================================================

💡 INTERPRETASI:
Model performance: Excellent (Accuracy: 95.24%)
✓ Recall tinggi: Model berhasil mendeteksi stunting dengan baik
✓ Precision tinggi: Prediksi stunting cukup akurat
```

### 2. API JSON Response

**GET /api/evaluation/knn/kader/2:**

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
  "interpretation": "Model performance: Excellent (Accuracy: 95.24%)\n✓ Recall tinggi: Model berhasil mendeteksi stunting dengan baik\n✓ Precision tinggi: Prediksi stunting cukup akurat"
}
```

---

## Interpretasi Metrik

| Metrik | Rumus | Arti |
|--------|-------|------|
| **Accuracy** | (TP + TN) / Total | Seberapa akurat model overall (% prediksi benar) |
| **Precision** | TP / (TP + FP) | Dari prediksi stunting, berapa % yang benar (reliability) |
| **Recall** | TP / (TP + FN) | Dari actual stunting, berapa % yang terdeteksi (coverage) |
| **Specificity** | TN / (TN + FP) | Dari actual normal, berapa % yang terdeteksi dengan benar |
| **F1-Score** | 2 * (Precision * Recall) / (P + R) | Kombinasi precision dan recall (harmonic mean) |

### Performance Levels (berdasarkan Accuracy)

- **Excellent** (≥85%): Model sangat baik
- **Good** (75-85%): Model cukup baik
- **Fair** (65-75%): Model lumayan
- **Poor** (<65%): Model perlu improvement

### Penting untuk Medical Context

Di bidang medis/kesehatan, **Recall** adalah metrik paling penting karena:
- **High Recall**: Mengurangi False Negative (stunting yang terlewat) → operasional baik
- **Low Recall**: Banyak False Negative → anak stunting tidak terdeteksi → bad outcome

---

## Confusion Matrix Explanation

```
                 PREDICTED
                Normal  Stunting
         Normal   TN      FP      ← Actual Normal
ACTUAL   Stunting FN      TP      ← Actual Stunting

TN = True Negative   (benar prediksi Normal, actual Normal) ✓
TP = True Positive   (benar prediksi Stunting, actual Stunting) ✓
FN = False Negative  (salah prediksi Normal, actual Stunting) ❌ PENTING!
FP = False Positive  (salah prediksi Stunting, actual Normal) ⚠
```

**Dalam konteks stunting detection:**
- **TP tinggi** = Anak stunting terdeteksi (good)
- **FN tinggi** = Anak stunting tidak terdeteksi (bad, perlu perhatian)
- **FP sedang** = False alarm (minor issue)

---

## Batch Evaluation (Semua Bulan Sekaligus)

Untuk evaluate kader di semua bulan dan dapatkan summary:

```python
from app.ml.evaluate_knn_per_kader import KNNKaderEvaluator

evaluator = KNNKaderEvaluator(k=5)

# Evaluate per-bulan
print("Evaluasi per-bulan untuk kader_id=2:")
for month in range(1, 13):
    try:
        result = evaluator.evaluate_kader(user_id=2, month=month, year=2024)
        m = result['metrics']
        print(f"\nBulan {month:2d}: Acc={m['accuracy']:.4f}, Recall={m['recall']:.4f}, F1={m['f1_score']:.4f}, N={result['n_samples']}")
    except ValueError as e:
        print(f"\nBulan {month:2d}: No data")
```

Atau via API:

```bash
curl -X POST http://localhost:8000/api/evaluation/knn/kader/2/evaluate-all-months
```

Response:

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
      "metrics": {...}
    },
    ...
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

---

## Troubleshooting

### Error: "Tidak ada data untuk kader_id=X"

**Penyebab:** User ID tidak ada atau tidak punya data pengukuran

**Solusi:**
1. Cek apakah `user_id` valid di database
2. Cek apakah ada data di tabel `pengukuran` dengan `kader_id=X`

```sql
SELECT COUNT(*) FROM pengukuran WHERE kader_id = 2;
```

### Error: "Tidak ada data untuk bulan=X"

**Penyebab:** Kader tidak punya pengukuran di bulan tersebut

**Solusi:** Gunakan `month=None` untuk evaluate semua bulan

### Error: "Tidak ada data di tabel pengukuran"

**Penyebab:** Tabel kosong atau tidak ada data yang valid

**Solusi:**
1. Cek koneksi Supabase
2. Cek apakah ada data di tabel `pengukuran`

```sql
SELECT COUNT(*) FROM pengukuran;
```

---

## File Lokasi

| File | Lokasi | Fungsi |
|------|--------|---------|
| `evaluate_knn_per_kader.py` | `backend/app/ml/` & `api/app/ml/` | Main logic |
| `knn_kader_evaluation.py` | `backend/app/routes/` | API endpoints |
| Dokumentasi ini | Root workspace | Usage guide |

---

## Konfigurasi & Requirements

### Environment Variables

Pastikan `.env` sudah dikonfigurasi:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

### Packages Required

```bash
pip install numpy pandas scikit-learn
```

### Database Requirements

Tabel `pengukuran` harus memiliki kolom:
- `kader_id` (INTEGER) - FK to users
- `jenis_kelamin` (VARCHAR: "L" or "P")
- `usia_bulan` (INTEGER)
- `tinggi_badan` (FLOAT)
- `berat_badan` (FLOAT)
- `lingkar_lengan` (FLOAT)
- `lingkar_kepala` (FLOAT)
- `status_gizi_label` (INTEGER: 0-3)
- `tanggal_pengukuran` (TIMESTAMP)

---

## Tips & Best Practices

1. **Gunakan K=5** untuk production (sudah teruji dengan evaluasi sebelumnya)

2. **Evaluasi per-bulan** untuk trend analysis kader

3. **Monitor Recall** - penting untuk medical context

4. **Batch evaluate semua bulan** untuk dashboard insights

5. **Benchmark dengan global model** - bandingkan per-kader dengan overall performance

---

## Referensi

- [Confusion Matrix & Metrics](https://en.wikipedia.org/wiki/Confusion_matrix)
- [Sensitivity, Specificity, Precision, Recall (Medical Context)](https://en.wikipedia.org/wiki/Sensitivity_and_specificity)
- [Scikit-Learn KNN](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html)
- [Database Schema](DATABASE_SCHEMA_AND_GROUND_TRUTH.md)

