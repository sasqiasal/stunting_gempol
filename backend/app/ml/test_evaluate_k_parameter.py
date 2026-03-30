"""
Test script untuk evaluasi KNN parameter K
Gunakan ini untuk verifikasi bahwa script berjalan dengan benar
"""

import sys
import os

# Untuk development/testing: tambahkan path backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Jika menggunakan dari folder backend
try:
    from app.ml.evaluate_k_parameter import KParameterEvaluator
except ImportError:
    print("❌ Tidak dapat import KParameterEvaluator")
    print("   Pastikan menjalankan dari folder backend atau api")
    sys.exit(1)


def test_evaluator():
    """Test evaluator dengan data mock"""
    print("=" * 80)
    print("TEST: KNN Parameter K Evaluator")
    print("=" * 80)
    
    try:
        # Initialize evaluator
        print("\n1️⃣ Initializing KParameterEvaluator...")
        evaluator = KParameterEvaluator()
        print(f"   ✓ K values: {evaluator.k_values}")
        print(f"   ✓ Num classes: {evaluator.num_classes}")
        print(f"   ✓ Class names: {evaluator.class_names}")
        
        # Try to fetch data from Supabase
        print("\n2️⃣ Fetching data from Supabase...")
        try:
            X_data, y_data = evaluator.fetch_data_from_supabase()
            print(f"   ✓ Fetched {len(X_data)} samples")
        except Exception as e:
            print(f"   ⚠️  Warning: {str(e)}")
            print("   💡 Tip: Pastikan Supabase sudah connected dan ada data di tabel pengukuran")
            print("\n   Creating mock data for testing...")
            
            # Create mock data for testing
            import numpy as np
            np.random.seed(42)
            n_samples = 100
            n_features = 6
            
            X_data = np.random.randn(n_samples, n_features) * 10 + 50
            y_data = np.random.randint(0, 4, n_samples)
            
            print(f"   ✓ Mock data created: {n_samples} samples, {n_features} features")
        
        # Run evaluation
        print("\n3️⃣ Running K parameter evaluation...")
        print("   This may take a moment...\n")
        
        results_dict = {}
        y_true = y_data
        
        for k in evaluator.k_values:
            result = evaluator.evaluate_k(X_data, y_data, k)
            results_dict[k] = result
        
        # Print summary
        print("\n4️⃣ Print summary table...")
        evaluator.print_summary_table(results_dict, y_true)
        
        # Print detailed metrics
        print("\n5️⃣ Print detailed metrics...")
        evaluator.print_detailed_metrics(results_dict)
        
        # Determine best K
        print("\n6️⃣ Determine best K...")
        best_k = evaluator.determine_best_k(results_dict)
        
        print("\n✅ TEST PASSED!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED!\n")
        print(f"Error: {str(e)}")
        
        import traceback
        print("\nTraceback:")
        traceback.print_exc()
        
        return False


if __name__ == "__main__":
    success = test_evaluator()
    sys.exit(0 if success else 1)
