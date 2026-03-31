# Evaluasi Parameter K pada KNN

## Deskripsi

Script ini membandingkan nilai K (3, 5, 7, 9) pada algoritma KNN menggunakan data dari Supabase.

**Fitur yang digunakan:**
- jenis_kelamin (encoded: L=1, P=0)
- usia_bulan
- tinggi_badan
- berat_badan
- lingkar_lengan
- lingkar_kepala

**Label (Ground Truth):**
- status_gizi_label (0-3 kelas, 4-class classification)
  - 0: Normal & Gizi Baik
  - 1: Normal & Kurang Gizi
  - 2: Stunting & Gizi Baik
  - 3: Stunting & Kurang Gizi

**Metrik yang dihitung:**
- Accuracy = (TP + TN) / Total
- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- Specificity = TN / (TN + FP)
- F1-Score = 2 × (Precision × Recall) / (Precision + Recall)

**Cara Perhitungan:**
- Untuk 4-class classification, menggunakan pendekatan One-vs-Rest per class
- Metrik kemudian di-aggregate dengan macro-average

---

## Cara Menggunakan

### 1. Backend (Python)

**Di folder backend:**

```bash
cd d:\development\stunting_gempol\backend
python -m app.ml.evaluate_k_parameter
```

Atau jika sudah ada virtual environment:

```bash
# Dengan venv/conda yang sudah aktif
python -m app.ml.evaluate_k_parameter
```

### 2. API (FastAPI)

**Di folder api:**

```bash
cd d:\development\stunting_gempol\api
python -m app.ml.evaluate_k_parameter
```

---

## Output yang Diharapkan

### 1. Summary Table

Perbandingan metrik antar nilai K:

```
===============================================================================================================
                      TABEL PERBANDINGAN PARAMETER K
===============================================================================================================
  K  Overall Acc  Macro Acc  Macro Prec  Macro Rec  Macro Spec  Macro F1
  3      0.7234      0.6145      0.6234      0.5892      0.8145      0.6012
  5      0.7456      0.6423      0.6512      0.6234      0.8234      0.6367
  7      0.7389      0.6234      0.6345      0.6089      0.8012      0.6215
  9      0.7234      0.6012      0.6123      0.5945      0.7945      0.6023
===============================================================================================================
```

### 2. Detail Metrik per Class

Untuk setiap K, menampilkan metrik untuk setiap class:

```
============================================================
K = 5
============================================================

  Class 0: Normal & Gizi Baik (0)
  ├─ TP= 345 | TN=2456 | FP= 123 | FN= 234
  ├─ Accuracy:   0.8923
  ├─ Precision:  0.7372
  ├─ Recall:     0.5950
  ├─ Specificity: 0.9525
  └─ F1-Score:   0.6572

  Class 1: Normal & Kurang Gizi (1)
  ├─ TP= 123 | TN=2678 | FP=  89 | FN= 110
  ├─ Accuracy:   0.9456
  ├─ Precision:  0.5803
  ├─ Recall:     0.5275
  ├─ Specificity: 0.9679
  └─ F1-Score:   0.5527
  ...
```

### 3. Rekomendasi K Terbaik

Ditentukan berdasarkan **Overall Accuracy tertinggi**:

```
================================================================
✓ K TERBAIK: 5 (Overall Accuracy: 0.7456)
================================================================
```

---

## Interpretasi Hasil

### Memilih K Terbaik

1. **Lihat Overall Accuracy**: K dengan accuracy tertinggi adalah rekomendasi utama
2. **Balance Precision & Recall**: Untuk kasus medis, Recall lebih penting (mencegah false negative)
3. **Cek per-class metrics**: Lihat performa untuk class majority vs minority

### Tips Interpretasi

- **High Precision, Low Recall**: Model terlalu konservatif (banyak False Negative)
- **Low Precision, High Recall**: Model terlalu aggressive (banyak False Positive)
- **Balanced**: Precision dan Recall keduanya tinggi (F1-Score tinggi)

### Contoh Interpretasi

Jika K=5 memberikan:
- Overall Accuracy: 74.56%
- Macro Recall: 62.34% (rata-rata recall semua class)
- Macro F1: 63.67%

Artinya model K=5 mampu mengidentifikasi:
- 74% dari semua kasus dengan benar
- Rata-rata 62% positive cases terdeteksi (recall)

---

## Prasyarat

### Packages Required

```bash
numpy
pandas
scikit-learn
supabase   # untuk fetch data dari Supabase
```

Install jika belum ada:

```bash
pip install numpy pandas scikit-learn supabase-py
```

### Environment Variables

Pastikan `.env` sudah dikonfigurasi dengan:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

### Database

Tabel `pengukuran` di Supabase harus memiliki kolom:
- jenis_kelamin (VARCHAR: "L" or "P")
- usia_bulan (INTEGER)
- tinggi_badan (FLOAT)
- berat_badan (FLOAT)
- lingkar_lengan (FLOAT)
- lingkar_kepala (FLOAT)
- status_gizi_label (INTEGER: 0-3)

---

## File Lokasi

**Backend:**
- `backend/app/ml/evaluate_k_parameter.py`

**API:**
- `api/app/ml/evaluate_k_parameter.py`

---

## Modifikasi (Opsional)

Jika ingin mengubah K values yang dibandingkan:

Buka file `evaluate_k_parameter.py`, cari:

```python
def __init__(self):
    self.k_values = [3, 5, 7, 9]  # <-- Ubah di sini
```

Contoh, untuk membandingkan K=3,5,7,9,11,13:

```python
self.k_values = [3, 5, 7, 9, 11, 13]
```

---

## Troubleshooting

### Error: "Module app.database not found"

Pastikan menjalankan dari folder yang benar:

```bash
# ✓ Benar
cd d:\development\stunting_gempol\backend
python -m app.ml.evaluate_k_parameter

# ✗ Salah
cd d:\development\stunting_gempol\backend\app\ml
python evaluate_k_parameter.py
```

### Error: "Tidak ada data di tabel pengukuran"

1. Cek apakah tabel `pengukuran` ada di Supabase
2. Cek apakah ada data di tabel tersebut
3. Cek koneksi Supabase (SUPABASE_URL, SUPABASE_SERVICE_KEY)

### Error: "All data have missing values"

Data memiliki NULL/None di kolom-kolom fitur. Cek:

```sql
SELECT * FROM pengukuran 
WHERE jenis_kelamin IS NULL 
   OR usia_bulan IS NULL
   OR tinggi_badan IS NULL
   OR status_gizi_label IS NULL;
```

---

## Sharing Hasil

Hasil evaluasi ditampilkan di terminal. Untuk save ke file:

```bash
# Linux/Mac
python -m app.ml.evaluate_k_parameter > evaluation_results.txt

# Windows PowerShell
python -m app.ml.evaluate_k_parameter | Out-File evaluation_results.txt
```

---

## Referensi

- [Scikit-Learn KNeighborsClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html)
- [Confusion Matrix & Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html)
- Database Schema: `DATABASE_SCHEMA_AND_GROUND_TRUTH.md`

