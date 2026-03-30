import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('data_latih_stunting.csv')

print('='*80)
print('ANALISIS KUALITAS DATA - DATA_LATIH_STUNTING.CSV')
print('='*80)
print()

print('1. INFORMASI UMUM')
print('-'*80)
print(f'Total Records: {len(df)}')
print(f'Total Kolom: {len(df.columns)}')
print(f'Kolom: {", ".join(df.columns.tolist())}')

print()
print('2. CEK MISSING VALUES')
print('-'*80)
missing = df.isnull().sum()
if missing.sum() == 0:
    print('✓ TIDAK ADA missing values')
else:
    print('⚠️ ADA missing values:')
    print(missing[missing > 0])

print()
print('3. CEK DATA TYPES')
print('-'*80)
print(df.dtypes)

print()
print('4. CEK DUPLICATE ROWS (EXACT DUPLICATE)')
print('-'*80)
duplicates_exact = df.duplicated().sum()
print(f'Total exact duplicates: {duplicates_exact}')

if duplicates_exact > 0:
    print()
    print('Rows yang duplikat:')
    dup_rows = df[df.duplicated(keep=False)].sort_values(by=list(df.columns))
    print(dup_rows.to_string())
    print()
else:
    print('✓ TIDAK ADA exact duplicates')

print()
print('5. CEK DUPLICATE BASEDON KEY FIELDS (Tanpa Label)')
print('-'*80)
key_cols = ['jenis_kelamin', 'usia_bulan', 'berat_badan', 'tinggi_badan', 'lingkar_lengan', 'lingkar_kepala']
duplicates_keys = df.duplicated(subset=key_cols).sum()
print(f'Total records dengan measurement data yang identik: {duplicates_keys}')

if duplicates_keys > 0:
    print()
    print('⚠️ Records yang memiliki measurement identik (beda label):')
    dup_keys = df[df.duplicated(subset=key_cols, keep=False)].sort_values(by=key_cols)
    print(f'Menampilkan {min(20, len(dup_keys))} dari {len(dup_keys)} records:')
    print(dup_keys.head(20).to_string())
    print()
else:
    print('✓ Semua measurement data unik')

print()
print('6. CEK OUTLIERS & NILAI TIDAK MASUK AKAL')
print('-'*80)

# Check for impossible values
issues = []

# Age should be 0-60 months
invalid_age = df[(df['usia_bulan'] < 0) | (df['usia_bulan'] > 60)]
if len(invalid_age) > 0:
    issues.append(f'⚠️ Usia tidak valid (bukan 0-60 bulan): {len(invalid_age)} records')

# Weight should be realistic for children
invalid_weight = df[(df['berat_badan'] < 2) | (df['berat_badan'] > 25)]
if len(invalid_weight) > 0:
    issues.append(f'⚠️ Berat badan tidak realistis: {len(invalid_weight)} records')

# Height should be 45-120 cm
invalid_height = df[(df['tinggi_badan'] < 45) | (df['tinggi_badan'] > 120)]
if len(invalid_height) > 0:
    issues.append(f'⚠️ Tinggi badan tidak realistis: {len(invalid_height)} records')

# Head circumference should be 30-65 cm
invalid_head = df[(df['lingkar_kepala'] < 30) | (df['lingkar_kepala'] > 65)]
if len(invalid_head) > 0:
    issues.append(f'⚠️ Lingkar kepala tidak realistis: {len(invalid_head)} records')

# Arm circumference should be 10-20 cm
invalid_arm = df[(df['lingkar_lengan'] < 10) | (df['lingkar_lengan'] > 20)]
if len(invalid_arm) > 0:
    issues.append(f'⚠️ Lingkar lengan tidak realistis: {len(invalid_arm)} records')

# Gender should be 0 or 1
invalid_gender = df[(df['jenis_kelamin'] != 0) & (df['jenis_kelamin'] != 1)]
if len(invalid_gender) > 0:
    issues.append(f'⚠️ Jenis kelamin tidak valid: {len(invalid_gender)} records')

# Status stunting should be 0, 1, 2, or 3
invalid_status = df[~df['status_stunting'].isin([0, 1, 2, 3])]
if len(invalid_status) > 0:
    issues.append(f'⚠️ Status stunting tidak valid: {len(invalid_status)} records')

if len(issues) == 0:
    print('✓ SEMUA VALUES VALID')
else:
    print('ISSUES FOUND:')
    for issue in issues:
        print(f'  {issue}')

print()
print('7. CEK PLAUSIBILITY (Height vs Weight)')
print('-'*80)

# Height and weight should correlate
# For children: very rough check for physically possible combinations
suspicious = 0
suspicious_rows = []

for idx, row in df.iterrows():
    height = row['tinggi_badan']
    weight = row['berat_badan']
    age = row['usia_bulan']
    
    # Very rough check: height/weight ratio
    # If height is 50cm, weight should be ~5kg
    # If height is 100cm, weight should be ~15kg
    expected_weight_min = (height - 45) * 0.15  # Linear approximation lower bound
    expected_weight_max = (height - 45) * 0.25  # Linear approximation upper bound
    
    if weight < expected_weight_min or weight > expected_weight_max:
        suspicious += 1
        suspicious_rows.append((idx, height, weight))

if suspicious > 0:
    print(f'⚠️ {suspicious} records dengan height/weight combination mencurigakan:')
    for idx, h, w in suspicious_rows[:10]:  # Show first 10
        print(f'  Row {idx}: Height={h}cm, Weight={w}kg')
    if suspicious > 10:
        print(f'  ... dan {suspicious - 10} records lainnya')
    print('  (Ini BUKAN berarti error, tapi kombinasi tidak umum)')
else:
    print('✓ Semua height/weight combinations masuk akal')

print()
print('8. DATA STATISTICS SUMMARY')
print('-'*80)
print(df[['berat_badan', 'tinggi_badan', 'lingkar_lengan', 'lingkar_kepala', 'usia_bulan']].describe().to_string())

print()
print('='*80)
print('KESIMPULAN')
print('='*80)
if len(issues) == 0 and duplicates_exact == 0:
    print('✓ DATA QUALITY: BAIK')
    print('✓ Tidak ada duplicates')
    print('✓ Tidak ada invalid values')
    print('✓ SIAP UNTUK TRAINING')
else:
    print('⚠️ ADA ISSUES YANG PERLU DIPERBAIKI')
    print(f'   - Exact duplicates: {duplicates_exact}')
    print(f'   - Invalid values: {len(issues)}')
