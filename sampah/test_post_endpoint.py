#!/usr/bin/env python3
"""Test the POST (create) endpoint"""

import requests
from datetime import date

BASE_URL = 'http://localhost:8000/api/v1'

# Login
print("Logging in...")
login_r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'testuser@gempol.id', 'password': 'testpass123'})
if login_r.status_code != 200:
    print(f"[!] Login failed: {login_r.text}")
    exit(1)

token = login_r.json().get('access_token')
print("[OK] Login successful")

# Test create pengukuran
print("\nCreating new pengukuran for balita ID 3...")
create_data = {
    "balita_id": 3,
    "tinggi_badan": 66.0,
    "berat_badan": 8.3,
    "lingkar_lengan": 14.2,
    "lingkar_kepala": 41.2,
    "catatan": "New measurement test"
}

headers = {'Authorization': f'Bearer {token}'}
r = requests.post(f'{BASE_URL}/pengukuran/', json=create_data, headers=headers)
print(f'Status: {r.status_code}')

if r.status_code == 201:
    data = r.json()
    print(f'[OK] Create successful!')
    print(f'\nNew pengukuran:')
    print(f'  ID: {data.get("id")}')
    print(f'  Status Gizi: {data.get("status_gizi")}')
    print(f'  Status Gizi Label: {data.get("status_gizi_label")}')
    print(f'  Tinggi Badan: {data.get("tinggi_badan")}')
    print(f'  Catatan: {data.get("catatan")}')
    
    print("\n======================================")
    print("[OK] POST ENDPOINT FIXED!")
    print("======================================")
else:
    print(f'[!] Error: {r.status_code}')
    print(f'Response: {r.text[:1000]}')
