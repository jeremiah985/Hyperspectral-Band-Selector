"""
SVM Classifier - 支持向量机分类器
"""

import numpy as np
from .base import BaseClassifier


class SVMClassifier(BaseClassifier):
    """支持向量机分类器"""
    
    def __init__(self, kernel='rbf', C=1.0, random_state=42):
        super().__init__()
        self.name = "SVM"
        self.kernel = kernel
        self.C = C
        self.random_state = random_state
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        from sklearn.svm import SVC
        self.model = SVC(kernel=self.kernel, C=self.C, random_state=self.random_state)
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained:
            raise RuntimeError("分类器尚未训练")
        return self.model.predict(X)
