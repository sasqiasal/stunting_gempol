# Database Schema & Ground Truth untuk Confusion Matrix

## 1. TABEL PENGUKURAN (pengukuran)

### Schema/Struktur Kolom

| Kolom | Tipe Data | Deskripsi | Catatan |
|-------|-----------|-----------|---------|
| **id** | INTEGER (PK) | Primary Key | Auto-increment |
| **balita_id** | INTEGER (FK) | Foreign Key ke tabel balita | Required |
| **kader_id** | INTEGER (FK) | Foreign Key ke tabel kader/users | User yang membuat pengukuran |
| **tanggal_pengukuran** | TIMESTAMP | Tanggal & waktu pelaksanaan pengukuran | Default: sekarang |
| **tinggi_badan** | FLOAT | Tinggi badan dalam cm | Range: 40-120 cm |
| **berat_badan** | FLOAT | Berat badan dalam kg | Range: 2-30 kg |
| **lingkar_lengan** | FLOAT | Lingkar lengan atas dalam cm (MUAC) | Range: 7-20 cm |
| **lingkar_kepala** | FLOAT | Lingkar kepala dalam cm | Range: 30-60 cm |
| **usia_bulan** | INTEGER | Usia balita dalam bulan saat pengukuran | Dihitung dari DOB |
| **jenis_kelamin** | VARCHAR | Jenis kelamin: "L" (Laki-laki) atau "P" (Perempuan) | Required |
| **zscore_bbu** | FLOAT | Z-Score Berat Badan/Usia | Dihitung dari WHO standard |
| **zscore_tbu** | FLOAT | Z-Score Tinggi Badan/Usia | **GROUND TRUTH untuk stunting** |
| **status_gizi** | VARCHAR | Status Gizi 4 Kelas | Contoh: "Normal + Gizi Baik" |
| **status_gizi_label** | INTEGER | Label numerik untuk status gizi 4 kelas | 0-3 (lihat tabel di bawah) |
| **prediksi_stunting** | BOOLEAN | Prediksi stunting (legacy, backward compat) | True jika label 2 atau 3 |
| **confidence_score** | FLOAT | Confidence score prediksi KNN | Range: 0.0-1.0 |
| **catatan** | TEXT | Catatan/keterangan pengukuran | Optional |
| **created_at** | TIMESTAMP | Waktu data dibuat di database | Auto |
| **updated_at** | TIMESTAMP | Waktu terakhir data diupdate | Auto |

### Pemetaan Status Gizi 4 Kelas

| Label | Nama Kelas | Kondisi | Dihitung Dari |
|-------|-----------|---------|---------------|
| **0** | Normal + Gizi Baik | zscore_tbu ≥ -2 AND zscore_bbu ≥ -2 | Tinggi normal, berat normal |
| **1** | Normal + Kurang Gizi | zscore_tbu ≥ -2 AND zscore_bbu < -2 | Tinggi normal, berat kurang |
| **2** | Stunting + Gizi Baik | zscore_tbu < -2 AND zscore_bbu ≥ -2 | Tinggi pendek, berat normal |
| **3** | Stunting + Kurang Gizi | zscore_tbu < -2 AND zscore_bbu < -2 | Tinggi pendek, berat kurang |

### Contoh Data

```json
{
  "id": 1,
  "balita_id": 5,
  "kader_id": 2,
  "tanggal_pengukuran": "2024-03-15T10:30:00",
  "tinggi_badan": 85.5,
  "berat_badan": 12.8,
  "lingkar_lengan": 14.2,
  "lingkar_kepala": 48.5,
  "usia_bulan": 24,
  "jenis_kelamin": "L",
  "zscore_bbu": -1.45,
  "zscore_tbu": -2.15,
  "status_gizi": "Stunting + Gizi Baik",
  "status_gizi_label": 2,
  "prediksi_stunting": true,
  "confidence_score": 0.92,
  "catatan": "Sehat, aktif bermain",
  "created_at": "2024-03-15T10:32:00",
  "updated_at": "2024-03-15T10:32:00"
}
```

---

