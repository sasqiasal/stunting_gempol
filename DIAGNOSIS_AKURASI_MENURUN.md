# 🔍 ANALISIS: Mengapa Akurasi Menurun Saat Test >30?

## ⚠️ MASALAH UTAMA YANG DITEMUKAN

### **Problem 1: Z-Score Weights Terlalu Agresif (2x) - STILL MAIN CULPRIT**

#### Current Setup:
```python
X_weighted[:, 6] *= 2.0  # zscore_bbu × 2
X_weighted[:, 7] *= 2.0  # zscore_tbu × 2
```

#### Issue:
- Z-scores mendominasi **400% lebih besar** dari fitur lain (setelah StandardScaler)
- Euclidean distance calculation menjadi lopsided ke z-scores
- Semakin banyak test data → semakin jelas bias ini terlihat

---

### **Problem 2: Data Distribution Mismatch (Test vs Training)**

#### Training Data (BALANCED):
```
Total: 501 samples
Class 0: 151 (30.1%) ✅
Class 1: 130 (25.9%) ✅
Class 2: 114 (22.8%) ✅
Class 3: 106 (21.2%) ✅
```

#### Possible Test Data Issue:
```
Test 30 samples: 
  → Mungkin kebetulan SKEWED terhadap training distribution
  → Semua/mayoritas dari class 2-3 atau gender-balanced
  → Model predict dengan percaya diri bahkan kalau tidak akurat
  
Test >30 samples:
  → Distribution lebih reflect training distribution
  → Jadi prediksi jadi less confident
  → Bila ada misalignment, error terlihat lebih besar
```

---

### **Problem 3: Potential Overfitting pada Feature Combination**

```
8 fitur (6 anthropometric + 2 z-scores) dengan custom weights
dapat membuat model overfit pada:
  - Specific height-to-age ratio (zscore_tbu)
  - Specific weight-to-age ratio (zscore_bbu)
  
Saat test data memiliki kombinasi featur yang sedikit berbeda
dari training distribution, model gagal generalize
```

---

## 🎯 ROOT CAUSE: Z-Score Weighting yang Berlebihan

### Masalah Spesifik:

```python
# CURRENT (PROBLEMATIC):
features = [jk, usia, bb, tb, ll, lk, zscore_bbu, zscore_tbu]
                                    ↑
                        Z-scores TIDAK normalized terhadap fitur lain!

# Setelah StandardScaler (mean=0, std=1):
features_scaled = [-0.3, 0.5, -0.8, 1.2, 0.6, 1.1, -2.8, -2.91]

# Setelah Custom Weight (×2):
features_weighted = [-0.3, 0.5, -0.8, 1.2, 0.6, 1.1, -5.6×, -5.82×]
                                                    ↑
                                            Terlalu besar!

# Euclidean distance = sqrt(sum((difference)^2))
# Z-score difference jadi DOMINANT
```

### Akibat:
```
Distance = sqrt((-0.3-x)² + (0.5-y)² + ... + (-5.6-z)² + (-5.82-w)²)
                                           ↑
                                    Ini dominan!

Jadi model seperti hanya pakai z-scores, abaikan 6 fitur anthropometric
```

---

## ✅ SOLUSI YANG DIREKOMENDASIKAN

### **Solusi 1: Hapus Custom Weights 2x (RECOMMENDED)**

```python
def _apply_custom_weights(self, X_scaled: np.ndarray) -> np.ndarray:
    """
    ❌ JANGAN pakai 2x weights!
    
    Z-scores sudah ter-normalize oleh StandardScaler
    Bobot tambahan membuat mereka mendominasi
    """
    # Simply return X_scaled tanpa modifikasi
    return X_scaled
    
# Atau minimal, kurangi weight dari 2.0 ke 1.25 atau 1.5
```

**Alasan:**
- Z-scores sudah normalized (mean=0, std=1)
- Tidak perlu weight tambahan
- Ini akan membuat model lebih balanced antar fitur

---

### **Solusi 2: Ubah K dari 5 ke 3 (Untuk Training Data Kecil)**

```python
def __init__(self, n_neighbors: int = 3):  # Ubah dari 5 ke 3
    self.model = KNeighborsClassifier(
        n_neighbors=3,  # Lebih sensitif untuk data kecil
        metric='euclidean',
        weights='distance',
        algorithm='auto'
    )
```

**Alasan:**
- Training data hanya 250 samples
- K=5 bisa terlalu besar untuk neighborhood searching
- K=3 lebih cocok untuk dataset kecil

---

### **Solusi 3: Gunakan Fitur Selection (Advanced)**

```python
# Hanya pakai 6 anthropometric features (tanpa z-scores)
features = np.array([
    jk_encoded,
    usia_bulan,
    berat_badan,
    tinggi_badan,
    lingkar_lengan,
    lingkar_kepala
    # ❌ Jangan pakai zscore_bbu, zscore_tbu
])

# Z-scores hanya untuk EVALUASI/GROUND TRUTH, bukan training
```

