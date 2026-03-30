# Perbaikan Sistem Evaluasi Model - Phase 2 Complete

## Problem Statement
**User Issue:** "Sistem langsung menampilkan Total Data Evaluasi = 100 dengan TP = 50 dan TN = 50, padahal saya baru melakukan 1 pengukuran"

**Root Cause:** Evaluasi dihitung dari training data CSV (500 sampel untuk training, ~100 untuk testing) bukan dari data pengukuran real yang tersimpan di database Supabase.

**Expected Behavior:** Sistem harus menampilkan metriks evaluasi berdasarkan pengukuran actual:
- Jika 1 pengukuran → total evaluasi = 1
- Jika 10 pengukuran → total evaluasi = 10
- dst.

---

## Solution Implemented

### 1. Backend: `/api/app/routes/evaluasi.py`

#### New Function: `calculate_confusion_matrix_from_measurements(supabase_client)`
```python
def calculate_confusion_matrix_from_measurements(supabase_client) -> Dict[str, Any]:
    """
    Hitung confusion matrix dari data pengukuran REAL di database, bukan dari CSV training
    
    Ground Truth: zscore_tbu < -2.0 (WHO standard untuk stunting)
    Predictions: status_gizi_label dari hasil KNN classification
    Classification: Binary (Normal vs Stunting)
    """
```

**Mekanisme:**
1. Query ALL pengukuran dari tabel Supabase
2. Extract zscore_tbu → ground truth (1 jika < -2.0, 0 otherwise)
3. Extract status_gizi_label → prediction (1 jika label 2,3, 0 jika label 0,1)
4. Calculate binary confusion matrix
5. Compute metrics: accuracy, precision, recall, specificity, f1-score

**Key Features:**
- ✅ Handles zero measurements gracefully
- ✅ Includes extensive logging for debugging
- ✅ Error handling with null checks
- ✅ Returns both confusion matrix and calculated metrics

#### New Endpoint: `GET /evaluasi/real-performance`
```
Authorization: Admin/Kader role required
Response: {
  "status": "success",
  "measurements_count": N,
  "confusion_matrix": {
    "tp": int,
    "tn": int,
    "fp": int,
    "fn": int
  },
  "metrics": {
    "accuracy": float,
    "accuracy_percentage": int,
    "precision": float,
    "precision_percentage": int,
    "recall": float,
    "recall_percentage": int,
    "specificity": float,
    "specificity_percentage": int,
    "f1_score": float,
    "f1_score_pct": int
  },
  "data_source": "Database pengukuran (ground truth: zscore_tbu < -2.0)"
}
```

**Graceful Handling:**
```json
{
  "status": "warning",
  "measurements_count": 0,
  "message": "Belum ada data pengukuran dalam database",
  "data_source": "Database pengukuran (ground truth: zscore_tbu < -2.0)"
}
```

### 2. Frontend: `src/services/evaluasiService.js`

#### New Function: `getRealPerformance()`
```javascript
export const getRealPerformance = async () => {
  /**
   * Fetch evaluasi dari data pengukuran real
   * Total data evaluasi = jumlah pengukuran yang ada di database
   */
  const response = await api.get(`/evaluasi/real-performance`);
  return response;
};
```

### 3. Frontend: `src/pages/EvaluasiModelPage.jsx`

#### New State
```javascript
const [realPerformanceData, setRealPerformanceData] = useState(null);
const [performanceTab, setPerformanceTab] = useState("model"); // "model" | "real"
```

#### New Component: `renderRealPerformanceMetrics()`
- Displays info card dengan data sumber dan performa
- Shows confusion matrix dari real measurements (TP/TN/FP/FN)
- Displays all metrics (accuracy, precision, recall, specificity, F1-score)
- Shows actual measurement count in database

#### New UI: Performance Tab Switch
```
📊 Model Training (K-Comparison)  [ACTIVE]
🏥 Real Pengukuran (Database)     
        ↑ User can switch between these two evaluations
```

**Tab Content:**
- **Model Training:** K-comparison (K=3,5,7,9) dari CSV training data
- **Real Pengukuran:** Evaluasi dari actual measurements di database

#### Data Fetching
```javascript
const [modelData, realData] = await Promise.all([
  getModelPerformance(),
  getRealPerformance()
]);
```

---

## Ground Truth Mechanism

### WHO Standard Stunting Detection
```
zscore_tbu (Height-for-Age Z-Score) < -2.0 → Stunting (1)
zscore_tbu >= -2.0 → Normal (0)
```

### 4-Class to Binary Mapping
```
Class 0 (Normal + Gizi Baik)         → Binary 0 (Normal)
Class 1 (Normal + Kurang Gizi)       → Binary 0 (Normal)
Class 2 (Stunting + Gizi Baik)       → Binary 1 (Stunting)
Class 3 (Stunting + Kurang Gizi)     → Binary 1 (Stunting)
```

### Data Sources
```
┌─────────────────────────────────────────┐
│ TRAINING (Model Development)            │
├─────────────────────────────────────────┤
│ Source: data_latih_stunting.csv          │
│ Samples: 500 total                       │
│ Test split: ~100 samples for evaluation  │
│ Used for: K-comparison analysis          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ PRODUCTION (Real Performance)            │
├─────────────────────────────────────────┤
│ Source: pengukuran table (Supabase)      │
│ Samples: N (actual measurements)         │
│ Ground truth: zscore_tbu < -2.0 (WHO)   │
│ Used for: Dashboard medical accuracy     │
└─────────────────────────────────────────┘
```

---

## Testing

