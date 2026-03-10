"""
Variance Band Selector - 方差波段选择器
"""

from typing import List, Tuple
import numpy as np
from .base import BaseBandSelector


class VarianceSelector(BaseBandSelector):
    """基于方差的波段选择器"""
    
    def __init__(self):
        super().__init__()
        self.name = "方差"
    
    def select(self, data: np.ndarray, n_bands: int, labels: np.ndarray = None) -> Tuple[List[int], List[float]]:
        h, w, total_bands = data.shape
        X = data.reshape(-1, total_bands)
        
        scores = np.var(X, axis=0)
        
        selected_indices = np.argsort(scores)[-n_bands:].tolist()
        selected_indices = sorted(selected_indices)
        
        self.selected_bands = selected_indices
        self.scores = scores.tolist()
        
        return selected_indices, self.scores
