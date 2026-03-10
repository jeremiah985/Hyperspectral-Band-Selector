"""
PCA Band Selector - PCA波段选择器
"""

from typing import List, Tuple
import numpy as np
from .base import BaseBandSelector


class PCASelector(BaseBandSelector):
    """基于主成分分析的波段选择器"""
    
    def __init__(self):
        super().__init__()
        self.name = "PCA"
    
    def select(self, data: np.ndarray, n_bands: int, labels: np.ndarray = None) -> Tuple[List[int], List[float]]:
        from sklearn.decomposition import PCA
        
        h, w, total_bands = data.shape
        X = data.reshape(-1, total_bands)
        
        pca = PCA(n_components=min(n_bands, total_bands))
        pca.fit(X)
        
        components = np.abs(pca.components_)
        scores = components.sum(axis=0)
        
        selected_indices = np.argsort(scores)[-n_bands:].tolist()
        selected_indices = sorted(selected_indices)
        
        self.selected_bands = selected_indices
        self.scores = scores.tolist()
        
        return selected_indices, self.scores
