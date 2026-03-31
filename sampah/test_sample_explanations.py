"""Test if model-performance returns sample_explanations"""
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
    print(f'❌ Login failed')
    exit(1)

token = login_r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}
print('✓ Login successful')

# Get model-performance
print('\n[2] Fetching model-performance...')
perf_r = requests.get(f'{BASE_URL}/evaluasi/model-performance', headers=headers)
print(f'    Status: {perf_r.status_code}')

if perf_r.status_code != 200:
    print(f'❌ Error: {perf_r.text[:300]}')
    exit(1)

data = perf_r.json()
print('✓ Model performance fetched')

# Check for sample_explanations
print('\n[3] Checking for sample_explanations...')
if 'sample_explanations' in data:
    explanations = data.get('sample_explanations', [])
    print(f'✓ Found {len(explanations)} sample explanations')
    
    if len(explanations) > 0:
        sample = explanations[0]
        print(f'\n   Sample #1 Details:')
        print(f'     ID: {sample.get("id")}')
        print(f'     Nama: {sample.get("input", {}).get("nama")}')
        print(f'     Usia: {sample.get("input", {}).get("usia_bulan")} bulan')
        print(f'     Prediksi: {sample.get("prediction")}')
        print(f'     Actual: {sample.get("actual")}')
        print(f'     Neighbors: {len(sample.get("neighbors", []))} records')
        
        if sample.get("neighbors"):
            neighbor = sample["neighbors"][0]
            print(f'\n   First Neighbor:')
            print(f'     Label: {neighbor.get("label")}')
            print(f'     Distance: {neighbor.get("distance")}')
            print(f'     Usia: {neighbor.get("usia_bulan")}')
    else:
        print('⚠️  No sample_explanations data (empty list)')
else:
    print('❌ sample_explanations field missing!')
    print(f'\nAvailable fields: {list(data.keys())}')

print('\n✓ Test complete')