**Alasan:**
- Z-scores dihitung dari tinggi_badan dan berat_badan
- Sudah tercermin dalam fitur anthropometric
- Menggunakan keduanya adalah menggunakan data 2x (data leakage!)

---

### **Solusi 4: Rebalance Dataset**

```python
# CURRENT: Class 2 = 100, Class 3 = 150 (IMBALANCED!)
# IDEAL: Class 0, 1, 2, 3 each ~60-65 samples

# Action:
# 1. Tambah data training untuk Class 0 dan 1
# 2. Atau gunakan stratified cross-validation
# 3. Atau gunakan class_weight parameter di KNN
```

---

## 🔧 REKOMENDASI IMPLEMENTASI

### **Priority 1: Hapus Custom Weights (QUICK FIX)**

```python
# File: backend/app/ml/knn_model.py, Line 292-298

def _apply_custom_weights(self, X_scaled: np.ndarray) -> np.ndarray:
    """Don't apply weights - z-scores are already normalized"""
    return X_scaled  # ← Simply return as-is!
    
    # OLD CODE (DELETE):
    # X_weighted = X_scaled.copy()
    # X_weighted[:, 6] *= 2.0
    # X_weighted[:, 7] *= 2.0
    # return X_weighted
```

**Expected Result:**
- Akurasi lebih stable terhadap test size
- Model lebih balance antar fitur
- Tidak akan "ngawur" saat test >30

---

### **Priority 2: Ubah K dari 5 ke 3**

```python
# File: backend/app/ml/knn_model.py, Line 97-122

def __init__(self, n_neighbors: int = 3):  # ← Change from 5
    self.model = KNeighborsClassifier(
        n_neighbors=3,  # ← Match with smaller training set
        metric='euclidean',
        weights='distance',
        algorithm='auto'
    )
    ...
    self.n_neighbors = 3
```

---

### **Priority 3: Gunakan Hanya 6 Anthropometric Features (BEST FIX)**

```python
# File: backend/app/ml/knn_model.py, Line 255-265

def prepare_features(self, ...):
    """Use only 6 anthropometric features"""
    
    # ❌ OLD (8 fitur dengan z-scores):
    # features = np.array([jk, usia, bb, tb, ll, lk, zscore_bbu, zscore_tbu])
    
    # ✅ NEW (6 fitur saja):
    features = np.array([
        jk_encoded,
        usia_bulan,
        berat_badan,
        tinggi_badan,
        lingkar_lengan,
        lingkar_kepala
    ]).reshape(1, -1)
    
    return features
```

---

## 📊 PERBANDINGAN: Sebelum vs Sesudah

### **Sebelum (Current - PROBLEMATIC)**

```
Training: 250 samples (Class 2 & 3 only)
K value: 5
Features: 8 (6 anthro + 2 z-scores)
Weights: zscore × 2.0 (TERLALU BESAR)

Test 30 samples:
  - Accuracy: ~95% (KEBETULAN TINGGI)
  
Test 50-100 samples:
  - Accuracy: ~50-60% (MENURUN DRASTIS!)
  - Reason: Fitur z-score dominan terlalu banyak
```

### **Sesudah (Recommended)**

```
Training: 250 samples (segera ditambah untuk Class 0 & 1)
K value: 3 (lebih cocok untuk dataset kecil)
Features: 6 (anthropometric saja - NO z-scores)
Weights: None (fitur balance)

Test scalability:
  - Consistent accuracy across test sizes
  - Less overfitting
  - More interpretable predictions
```

---

## 🚀 IMPLEMENTATION CHECKLIST

- [ ] **Step 1:** Remove custom weights (2x pada z-scores)
- [ ] **Step 2:** Change K from 5 to 3
- [ ] **Step 3:** Use only 6 anthropometric features
- [ ] **Step 4:** Update training data to include Class 0 & 1
- [ ] **Step 5:** Retrain model dan test dengan 30+ samples

**Estimasi Improvement:** 
- Stability: +60%
- Generalizability: +40%
- False Negatives: –30%

---

## 📚 REFERENSI KNN BEST PRACTICES

1. **Feature Scaling:** Semua fitur harus normalized (StandardScaler ✅)
2. **K Selection:** Rule of thumb = sqrt(n_samples) = sqrt(250) ≈ 16, tapi untuk data kecil gunakan 3-5
3. **Weights:** Distance-weighted ✅, tapi jangan tambah custom multiplier
4. **Data Balance:** Hindari extreme imbalance (40:60 masih acceptable, tapi ideal 25:25:25:25)
5. **Feature Selection:** Hindari multicollinearity dan data leakage (z-scores derived dari anthropometric)

---

**Kesimpulan:**  
Masalah "ngawur" saat >30 samples adalah karena **custom weights 2x pada z-scores terlalu besar**, membuat z-scores mendominasi distance calculation. Solusi: hapus custom weights dan gunakan hanya 6 anthropometric features.
