import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

df = pd.read_csv('data_latih_stunting.csv')

print('='*70)
print('ANALISIS: Mengapa Akurasi KNN Tidak Optimal?')
print('='*70)
print()

# 1. Check feature overlap between classes
print('1. ANALISIS RANGE FITUR PER KELAS')
print('-'*70)
for label in sorted(df['status_stunting'].unique()):
    class_names = {0: 'Normal + Gizi Baik', 1: 'Normal + Kurang Gizi', 
                   2: 'Stunting + Gizi Baik', 3: 'Stunting + Kurang Gizi'}
    print(f'\nKELAS {label}: {class_names[label]}')
    subset = df[df['status_stunting'] == label]
    for col in ['berat_badan', 'tinggi_badan', 'lingkar_lengan', 'lingkar_kepala']:
        min_val = subset[col].min()
        max_val = subset[col].max()
        mean_val = subset[col].mean()
        std_val = subset[col].std()
        print(f'  {col:18s}: {min_val:6.2f} - {max_val:6.2f} (mean={mean_val:6.2f}, std={std_val:5.2f})')

print()
print('2. FEATURE IMPORTANCE - Seberapa Prediktif Setiap Fitur?')
print('-'*70)

X = df.drop('status_stunting', axis=1)
y = df['status_stunting']

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, 
                                                      random_state=42, stratify=y)

feature_names = X.columns.tolist()

# All features
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
acc_all = knn.score(X_test, y_test)
print(f'\nAkurasi KNN (K=5):')
print(f'  Semua 6 fitur: {acc_all*100:.2f}%')

print()
print('3. CLASS OVERLAP - Pusat Setiap Kelas')
print('-'*70)

class_centers = df.groupby('status_stunting')[['berat_badan', 'tinggi_badan', 
                                                'lingkar_lengan', 'lingkar_kepala']].mean()

print('\nPusat kelas (centroid):')
for idx, row in class_centers.iterrows():
    class_names = {0: 'Normal + Gizi Baik', 1: 'Normal + Kurang Gizi', 
                   2: 'Stunting + Gizi Baik', 3: 'Stunting + Kurang Gizi'}
    bb = row['berat_badan']
    tb = row['tinggi_badan']
    ll = row['lingkar_lengan']
    lk = row['lingkar_kepala']
    print(f'Kelas {idx}: {class_names[idx]:<25s}')
    print(f'          BB={bb:5.1f}kg, TB={tb:6.1f}cm, LL={ll:5.1f}cm, LK={lk:5.1f}cm')

print()
print('4. CONFUSION MATRIX pada TEST SET')
print('-'*70)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)

cm = confusion_matrix(y_test, y_pred)

print('\nConfusion Matrix (Actual vs Predicted):')
print('        Predicted: Cls0  Cls1  Cls2  Cls3')
for i, row in enumerate(cm):
    print(f'Actual Cls{i}:     {row[0]:4d}  {row[1]:4d}  {row[2]:4d}  {row[3]:4d}')

print()
acc_overall = knn.score(X_test, y_test)
print(f'Overall Accuracy: {acc_overall*100:.2f}%')
print()
print('Per-Class Recall (Sensitivity):')
for i in range(4):
    if cm[i].sum() > 0:
        recall = cm[i, i] / cm[i].sum()
        print(f'  Class {i}: {recall*100:6.2f}%')

print()
print('5. MASALAH UTAMA YANG DITEMUKAN:')
print('-'*70)
print()

# Find the problematic class pairs
misclassified = []
for i in range(4):
    for j in range(4):
        if i != j and cm[i, j] > 0:
            misclassified.append((i, j, cm[i, j]))

misclassified.sort(key=lambda x: x[2], reverse=True)

if misclassified:
    print('Kesalahan klasifikasi terbesar:')
    for actual, predicted, count in misclassified[:5]:
        class_names = {0: 'Normal + Gizi Baik', 1: 'Normal + Kurang Gizi', 
                       2: 'Stunting + Gizi Baik', 3: 'Stunting + Kurang Gizi'}
        print(f'  - Kelas {actual} ({class_names[actual]}) sering disalahkan sebagai Kelas {predicted} ({count}x)')

print()
print('✓ Penyebab Akurasi Tidak Optimal:')
print('  1. OVERLAP FITUR: Range fitur antar kelas sangat tumpang tindih')
print('  2. KELAS SULIT DIBEDAKAN: Terutama kelas 1 vs kelas 3 memiliki nilai sangat mirip')
print('  3. KNN MEMBUTUHKAN FITUR DISKRIMINATIF: Fitur yang ada terlalu overlap')
print('  4. MASALAH DATA LABEL: Mungkin ada kesalahan labeling di dataset')
