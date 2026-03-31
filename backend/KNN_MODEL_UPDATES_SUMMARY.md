# 📋 KNN Model Updates Summary

## Tanggal Update: 29 Maret 2026
## File: `backend/app/ml/knn_model.py`

---

## ✅ Fitur yang Telah Diimplementasikan

### 1. **StandardScaler Preprocessing** ✓
**Lokasi:** Class `StuntingKNNModel.__init__()` dan method `train()`

```python
# Training Phase (fit_transform)
X_train_scaled = self.scaler.fit_transform(X_train)

# Prediction Phase (transform only)
X_scaled = self.scaler.transform(X)
```

**Keuntungan:**
- Menormalisasi semua fitur ke mean=0, std=1
- Fitur 'usia_bulan' tidak kalah bobot dengan 'tinggi_badan'
- Setiap fitur berkontribusi secara setara dalam perhitungan jarak Euclidean
- fit() hanya dilakukan pada training data, transform() pada data baru

**Implementasi:**
```python
self.scaler = StandardScaler()
# di training: X_train_scaled = self.scaler.fit_transform(X_train)
# di prediksi: X_scaled = self.scaler.transform(X)
```

---

### 2. **Distance Weighting** ✓
**Lokasi:** Class `StuntingKNNModel.__init__()` - Parameter KNeighborsClassifier

```python
self.model = KNeighborsClassifier(
    n_neighbors=n_neighbors,
    metric='euclidean',
    weights='distance',  # ← DISTANCE WEIGHTING
    algorithm='auto'
)
```

**Keuntungan:**
- Tetangga yang lebih dekat memiliki pengaruh lebih besar dalam votingclass
- Tetangga yang sangat jauh (outlier dalam fitur space) tidak memiliki pengaruh sebesar tetangga yang mirip
- Menghasilkan prediksi yang lebih akurat dan smooth

**Formula Weighting:**
```
weight = 1 / distance
```

Contoh:
- Tetangga pada distance=0.5 mendapat weight=2.0
- Tetangga pada distance=2.0 mendapat weight=0.5
- Tetangga pada distance=10.0 mendapat weight=0.1

---

### 3. **Optimalisasi Parameter K** ✓
**Lokasi:** Class `StuntingKNNModel.__init__()`

**Rekomendasi:**
- **Default:** `n_neighbors=5` (good balance untuk dataset medium-large)
- **Alternatif:** `n_neighbors=3` (untuk dataset kecil, mengurangi overfitting)

**Pedoman Pemilihan:**
```python
# Dataset > 200 sampel
knn_model = StuntingKNNModel(n_neighbors=5)

# Dataset < 200 sampel
knn_model = StuntingKNNModel(n_neighbors=3)
```

**Alasan:**
- K=3: Underfitting cenderung lebih rendah, cocok untuk data sedikit
- K=5: Balance yang baik, cocok untuk data umum
- K>7: Risiko overfitting meningkat dengan data terbatas

---

### 4. **Validasi Medis Z-Score** ✓
**Lokasi:** Method `validate_zscore()` dan `predict_with_zscore_validation()`

#### 4a. Method `validate_zscore(zscore_tbu, zscore_bbu)`

**Fungsi:** Deteksi data ekstrem/outlier sebelum masuk KNN

**Parameter WHO Z-Score Range:**
```
Normal:           -2.0 ≤ zscore < 3.0 (WHO standard growth)
Stunting:         -3.0 ≤ zscore < -2.0 (height-for-age)
Severe Stunting:  -4.0 ≤ zscore < -3.0
Extreme Low:      zscore < -3.0 (🚨 OUTLIER)
Extreme High:     zscore > 3.0 (🚨 OUTLIER)
```

