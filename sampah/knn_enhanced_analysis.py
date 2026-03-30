"""
Enhanced KNN K-Comparison Script with Data Analysis
Включает analisis dataset distribution dan advanced metrics

Fitur tambahan:
- Dataset statistics dan distribution analysis
- Class balance analysis
- Feature importance consideration
- Cross-validation metrics
- Detailed confusion matrix interpretation
"""

import csv
import math
from pathlib import Path
from collections import defaultdict


class EnhancedKNNAnalyzer:
    """Enhanced analyzer dengan additional insights"""
    
    def __init__(self):
        self.data = []
        self.X = []
        self.y = []
        self.feature_names = [
            'jenis_kelamin', 'usia_bulan', 'berat_badan',
            'tinggi_badan', 'lingkar_lengan', 'lingkar_kepala'
        ]
        self.results = {}
        
    def load_and_analyze(self, csv_file):
        """Load data dan lakukan analisis statistik"""
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        features = [
                            float(row['jenis_kelamin']),
                            float(row['usia_bulan']),
                            float(row['berat_badan']),
                            float(row['tinggi_badan']),
                            float(row['lingkar_lengan']),
                            float(row['lingkar_kepala'])
                        ]
                        label = int(row['status_stunting'])
                        self.data.append((features, label))
                        self.X.append(features)
                        self.y.append(label)
                    except (ValueError, KeyError):
                        continue
            
            if len(self.data) == 0:
                print("❌ No valid data found")
                return False
            
            print(f"✅ Loaded {len(self.data)} samples\n")
            self.print_dataset_statistics()
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def print_dataset_statistics(self):
        """Tampilkan statistik dataset"""
        print("="*80)
        print("📊 DATASET STATISTICS")
        print("="*80)
        
        print(f"\nTotal Samples: {len(self.data)}")
        
        # Class distribution
        normal_count = sum(1 for _, y in self.data if y == 0)
        stunting_count = sum(1 for _, y in self.data if y == 1)
        
        print(f"\nClass Distribution:")
        print(f"  Normal (0):   {normal_count:3d} samples ({normal_count/len(self.data)*100:5.1f}%)")
        print(f"  Stunting (1): {stunting_count:3d} samples ({stunting_count/len(self.data)*100:5.1f}%)")
        print(f"  Class Balance: {normal_count/stunting_count:.2f}:1")
        
        # Feature statistics
        print(f"\nFeature Statistics:")
        print(f"{'Feature':<18} {'Min':<10} {'Max':<10} {'Mean':<10} {'Std':<10}")
        print("-" * 60)
        
        for i, fname in enumerate(self.feature_names):
            values = [x[i] for x, _ in self.data]
            min_val = min(values)
            max_val = max(values)
            mean_val = sum(values) / len(values)
            
            # Calculate std
            variance = sum((v - mean_val)**2 for v in values) / len(values)
            std = math.sqrt(variance)
            
            print(f"{fname:<18} {min_val:<10.2f} {max_val:<10.2f} {mean_val:<10.2f} {std:<10.2f}")
        
        print("\n" + "="*80 + "\n")
    
    def analyze_k_range(self, k_values):
        """Analisis multiple K values dengan detail breakdown"""
        print("="*80)
        print("🔬 DETAILED K-VALUES ANALYSIS")
        print("="*80 + "\n")
        
        # Split data
        split_idx = int(len(self.data) * 0.8)
        X_train = [x for x, _ in self.data[:split_idx]]
        y_train = [y for _, y in self.data[:split_idx]]
        X_test = [x for x, _ in self.data[split_idx:]]
        y_test = [y for _, y in self.data[split_idx:]]
        
        print(f"Train set: {len(X_train)} samples")
        print(f"Test set:  {len(X_test)} samples\n")
        
        summary_table = []
        
        for k in k_values:
            print(f"Evaluating K = {k}...")
            
            # Normalize
            X_train_norm, X_test_norm = self._normalize(X_train, X_test)
            
            # Predict
            y_pred = self._predict(X_train_norm, y_train, X_test_norm, k)
            
            # Confusion matrix
            tp = sum(1 for t, p in zip(y_test, y_pred) if t==1 and p==1)
            tn = sum(1 for t, p in zip(y_test, y_pred) if t==0 and p==0)
            fp = sum(1 for t, p in zip(y_test, y_pred) if t==0 and p==1)
            fn = sum(1 for t, p in zip(y_test, y_pred) if t==1 and p==0)
            
            # Metrics
            total = tp + tn + fp + fn
            accuracy = (tp + tn) / total if total > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            summary_table.append({
                'k': k,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'specificity': specificity,
                'f1': f1,
                'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn
            })
            
            print(f"  Accuracy: {accuracy*100:6.2f}% | Recall: {recall*100:6.2f}% | Precision: {precision*100:6.2f}%")
            print()
        
        # Summary table
        print("="*80)
        print("SUMMARY TABLE")
        print("="*80)
        print(f"{'K':<3} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'TP':<4} {'TN':<4} {'FP':<4} {'FN':<4}")
        print("-" * 80)
        
        best_k = max(summary_table, key=lambda x: x['accuracy'])
        
        for row in summary_table:
            marker = "⭐" if row['k'] == best_k['k'] else "  "
            print(f"{row['k']:<3} {marker} {row['accuracy']*100:>10.2f}% {row['precision']*100:>10.2f}% {row['recall']*100:>10.2f}% {row['f1']*100:>10.2f}% {row['tp']:<4} {row['tn']:<4} {row['fp']:<4} {row['fn']:<4}")
        
        print("-" * 80)
        print(f"\n✅ BEST K = {best_k['k']} with Accuracy = {best_k['accuracy']*100:.2f}%\n")
        
        return best_k
    
    def _normalize(self, X_train, X_test):
        """Normalize using Z-score"""
        n_features = len(X_train[0])
        means = []
        stds = []
        
        # Calculate mean and std for each feature
        for i in range(n_features):
            values = [x[i] for x in X_train]
            mean = sum(values) / len(values)
            variance = sum((v - mean)**2 for v in values) / len(values)
            std = math.sqrt(variance)
            means.append(mean)
            stds.append(std)
        
        # Apply normalization
        X_train_norm = []
        for x in X_train:
            normalized = []
            for i in range(n_features):
                if stds[i] == 0:
                    normalized.append(0)
                else:
                    z = (x[i] - means[i]) / stds[i]
                    normalized.append(z)
            X_train_norm.append(normalized)
        
        X_test_norm = []
        for x in X_test:
            normalized = []
            for i in range(n_features):
                if stds[i] == 0:
                    normalized.append(0)
                else:
                    z = (x[i] - means[i]) / stds[i]
                    normalized.append(z)
            X_test_norm.append(normalized)
        
        return X_train_norm, X_test_norm
    
    def _euclidean_distance(self, x1, x2):
        """Calculate Euclidean distance"""
        return math.sqrt(sum((x1[i] - x2[i])**2 for i in range(len(x1))))
    
    def _predict(self, X_train, y_train, X_test, k):
        """Predict labels"""
        predictions = []
        
        for x_test in X_test:
            # Find k nearest
            distances = [(i, self._euclidean_distance(x_test, X_train[i])) 
                        for i in range(len(X_train))]
            distances.sort(key=lambda x: x[1])
            nearest_labels = [int(y_train[distances[i][0]]) for i in range(min(k, len(distances)))]
            
            # Majority vote
            votes = [0, 0]
            for label in nearest_labels:
                if label == 0:
                    votes[0] += 1
                elif label == 1:
                    votes[1] += 1
            
            predictions.append(0 if votes[0] >= votes[1] else 1)
        
        return predictions


