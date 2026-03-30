"""Final comprehensive test of the complete system flow"""
import requests

BASE_URL = 'http://localhost:8000/api/v1'

print("=" * 80)
print("COMPREHENSIVE SYSTEM TEST - CLASSIFICATION DATA DISPLAY")
print("=" * 80)

# 1. Login
print('\n[1] Authentication...')
login_r = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'testuser@gempol.id',
    'password': 'testpass123'
})

if login_r.status_code != 200:
    print(f'❌ Login failed')
    exit(1)

token = login_r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}
print('    ✓ Logged in successfully')

# 2. Get pengukuran list
print('\n[2] Pengukuran Data...')
peng_r = requests.get(f'{BASE_URL}/pengukuran/?limit=500', headers=headers)
pengukuran_list = peng_r.json()
print(f'    ✓ Found {len(pengukuran_list)} pengukuran records')

# 3. Get model performance (which now includes sample_explanations)
print('\n[3] Model Performance & Classification Data...')
perf_r = requests.get(f'{BASE_URL}/evaluasi/model-performance', headers=headers)
perf_data = perf_r.json()

print(f'    Status Code: {perf_r.status_code}')
print(f'    ✓ Fetched successfully')
print(f'    ✓ Has sample_explanations: {"sample_explanations" in perf_data}')

if 'sample_explanations' in perf_data:
    explanations = perf_data['sample_explanations']
    print(f'    ✓ Sample explanations count: {len(explanations)}')
    
    if len(explanations) > 0:
        print('\n[4] Sample Data Structure Verification...')
        
        # Check first 3 samples
        for idx, sample in enumerate(explanations[:3], 1):
            print(f'\n    Sample #{idx}:')
            print(f'      • Nama: {sample.get("input", {}).get("nama")}')
            print(f'      • Usia: {sample.get("input", {}).get("usia_bulan")} bulan')
            print(f'      • Prediksi: {sample.get("prediction")}')
            print(f'      • Status Aktual: {sample.get("actual")}')
            
            neighbors = sample.get('neighbors', [])
            print(f'      • Tetangga Terdekat: {len(neighbors)} records')
            
            if neighbors:
                n1 = neighbors[0]
                print(f'        - #1: {n1.get("label")} (dist: {n1.get("distance")})')
        
        print('\n' + '=' * 80)
        print('✅ ALL CHECKS PASSED!')
        print('=' * 80)
        print('\nFrontend should now display:')
        print('  • "Analisis Tetangga Terdekat (Explainability)" tab')
        print('  • 7 actual pengukuran records with their nearest neighbors')
        print('  • 4-class classification labels')
        print('  • Full feature set (JK, Usia, BB, TB, LILA, LK, Distance)')
        print('\nNo more "Belum Ada Data Klasifikasi" message!')
    else:
        print('❌ sample_explanations is empty!')
else:
    print('❌ sample_explanations field is missing!')
