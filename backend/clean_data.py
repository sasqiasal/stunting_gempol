import pandas as pd

# Load original data
df_original = pd.read_csv('data_latih_stunting.csv')

print('='*80)
print('PROSES PEMBERSIHAN DATA')
print('='*80)
print()

print('SEBELUM PEMBERSIHAN:')
print('-'*80)
print(f'Total Records: {len(df_original)}')

# Show duplicates
duplicates = df_original[df_original.duplicated(keep=False)].sort_values(by=list(df_original.columns))
print(f'Total Exact Duplicates: {len(duplicates)}')
print()
print('Duplicate Records yang akan dihapus:')
print(duplicates.to_string())

print()
print()
print('MENGHAPUS DUPLICATES...')
print('-'*80)

# Remove exact duplicates, keep first occurrence
df_cleaned = df_original.drop_duplicates(keep='first')

print(f'Total Records setelah remove duplicates: {len(df_cleaned)}')
print(f'Records dihapus: {len(df_original) - len(df_cleaned)}')

print()
print('HASIL PEMBERSIHAN:')
print('-'*80)
print(f'✓ Total Records: {len(df_cleaned)}')
print(f'✓ Tidak ada lagi exact duplicates: {df_cleaned.duplicated().sum()}')

print()
print('Distribusi Status Stunting:')
class_names = {0: 'Normal + Gizi Baik', 1: 'Normal + Kurang Gizi', 
               2: 'Stunting + Gizi Baik', 3: 'Stunting + Kurang Gizi'}

status_dist = df_cleaned['status_stunting'].value_counts().sort_index()
total = len(df_cleaned)

for label in sorted(status_dist.index):
    count = status_dist[label]
    pct = (count / total) * 100
    name = class_names.get(label, 'Unknown')
    print(f'  Label {label}: {name:<25s} = {count:3d} ({pct:5.1f}%)')

print()
print('SIMPAN DATA YANG SUDAH DIBERSIHKAN...')
print('-'*80)

# Save cleaned data
df_cleaned.to_csv('data_latih_stunting.csv', index=False)
print('✓ Data yang sudah dibersihkan disimpan ke: data_latih_stunting.csv')

# Also create backup
df_original.to_csv('data_latih_stunting_backup_original.csv', index=False)
print('✓ Data original (sebelum pembersihan) disimpan ke: data_latih_stunting_backup_original.csv')

print()
print('='*80)
print('✅ PEMBERSIHAN DATA SELESAI!')
print('='*80)
print()
print(f'Dataset siap untuk training!')
print(f'Total records yang clean: {len(df_cleaned)}')
