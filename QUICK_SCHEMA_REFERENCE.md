# Quick Reference - Schema & Confusion Matrix

## Tabel PENGUKURAN - Kolom Penting

```
INPUT FITUR (6 kolom):
  jenis_kelamin → encoded: L=1, P=0
  usia_bulan
  tinggi_badan (cm)
  berat_badan (kg)
  lingkar_lengan (cm)
  lingkar_kepala (cm)

OUTPUT/CALCULATED (3 kolom):
  zscore_bbu → Z-Score Berat/Usia (WHO standard)
  zscore_tbu → Z-Score Tinggi/Usia (used as GROUND TRUTH)
  status_gizi_label → 0=Normal+Baik, 1=Normal+Kurang, 2=Stunting+Baik, 3=Stunting+Kurang

METADATA:
  id, balita_id, kader_id, tanggal_pengukuran, catatan
  created_at, updated_at
```

---

## Tabel EVALUASI_MODEL_KNN - Kolom

```
id → primary key
pengukuran_id → FK to pengukuran (one-to-one)
k_value → K used (default: 5)
algorithm → "KNN"
nearest_neighbors → JSONB array of K nearest points
  {index, distance, label, status_gizi, zscore_tbu, zscore_bbu, ...}
created_at, updated_at
```

---

## GROUND TRUTH = zscore_tbu < -2.0

Standar WHO:
```
zscore_tbu < -2.0   →  STUNTING   (y_true = 1)
zscore_tbu >= -2.0  →  NORMAL     (y_true = 0)
```

---

## Confusion Matrix Calculation

```
y_true = [1 if zscore_tbu < -2.0 else 0 for each record]
y_pred = [1 if status_gizi_label in (2,3) else 0 for each record]

TP = count(y_true==1 AND y_pred==1)
TN = count(y_true==0 AND y_pred==0)
FP = count(y_true==0 AND y_pred==1)
FN = count(y_true==1 AND y_pred==0)

Metrics:
  Accuracy  = (TP + TN) / (TP + TN + FP + FN)
  Precision = TP / (TP + FP)
  Recall    = TP / (TP + FN)
  F1-Score  = 2 * (Precision * Recall) / (Precision + Recall)
```

---

## IMPORTANT: NO "actual_status" column exists

✓ Ground truth from zscore_tbu (automatic, no manual field)
✗ NO kolom: actual_status, verified_status, status_aktual, true_label, actual_label

---

## ⚠️ NO DATA LEAKAGE

Z-Score must NOT be used as input feature!
```
✗ Features: zscore_tbu    (WRONG - data leakage)
✓ Features: tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala, usia_bulan, jenis_kelamin (CORRECT)
✓ Ground Truth: zscore_tbu only (for evaluation)
```

---

## Example Query to Calculate CM

```sql
WITH binary_data AS (
  SELECT 
    CASE WHEN zscore_tbu < -2 THEN 1 ELSE 0 END as y_true,
    CASE WHEN status_gizi_label IN (2,3) THEN 1 ELSE 0 END as y_pred
  FROM pengukuran
)
SELECT
  SUM(CASE WHEN y_true=1 AND y_pred=1 THEN 1 ELSE 0 END) as TP,
  SUM(CASE WHEN y_true=0 AND y_pred=0 THEN 1 ELSE 0 END) as TN,
  SUM(CASE WHEN y_true=0 AND y_pred=1 THEN 1 ELSE 0 END) as FP,
  SUM(CASE WHEN y_true=1 AND y_pred=0 THEN 1 ELSE 0 END) as FN
FROM binary_data;
```

Result example:
```
TP=50, TN=250, FP=5, FN=2
Accuracy = (50+250)/307 = 97.6%
```
