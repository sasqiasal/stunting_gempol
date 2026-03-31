"""
Test startup dan connectivity ke backend
"""
import time
import subprocess
import sys
import requests
import os
from pathlib import Path

def test_backend_startup():
    """Test backend startup dengan uvicorn"""
    print("="*80)
    print("BACKEND STARTUP TEST")
    print("="*80)
    
    backend_path = Path(r'd:\development\stunting_gempol')
    venv_python = backend_path / r'backend\venv\Scripts\python.exe'
    
    # Set environment
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_path / 'api')
    
    print(f"\n1. Starting Uvicorn server...")
    print(f"   Python: {venv_python}")
    print(f"   Working Dir: {backend_path}")
    
    try:
        # Start backend with output capture
        process = subprocess.Popen(
            [str(venv_python), '-m', 'uvicorn', 'api.app.main:app', 
             '--host', '127.0.0.1', '--port', '8000'],
            cwd=str(backend_path),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"   Process ID: {process.pid}")
        print(f"\n2. Waiting for server to start...")
        
        # Give server time to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("   ✅ Process is running")
        else:
            print("   ❌ Process exited")
            stdout, stderr = process.communicate()
            print(f"   STDOUT: {stdout[:500]}")
            print(f"   STDERR: {stderr[:500]}")
            return False
        
        # Test connectivity
        print(f"\n3. Testing HTTP connectivity...")
        max_retries = 3
        for i in range(max_retries):
            try:
                response = requests.get('http://localhost:8000/docs', timeout=2)
                print(f"   ✅ Server responding on port 8000")
                print(f"   HTTP Status: {response.status_code}")
                
                # Test auth endpoint
                print(f"\n4. Testing login endpoint...")
                try:
                    login_response = requests.post(
                        'http://localhost:8000/api/v1/auth/login',
                        json={'email': 'testuser@gempol.id', 'password': 'testpass123'},
                        timeout=5
                    )
                    print(f"   ✅ Login endpoint responding")
                    print(f"   Status: {login_response.status_code}")
                    
                    if login_response.status_code == 200:
                        token = login_response.json().get('access_token')
                        print(f"   ✅ Token retrieved: {token[:20]}...")
                        
                        # Test real-performance endpoint
                        print(f"\n5. Testing /evaluasi/real-performance endpoint...")
                        eval_response = requests.get(
                            'http://localhost:8000/api/v1/evaluasi/real-performance',
                            headers={'Authorization': f'Bearer {token}'},
                            timeout=5
                        )
                        print(f"   Status: {eval_response.status_code}")
                        
                        if eval_response.status_code in [200, 403]:
                            print(f"   ✅ Endpoint is responding")
                            print(f"   Response: {eval_response.json()}")
                        else:
                            print(f"   Response: {eval_response.text[:300]}")
                    else:
                        print(f"   Response: {login_response.text[:300]}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"   Error: {str(e)}")
                
                # Clean up
                print(f"\n6. Cleaning up...")
                process.terminate()
                process.wait(timeout=5)
                print("   ✅ Server stopped.")
                
                return True
                
            except requests.exceptions.ConnectionError:
                print(f"   Retry {i+1}/{max_retries}: Connection refused, retrying...")
                time.sleep(2)
        
        print(f"   ❌ Could not connect after {max_retries} retries")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_backend_startup()
    sys.exit(0 if success else 1)
