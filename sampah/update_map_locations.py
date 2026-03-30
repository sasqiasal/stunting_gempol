import json

# Load current map.geojson
with open('public/map.geojson', 'r') as f:
    data = json.load(f)

# Create mapping from current nama to feature
current_features = {}
for feature in data['features']:
    nama = feature['properties']['nama_posyandu']
    current_features[nama] = feature

print("📍 ORIGINAL MAP:")
print("=" * 70)
for idx, feature in enumerate(data['features'], 1):
    print(f"{idx}. {feature['properties']['nama_posyandu']}")

# Mapping: tempat sekarang → ambil lokasi dari posyandu ini
location_swap = {
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

print("\n📝 MAPPING PERUBAHAN:")
print("=" * 70)
print("Posyandu Sekarang → Ambil Lokasi Dari Posyandu:")
print("-" * 70)

# Create new features with swapped locations
new_features = []
for current_name, source_name in location_swap.items():
    if source_name in current_features:
        # Clone feature dari source
        source_feature = current_features[source_name]
        new_feature = {
            "type": "Feature",
            "properties": {
                "stroke": source_feature['properties'].get("stroke", "#555555"),
                "stroke-width": source_feature['properties'].get("stroke-width", 0),
                "stroke-opacity": source_feature['properties'].get("stroke-opacity", 1),
                "fill": source_feature['properties'].get("fill", "#ffa200"),
                "fill-opacity": source_feature['properties'].get("fill-opacity", 0.5),
                "nama_posyandu": current_name
            },
            "geometry": source_feature['geometry']
        }
        new_features.append(new_feature)
        print(f"  {current_name:15s} ← {source_name:15s} ✅")
    else:
        print(f"  {current_name:15s} ← {source_name:15s} ❌ NOT FOUND")

# Sort by original order names
original_order = [f['properties']['nama_posyandu'] for f in data['features']]
sorted_features = []
for original_name in original_order:
    for new_feat in new_features:
        if new_feat['properties']['nama_posyandu'] == original_name:
            sorted_features.append(new_feat)
            break

# Save new map.geojson
new_data = {
    "type": "FeatureCollection",
    "features": sorted_features
}

with open('public/map.geojson', 'w') as f:
    json.dump(new_data, f, indent=2)

print("\n" + "=" * 70)
print("🆕 NEW MAP:")
print("=" * 70)
for idx, feature in enumerate(sorted_features, 1):
    print(f"{idx}. {feature['properties']['nama_posyandu']}")

print("\n✅ map.geojson BERHASIL DIPERBARUI!")
print(f"   Total Features: {len(sorted_features)}")
