#!/usr/bin/env python
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Test login
print("Testing login endpoint...")
login_data = {
    "username": "admintest",
    "password": "password"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# If login works, try getting evaluation data
print("\n" + "="*50)
print("Testing evaluation endpoint...")

# First, try without auth
response = requests.get(f"{BASE_URL}/evaluasi/model-performance", timeout=5)
print(f"Without auth - Status: {response.status_code}")
if response.status_code != 200:
    print(f"Response: {response.text[:300]}")
else:
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
