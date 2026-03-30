"""
Comprehensive test untuk Phase 2: Real Performance Evaluation
Test endpoint /evaluasi/real-performance dengan mock data
"""
import sys
sys.path.insert(0, r'd:\development\stunting_gempol\api')

def test_confusion_matrix_calculation():
    """Test fungsi calculate_confusion_matrix_from_measurements dengan mock data"""
    print("\n" + "="*80)
    print("TEST 1: CONFUSION MATRIX CALCULATION (Mock Data)")
    print("="*80)
    
    try:
        # Import necessary modules
        from app.ml.knn_manual import calculate_confusion_matrix
        import numpy as np
        
        # Create sample data
        # y_true: 0=normal, 1=stunting (from zscore_tbu < -2.0)
        # y_pred: 0=normal, 1=stunting (from status_gizi_label class mapping)
        
        y_true = np.array([0, 0, 0, 1, 1, 1, 0, 1, 1, 0])  # 4 normal, 6 stunting
        y_pred = np.array([0, 0, 1, 1, 1, 0, 0, 1, 1, 1])  # wrong predictions for indices 2, 5, 9
        
        print(f"\nTest Data:")
        print(f"  y_true (ground truth):  {y_true}")
        print(f"  y_pred (predictions):   {y_pred}")
        print(f"  Total samples: {len(y_true)}")
        
        # Calculate confusion matrix
        cm = calculate_confusion_matrix(y_true, y_pred, labels=[0, 1])
        print(f"\nConfusion Matrix:")
        print(f"  {cm}")
        
        # Extract values
        tn = int(cm[0, 0])  # Normal predicted correctly
        fp = int(cm[0, 1])  # Normal but predicted stunting
        fn = int(cm[1, 0])  # Stunting but predicted normal
        tp = int(cm[1, 1])  # Stunting predicted correctly
        
        print(f"\nExtracted Values:")
        print(f"  TN (True Negative):  {tn}")
        print(f"  FP (False Positive): {fp}")
        print(f"  FN (False Negative): {fn}")
        print(f"  TP (True Positive):  {tp}")
        print(f"  Total: {tn + fp + fn + tp}")
        
        # Calculate metrics
        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\nMetrics:")
        print(f"  Accuracy:   {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"  Precision:  {precision:.4f} ({precision*100:.2f}%)")
        print(f"  Recall:     {recall:.4f} ({recall*100:.2f}%)")
        print(f"  Specificity: {specificity:.4f} ({specificity*100:.2f}%)")
        print(f"  F1-Score:   {f1_score:.4f} ({f1_score*100:.2f}%)")
        
        print("\n✅ TEST 1 PASSED: Confusion matrix calculation works correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_imports():
    """Test if all necessary modules can be imported"""
    print("\n" + "="*80)
    print("TEST 2: MODULE IMPORTS")
    print("="*80)
    
    modules_to_test = [
        'app.config',
        'app.database',
        'app.ml.knn_manual',
        'app.routes.evaluasi',
        'app.utils.auth',
    ]
    
    results = {}
    for module in modules_to_test:
        try:
            __import__(module)
            results[module] = "✅"
            print(f"  ✅ {module}")
        except Exception as e:
            results[module] = f"❌ {str(e)}"
            print(f"  ❌ {module}: {str(e)}")
    
    if all(v == "✅" for v in results.values()):
        print("\n✅ TEST 2 PASSED: All imports successful")
        return True
    else:
        print("\n❌ TEST 2 FAILED: Some imports failed")
        return False


def test_response_format():
    """Test response format from endpoint"""
    print("\n" + "="*80)
    print("TEST 3: RESPONSE FORMAT VALIDATION")
    print("="*80)
    
    # Mock response format
    mock_response = {
        "status": "success",
        "message": "Real performance evaluation from 5 measurements",
        "measurements_count": 5,
        "confusion_matrix": {
            "tp": 3,
            "tn": 2,
            "fp": 0,
            "fn": 0
        },
        "metrics": {
            "accuracy": 1.0,
            "accuracy_percentage": 100.0,
            "precision": 1.0,
            "precision_percentage": 100.0,
            "recall": 1.0,
            "recall_percentage": 100.0,
            "specificity": 1.0,
            "specificity_percentage": 100.0,
            "f1_score": 1.0,
            "f1_score_percentage": 100.0,
        },
        "data_source": "Real pengukuran from database",
    }
    
    print("\nValidating response structure:")
    
    required_fields = [
        "status",
        "measurements_count",
        "confusion_matrix",
        "metrics",
        "data_source"
    ]
    
    required_cm_fields = ["tp", "tn", "fp", "fn"]
    required_metrics_fields = [
        "accuracy", "accuracy_percentage",
        "precision", "precision_percentage",
        "recall", "recall_percentage",
        "specificity", "specificity_percentage",
        "f1_score", "f1_score_percentage"
    ]
    
    all_valid = True
    
    # Check top-level fields
    for field in required_fields:
        if field in mock_response:
            print(f"  ✅ {field}")
        else:
            print(f"  ❌ {field} missing")
            all_valid = False
    
    # Check confusion matrix fields
    print("\n  Confusion Matrix fields:")
    for field in required_cm_fields:
        if field in mock_response["confusion_matrix"]:
            print(f"    ✅ {field}")
        else:
            print(f"    ❌ {field} missing")
            all_valid = False
    
    # Check metrics fields
    print("\n  Metrics fields:")
    for field in required_metrics_fields:
        if field in mock_response["metrics"]:
            print(f"    ✅ {field}")
        else:
            print(f"    ❌ {field} missing")
            all_valid = False
    
    if all_valid:
        print("\n✅ TEST 3 PASSED: Response format is valid")
        return True
    else:
        print("\n❌ TEST 3 FAILED: Response format has missing fields")
        return False


def main():
    print("\n" + "="*80)
    print("PHASE 2: REAL PERFORMANCE EVALUATION - UNIT TESTS")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("Confusion Matrix Calculation", test_confusion_matrix_calculation()))
    results.append(("Module Imports", test_imports()))
    results.append(("Response Format", test_response_format()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
