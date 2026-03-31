#!/usr/bin/env python3
"""Test the pengukuran endpoint after fix"""

import requests
import json

BASE_URL = 'http://localhost:8000/api/v1'

# Login
print("Logging in...")
login_r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'testuser@gempol.id', 'password': 'testpass123'})
if login_r.status_code != 200:
    print(f"❌ Login failed: {login_r.text}")
    exit(1)

token = login_r.json().get('access_token')
print("✅ Login successful")

# Test pengukuran fetch
print("\nFetching pengukuran data...")
r = requests.get(f'{BASE_URL}/pengukuran/?limit=500', headers={'Authorization': f'Bearer {token}'})
print(f'Status: {r.status_code}')

if r.status_code == 200:
    data = r.json()
    print(f'✅ Success! Got {len(data)} records')
    
    if len(data) > 0:
        record = data[0]
        print(f'\n📊 First record:')
        print(f'  ID: {record.get("id")}')
        print(f'  Status Gizi: {record.get("status_gizi")}')
        print(f'  Status Gizi Label: {record.get("status_gizi_label")}')
        print(f'  Prediksi Stunting: {record.get("prediksi_stunting")}')
        print(f'  Balita: {record.get("balita_nama")}')
        
    print("\n======================================")
    print("✅ FRONTEND 500 ERROR FIXED!")
    print("======================================")
else:
    print(f'\n❌ Error fetching pengukuran:')
    print(f'Response: {r.text[:500]}')
