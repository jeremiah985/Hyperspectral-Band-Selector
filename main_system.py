"""
高光谱图像波段选择与分类系统 v6.0
==================================

工作流程:
1. 加载数据文件 (.mat) 和标签文件 (*_gt.mat)
2. 可视化高光谱图像 (鼠标滚轮缩放)
3. 波段选择 (降维) - 选择重要波段
4. 基于选中波段进行分类
5. 结果对比与导出

运行方式: python main_system.py
"""

import sys
import os
from pathlib import Path
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QScrollArea, QGroupBox, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QFileDialog, QMessageBox, QProgressBar, QFrame, QSizePolicy,
    QStatusBar, QMenuBar, QMenu, QAction, QTabWidget, QFormLayout,
    QSlider, QGridLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPointF
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QImage, QWheelEvent

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap
import seaborn as sns

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))


def setup_chinese():
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

setup_chinese()


class ZoomableCanvas(FigureCanvas):
    """支持鼠标滚轮缩放的画布"""
    
    def __init__(self, figure, parent=None):
        super().__init__(figure)
        self.parent_widget = parent
        self.mpl_connect('scroll_event', self._on_scroll)
        
    def _on_scroll(self, event):
        if event.inaxes is None:
            return
        
        ax = event.inaxes
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        xdata = event.xdata
        ydata = event.ydata
        
        if event.button == 'up':
            scale_factor = 0.8
        elif event.button == 'down':
            scale_factor = 1.25
        else:
            return
        
        new_xlim = [xdata - (xdata - xlim[0]) * scale_factor,
                    xdata + (xlim[1] - xdata) * scale_factor]
        new_ylim = [ydata - (ydata - ylim[0]) * scale_factor,
                    ydata + (ylim[1] - ydata) * scale_factor]
        
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)
        self.draw_idle()


