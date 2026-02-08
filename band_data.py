# %% [markdown]
# ## 2. 📊 创建数据模块 (band_data.py)

# %%
#%%writefile band_data.py
"""
数据管理模块
"""

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
import time

class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.data = None
        self.labels = None
        self.feature_names = None
        self.class_names = None
        
    def generate_sample_data(self, n_samples=1000, n_features=30, n_classes=5):
        """生成模拟光谱数据"""
        print(f"🎲 生成模拟数据: {n_samples}样本 × {n_features}波段 × {n_classes}类别")
        
        # 生成更真实的模拟光谱数据
        X, y = make_classification(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=int(n_features * 0.7),  # 70%的波段包含信息
            n_redundant=int(n_features * 0.2),    # 20%的波段冗余
            n_classes=n_classes,
            n_clusters_per_class=2,
            random_state=42
        )
        
        # 添加光谱特性
        X = self.add_spectral_characteristics(X)
        
        self.data = X
        self.labels = y
        self.feature_names = [f"波段_{i+1:02d}" for i in range(n_features)]
        self.class_names = [f"类别_{i+1}" for i in range(n_classes)]
        
        return self.get_stats()
    
    def add_spectral_characteristics(self, X):
        """添加光谱特征"""
        n_samples, n_features = X.shape
        
        # 添加连续性和平滑性（光谱特征）
        for i in range(n_samples):
            # 添加高斯平滑
            from scipy.ndimage import gaussian_filter1d
            X[i] = gaussian_filter1d(X[i], sigma=1.5)
            
        # 确保所有值为正（反射率特征）
        X = X - X.min() + 0.1
        
        return X
    
    def get_stats(self):
        """获取数据统计信息"""
        if self.data is None:
            return None
            
        stats = {
            'shape': self.data.shape,
            'n_samples': self.data.shape[0],
            'n_features': self.data.shape[1],
            'n_classes': len(np.unique(self.labels)) if self.labels is not None else 0,
            'data_range': (float(self.data.min()), float(self.data.max())),
            'data_mean': float(self.data.mean()),
            'data_std': float(self.data.std()),
            'class_distribution': dict(zip(*np.unique(self.labels, return_counts=True))) 
                                if self.labels is not None else {}
        }
        
        return stats
    
    def get_subset(self, band_indices):
        """获取指定波段的子集"""
        if self.data is None:
            return None
            
        if not band_indices:
            return self.data
            
        # 确保索引在有效范围内
        valid_indices = [idx for idx in band_indices if 0 <= idx < self.data.shape[1]]
        return self.data[:, valid_indices]
    
    def save_data(self, filepath):
        """保存数据到文件"""
        if self.data is not None and self.labels is not None:
            df = pd.DataFrame(self.data, columns=self.feature_names)
            df['label'] = self.labels
            df.to_csv(filepath, index=False)
            return True
        return False
    
    def load_data(self, filepath):
        """从文件加载数据"""
        try:
            df = pd.read_csv(filepath)
            self.labels = df['label'].values
            self.data = df.drop('label', axis=1).values
            self.feature_names = df.drop('label', axis=1).columns.tolist()
            self.class_names = [f"类别_{i+1}" for i in np.unique(self.labels)]
            return True
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            return False

# %% [markdown]
# ## 3. 🤖 创建算法模块 (band_algorithms.py)