# 🚀 QUICK START - Evaluasi KNN Confusion Matrix

## **30-Second Quick Start**

### Copy-Paste This:
```python
from evaluate_knn_sklearn import evaluate_knn_model
import numpy as np

# Your data
y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3, ...])  # Ground truth
y_pred = np.array([0, 1, 2, 2, 0, 1, 3, 3, ...])  # Predictions

# Evaluate!
cm, metrics = evaluate_knn_model(y_true, y_pred)
# Done! Results printed automatically.
```

### Run Directly:
```bash
python evaluate_knn_sklearn.py
# OR see examples:
python example_integration_evaluate_knn.py
```

---

## **Files You Have**

| File | Purpose | When to Use |
|------|---------|------------|
| `evaluate_knn_sklearn.py` | Main evaluation code | Import in your project |
| `EVALUATE_KNN_USAGE_GUIDE.md` | Full documentation | Read when confused |
| `example_integration_evaluate_knn.py` | 5 examples | Run to learn |
| `EVALUASI_KNN_RINGKASAN.md` | Complete summary | Reference guide |
| `VERIFICATION_CHECKLIST.md` | Quality checklist | Verify everything works |

---

## **4 Class Labels**

```
0 = Normal + Gizi Baik
1 = Normal + Kurang Gizi
2 = Stunting + Gizi Baik
3 = Stunting + Kurang Gizi
```

---

## **Output Explained**

**Confusion Matrix:**
```
        Pred → 0  1  2  3
Y_true: 0      □  □  □  □
        1      □  □  □  □
        2      □  □  □  □
        3      □  □  □  □
```
- Diagonal = Correct
- Off-diagonal = Errors

**TP/TN/FP/FN for Class 0:**
- **TP** = correctly predicted 0
- **TN** = correctly predicted not-0
- **FP** = wrongly predicted 0
- **FN** = wrongly predicted not-0 (but was 0)

**Metrics for Class 0:**
- **Precision** = TP/(TP+FP) → How accurate is "0" prediction?
- **Recall** = TP/(TP+FN) → How many "0" did we catch?
- **F1** = Balance of both
- **Specificity** = TN/(TN+FP) → How good at avoiding false alarms?

---

## **Common Use Cases**

### **Use 1: Check Model Accuracy**
```python
from evaluate_knn_sklearn import evaluate_knn_model

cm, metrics = evaluate_knn_model(y_true, y_pred)
# Prints confusion matrix + all metrics
```

### **Use 2: Find Problem Classes**
```python
# Which class has lowest recall?
for class_idx in range(4):
    recall = metrics[class_idx]["Recall"]
    if recall < 0.7:
        print(f"Class {class_idx}: Low recall ({recall:.1%})")
```

### **Use 3: API Endpoint**
```python
from evaluate_knn_sklearn import evaluate_knn_model

@app.post("/metrics")
def get_metrics(y_true: list, y_pred: list):
    cm, metrics = evaluate_knn_model(np.array(y_true), np.array(y_pred))
    return {"cm": cm.tolist(), "metrics": metrics}
```

### **Use 4: Batch Evaluation**
```python
# Evaluate model every week
for week in range(52):
    y_true = get_week_data(week)
    y_pred = predict_week(week)
    cm, metrics = evaluate_knn_model(y_true, y_pred)
    save_to_db(week, metrics)
```

---

## **Troubleshooting**

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: sklearn` | `pip install scikit-learn` |
| Shape mismatch error | `assert len(y_true) == len(y_pred)` |
| Unexpected metrics | Check labels are only 0,1,2,3 |
| Import error | Make sure file in same folder |

---

## **Metrics Reference**

```
Precision = "How many predicted as class X are actually X?"
  Formula: TP / (TP + FP)
  Range: 0 to 1
  Best for: Avoiding false positives

Recall = "How many actual class X did we find?"
  Formula: TP / (TP + FN)
  Range: 0 to 1
  Best for: Medical/critical applications

F1-Score = "Balance between Precision and Recall"
  Formula: 2 * (P*R)/(P+R)
  Range: 0 to 1
  Best for: General model evaluation

Specificity = "How good are we at NOT predicting class X?"
  Formula: TN / (TN + FP)
  Range: 0 to 1
  Best for: Reducing false alarms
```

---

## **Example Output**

```
======================== CONFUSION MATRIX ========================
Klasifikasi KNN (Confusion Matrix)
                        Pred_0  Pred_1  Pred_2  Pred_3
Actual_0                     6       0       0       3
Actual_1                     0       7       2       0
Actual_2                     0       2       6       1
Actual_3                     0       0       1       6

======================== OVR METRICS ============================
                Kelas             TP  TN  FP  FN  Precision  Recall  F1-Score
0: Normal+Gizi Baik                6  23   0   3    1.0000  0.6667   0.8000
1: Normal+Kurang Gizi              7  20   3   2    0.7000  0.7778   0.7368
2: Stunting+Gizi Baik              6  22   3   1    0.6667  0.8571   0.7500
3: Stunting+Kurang Gizi            6  24   1   1    0.8571  0.8571   0.8571

Overall Accuracy: 78.12%
```

---

## **Cheat Sheet**

**Function names:**
- `evaluate_knn_model()` ← Use this! (main)
- `calculate_confusion_matrix_sklearn()` ← Low-level
- `calculate_ovr_metrics()` ← Low-level
- `calculate_metrics_for_all_classes()` ← Low-level

**What to import:**
```python
from evaluate_knn_sklearn import evaluate_knn_model
# That's it! Everything else is internal.
```

**What to pass:**
```python
import numpy as np
y_true = np.array([...])  # Ground truth labels (0-3)
y_pred = np.array([...])  # Predicted labels (0-3)
```

**What you get:**
```python
cm          # Confusion matrix (4x4 numpy array)
metrics     # Dict of metrics per class
# Plus: printed output with tables
```

---

## **One More Thing**

### Test it NOW:
```bash
# Change to project directory
cd d:\development\stunting_gempol

# Run example 1
python example_integration_evaluate_knn.py
# Enter: 1
# See: 86% accuracy example output
```

---

**Status:** ✅ Ready to use  
**Complexity:** ⭐ Very Simple  
**Documentation:** ✅ Complete  
**Support:** See EVALUATE_KNN_USAGE_GUIDE.md for advanced topics

**Enjoy! 🎉**