class WorkerThread(QThread):
    """异步工作线程"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            import traceback
            self.error.emit(f"{str(e)}\n{traceback.format_exc()}")


class LoadingWidget(QWidget):
    """加载动画"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setVisible(False)
        self._init_ui()
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._counter = 0

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(40, 44, 52, 240);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        container_layout = QVBoxLayout(container)
        
        self.spinner = QLabel("◐")
        self.spinner.setStyleSheet("color: #61afef; font-size: 42px; font-weight: bold;")
        self.spinner.setAlignment(Qt.AlignCenter)
        
        self.message = QLabel("处理中...")
        self.message.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.message.setAlignment(Qt.AlignCenter)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFixedWidth(220)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #3e4451;
                color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #61afef, stop:1 #98c379);
                border-radius: 6px;
            }
        """)
        
        container_layout.addWidget(self.spinner)
        container_layout.addWidget(self.message)
        container_layout.addWidget(self.progress)
        
        layout.addWidget(container)

    def _animate(self):
        chars = ["◐", "◓", "◑", "◒"]
        self.spinner.setText(chars[self._counter % 4])
        self._counter += 1

    def show_loading(self, msg="处理中..."):
        self.message.setText(msg)
        self.progress.setValue(0)
        self._timer.start(100)
        self.setVisible(True)
        self.raise_()

    def hide_loading(self):
        self._timer.stop()
        self.setVisible(False)

    def resizeEvent(self, event):
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())


class HyperspectralData:
    """高光谱数据管理"""
    
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
        """加载高光谱数据文件"""
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
        """加载标签文件"""
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
        """获取数据统计信息"""
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
        """生成RGB伪彩色图像"""
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
        """获取指定波段图像"""
        if self.data is None or band_idx >= self.n_bands:
            return None
        
        band = self.data[:, :, band_idx]
        p2, p98 = np.percentile(band, (2, 98))
        band = np.clip(band, p2, p98)
        band = (band - band.min()) / (band.max() - band.min() + 1e-10)
        return (band * 255).astype(np.uint8)
    
    def get_selected_bands_data(self, band_indices: List[int]) -> Optional[np.ndarray]:
        """获取选中波段的数据"""
        if self.data is None or not band_indices:
            return None
        return self.data[:, :, band_indices]
    
    def get_spectrum(self, row: int, col: int) -> Optional[np.ndarray]:
        """获取指定像素的光谱"""
        if self.data is None:
            return None
        if 0 <= row < self.n_rows and 0 <= col < self.n_cols:
            return self.data[row, col, :]
        return None


class BandSelector:
    """波段选择器"""
    
    @staticmethod
    def get_available_methods() -> List[str]:
        """获取可用的波段选择方法"""
        return ['PCA', 'ICA', 'JM距离', '互信息', '方差', '随机']
    
    @staticmethod
    def select_bands(data: np.ndarray, method: str, n_bands: int, labels: np.ndarray = None) -> Tuple[List[int], List[float]]:
        """
        波段选择
        
        Args:
            data: 高光谱数据 (H, W, bands)
            method: 选择方法
            n_bands: 选择波段数
            labels: 标签数据 (用于监督方法)
            
        Returns:
            selected_indices: 选中的波段索引
            scores: 各波段得分
        """
        h, w, total_bands = data.shape
        X = data.reshape(-1, total_bands)
        
        if method == 'PCA':
            from sklearn.decomposition import PCA
            pca = PCA(n_components=min(n_bands, total_bands))
            pca.fit(X)
            components = np.abs(pca.components_)
            scores = components.sum(axis=0)
            selected_indices = np.argsort(scores)[-n_bands:].tolist()
            scores = scores.tolist()
            
        elif method == 'ICA':
            from sklearn.decomposition import FastICA
            ica = FastICA(n_components=min(n_bands, total_bands), random_state=42, max_iter=500)
            ica.fit(X)
            components = np.abs(ica.components_)
            scores = components.sum(axis=0)
            selected_indices = np.argsort(scores)[-n_bands:].tolist()
            scores = scores.tolist()
            
        elif method == 'JM距离':
            if labels is None:
                scores = np.var(X, axis=0)
                selected_indices = np.argsort(scores)[-n_bands:].tolist()
                scores = scores.tolist()
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
                scores = scores.tolist()
                
        elif method == '互信息':
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
            scores = scores.tolist()
            
        elif method == '方差':
            scores = np.var(X, axis=0)
            selected_indices = np.argsort(scores)[-n_bands:].tolist()
            scores = scores.tolist()
            
        elif method == '随机':
            np.random.seed(42)
            selected_indices = np.random.choice(total_bands, n_bands, replace=False).tolist()
            scores = [1.0] * total_bands
            
        else:
            scores = np.var(X, axis=0)
            selected_indices = np.argsort(scores)[-n_bands:].tolist()
            scores = scores.tolist()
        
        selected_indices = sorted(selected_indices)
        return selected_indices, scores


class ControlPanel(QWidget):
    """左侧控制面板"""
    
    dataLoaded = pyqtSignal()
    bandsSelected = pyqtSignal()
    classificationDone = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.hs_data = main_window.hs_data
        self.worker = None
        self.selected_bands = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:#f8f9fa;}")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(6)
        
        container_layout.addWidget(self._create_data_section())
        container_layout.addWidget(self._create_band_section())
        container_layout.addWidget(self._create_classification_section())
        container_layout.addWidget(self._create_export_section())
        container_layout.addStretch()
        
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _section_header(self, title, icon, color):
        w = QWidget()
        w.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 {self._darken(color)});
                border-radius: 6px;
            }}
        """)
        h = QHBoxLayout(w)
        h.setContentsMargins(10, 6, 10, 6)
        h.addWidget(QLabel(f"<span style='font-size:14px'>{icon}</span>"))
        h.addWidget(QLabel(f"<b style='color:white;font-size:12px'>{title}</b>"))
        h.addStretch()
        return w

    def _darken(self, hex_color):
        c = hex_color.lstrip('#')
        rgb = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
        d = tuple(int(v * 0.75) for v in rgb)
        return f"#{d[0]:02x}{d[1]:02x}{d[2]:02x}"

    def _btn(self, text, color, h=32):
        btn = QPushButton(text)
        btn.setMinimumHeight(h)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{ background: {self._darken(color)}; }}
            QPushButton:pressed {{ background: {self._darken(self._darken(color))}; }}
            QPushButton:disabled {{ background: #95a5a6; }}
        """)
        return btn

    def _create_data_section(self):
        g = QGroupBox()
        g.setStyleSheet("QGroupBox{border:1px solid #ddd;border-radius:8px;margin-top:0;padding-top:8px;}")
        l = QVBoxLayout(g)
        l.setSpacing(6)
        
        l.addWidget(self._section_header("数据加载", "📁", "#3498db"))
        
        l.addWidget(QLabel("<b>数据文件:</b>"))
        data_h = QHBoxLayout()
        self.data_edit = QLineEdit()
        self.data_edit.setPlaceholderText("选择数据文件 (*.mat)")
        self.data_edit.setStyleSheet("padding:6px;border:1px solid #ccc;border-radius:4px;background:white;")
        data_btn = self._btn("浏览", "#3498db")
        data_btn.clicked.connect(self._browse_data)
        data_h.addWidget(self.data_edit, 1)
        data_h.addWidget(data_btn)
        l.addLayout(data_h)
        
        l.addWidget(QLabel("<b>标签文件:</b>"))
        label_h = QHBoxLayout()
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("选择标签文件 (*_gt.mat)")
        self.label_edit.setStyleSheet("padding:6px;border:1px solid #ccc;border-radius:4px;background:white;")
        label_btn = self._btn("浏览", "#3498db")
        label_btn.clicked.connect(self._browse_label)
        label_h.addWidget(self.label_edit, 1)
        label_h.addWidget(label_btn)
        l.addLayout(label_h)
        
        btn_h = QHBoxLayout()
        load_btn = self._btn("📥 加载数据", "#27ae60")
        load_btn.clicked.connect(self._load_data)
        auto_btn = self._btn("🔄 自动匹配", "#9b59b6")
        auto_btn.clicked.connect(self._auto_match)
        btn_h.addWidget(load_btn)
        btn_h.addWidget(auto_btn)
        l.addLayout(btn_h)
        
        self.data_info = QTextEdit()
        self.data_info.setMaximumHeight(100)
        self.data_info.setReadOnly(True)
        self.data_info.setStyleSheet("font-family:Consolas;font-size:10px;border:1px solid #eee;border-radius:4px;padding:4px;background:#fafafa;")
        l.addWidget(self.data_info)
        
        return g

    def _create_band_section(self):
        g = QGroupBox()
        g.setStyleSheet("QGroupBox{border:1px solid #ddd;border-radius:8px;margin-top:0;padding-top:8px;}")
        l = QVBoxLayout(g)
        l.setSpacing(6)
        
        l.addWidget(self._section_header("波段选择", "🎯", "#9b59b6"))
        
        form = QFormLayout()
        form.setSpacing(4)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(BandSelector.get_available_methods())
        form.addRow("方法:", self.method_combo)
        
        self.n_bands_spin = QSpinBox()
        self.n_bands_spin.setRange(1, 200)
        self.n_bands_spin.setValue(10)
        form.addRow("波段数:", self.n_bands_spin)
        
        l.addLayout(form)
        
        select_btn = self._btn("🔍 执行波段选择", "#9b59b6")
        select_btn.clicked.connect(self._run_band_selection)
        l.addWidget(select_btn)
        
        self.band_result = QTextEdit()
        self.band_result.setMaximumHeight(80)
        self.band_result.setReadOnly(True)
        self.band_result.setStyleSheet("font-family:Consolas;font-size:10px;border:1px solid #eee;border-radius:4px;padding:4px;background:#fafafa;")
        l.addWidget(self.band_result)
        
        l.addWidget(QLabel("<b>选中波段:</b>"))
        self.band_list = QListWidget()
        self.band_list.setMaximumHeight(100)
        self.band_list.setStyleSheet("font-size:10px;")
        l.addWidget(self.band_list)
        
        return g

    def _create_classification_section(self):
        g = QGroupBox()
        g.setStyleSheet("QGroupBox{border:1px solid #ddd;border-radius:8px;margin-top:0;padding-top:8px;}")
        l = QVBoxLayout(g)
        l.setSpacing(6)
        
        l.addWidget(self._section_header("图像分类", "📊", "#e67e22"))
        
        form = QFormLayout()
        form.setSpacing(4)
        
        self.clf_combo = QComboBox()
        self.clf_combo.addItems(['SVM', 'RandomForest', 'KNN', 'LogisticRegression'])
        form.addRow("分类器:", self.clf_combo)
        
        self.test_spin = QDoubleSpinBox()
        self.test_spin.setRange(0.1, 0.5)
        self.test_spin.setValue(0.3)
        self.test_spin.setSingleStep(0.05)
        form.addRow("测试比例:", self.test_spin)
        
        l.addLayout(form)
        
        classify_btn = self._btn("▶ 训练并分类", "#e67e22")
        classify_btn.clicked.connect(self._run_classification)
        l.addWidget(classify_btn)
        
        self.clf_result = QTextEdit()
        self.clf_result.setMaximumHeight(80)
        self.clf_result.setReadOnly(True)
        self.clf_result.setStyleSheet("font-family:Consolas;font-size:10px;border:1px solid #eee;border-radius:4px;padding:4px;background:#fafafa;")
        l.addWidget(self.clf_result)
        
        return g

    def _create_export_section(self):
        g = QGroupBox()
        g.setStyleSheet("QGroupBox{border:1px solid #ddd;border-radius:8px;margin-top:0;padding-top:8px;}")
        l = QVBoxLayout(g)
        l.setSpacing(6)
        
        l.addWidget(self._section_header("结果导出", "💾", "#27ae60"))
        
        btn_h = QHBoxLayout()
        mat_btn = self._btn("导出 .mat", "#27ae60")
        mat_btn.clicked.connect(self._export_mat)
        csv_btn = self._btn("导出 .csv", "#3498db")
        csv_btn.clicked.connect(self._export_csv)
        btn_h.addWidget(mat_btn)
        btn_h.addWidget(csv_btn)
        l.addLayout(btn_h)
        
        img_btn = self._btn("📷 导出图像", "#9b59b6")
        img_btn.clicked.connect(self._export_image)
        l.addWidget(img_btn)
        
        return g

    def _browse_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择数据文件", str(project_root / "dataset"),
            "MAT 文件 (*.mat);;所有文件 (*.*)"
        )
        if path:
            self.data_edit.setText(path)
            self.main_window.statusBar().showMessage(f"已选择数据: {Path(path).name}", 3000)

    def _browse_label(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择标签文件", str(project_root / "dataset"),
            "MAT 文件 (*.mat);;所有文件 (*.*)"
        )
        if path:
            self.label_edit.setText(path)
            self.main_window.statusBar().showMessage(f"已选择标签: {Path(path).name}", 3000)

    def _auto_match(self):
        data_path = self.data_edit.text().strip()
        if not data_path:
            QMessageBox.warning(self, "提示", "请先选择数据文件")
            return
        
        data_path = Path(data_path)
        label_path = data_path.parent / (data_path.stem + "_gt" + data_path.suffix)
        
        if label_path.exists():
            self.label_edit.setText(str(label_path))
            self.main_window.statusBar().showMessage(f"自动匹配标签: {label_path.name}", 3000)
        else:
            QMessageBox.warning(self, "提示", f"未找到匹配的标签文件:\n{label_path}")

    def _load_data(self):
        data_path = self.data_edit.text().strip()
        label_path = self.label_edit.text().strip()
        
        if not data_path:
            QMessageBox.warning(self, "提示", "请选择数据文件")
            return
        
        self.main_window.show_loading("加载数据中...")
        
        def load_task():
            stats = self.hs_data.load_data(data_path)
            if label_path:
                stats = self.hs_data.load_labels(label_path)
            return stats
        
        self.worker = WorkerThread(load_task)
        self.worker.finished.connect(self._on_data_loaded)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_data_loaded(self, stats):
        self.main_window.hide_loading()
        
        info = f"数据维度: {stats['shape']}\n"
        info += f"波段数: {stats['n_bands']}\n"
        info += f"图像尺寸: {stats['n_rows']} x {stats['n_cols']}\n"
        if stats['has_labels']:
            info += f"类别数: {stats['n_classes']}"
        else:
            info += "标签: 未加载"
        self.data_info.setText(info)
        
        self.n_bands_spin.setMaximum(stats['n_bands'])
        
        self.dataLoaded.emit()
        self.main_window.update_visualization()
        self.main_window.statusBar().showMessage("数据加载成功", 3000)

    def _on_error(self, msg):
        self.main_window.hide_loading()
        QMessageBox.critical(self, "错误", f"操作失败:\n{msg[:500]}")

    def _run_band_selection(self):
        if self.hs_data.data is None:
            QMessageBox.warning(self, "提示", "请先加载数据")
            return
        
        method = self.method_combo.currentText()
        n_bands = self.n_bands_spin.value()
        
        self.main_window.show_loading(f"波段选择中... ({method})")
        
        def select_task():
            indices, scores = BandSelector.select_bands(
                self.hs_data.data, method, n_bands, self.hs_data.labels
            )
            return {'indices': indices, 'scores': scores, 'method': method}
        
        self.worker = WorkerThread(select_task)
        self.worker.finished.connect(self._on_bands_selected)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_bands_selected(self, result):
        self.main_window.hide_loading()
        
        self.selected_bands = result['indices']
        
        text = f"方法: {result['method']}\n"
        text += f"选中 {len(self.selected_bands)} 个波段\n"
        text += f"索引: {self.selected_bands}"
        self.band_result.setText(text)
        
        self.band_list.clear()
        for idx in self.selected_bands:
            score = result['scores'][idx] if idx < len(result['scores']) else 0
            item = QListWidgetItem(f"波段 {idx}: 得分 {score:.4f}")
            self.band_list.addItem(item)
        
        self.bandsSelected.emit()
        self.main_window.update_spectrum_plot()
        self.main_window.statusBar().showMessage(f"波段选择完成: {len(self.selected_bands)} 个波段", 3000)

    def _run_classification(self):
        if self.hs_data.data is None:
            QMessageBox.warning(self, "提示", "请先加载数据")
            return
        
        if self.hs_data.labels is None:
            QMessageBox.warning(self, "提示", "请先加载标签文件")
            return
        
        if not self.selected_bands:
            QMessageBox.warning(self, "提示", "请先执行波段选择")
            return
        
        clf_name = self.clf_combo.currentText()
        test_ratio = self.test_spin.value()
        
        self.main_window.show_loading(f"分类训练中... ({clf_name})")
        
        def classify_task():
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
            from sklearn.svm import SVC
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.linear_model import LogisticRegression
            
            X = self.hs_data.data[:, :, self.selected_bands]
            y = self.hs_data.labels
            
            h, w, n_bands = X.shape
            X = X.reshape(-1, n_bands)
            y = y.flatten()
            
            valid_mask = y > 0
            X = X[valid_mask]
            y = y[valid_mask]
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_ratio, random_state=42, stratify=y
            )
            
            classifiers = {
                'SVM': SVC(kernel='rbf', random_state=42),
                'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
                'KNN': KNeighborsClassifier(n_neighbors=5),
                'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42)
            }
            
            clf = classifiers[clf_name]
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            
            y_pred_full = clf.predict(self.hs_data.data[:, :, self.selected_bands].reshape(-1, n_bands))
            y_pred_full = y_pred_full.reshape(h, w)
            
            return {
                'accuracy': accuracy_score(y_test, y_pred),
                'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0),
                'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
                'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'y_test': y_test,
                'y_pred': y_pred,
                'y_pred_full': y_pred_full,
                'classifier': clf_name
            }
        
        self.worker = WorkerThread(classify_task)
        self.worker.finished.connect(self._on_classification_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_classification_done(self, result):
        self.main_window.hide_loading()
        
        text = f"分类器: {result['classifier']}\n"
        text += f"准确率: {result['accuracy']:.4f}\n"
        text += f"F1分数: {result['f1']:.4f}\n"
        text += f"精确率: {result['precision']:.4f}\n"
        text += f"召回率: {result['recall']:.4f}"
        self.clf_result.setText(text)
        
        self.classificationDone.emit()
        self.main_window.show_classification_result(result)
        self.main_window.statusBar().showMessage(f"分类完成: 准确率 {result['accuracy']:.4f}", 3000)

    def _export_mat(self):
        if self.hs_data.data is None:
            QMessageBox.warning(self, "提示", "没有数据可导出")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "导出MAT文件", "", "MAT 文件 (*.mat)")
        if path:
            try:
                import scipy.io as sio
                save_dict = {
                    'data': self.hs_data.data,
                    'selected_bands': np.array(self.selected_bands)
                }
                if self.hs_data.labels is not None:
                    save_dict['labels'] = self.hs_data.labels
                sio.savemat(path, save_dict)
                QMessageBox.information(self, "成功", f"数据已导出到:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def _export_csv(self):
        if not self.selected_bands:
            QMessageBox.warning(self, "提示", "请先执行波段选择")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "导出CSV文件", "", "CSV 文件 (*.csv)")
        if path:
            try:
                import pandas as pd
                X = self.hs_data.data[:, :, self.selected_bands]
                h, w, n = X.shape
                df = pd.DataFrame(X.reshape(-1, n), columns=[f'band_{i}' for i in self.selected_bands])
                if self.hs_data.labels is not None:
                    df['label'] = self.hs_data.labels.flatten()
                df.to_csv(path, index=False)
                QMessageBox.information(self, "成功", f"数据已导出到:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def _export_image(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出图像", "", "PNG 图像 (*.png)")
        if path:
            try:
                self.main_view.save_current_image(path)
                QMessageBox.information(self, "成功", f"图像已导出到:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")


class MainViewArea(QWidget):
    """主视图区域"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.hs_data = main_window.hs_data
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 2px solid #dee2e6; border-radius: 8px; background: white; }
            QTabBar::tab { background: #f8f9fa; border: 1px solid #dee2e6; border-bottom: none;
                border-top-left-radius: 6px; border-top-right-radius: 6px; padding: 8px 16px;
                margin-right: 2px; font-weight: bold; font-size: 11px; }
            QTabBar::tab:selected { background: white; border-bottom: 2px solid white; }
            QTabBar::tab:hover { background: #e3f2fd; }
        """)
        
        self.tabs.addTab(self._create_image_tab(), "🖼️ 高光谱图像")
        self.tabs.addTab(self._create_spectrum_tab(), "📊 光谱曲线")
        self.tabs.addTab(self._create_result_tab(), "📈 分类结果")
        
        layout.addWidget(self.tabs)

    def _create_image_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("显示:"))
        self.display_mode = QComboBox()
        self.display_mode.addItems(["RGB合成", "单波段", "伪彩色", "真实标签"])
        self.display_mode.currentTextChanged.connect(self.update_image)
        ctrl.addWidget(self.display_mode)
        
        ctrl.addWidget(QLabel("波段:"))
        self.band_slider = QSlider(Qt.Horizontal)
        self.band_slider.setRange(0, 200)
        self.band_slider.setValue(0)
        self.band_slider.setMaximumWidth(150)
        self.band_slider.valueChanged.connect(self.update_image)
        ctrl.addWidget(self.band_slider)
        self.band_label = QLabel("0")
        self.band_label.setMinimumWidth(30)
        ctrl.addWidget(self.band_label)
        ctrl.addStretch()
        l.addLayout(ctrl)
        
        hint = QLabel("💡 提示: 鼠标指向图像位置，滚动滚轮可缩放")
        hint.setStyleSheet("color: #666; font-size: 10px;")
        l.addWidget(hint)
        
        self.image_fig = Figure(figsize=(10, 8), facecolor='white')
        self.image_canvas = ZoomableCanvas(self.image_fig, self)
        self.image_toolbar = NavigationToolbar(self.image_canvas, self)
        l.addWidget(self.image_toolbar)
        l.addWidget(self.image_canvas)
        
        return w

    def _create_spectrum_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        self.spectrum_fig = Figure(figsize=(10, 8), facecolor='white')
        self.spectrum_canvas = FigureCanvas(self.spectrum_fig)
        self.spectrum_toolbar = NavigationToolbar(self.spectrum_canvas, self)
        l.addWidget(self.spectrum_toolbar)
        l.addWidget(self.spectrum_canvas)
        
        return w

    def _create_result_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        self.result_fig = Figure(figsize=(12, 8), facecolor='white')
        self.result_canvas = FigureCanvas(self.result_fig)
        self.result_toolbar = NavigationToolbar(self.result_canvas, self)
        l.addWidget(self.result_toolbar)
        l.addWidget(self.result_canvas)
        
        return w

    def update_image(self):
        self.image_fig.clear()
        data = self.hs_data.data
        labels = self.hs_data.labels
        
        ax = self.image_fig.add_subplot(111)
        
        if data is None:
            ax.text(0.5, 0.5, "请先加载数据", ha='center', va='center', fontsize=16, color='gray')
            ax.axis('off')
            self.image_canvas.draw()
            return
        
        mode = self.display_mode.currentText()
        h, w, bands = data.shape
        self.band_slider.setMaximum(bands - 1)
        band_idx = self.band_slider.value()
        self.band_label.setText(str(band_idx))
        
        if mode == "RGB合成":
            rgb = self.hs_data.get_rgb_image()
            ax.imshow(rgb)
            ax.set_title(f"RGB伪彩色合成", fontsize=12, fontweight='bold')
        elif mode == "单波段":
            band_img = self.hs_data.get_band_image(band_idx)
            im = ax.imshow(band_img, cmap='gray')
            ax.set_title(f"波段 {band_idx}", fontsize=12)
            self.image_fig.colorbar(im, ax=ax, fraction=0.046)
        elif mode == "伪彩色":
            band_img = self.hs_data.get_band_image(band_idx)
            im = ax.imshow(band_img, cmap='jet')
            ax.set_title(f"波段 {band_idx} (伪彩色)", fontsize=12)
            self.image_fig.colorbar(im, ax=ax, fraction=0.046)
        elif mode == "真实标签":
            if labels is not None:
                unique_labels = np.unique(labels)
                n_classes = len(unique_labels[unique_labels > 0])
                
                colors = ['#000000', '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
                         '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080',
                         '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000']
                
                while len(colors) < len(unique_labels):
                    colors.extend(colors[:10])
                
                cmap = ListedColormap(colors[:len(unique_labels)])
                im = ax.imshow(labels, cmap=cmap, interpolation='nearest')
                ax.set_title(f"真实标签图 ({n_classes} 类)", fontsize=12, fontweight='bold')
            else:
                ax.text(0.5, 0.5, "未加载标签", ha='center', va='center', fontsize=14)
        
        ax.axis('off')
        self.image_fig.tight_layout()
        self.image_canvas.draw()

    def update_spectrum(self, selected_bands=None):
        self.spectrum_fig.clear()
        data = self.hs_data.data
        
        ax = self.spectrum_fig.add_subplot(111)
        
        if data is None:
            ax.text(0.5, 0.5, "请先加载数据", ha='center', va='center', fontsize=16, color='gray')
            ax.axis('off')
            self.spectrum_canvas.draw()
            return
        
        h, w, bands = data.shape
        mean_spec = data.reshape(-1, bands).mean(axis=0)
        wavelengths = np.arange(bands)
        
        ax.plot(wavelengths, mean_spec, 'b-', linewidth=2, label='平均光谱', alpha=0.7)
        ax.fill_between(wavelengths, mean_spec, alpha=0.2)
        
        if selected_bands:
            ax.scatter(selected_bands, mean_spec[selected_bands], c='red', s=50, zorder=5, label='选中波段')
            for idx in selected_bands[:10]:
                ax.axvline(x=idx, color='red', linestyle='--', alpha=0.3)
        
        ax.set_xlabel("波段索引", fontsize=11)
        ax.set_ylabel("平均反射率", fontsize=11)
        ax.set_title("光谱曲线与选中波段", fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        self.spectrum_fig.tight_layout()
        self.spectrum_canvas.draw()

    def update_classification(self, result):
        self.result_fig.clear()
        
        if result is None:
            ax = self.result_fig.add_subplot(111)
            ax.text(0.5, 0.5, "请先执行分类", ha='center', va='center', fontsize=16, color='gray')
            ax.axis('off')
            self.result_canvas.draw()
            return
        
        gs = self.result_fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        ax1 = self.result_fig.add_subplot(gs[0, 0])
        metrics = ['accuracy', 'f1', 'precision', 'recall']
        values = [result.get(m, 0) for m in metrics]
        colors = ['#3498db', '#9b59b6', '#e67e22', '#27ae60']
        bars = ax1.bar(['准确率', 'F1', '精确率', '召回率'], values, color=colors)
        ax1.set_ylim(0, 1.1)
        ax1.set_title("分类指标", fontweight='bold')
        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{val:.3f}', ha='center', fontsize=9, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        ax2 = self.result_fig.add_subplot(gs[0, 1])
        cm = result.get('confusion_matrix')
        if cm is not None:
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax2, cbar_kws={'shrink': 0.8})
            ax2.set_title("混淆矩阵", fontweight='bold')
            ax2.set_xlabel("预测")
            ax2.set_ylabel("真实")
        
        ax3 = self.result_fig.add_subplot(gs[0, 2])
        y_test = result.get('y_test')
        y_pred = result.get('y_pred')
        if y_test is not None and y_pred is not None:
            ax3.scatter(y_test, y_pred, alpha=0.5, s=10)
            lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
            ax3.plot(lims, lims, 'r--', lw=2, label='理想')
            ax3.set_title("预测 vs 真实", fontweight='bold')
            ax3.legend()
        
        ax4 = self.result_fig.add_subplot(gs[1, 0])
        if self.hs_data.labels is not None:
            unique_labels = np.unique(self.hs_data.labels)
            n_classes = len(unique_labels[unique_labels > 0])
            colors = ['#000000', '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
                     '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080',
                     '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000']
            cmap = ListedColormap(colors[:len(unique_labels)])
            ax4.imshow(self.hs_data.labels, cmap=cmap)
            ax4.set_title("真实标签", fontweight='bold')
            ax4.axis('off')
        
        ax5 = self.result_fig.add_subplot(gs[1, 1])
        y_pred_full = result.get('y_pred_full')
        if y_pred_full is not None:
            unique_labels = np.unique(self.hs_data.labels)
            colors = ['#000000', '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
                     '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080',
                     '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000']
            cmap = ListedColormap(colors[:len(unique_labels)])
            ax5.imshow(y_pred_full, cmap=cmap)
            ax5.set_title("预测结果", fontweight='bold')
            ax5.axis('off')
        
        ax6 = self.result_fig.add_subplot(gs[1, 2])
        if y_pred_full is not None and self.hs_data.labels is not None:
            diff = (y_pred_full != self.hs_data.labels).astype(float)
            diff[self.hs_data.labels == 0] = np.nan
            ax6.imshow(diff, cmap='Reds')
            ax6.set_title("分类错误区域", fontweight='bold')
            ax6.axis('off')
        
        self.result_fig.suptitle(f"分类结果 - {result.get('classifier', '')}", fontsize=14, fontweight='bold')
        self.result_fig.tight_layout()
        self.result_canvas.draw()

    def save_current_image(self, path):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            self.image_fig.savefig(path, dpi=150, bbox_inches='tight')
        elif current_tab == 1:
            self.spectrum_fig.savefig(path, dpi=150, bbox_inches='tight')
        elif current_tab == 2:
            self.result_fig.savefig(path, dpi=150, bbox_inches='tight')


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.hs_data = HyperspectralData()
        self.loading = None
        self._init_ui()
        
    def _init_ui(self):
        self.setWindowTitle("高光谱图像波段选择与分类系统 v6.0")
        self.setGeometry(80, 80, 1500, 950)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(300)
        left_scroll.setMaximumWidth(380)
        left_scroll.setStyleSheet("QScrollArea{border:none;background:#f5f6fa;}")
        
        self.control = ControlPanel(self)
        left_scroll.setWidget(self.control)
        
        self.main_view = MainViewArea(self)
        
        splitter.addWidget(left_scroll)
        splitter.addWidget(self.main_view)
        splitter.setSizes([350, 1150])
        
        main_layout.addWidget(splitter)
        
        self.loading = LoadingWidget(self)
        
        self._create_menu()
        self._create_status()
        
        self.control.dataLoaded.connect(self.update_visualization)
        self.control.bandsSelected.connect(self.update_spectrum_plot)
        self.control.classificationDone.connect(lambda: None)

    def _create_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件")
        
        open_action = QAction("打开数据", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_status(self):
        self.statusBar().showMessage("就绪 - 请加载数据文件和标签文件")

    def _open_file(self):
        self.control._browse_data()

    def _show_about(self):
        QMessageBox.about(self, "关于", 
            "高光谱图像波段选择与分类系统 v6.0\n\n"
            "工作流程:\n"
            "1. 加载数据文件和标签文件\n"
            "2. 执行波段选择\n"
            "3. 基于选中波段进行分类\n"
            "4. 查看结果并导出\n\n"
            "提示: 鼠标指向图像位置，滚动滚轮可缩放")

    def show_loading(self, msg):
        self.loading.show_loading(msg)

    def hide_loading(self):
        self.loading.hide_loading()

    def update_visualization(self):
        self.main_view.update_image()

    def update_spectrum_plot(self):
        self.main_view.update_spectrum(self.control.selected_bands)

    def show_classification_result(self, result):
        self.main_view.update_classification(result)
        self.main_view.tabs.setCurrentIndex(2)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(248, 249, 250))
    palette.setColor(QPalette.WindowText, QColor(33, 37, 41))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(33, 37, 41))
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
