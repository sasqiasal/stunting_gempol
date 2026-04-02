# 📁 FILE STRUKTUR KLASIFIKASI - PANDUAN LENGKAP

## ⭐ QUICK ANSWER: File Mana yang Digunakan?

### Ada 2 Setup Berbeda:

#### **1️⃣ BACKEND (Main Server - Production)**
```
backend/
  ├── app/ml/
  │   ├── knn_model.py              ← 🎯 MODEL KLASIFIKASI (sklearn KNeighborsClassifier)
  │   └── knn_manual.py             ← Confusion matrix calculation
  ├── app/services/
  │   ├── prediction_service.py     ← 🎯 PREDIKSI (menggunakan knn_model.py)
  │   └── evaluation_service.py     ← Evaluasi performa
  └── app/ml/
      └── knn_model.pkl            ← Model yang sudah dilatih (pickle)
```

#### **2️⃣ API (Vercel/Serverless - Alternative)**
```
api/
  ├── app/ml/
  │   ├── knn_model.py              ← 🎯 MODEL KLASIFIKASI (sklearn KNeighborsClassifier)
  │   └── knn_manual.py             ← Confusion matrix calculation
  ├── app/services/
  │   └── prediction_service.py     ← 🎯 PREDIKSI (menggunakan knn_model.py)
  └── app/ml/
      └── knn_model.pkl            ← Model yang sudah dilatih (pickle)
```

---

## ⚠️ PENTING: 6 vs 8 Fitur - KLARIFIKASI

Ada **KONTRADIKSI** dalam kode knn_model.py:

### Dokumentasi (di komentar):
```
Menggunakan 6 fitur utama (TANPA Z-Scores sebagai input):
1. Jenis Kelamin
2. Usia
3. Berat Badan
4. Tinggi Badan
5. Lingkar Lengan
6. Lingkar Kepala
```

### Kode yang Sebenarnya:
```python
features = np.array([
    jk_encoded,      # 1
    usia_bulan,      # 2
    berat_badan,     # 3
    tinggi_badan,    # 4
    lingkar_lengan,  # 5
    lingkar_kepala,  # 6
    zscore_bbu,      # 7 ← INCLUDED!
    zscore_tbu       # 8 ← INCLUDED!
])
```

### Training Data (CSV):
```
jenis_kelamin, usia_bulan, berat_badan, tinggi_badan, lingkar_lengan, lingkar_kepala, z_score_bb, z_score_tb
Kolom 1        Kolom 2     Kolom 3       Kolom 4       Kolom 5         Kolom 6         Kolom 7     Kolom 8
```

### Custom Weights:
```python
X_weighted[:, 6] *= 2.0  # zscore_bbu × 2
X_weighted[:, 7] *= 2.0  # zscore_tbu × 2
```

### ✅ JAWABAN: **SEBENARNYA MENGGUNAKAN 8 FITUR!**

**Dokumentasi di komentar SALAH/OUTDATED!** 
Kode yang sebenarnya menggunakan **8 fitur dengan z-scores**, dan z-scores diberi bobot **2x lebih besar** agar prediksi lebih menempel pada WHO standard.

---

### **1. PRIMARY: knn_model.py** (Untuk Training & Prediction)

#### Lokasi:
- `backend/app/ml/knn_model.py`
- `api/app/ml/knn_model.py`

#### Fungsi Utama:

