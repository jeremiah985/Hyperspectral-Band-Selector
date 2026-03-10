"""
Algorithms Module - 波段选择算法模块
====================================

包含各种波段选择（降维）算法
"""

from .base import BaseBandSelector
from .pca_selector import PCASelector
from .ica_selector import ICASelector
from .jm_selector import JMSelector
from .mutual_info_selector import MutualInfoSelector
from .variance_selector import VarianceSelector
from .random_selector import RandomSelector

ALGORITHM_REGISTRY = {
    'PCA': PCASelector,
    'ICA': ICASelector,
    'JM距离': JMSelector,
    '互信息': MutualInfoSelector,
    '方差': VarianceSelector,
    '随机': RandomSelector
}

def get_available_methods():
    return list(ALGORITHM_REGISTRY.keys())

def get_selector(method_name: str):
    if method_name not in ALGORITHM_REGISTRY:
        raise ValueError(f"未知的波段选择方法: {method_name}")
    return ALGORITHM_REGISTRY[method_name]()

__all__ = [
    'BaseBandSelector',
    'PCASelector',
    'ICASelector', 
    'JMSelector',
    'MutualInfoSelector',
    'VarianceSelector',
    'RandomSelector',
    'get_available_methods',
    'get_selector',
    'ALGORITHM_REGISTRY'
]
