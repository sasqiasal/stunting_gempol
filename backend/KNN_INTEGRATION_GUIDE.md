# 🔧 KNN Model Integration Guide

## Quick Start - Implementasi Lengkap

### 1. Import Model
```python
from app.ml.knn_model import StuntingKNNModel, get_knn_model

# Opsi 1: Gunakan instance global
model = get_knn_model()

# Opsi 2: Buat instance baru dengan K custom
model = StuntingKNNModel(n_neighbors=3)  # untuk dataset kecil
```

### 2. Training Model
```python
import pandas as pd
import numpy as np

# Baca data training
df = pd.read_csv('data_latih_stunting.csv')

# Siapkan features dan target
X = df[['jenis_kelamin', 'usia_bulan', 'berat_badan', 'tinggi_badan', 
         'lingkar_lengan', 'lingkar_kepala']].values
y = df['status_stunting'].values

# Training
result = model.train(X, y)
print(f"✓ Training complete: {result}")

# Simpan model
model.save_model('app/ml/models/knn_stunting_model.pkl')
```

### 3. Prediksi Dengan Validasi Z-Score

#### Option A: Simple Prediction (existing)
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

# Prediksi (tanpa validasi Z-Score)
prediction, confidence = model.predict(features)
print(f"Prediksi: {model.CLASS_LABELS[prediction]}")
print(f"Confidence: {confidence}")
```

#### Option B: Prediksi Dengan Validasi Z-Score (REKOMENDASI) ✓
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

# Prediksi + Validasi Z-Score
result = model.predict_with_zscore_validation(
    X=features,
    zscore_tbu=-2.1,
    zscore_bbu=-1.0
)

# Print hasil
print(json.dumps(result, indent=2))

# Handle outliers
if result["zscore_validation"]["is_outlier"]:
    print(f"⚠️ WARNING: {result['zscore_validation']['warning']}")
    # Flag untuk verifikasi manual di UI
else:
    print(f"✓ Prediksi: {result['prediction_label']}")
```

---

## 📋 Prediction Service Integration

**File:** `backend/app/services/prediction_service.py`

### Before (Existing)
```python
def make_prediction(jenis_kelamin, usia_bulan, tinggi_badan, ...):
    model = get_knn_model()
    features = model.prepare_features(...)
    prediction, confidence = model.predict(features)
    
    return {
        "status_stunting": prediction,
        "confidence": confidence
    }
```

### After (Updated dengan Validasi Z-Score)
```python
def make_prediction(
    jenis_kelamin, usia_bulan, tinggi_badan, berat_badan,
    lingkar_lengan, lingkar_kepala, 
    zscore_tbu=0.0, zscore_bbu=0.0
):
    model = get_knn_model()
    
    # Persiapan fitur
    features = model.prepare_features(
        jenis_kelamin=jenis_kelamin,
        usia_bulan=usia_bulan,
        tinggi_badan=tinggi_badan,
        berat_badan=berat_badan,
        lingkar_lengan=lingkar_lengan,
        lingkar_kepala=lingkar_kepala,
        zscore_tbu=zscore_tbu,
        zscore_bbu=zscore_bbu
    )
    
    # ✅ Prediksi dengan validasi Z-Score
    result = model.predict_with_zscore_validation(
        X=features,
        zscore_tbu=zscore_tbu,
        zscore_bbu=zscore_bbu
    )
    
    # Tambahkan distance dari nearest neighbors
    neighbors = model.find_nearest_neighbors(features, n_neighbors=3)
    if neighbors:
        result["nearest_neighbor_distance"] = neighbors[0]["distance"]
        result["nearest_neighbors"] = neighbors
    
    # ✅ Return hasil JSON lengkap dengan validasi
    return {
        "status_stunting": result["prediction_code"],
        "status_label": result["prediction_label"],
        "confidence": result["confidence"],
        "distance": result.get("nearest_neighbor_distance"),
        "zscore_validation": result["zscore_validation"],
        "model_config": result["model_config"],
        "nearest_neighbors": result.get("nearest_neighbors", [])
    }
```

---

## 🔌 API Routes Integration

**File:** `backend/app/routes/pengukuran.py` atau `backend/app/routes/evaluasi.py`

