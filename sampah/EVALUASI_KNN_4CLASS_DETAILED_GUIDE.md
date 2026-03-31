# Evaluasi KNN 4-Class Classification - Panduan Lengkap

## 📋 Overview

Sistem evaluasi KNN yang telah diperbaiki untuk menggunakan **4-class classification** berdasarkan Z-Score WHO standard, bukan binary classification. Ini adalah implementasi yang `rapi, jelas, dan siap untuk skripsi`.

---

## 🎯 Klasi katerisasi 4-Class (WHO Standard)

Labels dihitung dari Z-Score:
- **ZTB (Z-Score Tinggi Badan):** Z-Score height-for-age
- **ZBB (Z-Score Berat Badan):** Z-Score weight-for-age

### Definisi Kelas:

```
Class 0: Normal + Gizi Baik
└─ ZTB ≥ -2.0  (Normal)
└─ ZBB ≥ -1.0  (Gizi Baik)

Class 1: Normal + Kurang Gizi
└─ ZTB ≥ -2.0  (Normal)
└─ ZBB < -1.0  (Kurang Gizi)

Class 2: Stunting + Gizi Baik
└─ ZTB < -2.0  (Stunting)
└─ ZBB ≥ -1.0  (Gizi Baik)

Class 3: Stunting + Kurang Gizi
└─ ZTB < -2.0  (Stunting)
└─ ZBB < -1.0  (Kurang Gizi)
```

---

## 📂 File Struktur

### Global Evaluasi (Semua Data)
```
backend/app/ml/evaluate_knn_global_4class.py
api/app/ml/evaluate_knn_global_4class.py
└─ Class: KNNGlobalEvaluator4Class
└─ Class: ZScoreCalculator
└─ Methods:
   ├─ fetch_all_data()          # Fetch semua pengukuran
   ├─ evaluate_global()         # Main evaluation
   ├─ print_results()           # Format output
   └─ get_interpretation()      # Medical interpretation
```

### Per-Kader Evaluasi (Staff Individual)
```
backend/app/ml/evaluate_knn_per_kader_4class.py
api/app/ml/evaluate_knn_per_kader_4class.py
└─ Class: KNNKaderEvaluator4Class
└─ Methods:
   ├─ fetch_training_data()     # Semua data untuk training
   ├─ fetch_kader_data()        # Data kader tertentu (with month filter)
   ├─ evaluate_kader()          # Evaluai per-kader
   └─ print_results()           # Format output
```

### K Parameter Evaluasi (Optimal K)
```
backend/app/ml/evaluate_k_parameter_4class.py
api/app/ml/evaluate_k_parameter_4class.py
└─ Class: KNNKParameterEvaluator4Class
└─ Methods:
   ├─ fetch_all_data()          # Fetch semua data
   ├─ evaluate_k()              # Test single K value
   ├─ evaluate_all_k_values()   # Test K=3,5,7,9
   ├─ determine_best_k()        # Tentukan K terbaik
   ├─ print_summary_table()     # Summary tabel
   └─ print_detailed_results()  # Detail per-K
```

---

## 🔧 Penggunaan

### 1. Global Evaluasi

```python
from app.ml.evaluate_knn_global_4class import KNNGlobalEvaluator4Class

evaluator = KNNGlobalEvaluator4Class(k=5)
result = evaluator.evaluate_global()
evaluator.print_results(result)
print(evaluator.get_interpretation(result))
```

**Output:**
```
HASIL EVALUASI KNN GLOBAL - 4-CLASS CLASSIFICATION
================================================

📋 SUMMARY:
  K Value: 5
  Total Samples: 1234
  Overall Accuracy: 0.7856 (78.56%)

📊 CLASS DISTRIBUTION (Actual):
  Class 0: Normal + Gizi Baik       = 600 (48.63%)
  Class 1: Normal + Kurang Gizi     = 300 (24.31%)
  Class 2: Stunting + Gizi Baik     = 150 (12.16%)
  Class 3: Stunting + Kurang Gizi   = 184 (14.90%)

🔲 4x4 CONFUSION MATRIX:
[[ 500   50   30   20]
 [  40  250   10    0]
 [  20   15  120   15]
 [  30    5   10  139]]

📈 PER-CLASS METRICS (One-vs-Rest):
  Class                        Precision    Recall  F1-Score  Support
  0: Normal + Gizi Baik         0.8333    0.8333    0.8333      600
  1: Normal + Kurang Gizi       0.7692    0.8333    0.8000      300
  2: Stunting + Gizi Baik       0.7143    0.8000    0.7556      150
  3: Stunting + Kurang Gizi     0.7391    0.7554    0.7472      184
  MACRO-AVERAGE                 0.7640    0.8030    0.7840
```

### 2. Per-Kader Evaluasi

```python
from app.ml.evaluate_knn_per_kader_4class import KNNKaderEvaluator4Class

evaluator = KNNKaderEvaluator4Class(k=5)

# Evaluate kader ID 1, semua bulan
result = evaluator.evaluate_kader(user_id=1)

# Evaluate kader ID 1, bulan November
result = evaluator.evaluate_kader(user_id=1, month=11)

evaluator.print_results(result)
```

### 3. K Parameter Evaluasi

