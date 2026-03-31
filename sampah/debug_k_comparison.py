import requests
import json

BASE_URL = 'http://localhost:8000/api/v1'

# Login
print('[1] Logging in...')
login_r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'testuser@gempol.id', 'password': 'testpass123'})
if login_r.status_code != 200:
    print(f'Login failed: {login_r.text}')
    exit(1)

token = login_r.json().get('access_token')
headers = {'Authorization': f'Bearer {token}'}

# Get model performance
print('[2] Getting model performance...')
perf_r = requests.get(f'{BASE_URL}/model-performance', headers=headers)
print(f'Status: {perf_r.status_code}')

if perf_r.status_code == 200:
    data = perf_r.json()
    print(f'\n[K-Comparisons Data]:')
    for k_comp in data.get('k_comparisons', []):
        print(f"K={k_comp.get('k')}: Accuracy={k_comp.get('accuracy')}, TP={k_comp.get('tp')}, TN={k_comp.get('tn')}, FP={k_comp.get('fp')}, FN={k_comp.get('fn')}")
    
    print(f'\n[Dataset Info]:')
    dataset_info = data.get('dataset_info', {})
    print(f"Source: {dataset_info.get('source')}")
    print(f"Train size: {dataset_info.get('train_size')}")
    print(f"Test size: {dataset_info.get('test_size')}")
else:
    print(f'Error: {perf_r.text[:500]}')