```python
class StuntingKNNModel:
    """
    Model KNN untuk klasifikasi 4-class stunting
    Menggunakan sklearn.neighbors.KNeighborsClassifier
    Input: 8 fitur (6 anthropometric + 2 z-scores)
    """
    
    def __init__(self, n_neighbors: int = 5):
        self.model = KNeighborsClassifier(
            n_neighbors=5,
            metric='euclidean',
            weights='distance',
            algorithm='auto'
        )
        self.scaler = StandardScaler()
    
    def prepare_features(self, jk, usia, bb, tb, ll, lk, zscore_bbu, zscore_tbu):
        """Prepare 8 fitur: 6 anthropometric + 2 z-scores"""
        features = np.array([
            jk_encoded,    # 1
            usia_bulan,    # 2
            berat_badan,   # 3
            tinggi_badan,  # 4
            lingkar_lengan,    # 5
            lingkar_kepala,    # 6
            zscore_bbu,   # 7 ← Z-SCORE INCLUDED
            zscore_tbu    # 8 ← Z-SCORE INCLUDED
        ])
        return features
    
    def train(self, X_train, y_train):
        """Train model dengan 8 fitur"""
        # 1. Scale fitur menggunakan StandardScaler
        self.scaler.fit(X_train)
        X_scaled = self.scaler.transform(X_train)
        
        # 2. Apply custom weights (2x pada z-scores)
        X_weighted = self._apply_custom_weights(X_scaled)
        
        # 3. Train KNN
        self.model.fit(X_weighted, y_train)
    
    def predict(self, features):
        """Predict 4-class label (0, 1, 2, 3) menggunakan 8 fitur"""
        # Scale dan weight
        features_scaled = self.scaler.transform(features)
        features_weighted = self._apply_custom_weights(features_scaled)
        
        # Predict
        prediction = self.model.predict(features_weighted)
        probabilities = self.model.predict_proba(features_weighted)
        confidence = max(probabilities[0])
        
        return prediction, confidence
    
    def _apply_custom_weights(self, X_scaled):
        """Apply 2x weight pada fitur z-scores (index 6 dan 7)"""
        X_weighted = X_scaled.copy()
        X_weighted[:, 6] *= 2.0  # zscore_bbu
        X_weighted[:, 7] *= 2.0  # zscore_tbu
        return X_weighted
```

#### Input Features (8 fitur):
```
ANTHROPOMETRIC (6 fitur):
  1. jenis_kelamin      (0=Perempuan, 1=Laki-laki)
  2. usia_bulan         (age in months)
  3. berat_badan        (weight in kg)
  4. tinggi_badan       (height in cm)
  5. lingkar_lengan     (arm circumference in cm)
  6. lingkar_kepala     (head circumference in cm)

Z-SCORES (2 fitur) - WITH 2X CUSTOM WEIGHT:
  7. zscore_bbu         (Z-Score Weight-for-Age) ⚖️ ×2.0 weight
  8. zscore_tbu         (Z-Score Height-for-Age) ⚖️ ×2.0 weight
```

**⚠️ Note:** Meskipun ada komentar saying "6 fitur utama", kode sebenarnya menggunakan **8 fitur** termasuk 2 z-scores dengan custom weights 2x lebih besar

#### Output (4-Class Classification):
```
0: Normal + Gizi Baik
1: Normal + Kurang Gizi
2: Stunting + Gizi Baik
3: Stunting + Kurang Gizi
```

#### Algoritma & Parameter:
| Parameter | Value | Alasan |
|-----------|-------|--------|
| Algorithm | K-Nearest Neighbors | Sederhana, interpretable, cocok untuk medical data |
| Distance | Euclidean | Standard untuk continuous features |
| K value | 5 (default) | Baik untuk ~500 training data |
| Weights | Distance-weighted | Tetangga dekat lebih penting |
| Scaling | StandardScaler | Normalisasi fitur (mean=0, std=1) |
| Custom Weights | 2x on z-scores | Z-scores diberi bobot 2x untuk WHO standard compliance |
| Input Features | 8 fitur | 6 anthropometric + 2 z-scores |
| Training Data | 500 samples | data_latih_stunting.csv dengan 8 fitur input |
| Output | 4-class label | 0, 1, 2, 3

---

### **2. SECONDARY: prediction_service.py** (Wrapper/Integration)

#### Lokasi:
- `backend/app/services/prediction_service.py`
- `api/app/services/prediction_service.py`

#### Fungsi:
```python
class PredictionService:
    @staticmethod
    def predict_stunting(
        jenis_kelamin: str,      # "L" atau "P"
        usia_bulan: int,
        tinggi_badan: float,
        berat_badan: float,
        lingkar_lengan: float,
        lingkar_kepala: float
    ) -> Dict:
        """
        Melakukan prediksi stunting dengan flow:
        
        1. Hitung Z-Score (untuk ground truth evaluasi)
        2. Prepare features
        3. Gunakan knn_model.py untuk prediksi
        4. Return hasil 4-class classification
        """
        
        # Step 1: Hitung Z-Score
        zscore_bbu = calculate_zscore_bbu(...)
        zscore_tbu = calculate_zscore_tbu(...)
        
        # Step 2: Get model
        model = get_knn_model()  # Load knn_model.py
        
        # Step 3: Prepare fitur
        features = model.prepare_features(...)
        
        # Step 4: Predict menggunakan knn_model
        prediction, confidence = model.predict(features)  # Result: (0-3, 0.0-1.0)
        
        # Step 5: Get nearest neighbors (untuk explanation)
        neighbors = model.find_nearest_neighbors(features, n_neighbors=10)
        
        # Step 6: Return hasil
        return {
            "status_gizi": "Stunting + Gizi Baik",  # Description
            "status_gizi_label": 2,                  # Numeric (0-3)
            "confidence_score": 0.85,
            "zscore_bbu": -1.5,
            "zscore_tbu": -2.3,
            "nearest_neighbors": [...]
        }
```