### Endpoint untuk POST Pengukuran Baru
```python
from fastapi import APIRouter, HTTPException
from app.services.prediction_service import make_prediction
from app.utils.zscore_calculator import ZScoreCalculator

router = APIRouter()

@router.post("/api/pengukuran")
async def create_pengukuran(data: dict):
    """
    POST /api/pengukuran
    
    Body:
    {
        "balita_id": 123,
        "jenis_kelamin": "L",
        "usia_bulan": 24,
        "tinggi_badan": 75.5,
        "berat_badan": 10.2,
        "lingkar_lengan": 16.3,
        "lingkar_kepala": 48.5
    }
    
    Response:
    {
        "pengukuran_id": 456,
        "prediction": {...},
        "zscore_validation": {...},
        "status": "success"
    }
    """
    try:
        # Hitung Z-Score terlebih dahulu
        zscore_calculator = ZScoreCalculator()
        zscore_result = zscore_calculator.calculate(
            jenis_kelamin=data["jenis_kelamin"],
            usia_bulan=data["usia_bulan"],
            tinggi_badan=data["tinggi_badan"],
            berat_badan=data["berat_badan"]
        )
        
        # Lakukan prediksi dengan validasi
        prediction = make_prediction(
            jenis_kelamin=data["jenis_kelamin"],
            usia_bulan=data["usia_bulan"],
            tinggi_badan=data["tinggi_badan"],
            berat_badan=data["berat_badan"],
            lingkar_lengan=data["lingkar_lengan"],
            lingkar_kepala=data["lingkar_kepala"],
            zscore_tbu=zscore_result.get("zscore_tbu", 0.0),
            zscore_bbu=zscore_result.get("zscore_bbu", 0.0)
        )
        
        # Simpan ke database
        pengukuran = {
            "balita_id": data["balita_id"],
            "jenis_kelamin": data["jenis_kelamin"],
            "usia_bulan": data["usia_bulan"],
            "tinggi_badan": data["tinggi_badan"],
            "berat_badan": data["berat_badan"],
            "lingkar_lengan": data["lingkar_lengan"],
            "lingkar_kepala": data["lingkar_kepala"],
            "zscore_tbu": zscore_result.get("zscore_tbu"),
            "zscore_bbu": zscore_result.get("zscore_bbu"),
            "prediksi_stunting": prediction["status_stunting"] in [2, 3],
            "confidence_score": prediction["confidence"]
        }
        
        # Save to DB...
        pengukuran_id = save_pengukuran(pengukuran)
        
        # ✅ Return hasil prediksi dengan validasi
        return {
            "pengukuran_id": pengukuran_id,
            "prediction": prediction,
            "zscore_validation": prediction["zscore_validation"],
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 🔍 Validation Examples

### Example 1: Data Normal
```python
result = model.predict_with_zscore_validation(
    X=features_normal,
    zscore_tbu=-1.5,    # Normal range
    zscore_bbu=-0.8     # Normal range
)

print(result)
# Output:
# {
#     "prediction_code": 1,
#     "prediction_label": "Normal & Kurang Gizi",
#     "confidence": 0.82,
#     "zscore_validation": {
#         "is_valid": True,
#         "is_outlier": False,
#         "status": "NORMAL",
#         "zscore_tbu": -1.5,
#         "zscore_tbu_status": "NORMAL (>= -2.0 SD)"
#     }
# }
```

### Example 2: Data dengan Stunting (Normal untuk dideteksi)
```python
result = model.predict_with_zscore_validation(
    X=features_stunting,
    zscore_tbu=-2.3,    # Stunting range
    zscore_bbu=-1.5     # Underweight
)

print(result)
# Output:
# {
#     "prediction_code": 3,
#     "prediction_label": "Stunting & Kurang Gizi",
#     "confidence": 0.88,
#     "zscore_validation": {
#         "is_valid": True,
#         "is_outlier": False,
#         "status": "NORMAL",
#         "zscore_tbu": -2.3,
#         "zscore_tbu_status": "STUNTING (< -2.0 SD)"
#     }
# }
```

### Example 3: Data Ekstrem (OUTLIER)
```python
result = model.predict_with_zscore_validation(
    X=features_extreme,
    zscore_tbu=3.5,     # ← EKSTREM TINGGI (bayi sangat besar)
    zscore_bbu=4.0      # ← EKSTREM TINGGI
)

print(result)
# Output:
# {
#     "prediction_code": 0,
#     "prediction_label": "Normal & Gizi Baik",
#     "confidence": 0.45,
#     "zscore_validation": {
#         "is_valid": False,
#         "is_outlier": True,
#         "status": "OUTLIER_EXTREME_HIGH",
#         "warning": "⚠️ PERINGATAN MEDIS: Tinggi badan sangat ekstrem tinggi... Bayi mungkin tidak stunting, perlu verifikasi.",
#         "zscore_tbu": 3.5,
#         "zscore_tbu_status": "EXTREME_HIGH (> +3.0 SD)"
#     }
# }
```

### Example 4: Data Ekstrem Rendah (OUTLIER)
```python
result = model.predict_with_zscore_validation(
    X=features_extreme_low,
    zscore_tbu=-3.5,    # ← EKSTREM RENDAH (bayi sangat kecil)
    zscore_bbu=-3.2     # ← EKSTREM RENDAH
)

