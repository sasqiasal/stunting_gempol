"""Test current state of pengukuran data and classifications"""
import requests
import json

BASE_URL = 'http://localhost:8000/api/v1'

# Login
print('[1] Logging in...')
login_r = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'testuser@gempol.id',
    'password': 'testpass123'
})

if login_r.status_code != 200:
    print(f'    ❌ Login failed: {login_r.text}')
    exit(1)

token = login_r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}
print(f'    ✓ Login successful')

# Get pengukuran list
print('\n[2] Fetching pengukuran list...')
pengukuran_r = requests.get(f'{BASE_URL}/pengukuran/?limit=500', headers=headers)
print(f'    Status: {pengukuran_r.status_code}')

if pengukuran_r.status_code != 200:
    print(f'    ❌ Error: {pengukuran_r.text[:300]}')
    exit(1)

pengukuran_list = pengukuran_r.json()
print(f'    ✓ Found {len(pengukuran_list)} pengukuran records')

if len(pengukuran_list) == 0:
    print('\n⚠️  No pengukuran data found. Need to create test data.')
    exit(1)

# Check each pengukuran for evaluasi/classification
print('\n[3] Checking for classification data...')
for p in pengukuran_list[:3]:  # Check first 3
    pengukuran_id = p.get('id')
    
    # Try to get detail evaluasi
    detail_r = requests.get(f'{BASE_URL}/pengukuran/{pengukuran_id}/detail-evaluasi', headers=headers)
    
    print(f'\n    Pengukuran ID {pengukuran_id}:')
    print(f'      Status: {detail_r.status_code}')
    
    if detail_r.status_code == 200:
        detail = detail_r.json()
        has_neighbors = 'nearest_neighbors' in detail and len(detail.get('nearest_neighbors', [])) > 0
        has_label = 'hasil_prediksi' in detail
        
        print(f'      Has hasil_prediksi: {has_label}')
        print(f'      Nearest neighbors: {len(detail.get("nearest_neighbors", []))} records')
        
        if has_label:
            print(f"      Hasil: {detail.get('hasil_prediksi')}")
    else:
        print(f'      ❌ Error: {detail_r.text[:200]}')

print('\n✓ Test complete')
