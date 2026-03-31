"""
Contoh Integrasi: Evaluasi Model KNN dengan Confusion Matrix

Menunjukkan cara menggunakan evaluate_knn_sklearn.py bersama model KNN sklearn
untuk melakukan evaluasi lengkap pada data test from database or file.
"""

import numpy as np
from typing import Tuple
import sys
from pathlib import Path

# ============================================================================
# EXAMPLE 1: Evaluasi dengan Data Simulasi
# ============================================================================

def example_1_evaluasi_data_simulasi():
    """
    Contoh sederhana: Evaluasi dengan data simulasi
    Cocok untuk testing awal
    """
    print("\n" + "=" * 100)
    print("EXAMPLE 1: Evaluasi dengan Data Simulasi")
    print("=" * 100)
    
    from evaluate_knn_sklearn import evaluate_knn_model
    
    # Simulasi 50 sampel data test
    np.random.seed(42)
    y_true = np.random.choice([0, 1, 2, 3], size=50)
    
    # Simulasi prediksi (dengan beberapa error)
    y_pred = y_true.copy()
    error_indices = np.random.choice(50, size=8, replace=False)
    y_pred[error_indices] = np.random.choice([0, 1, 2, 3], size=8)
    
    print(f"\n📊 Data Simulasi:")
    print(f"  - Total samples: {len(y_true)}")
    print(f"  - Ground truth distribution: {np.bincount(y_true)}")
    print(f"  - Errors introduced: {8}")
    
    # Jalankan evaluasi
    print("\n🔄 Running evaluation...")
    cm, metrics_all = evaluate_knn_model(y_true, y_pred)
    
    print("\n✅ Evaluation complete!")


# ============================================================================
# EXAMPLE 2: Evaluasi dengan Data dari CSV
# ============================================================================

