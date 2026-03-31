import requests
import json

# Test realtime endpoint
print("=== REALTIME ENDPOINT ===")
r = requests.get('http://127.0.0.1:8000/api/v1/evaluasi/realtime', timeout=10)
data = r.json()
print("Status:", r.status_code)
print("Top-level keys:", list(data.keys()))
if 'data' in data:
    print("Data keys:", list(data['data'].keys()))
    if 'binary_classification' in data['data']:
        print("- Binary CM:", 'confusion_matrix' in data['data']['binary_classification'].get('metrics', {}))
    if 'multiclass_classification' in data['data']:
        print("- Multiclass CM:", 'confusion_matrix' in data['data']['multiclass_classification'].get('metrics', {}))

# Test prediction history endpoint
print("\n=== PREDICTION HISTORY ENDPOINT ===")
r = requests.get('http://127.0.0.1:8000/api/v1/evaluasi/prediction-history?limit=100', timeout=10)
data = r.json()
print("Status:", r.status_code)
print("Top-level keys:", list(data.keys()))
if 'data' in data:
    print("Data keys:", list(data['data'].keys()))
    print("Predictions count:", len(data['data'].get('predictions', [])))
    if data['data'].get('predictions'):
        print("First prediction keys:", list(data['data']['predictions'][0].keys()))
