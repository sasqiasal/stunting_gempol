# Manual KNN Implementation - Stunting Detection System

## Overview

This document outlines the complete refactoring of the K-Nearest Neighbors (KNN) classification system to use **manual implementations** instead of scikit-learn or any ML libraries.

### What Changed

**Before:** Project used `sklearn.neighbors.KNeighborsClassifier` and `sklearn.preprocessing.StandardScaler`

**After:** Complete manual implementation with:
- ✅ Manual Euclidean Distance calculation
- ✅ Manual Z-score normalization (StandardScaler)
- ✅ Manual K-Nearest Neighbors search
- ✅ Manual majority voting for classification
- ✅ Manual confusion matrix calculation
- ✅ Manual metrics calculation (Accuracy, Precision, Recall, Specificity, F1-Score)

---

## Architecture

### 1. **Manual Implementation Module** (`app/ml/knn_manual.py`)

#### Classes

##### `ManualStandardScaler`
Implements Z-score normalization manually without sklearn.

```python
from app.ml.knn_manual import ManualStandardScaler
import numpy as np

# Initialize scaler
scaler = ManualStandardScaler()

# Fit and transform training data
X_train_scaled = scaler.fit_transform(X_train)

# Transform test data
X_test_scaled = scaler.transform(X_test)
```

**Algorithm:**
```
For each feature:
  z = (x - mean) / std
```

---

##### `ManualKNNClassifier`
Complete KNN implementation without sklearn.

```python
from app.ml.knn_manual import ManualKNNClassifier
import numpy as np

# Initialize with k=5, distance-weighted voting
knn = ManualKNNClassifier(n_neighbors=5, weights='distance')

# Fit model (stores training data - lazy learning)
knn.fit(X_train_scaled, y_train)

# Make predictions
predictions = knn.predict(X_test_scaled)

# Get probabilities
probabilities = knn.predict_proba(X_test_scaled)

# Calculate accuracy
accuracy = knn.score(X_test_scaled, y_test)

# Find k nearest neighbors
distances, indices = knn.kneighbors(X_test_scaled, n_neighbors=5)
```

**Algorithm:**

For each query point:
1. **Calculate Euclidean Distance** to all training samples
   ```
   distance = sqrt(sum((x_query - x_train)^2))
   ```

2. **Find K Nearest Neighbors** - Sort by distance, take k smallest

3. **Majority Voting**
   - **Uniform weights:** Vote equally (class with most neighbors wins)
   - **Distance weights:** Vote inversely proportional to distance
     ```
     weight = 1 / (distance + epsilon)
     ```

---

#### Functions

##### `calculate_confusion_matrix(y_true, y_pred, labels=None)`
Manual confusion matrix calculation without sklearn.

```python
from app.ml.knn_manual import calculate_confusion_matrix
import numpy as np

y_true = np.array([0, 0, 1, 1, 0, 1])
y_pred = np.array([0, 1, 1, 0, 0, 1])

cm = calculate_confusion_matrix(y_true, y_pred, labels=[0, 1])
```

**Output:**
```
[[TN  FP]
 [FN  TP]]
```

---

##### `calculate_metrics(y_true, y_pred)`
Manual calculation of all classification metrics.

```python
from app.ml.knn_manual import calculate_metrics
import numpy as np

metrics = calculate_metrics(y_true, y_pred)

print(metrics['accuracy'])      # (TP + TN) / Total
print(metrics['precision'])     # TP / (TP + FP)
print(metrics['recall'])        # TP / (TP + FN)
print(metrics['specificity'])   # TN / (TN + FP)
print(metrics['f1_score'])      # 2 * (precision * recall) / (precision + recall)
```

**Returns Dictionary:**
```python
{
    "accuracy": 0.8667,
    "precision": 0.8,
    "recall": 0.8,
    "specificity": 0.9333,
    "f1_score": 0.8,
    "tp": 4,
    "tn": 14,
    "fp": 1,
    "fn": 1,
    "confusion_matrix": array(...)
}
```

---

##### `format_confusion_matrix_table(cm, labels=None)`
Format confusion matrix as readable table.

```python
from app.ml.knn_manual import format_confusion_matrix_table

print(format_confusion_matrix_table(cm))
```

**Output:**
```
============================================================
CONFUSION MATRIX (Manual Calculation)
============================================================
                 Predicted Normal  Predicted Stunting
Actual Normal                   14                   1
Actual Stunting                  1                   4
============================================================
```

---

## 2. **Model Class** (`app/ml/knn_model.py`)

The `StuntingKNNModel` class now uses manual implementations:

