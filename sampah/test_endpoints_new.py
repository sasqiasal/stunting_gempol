import requests
import json

r = requests.get('http://127.0.0.1:8000/api/v1/evaluasi/realtime', timeout=15)
print('Status:', r.status_code)
result = r.json()

# Check metrics
data = result.get('data', {})
binary = data.get('binary_classification', {}).get('metrics', {})
multiclass = data.get('multiclass_classification', {}).get('metrics', {})

print(f"Total data: {data.get('metadata', {}).get('total_data')}")
print(f"\nBinary Classification:")
print(f"  Accuracy: {binary.get('accuracy', 0):.4f}")
print(f"  TP={binary.get('tp')}, TN={binary.get('tn')}, FP={binary.get('fp')}, FN={binary.get('fn')}")
print(f"  Confusion Matrix: {binary.get('confusion_matrix', [])}")

print(f"\n4-Class Classification:")
print(f"  Accuracy: {multiclass.get('accuracy', 0):.4f}")
cm = multiclass.get('confusion_matrix', [])
print(f"  Confusion Matrix:")
for row in cm:
    print(f"    {row}")
