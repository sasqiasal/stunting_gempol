import requests
import json

headers = {
    'Content-Type': 'application/json'
}

test_data = {
    'jenis_kelamin': 'L',
    'usia_bulan': 6,
    'berat_badan': 5.8,
    'tinggi_badan': 58.0,
    'lingkar_lengan': 12.0,
    'lingkar_kepala': 40.7
}

print("🧪 Testing /api/v1/evaluasi/simulate")
print(f"Headers: {headers}")
print(f"Data: {test_data}")
print()

try:
    response = requests.post(
        'http://localhost:8000/api/v1/evaluasi/simulate',
        json=test_data,
        headers=headers,
        timeout=5
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
