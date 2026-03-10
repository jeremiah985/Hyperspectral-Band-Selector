"""
Logistic Regression Classifier - 逻辑回归分类器
"""

import numpy as np
from .base import BaseClassifier


class LRClassifier(BaseClassifier):
    """逻辑回归分类器"""
    
    def __init__(self, max_iter=1000, random_state=42):
        super().__init__()
        self.name = "LogisticRegression"
        self.max_iter = max_iter
        self.random_state = random_state
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        from sklearn.linear_model import LogisticRegression
        self.model = LogisticRegression(max_iter=self.max_iter, random_state=self.random_state)
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("分类器尚未训练")
        return self.model.predict(X)