print(result)
# Output:
# {
#     "prediction_code": 3,
#     "prediction_label": "Stunting & Kurang Gizi",
#     "confidence": 0.75,
#     "zscore_validation": {
#         "is_valid": False,
#         "is_outlier": True,
#         "status": "OUTLIER_EXTREME_LOW",
#         "warning": "⚠️ PERINGATAN MEDIS: Tinggi badan sangat ekstrem rendah... Data perlu verifikasi manual.",
#         "zscore_tbu": -3.5,
#         "zscore_tbu_status": "EXTREME_LOW (< -3.0 SD)"
#     }
# }
```

---

## 🎯 Frontend Integration (React/Vue)

### React Component Example
```jsx
import React, { useState } from 'react';

function PengukuranForm() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (formData) => {
    setLoading(true);
    try {
      const response = await fetch('/api/pengukuran', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      setResult(data);
      
      // Handle outlier case
      if (!data.prediction.zscore_validation.is_valid) {
        alert(`⚠️ PERINGATAN!\n${data.prediction.zscore_validation.warning}`);
      }
      
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {result && (
        <div className="result">
          <h3>{result.prediction.prediction_label}</h3>
          <p>Confidence: {(result.prediction.confidence * 100).toFixed(1)}%</p>
          
          {result.prediction.zscore_validation.is_outlier && (
            <div className="alert alert-warning">
              <strong>⚠️ Data Ekstrem!</strong>
              <p>{result.prediction.zscore_validation.warning}</p>
              <p>Z-Score Tinggi/Usia: {result.prediction.zscore_validation.zscore_tbu} SD</p>
              <button onClick={() => alert('Verifikasi data manual di dashboard admin')}>
                Minta Verifikasi Manual
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## ✅ Testing Checklist

```python
#!/usr/bin/env python
"""Test KNN Model Updates"""

from app.ml.knn_model import StuntingKNNModel

def test_all():
    model = StuntingKNNModel(n_neighbors=5)
    
    # Test 1: StandardScaler
    print("Test 1: StandardScaler...")
    assert model.scaler is not None, "Scaler not initialized"
    print("✓ Scaler initialized")
    
    # Test 2: Distance Weighting
    print("\nTest 2: Distance Weighting...")
    assert model.model.weights == 'distance', "Weights not set to distance"
    print("✓ Weights set to 'distance'")
    
    # Test 3: Z-Score Validation
    print("\nTest 3: Z-Score Validation...")
    validation = model.validate_zscore(zscore_tbu=-1.5, zscore_bbu=-0.8)
    assert validation["is_valid"] == True, "Normal data should be valid"
    assert validation["is_outlier"] == False, "Normal data should not be outlier"
    print("✓ Normal data validation OK")
    
    validation_outlier = model.validate_zscore(zscore_tbu=3.5, zscore_bbu=4.0)
    assert validation_outlier["is_outlier"] == True, "Extreme data should be outlier"
    print("✓ Outlier detection OK")
    
    # Test 4: Prediction with Validation
    print("\nTest 4: Prediction with Validation...")
    try:
        result = model.predict_with_zscore_validation(
            X=[[1, 24, 10.2, 75.5, 16.3, 48.5]],
            zscore_tbu=-2.1,
            zscore_bbu=-1.0
        )
        assert "prediction_code" in result, "Missing prediction_code"
        assert "confidence" in result, "Missing confidence"
        assert "zscore_validation" in result, "Missing zscore_validation"
        assert "model_config" in result, "Missing model_config"
        print("✓ Prediction with validation OK")
        print(f"  - Prediction code: {result['prediction_code']}")
        print(f"  - Confidence: {result['confidence']}")
        print(f"  - Is valid: {result['zscore_validation']['is_valid']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    test_all()
```

---

## 📚 References

### WHO Child Growth Standards
- https://www.who.int/tools/child-growth-standards
- Z-Score Range: -4 to +3 SD
- Stunting definition: zscore_tbu < -2.0 SD

### Scikit-learn KNN
- https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsClassifier.html
- weights='distance' dokumentasi: inverse distance weighting

### StandardScaler
- https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
- Formula: (X - mean) / std

---

**Version:** 1.0
**Updated:** 29 March 2026
**Status:** Ready for Integration