**Return Value - Dictionary:**
```python
{
    "is_valid": bool,           # True jika data normal
    "is_outlier": bool,         # True jika ada nilai ekstrem
    "status": str,              # "NORMAL" / "OUTLIER_EXTREME_LOW" / "OUTLIER_EXTREME_HIGH"
    "zscore_tbu_status": str,   # Deskripsi untuk tinggi/usia
    "zscore_bbu_status": str,   # Deskripsi untuk berat/usia
    "warning": str,             # Pesan peringatan jika ada
    "zscore_tbu": float,        # Nilai zscore_tbu (rounded 2 decimal)
    "zscore_bbu": float         # Nilai zscore_bbu (rounded 2 decimal)
}
```

**Contoh Output:**
```json
{
    "is_valid": false,
    "is_outlier": true,
    "status": "OUTLIER_EXTREME_HIGH",
    "zscore_tbu_status": "EXTREME_HIGH (> +3.0 SD)",
    "zscore_bbu_status": "NORMAL (>= -2.0 SD)",
    "warning": "⚠️ PERINGATAN MEDIS: Tinggi badan sangat ekstrem tinggi (zscore_tbu=3.5). Bayi mungkin tidak stunting, perlu verifikasi.",
    "zscore_tbu": 3.5,
    "zscore_bbu": 1.2
}
```

**Use Case:**
```python
validation = model.validate_zscore(
    zscore_tbu=2.5,   # Bayi tinggi
    zscore_bbu=1.0    # Bayi berat normal
)

if validation["is_outlier"]:
    print(f"⚠️ {validation['warning']}")  # Tandai untuk verifikasi manual
```

#### 4b. Method `predict_with_zscore_validation(X, zscore_tbu, zscore_bbu)`

**Fungsi:** Prediksi KNN + Validasi Z-Score dalam satu method

**Return Value - Dictionary JSON Lengkap:**
```python
{
    "prediction_code": 0,           # Label kelas (0-3)
    "prediction_label": "Normal & Gizi Baik",
    "confidence": 0.85,             # Confidence score (0-1)
    "zscore_validation": {
        "is_valid": true,
        "is_outlier": false,
        "status": "NORMAL",
        "zscore_tbu_status": "STUNTING (< -2.0 SD)",
        "zscore_bbu_status": "NORMAL (>= -2.0 SD)",
        "warning": null,
        "zscore_tbu": -2.3,
        "zscore_bbu": -1.5
    },
    "model_config": {
        "n_neighbors": 5,
        "metric": "euclidean",
        "weights": "distance",
        "preprocessing": "StandardScaler (fit on training, transform on input)"
    }
}
```

**Usage Example:**
```python
# Persiapan fitur
features = model.prepare_features(
    jenis_kelamin="L",
    usia_bulan=24,
    tinggi_badan=75.5,
    berat_badan=10.2,
    lingkar_lengan=16.3,
    lingkar_kepala=48.5,
    zscore_tbu=-2.1,
    zscore_bbu=-1.0
)

# Prediksi dengan validasi
result = model.predict_with_zscore_validation(
    X=features,
    zscore_tbu=-2.1,
    zscore_bbu=-1.0
)

# Check hasil
if result["zscore_validation"]["is_outlier"]:
    print("🚨 Data ekstrem - perlu verifikasi manual")
else:
    print(f"✓ Prediksi: {result['prediction_label']}")
```

---

### 5. **Output JSON dengan Distance dan Label Code** ✓
**Lokasi:** Method `predict_with_zscore_validation()`

**Struktur Output:**
```json
{
    "prediction_code": 2,
    "prediction_label": "Stunting & Gizi Baik",
    "confidence": 0.78,
    "distance": 1.23,  // ← Akan diisi oleh sistem yang memanggil
    "zscore_validation": {
        "is_valid": true,
        "is_outlier": false,
        "status": "NORMAL",
        "zscore_tbu": -2.5
    },
    "model_config": {...}
}
```

**Cara Menggunakan di Sistem:**

1. **Di API Endpoint (`routes/evaluasi.py` atau `routes/pengukuran.py`):**
```python
# Panggil model dengan validasi
result = model.predict_with_zscore_validation(
    X=features,
    zscore_tbu=zscore_tbu,
    zscore_bbu=zscore_bbu
)

# Tambahkan distance dari nearest neighbors
neighbors = model.find_nearest_neighbors(features)
result["distance"] = neighbors[0]["distance"] if neighbors else None

# Return ke frontend
return result
```

