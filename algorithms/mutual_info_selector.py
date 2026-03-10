"""
Mutual Information Band Selector - 互信息波段选择器
"""

from typing import List, Tuple
import numpy as np
from .base import BaseBandSelector


class MutualInfoSelector(BaseBandSelector):
    """基于互信息的波段选择器"""
    
    def __init__(self):
        super().__init__()
        self.name = "互信息"
    
    def select(self, data: np.ndarray, n_bands: int, labels: np.ndarray = None) -> Tuple[List[int], List[float]]:
        h, w, total_bands = data.shape
        X = data.reshape(-1, total_bands)
        
        if labels is None:
            scores = np.var(X, axis=0)
        else:
            from sklearn.feature_selection import mutual_info_classif
            y = labels.flatten()
            valid_mask = y > 0
            X_valid = X[valid_mask]
            y_valid = y[valid_mask]
            scores = mutual_info_classif(X_valid, y_valid, random_state=42)
        
        selected_indices = np.argsort(scores)[-n_bands:].tolist()
        selected_indices = sorted(selected_indices)
        
        self.selected_bands = selected_indices
        self.scores = scores.tolist()
        
        return selected_indices, self.scores
