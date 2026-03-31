import json

# Load current map.geojson
with open('public/map.geojson', 'r') as f:
    data = json.load(f)

print("📍 ORIGINAL MAP:")
print("=" * 70)
for idx, feature in enumerate(data['features'], 1):
    print(f"{idx}. {feature['properties']['nama_posyandu']}")

# Mapping: lokasi sekarang → ganti NAMA dengan ini
# Lokasi Melati akan ganti nama jadi Kamboja
# Lokasi Tanjung akan ganti nama jadi Durian 2, dst
name_mapping = {
    "Melati": "Kamboja",
    "Tanjung": "Durian 2",
    "Ceria": "Tanjung",
    "Kamboja": "Durian 1",
    "Strawberry": "Strawberry",
    "Durian 1": "Anggrek 2",
    "Durian 2": "Anggrek 1",
    "Matahari 1": "Melati",
    "Sakura": "Dahlia",
    "Matahari 2": "Ceria",
    "Anggrek 2": "Matahari 2",
    "Anggrek 1": "Matahari 1",
    "Dahlia": "Sakura",
}

print("\n📝 PERUBAHAN NAMA:")
print("=" * 70)
print("Lokasi Sekarang → Nama Baru:")
print("-" * 70)

# Update features dengan nama baru
for feature in data['features']:
    old_name = feature['properties']['nama_posyandu']
    if old_name in name_mapping:
        new_name = name_mapping[old_name]
        feature['properties']['nama_posyandu'] = new_name
        print(f"  {old_name:15s} → {new_name:15s} ✅")
    else:
        print(f"  {old_name:15s} → (tidak ada mapping) ❌")

# Save updated map.geojson
with open('public/map.geojson', 'w') as f:
    json.dump(data, f, indent=2)

print("\n" + "=" * 70)
print("🆕 NEW MAP:")
print("=" * 70)
for idx, feature in enumerate(data['features'], 1):
    print(f"{idx}. {feature['properties']['nama_posyandu']}")

print("\n✅ map.geojson BERHASIL DIPERBARUI!")
print(f"   Total Features: {len(data['features'])}")
