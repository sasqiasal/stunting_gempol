# 📊 Evaluasi Model KNN dengan Confusion Matrix & Metrik Per Kelas

## Overview

Script `evaluate_knn_sklearn.py` menyediakan evaluasi lengkap untuk model K-Nearest Neighbors (KNN) dengan:
- ✅ **Confusion Matrix 4x4** - Menggunakan sklearn.metrics
- ✅ **TP, TN, FP, FN per Kelas** - Dengan pendekatan One-vs-Rest (OvR)
- ✅ **Metrik Evaluasi** - Precision, Recall, F1-Score, Specificity
- ✅ **Visualisasi Rapi** - Format tabel yang mudah dibaca

---

## Struktur Kode

### 1. **Confusion Matrix 4x4**

```python
from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2, 3])

# Hasil: matriks berukuran (4, 4)
#          Pred_Class_0  Pred_Class_1  Pred_Class_2  Pred_Class_3
# Actual_0      [CM]
# Actual_1      [CM]
# Actual_2      [CM]
# Actual_3      [CM]
```

**Penjelasan:**
- `cm[i, j]` = jumlah sampel dengan label aktual i yang diprediksi sebagai j
- `cm[i, i]` = diagonal = True Positive untuk kelas i

---

### 2. **Perhitungan One-vs-Rest (OvR)**

Untuk menghitung TP, TN, FP, FN per kelas:

```python
# Untuk kelas k (misalnya k=0):
# Positif = kelas 0, Negatif = kelas 1, 2, 3

TP = cm[k, k]              # Prediksi 0, Aktual 0
FP = cm[:, k].sum() - TP   # Semua yang diprediksi 0 - True Positive
FN = cm[k, :].sum() - TP   # Semua yang seharusnya 0 - True Positive
TN = cm.sum() - TP - FP - FN  # Sisanya
```

---

### 3. **Metrik Per Kelas**

Untuk setiap kelas:

```
Precision = TP / (TP + FP)      → Dari prediksi kelas i, berapa yang benar?
Recall    = TP / (TP + FN)      → Dari aktual kelas i, berapa yang berhasil diprediksi?
F1-Score  = 2 * (P * R) / (P + R) → Harmonic mean dari Precision dan Recall
Specificity = TN / (TN + FP)    → Kemampuan mengidentifikasi negatif dengan benar
```

---

## Penggunaan

### **Cara 1: Langsung Jalankan Script**

```bash
python evaluate_knn_sklearn.py
```

Output akan menampilkan:
- Confusion Matrix 4x4
- TP, TN, FP, FN per kelas
- Metrik detail (Precision, Recall, F1-Score)
- Classification Report

---

### **Cara 2: Import dalam Kode Python Anda**

```python
from evaluate_knn_sklearn import evaluate_knn_model, calculate_confusion_matrix_sklearn
import numpy as np

# Siapkan data
y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3, ...])  # Ground truth dari Z-Score
y_pred = np.array([0, 1, 2, 3, 0, 1, 1, 3, ...])  # Prediksi dari model KNN

# Jalankan evaluasi lengkap
cm, metrics_all = evaluate_knn_model(y_true, y_pred)
```

---

### **Cara 3: Integrasi dengan Model KNN di Project Anda**

```python
from api.app.ml.knn_sklearn import get_knn_model, StuntingKNNModel
from evaluate_knn_sklearn import evaluate_knn_model, calculate_confusion_matrix_sklearn
import numpy as np

# Load model
model = get_knn_model()

# Assume model sudah dilatih dengan X_train, y_train
# Sekarang eval dengan data test
X_test = np.array([...])  # Data test
y_test_true = np.array([...])  # Ground truth dari Z-Score

# Prediksi
y_pred = model.predict(X_test)[0]  # Ambil kelas saja, bukan confidence

# Evaluasi
cm, metrics_all = evaluate_knn_model(y_test_true, y_pred)
```

---

## Struktur Output

### **Confusion Matrix**

```
                         Pred_Class_0  Pred_Class_1  Pred_Class_2  Pred_Class_3
Actual_Class_0                  6            0             0              3
Actual_Class_1                  0            7             2              0
Actual_Class_2                  0            2             6              1
Actual_Class_3                  0            0             1              6
```

**Interpretasi:**
- Baris = Label Aktual
- Kolom = Label Prediksi
- Diagonal = Prediksi Benar

---

### **TP, TN, FP, FN Per Kelas (OvR)**

```
                              Kelas              TP  TN  FP  FN
0: Normal + Gizi Baik                             6  23   0   3
1: Normal + Kurang Gizi                           7  20   3   2
2: Stunting + Gizi Baik                           6  22   3   1
3: Stunting + Kurang Gizi                         6  24   1   1
```

**Penjelasan Baris Pertama (Kelas 0):**
- TP = 6 → Diprediksi 0 dan Aktual 0 (Benar)
- TN = 23 → Diprediksi bukan 0 dan Aktual bukan 0 (Benar)
- FP = 0 → Diprediksi 0 tapi Aktual bukan 0 (Salah prediksi positif)
- FN = 3 → Diprediksi bukan 0 tapi Aktual 0 (Salah prediksi negatif)

---

### **Metrik Per Kelas**

```
                             Kelas    Precision Recall F1-Score Specificity
0: Normal + Gizi Baik...          1.0000 0.6667   0.8000      1.0000
1: Normal + Kurang Gizi...        0.7000 0.7778   0.7368      0.8696
2: Stunting + Gizi Baik...        0.6667 0.8571   0.7500      0.8800
3: Stunting + Kurang Gi...        0.8571 0.8571   0.8571      0.9600

Overall Accuracy: 0.7812 (78.12%)
```

