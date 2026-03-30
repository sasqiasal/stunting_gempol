# RINGKASAN LENGKAP: Schema Database & Ground Truth untuk Confusion Matrix

## 📋 TABEL PENGUKURAN - Semua Kolom

### Input Features (6 Kolom)
| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| jenis_kelamin | VARCHAR | "L" atau "P" |
| usia_bulan | INTEGER | Usia dalam bulan (auto-calculated dari DOB) |
| tinggi_badan | FLOAT | cm (range: 40-120) |
| berat_badan | FLOAT | kg (range: 2-30) |
| lingkar_lengan | FLOAT | cm MUAC (range: 7-20) |
| lingkar_kepala | FLOAT | cm (range: 30-60) |

### Calculated/Stored Output (3 Kolom Penting)
| Kolom | Tipe | Deskripsi | Kegunaan |
|-------|------|-----------|----------|
| zscore_bbu | FLOAT | Z-Score Berat/Usia (WHO) | Untuk klasifikasi gizi |
| **zscore_tbu** | FLOAT | **Z-Score Tinggi/Usia (WHO)** | **→ GROUND TRUTH untuk Stunting** |
| status_gizi_label | INTEGER | 0-3 (class label dari KNN) | Prediksi model |
| prediksi_stunting | BOOLEAN | True jika label ∈ {2,3} | Legacy compatibility |
| confidence_score | FLOAT | 0.0-1.0 | Kepercayaan prediksi |

### Metadata Columns
| Kolom | Tipe |
|-------|------|
| id | INTEGER PK |
| balita_id | INTEGER FK |
| kader_id | INTEGER FK |
| tanggal_pengukuran | TIMESTAMP |
| catatan | TEXT |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

---

## 📋 TABEL EVALUASI_MODEL_KNN - Semua Kolom

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | INTEGER PK | Primary key |
| pengukuran_id | INTEGER FK | Foreign key ke pengukuran (one-to-one) |
| k_value | INTEGER | K yang digunakan dalam KNN (default: 5) |
| algorithm | VARCHAR | "KNN" |
| nearest_neighbors | JSONB | Array of K tetangga terdekat |
| created_at | TIMESTAMP | Auto |
| updated_at | TIMESTAMP | Auto |

### Struktur nearest_neighbors (JSONB Array)
```json
[
  {
    "index": 0,
    "distance": 0.45,
    "label": 2,
    "status_gizi": "Stunting + Gizi Baik",
    "zscore_bbu": -1.50,
    "zscore_tbu": -2.20,
    "jenis_kelamin": "L",
    "usia_bulan": 24
  },
  ...
]
```

---

## 🎯 GROUND TRUTH DEFINITION

### **Source: zscore_tbu < -2.0** (WHO Child Growth Standards)

**NOT:** actual_status, verified_status, status_aktual, atau sejenisnya

```
Mengapa tidak ada kolom "actual_status"?
✓ Ground truth adalah zscore_tbu yang dihitung otomatis
✓ Standar WHO adalah objektif, tidak perlu verifikasi manual
✓ Data entry dilakukan oleh kader terlatih
✓ Z-Score sudah cukup sebagai ground truth
```

### Conversion Binary Labels
```python
# Untuk Confusion Matrix (binary classification)
y_true = 1 if zscore_tbu < -2.0 else 0    # Ground Truth (Stunting vs Normal)
y_pred = 1 if status_gizi_label in (2,3) else 0  # Model Prediction
```

---

## 📊 CONFUSION MATRIX - BAGAIMANA SEHARUSNYA DIHITUNG

### Step-by-Step Calculation

```python
# 1. Extract data from table
from database import get_pengukuran_data

pengukuran_list = get_pengukuran_data()

# 2. Create arrays
y_true = []
y_pred = []

for record in pengukuran_list:
    # Ground truth dari Z-Score
    y_true.append(1 if float(record['zscore_tbu']) < -2.0 else 0)
    
    # Prediction dari model KNN
    y_pred.append(1 if int(record['status_gizi_label']) in (2, 3) else 0)

# 3. Calculate confusion matrix
tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)

# 4. Calculate metrics
accuracy = (tp + tn) / len(y_true)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"TP={tp}, TN={tn}, FP={fp}, FN={fn}")
print(f"Accuracy={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, F1={f1_score:.4f}")
```

### SQL Query Alternative
```sql
SELECT
  SUM(CASE WHEN zscore_tbu < -2.0 AND status_gizi_label IN (2,3) THEN 1 ELSE 0 END) as TP,
  SUM(CASE WHEN zscore_tbu >= -2.0 AND status_gizi_label NOT IN (2,3) THEN 1 ELSE 0 END) as TN,
  SUM(CASE WHEN zscore_tbu >= -2.0 AND status_gizi_label IN (2,3) THEN 1 ELSE 0 END) as FP,
  SUM(CASE WHEN zscore_tbu < -2.0 AND status_gizi_label NOT IN (2,3) THEN 1 ELSE 0 END) as FN
FROM pengukuran;
```

---

## 📌 TABEL PEMETAAN 4-CLASS LABELS

