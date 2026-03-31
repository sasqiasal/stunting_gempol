import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_score, recall_score, f1_score

# Load data terbaru
df = pd.read_csv('data_latih_stunting.csv')

print('='*70)
print('RETRAIN MODEL KNN DENGAN DATASET TERBARU')
print('='*70)
print()

print('1. DATA SUMMARY')
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

print()
print('2. PREPARE FEATURES & LABELS')
print('-'*70)

X = df.drop('status_stunting', axis=1)
y = df['status_stunting']

print(f'Features shape: {X.shape}')
print(f'Labels shape: {y.shape}')

# Normalisasi/Standardisasi
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print('\nScaler fitted dan X distandarisasi')

print()
print('3. TRAIN-TEST SPLIT (80-20)')
print('-'*70)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f'Training set: {len(X_train)} samples')
print(f'Test set: {len(X_test)} samples')

print('\nDistribusi train set:')
for label in sorted(np.unique(y_train)):
    count = (y_train == label).sum()
    pct = (count / len(y_train)) * 100
    print(f'  Label {label}: {count:3d} ({pct:5.2f}%)')

print('\nDistribusi test set:')
for label in sorted(np.unique(y_test)):
    count = (y_test == label).sum()
    pct = (count / len(y_test)) * 100
    print(f'  Label {label}: {count:3d} ({pct:5.2f}%)')

print()
print('4. TRAIN KNN MODEL (K=5)')
print('-'*70)

model = KNeighborsClassifier(n_neighbors=5, metric='euclidean', weights='distance')
model.fit(X_train, y_train)

print('✓ Model KNN (K=5) sudah dilatih')

print()
print('5. EVALUASI MODEL')
print('-'*70)

# Predictions
y_pred = model.predict(X_test)

# Metrics
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

print(f'\nOVERALL METRICS:')
print(f'  Accuracy:  {acc*100:6.2f}%')
print(f'  Precision: {prec*100:6.2f}%')
print(f'  Recall:    {rec*100:6.2f}%')
print(f'  F1-Score:  {f1*100:6.2f}%')

print()
print('Confusion Matrix:')
cm = confusion_matrix(y_test, y_pred)
print('        Predicted: Cls0  Cls1  Cls2  Cls3')
for i, row in enumerate(cm):
    print(f'Actual Cls{i}:     {row[0]:4d}  {row[1]:4d}  {row[2]:4d}  {row[3]:4d}')

print()
print('Per-Class Metrics:')
print('-'*70)
print(classification_report(y_test, y_pred, 
                          target_names=[class_names[i] for i in range(4)],
                          zero_division=0))

print()
print('6. SAVE MODEL')
print('-'*70)

# Save model
with open('knn_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print('✓ Model disimpan ke: knn_model.pkl')

# Save scaler
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print('✓ Scaler disimpan ke: scaler.pkl')

# Save feature names
feature_names = X.columns.tolist()
with open('feature_names.pkl', 'wb') as f:
    pickle.dump(feature_names, f)
print('✓ Feature names disimpan ke: feature_names.pkl')

print()
print('='*70)
print('✓ RETRAIN SELESAI!')
print('='*70)
