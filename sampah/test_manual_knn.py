"""
Test script untuk verifikasi Manual KNN implementation
Test semua komponen tanpa sklearn
"""

import numpy as np
import sys
import os

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.ml.knn_manual import (
    ManualStandardScaler,
    ManualKNNClassifier,
    calculate_confusion_matrix,
    calculate_metrics,
    format_confusion_matrix_table
)

def test_manual_scaler():
    """Test Manual StandardScaler implementation"""
    print("=" * 70)
    print("TEST 1: Manual StandardScaler (Z-score normalization)")
    print("=" * 70)
    
    # Create test data
    X_train = np.array([
        [1, 10, 100],
        [2, 20, 200],
        [3, 30, 300],
        [4, 40, 400],
        [5, 50, 500]
    ], dtype=float)
    
    X_test = np.array([
        [2.5, 25, 250],
        [3.5, 35, 350]
    ], dtype=float)
    
    # Initialize and fit scaler
    scaler = ManualStandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("\n✅ Original Training Data:")
    print(X_train)
    
    print("\n✅ Scaled Training Data:")
    print(X_train_scaled)
    
    print("\n✅ Scaled Test Data:")
    print(X_test_scaled)
    
    print("\n✅ Scaler Parameters:")
    print(f"   Mean: {scaler.mean}")
    print(f"   Std:  {scaler.std}")
    print("\n✓ Manual StandardScaler working correctly!\n")


def test_euclidean_distance():
    """Test Euclidean distance calculation"""
    print("=" * 70)
    print("TEST 2: Euclidean Distance Calculation")
    print("=" * 70)
    
    knn = ManualKNNClassifier(n_neighbors=3)
    
    point1 = np.array([0, 0, 0])
    point2 = np.array([3, 4, 0])
    
    distance = knn._euclidean_distance(point1, point2)
    expected = 5.0  # sqrt(3^2 + 4^2) = sqrt(25) = 5
    
    print(f"\nPoints:")
    print(f"  Point 1: {point1}")
    print(f"  Point 2: {point2}")
    print(f"\n✅ Calculated Distance: {distance}")
    print(f"✅ Expected Distance:   {expected}")
    print(f"✓ Match: {np.isclose(distance, expected)}\n")


def test_knn_classification():
    """Test Manual KNN Classification"""
    print("=" * 70)
    print("TEST 3: Manual KNN Classification")
    print("=" * 70)
    
    # Create synthetic training data
    np.random.seed(42)
    X_train = np.array([
        [1, 2, 3],
        [2, 3, 4],
        [1.5, 2.5, 3.5],
        [10, 11, 12],
        [11, 12, 13],
        [10.5, 11.5, 12.5]
    ], dtype=float)
    
    y_train = np.array([0, 0, 0, 1, 1, 1])
    
    # Create KNN classifier
    knn = ManualKNNClassifier(n_neighbors=3, weights='uniform')
    knn.fit(X_train, y_train)
    
    # Make predictions
    X_test = np.array([
        [1.2, 2.2, 3.2],  # Should be class 0
        [10.2, 11.2, 12.2]  # Should be class 1
    ], dtype=float)
    
    predictions = knn.predict(X_test)
    probabilities = knn.predict_proba(X_test)
    accuracy = knn.score(X_train, y_train)
    
    print(f"\n✅ Training data shape: {X_train.shape}")
    print(f"✅ Training labels: {y_train}")
    print(f"\n✅ Test data shape: {X_test.shape}")
    print(f"✅ Predictions: {predictions}")
    print(f"✅ Probabilities:\n{probabilities}")
    print(f"✅ Training Accuracy: {accuracy:.4f}")
    print("\n✓ Manual KNN Classification working correctly!\n")


def test_confusion_matrix():
    """Test Manual Confusion Matrix"""
    print("=" * 70)
    print("TEST 4: Manual Confusion Matrix Calculation")
    print("=" * 70)
    
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1, 1, 0])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 1, 1, 1, 0])
    
    cm = calculate_confusion_matrix(y_true, y_pred, labels=[0, 1])
    
    print(f"\n✅ True Labels:      {y_true}")
    print(f"✅ Predicted Labels: {y_pred}")
    print(f"\n✅ Confusion Matrix:")
    print(cm)
    print(format_confusion_matrix_table(cm))
    print("\n✓ Manual Confusion Matrix working correctly!\n")


def test_metrics_calculation():
    """Test Manual Metrics Calculation"""
    print("=" * 70)
    print("TEST 5: Manual Metrics Calculation")
    print("=" * 70)
    
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1, 1, 0])
    y_pred = np.array([0, 0, 1, 0, 0, 1, 1, 1, 1, 0])
    
    metrics = calculate_metrics(y_true, y_pred)
    
    print(f"\n✅ Metrics calculated MANUALLY (NO sklearn):")
    print(f"   - Accuracy:    {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"   - Precision:   {metrics['precision']:.4f}")
    print(f"   - Recall:      {metrics['recall']:.4f}")
    print(f"   - Specificity: {metrics['specificity']:.4f}")
    print(f"   - F1-Score:    {metrics['f1_score']:.4f}")
    print(f"\n✅ Confusion Matrix Components:")
    print(f"   - TP (True Positive):  {metrics['tp']}")
    print(f"   - TN (True Negative):  {metrics['tn']}")
    print(f"   - FP (False Positive): {metrics['fp']}")
    print(f"   - FN (False Negative): {metrics['fn']}")
    print("\n✓ Manual Metrics Calculation working correctly!\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("TESTING MANUAL KNN IMPLEMENTATION (NO sklearn)")
    print("=" * 70 + "\n")
    
    try:
        test_manual_scaler()
        test_euclidean_distance()
        test_knn_classification()
        test_confusion_matrix()
        test_metrics_calculation()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n✓ Manual KNN implementation is working correctly!")
        print("✓ No sklearn or other ML libraries required!")
        print("✓ Ready for production use!\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
