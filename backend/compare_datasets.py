import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load both datasets
df_current = pd.read_csv('data_latih_stunting.csv')
df_copy = pd.read_csv('data_latih_stunting copy.csv')

print('='*80)
print('PERBANDINGAN DATASET')
print('='*80)
print()

print('DATASET SAAT INI (data_latih_stunting.csv):')
print('-'*80)
print(f'Total Records: {len(df_current)}')
print(f'Total Fitur: {len(df_current.columns)}')
print()
print('Distribusi Status Stunting:')
class_names = {0: 'Normal + Gizi Baik', 1: 'Normal + Kurang Gizi', 
               2: 'Stunting + Gizi Baik', 3: 'Stunting + Kurang Gizi'}

status_dist = df_current['status_stunting'].value_counts().sort_index()
total_cur = len(df_current)
for label in sorted(status_dist.index):
    count = status_dist[label]
    pct = (count / total_cur) * 100
    name = class_names.get(label, 'Unknown')
    print(f'  Label {label}: {name:<25s} = {count:3d} ({pct:5.1f}%)')

print()
print('DATASET COPY (data_latih_stunting copy.csv):')
print('-'*80)
print(f'Total Records: {len(df_copy)}')
print(f'Total Fitur: {len(df_copy.columns)}')
print()
print('Distribusi Status Stunting:')
status_dist_copy = df_copy['status_stunting'].value_counts().sort_index()
total_copy = len(df_copy)
for label in sorted(status_dist_copy.index):
    count = status_dist_copy[label]
    pct = (count / total_copy) * 100
    name = class_names.get(label, 'Unknown')
    print(f'  Label {label}: {name:<25s} = {count:3d} ({pct:5.1f}%)')

print()
print('='*80)
print('ANALISIS FITUR & KUALITAS DATA')
print('='*80)
print()

# Feature statistics
features = ['berat_badan', 'tinggi_badan', 'lingkar_lengan', 'lingkar_kepala']

print('STATISTIK FITUR - DATASET SAAT INI:')
print('-'*80)
stats_current = df_current[features].describe()
print(stats_current.to_string())

print()
print()
print('STATISTIK FITUR - DATASET COPY:')
print('-'*80)
stats_copy = df_copy[features].describe()
print(stats_copy.to_string())

print()
print()
print('='*80)
print('PERBANDINGAN KUALITAS DATA')
print('='*80)
print()

# Check missing values
missing_cur = df_current.isnull().sum().sum()
missing_copy = df_copy.isnull().sum().sum()
print(f'Missing values - Dataset Saat Ini: {missing_cur} cells')
print(f'Missing values - Dataset Copy:     {missing_copy} cells')

print()
print('Range Consistency:')
print(f'  Tinggi Badan Saat Ini: {df_current["tinggi_badan"].min():.1f} - {df_current["tinggi_badan"].max():.1f} cm')
print(f'  Tinggi Badan Copy:     {df_copy["tinggi_badan"].min():.1f} - {df_copy["tinggi_badan"].max():.1f} cm')

print()
print(f'  Berat Badan Saat Ini: {df_current["berat_badan"].min():.1f} - {df_current["berat_badan"].max():.1f} kg')
print(f'  Berat Badan Copy:     {df_copy["berat_badan"].min():.1f} - {df_copy["berat_badan"].max():.1f} kg')

print()
print('Label Balance (variance between classes, lower is better):')
cur_counts = df_current['status_stunting'].value_counts().sort_index().values
copy_counts = df_copy['status_stunting'].value_counts().sort_index().values

cur_balance = cur_counts.max() - cur_counts.min()
copy_balance = copy_counts.max() - copy_counts.min()

print(f'  Saat Ini: {cur_balance} (Class count range: {cur_counts.min()} - {cur_counts.max()})')
print(f'  Copy:     {copy_balance} (Class count range: {copy_counts.min()} - {copy_counts.max()})')

print()
print('='*80)
print('TEST MODEL PERFORMANCE')
print('='*80)
print()

def train_and_evaluate(df, name):
    X = df.drop('status_stunting', axis=1)
    y = df['status_stunting']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = KNeighborsClassifier(n_neighbors=5, metric='euclidean', weights='distance')
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    return acc, prec, rec, f1

print('PERFORMANCE - Dataset Saat Ini:')
acc1, prec1, rec1, f1_1 = train_and_evaluate(df_current, 'Current')
print(f'  Accuracy:  {acc1*100:.2f}%')
print(f'  Precision: {prec1*100:.2f}%')
print(f'  Recall:    {rec1*100:.2f}%')
print(f'  F1-Score:  {f1_1*100:.2f}%')

print()
print('PERFORMANCE - Dataset Copy:')
acc2, prec2, rec2, f1_2 = train_and_evaluate(df_copy, 'Copy')
print(f'  Accuracy:  {acc2*100:.2f}%')
print(f'  Precision: {prec2*100:.2f}%')
print(f'  Recall:    {rec2*100:.2f}%')
print(f'  F1-Score:  {f1_2*100:.2f}%')

print()
print('='*80)
print('REKOMENDASI')
print('='*80)
print()

if acc2 > acc1:
    better = 'DATASET COPY'
    diff = acc2 - acc1
else:
    better = 'DATASET SAAT INI'
    diff = acc1 - acc2

print(f'GUNAKAN: {better}')
print(f'Alasan: Lebih baik {diff*100:.2f}% dalam accuracy')
print()

if copy_balance < cur_balance:
    print('✓ Dataset Copy memiliki label balance yang LEBIH SEIMBANG')
else:
    print('✓ Dataset Saat Ini memiliki label balance yang LEBIH SEIMBANG')

if len(df_copy) > len(df_current):
    print(f'✓ Dataset Copy lebih besar ({len(df_copy)} vs {len(df_current)} records)')
else:
    print(f'✓ Dataset Saat Ini lebih besar ({len(df_current)} vs {len(df_copy)} records)')

print()
print('Kesimpulan: Gunakan dataset dengan accuracy lebih tinggi dan balanced label')