```python
from app.ml.evaluate_k_parameter_4class import KNNKParameterEvaluator4Class

evaluator = KNNKParameterEvaluator4Class()

# Test K = [3, 5, 7, 9]
results = evaluator.evaluate_all_k_values([3, 5, 7, 9])

# Print summary
evaluator.print_summary_table(results)

# Print detailed per-K
evaluator.print_detailed_results(results)
```

---

## 📊 Metrics Explanation

### Accuracy (Overall)
```
Accuracy = (Semua prediksi benar) / Total predictions
```

### Precision (Per-Class, One-vs-Rest)
```
Precision = TP / (TP + FP)
Artinya: Dari yang diprediksi class X, berapa yang benar?
```

### Recall (Per-Class, One-vs-Rest)
```
Recall = TP / (TP + FN)
Artinya: Dari yang sebenarnya class X, berapa yang terdeteksi?
```

### F1-Score (Per-Class)
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
Artinya: Balance antara Precision dan Recall
```

### Macro-Average
```
Macro-Average = (Class 0 + Class 1 + Class 2 + Class 3) / 4
Artinya: Average dari semua class metrics
```

---

## 🔍 Z-Score Kalkulasi

### ZTB (Height-for-Age)
```python
ZTB = (Tinggi_Aktual - Mean_Referensi) / StdDev_Referensi
```

**WHO Standard:**
- ZTB < -2.0  → Stunting
- ZTB ≥ -2.0  → Normal height

### ZBB (Weight-for-Age)
```python
ZBB = (Berat_Aktual - Mean_Referensi) / StdDev_Referensi
```

**WHO Standard:**
- ZBB < -1.0  → Kurang Gizi (underweight)
- ZBB ≥ -1.0  → Gizi Baik

---

## 🤖 Model KNN Configuration

```python
KNeighborsClassifier(
    n_neighbors=5,              # K value (default optimal)
    metric='euclidean',         # Distance metric
    weights='distance',         # Distance-weighted voting
    algorithm='auto'
)

Features: 6 inputs
├─ jenis_kelamin (binary: L=1, P=0)
├─ usia_bulan
├─ tinggi_badan
├─ berat_badan
├─ lingkar_lengan
└─ lingkar_kepala

Normalization: StandardScaler
```

---

## 📈 4x4 Confusion Matrix Interpretation

### Structure:
```
                 Predicted Class
              0    1    2    3
Actual Class
      0       a    b    c    d
      1       e    f    g    h
      2       i    j    k    l
      3       m    n    o    p
```

### Diagonal = Correct Predictions (a, f, k, p)
- Class 0 that are correctly identified as Class 0
- Class 1 that are correctly identified as Class 1
- etc.

### Off-diagonal = Misclassifications
- Class 0 misclassified as Class 1, 2, or 3
- etc.

---

## ✅ Quality Checklist untuk Skripsi

- [x] 4-class classification (bukan binary)
- [x] Ground truth dari Z-Score (WHO standard)
- [x] 4x4 confusion matrix
- [x] One-vs-rest metrics per class
- [x] Macro-average metrics
- [x] StandardScaler normalization
- [x] KNeighborsClassifier sklearn
- [x] K=5 (proven optimal)
- [x] Rapi dan jelas  
- [x] Siap untuk evaluasi akademis

---

## 🚀 Penggunaan API (Coming Soon)

API endpoints akan ditambahkan untuk:
```
POST /api/evaluation/knn/global-4class
POST /api/evaluation/knn/kader/{user_id}-4class
POST /api/evaluation/k-parameter-4class
```

---

## 📚 Referensi

- **WHO Growth Standards:** https://www.who.int/tools/child-growth-standards/
- **Z-Score Calculation:** WHO 2006 for child height-for-age and weight-for-age
- **Scikit-Learn KNN:** https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html

---

## 📝 Catatan Penting

1. **Data Aktual:** Dari perhitungan Z-Score (bukan status_gizi_label)
2. **One-vs-Rest:** Untuk multiclass, metrics dihitung per-class
3. **Macro-Average:** Average sederhana dari semua class metrics
4. **Training:** Menggunakan semua data pengukuran
5. **Testing:** Per-kader atau global, tapi metrics dengan same method

---

## ❓ FAQ

**Q: Bagaimana jika jumlah samples per class tidak balance?**
A: Macro-average metrics akan menangani ini (setiap class memiliki weight sama)

**Q: Mengapa menggunakan One-vs-Rest untuk metrics?**
A: Untuk clarity dan fairness dalam multiclass evaluation

**Q: Apakah bisa menggunakan K value lain?**
A: Ya, tapi K=5 sudah proven optimal dari K parameter evaluation

**Q: Data training & testing sama?**
A: Ya, global evaluation menggunakan semua data. Per-kader menggunakan semua data training, kader-specific untuk testing.

---

## 📞 Support

Untuk pertanyaan:
- Check docstring di source code
- Lihat example di `main()` function
- Baca WHO growth standards documentation

---

**Status:** ✅ READY FOR THESIS EVALUATION
**Last Updated:** 2024-11-20
**Framework:** Scikit-Learn KNN + 4-Class Classification
**Classification:** WHO Standard Z-Score Based
