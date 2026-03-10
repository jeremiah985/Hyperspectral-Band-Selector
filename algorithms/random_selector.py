"""
Random Band Selector - 随机波段选择器
"""

from typing import List, Tuple
import numpy as np
from .base import BaseBandSelector


class RandomSelector(BaseBandSelector):
    """随机波段选择器（基线方法）"""
    
    def __init__(self):
        super().__init__()
        self.name = "随机"
    
    def select(self, data: np.ndarray, n_bands: int, labels: np.ndarray = None) -> Tuple[List[int], List[float]]:
        h, w, total_bands = data.shape
        
        np.random.seed(42)
        selected_indices = np.random.choice(total_bands, n_bands, replace=False).tolist()
        selected_indices = sorted(selected_indices)
        
        scores = [1.0] * total_bands
        
        self.selected_bands = selected_indices
        self.scores = scores
        
        return selected_indices, scores
