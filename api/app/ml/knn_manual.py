"""
Manual K-Nearest Neighbors (KNN) Implementation
WITHOUT scikit-learn or any ML libraries

Implements:
1. Manual feature scaling (Z-score normalization)
2. Euclidean distance calculation
3. Finding K nearest neighbors
4. Majority voting for classification
5. Manual confusion matrix calculation

Features used for KNN classification:
- jenis_kelamin (0=Perempuan, 1=Laki-laki)
- usia_bulan
- tinggi_badan
- berat_badan
- lingkar_lengan
- lingkar_kepala
- zscore_bbu

Target label:
- status_stunting (0=Normal, 1=Stunting)
"""

import numpy as np
from typing import Tuple, List, Dict, Optional
import math


class ManualStandardScaler:
    """
    Manual implementation of feature scaling (Z-score normalization)
    WITHOUT sklearn.preprocessing.StandardScaler
    
    Formula: z = (x - mean) / std
    """
    
    def __init__(self):
        """Initialize the scaler"""
        self.mean = None
        self.std = None
        self.is_fitted = False
    
    def fit(self, X: np.ndarray) -> None:
        """
        Calculate mean and standard deviation for each feature
        
        Args:
            X: Training data (n_samples, n_features)
        """
        # Calculate mean for each feature (column)
        self.mean = np.mean(X, axis=0)
        
        # Calculate standard deviation for each feature
        # Using sample std (N-1) for better estimation
        self.std = np.std(X, axis=0, ddof=0)
        
        # Avoid division by zero
        self.std[self.std == 0] = 1.0
        
        self.is_fitted = True
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """
        Fit the scaler and transform data in one step
        
        Args:
            X: Training data (n_samples, n_features)
            
        Returns:
            Scaled data (n_samples, n_features)
        """
        self.fit(X)
        return self.transform(X)
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Scale data using fitted mean and std
        
        Args:
            X: Data to scale (n_samples, n_features)
            
        Returns:
            Scaled data (n_samples, n_features)
        """
        if not self.is_fitted:
            raise ValueError("Scaler must be fitted first. Call fit() or fit_transform().")
        
        # Apply z-score normalization: (x - mean) / std
        X_scaled = (X - self.mean) / self.std
        return X_scaled


class ManualKNNClassifier:
    """
    Manual K-Nearest Neighbors classifier WITHOUT sklearn
    
    Algorithm:
    1. Store all training data (lazy learning)
    2. For prediction:
       a. Calculate Euclidean distance from query to all training samples
       b. Sort distances and get k smallest
       c. Perform majority voting on k neighbors' labels
    
    Supports:
    - Euclidean distance metric only
    - Uniform weights (all neighbors have equal weight)
    - Multi-class classification
    """
    
    def __init__(self, n_neighbors: int = 5, weights: str = 'uniform'):
        """
        Initialize KNN classifier
        
        Args:
            n_neighbors: Number of neighbors to consider (default: 5)
            weights: 'uniform' (all equal) or 'distance' (weighted by inverse distance)
        """
        self.n_neighbors = n_neighbors
        self.weights = weights
        
        # Training data storage (lazy learning)
        self.X_train = None
        self.y_train = None
        self.classes_ = None
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Fit the KNN model by storing training data
        (KNN is a lazy learning algorithm - no actual training)
        
        Args:
            X: Training features (n_samples, n_features)
            y: Training labels (n_samples,)
        """
        # Store training data
        self.X_train = np.array(X)
        self.y_train = np.array(y)
        
        # Store unique classes
        self.classes_ = np.unique(y)
    
    @staticmethod
    def _euclidean_distance(point1: np.ndarray, point2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two points
        
        Formula: sqrt(sum((x1 - x2)^2))
        
        Args:
            point1: First point (1D array)
            point2: Second point (1D array)
            
        Returns:
            Distance as float
        """
        # Calculate squared differences
        squared_diff = np.power(point1 - point2, 2)
        
        # Sum and take square root
        distance = math.sqrt(np.sum(squared_diff))
        
        return distance
    
    def _calculate_distances(self, query: np.ndarray) -> np.ndarray:
        """
        Calculate distances from query point to all training samples
        
        Args:
            query: Query point (1D array, n_features,)
            
        Returns:
            Array of distances (n_samples,)
        """
        distances = []
        
        for i in range(len(self.X_train)):
            distance = self._euclidean_distance(query, self.X_train[i])
            distances.append(distance)
        
        return np.array(distances)
    
    def _find_nearest_neighbors(
        self, 
        distances: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find indices and distances of k nearest neighbors
        
        Args:
            distances: Array of distances (n_samples,)
            
        Returns:
            Tuple of (distances_sorted, indices_sorted) for k nearest
        """
        # Get k smallest distances
        k = min(self.n_neighbors, len(distances))
        
        # Get indices that would sort the array (ascending)
        sorted_indices = np.argsort(distances)
        
        # Take k smallest
        k_indices = sorted_indices[:k]
        k_distances = distances[k_indices]
        
        return k_distances, k_indices
    
    def _majority_vote(self, neighbor_labels: np.ndarray) -> int:
        """
        Determine class using majority voting
        
        Args:
            neighbor_labels: Labels of k nearest neighbors
            
        Returns:
            Predicted class (most frequent label)
        """
        # Count occurrences of each label
        unique_labels, counts = np.unique(neighbor_labels, return_counts=True)
        
        # Find label with highest count
        max_count_idx = np.argmax(counts)
        predicted_class = unique_labels[max_count_idx]
        
        return int(predicted_class)
    
    def _majority_vote_with_weights(
        self,
        neighbor_labels: np.ndarray,
        neighbor_distances: np.ndarray
    ) -> int:
        """
        Determine class using weighted majority voting
        Weight = 1 / (distance + epsilon) to avoid division by zero
        
        Args:
            neighbor_labels: Labels of k nearest neighbors
            neighbor_distances: Distances of k nearest neighbors
            
        Returns:
            Predicted class
        """
        # Weights inversely proportional to distance
        # Add small epsilon to avoid division by zero
        epsilon = 1e-10
        weights = 1.0 / (neighbor_distances + epsilon)
        
        # Normalize weights
        weights = weights / np.sum(weights)
        
        # Calculate weighted vote for each class
        class_weights = {}
        for label, weight in zip(neighbor_labels, weights):
            label_int = int(label)
            if label_int not in class_weights:
                class_weights[label_int] = 0
            class_weights[label_int] += weight
        
        # Return class with highest weighted vote
        predicted_class = max(class_weights, key=class_weights.get)
        
        return int(predicted_class)
    
    def predict(self, X: np.ndarray, exclude_indices: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Predict class for X
        
        Args:
            X: Query data (n_samples, n_features)
            exclude_indices: Array of training indices to exclude per query (for Leave-One-Out)
                            Shape (n_samples,) with index to exclude for each query
            
        Returns:
            Predicted labels (n_samples,)
        """
        predictions = []
        
        for i in range(len(X)):
            query = X[i]
            
            # Calculate distances from query to all training samples
            distances = self._calculate_distances(query)
            
            # If exclude_indices provided, set that distance to infinity
            if exclude_indices is not None and i < len(exclude_indices):
                exclude_idx = exclude_indices[i]
                if exclude_idx >= 0:  # -1 means no exclusion
                    distances[exclude_idx] = np.inf
            
            # Find k nearest neighbors
            k_distances, k_indices = self._find_nearest_neighbors(distances)
            
            # Validate neighbors found
            if len(k_indices) == 0:
                # No neighbors found (all excluded), return most common class
                predictions.append(int(np.bincount(self.y_train.astype(int)).argmax()))
                continue
            
            # Get labels of k neighbors
            neighbor_labels = self.y_train[k_indices]
            
            # Perform voting
            if self.weights == 'distance':
                prediction = self._majority_vote_with_weights(neighbor_labels, k_distances)
            else:  # uniform
                prediction = self._majority_vote(neighbor_labels)
            
            predictions.append(prediction)
        
        return np.array(predictions)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities for X
        
        Returns probability distribution over classes
        
        Args:
            X: Query data (n_samples, n_features)
            
        Returns:
            Probabilities (n_samples, n_classes)
        """
        probabilities = []
        
        for i in range(len(X)):
            query = X[i]
            
            # Calculate distances
            distances = self._calculate_distances(query)
            
            # Find k nearest neighbors
            k_distances, k_indices = self._find_nearest_neighbors(distances)
            
            # Get labels of k neighbors
            neighbor_labels = self.y_train[k_indices]
            
            # Calculate probability for each class
            class_probs = {}
            for cls in self.classes_:
                if self.weights == 'distance':
                    # Weighted voting: count weighted votes per class
                    epsilon = 1e-10
                    weights = 1.0 / (k_distances + epsilon)
                    weights_normalized = weights / np.sum(weights)
                    weighted_count = np.sum(weights_normalized[neighbor_labels == cls])
                    class_probs[int(cls)] = weighted_count
                else:  # uniform
                    # Uniform voting: count occurrences
                    count = np.sum(neighbor_labels == cls)
                    class_probs[int(cls)] = count / len(neighbor_labels)
            
            # Normalize if needed (for weighted voting, already normalized)
            if self.weights == 'uniform':
                total = sum(class_probs.values())
                class_probs = {k: v / total for k, v in class_probs.items()}
            
            # Create probability array
            probs = [class_probs.get(int(cls), 0.0) for cls in self.classes_]
            probabilities.append(probs)
        
        return np.array(probabilities)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Calculate accuracy score for X and y
        
        Args:
            X: Test features (n_samples, n_features)
            y: Test labels (n_samples,)
            
        Returns:
            Accuracy (0-1)
        """
        predictions = self.predict(X)
        accuracy = np.mean(predictions == y)
        return accuracy
    
    def kneighbors(
        self,
        X: np.ndarray,
        n_neighbors: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Find the K neighbors of query points X
        
        Returns: (distances, indices)
        
        Args:
            X: Query data (n_samples, n_features)
            n_neighbors: Number of neighbors. If None, use self.n_neighbors
            
        Returns:
            Tuple of:
            - distances: Array of shape (n_samples, n_neighbors)
            - indices: Array of shape (n_samples, n_neighbors)
        """
        if n_neighbors is None:
            n_neighbors = self.n_neighbors
        
        all_distances = []
        all_indices = []
        
        for i in range(len(X)):
            query = X[i]
            
            # Calculate all distances
            distances = self._calculate_distances(query)
            
            # Find k nearest
            k = min(n_neighbors, len(distances))
            sorted_indices = np.argsort(distances)
            k_indices = sorted_indices[:k]
            k_distances = distances[k_indices]
            
            all_distances.append(k_distances)
            all_indices.append(k_indices)
        
        # Pad with -1 if n_queries > 1
        max_n = max(len(d) for d in all_distances)
        padded_distances = np.full((len(X), max_n), np.inf)
        padded_indices = np.full((len(X), max_n), -1)
        
        for i in range(len(X)):
            n = len(all_distances[i])
            padded_distances[i, :n] = all_distances[i]
            padded_indices[i, :n] = all_indices[i]
        
        return padded_distances, padded_indices.astype(int)


def calculate_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[int]] = None
) -> np.ndarray:
    """
    Calculate confusion matrix MANUALLY without sklearn.metrics.confusion_matrix
    
    Confusion Matrix structure (for binary classification):
    
           Predicted
          Neg    Pos
       Neg [TN    FP]
    A  Pos [FN    TP]
    c
    t
    u
    a
    l
    
    Args:
        y_true: Ground truth labels (n_samples,)
        y_pred: Predicted labels (n_samples,)
        labels: List of label classes. If None, use unique from y_true and y_pred
        
    Returns:
        Confusion matrix (n_classes, n_classes)
    """
    if labels is None:
        labels = sorted(list(set(np.unique(y_true)) | set(np.unique(y_pred))))
    
    n_classes = len(labels)
    cm = np.zeros((n_classes, n_classes), dtype=int)
    
    # For each sample, increment the appropriate cell
    for true_label, pred_label in zip(y_true, y_pred):
        true_idx = labels.index(true_label) if isinstance(labels, list) else np.where(labels == true_label)[0][0]
        pred_idx = labels.index(pred_label) if isinstance(labels, list) else np.where(labels == pred_label)[0][0]
        cm[true_idx, pred_idx] += 1
    
    return cm


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Calculate classification metrics manually WITHOUT sklearn
    
    Metrics calculated:
    - Accuracy: (TP + TN) / Total
    - Precision (class 1): TP / (TP + FP)
    - Recall/Sensitivity (class 1): TP / (TP + FN)
    - Specificity (class 0): TN / (TN + FP)
    - F1-Score (class 1): 2 * (Precision * Recall) / (Precision + Recall)
    
    Args:
        y_true: Ground truth labels
        y_pred: Predicted labels
        
    Returns:
        Dictionary of metrics
    """
    # Calculate confusion matrix
    cm = calculate_confusion_matrix(y_true, y_pred, labels=[0, 1])
    
    # Extract TP, TN, FP, FN for binary classification
    TN = cm[0, 0]  # True Negative
    FP = cm[0, 1]  # False Positive
    FN = cm[1, 0]  # False Negative
    TP = cm[1, 1]  # True Positive
    
    # Calculate metrics
    total = TP + TN + FP + FN
    
    # Accuracy
    accuracy = (TP + TN) / total if total > 0 else 0
    
    # Precision
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    
    # Recall (Sensitivity)
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    
    # Specificity
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
    
    # F1-Score
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "f1_score": f1,
        "tp": int(TP),
        "tn": int(TN),
        "fp": int(FP),
        "fn": int(FN),
        "confusion_matrix": cm
    }


def format_confusion_matrix_table(
    cm: np.ndarray,
    labels: List[str] = None
) -> str:
    """
    Format confusion matrix as a readable table
    
    Args:
        cm: Confusion matrix (n_classes, n_classes)
        labels: Class labels. Default: ['Normal', 'Stunting']
        
    Returns:
        Formatted string representation
    """
    if labels is None:
        labels = ['Normal', 'Stunting']
    
    # Build table
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append("CONFUSION MATRIX (Manual Calculation)")
    lines.append("=" * 60)
    lines.append(f"{'':20} {'Predicted Normal':>15} {'Predicted Stunting':>15}")
    lines.append("-" * 60)
    
    for i, true_label in enumerate(labels):
        lines.append(f"Actual {true_label:12} {cm[i, 0]:>15} {cm[i, 1]:>15}")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