## 2. TABEL EVALUASI_MODEL_KNN (evaluasi_model_knn)

### Schema/Struktur Kolom

| Kolom | Tipe Data | Deskripsi | Catatan |
|-------|-----------|-----------|---------|
| **id** | INTEGER (PK) | Primary Key | Auto-increment |
| **pengukuran_id** | INTEGER (FK) | Foreign Key ke tabel pengukuran | Unique per pengukuran |
| **k_value** | INTEGER | Nilai K yang digunakan dalam KNN | Default: 5 |
| **algorithm** | VARCHAR | Algoritma yang digunakan | Nilai: "KNN" |
| **nearest_neighbors** | JSONB/JSON | List of K nearest neighbors | Berisi data tetangga terdekat |
| **created_at** | TIMESTAMP | Waktu data dibuat | Auto |
| **updated_at** | TIMESTAMP | Waktu terakhir diupdate | Auto |

### Struktur nearest_neighbors (JSONB)

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
  {
    "index": 1,
    "distance": 0.52,
    "label": 2,
    "status_gizi": "Stunting + Gizi Baik",
    "zscore_bbu": -1.45,
    "zscore_tbu": -2.15,
    "jenis_kelamin": "L",
    "usia_bulan": 23
  },
  ...
]
```

### Contoh Data Evaluasi

```json
{
  "id": 1,
  "pengukuran_id": 1,
  "k_value": 5,
  "algorithm": "KNN",
  "nearest_neighbors": [
    {
      "index": 0,
      "distance": 0.45,
      "label": 2,
      "status_gizi": "Stunting + Gizi Baik"
    },
    ...
  ],
  "created_at": "2024-03-15T10:32:00",
  "updated_at": "2024-03-15T10:32:00"
}
```

---

## 3. GROUND TRUTH UNTUK EVALUASI MODEL

### Definisi Ground Truth

**Ground Truth = Label Sebenarnya berdasarkan Z-Score TB/U (Tinggi Badan/Usia)**

### Standar WHO untuk Stunting

```
Z-Score TB/U < -2.0  ➜ STUNTING (Pendek)
Z-Score TB/U ≥ -2.0  ➜ NORMAL (Tinggi Sesuai Usia)
```

### Implementasi di Kode

```python
# File: api/app/utils/zscore_calculator.py (line 247-257)
def is_stunting(zscore_tbu: float) -> bool:
    """
    Menentukan apakah balita mengalami stunting
    berdasarkan standar WHO
    """
    return zscore_tbu < -2.0
```

### Alasan Z-Score TB/U sebagai Ground Truth

1. **Standar Internasional**: WHO Child Growth Standards
2. **Objektif**: Tidak tergantung interpretasi subjektif
3. **Valid**: Terbukti secara medis dan epidemiologi
4. **Konsisten**: Sama di seluruh populasi

---

## 4. BAGAIMANA CONFUSION MATRIX DIHITUNG

### Definisi Confusion Matrix (Untuk 2 Kelas: Stunting vs Normal)

```
                    PREDIKSI
                 Normal  Stunting
ACTUAL  Normal      TN      FP
        Stunting    FN      TP
```

### Rumus Perhitungan

1. **True Positive (TP)**
   - Kondisi: `Ground Truth = Stunting AND Prediksi = Stunting`
   - Artinya: Model benar memprediksi stunting

2. **True Negative (TN)**
   - Kondisi: `Ground Truth = Normal AND Prediksi = Normal`
   - Artinya: Model benar memprediksi normal

3. **False Positive (FP)**
   - Kondisi: `Ground Truth = Normal AND Prediksi = Stunting`
   - Artinya: Model salah memprediksi stunting (positive bias)

4. **False Negative (FN)**
   - Kondisi: `Ground Truth = Stunting AND Prediksi = Normal`
   - Artinya: Model keliru tidak mendeteksi stunting (dangerous!)

### Pseudo Code Perhitungan

```python
def calculate_confusion_matrix(y_true, y_pred):
    """
    y_true: Ground truth labels dari zscore_tbu < -2
    y_pred: Prediksi dari model KNN
    """
    tp = sum((y_true == 1) & (y_pred == 1))  # Stunting dan diprediksi stunting
    tn = sum((y_true == 0) & (y_pred == 0))  # Normal dan diprediksi normal
    fp = sum((y_true == 0) & (y_pred == 1))  # Normal tapi diprediksi stunting
    fn = sum((y_true == 1) & (y_pred == 0))  # Stunting tapi diprediksi normal
    
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn}
```

### Ekstraksi Binary Labels dari Data 4-Kelas

```python
# Dari data pengukuran:
# 4-class labels: 0, 1, 2, 3

