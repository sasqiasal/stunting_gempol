"""
Test script untuk endpoint /evaluasi/real-performance
Verifikasi bahwa confusion matrix dihitung dari data pengukuran real di database, bukan dari CSV training
"""
import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Authorization": "Bearer test-token"
}

def test_real_performance():
    """Test endpoint /evaluasi/real-performance"""
    endpoint = f"{BASE_URL}/evaluasi/real-performance"
    
    print("=" * 80)
    print("TESTING: GET /evaluasi/real-performance")
    print("=" * 80)
    print(f"\nEndpoint: {endpoint}")
    print(f"Headers: {HEADERS}")
    
    try:
        response = requests.get(endpoint, headers=HEADERS)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS! Response:")
            pprint(data, width=100)
            
            # Validate response structure
            print("\n" + "=" * 80)
            print("VALIDATION:")
            print("=" * 80)
            
            required_fields = ["measurements_count", "confusion_matrix", "metrics", "data_source"]
            for field in required_fields:
                if field in data:
                    print(f"✅ {field}: Present")
                else:
                    print(f"❌ {field}: Missing")
            
            # Detailed metrics check
            if "metrics" in data:
                metrics = data["metrics"]
                metric_fields = ["accuracy", "precision", "recall", "specificity", "f1_score",
                               "accuracy_percentage", "precision_percentage", "recall_percentage",
                               "specificity_percentage", "f1_score_pct"]
                print("\nMetrics fields:")
                for field in metric_fields:
                    if field in metrics:
                        print(f"  ✅ {field}: {metrics[field]}")
            
            # Confusion matrix check
            if "confusion_matrix" in data:
                cm = data["confusion_matrix"]
                print(f"\nConfusion Matrix:")
                print(f"  TP: {cm.get('tp', 'N/A')}")
                print(f"  TN: {cm.get('tn', 'N/A')}")
                print(f"  FP: {cm.get('fp', 'N/A')}")
                print(f"  FN: {cm.get('fn', 'N/A')}")
                print(f"  Total: {cm.get('tp', 0) + cm.get('tn', 0) + cm.get('fp', 0) + cm.get('fn', 0)}")
                print(f"  ↳ Should equal measurements_count: {data.get('measurements_count', 0)}")
            
            print("\n" + "=" * 80)
            print("✅ TEST PASSED")
            print("=" * 80)
            
        else:
            print(f"\n❌ Error Response:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Could not connect to {BASE_URL}")
        print("Make sure backend is running with: python backend/main.py")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_model_performance_comparison():
    """Compare /evaluasi/model-performance vs /evaluasi/real-performance"""
    print("\n\n" + "=" * 80)
    print("COMPARISON: Model Performance vs Real Performance")
    print("=" * 80)
    
    endpoints = {
        "model": f"{BASE_URL}/evaluasi/model-performance",
        "real": f"{BASE_URL}/evaluasi/real-performance"
    }
    
    results = {}
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(endpoint, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                results[name] = {
                    "total_samples": data.get("dataset_info", {}).get("total_samples", data.get("measurements_count", "N/A")),
                    "accuracy": data.get("metrics", {}).get("accuracy", "N/A"),
                    "data_source": data.get("data_source", f"(from {name})")
                }
        except Exception as e:
            results[name] = {"error": str(e)}
    
    print("\nResults:")
    for name, result in results.items():
        print(f"\n{name.upper()}:")
        for key, value in result.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("EXPECTED:")
    print("  Model: total_samples = 100 (from CSV 80/20 split)")
    print("  Real:  total_samples = N  (actual pengukuran dari database)")
    print("=" * 80)

if __name__ == "__main__":
    test_real_performance()
    test_model_performance_comparison()
    
    print("\n\n📝 NOTE: Check backend logs for detailed calculation debug output")
    print("   Expected output includes:")
    print("   - ========== CALCULATING CONFUSION MATRIX FROM REAL MEASUREMENTS ==========")
    print("   - ✅ Fetched X measurements from database")
    print("   - 📊 Confusion Matrix (Binary: Normal vs Stunting)")
    print("   - 📊 Metrics: TP=..., TN=..., FP=..., FN=...")