```python
from app.ml.knn_model import StuntingKNNModel
import numpy as np

# Create model
model = StuntingKNNModel(n_neighbors=5)

# Train (stores all data for lazy learning)
result = model.train(X_train, y_train)

# Predict
prediction, confidence = model.predict(X_test)

# Find nearest neighbors
neighbors = model.find_nearest_neighbors(X_test, n_neighbors=5)

# Save/Load
model.save_model("model.pkl")  # Uses pickle (NO joblib)
model.load_model("model.pkl")
```

**Key Features:**
- Uses `ManualStandardScaler` for feature scaling
- Uses `ManualKNNClassifier` for classification
- Custom gender weighting (5x boost on gender feature)
- Saves with pickle (no joblib dependency)

---

## 3. **Feature Set**

**Features (6 anthropometric + 1 zscore):**
1. `jenis_kelamin` (0=Perempuan, 1=Laki-laki)
2. `usia_bulan` (Age in months)
3. `tinggi_badan` (Height in cm)
4. `berat_badan` (Weight in kg)
5. `lingkar_lengan` (Upper arm circumference in cm)
6. `lingkar_kepala` (Head circumference in cm)
7. `zscore_bbu` (Weight-for-Age Z-score)

**Target Label:**
- `status_stunting`: 0=Normal, 1=Stunting

---

## 4. **Files Modified**

| File | Changes |
|------|---------|
| `backend/app/ml/knn_manual.py` | ✅ New - Complete manual KNN implementation |
| `api/app/ml/knn_manual.py` | ✅ New - Same as backend |
| `backend/app/ml/knn_model.py` | ✅ Refactored - Uses manual implementations |
| `api/app/ml/knn_model.py` | ✅ Refactored - Uses manual implementations |
| `backend/train_model.py` | ✅ Updated - Comments reflect manual KNN |
| `backend/app/routes/evaluasi.py` | ✅ Refactored - Uses manual metrics |
| `backend/requirements.txt` | ✅ Updated - Removed sklearn, scipy, joblib, threadpoolctl |

---

## 5. **Dependencies Removed**

```
❌ scikit-learn==1.7.2
❌ scipy==1.16.1
❌ joblib==1.5.2
❌ threadpoolctl==3.6.0
```

**Only uses:**
- `numpy` (for array operations)
- `pandas` (for CSV loading)
- `pickle` (standard library - for model serialization)
- `math` (standard library - for sqrt)

---

## 6. **How Manual KNN Works**

### Step-by-Step Example

**Training Phase:**
```python
# Train data
X_train = [[0, 10, 100],
           [1, 20, 200],
           [0, 12, 110]]
y_train = [0, 1, 0]

# Model stores all training data (lazy learning)
model.fit(X_train, y_train)
```

**Prediction Phase (Query: [0.5, 15, 105]):**

**Step 1: Scale Features**
```
Using training data mean/std:
Scaled_query = (query - mean) / std
```

**Step 2: Calculate Euclidean Distances**
```
Distance to sample 1: sqrt((0-0.5)^2 + (10-15)^2 + (100-105)^2)
                    = sqrt(0.25 + 25 + 25) = 7.07
                    
Distance to sample 2: sqrt((1-0.5)^2 + (20-15)^2 + (200-105)^2)
                    = sqrt(0.25 + 25 + 9025) = 95.05
                    
Distance to sample 3: sqrt((0-0.5)^2 + (12-15)^2 + (110-105)^2)
                    = sqrt(0.25 + 9 + 25) = 5.86
```

**Step 3: Find K=3 Nearest Neighbors**
```
Sorted by distance:
1. Sample 3 (distance 5.86) → label 0
2. Sample 1 (distance 7.07) → label 0
3. Sample 2 (distance 95.05) → label 1
```

**Step 4: Majority Voting**
```
Uniform voting: label 0 appears 2 times, label 1 appears 1 time
→ Prediction: 0 (Normal)

Confidence = 2/3 = 0.667
```

---

## 7. **Testing**

Run the test script to verify all manual implementations:

```bash
cd /path/to/stunting_gempol
python test_manual_knn.py
```

**Test Coverage:**
- ✅ Manual StandardScaler (Z-score normalization)
- ✅ Euclidean Distance calculation
- ✅ KNN Classification (uniform and distance weighting)
- ✅ Confusion Matrix (manual calculation)
- ✅ Metrics (Accuracy, Precision, Recall, Specificity, F1)

---

## 8. **Training the Model**

```bash
cd backend
python train_model.py
```

**Output:** `backend/app/ml/models/knn_stunting_model.pkl`

---

## 9. **API Endpoints**

### Evaluate Model Performance
```
GET /api/v1/evaluasi/model-performance
```