### Manual Testing
```bash
# Test script tersedia di:
python test_real_performance.py

# Atau menggunakan curl:
curl -X GET http://localhost:8000/evaluasi/real-performance \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Expected Output
```
✅ Fetched N measurements from database
📊 Data Summary:
   Total measurements: N
   Actual stunting: X (Y%)
   Predicted stunting: X (Y%)
📊 Confusion Matrix (Binary: Normal vs Stunting):
   Rows=Actual, Cols=Predicted
     Normal  Stunt
Norm TN      FP
Stun FN      TP
📊 Metrics:
   TP=X, TN=X, FP=X, FN=X
   Accuracy: XYZ%, Precision: XYZ%, Recall: XYZ%, F1: XYZ%
```

---

## Behavioral Changes

### Before (Phase 1)
```
Dashboard Evaluasi:
┌─────────────────────────────┐
│ Total Data Evaluasi: 100    │ ← FIXED (dari CSV test set)
│ TP: 50, TN: 50, FP: 0, FN: 0│
│                             │
│ (Ini tetap sama walau user  │
│  baru input 1 pengukuran)   │
└─────────────────────────────┘
```

### After (Phase 2)
```
Dashboard Evaluasi:
┌──────────────────────────────┐
│ 📊 Model Training            │  ← Click to switch
│ 🏥 Real Pengukuran  [ACTIVE] │
├──────────────────────────────┤
│ Total Pengukuran: 1          │ ← VARIABLE (dari database)
│ TP: 0, TN: 1, FP: 0, FN: 0   │
│                              │
│ (Merupakan evaluasi actual   │
│  dari 1 pengukuran user)     │
└──────────────────────────────┘

[Klik "Model Training" untuk lihat K-comparison]
```

---

## Key Architectural Changes

### Separation of Concerns
```
BEFORE:
  Dashboard → /evaluasi/model-performance → CSV Training Data
  
AFTER:
  Dashboard → /evaluasi/model-performance → CSV Training Data (unchanged)
           → /evaluasi/real-performance → Database Measurements (NEW)
  
USER SEES: Two separate evaluation views, can switch between them
```

### Data Isolation
```
Training Metrics (K-Comparison):
  - Fixed dataset: 500 samples CSV
  - Purpose: Model development & optimization
  - Data stable: doesn't change with new measurements

Real Performance Metrics:
  - Dynamic dataset: actual measurements in database
  - Purpose: Medical accuracy reporting
  - Data changes: updates as new measurements added
```

---

## Files Modified

### Backend
- `api/app/routes/evaluasi.py`
  - Added: `calculate_confusion_matrix_from_measurements()` function
  - Added: `GET /evaluasi/real-performance` endpoint

### Frontend
- `src/services/evaluasiService.js`
  - Added: `getRealPerformance()` function
  - Updated: Export statement

- `src/pages/EvaluasiModelPage.jsx`
  - Added: New state variables (realPerformanceData, performanceTab)
  - Added: Fetch logic for getRealPerformance()
  - Added: `renderRealPerformanceMetrics()` function
  - Added: Performance tab switch UI
  - Added: Conditional rendering based on performanceTab
  - Modified: Data fetching to use Promise.all() for parallel requests

---

## Integration Checklist

- [x] Backend function implemented
- [x] Backend endpoint created
- [x] Frontend service function added
- [x] Frontend state variables configured
- [x] Frontend UI with performance tabs added
- [x] Error handling for 0 measurements
- [x] Logging for debugging
- [ ] Database has test measurements (depends on user)
- [ ] Complete end-to-end testing with actual data
- [ ] Performance optimization if needed (large datasets)

---

## User Impact

### Positive Changes
✅ Dashboard now shows REAL model performance on actual measurements
✅ Total count matches actual data in system (1 measurement = 1 evaluated)
✅ Ground truth based on WHO standard (zscore_tbu < -2.0)
✅ Can compare training metrics vs. production metrics
✅ Medical staff sees accurate system reliability

### No Breaking Changes
✅ Model Training metrics still available for developers
✅ K-comparison still works as before
✅ All existing endpoints unchanged
✅ Backward compatible

---

## Next Steps for User

1. **Add Test Data:** Create pengukuran entries in database for testing
2. **View Real Performance:** Go to Evaluasi page → click "Real Pengukuran" tab
3. **Interpret Results:** 
   - TP = model correctly identified stunting
   - TN = model correctly identified normal
   - FP = model false alarm (predicted stunting, was normal)
   - FN = model miss (predicted normal, was stunting)
4. **Monitor:** Track metrics as more measurements are added

---

## Debugging

**Check Backend Logs for:**
```
========== CALCULATING CONFUSION MATRIX FROM REAL MEASUREMENTS ==========
✅ Fetched 5 measurements from database
📊 Data Summary:
   Total measurements: 5
   Actual stunting: 2 (40%)
   Predicted stunting: 2 (40%)
...
```

**In Frontend DevTools (Console):**
```javascript
// Check if getRealPerformance() fetches correctly
window.fetch('/evaluasi/real-performance', {
  headers: { 'Authorization': 'Bearer your-token' }
}).then(r => r.json()).then(console.log)
```

---

## Summary
✅ **Issue Resolved:** Dashboard now evaluates model on REAL measurements, not training data
✅ **Ground Truth:** Using WHO standard (zscore_tbu < -2.0) for stunting detection
✅ **User Expectation Met:** "Jika baru ada 1 pengukuran, maka total evaluasi juga harus 1"
✅ **Backward Compatible:** Existing functionality preserved, new tab added
