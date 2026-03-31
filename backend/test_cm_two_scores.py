import requests
import json

r = requests.get('http://127.0.0.1:8000/api/v1/evaluasi/realtime', timeout=10)
data = r.json().get('data', {})

print("=== EVALUATION METRICS ===")
print(f"Total Data: {data.get('metadata', {}).get('total_data')}")

multiclass = data.get('multiclass_classification', {})
metrics = multiclass.get('metrics', {})
cm = metrics.get('confusion_matrix', [])

print(f"\n4x4 Confusion Matrix (Actual from 2 z-scores, Predicted from KNN):")
class_names = [
    "Normal+Baik",
    "Normal+Kurang",
    "Stunting+Baik",
    "Stunting+Kurang"
]

if cm:
    for i, row in enumerate(cm):
        print(f"  {class_names[i]}: {row}")

print(f"\nMulticlass Accuracy: {metrics.get('accuracy_percent', 0):.2f}%")
print(f"Note: Actual status is now from BOTH z-scores (zscore_tbu + zscore_bbu)")
