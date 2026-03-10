"""
JM Distance Band Selector - JM距离波段选择器
"""

from typing import List, Tuple
import numpy as np
from .base import BaseBandSelector


class JMSelector(BaseBandSelector):
    """基于Jeffries-Matusita距离的波段选择器"""
    
    def __init__(self):
        super().__init__()
        self.name = "JM距离"
    
    def select(self, data: np.ndarray, n_bands: int, labels: np.ndarray = None) -> Tuple[List[int], List[float]]:
        h, w, total_bands = data.shape
        X = data.reshape(-1, total_bands)
        
        if labels is None:
            scores = np.var(X, axis=0)
        else:
            y = labels.flatten()
            valid_mask = y > 0
            X_valid = X[valid_mask]
            y_valid = y[valid_mask]
            
            classes = np.unique(y_valid)
            n_classes = len(classes)
            
            scores = np.zeros(total_bands)
            for b in range(total_bands):
                band_data = X_valid[:, b]
                class_means = []
                class_stds = []
                for c in classes:
                    c_data = band_data[y_valid == c]
                    class_means.append(c_data.mean())
                    class_stds.append(c_data.std() + 1e-10)
                
                jm_sum = 0
                for i in range(n_classes):
                    for j in range(i+1, n_classes):
                        m1, m2 = class_means[i], class_means[j]
                        s1, s2 = class_stds[i], class_stds[j]
                        jm = 2 * (1 - np.exp(-((m1-m2)**2) / (8 * (s1**2 + s2**2))))
                        jm_sum += jm
                scores[b] = jm_sum
        
        selected_indices = np.argsort(scores)[-n_bands:].tolist()
        selected_indices = sorted(selected_indices)
        
        self.selected_bands = selected_indices
        self.scores = scores.tolist()
        
        return selected_indices, self.scores
