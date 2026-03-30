#!/usr/bin/env python3
"""Simple test to check nearest neighbors format"""

import requests
import json

BASE_URL = 'http://localhost:8000/api/v1'

# Login
login_r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'testuser@gempol.id', 'password': 'testpass123'})
token = login_r.json().get('access_token')

headers = {'Authorization': f'Bearer {token}'}

# Get the evaluasi for pengukuran 24 (we just created)
print("Fetching detail evaluasi for pengukuran 24...")
r = requests.get(f'{BASE_URL}/pengukuran/24/detail-evaluasi', headers=headers, timeout=10)

print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(json.dumps(data, indent=2)[:2000])
else:
    print(f"Error: {r.text[:500]}")
