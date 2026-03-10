"""
Base Classifier - 分类器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class BaseClassifier(ABC):
    """分类器基类"""
    
    def __init__(self):
        self.name = "Base Classifier"
        self.model = None
        self.is_trained = False
    
    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray):
        """训练分类器"""
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        pass
    
    def predict_proba(self, X: np.ndarray) -> Optional[np.ndarray]:
        """预测概率（如果支持）"""
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        return None
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """计算准确率"""
        y_pred = self.predict(X)
        return np.mean(y_pred == y)
    
    def get_model(self):
        """获取底层模型"""
        return self.model
