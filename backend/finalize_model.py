import pandas as pd
import numpy as np
import pickle
import os
import json
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_score, recall_score, f1_score

# Load data terbaru
df = pd.read_csv('data_latih_stunting.csv')

print('='*70)
print('RETRAIN MODEL KNN - FINALIZE & SAVE')
print('='*70)
print()

print('1. DATA PREPARATION')
print('-'*70)
print(f'Total Data: {len(df)} baris')

class_names = {0: 'Normal + Gizi Baik', 1: 'Normal + Kurang Gizi', 
               2: 'Stunting + Gizi Baik', 3: 'Stunting + Kurang Gizi'}

status_dist = df['status_stunting'].value_counts().sort_index()
total = len(df)

for label in sorted(status_dist.index):
    count = status_dist[label]
    percentage = (count / total) * 100
    print(f'  Label {label}: {class_names[label]:<25s} = {count:3d} data ({percentage:5.2f}%)')

X = df.drop('status_stunting', axis=1)
y = df['status_stunting']

# Standarisasi
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print()
print('2. TRAIN MODEL')
print('-'*70)

model = KNeighborsClassifier(n_neighbors=5, metric='euclidean', weights='distance')
model.fit(X_train, y_train)
print('✓ Model KNN (K=5) sudah dilatih')

print()
print('3. EVALUATE ON TEST SET')
print('-'*70)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f'Test Accuracy: {acc*100:.2f}%')

print()
print('4. SAVE MODEL FILES')
print('-'*70)

# Ensure directory exists
os.makedirs('app/ml/models', exist_ok=True)

# Save model
model_path = 'app/ml/models/knn_stunting_model_sklearn.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
print(f'✓ Model disimpan ke: {model_path}')

# Save scaler
scaler_path = 'app/ml/models/scaler_sklearn.pkl'
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
print(f'✓ Scaler disimpan ke: {scaler_path}')

# Save feature names
feature_path = 'app/ml/models/feature_names.pkl'
feature_names = X.columns.tolist()
with open(feature_path, 'wb') as f:
    pickle.dump(feature_names, f)
print(f'✓ Feature names disimpan ke: {feature_path}')

print()
print('5. UPDATE EVALUATION METRICS')
print('-'*70)

# Evaluate all K values on test set
k_values = [3, 5, 7, 9]
k_comparisons = []

for k in k_values:
    knn_k = KNeighborsClassifier(n_neighbors=k, metric='euclidean', weights='distance')
    knn_k.fit(X_train, y_train)
    
    y_pred_k = knn_k.predict(X_test)
    
    acc_k = accuracy_score(y_test, y_pred_k)
    prec_k = precision_score(y_test, y_pred_k, average='weighted', zero_division=0)
    rec_k = recall_score(y_test, y_pred_k, average='weighted', zero_division=0)
    f1_k = f1_score(y_test, y_pred_k, average='weighted', zero_division=0)
    
    k_comparisons.append({
        "k": k,
        "accuracy": round(acc_k, 4),
        "precision": round(prec_k, 4),
        "recall": round(rec_k, 4),
        "f1_score": round(f1_k, 4)
    })
    
    print(f'K={k}: Accuracy={acc_k*100:.2f}%, Precision={prec_k*100:.2f}%, Recall={rec_k*100:.2f}%, F1={f1_k*100:.2f}%')

print()
print('6. COMPUTE CONFUSION MATRIX & METRICS FOR K=5')
print('-'*70)

y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)

print('\nConfusion Matrix:')
print('        Predicted: Cls0  Cls1  Cls2  Cls3')
for i, row in enumerate(cm):
    print(f'Actual Cls{i}:     {row[0]:4d}  {row[1]:4d}  {row[2]:4d}  {row[3]:4d}')

# Per-class metrics
per_class_metrics = []
for i in range(4):
    if cm[i].sum() > 0:
        tp = cm[i, i]
        fn = cm[i, :].sum() - tp
        fp = cm[:, i].sum() - tp
        tn = cm.sum() - tp - fn - fp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        per_class_metrics.append({
            "class_idx": i,
            "class_name": class_names[i],
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(tn),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        })

# Save metrics to JSON
metrics_data = {
    "accuracy": round(acc, 4),
    "accuracy_percentage": round(acc * 100, 2),
    "macro_avg_precision": round(precision_score(y_test, y_pred, average='macro', zero_division=0), 4),
    "macro_avg_precision_percentage": round(precision_score(y_test, y_pred, average='macro', zero_division=0) * 100, 2),
    "macro_avg_recall": round(recall_score(y_test, y_pred, average='macro', zero_division=0), 4),
    "macro_avg_recall_percentage": round(recall_score(y_test, y_pred, average='macro', zero_division=0) * 100, 2),
    "macro_avg_f1": round(f1_score(y_test, y_pred, average='macro', zero_division=0), 4),
    "macro_avg_f1_percentage": round(f1_score(y_test, y_pred, average='macro', zero_division=0) * 100, 2),
    "k_value_used": 5,
    "test_set_size": len(y_test),
    "training_set_size": len(y_train),
    "confusion_matrix_raw": cm.tolist(),
    "per_class_metrics": per_class_metrics,
    "k_comparisons": k_comparisons
}

metrics_path = 'app/ml/models/evaluation_metrics.json'
with open(metrics_path, 'w') as f:
    json.dump(metrics_data, f, indent=2)
print(f'✓ Metrics disimpan ke: {metrics_path}')

print()
print('='*70)
print('✓ MODEL RETRAIN & SAVE SELESAI!')
print('='*70)
print()
print('SUMMARY:')
print(f'  Overall Accuracy: {acc*100:.2f}%')
print(f'  Test Set Size: {len(y_test)} samples')
print(f'  Training Set Size: {len(y_train)} samples')
