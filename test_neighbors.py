import requests
import json
import time

# Wait for server to start
time.sleep(2)

test_data = {
    'jenis_kelamin': 'L',  # L=Laki-laki, P=Perempuan
    'usia_bulan': 6,
    'berat_badan': 5.8,
    'tinggi_badan': 58.0,
    'lingkar_lengan': 12.0,
    'lingkar_kepala': 40.7
}

print('🧪 TEST NEAREST NEIGHBORS')
print('=' * 60)
print('Input data:', test_data)
print()

try:
    response = requests.post('http://localhost:8000/api/v1/simulate', json=test_data)
    result = response.json()
    
    if 'nearest_neighbors' in result:
        neighbors = result['nearest_neighbors']
        print(f'✅ Ditemukan {len(neighbors)} nearest neighbors:')
        print()
        for i, neighbor in enumerate(neighbors[:3], 1):
            print(f'  Neighbor #{i}:')
            print(f'    Gender: {neighbor.get("jenis_kelamin")}')
            print(f'    Age: {neighbor.get("usia_bulan")}')
            print(f'    Weight: {neighbor.get("berat_badan")} kg')
            print(f'    Height: {neighbor.get("tinggi_badan")} cm')
            print(f'    Arm Circ: {neighbor.get("lingkar_lengan")}')
            print(f'    Head Circ: {neighbor.get("lingkar_kepala")}')
            print(f'    Distance: {neighbor.get("distance"):.4f}')
            print()
    else:
        print('Response:', json.dumps(result, indent=2))
except Exception as e:
    print(f'❌ Error: {e}')