---

### **3. TERTIARY: knn_manual.py** (Evaluasi CM)

#### Lokasi:
- `backend/app/ml/knn_manual.py`
- `api/app/ml/knn_manual.py`

#### Fungsi:
```python
def calculate_confusion_matrix(y_true, y_pred, labels=[0,1,2,3]):
    """
    Hitung 4x4 confusion matrix secara manual
    Digunakan untuk evaluasi (bukan training)
    """
    cm = np.zeros((4, 4))
    for true, pred in zip(y_true, y_pred):
        cm[true, pred] += 1
    return cm

def calculate_metrics(y_true, y_pred):
    """
    Hitung per-class metrics (Precision, Recall, F1)
    """
    cm = calculate_confusion_matrix(y_true, y_pred)
    
    # Per-class OvR metrics
    for class_idx in range(4):
        # Binary classification: class_i vs rest
        tp = cm[class_idx, class_idx]
        fp = cm[:, class_idx].sum() - tp
        fn = cm[class_idx, :].sum() - tp
        
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * (precision * recall) / (precision + recall)
    
    return metrics
```

---

## 🔄 FLOW KLASIFIKASI LENGKAP

### **Untuk Prediksi (Mendapatkan Status Gizi Anak)**

```
User Input (6 fitur anthropometric)
  ├── jenis_kelamin
  ├── usia_bulan
  ├── tinggi_badan
  ├── berat_badan
  ├── lingkar_lengan
  └── lingkar_kepala
       ↓
       ↓ [Calculate Z-Scores]
       ↓
[prediction_service.py] → Add z-scores (zscore_bbu, zscore_tbu)
  → Total 8 fitur sekarang (6 anthropometric + 2 z-scores)
  1. Load model dari [api/app/ml/knn_model.py]
  2. Prepare 8 fitur
  3. Scale dengan StandardScaler
  4. Apply custom weights (2x pada z-scores)
  5. Predict menggunakan KNeighborsClassifier
       ↓
[api/app/ml/knn_model.py]
  - scaler.transform(8 features) ← Using all 8 features!
  - _apply_custom_weights() → multiply zscore features by 2x
  - model.predict(weighted_features) → KNN dengan k=5
       ↓
Status_Gizi Output (4-class)
  ├── 0: Normal + Gizi Baik
  ├── 1: Normal + Kurang Gizi
  ├── 2: Stunting + Gizi Baik
  └── 3: Stunting + Kurang Gizi
```

### **Untuk Evaluasi (Mengevaluasi Kinerja Model)**

```
Real Pengukuran Data (dari database)
  └── 100+ records dengan:
      ├── status_gizi (actual prediction)
      ├── zscore_tbu (ground truth)
      └── zscore_bbu (ground truth)
           ↓
           ↓ [backend/app/services/evaluation_service.py]
           ↓
Convert ke Labels:
  - y_true = [0, 1, 2, 1, 3, 2, ...]  (dari Z-Score)
  - y_pred = [0, 1, 2, 1, 3, 2, ...]  (dari status_gizi disimpan)
       ↓
       ↓ [backend/app/ml/knn_manual.py]
       ↓ calculate_confusion_matrix(y_true, y_pred)
       ↓ calculate_metrics(y_true, y_pred)
       ↓
Hasil Evaluasi:
  ├── 4x4 Confusion Matrix
  ├── Per-class Metrics (Precision, Recall, F1)
  ├── Macro-average Metrics
  └── Accuracy
```

---