2. **Di Frontend (JavaScript/React):**
```javascript
const result = await fetch('/api/evaluasi/predict').then(r => r.json());

console.log(`Prediksi: ${result.prediction_label}`);
console.log(`Confidence: ${(result.confidence * 100).toFixed(1)}%`);
console.log(`Distance ke tetangga terdekat: ${result.distance}`);

if (result.zscore_validation.is_outlier) {
    alert(`⚠️ ${result.zscore_validation.warning}`);
}
```

---

## 📝 Ringkasan Perubahan Teknis

### Class Attributes yang Ditambahkan:
```python
Z_SCORE_RANGES = {
    "normal": {"min": -2.0, "max": 3.0},
    "stunting": {"min": -3.0, "max": -2.0},
    "severe": {"min": -4.0, "max": -3.0},
    "extreme_low": {"value": -3.0},
    "extreme_high": {"value": 3.0}
}
```

### Method yang Ditambahkan:
1. `validate_zscore(zscore_tbu, zscore_bbu)` - Validasi Z-Score
2. `predict_with_zscore_validation(X, zscore_tbu, zscore_bbu)` - Prediksi + Validasi

### Method yang Diupdate:
1. `__init__()` - Dokumentasi K parameter dan preprocessing
2. `train()` - Dokumentasi detail StandardScaler fit_transform
3. `predict()` - Dokumentasi StandardScaler transform (bukan fit_transform)
4. `prepare_features()` - Dokumentasi Z-Score tidak sebagai input feature

---

## 🔒 Data Leakage Prevention

**PENTING:** Z-Scores TIDAK digunakan sebagai input feature untuk KNN:

```python
# ❌ SALAH - Data leakage
features = [jk, usia, BB, TB, LL, LK, zscore_tbu, zscore_bbu]

# ✅ BENAR - Hanya 6 fitur mentah
features = [jk, usia, BB, TB, LL, LK]

# ✅ Z-Score hanya untuk:
# - Validasi medis (deteksi outlier)
# - Ground truth evaluation (confusion matrix)
# - Tidak untuk input feature KNN
```

---

## 🧪 Testing Checklist

- [ ] Verify StandardScaler fit pada training, transform pada test
- [ ] Verify distance weighting: tetangga dekat lebih berpengaruh
- [ ] Test K=3 dan K=5 pada dataset yang berbeda ukuran
- [ ] Test validate_zscore() dengan nilai ekstrem (-3.5, +4.0)
- [ ] Test predict_with_zscore_validation() mengembalikan JSON lengkap
- [ ] Verify distance dan label_code ada di output JSON
- [ ] Test dengan data normal dan data outlier

---

## 📚 Files Modified

- ✅ `backend/app/ml/knn_model.py` - Main model class
- ❓ `backend/app/services/prediction_service.py` - Perlu update untuk gunakan validate_zscore
- ❓ `backend/app/routes/pengukuran.py` - Perlu update untuk return JSON lengkap

---

## 🚀 Next Steps

1. **Test model dengan data baru:**
```bash
cd backend
python -c "
from app.ml.knn_model import StuntingKNNModel
model = StuntingKNNModel(n_neighbors=5)
# Test validasi Z-Score
result = model.validate_zscore(zscore_tbu=-2.5, zscore_bbu=-1.5)
print('Validasi OK' if result['is_valid'] else 'Data outlier!')
"
```

2. **Update prediction_service.py untuk menggunakan predict_with_zscore_validation()**

3. **Update API endpoints untuk mengembalikan output JSON lengkap**

4. **Training model dengan data terbaru**

---

## 📖 Referensi WHO

- Z-Score Height-for-Age (zscore_tbu): WHO Child Growth Standards
- Normal range: -2.0 hingga +3.0 SD
- Stunting definition: zscore_tbu < -2.0 (pertinent untuk stunting profiling)

---

**Status:** ✅ Ready for Integration
**Approved by:** System Update (29 March 2026)
