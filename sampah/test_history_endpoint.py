import requests

r = requests.get('http://127.0.0.1:8000/api/v1/evaluasi/prediction-history?limit=5')
print(f'Status: {r.status_code}')
data = r.json().get('data', {})
predictions = data.get('predictions', [])

if predictions:
    print(f'Total predictions returned: {len(predictions)}\n')
    print('Sample predictions:')
    for i, p in enumerate(predictions[:5]):
        actual_label = p.get('actual_label')
        predicted_label = p.get('predicted_label')
        is_correct = p.get('is_correct')
        name = p.get('nama_balita', 'Unknown')[:20]
        print(f'{i+1}. {name:20s} Actual:{actual_label} Pred:{predicted_label} OK:{is_correct}')
else:
    print('No predictions found')
