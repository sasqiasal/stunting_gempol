#!/usr/bin/env python
"""
Test script to verify API endpoints are working after 4-class fixes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("TESTING API ENDPOINTS AFTER 4-CLASS CLASSIFICATION FIX")
print("=" * 70)

# Test 1: Check if backend is responsive
print("\n[1] Backend Health Check...")
try:
    r = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"    Status: {r.status_code}")
    if r.status_code == 200:
        print("    [OK] Backend is running")
    else:
        print(f"    [ERROR] Unexpected status")
except Exception as e:
    print(f"    [ERROR] {e}")
    exit(1)

# Test 2: Check OpenAPI routes
print("\n[2] Checking Available Routes...")
try:
    r = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    routes = list(r.json()['paths'].keys())
    
    pengukuran_routes = [rt for rt in routes if 'pengukuran' in rt]
    balita_routes = [rt for rt in routes if 'balita' in rt]
    
    print(f"    [OK] Found {len(pengukuran_routes)} pengukuran routes")
    print(f"    [OK] Found {len(balita_routes)} balita routes")
    
    for route in sorted(pengukuran_routes):
        print(f"       - {route}")
        
except Exception as e:
    print(f"    [ERROR] {e}")

# Test 3: Try to fetch with custom header (simulate frontend request via proxy)
print("\n[3] Testing Pengukuran Endpoint (without auth)...")
try:
    # Just try to get the endpoint response without auth
    r = requests.get(f"{BASE_URL}/api/v1/pengukuran/?limit=10", timeout=5)
    print(f"    Status Code: {r.status_code}")
    
    if r.status_code == 401:
        print("    [OK] Auth required (expected for protected endpoint)")
        print("    Endpoint is responsive, just needs valid token")
    elif r.status_code == 200:
        print("    [OK] Received data successfully")
        data = r.json()
        print(f"    Response has {len(data) if isinstance(data, list) else 'N/A'} items")
    elif r.status_code == 500:
        print("    [ERROR] Internal Server Error")
        print("    Response:", r.text[:200])
    else:
        print(f"    [WARNING] Unexpected status: {r.status_code}")
        
except Exception as e:
    print(f"    [ERROR] {e}")

print("\n" + "=" * 70)
print("ENDPOINT TESTING COMPLETE")
print("=" * 70)
print("\nNote: For full testing with data, provide valid JWT auth token")
