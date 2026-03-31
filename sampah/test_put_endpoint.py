#!/usr/bin/env python3
"""Test the PUT (update) endpoint"""

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
print("[OK] Login successful")

# Test update endpoint
print("\nUpdating pengukuran ID 21...")
update_data = {
    "tinggi_badan": 65.5,
    "berat_badan": 8.2,
    "lingkar_lengan": 14.0,
    "lingkar_kepala": 41.1,
    "catatan": "Update test - still normal"
}

headers = {'Authorization': f'Bearer {token}'}
r = requests.put(f'{BASE_URL}/pengukuran/21', json=update_data, headers=headers)
print(f'Status: {r.status_code}')

if r.status_code == 200:
    data = r.json()
    print(f'[OK] Update successful!')
    print(f'\nUpdated pengukuran:')
    print(f'  ID: {data.get("id")}')
    print(f'  Status Gizi: {data.get("status_gizi")}')
    print(f'  Status Gizi Label: {data.get("status_gizi_label")}')
    print(f'  Tinggi Badan: {data.get("tinggi_badan")}')
    print(f'  Catatan: {data.get("catatan")}')
    
    print("\n======================================")
    print("[OK] PUT ENDPOINT FIXED!")
    print("======================================")
else:
    print(f'[!] Error: {r.status_code}')
    print(f'Response: {r.text[:800]}')
