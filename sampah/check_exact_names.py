import json

with open('public/map.geojson', 'r') as f:
    data = json.load(f)

print('Nama posyandu di file (exact):')
print('=' * 50)
for idx, feature in enumerate(data['features'], 1):
    nama = feature['properties']['nama_posyandu']
    print(f'{idx}. "{nama}"')