| Label | Kondisi | Z-Score TB/U | Z-Score BB/U | untuk CM |
|-------|---------|--------------|--------------|----------|
| 0 | Normal + Gizi Baik | ≥ -2.0 | ≥ -2.0 | Normal (0) |
| 1 | Normal + Kurang Gizi | ≥ -2.0 | < -2.0 | Normal (0) |
| 2 | **Stunting + Gizi Baik** | **< -2.0** | ≥ -2.0 | **Stunting (1)** |
| 3 | **Stunting + Kurang Gizi** | **< -2.0** | < -2.0 | **Stunting (1)** |

```
Binary Conversion:
  Labels {0, 1} → Normal      (y_pred = 0)
  Labels {2, 3} → Stunting    (y_pred = 1)
```

---

## ⚠️ PENTING: DATA LEAKAGE

### JANGAN PERNAH gunakan Z-Score sebagai Input Features!

```python
# ❌ SALAH (Data Leakage)
features = [jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, zscore_tbu, zscore_bbu]
model.train(features, labels)
# Model akan mempelajari ground truth langsung → 100% accuracy tapi tidak valid!

# ✓ BENAR (No Leakage)
features = [jenis_kelamin, usia_bulan, tinggi_badan, berat_badan, lingkar_lengan, lingkar_kepala]
y_true = [1 if zscore_tbu < -2 else 0]  # Hanya untuk evaluasi
model.train(features, labels)
cm = calculate_confusion_matrix(y_true, model.predict(features))  # Setelah training selesai!
```

---

## 📂 Referensi Files di Repository

### Untuk Ground Truth & Z-Score Calculation
- `api/app/utils/zscore_calculator.py` (lines 247-257)
  ```python
  def is_stunting(zscore_tbu: float) -> bool:
      return zscore_tbu < -2.0
  ```

### Untuk Confusion Matrix Calculation
- `api/app/ml/knn_manual.py`
  - `calculate_confusion_matrix(y_true, y_pred, labels)`
  - `calculate_metrics(y_true, y_pred, labels)`
  - `format_confusion_matrix_table(cm, labels)`

### Untuk Evaluasi Model
- `api/app/routes/evaluasi.py`
  - Endpoint: GET `/api/v1/evaluasi/model-performance`
  - Menghitung CM untuk K=3,5,7,9

### Untuk Create/Update Pengukuran
- `api/app/routes/pengukuran.py`
  - POST `/api/v1/pengukuran/` → buat & hitung zscore
  - PUT `/api/v1/pengukuran/{id}` → update & recalculate
  - Insert ke evaluasi_model_knn otomatis

---

## 🎓 Contoh Konkrit: Calculation Manual

### Dari 10 test samples:

```
ID | zscore_tbu | status_gizi_label | y_true | y_pred | Benar?
---+------------+-------------------+--------+--------+-------
1  | -2.5       | 2 (Stunting+Good)  | 1      | 1      | ✓ TP
2  | -1.8       | 0 (Normal+Good)    | 0      | 0      | ✓ TN
3  | -2.1       | 2 (Stunting+Good)  | 1      | 1      | ✓ TP
4  | 0.5        | 1 (Normal+Poor)    | 0      | 0      | ✓ TN
5  | -2.2       | 0 (Normal+Good)    | 1      | 0      | ✗ FN (missed!)
6  | -0.5       | 3 (Stunting+Poor)  | 0      | 1      | ✗ FP (wrong!)
7  | -2.3       | 3 (Stunting+Poor)  | 1      | 1      | ✓ TP
8  | 0.2        | 0 (Normal+Good)    | 0      | 0      | ✓ TN
9  | -1.9       | 1 (Normal+Poor)    | 0      | 0      | ✓ TN
10 | -2.0       | 2 (Stunting+Good)  | 0      | 1      | ✗ FP (wrong!)
```

### Hasil:
```
TP = 3 (correctly detected stunting)
TN = 5 (correctly detected normal)
FP = 2 (false alarms - said stunting when actually normal)
FN = 1 (missed stunting - DANGEROUS!)

Accuracy = (3+5)/10 = 80%
Precision = 3/(3+2) = 60% (when model says stunting, 60% right)
Recall = 3/(3+1) = 75% (caught 75% of actual stunting cases)
F1 = 2*(0.6*0.75)/(0.6+0.75) = 0.667

Catatan: FN=1 ini sangat kritis! Perlu improvement di recall.
```

---

## ✅ Checklist Implementasi Confusion Matrix

- [x] Data dari tabel pengukuran + evaluasi_model_knn
- [x] y_true = zscore_tbu < -2.0
- [x] y_pred = status_gizi_label IN (2,3)
- [x] Calculate TP, TN, FP, FN
- [x] Calculate metrics (Accuracy, Precision, Recall, F1)
- [x] Store atau return via API
- [x] Display di frontend
- [x] Dokumentasikan dengan penjelasan

---

## 📖 Dokumentasi Lengkap Lainnya

1. **DATABASE_SCHEMA_AND_GROUND_TRUTH.md** (comprehensive, 400+ lines)
2. **QUICK_SCHEMA_REFERENCE.md** (quick cheat sheet)
3. **CONFUSION_MATRIX_DIAGRAMS.md** (visual explanations & SQL examples)

---

Created: 2024-03-15
For: Stunting Gempol Project
Purpose: Understanding database schema and confusion matrix calculation
