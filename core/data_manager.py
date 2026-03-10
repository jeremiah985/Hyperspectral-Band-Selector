"""
Data Manager - 数据管理模块
===========================

负责高光谱数据的加载、存储和处理
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import numpy as np


class HyperspectralData:
    """高光谱数据管理类"""
    
    def __init__(self):
        self.data: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.n_rows: int = 0
        self.n_cols: int = 0
        self.n_bands: int = 0
        self.n_classes: int = 0
        self.class_names: List[str] = []
        self.data_file: str = ""
        self.label_file: str = ""
        
    def load_data(self, filepath: str) -> Dict[str, Any]:
        import scipy.io as sio
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        mat = sio.loadmat(str(filepath))
        
        data_keys = [k for k in mat.keys() if not k.startswith('__')]
        if not data_keys:
            raise ValueError("MAT文件中没有有效数据")
        
        data_key = data_keys[0]
        data = mat[data_key].astype(np.float64)
        
        if len(data.shape) != 3:
            raise ValueError(f"数据维度不正确: {data.shape}, 期望3维 (H, W, bands)")
        
        self.data = data
        self.n_rows, self.n_cols, self.n_bands = data.shape
        self.data_file = str(filepath)
        
        return self.get_stats()
    
    def load_labels(self, filepath: str) -> Dict[str, Any]:
        import scipy.io as sio
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        mat = sio.loadmat(str(filepath))
        
        label_keys = [k for k in mat.keys() if not k.startswith('__')]
        if not label_keys:
            raise ValueError("MAT文件中没有有效数据")
        
        label_key = label_keys[0]
        labels = mat[label_key]
        
        if labels.shape != (self.n_rows, self.n_cols):
            raise ValueError(f"标签尺寸 {labels.shape} 与数据尺寸 ({self.n_rows}, {self.n_cols}) 不匹配")
        
        self.labels = labels
        self.label_file = str(filepath)
        
        unique_labels = np.unique(labels)
        self.n_classes = len(unique_labels[unique_labels > 0])
        
        return self.get_stats()
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {
            'shape': (self.n_rows, self.n_cols, self.n_bands) if self.data is not None else None,
            'n_bands': self.n_bands,
            'n_rows': self.n_rows,
            'n_cols': self.n_cols,
            'n_classes': self.n_classes,
            'has_data': self.data is not None,
            'has_labels': self.labels is not None,
            'data_file': self.data_file,
            'label_file': self.label_file
        }
        
        if self.data is not None:
            stats['data_min'] = float(self.data.min())
            stats['data_max'] = float(self.data.max())
            stats['data_mean'] = float(self.data.mean())
        
        if self.labels is not None:
            unique, counts = np.unique(self.labels, return_counts=True)
            stats['class_distribution'] = dict(zip(unique.tolist(), counts.tolist()))
        
        return stats
    
    def get_rgb_image(self) -> Optional[np.ndarray]:
        if self.data is None:
            return None
        
        n_bands = self.n_bands
        r_idx = int(n_bands * 0.67)
        g_idx = int(n_bands * 0.5)
        b_idx = int(n_bands * 0.33)
        
        r_band = self.data[:, :, r_idx]
        g_band = self.data[:, :, g_idx]
        b_band = self.data[:, :, b_idx]
        
        def normalize(band):
            p2, p98 = np.percentile(band, (2, 98))
            band = np.clip(band, p2, p98)
            return (band - band.min()) / (band.max() - band.min() + 1e-10)
        
        rgb = np.stack([normalize(r_band), normalize(g_band), normalize(b_band)], axis=-1)
        return (rgb * 255).astype(np.uint8)
    
    def get_band_image(self, band_idx: int) -> Optional[np.ndarray]:
        if self.data is None or band_idx >= self.n_bands:
            return None
        
        band = self.data[:, :, band_idx]
        p2, p98 = np.percentile(band, (2, 98))
        band = np.clip(band, p2, p98)
        band = (band - band.min()) / (band.max() - band.min() + 1e-10)
        return (band * 255).astype(np.uint8)
    
    def get_selected_bands_data(self, band_indices: List[int]) -> Optional[np.ndarray]:
        if self.data is None or not band_indices:
            return None
        return self.data[:, :, band_indices]
    
    def get_spectrum(self, row: int, col: int) -> Optional[np.ndarray]:
        if self.data is None:
            return None
        if 0 <= row < self.n_rows and 0 <= col < self.n_cols:
            return self.data[row, col, :]
        return None
    
    def clear(self):
        self.data = None
        self.labels = None
        self.n_rows = 0
        self.n_cols = 0
        self.n_bands = 0
        self.n_classes = 0
        self.data_file = ""
        self.label_file = ""
