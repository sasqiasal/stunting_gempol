import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.services.evaluation_service import EvaluationService

# Test contoh data
service = EvaluationService()

# Data dari history: zonang -2.02, zscore_bbu -1.8
zscore_tbu = -2.02
zscore_bbu = -1.8

# Hitung dengan threshold baru
label = service.convert_zscores_to_class_label(zscore_tbu, zscore_bbu)

labels_map = {
    0: "Normal + Gizi Baik",
    1: "Normal + Kurang Gizi",
    2: "Stunting + Gizi Baik",
    3: "Stunting + Kurang Gizi"
}

print("🔍 TEST THRESHOLD BARU")
print("=" * 60)
print(f"zscore_tbu: {zscore_tbu} (< -2.0 = Stunting)")
print(f"zscore_bbu: {zscore_bbu} (>= -2.0 = Gizi Baik)")
print()
print(f"✅ Ground Truth Label: {label} = {labels_map[label]}")
print()

# Test lagi dengan data lainnya
test_cases = [
    (-1.5, -1.5, "Normal + Gizi Baik"),      # Normal, Baik
    (-1.5, -2.5, "Normal + Kurang Gizi"),    # Normal, Kurang
    (-2.5, -1.5, "Stunting + Gizi Baik"),    # Stunting, Baik
    (-2.5, -2.5, "Stunting + Kurang Gizi"),  # Stunting, Kurang
]

print("Test cases lainnya:")
print("-" * 60)
for test_tbu, test_bbu, expected in test_cases:
    result_label = service.convert_zscores_to_class_label(test_tbu, test_bbu)
    result_str = labels_map[result_label]
    match = "✓" if result_str == expected else "✗"
    print(f"{match} Z-TBU={test_tbu:5.1f}, Z-BBU={test_bbu:5.1f} → {result_str:30s} (Expected: {expected})")
