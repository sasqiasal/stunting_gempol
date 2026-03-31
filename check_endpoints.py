import requests

print("🔍 Checking available endpoints...")
try:
    response = requests.get('http://localhost:8000/openapi.json')
    if response.status_code == 200:
        openapi = response.json()
        paths = list(openapi.get('paths', {}).keys())
        print(f"✅ Found {len(paths)} endpoints:")
        for path in sorted(paths):
            if 'simulat' in path.lower() or 'predict' in path.lower():
                print(f"  ✓ {path}")
        print("\nAll endpoints:")
        for path in sorted(paths)[:20]:
            print(f"  {path}")
        if len(paths) > 20:
            print(f"  ... and {len(paths) - 20} more")
    else:
        print(f"❌ Error: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
