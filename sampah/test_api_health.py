import urllib.request
import traceback

try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/health")
    with urllib.request.urlopen(req) as res:
        print("Status:", res.status)
        print("Body:", res.read().decode('utf-8'))
except urllib.error.URLError as e:
    print("URLError:", getattr(e, 'reason', e))
except Exception as e:
    traceback.print_exc()