# Konversi ke binary:
y_true_binary = [1 if zscore_tbu < -2 else 0 for zscore_tbu in data]
y_pred_binary = [1 if label in [2, 3] else 0 for label in predicted_labels]
# Label 2, 3 = Stunting (baik atau kurang gizi)
# Label 0, 1 = Normal   (baik atau kurang gizi)
```

---

## 5. CONTOH PERHITUNGAN CONFUSION MATRIX

### Data Testing (Contoh)

```
ID | zscore_tbu | Actual Status | Predicted Label | Pred Status | Ground Truth | Prediction
1  | -2.5       | Stunting      | 2              | Stunting    | 1           | 1
2  | -1.8       | Normal        | 0              | Normal      | 0           | 0
3  | -2.1       | Stunting      | 2              | Stunting    | 1           | 1
4  | 0.5        | Normal        | 1              | Normal      | 0           | 0
5  | -2.2       | Stunting      | 0              | Normal      | 1           | 0  ← FN!
6  | -0.5       | Normal        | 3              | Stunting    | 0           | 1  ← FP!
...
```

### Hasil Perhitungan

```
TP (True Positive)  = 50  (Benar prediksi Stunting)
TN (True Negative)  = 250 (Benar prediksi Normal)
FP (False Positive) = 5   (Salah prediksi Stunting)
FN (False Negative) = 2   (Salah tidak prediksi Stunting)

Confusion Matrix:
              Prediksi
           Normal  Stunting
Actual Normal 250      5
       Stunting  2     50
```

### Metrik Performa

```
Accuracy  = (TP + TN) / Total = (50 + 250) / 307 = 0.976 (97.6%)
Precision = TP / (TP + FP)    = 50 / 55         = 0.909 (90.9%)
Recall    = TP / (TP + FN)    = 50 / 52         = 0.962 (96.2%)
F1-Score  = 2 * (Precision * Recall) / (Precision + Recall) = 0.935
```

---

## 6. TIDAK ADA KOLOM "actual_status" ATAU "verified_status"

### Catatan Penting

**Pengamatan dari kode:**
- ❌ **TIDAK ada kolom**: `actual_status`, `verified_status`, `status_aktual`
- ✅ **Yang ada**: `zscore_tbu` sebagai ground truth

### Mengapa?

1. **Z-Score sudah cukup**: Standar WHO adalah objektif
2. **Tidak perlu manual verification**: Z-Score dihitung dari anthropometry
3. **Kualitas data dijamin**: Kader terlatih melakukan pengukuran

### Proses Pengisian Ground Truth

```
1. Kader mengukur: tinggi badan, berat badan, lingkar lengan, lingkar kepala
   ↓
2. Sistem hitung: Z-Score berdasarkan WHO standards
   ↓
3. Ground Truth otomatis = zscore_tbu < -2.0
   ↓
4. Model KNN melakukan prediksi
   ↓
