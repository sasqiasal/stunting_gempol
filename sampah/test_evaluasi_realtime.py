#!/usr/bin/env python3
"""
Test script untuk memverifikasi backend evaluasi/realtime endpoint
Jalankan dengan: python test_evaluasi_realtime.py

Memeriksa:
1. Server connectivity
2. Endpoint accessibility
3. Response structure
4. Data completeness
"""

import requests
import json
import sys

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
EVALUASI_ENDPOINT = f"{BACKEND_URL}/api/v1/evaluasi/realtime"
TIMEOUT = 10

def test_endpoint():
    """Test the evaluasi/realtime endpoint"""
    
    print("\n" + "="*70)
    print("  TESTING BACKEND EVALUASI/REALTIME ENDPOINT")
    print("="*70 + "\n")
    
    # Test 1: Server connectivity
    print("1️⃣  Testing server connectivity...")
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=TIMEOUT)
        if response.status_code == 200:
            print("   ✅ Backend server is running\n")
        else:
            print(f"   ❌ Backend returned status {response.status_code}\n")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        print(f"   Make sure to run: python -m uvicorn main:app --reload\n")
        return False
    
    # Test 2: Call endpoint
    print("2️⃣  Calling endpoint: GET /api/v1/evaluasi/realtime")
    try:
        response = requests.get(EVALUASI_ENDPOINT, timeout=TIMEOUT)
        print(f"   Response Status: {response.status_code}\n")
        
        if response.status_code != 200:
            print(f"   ❌ Expected 200, got {response.status_code}\n")
            return False
        
        # Parse JSON
        data = response.json()
        
        # Check structure
        if data.get("status") != "success":
            print(f"   ❌ Response status is not 'success'\n")
            return False
        
        eval_data = data.get("data", {})
        
        if not eval_data.get("success", False):
            error = eval_data.get("error", "Unknown error")
            print(f"   ❌ Evaluation failed: {error}\n")
            return False
        
        print("   ✅ Endpoint returned valid response\n")
        
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timed out after {TIMEOUT}s\n")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False
    
    # Test 3: Verify response structure
    print("3️⃣  Verifying response structure...\n")
    
    required_fields = [
        "metadata",
        "binary_classification",
        "multiclass_classification",
        "k_comparison",
        "distribution"
    ]
    
    for field in required_fields:
        if field in eval_data:
            print(f"   ✅ Contains '{field}'")
        else:
            print(f"   ❌ Missing '{field}'")
            return False
    
    print()
    
    # Test 4: Display data summary
    print("4️⃣  Data Summary:\n")
    
    metadata = eval_data.get("metadata", {})
    print(f"   📊 Total Data: {metadata.get('total_data', 'N/A')}")
    print(f"   ⏰ Timestamp: {metadata.get('evaluation_timestamp', 'N/A')}\n")
    
    binary_metrics = eval_data.get("binary_classification", {}).get("metrics", {})
    if binary_metrics:
        print("   📈 Binary Classification Metrics:")
        print(f"      • Accuracy:  {binary_metrics.get('accuracy_percent', 0):.2f}%")
        print(f"      • Precision: {binary_metrics.get('precision_percent', 0):.2f}%")
        print(f"      • Recall:    {binary_metrics.get('recall_percent', 0):.2f}%")
        print(f"      • F1-Score:  {binary_metrics.get('f1_score_percent', 0):.2f}%\n")
    
    k_comp = eval_data.get("k_comparison", [])
    if k_comp:
        print(f"   🔢 K Comparison ({len(k_comp)} K values):")
        for item in k_comp:
            print(f"      • K={item['k']}: Acc={item['accuracy_percent']:.2f}%, F1={item['f1_score_percent']:.2f}%")
        print()
    
    dist = eval_data.get("distribution", {})
    if dist:
        print("   👶 Data Distribution:")
        print(f"      • Normal:   {dist.get('normal_count', 0)} ({dist.get('normal_percent', 0):.1f}%)")
        print(f"      • Stunting: {dist.get('stunting_count', 0)} ({dist.get('stunting_percent', 0):.1f}%)\n")
    
    # Test 5: Confusion matrix
    print("5️⃣  Confusion Matrix (4×4):\n")
    
    cm_4x4 = eval_data.get("multiclass_classification", {}).get("metrics", {}).get("confusion_matrix", [])
    if cm_4x4:
        labels = ["Normal+Baik", "Normal+Kurang", "Stunting+Baik", "Stunting+Kurang"]
        
        # Print header
        print("   " + " "*20 + "PREDICTED")
        print("   " + " "*18 + "".join(f"{l:>15}".replace(" ", "") for l in labels[:2]))
        print("   " + " "*18 + "".join(f"{l:>15}" for l in labels[2:]))
        
        # Print rows
        for i, row in enumerate(cm_4x4):
            label_short = labels[i].replace("+", "+\n   " + " "*16)
            print(f"   ACTUAL {label_short[:15]:>15} ", end="")
            for j, val in enumerate(row):
                print(f"{val:>15}", end="")
            print()
        print()
    
    return True

if __name__ == "__main__":
    success = test_endpoint()
    
    if success:
        print("="*70)
        print("  ✅ ALL TESTS PASSED! Backend evaluasi endpoint is ready!")
        print("="*70 + "\n")
        sys.exit(0)
    else:
        print("="*70)
        print("  ❌ TESTS FAILED! Check the errors above.")
        print("="*70 + "\n")
        sys.exit(1)
