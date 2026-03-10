"""
KNN Classifier - K近邻分类器
"""

import numpy as np
from .base import BaseClassifier


class KNNClassifier(BaseClassifier):
    """K近邻分类器"""
    
    def __init__(self, n_neighbors=5):
        super().__init__()
        self.name = "KNN"
        self.n_neighbors = n_neighbors
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        from sklearn.neighbors import KNeighborsClassifier
        self.model = KNeighborsClassifier(n_neighbors=self.n_neighbors)
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("分类器尚未训练")
        return self.model.predict(X)
