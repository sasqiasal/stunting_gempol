import requests
import json
import time

time.sleep(3)

BASE_URL = 'http://localhost:8000/api/v1'

# Login
login_resp = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'testuser@gempol.id',
    'password': 'testpass123'
})

if login_resp.status_code == 200:
    token = login_resp.json().get('access_token')
    print('✓ Login berhasil')
    
    # Test evaluasi endpoint
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    resp = requests.get(f'{BASE_URL}/evaluasi/model-performance', headers=headers)
    
    print(f'Status: {resp.status_code}')
    
    if resp.status_code == 200:
        data = resp.json()
        print('✓ Evaluasi endpoint berhasil!')
        print(f'Keys in response: {list(data.keys())}')
        
        if 'k_comparisons' in data:
            print(f'✓ k_comparisons found!')
            print(f'Number of K values: {len(data["k_comparisons"])}')
            if len(data['k_comparisons']) > 0:
                first_k = data['k_comparisons'][0]
                print(f'First K result:')
                print(json.dumps(first_k, indent=2))
                # Check for TP/TN/FP/FN
                print(f'\nTP/TN/FP/FN values:')
                print(f'  TP: {first_k.get("tp")}')
                print(f'  TN: {first_k.get("tn")}')
                print(f'  FP: {first_k.get("fp")}')
                print(f'  FN: {first_k.get("fn")}')
        else:
            print('⚠ k_comparisons NOT found in response')
    else:
        print(f'Error: {resp.text[:1000]}')
else:
    print(f'Login failed: {login_resp.text}')
