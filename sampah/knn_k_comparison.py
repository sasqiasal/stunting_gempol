"""
Script untuk Perbandingan Nilai K pada Klasifikasi KNN Manual
Stunting Detection System - Research & Analysis

Fitur yang digunakan:
- jenis_kelamin
- usia_bulan
- berat_badan
- tinggi_badan
- lingkar_lengan
- lingkar_kepala

Target: status_stunting (0=Normal, 1=Stunting)

K Values yang diuji: 3, 5, 7, 9

Tanpa menggunakan sklearn atau library ML apapun
"""

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path


class ManualKNNComparator:
    """Class untuk membandingkan performa KNN dengan berbagai nilai K"""
    
    def __init__(self):
        """Inisialisasi komparator"""
        self.X_train = []
        self.y_train = []
        self.X_test = []
        self.y_test = []
        self.feature_names = [
            'jenis_kelamin', 'usia_bulan', 'berat_badan', 
            'tinggi_badan', 'lingkar_lengan', 'lingkar_kepala'
        ]
        self.results = {}
        
    def load_data(self, csv_file):
        """
        Load data dari CSV file
        
        Args:
            csv_file (str): Path ke file CSV
            
        Returns:
            bool: True jika berhasil load, False jika gagal
        """
        try:
            if not Path(csv_file).exists():
                print(f"❌ File tidak ditemukan: {csv_file}")
                return False
            
            data = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Extract features sesuai urutan
                        features = [
                            float(row['jenis_kelamin']),
                            float(row['usia_bulan']),
                            float(row['berat_badan']),
                            float(row['tinggi_badan']),
                            float(row['lingkar_lengan']),
                            float(row['lingkar_kepala'])
                        ]
                        label = int(row['status_stunting'])
                        data.append((features, label))
                    except (ValueError, KeyError) as e:
                        continue
            
            if len(data) == 0:
                print("❌ Tidak ada data yang valid di CSV")
                return False
            
            print(f"✅ Berhasil load {len(data)} sampel data")
            
            # Train-test split (80-20)
            split_idx = int(len(data) * 0.8)
            
            self.X_train = [d[0] for d in data[:split_idx]]
            self.y_train = [d[1] for d in data[:split_idx]]
            self.X_test = [d[0] for d in data[split_idx:]]
            self.y_test = [d[1] for d in data[split_idx:]]
            
            print(f"📊 Data split:")
            print(f"   - Training set: {len(self.X_train)} sampel")
            print(f"   - Testing set: {len(self.X_test)} sampel")
            print(f"   - Fitur: {', '.join(self.feature_names)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def normalize_data(self, X_train, X_test):
        """
        Normalisasi data menggunakan Z-score (manual, tanpa sklearn)
        
        Args:
            X_train (list): Training features
            X_test (list): Testing features
            
        Returns:
            tuple: (X_train_norm, X_test_norm, means, stds)
        """
        n_features = len(X_train[0])
        means = []
        stds = []
        
        # Hitung mean dan std untuk setiap fitur
        for i in range(n_features):
            feature_values = [x[i] for x in X_train]
            mean = sum(feature_values) / len(feature_values)
            
            # Hitung standard deviation
            variance = sum((x - mean) ** 2 for x in feature_values) / len(feature_values)
            std = math.sqrt(variance)
            
            means.append(mean)
            stds.append(std)
        
        # Normalisasi training data
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
        
        # Normalisasi test data
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
        
        return X_train_norm, X_test_norm, means, stds
    
    def euclidean_distance(self, x1, x2):
        """
        Hitung Euclidean Distance antara dua vektor
        Formula: √(Σ(x1[i] - x2[i])²)
        
        Args:
            x1 (list): Vektor pertama
            x2 (list): Vektor kedua
            
        Returns:
            float: Jarak Euclidean
        """
        sum_squared = sum((x1[i] - x2[i]) ** 2 for i in range(len(x1)))
        return math.sqrt(sum_squared)
    
    def find_nearest_neighbors(self, x_test, X_train_norm, k):
        """
        Cari k tetangga terdekat untuk satu sampel test
        
        Args:
            x_test (list): Sampel test yang dinormalisasi
            X_train_norm (list): Training data yang sudah dinormalisasi
            k (int): Jumlah tetangga
            
        Returns:
            list: Index dari k tetangga terdekat
        """
        distances = []
        
        # Hitung jarak ke semua training sampel
        for i, x_train in enumerate(X_train_norm):
            dist = self.euclidean_distance(x_test, x_train)
            distances.append((i, dist))
        
        # Sort berdasarkan jarak dan ambil k terkecil
        distances.sort(key=lambda x: x[1])
        nearest_indices = [idx for idx, _ in distances[:k]]
        
        return nearest_indices
    
    def majority_vote(self, nearest_indices, y_train, k):
        """
        Tentukan kelas berdasarkan majority voting
        
        Args:
            nearest_indices (list): Index dari k tetangga terdekat
            y_train (list): Labels dari training data
            k (int): Jumlah tetangga
            
        Returns:
            int: Kelas prediksi (0 atau 1)
        """
        votes = [0, 0]  # [count_class_0, count_class_1]
        
        for idx in nearest_indices:
            label = int(y_train[idx])
            if label == 0:
                votes[0] += 1
            elif label == 1:
                votes[1] += 1
        
        # Return kelas dengan votes terbanyak
        return 0 if votes[0] > votes[1] else 1
    
    def predict(self, X_train_norm, y_train, X_test_norm, k):
        """
        Prediksi label untuk semua test data
        
        Args:
            X_train_norm (list): Training features yang dinormalisasi
            y_train (list): Training labels
            X_test_norm (list): Test features yang dinormalisasi
            k (int): Jumlah tetangga
            
        Returns:
            list: Prediksi label untuk test data
        """
        predictions = []
        
        for x_test in X_test_norm:
            # Cari k tetangga terdekat
            nearest_indices = self.find_nearest_neighbors(x_test, X_train_norm, k)
            
            # Majority voting
            prediction = self.majority_vote(nearest_indices, y_train, k)
            predictions.append(prediction)
        
        return predictions
    
    def calculate_confusion_matrix(self, y_true, y_pred):
        """
        Hitung confusion matrix secara manual
        
        Categories:
        - TP (True Positive): Predicted 1, Actual 1
        - TN (True Negative): Predicted 0, Actual 0
        - FP (False Positive): Predicted 1, Actual 0
        - FN (False Negative): Predicted 0, Actual 1
        
        Args:
            y_true (list): Label sebenarnya
            y_pred (list): Label prediksi
            
        Returns:
            dict: Confusion matrix {TP, TN, FP, FN}
        """
        tp = tn = fp = fn = 0
        
        for true, pred in zip(y_true, y_pred):
            true = int(true)
            pred = int(pred)
            
            if pred == 1 and true == 1:
                tp += 1
            elif pred == 0 and true == 0:
                tn += 1
            elif pred == 1 and true == 0:
                fp += 1
            elif pred == 0 and true == 1:
                fn += 1
        
        return {'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn}
    
    def calculate_metrics(self, cm):
        """
        Hitung metrik performa dari confusion matrix
        
        Formula:
        - Accuracy = (TP + TN) / (TP + TN + FP + FN)
        - Precision = TP / (TP + FP)
        - Recall = TP / (TP + FN)
        - F1-Score = 2 * (Precision * Recall) / (Precision + Recall)
        
        Args:
            cm (dict): Confusion matrix
            
        Returns:
            dict: Metrics {accuracy, precision, recall, f1_score}
        """
        tp, tn, fp, fn = cm['TP'], cm['TN'], cm['FP'], cm['FN']
        total = tp + tn + fp + fn
        
        # Accuracy
        accuracy = (tp + tn) / total if total > 0 else 0
        
        # Precision
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        
        # Recall (Sensitivity)
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        # Specificity
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # F1-Score
        if (precision + recall) > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'specificity': specificity,
            'f1_score': f1_score
        }
    
    def evaluate_k_value(self, k):
        """
        Evaluasi performa KNN untuk nilai K tertentu
        
        Args:
            k (int): Jumlah tetangga
            
        Returns:
            dict: Hasil evaluasi {cm, metrics, y_pred}
        """
        # Normalisasi data
        X_train_norm, X_test_norm, _, _ = self.normalize_data(self.X_train, self.X_test)
        
        # Prediksi
        y_pred = self.predict(X_train_norm, self.y_train, X_test_norm, k)
        
        # Confusion matrix
        cm = self.calculate_confusion_matrix(self.y_test, y_pred)
        
        # Metrics
        metrics = self.calculate_metrics(cm)
        
        return {
            'cm': cm,
            'metrics': metrics,
            'y_pred': y_pred
        }
    
    def compare_k_values(self, k_values):
        """
        Bandingkan performa untuk berbagai nilai K
        
        Args:
            k_values (list): List nilai K yang akan diuji
        """
        print("\n" + "="*80)
        print("🔍 PERBANDINGAN NILAI K UNTUK KNN MANUAL STUNTING CLASSIFICATION")
        print("="*80 + "\n")
        
        self.results = {}
        
        for k in k_values:
            print(f"⏳ Evaluating K = {k}...", end=" ")
            result = self.evaluate_k_value(k)
            self.results[k] = result
            accuracy = result['metrics']['accuracy']
            print(f"✅ Akurasi: {accuracy*100:.2f}%")
        
        # Display comparison table
        self.display_comparison_table(k_values)
        
        # Determine best K
        best_k = self.determine_best_k(k_values)
        
        # Display detailed results
        self.display_detailed_results(best_k)
        
        # Display conclusion
        self.display_conclusion(best_k, k_values)
    
    def display_comparison_table(self, k_values):
        """Tampilkan tabel perbandingan performa untuk berbagai K"""
        print("\n" + "="*80)
        print("📊 TABEL PERBANDINGAN PERFORMA UNTUK BERBAGAI NILAI K")
        print("="*80 + "\n")
        
        # Header
        print(f"{'K':<5} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'TP':<6} {'TN':<6} {'FP':<6} {'FN':<6}")
        print("-" * 80)
        
        # Data
        for k in k_values:
            result = self.results[k]
            cm = result['cm']
            metrics = result['metrics']
            
            print(f"{k:<5} {metrics['accuracy']*100:>10.2f}% {metrics['precision']*100:>10.2f}% {metrics['recall']*100:>10.2f}% {metrics['f1_score']*100:>10.2f}% {cm['TP']:<6} {cm['TN']:<6} {cm['FP']:<6} {cm['FN']:<6}")
        
        print("-" * 80)
    
    def determine_best_k(self, k_values):
        """
        Tentukan nilai K terbaik berdasarkan accuracy tertinggi
        
        Args:
            k_values (list): List nilai K
            
        Returns:
            int: Nilai K terbaik
        """
        best_k = k_values[0]
        best_accuracy = self.results[best_k]['metrics']['accuracy']
        
        for k in k_values[1:]:
            accuracy = self.results[k]['metrics']['accuracy']
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_k = k
        
        return best_k
    
    def display_detailed_results(self, best_k):
        """Tampilkan hasil detail untuk K terbaik"""
        print("\n" + "="*80)
        print(f"🏆 HASIL DETAIL UNTUK K TERBAIK (K = {best_k})")
        print("="*80 + "\n")
        
        result = self.results[best_k]
        cm = result['cm']
        metrics = result['metrics']
        
        # Confusion Matrix
        print("📈 Confusion Matrix:")
        print(f"   ┌─────────────────┬─────────────────┐")
        print(f"   │   Predicted 0   │   Predicted 1   │")
        print(f"   ├─────────────────┼─────────────────┤")
        print(f"   │ Actual 0: {cm['TN']:<3} | {cm['FP']:<15} │")
        print(f"   │ Actual 1: {cm['FN']:<3} | {cm['TP']:<15} │")
        print(f"   └─────────────────┴─────────────────┘")
        
        # Metrics
        print("\n📊 Metrik Performa:")
        print(f"   • Akurasi:    {metrics['accuracy']*100:>7.2f}% ({cm['TP'] + cm['TN']}/{cm['TP'] + cm['TN'] + cm['FP'] + cm['FN']})")
        print(f"   • Presisi:    {metrics['precision']*100:>7.2f}% (TP/(TP+FP))")
        print(f"   • Recall:     {metrics['recall']*100:>7.2f}% (TP/(TP+FN))")
        print(f"   • Spesifisitas: {metrics['specificity']*100:>5.2f}% (TN/(TN+FP))")
        print(f"   • F1-Score:   {metrics['f1_score']*100:>7.2f}%")
        
        # Interpretasi
        print("\n💡 Interpretasi:")
        print(f"   • Total sampel test: {len(self.y_test)}")
        print(f"   • Prediksi benar (TP+TN): {cm['TP'] + cm['TN']}")
        print(f"   • Prediksi salah (FP+FN): {cm['FP'] + cm['FN']}")
        print(f"   • False Positive (False Alarm): {cm['FP']}")
        print(f"   • False Negative (Missed Cases): {cm['FN']}")
    
    def display_conclusion(self, best_k, k_values):
        """Tampilkan kesimpulan"""
        print("\n" + "="*80)
        print("📝 KESIMPULAN")
        print("="*80 + "\n")
        
        best_accuracy = self.results[best_k]['metrics']['accuracy']
        
        print(f"Berdasarkan hasil perbandingan performa KNN manual dengan berbagai nilai K:")
        print(f"\n✅ K TERBAIK: K = {best_k} dengan Akurasi = {best_accuracy*100:.2f}%\n")
        
        # Analisis K values
        print("📊 Analisis Perbandingan K Values:")
        for i, k in enumerate(k_values, 1):
            accuracy = self.results[k]['metrics']['accuracy']
            marker = "🏆" if k == best_k else "  "
            print(f"   {marker} K = {k}: Akurasi = {accuracy*100:.2f}%")
        
        # Rekomendasi
        print(f"\n💡 Rekomendasi:")
        print(f"   • Gunakan K = {best_k} untuk klasifikasi status stunting pada dataset ini")
        print(f"   • Nilai K ini memberikan keseimbangan terbaik antara:")
        print(f"     - Generalisasi model")
        print(f"     - Sensitivitas deteksi stunting")
        print(f"     - Spesifisitas deteksi normal")
        
        # Catatan untuk penelitian
        print(f"\n📌 Catatan untuk Penelitian Skripsi:")
        print(f"   • Metode: K-Nearest Neighbors (KNN) Manual (tanpa sklearn)")
        print(f"   • Fitur: 6 anthropometric features (jenis_kelamin, usia_bulan, berat_badan,")
        print(f"            tinggi_badan, lingkar_lengan, lingkar_kepala)")
        print(f"   • Normalisasi: Z-score normalization (manual)")
        print(f"   • Distance: Euclidean Distance")
        print(f"   • Voting: Majority voting")
        print(f"   • Dataset: {len(self.X_train) + len(self.X_test)} sampel (80% train, 20% test)")
        print(f"   • K optimal: {best_k}")
        print(f"   • Akurasi optimal: {best_accuracy*100:.2f}%\n")
        
        print("="*80 + "\n")


def main():
    """Main function untuk menjalankan perbandingan K values"""
    
    # Initialize comparator
    comparator = ManualKNNComparator()
    
    # Load data
    csv_file = "backend/data_latih_stunting.csv"
    print(f"📁 Loading data dari: {csv_file}")
    
    if not comparator.load_data(csv_file):
        # Try alternative path
        csv_file = "data_latih_stunting.csv"
        print(f"\n📁 Trying alternative path: {csv_file}")
        if not comparator.load_data(csv_file):
            print("\n❌ Tidak bisa load data. Silakan pastikan file berada di:")
            print("   1. backend/data_latih_stunting.csv")
            print("   2. data_latih_stunting.csv (root directory)")
            sys.exit(1)
    
    # Define K values to test
    k_values = [3, 5, 7, 9]
    
    # Compare K values
    comparator.compare_k_values(k_values)


if __name__ == "__main__":
    main()
