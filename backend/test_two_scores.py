import requests
import json

r = requests.get('http://127.0.0.1:8000/api/v1/evaluasi/prediction-history?limit=1', timeout=10)
data = r.json()

if data['data']['predictions']:
    pred = data['data']['predictions'][0]
    print("=== PREDICTION RECORD ===")
    print(f"Nama: {pred['nama_balita']}")
    print(f"Z-Score TB: {pred['zscore_tbu']}")
    print(f"Z-Score BB: {pred['zscore_bbu']}")
    print(f"Actual Status (dari 2 z-scores): {pred['actual_status']}")
    print(f"Predicted Status (dari KNN): {pred['predicted_status']}")
    print(f"Benar: {pred['is_correct']}")
    print(f"\nActual Label: {pred['actual_label']}")
    print(f"Predicted Label: {pred['predicted_label']}")