Returns:
- Confusion Matrix
- Accuracy, Precision, Recall, Specificity, F1-Score
- Nearest Neighbors explanation

### Compare K Values
```
GET /api/v1/evaluasi/compare-k-values
```

Evaluates k=3, 5, 7, 9 and recommends best K based on F1-Score.

---

## 10. **Performance Characteristics**

### Time Complexity
- **Training:** O(1) - just stores data (lazy learning)
- **Prediction:** O(n × m) where n=training samples, m=features
  - Calculates distance to all training samples: O(n × m)
  - Sorts distances: O(n log n)
  - Voting: O(k)

### Space Complexity
- O(n × m) - stores entire training set

### Advantages
✅ No external ML library dependencies
✅ Simple, transparent, auditable code
✅ Easy to understand and modify
✅ Perfect for embedded or constrained environments

### Disadvantages
⚠️ Slower for large datasets (no optimizations like KD-trees)
⚠️ Cannot handle very high-dimensional data efficiently

---

## 11. **Customization**

### Change K (Number of Neighbors)

```python
from app.ml.knn_model import StuntingKNNModel

model = StuntingKNNModel(n_neighbors=7)  # Default is 5
```

### Change Weighting Scheme

In `knn_manual.py`:
```python
# Uniform voting (all neighbors equal weight)
knn = ManualKNNClassifier(n_neighbors=5, weights='uniform')

# Distance-weighted voting (closer neighbors have more weight)
knn = ManualKNNClassifier(n_neighbors=5, weights='distance')
```

### Custom Gender Weighting

In `StuntingKNNModel._apply_custom_weights()`:
```python
# Current: 5x boost on gender feature
X_weighted[:, 0] *= 5.0

# Change to different multiplier:
X_weighted[:, 0] *= 10.0  # Stronger gender separation
X_weighted[:, 0] *= 2.0   # Weaker gender separation
```

---

## 12. **Troubleshooting**

### Issue: Model predictions are inconsistent

**Cause:** Gender weighting not applied during prediction
**Solution:** Ensure `_apply_custom_weights()` is called in `predict()`

### Issue: Low accuracy

**Cause:** K value too high/low for dataset
**Solution:** Use `/evaluasi/compare-k-values` endpoint to test k=3,5,7,9

### Issue: Memory issues with large datasets

**Cause:** Manual KNN stores all training data (lazy learning)
**Solution:** Consider using mini-batch training or feature selection

---

## 13. **Code Examples**

### Complete Training Pipeline

```python
import numpy as np
import pandas as pd
from app.ml.knn_model import StuntingKNNModel
from app.ml.knn_manual import calculate_metrics

# 1. Load data
df = pd.read_csv("data_latih_stunting.csv")

# 2. Prepare features and target
features = df[['jenis_kelamin', 'usia_bulan', 'tinggi_badan', 
               'berat_badan', 'lingkar_lengan', 'lingkar_kepala', 
               'zscore_bbu']].values
target = df['status_stunting'].values

# 3. Create and train model
model = StuntingKNNModel(n_neighbors=5)
result = model.train(features, target)
print(f"Training Accuracy: {result['train_accuracy']}")

# 4. Save model
model.save_model("model.pkl")

# 5. Predict new sample
new_sample = np.array([[1, 24, 75.5, 12.3, 16.2, 46.5, -0.5]])
prediction, confidence = model.predict(new_sample)
print(f"Prediction: {['Normal', 'Stunting'][prediction]}")
print(f"Confidence: {confidence:.2%}")
```

### Evaluation Pipeline

```python
from app.ml.knn_manual import calculate_metrics, format_confusion_matrix_table

# Predictions
y_true = np.array([0, 0, 1, 1, 0, 1])
y_pred = np.array([0, 1, 1, 0, 0, 1])

# Calculate metrics
metrics = calculate_metrics(y_true, y_pred)

# Print results
print(format_confusion_matrix_table(metrics['confusion_matrix']))
print(f"Accuracy: {metrics['accuracy']:.2%}")
print(f"Precision: {metrics['precision']:.2%}")
print(f"Recall: {metrics['recall']:.2%}")
print(f"F1-Score: {metrics['f1_score']:.4f}")
```

---

## 14. **Summary of Benefits**

✅ **No External ML Libraries** - Only uses numpy, pandas, pickle
✅ **Transparent Algorithm** - Easy to understand and audit
✅ **Light Weight** - Minimal dependencies
✅ **Portable** - Can run anywhere Python runs
✅ **Maintainable** - All code is in-project
✅ **Educational** - Great for learning KNN algorithm
✅ **Production Ready** - Fully tested and documented

---

**Last Updated:** March 2026
**Status:** ✅ Production Ready
**License:** Follow project license
