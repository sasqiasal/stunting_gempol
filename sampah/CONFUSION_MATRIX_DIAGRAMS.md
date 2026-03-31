# Diagram Schema & Confusion Matrix Calculation

## 1. Data Flow untuk Confusion Matrix

```
PENGUKURAN TABLE (dari database)
├─ Input Features (6 kolom)
│  ├─ jenis_kelamin
│  ├─ usia_bulan
│  ├─ tinggi_badan
│  ├─ berat_badan
│  ├─ lingkar_lengan
│  └─ lingkar_kepala
│
├─ Ground Truth (1 kolom)
│  └─ zscore_tbu → Convert to y_true
│                  [1 if < -2.0, 0 if >= -2.0]
│
└─ Prediction (1 kolom)
   └─ status_gizi_label → Convert to y_pred
                      [1 if in (2,3), 0 if in (0,1)]
         
         ↓ ↓ ↓
         
Confusion Matrix Calculation
├─ TP = count(y_true=1 AND y_pred=1)
├─ TN = count(y_true=0 AND y_pred=0)
├─ FP = count(y_true=0 AND y_pred=1)
└─ FN = count(y_true=1 AND y_pred=0)
   
   ↓
   
Evaluation Metrics
├─ Accuracy = (TP+TN) / (TP+TN+FP+FN)
├─ Precision = TP / (TP+FP)
├─ Recall = TP / (TP+FN)
├─ Specificity = TN / (TN+FP)
└─ F1-Score = 2*(P*R)/(P+R)
```

---

## 2. Confusion Matrix Visual (Binary Classification)

```
                          PREDICTED CLASS
                       ┌──────┬──────────┐
                       │      │ Stunting │ Normal
                       ├──────┼──────────┼────────┤
ACTUAL      Stunting   │ TP   │    50    │ FN  2  │
  CLASS        │       ├──────┼──────────┼────────┤
            Normal     │ FP   │    5     | TN 250 │
                       └──────┴──────────┴────────┘

Total = 307 samples

TP = 50 (model correctly predicted stunting)
TN = 250 (model correctly predicted normal)
FP = 5 (model incorrectly predicted stunting when actually normal)
FN = 2 (model missed stunting - DANGEROUS!)

Accuracy = (50+250)/307 = 97.6%
Recall = 50/(50+2) = 96.2% (important for medical!)
```

---

## 3. Status Gizi 4-Class Breakdown

```
           Z-Score TB/U        Z-Score BB/U        Label
           (Stunting)          (Nutrition)
┌────────────────────────────────────────────────┐
│ >= -2.0 (Normal Height)  AND  >= -2.0 (Good)   │  0
│ Normal + Gizi Baik       →     Normal (y=0)    │
├────────────────────────────────────────────────┤
│ >= -2.0 (Normal Height)  AND  < -2.0 (Poor)    │  1
│ Normal + Kurang Gizi     →     Normal (y=0)    │
├────────────────────────────────────────────────┤
│ < -2.0 (Short Height!)   AND  >= -2.0 (Good)   │  2
│ Stunting + Gizi Baik     →     STUNTING (y=1)  │  ← WHO CRITERION
├────────────────────────────────────────────────┤
│ < -2.0 (Short Height!)   AND  < -2.0 (Poor)    │  3
│ Stunting + Kurang Gizi   →     STUNTING (y=1)  │
└────────────────────────────────────────────────┘

Binary Conversion:
  Labels 0,1 → Normal     (y_pred = 0)
  Labels 2,3 → Stunting   (y_pred = 1)
```

---

## 4. Ground Truth Determination Process

