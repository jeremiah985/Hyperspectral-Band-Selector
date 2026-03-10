"""
Core Module - 核心模块
======================

包含数据管理、工具类和配置
"""

from .data_manager import HyperspectralData
from .utils import WorkerThread, LoadingWidget
from .config import COLORS, PROJECT_ROOT, setup_chinese

__all__ = [
    'HyperspectralData',
    'WorkerThread', 
    'LoadingWidget',
    'setup_chinese',
    'COLORS',
    'PROJECT_ROOT'
]
