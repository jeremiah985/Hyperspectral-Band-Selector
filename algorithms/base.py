"""
Base Band Selector - 波段选择器基类
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np


class BaseBandSelector(ABC):
    """波段选择器基类"""
    
    def __init__(self):
        self.name = "Base Selector"
        self.selected_bands: List[int] = []
        self.scores: List[float] = []
    
    @abstractmethod
    def select(self, data: np.ndarray, n_bands: int, labels: np.ndarray = None) -> Tuple[List[int], List[float]]:
        """
        执行波段选择
        
        Args:
            data: 高光谱数据 (H, W, bands)
            n_bands: 选择波段数
            labels: 标签数据 (用于监督方法)
            
        Returns:
            selected_indices: 选中的波段索引
            scores: 各波段得分
        """
        pass
    
    def get_selected_bands(self) -> List[int]:
        return self.selected_bands
    
    def get_scores(self) -> List[float]:
        return self.scores