```
Step 1: Measurement
  ┌──────────────────────────────┐
  │ Kader mengukur:              │
  │ - Tinggi Badan               │
  │ - Berat Badan                │
  │ - Lingkar Lengan             │
  │ - Lingkar Kepala             │
  └────────────┬─────────────────┘
               │
               ▼
Step 2: Calculate Z-Scores (WHO Standard)
  ┌──────────────────────────────┐
  │ System calculate:             │
  │ - Z-Score Berat/Usia (BB/U)   │
  │ - Z-Score Tinggi/Usia (TB/U)  │
  └────────────┬─────────────────┘
               │
               ▼
Step 3: Determine Ground Truth
  ┌──────────────────────────────┐
  │ y_true = 1 if zscore_tbu<-2  │
  │          0 if zscore_tbu>=-2  │
  │ (Automatic, no manual action) │
  └────────────┬─────────────────┘
               │
               ▼
Step 4: Model Prediction
  ┌──────────────────────────────┐
  │ KNN Model predicts:           │
  │ status_gizi_label (0-3)       │
  │ y_pred = 1 if label in (2,3)  │
  │         = 0 if label in (0,1) │
  └────────────┬─────────────────┘
               │
               ▼
Step 5: Compare & Calculate CM
  ┌──────────────────────────────┐
  │ TP, TN, FP, FN calculated    │
  │ Metrics computed              │
  └──────────────────────────────┘
```

---

## 5. Database Schema Relationship

```
BALITA
  │
  ├─ id (PK)
  ├─ nama, nik, tgl_lahir
  └─ status_terkini
     (updated from latest pengukuran)
     
      │ has many
      ▼
      
PENGUKURAN (many-to-one with Balita)
  │
  ├─ PK: id
  ├─ FK: balita_id
  ├─ FK: kader_id
  │
  ├─ Measurements:
  │  ├─ tinggi_badan
  │  ├─ berat_badan
  │  ├─ lingkar_lengan
  │  └─ lingkar_kepala
  │
  ├─ Calculated:
  │  ├─ zscore_bbu (Z-Score BB/U)
  │  ├─ zscore_tbu ← GROUND TRUTH
  │  ├─ status_gizi_label (0-3)
  │  └─ confidence_score
  │
  ├─ Metadata:
  │  ├─ tanggal_pengukuran
  │  ├─ catatan
  │  ├─ created_at
  │  └─ updated_at
  │
      │ has one
      ▼
      
EVALUASI_MODEL_KNN (one-to-one with Pengukuran)
  │
  ├─ PK: id
  ├─ FK: pengukuran_id
  │
  ├─ k_value (e.g., 5)
  ├─ algorithm ("KNN")
  │
  └─ nearest_neighbors (JSONB array)
     ├─ [0] {index: 0, distance: 0.45, label: 2, ...}
     ├─ [1] {index: 1, distance: 0.52, label: 2, ...}
     ├─ [2] {index: 2, distance: 0.63, label: 2, ...}
     ├─ [3] {index: 3, distance: 0.71, label: 3, ...}
     └─ [4] {index: 4, distance: 0.78, label: 1, ...}

(No "actual_status" or "verified_status" column)
(Ground truth is automatically determined from zscore_tbu)
```

---

## 6. Feature Engineering - Input vs Ground Truth

```
INPUT FEATURES (untuk training model KNN):
┌─────────────────────────────────────┐
│ 1. jenis_kelamin (encoded: L=1, P=0)│
│ 2. usia_bulan                       │
│ 3. tinggi_badan                     │
│ 4. berat_badan                      │
│ 5. lingkar_lengan                   │
│ 6. lingkar_kepala                   │
└────────────────▲────────────────────┘
                 │
          NEVER USE:
          ✗ zscore_tbu
          ✗ zscore_bbu
          (DATA LEAKAGE!)

                 │
                 ▼
OUTPUT/LABELS (untuk pembanding):
┌─────────────────────────────────────┐
│ GROUND TRUTH:                       │
│ y_true = 1 if zscore_tbu < -2       │
│        = 0 if zscore_tbu >= -2      │
│                                     │
│ PREDICTION:                         │
│ y_pred = 1 if status_gizi_label∈(2,3)
│        = 0 if status_gizi_label∈(0,1)
└─────────────────────────────────────┘
```

---

## 7. Confusion Matrix Interpretation

