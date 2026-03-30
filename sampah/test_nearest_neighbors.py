#!/usr/bin/env python3
"""Test nearest neighbors format with 4-class labels"""

import requests
import json

BASE_URL = 'http://localhost:8000/api/v1'

# Login
print("Logging in...")
login_r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'testuser@gempol.id', 'password': 'testpass123'})
if login_r.status_code != 200:
    print(f"[!] Login failed: {login_r.text}")
    exit(1)

token = login_r.json().get('access_token')
print("[OK] Login successful\n")

# Create a new pengukuran to test the nearest neighbors
print("Creating new pengukuran for testing...")
create_data = {
    "balita_id": 11,  # Stunting child from earlier
    "tinggi_badan": 96.0,
    "berat_badan": 12.6,
    "lingkar_lengan": 14.2,
    "lingkar_kepala": 48.3,
    "catatan": "Test nearest neighbors format"
}

headers = {'Authorization': f'Bearer {token}'}
r = requests.post(f'{BASE_URL}/pengukuran/', json=create_data, headers=headers)

if r.status_code == 201:
    data = r.json()
    print(f"[OK] Created pengukuran ID {data.get('id')}")
    print(f"    Status: {data.get('status_gizi')}")
    print(f"    Label: {data.get('status_gizi_label')}\n")
    
    # Get detail evaluasi to check nearest neighbors
    pengukuran_id = data.get('id')
    print(f"Fetching nearest neighbors for pengukuran {pengukuran_id}...\n")
    
    eval_r = requests.get(f'{BASE_URL}/pengukuran/{pengukuran_id}/detail-evaluasi', headers=headers)
    
    if eval_r.status_code == 200:
        eval_data = eval_r.json()
        if eval_data.get('data') and eval_data['data'].get('nearest_neighbors'):
            neighbors = eval_data['data']['nearest_neighbors']
            print(f"[OK] Found {len(neighbors)} nearest neighbors\n")
            print("First 2 neighbors:")
            print(json.dumps(neighbors[:2], indent=2))
            
            # Check if labels are 4-class
            first_label = neighbors[0].get('label')
            if any(x in first_label for x in ['Stunting', 'Normal', 'Gizi', 'Kurang']):
                print("\n[OK] Nearest neighbors have proper 4-class labels!")
            else:
                print(f"\n[!] Warning: Label format may not be correct: {first_label}")
        else:
            print("[!] No nearest neighbors found in response")
    else:
        print(f"[!] Error fetching evaluasi: {eval_r.status_code}")
        print(eval_r.text[:500])
else:
    print(f"[!] Error creating pengukuran: {r.status_code}")
    print(r.text[:500])