## 📊 DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────┐
│  FILE STRUKTUR & DEPENDENSI KLASIFIKASI        │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Training Phase (Offline)                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  backend/data_latih_stunting.csv (500 rows)    │
│         ↓                                       │
│  [backend/app/ml/knn_model.py]                 │
│    - Load CSV                                   │
│    - Train KNeighborsClassifier                │
│    - Fit StandardScaler                         │
│    - Save to knn_model.pkl                      │
│         ↓                                       │
│  backend/app/ml/knn_model.pkl ← Model trained  │
│                                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Prediction Phase (Online - per request)        │
├─────────────────────────────────────────────────┤
│                                                 │
│  User Input (6 features)                        │
│         ↓                                       │
│  [api/app/services/prediction_service.py]      │
│    1. calculate_zscore()                        │
│    2. get_knn_model()                           │
│         ↓                                       │
│  [api/app/ml/knn_model.py]                     │
│    - scaler.transform(features)                │
│    - model.predict(scaled_features)            │
│    - model.predict_proba() for confidence      │
│    - model.kneighbors() for explanation        │
│         ↓                                       │
│  4-Class Prediction (0-3) + Confidence         │
│  Save to database.pengukuran.status_gizi       │
│                                                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Evaluation Phase (Periodic assessment)         │
├─────────────────────────────────────────────────┤
│                                                 │
│  Real Data from database                        │
│  - status_gizi (actual prediction) ← dari DB   │
│  - zscore_tbu, zscore_bbu (ground truth)       │
│         ↓                                       │
│  [backend/app/services/evaluation_service.py]  │
│    - convert_zscores_to_class_label()          │
│         ↓                                       │
│  [backend/app/ml/knn_manual.py]                │
│    - calculate_confusion_matrix(y_true, y_pred)│
│    - calculate_metrics()                        │
│         ↓                                       │
│  4x4 Confusion Matrix                           │
│  Per-class Metrics (P, R, F1)                   │
│  Macro-average Metrics & Accuracy              │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📋 SUMMARY TABLE

| Aspek | File | Fungsi |
|-------|------|--------|
| **Model** | `backend/app/ml/knn_model.py` | KNeighborsClassifier + StandardScaler (8 fitur) |
| **Training** | `knn_model.py` → `train()` method | Fit model dan scaler dengan 8 fitur dari CSV |
| **Inference** | `backend/app/services/prediction_service.py` | Get prediction untuk new data |
| **Prediction Model** | `knn_model.py` → `predict()` | Return 4-class label (0-3) dari 8 fitur |
| **Custom Weights** | `knn_model.py` → `_apply_custom_weights()` | Apply 2x weight pada z-scores (fitur 7 & 8) |
| **Evaluation** | `backend/app/ml/knn_manual.py` | Manual CM & metrics calculation |
| **Z-Score** | `app/utils/zscore_calculator.py` | Calculate ground truth & input fitur |
| **Database** | `pengukuran` table | Store predictions & Z-Scores |
| **Training Data** | `backend/data_latih_stunting.csv` | 500 samples dengan 8 fitur input + 1 target |

---

## 🎯 KEY TAKEAWAYS

1. **Klasifikasi dilakukan oleh:** `knn_model.py` menggunakan `KNeighborsClassifier`
2. **Input:** **8 fitur** (6 anthropometric + 2 z-scores)
3. **Output:** 4-class label (0, 1, 2, 3)
4. **Preprocessing:** StandardScaler (mean=0, std=1)
5. **Custom Weights:** Z-scores diberi bobot 2x lebih besar untuk WHO standard compliance
6. **Training:** Offline pada startup dengan 500 data dari CSV (8 fitur)
7. **Prediction:** Online per request, di-scale dan di-weight menggunakan fitted StandardScaler
8. **Evaluasi:** Manual confusion matrix calculation dari real data di database
9. **Ada 2 versi:** Backend (main) & API (Vercel alternative)

**⚠️ Penting:** Dokumentasi di komentar kode bilang "6 fitur" OUTDATED! Kode sebenarnya pakai **8 fitur** dengan z-scores.

---

**Simpulannya:** 
- 🎯 **Untuk klasifikasi pakai:** `knn_model.py` 
- 📊 **Untuk evaluasi pakai:** `knn_manual.py` 
- 🔄 **Untuk integration pakai:** `prediction_service.py` & `evaluation_service.py`