def example_2_evaluasi_dari_csv(csv_file: str = "backend/data_latih_stunting.csv"):
    """
    Contoh: Evaluasi dengan data dari CSV file
    Menggunakan kolom y_true (dari Z-Score) dan hasil prediksi KNN
    
    CSV harus memiliki kolom:
    - status_stunting (label aktual) dari Z-Score
    - predicted_label (hasil prediksi model KNN)
    """
    print("\n" + "=" * 100)
    print("EXAMPLE 2: Evaluasi dengan Data dari CSV")
    print("=" * 100)
    
    try:
        import pandas as pd
        from evaluate_knn_sklearn import evaluate_knn_model
        
        # Baca CSV
        df = pd.read_csv(csv_file)
        print(f"\n📄 Loaded CSV: {csv_file}")
        print(f"  - Rows: {len(df)}")
        print(f"  - Columns: {list(df.columns)}")
        
        # Extract y_true dan y_pred
        # Sesuaikan nama kolom dengan data Anda
        if 'status_stunting' in df.columns and 'predicted_label' in df.columns:
            y_true = df['status_stunting'].values
            y_pred = df['predicted_label'].values
            
            print(f"\n📊 Extracted data:")
            print(f"  - y_true distribution: {np.bincount(y_true)}")
            print(f"  - y_pred distribution: {np.bincount(y_pred)}")
            
            # Evaluasi
            print("\n🔄 Running evaluation...")
            cm, metrics_all = evaluate_knn_model(y_true, y_pred)
            
            print("\n✅ Evaluation complete!")
        else:
            print(f"\n❌ CSV tidak memiliki kolom yang diperlukan:")
            print(f"   Diperlukan: 'status_stunting' dan 'predicted_label'")
            print(f"   Kolom yang ada: {list(df.columns)}")
    
    except FileNotFoundError:
        print(f"\n❌ File tidak ditemukan: {csv_file}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


# ============================================================================
# EXAMPLE 3: Evaluasi dengan Model KNN Real
# ============================================================================

def example_3_evaluasi_dengan_model_knn_real():
    """
    Contoh: Evaluasi dengan model KNN yang sesungguhnya
    Memuat model, melakukan prediksi, kemudian evaluasi
    """
    print("\n" + "=" * 100)
    print("EXAMPLE 3: Evaluasi dengan Model KNN Real")
    print("=" * 100)
    
    try:
        # Import model KNN
        # NOTE: Sesuaikan path dengan struktur project Anda
        sys.path.insert(0, str(Path(__file__).parent / "api"))
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        
        from app.ml.knn_sklearn import StuntingKNNModel
        from evaluate_knn_sklearn import evaluate_knn_model
        import pandas as pd
        
        print("\n🔧 Setting up model...")
        
        # Buat atau load model
        model = StuntingKNNModel(n_neighbors=5)
        
        # Simulasi training data
        print("📊 Generating training data...")
        np.random.seed(42)
        n_train = 100
        X_train = np.random.randn(n_train, 6)  # 6 features
        y_train = np.random.choice([0, 1, 2, 3], size=n_train)
        
        # Train model
        print("⚙️  Training model...")
        info = model.train(X_train, y_train)
        print(f"  - Train accuracy: {info['train_accuracy']}")
        print(f"  - Total samples: {info['n_samples']}")
        
        # Simulasi test data
        print("📊 Generating test data...")
        n_test = 32
        X_test = np.random.randn(n_test, 6)
        y_true = np.random.choice([0, 1, 2, 3], size=n_test)
        
        # Prediksi
        print("🔮 Making predictions...")
        y_pred = []
        for i in range(n_test):
            features = X_test[i:i+1]
            pred, conf = model.predict(features)
            y_pred.append(pred)
        y_pred = np.array(y_pred)
        
        print(f"  - Predictions: {np.bincount(y_pred)}")
        
        # Evaluasi
        print("\n🔄 Running evaluation...")
        cm, metrics_all = evaluate_knn_model(y_true, y_pred)
        
        print("\n✅ Evaluation complete!")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print(f"   Make sure model files are in the correct location")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# EXAMPLE 4: Save dan Load Hasil Evaluasi
# ============================================================================

def example_4_save_load_hasil_evaluasi():
    """
    Contoh: Simpan hasil evaluasi ke file dan load kembali
    """
    print("\n" + "=" * 100)
    print("EXAMPLE 4: Save & Load Hasil Evaluasi")
    print("=" * 100)
    
    import pickle
    from evaluate_knn_sklearn import evaluate_knn_model
    
    # Generate data
    np.random.seed(42)
    y_true = np.random.choice([0, 1, 2, 3], size=50)
    y_pred = np.random.choice([0, 1, 2, 3], size=50)
    
    # Evaluasi
    print("\n🔄 Running evaluation...")
    cm, metrics_all = evaluate_knn_model(y_true, y_pred)
    
    # Save hasil
    print("\n💾 Saving results...")
    
    # Save confusion matrix
    with open("confusion_matrix.pkl", "wb") as f:
        pickle.dump(cm, f)
    print("  ✅ confusion_matrix.pkl saved")
    
    # Save metrics
    with open("metrics.pkl", "wb") as f:
        pickle.dump(metrics_all, f)
    print("  ✅ metrics.pkl saved")
    
    # Load hasil
    print("\n📖 Loading results...")
    
    with open("confusion_matrix.pkl", "rb") as f:
        cm_loaded = pickle.load(f)
    print("  ✅ confusion_matrix.pkl loaded")
    print(f"     Shape: {cm_loaded.shape}")
    
    with open("metrics.pkl", "rb") as f:
        metrics_loaded = pickle.load(f)
    print("  ✅ metrics.pkl loaded")
    print(f"     Classes: {list(metrics_loaded.keys())}")
    
    print("\n✅ Save/Load complete!")


# ============================================================================
# EXAMPLE 5: Custom Analysis dari Hasil Evaluasi
# ============================================================================

def example_5_custom_analysis():
    """
    Contoh: Custom analysis dari hasil confusion matrix dan metrics
    """
    print("\n" + "=" * 100)
    print("EXAMPLE 5: Custom Analysis dari Hasil Evaluasi")
    print("=" * 100)
    
    from evaluate_knn_sklearn import evaluate_knn_model
    
    # Generate data
    np.random.seed(42)
    y_true = np.random.choice([0, 1, 2, 3], size=50)
    y_pred = np.random.choice([0, 1, 2, 3], size=50)
    
    # Evaluasi
    print("\n🔄 Running evaluation...")
    cm, metrics_all = evaluate_knn_model(y_true, y_pred)
    
    print("\n" + "=" * 100)
    print("CUSTOM ANALYSIS")
    print("=" * 100)
    
    # Analisis 1: Kelas mana yang paling akurat?
    print("\n1️⃣  Kelas dengan recall tertinggi (paling akurat mendeteksi positif):")
    class_names = [
        "Normal + Gizi Baik",
        "Normal + Kurang Gizi",
        "Stunting + Gizi Baik",
        "Stunting + Kurang Gizi"
    ]
    
    recalls = {}
    for class_idx in range(4):
        tp = metrics_all[class_idx]["TP"]
        fn = metrics_all[class_idx]["FN"]
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        recalls[class_idx] = recall
    
    best_class = max(recalls, key=recalls.get)
    print(f"   Class {best_class} ({class_names[best_class]}): Recall = {recalls[best_class]:.2%}")
    
    # Analisis 2: Kelas mana yang paling sering salah?
    print("\n2️⃣  Kelas dengan error tertinggi (paling sering salah):")
    errors = {}
    for class_idx in range(4):
        fp = metrics_all[class_idx]["FP"]
        fn = metrics_all[class_idx]["FN"]
        total_error = fp + fn
        errors[class_idx] = total_error
    
    worst_class = max(errors, key=errors.get)
    print(f"   Class {worst_class} ({class_names[worst_class]}): Total errors = {errors[worst_class]}")
    
    # Analisis 3: Confusion mapping - terbanyak diprediksi apa?
    print("\n3️⃣  Confusion mapping (terbanyak diprediksi sebagai kelas apa):")
    for i in range(4):
        for j in range(4):
            if cm[i, j] > 0:
                print(f"   Aktual {i} ({class_names[i][:20]}...) → "
                      f"Pred {j} ({class_names[j][:20]}...): {cm[i, j]} sampel")
    
    # Analisis 4: Total accuracy per kelas
    print("\n4️⃣  Accuracy per kelas:")
    for class_idx in range(4):
        tp = metrics_all[class_idx]["TP"]
        total_in_class = cm[class_idx].sum()
        accuracy = tp / total_in_class if total_in_class > 0 else 0
        print(f"   Class {class_idx}: {accuracy:.2%} ({tp}/{total_in_class})")
    
    print("\n✅ Custom analysis complete!")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("CONTOH INTEGRASI: EVALUASI MODEL KNN DENGAN CONFUSION MATRIX")
    print("=" * 100)
    
    print("\nPilih contoh yang ingin dijalankan:")
    print("1. Example 1: Evaluasi dengan Data Simulasi")
    print("2. Example 2: Evaluasi dari CSV")
    print("3. Example 3: Evaluasi dengan Model KNN Real")
    print("4. Example 4: Save & Load Hasil Evaluasi")
    print("5. Example 5: Custom Analysis")
    print("6. Run All Examples")
    
    choice = input("\nMasukkan pilihan (1-6): ").strip()
    
    if choice == "1":
        example_1_evaluasi_data_simulasi()
    elif choice == "2":
        example_2_evaluasi_dari_csv()
    elif choice == "3":
        example_3_evaluasi_dengan_model_knn_real()
    elif choice == "4":
        example_4_save_load_hasil_evaluasi()
    elif choice == "5":
        example_5_custom_analysis()
    elif choice == "6":
        example_1_evaluasi_data_simulasi()
        example_2_evaluasi_dari_csv()
        example_3_evaluasi_dengan_model_knn_real()
        example_4_save_load_hasil_evaluasi()
        example_5_custom_analysis()
    else:
        print("\n❌ Pilihan tidak valid")