**Interpretasi Kelas 0:**
- Precision: 100% → Semua yang diprediksi kelas 0 adalah benar
- Recall: 66.67% → Hanya 2/3 sampel kelas 0 yang berhasil diprediksi
- F1-Score: 80% → Rata-rata harmonic dari precision dan recall

---

## 4 Kelas dalam Sistem

| Label | Nama |
|-------|------|
| 0 | Normal + Gizi Baik |
| 1 | Normal + Kurang Gizi |
| 2 | Stunting + Gizi Baik |
| 3 | Stunting + Kurang Gizi |

**Ground Truth dari Z-Score:**
- Zscore_TBU < -2.0 → Stunting (Label 2 atau 3)
- Zscore_BU < -2.0 → Kurang Gizi (Label 1 atau 3)
- Lainnya → Normal & Gizi Baik (Label 0)

---

## Fungsi-Fungsi Utama

### 1. `calculate_confusion_matrix_sklearn(y_true, y_pred)`
```python
cm = calculate_confusion_matrix_sklearn(y_true, y_pred)
# Return: numpy array (4, 4)
```

### 2. `calculate_ovr_metrics(cm, class_idx)`
```python
metrics = calculate_ovr_metrics(cm, 0)
# Return: {"TP": int, "TN": int, "FP": int, "FN": int}
```

### 3. `calculate_metrics_for_all_classes(cm)`
```python
metrics_all = calculate_metrics_for_all_classes(cm)
# Return: {0: {...}, 1: {...}, 2: {...}, 3: {...}}
```

### 4. `evaluate_knn_model(y_true, y_pred)` (Main Function)
```python
cm, metrics_all = evaluate_knn_model(y_true, y_pred)
# Print semua hasil evaluasi
# Return: cm (matrix), metrics_all (dict)
```

---

## Display Functions (Untuk Custom Output)

```python
# Tampilkan confusion matrix saja
print(display_confusion_matrix(cm))

# Tampilkan OvR metrics
print(display_ovr_metrics(metrics_all))

# Tampilkan classification report
print(display_detailed_metrics(y_true, y_pred, cm))

# Tampilkan perhitungan metrik per kelas
print(calculate_and_display_metrics_per_class(cm, metrics_all))
```

---

## Contoh Kasus: Evaluasi Model KNN Stunting

**Data:**
- 32 sampel data test
- 4 kelas klasifikasi
- Y_true dari Z-Score
- Y_pred dari Model KNN

**Output Hasil:**
```
CONFUSION MATRIX 4x4:
- Kelas 0 (Normal + Gizi Baik): 6/9 benar = 66.67%
- Kelas 1 (Normal + Kurang Gizi): 7/9 benar = 77.78%
- Kelas 2 (Stunting + Gizi Baik): 6/7 benar = 85.71%
- Kelas 3 (Stunting + Kurang Gizi): 6/7 benar = 85.71%

OVERALL ACCURACY: 78.12%

OvR METRICS:
- Kelas 0: TP=6, TN=23, FP=0, FN=3 (Precision=100%, Recall=66.67%)
- Kelas 1: TP=7, TN=20, FP=3, FN=2 (Precision=70%, Recall=77.78%)
- Kelas 2: TP=6, TN=22, FP=3, FN=1 (Precision=66.67%, Recall=85.71%)
- Kelas 3: TP=6, TN=24, FP=1, FN=1 (Precision=85.71%, Recall=85.71%)
```

---

## Tips & Trik

### 1. **Evaluasi dengan Data Real**
```python
# Load data dari database
y_true = get_ground_truth_from_zscore()
y_pred = get_predictions_from_knn()

# Evaluasi
cm, metrics = evaluate_knn_model(y_true, y_pred)
```

### 2. **Save Results ke File**
```python
import pickle

# Save confusion matrix
with open("confusion_matrix.pkl", "wb") as f:
    pickle.dump(cm, f)

# Save metrics
with open("metrics.pkl", "wb") as f:
    pickle.dump(metrics, f)
```

### 3. **Buat Custom Report**
```python
# Tambahkan di dalam kode
cm, metrics_all = evaluate_knn_model(y_true, y_pred)

# Custom processing
for class_idx in range(4):
    tp = metrics_all[class_idx]["TP"]
    recall = tp / (tp + metrics_all[class_idx]["FN"])
    print(f"Class {class_idx}: Recall = {recall:.2%}")
```

---

## Dependencies

Pastikan sudah install:
```bash
pip install numpy pandas scikit-learn
```

---

## File yang Berkaitan

- [evaluate_knn_sklearn.py](evaluate_knn_sklearn.py) - Script evaluasi utama
- [api/app/ml/knn_sklearn.py](api/app/ml/knn_sklearn.py) - Model KNN sklearn
- [QUICK_SCHEMA_REFERENCE.md](QUICK_SCHEMA_REFERENCE.md) - Schema database

---

## Next Steps

1. ✅ Test dengan contoh data (sudah dilakukan)
2. ⏳ Integrasikan dengan routes `/evaluasi` untuk endpoint evaluasi
3. ⏳ Buat dashboard untuk visualisasi confusion matrix
4. ⏳ Store results di database untuk tracking

---

**Created:** March 25, 2026
**Status:** Ready to use ✅
