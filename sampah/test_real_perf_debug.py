"""
Debug test untuk /evaluasi/real-performance endpoint
Test tanpa timeout untuk lihat apa yang happen
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_real_performance_debug():
    """Test endpoint dengan debugging"""
    print("="*80)
    print("REAL PERFORMANCE ENDPOINT - DEBUG TEST")
    print("="*80)
    
    print("\n[1] Login...")
    login_r = requests.post(
        f'{BASE_URL}/auth/login',
        json={'email': 'testuser@gempol.id', 'password': 'testpass123'},
        timeout=10
    )
    
    if login_r.status_code != 200:
        print(f"❌ Login failed: {login_r.status_code}")
        print(f"Response: {login_r.text}")
        return
    
    token = login_r.json().get('access_token')
    print(f"✅ Login successful, token: {token[:30]}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test 1: Check pengukuran endpoint to see how many records exist
    print("\n[2] Checking pengukuran data...")
    try:
        pengukuran_r = requests.get(
            f'{BASE_URL}/pengukuran/?limit=10',
            headers=headers,
            timeout=10
        )
        print(f"Status: {pengukuran_r.status_code}")
        if pengukuran_r.status_code == 200:
            data = pengukuran_r.json()
            print(f"✅ Found pengukuran data: {len(data)} records (limit 10)")
            if isinstance(data, list) and len(data) > 0:
                print(f"   Sample: {data[0]}")
        else:
            print(f"Note: {pengukuran_r.status_code}")
    except Exception as e:
        print(f"Error getting pengukuran: {str(e)}")
    
    # Test 2: Call real-performance with extended timeout
    print("\n[3] Testing /evaluasi/real-performance (with 30sec timeout)...")
    print("   This might take a while if calculating metrics from many records...")
    
    try:
        start = time.time()
        eval_r = requests.get(
            f'{BASE_URL}/evaluasi/real-performance',
            headers=headers,
            timeout=30  # Extended timeout
        )
        elapsed = time.time() - start
        
        print(f"Status: {eval_r.status_code}")
        print(f"Time: {elapsed:.2f} seconds")
        
        if eval_r.status_code == 200:
            data = eval_r.json()
            print(f"✅ Response received!")
            print(f"\nResponse:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Response: {eval_r.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout after 30 seconds")
        print("   This could indicate:")
        print("   1. Database is very slow or not responding")
        print("   2. There's a lot of pengukuran data to process")
        print("   3. Supabase connection is unstable")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_real_performance_debug()
