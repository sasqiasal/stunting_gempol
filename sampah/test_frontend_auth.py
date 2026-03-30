#!/usr/bin/env python3
"""
Test frontend authentication flow
1. Login with test credentials
2. Get JWT token
3. Fetch pengukuran data with token
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test login endpoint"""
    print("\n[1] Testing Login...")
    login_url = f"{BASE_URL}/auth/login"
    
    credentials = {
        "email": "admin@stunting.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"    ✅ Login successful")
            print(f"    Token: {token[:50]}..." if token else "No token")
            return token
        else:
            print(f"    ❌ Login failed")
            print(f"    Response: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None

def test_pengukuran(token):
    """Test pengukuran endpoint with token"""
    print("\n[2] Testing Pengukuran Endpoint...")
    pengukuran_url = f"{BASE_URL}/pengukuran/?limit=500"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(pengukuran_url, headers=headers)
        print(f"    Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Data fetched successfully")
            print(f"    Records count: {len(data) if isinstance(data, list) else 'N/A'}")
            if isinstance(data, list) and len(data) > 0:
                print(f"    First record keys: {list(data[0].keys())}")
            return True
        else:
            print(f"    ❌ Request failed")
            print(f"    Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

def main():
    print("=" * 70)
    print("TESTING FRONTEND AUTHENTICATION FLOW")
    print("=" * 70)
    
    # Step 1: Login
    token = test_login()
    
    if not token:
        print("\n❌ Cannot proceed - login failed")
        sys.exit(1)
    
    # Step 2: Fetch data with token
    success = test_pengukuran(token)
    
    print("\n" + "=" * 70)
    if success:
        print("✅ AUTHENTICATION FLOW WORKS")
        print("\nFrontend should:")
        print("1. Make sure user is logged in (has valid access_token in localStorage)")
        print("2. Call pengukuranService.getAll() after login")
    else:
        print("❌ AUTHENTICATION FLOW FAILED")
        print("\nCheck:")
        print("1. Backend is running on port 8000")
        print("2. Database is accessible")
        print("3. Pengukuran endpoint has no errors")
    print("=" * 70)

if __name__ == "__main__":
    main()
