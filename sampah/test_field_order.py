#!/usr/bin/env python3
"""Test nearest neighbors with corrected field order"""

import requests
import json

BASE_URL = 'http://localhost:8000/api/v1'

# Login
login_r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'testuser@gempol.id', 'password': 'testpass123'})
token = login_r.json().get('access_token')

headers = {'Authorization': f'Bearer {token}'}

# Create a stunting child pengukuran
print("Creating pengukuran for stunting child...")
create_data = {
    "balita_id": 11,
    "tinggi_badan": 96.0,
    "berat_badan": 12.6,
    "lingkar_lengan": 14.2,
    "lingkar_kepala": 48.3,
    "catatan": "Test corrected field order"
}

r = requests.post(f'{BASE_URL}/pengukuran/', json=create_data, headers=headers)

if r.status_code == 201:
    data = r.json()
    pengukuran_id = data.get('id')
    print(f"[OK] Created pengukuran {pengukuran_id}")
    print(f"     Input: TB={create_data['tinggi_badan']}, BB={create_data['berat_badan']}\n")
    
    # Fetch evaluasi
    eval_r = requests.get(f'{BASE_URL}/pengukuran/{pengukuran_id}/detail-evaluasi', headers=headers, timeout=10)
    
    if eval_r.status_code == 200:
        eval_data = eval_r.json()
        neighbors = eval_data['data']['nearest_neighbors']
        
        print(f"[OK] First 2 nearest neighbors:\n")
        
        for i, neighbor in enumerate(neighbors[:2]):
            print(f"Neighbor {i+1}:")
            print(f"  Label: {neighbor['label']}")
            print(f"  Distance: {neighbor['distance']}")
            print(f"  Usia: {neighbor['usia_bulan']} bulan")
            print(f"  Berat Badan: {neighbor['berat_badan']} kg")
            print(f"  Tinggi Badan: {neighbor['tinggi_badan']} cm")
            print(f"  Jenis Kelamin: {neighbor['jenis_kelamin']}")
            print(f"  Lingkar Kepala: {neighbor['lingkar_kepala']} cm")
            print(f"  Lingkar Lengan: {neighbor['lingkar_lengan']} cm")
            print()
        
        # Check if values match expected format
        first_neighbor = neighbors[0]
        if (first_neighbor['berat_badan'] < 20 and  # BB should be around 12-15 kg
            first_neighbor['tinggi_badan'] > 90):   # TB should be around 96-100 cm
            print("[OK] Field order is CORRECT!")
        else:
            print("[!] Field order may still be wrong!")
            print(f"    Expected: BB around 12-15 kg, TB around 90-100 cm")
            print(f"    Got: BB={first_neighbor['berat_badan']}, TB={first_neighbor['tinggi_badan']}")
else:
    print(f"Error: {r.status_code}")
