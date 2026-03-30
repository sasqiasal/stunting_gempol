#!/usr/bin/env python3
"""Test script untuk verifikasi evaluasi KNN yang diperbaiki"""

import requests
import json

def test_global_evaluation():
    """Test endpoint /evaluasi/global dengan train-test split"""
    print("\n" + "="*80)
    print("TEST: GLOBAL EVALUATION (Train-Test Split)")
    print("="*80)
    
    try:
        response = requests.get('http://127.0.0.1:8000/api/v1/evaluasi/global')
        
        if response.status_code != 200:
            print(f"❌ Error: Status {response.status_code}")
            print(response.text[:500])
            return False
        
        data = response.json()['data']
        
        print("\n📊 DATA SPLIT:")
        print(f"  Training samples: {data.get('training_samples')} (80%)")
        print(f"  Testing samples: {data.get('testing_samples')} (20%)")
        print(f"  Total samples: {data.get('total_samples')}")
        print(f"  Split method: {data.get('evaluation_split')}")
        
        print("\n📈 METRICS (on TEST SET):")
        print(f"  Overall Accuracy: {data.get('overall_accuracy')}")
        print(f"  Macro Precision: {data.get('macro_average', {}).get('precision')}")
        print(f"  Macro Recall: {data.get('macro_average', {}).get('recall')}")
        print(f"  Macro F1-Score: {data.get('macro_average', {}).get('f1_score')}")
        
        print("\n🔲 CONFUSION MATRIX (4x4):")
        cm = data.get('confusion_matrix', [])
        if cm:
            labels = ['Normal+GB', 'Normal+KG', 'Stunting+GB', 'Stunting+KG']
            print(f"{'':15}", end='')
            for label in labels:
                print(f"{label:>12}", end='')
            print()
            for i, row in enumerate(cm):
                print(f"{labels[i]:15}", end='')
                for val in row:
                    print(f"{val:>12}", end='')
                print()
        
        print("\n✓ Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {str(e)}")
        return False

def test_k_comparison():
    """Test endpoint /evaluasi/global-k-comparison dengan train-test split"""
    print("\n" + "="*80)
    print("TEST: K COMPARISON (Train-Test Split)")
    print("="*80)
    
    try:
        response = requests.get('http://127.0.0.1:8000/api/v1/evaluasi/global-k-comparison')
        
        if response.status_code != 200:
            print(f"❌ Error: Status {response.status_code}")
            print(response.text[:500])
            return False
        
        data = response.json()['data']
        
        print("\n📊 DATA SPLIT:")
        eval_info = data.get('evaluation_info', {})
        print(f"  Training samples: {eval_info.get('training_samples')}")
        print(f"  Testing samples: {eval_info.get('testing_samples')}")
        print(f"  Total samples: {eval_info.get('total_samples')}")
        print(f"  Split method: {eval_info.get('split_ratio')}")
        
        print("\n📊 K COMPARISON (on TEST SET):")
        print(f"{'K':>5} {'Accuracy':>12} {'Precision':>12} {'Recall':>12} {'F1-Score':>12}")
        print("-" * 55)
        
        for item in data.get('k_comparison', []):
            print(f"{item['k']:>5} {item['accuracy']:>12.4f} {item['precision']:>12.4f} {item['recall']:>12.4f} {item['f1_score']:>12.4f}")
        
        print(f"\n🏆 Best K:")
        best_k = data.get('best_k', {})
        print(f"  K value: {best_k.get('k')}")
        print(f"  Accuracy: {best_k.get('accuracy')}")
        print(f"  Recommendation: {best_k.get('recommendation')}")
        
        print("\n✓ Test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🧪 TESTING IMPROVED EVALUATION SYSTEM")
    print("=" * 80)
    
    test1 = test_global_evaluation()
    test2 = test_k_comparison()
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"  Global Evaluation: {'✓ PASS' if test1 else '❌ FAIL'}")
    print(f"  K Comparison: {'✓ PASS' if test2 else '❌ FAIL'}")
    print("="*80 + "\n")
