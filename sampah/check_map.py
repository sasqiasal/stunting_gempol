import json

with open('public/map.geojson', 'r') as f:
    data = json.load(f)

print('📍 PETA GEOJSON STRUCTURE:')
print('=' * 70)
print()
print(f'Total Features (Posyandu): {len(data.get("features", []))}')
print()
print('Daftar Posyandu:')
print('-' * 70)

for idx, feature in enumerate(data.get('features', [])):
    props = feature.get('properties', {})
    nama = props.get('nama_posyandu', 'Unknown')
    geom_type = feature.get('geometry', {}).get('type', 'N/A')
    
    if geom_type == 'Polygon':
        coords = feature['geometry']['coordinates'][0]
        first_coord = coords[0]
        print(f'{idx+1}. {nama}')
        print(f'   Type: {geom_type}')
        print(f'   First point: [lng={first_coord[0]:.4f}, lat={first_coord[1]:.4f}]')
        print(f'   Total points: {len(coords)}')
        print()

print('=' * 70)
print()
print('📝 Untuk ubah lokasi:')
print('  Opsi 1: Edit koordinat langsung di map.geojson')
print('  Opsi 2: Generate ulang dari database Supabase')
print('  Opsi 3: Tools online: geojson.io')
