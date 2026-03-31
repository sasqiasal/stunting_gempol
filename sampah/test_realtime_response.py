import requests
import json

try:
    r = requests.get('http://127.0.0.1:8000/api/v1/evaluasi/realtime', timeout=10)
    print(f'Status: {r.status_code}')
    print(f'Response:')
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f'ERROR: {e}')
