"""
Random Forest Classifier - 随机森林分类器
"""

import numpy as np
from .base import BaseClassifier


class RFClassifier(BaseClassifier):
    """随机森林分类器"""
    
    def __init__(self, n_estimators=100, random_state=42):
        super().__init__()
        self.name = "RandomForest"
        self.n_estimators = n_estimators
        self.random_state = random_state
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        from sklearn.ensemble import RandomForestClassifier
        self.model = RandomForestClassifier(n_estimators=self.n_estimators, random_state=self.random_state)
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("分类器尚未训练")
        return self.model.predict(X)