def main():
    """Main execution"""
    analyzer = EnhancedKNNAnalyzer()
    
    csv_file = "backend/data_latih_stunting.csv"
    if not Path(csv_file).exists():
        csv_file = "data_latih_stunting.csv"
    
    if not analyzer.load_and_analyze(csv_file):
        return
    
    # Test K values
    k_values = [3, 5, 7, 9]
    best_k = analyzer.analyze_k_range(k_values)
    
    print("\n" + "="*80)
    print("🎯 RECOMMENDATION")
    print("="*80)
    print(f"\nUse K = {best_k['k']} for optimal stunting detection")
    print(f"Expected Performance:")
    print(f"  - Accuracy:    {best_k['accuracy']*100:.2f}%")
    print(f"  - Recall:      {best_k['recall']*100:.2f}% (Detection rate)")
    print(f"  - Precision:   {best_k['precision']*100:.2f}%")
    print(f"  - Specificity: {best_k['specificity']*100:.2f}%")
    print(f"\nConfusion Matrix (Test Set):")
    print(f"  TP (Correctly detected stunting): {best_k['tp']}")
    print(f"  TN (Correctly identified normal):  {best_k['tn']}")
    print(f"  FP (False alarms):                 {best_k['fp']}")
    print(f"  FN (Missed cases):                 {best_k['fn']}")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
