#!/usr/bin/env python
"""
Test script untuk verify evaluasi model KNN bekerja dengan benar
Tanpa perlu running API server
"""

import os
import sys
import numpy as np
import pandas as pd

# Add API path to sys.path
api_path = os.path.join(os.path.dirname(__file__), 'api')
if api_path not in sys.path:
    sys.path.insert(0, api_path)

from app.ml.knn_manual import ManualKNNClassifier, ManualStandardScaler, calculate_confusion_matrix

def find_csv_path():
    """Find data_latih_stunting.csv"""
    possible_paths = [
        "backend/data_latih_stunting.csv",
        "./backend/data_latih_stunting.csv",
        "data_latih_stunting.csv",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    raise FileNotFoundError(f"CSV not found. Tried: {possible_paths}")


def test_evaluation():
    """Test evaluasi model KNN dengan dataset CSV"""
    
    print("=" * 80)
    print("🧪 TEST EVALUASI MODEL KNN")
    print("=" * 80)
    
    # 1. LOAD CSV
    print("\n[1/5] Loading CSV dataset...")
    try:
        csv_path = find_csv_path()
        df = pd.read_csv(csv_path)
        print(f"✅ CSV loaded: {csv_path}")
        print(f"   Samples: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return False
    
    # 2. PREPARE DATA
    print("\n[2/5] Preparing features and labels...")
    try:
        X_list = []
        y_list = []
        
        for idx, row in df.iterrows():
            label_val = row.get("status_stunting")
            if pd.isna(label_val):
                continue
            label = int(label_val)
            if label not in [0, 1, 2, 3]:
                continue
            
            y_list.append(label)
            jk_enc = 1 if str(row.get("jenis_kelamin", "L")).upper() == "L" else 0
            X_list.append([
                jk_enc,
                float(row.get("usia_bulan", 0)),
                float(row.get("tinggi_badan", 0)),
                float(row.get("berat_badan", 0)),
                float(row.get("lingkar_lengan", 0)),
                float(row.get("lingkar_kepala", 0)),
            ])
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        print(f"✅ Data prepared:")
        print(f"   Total samples: {len(X)}")
        print(f"   Features: {X.shape[1]}")
        print(f"   Classes distribution: {dict(zip(*np.unique(y, return_counts=True)))}")
        
        if len(X) == 0:
            print("❌ No valid data found")
            return False
    except Exception as e:
        print(f"❌ Failed to prepare data: {e}")
        return False
    
    # 3. TRAIN/TEST SPLIT
    print("\n[3/5] Splitting data (80/20 stratified)...")
    try:
        # Manual stratified split
        np.random.seed(42)
        train_indices = []
        test_indices = []
        
        for class_label in np.unique(y):
            class_mask = np.where(y == class_label)[0]
            np.random.shuffle(class_mask)
            split_point = int(len(class_mask) * 0.8)
            train_indices.extend(class_mask[:split_point])
            test_indices.extend(class_mask[split_point:])
        
        X_train = X[train_indices]
        y_train = y[train_indices]
        X_test = X[test_indices]
        y_test = y[test_indices]
        
        print(f"✅ Data split:")
        print(f"   Train: {len(X_train)} samples")
        print(f"   Test: {len(X_test)} samples")
        print(f"   Train classes: {dict(zip(*np.unique(y_train, return_counts=True)))}")
        print(f"   Test classes: {dict(zip(*np.unique(y_test, return_counts=True)))}")
    except Exception as e:
        print(f"❌ Failed to split data: {e}")
        return False
    
    # 4. SCALE & TRAIN
    print("\n[4/5] Scaling and training KNN...")
    try:
        scaler = ManualStandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        knn = ManualKNNClassifier(n_neighbors=5, weights='distance')
        knn.fit(X_train_scaled, y_train)
        
        print(f"✅ Model trained:")
        print(f"   K=5, distance-weighted voting")
        print(f"   Training samples: {len(X_train)}")
    except Exception as e:
        print(f"❌ Failed to train: {e}")
        return False
    
    # 5. PREDICT & EVALUATE
    print("\n[5/5] Predicting and calculating metrics...")
    try:
        y_pred = knn.predict(X_test_scaled)
        
        # Confusion matrix
        cm = calculate_confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3])
        
        # Accuracy
        accuracy = np.mean(y_test == y_pred)
        
        print(f"✅ Predictions completed:")
        print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"\n📊 Confusion Matrix (4x4):")
        print(f"   Rows=Actual, Cols=Predicted")
        labels_short = ["N+GB", "N+KG", "S+GB", "S+KG"]
        print(f"     {' '.join(f'{lbl:>6}' for lbl in labels_short)}")
        for i, row in enumerate(cm):
            print(f"{labels_short[i]:3s} {' '.join(f'{val:6d}' for val in row)}")
        
        # Check if confusion matrix has values
        if np.sum(cm) == 0:
            print("\n❌ ERROR: Confusion matrix is empty (no predictions made)")
            return False
        
        # Per-class metrics
        print(f"\n📊 Per-Class Metrics:")
        for i in range(4):
            tp = cm[i, i]
            fp = np.sum(cm[:, i]) - tp
            fn = np.sum(cm[i, :]) - tp
            tn = np.sum(cm) - tp - fp - fn
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            print(f"   Class {i} ({labels_short[i]:6s}): Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}, Support={np.sum(y_test == i)}")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_evaluation()
    exit(0 if success else 1)