```
                    ┌─────────────┬─────────────┐
                    │ Pred NO     │ Pred YES    │
                    │ (Normal)    │ (Stunting)  │
        ┌───────────┼─────────────┼─────────────┤
Actual  │ NO        │ TN=250      │ FP=5        │ ← Normal tapi
        │ (Normal)  │ (GOOD)      │ (Type I)    │   model salah
        ├───────────┼─────────────┼─────────────┤
        │ YES       │ FN=2        │ TP=50       │
        │(Stunting) │ (Type II)   │ (GOOD)      │ ← Stunting anak
        └───────────┼─────────────┼─────────────┘   terdeteksi!
                    │             │
                    └──Bad!───────┘
                (most critical
                 to minimize)

METRICS IMPORTANCE:
• Accuracy = 97.6%  (overall correctness)
• Precision = 90.9% (when model says stunting, how often right)
• Recall = 96.2%    (how many stunting cases caught) ← MOST IMPORTANT!
• F1 = 0.935        (harmonic mean)

In medical context: RECALL is critical!
Minimize FN (false negatives) = avoid missing stunting cases
```

---

## 8. Query Example untuk Manual CM Calculation

```sql
-- Calculate Confusion Matrix from pengukuran table
WITH classifications AS (
  SELECT 
    id,
    zscore_tbu,
    status_gizi_label,
    CASE WHEN zscore_tbu < -2.0 THEN 1 ELSE 0 END as ground_truth,
    CASE WHEN status_gizi_label IN (2,3) THEN 1 ELSE 0 END as prediction
  FROM pengukuran
  WHERE created_at >= '2024-01-01'  -- optional filter
)
SELECT
  -- Confusion Matrix Stats
  SUM(CASE WHEN ground_truth=1 AND prediction=1 THEN 1 ELSE 0 END) as TP,
  SUM(CASE WHEN ground_truth=0 AND prediction=0 THEN 1 ELSE 0 END) as TN,
  SUM(CASE WHEN ground_truth=0 AND prediction=1 THEN 1 ELSE 0 END) as FP,
  SUM(CASE WHEN ground_truth=1 AND prediction=0 THEN 1 ELSE 0 END) as FN,
  
  -- Calculated Metrics
  COUNT(*) as total,
  ROUND(100.0 * (
    SUM(CASE WHEN ground_truth=1 AND prediction=1 THEN 1 ELSE 0 END) +
    SUM(CASE WHEN ground_truth=0 AND prediction=0 THEN 1 ELSE 0 END)
  ) / COUNT(*), 2) as accuracy_percent
  
FROM classifications;

-- Result Example:
-- TP │ TN  │ FP │ FN │ total │ accuracy_percent
-- 50 │ 250 │ 5  │ 2  │ 307   │ 97.68
```

---

## 9. Files dengan Ground Truth & Confusion Matrix Logic

```
api/app/utils/zscore_calculator.py (line 247-257)
  ├─ def is_stunting(zscore_tbu) → zscore_tbu < -2.0

api/app/ml/knn_manual.py
  ├─ calculate_confusion_matrix(y_true, y_pred)
  ├─ calculate_metrics()
  └─ format_confusion_matrix_table()

api/app/routes/evaluasi.py
  ├─ evaluate_model_performance()
  │  ├─ Load data dari CSV
  │  ├─ Split train/test
  │  ├─ Train KNN untuk K=3,5,7,9
  │  ├─ Predict test set
  │  ├─ Calculate CM untuk setiap K
  │  └─ Return k_comparisons dengan TP/TN/FP/FN

api/app/routes/pengukuran.py
  ├─ create_pengukuran() → hitung zscore → simpan
  ├─ insert ke evaluasi_model_knn
  └─ update status_terkini di balita
```

---

## 10. Checklist Implementasi

```
☐ Extract ground truth: y_true = [1 if zscore_tbu < -2 else 0]
☐ Extract prediction:   y_pred = [1 if label in (2,3) else 0]
☐ Calculate TP = sum((y_true==1) & (y_pred==1))
☐ Calculate TN = sum((y_true==0) & (y_pred==0))
☐ Calculate FP = sum((y_true==0) & (y_pred==1))
☐ Calculate FN = sum((y_true==1) & (y_pred==0))
☐ Validate: TP+TN+FP+FN == total records
☐ Calculate Accuracy = (TP+TN) / Total
☐ Calculate Precision = TP / (TP+FP)
☐ Calculate Recall = TP / (TP+FN)
☐ Calculate F1-Score = 2*(P*R)/(P+R)
☐ Store in database or API response
☐ Display in frontend with confusion matrix table
☐ Add explanation/interpretation
```