5. Bandingkan: Ground Truth vs Prediksi
```

---

## 7. RINGKASAN KOLOM YANG DIGUNAKAN

### UNTUK FITUR/INPUT MODEL KNN

```
✓ jenis_kelamin    (encoded: 0=P, 1=L)
✓ usia_bulan       (numeric)
✓ tinggi_badan     (numeric)
✓ berat_badan      (numeric)
✓ lingkar_lengan   (numeric)
✓ lingkar_kepala   (numeric)
```

### UNTUK GROUND TRUTH (Y TRUE)

```
✓ zscore_tbu (< -2.0 = Stunting, >= -2.0 = Normal)
atau
✓ status_gizi_label (Labels 2,3 = Stunting, 0,1 = Normal)
```

### UNTUK PREDIKSI (Y PRED)

```
✓ status_gizi_label dari model KNN (0-3)
atau
✓ prediksi_stunting (binary untuk backward compat)
```

### UNTUK EVALUASI DETAIL

```
✓ nearest_neighbors (dari tabel evaluasi_model_knn)
  - Menunjukkan K neighbors terdekat
  - Digunakan untuk explainability
```

---

## 8. DATA LEAKAGE - PENTING!

### ⚠️ PERINGATAN

**Z-Score TIDAK BOLEH digunakan sebagai fitur input model KNN!**

### Alasan

```
Fitur Input: tinggi_badan, berat_badan, dll
       ↓
Model KNN → Prediksi status_gizi_label
       ↓
Ground Truth: zscore_tbu < -2 → Stunting
```

Jika Z-Score digunakan sebagai fitur:
- Model belajar langsung dari ground truth
- Membuat model overfitting 100%
- Tidak valid untuk evaluasi
- Disebut "DATA LEAKAGE"

### Implementasi yang Benar

```python
# File: api/app/routes/evaluasi.py (line 80)
"note": "Z-score TIDAK digunakan sebagai fitur (hanya untuk ground truth)"

# File: api/app/ml/knn_model.py (line 92)
"zscore_tbu: Tidak dipakai sebagai fitur (data leakage; digunakan hanya untuk ground truth)"
```

---

## 9. DOKUMENTASI REFERENSI

### File-File Penting

1. **Model Definition**: `api/app/ml/knn_model.py`
2. **Z-Score Calculator**: `api/app/utils/zscore_calculator.py`
3. **Prediction Service**: `api/app/services/prediction_service.py`
4. **Evaluation Routes**: `api/app/routes/evaluasi.py`
5. **Pengukuran Routes**: `api/app/routes/pengukuran.py`

### Query SQL untuk Debugging

```sql
-- Lihat sample confusion matrix
SELECT 
  id,
  zscore_tbu < -2.0 as actual_stunting,
  status_gizi_label in (2,3) as predicted_stunting,
  status_gizi,
  created_at
FROM pengukuran
LIMIT 20;

-- Hitung confusion matrix manual
WITH data AS (
  SELECT 
    CASE WHEN zscore_tbu < -2.0 THEN 1 ELSE 0 END as y_true,
    CASE WHEN status_gizi_label in (2,3) THEN 1 ELSE 0 END as y_pred
  FROM pengukuran
)
SELECT
  SUM(CASE WHEN y_true = 1 AND y_pred = 1 THEN 1 ELSE 0 END) as tp,
  SUM(CASE WHEN y_true = 0 AND y_pred = 0 THEN 1 ELSE 0 END) as tn,
  SUM(CASE WHEN y_true = 0 AND y_pred = 1 THEN 1 ELSE 0 END) as fp,
  SUM(CASE WHEN y_true = 1 AND y_pred = 0 THEN 1 ELSE 0 END) as fn
FROM data;
```

---

## 10. CHECKLIST UNTUK IMPLEMENTASI CONFUSION MATRIX

- [ ] Extract `zscore_tbu` dari tabel pengukuran (ground truth)
- [ ] Extract `status_gizi_label` dari tabel pengukuran (prediction)
- [ ] Convert keduanya ke binary (Stunting=1, Normal=0)
- [ ] Hitung TP, TN, FP, FN dengan loop atau SQL
- [ ] Hitung Accuracy = (TP+TN) / Total
- [ ] Hitung Precision = TP / (TP+FP)
- [ ] Hitung Recall = TP / (TP+FN)
- [ ] Hitung Specificity = TN / (TN+FP)
- [ ] Hitung F1-Score = 2 * (P*R) / (P+R)
- [ ] Validate bahwa nilai masuk akal
- [ ] Store di database atau response API
- [ ] Display di frontend dengan format table
