"""
Main View Area - 主视图区域
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QTabWidget
from PyQt5.QtCore import Qt
import numpy as np
from matplotlib.colors import ListedColormap
import seaborn as sns

import sys
sys.path.insert(0, str(__file__).rsplit('\\ui', 1)[0])

from core.config import CLASS_COLORS
from ui.widgets import ZoomableCanvas

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


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
        self.spectrum_canvas = ZoomableCanvas(self.spectrum_fig, self)
        self.spectrum_toolbar = NavigationToolbar(self.spectrum_canvas, self)
        l.addWidget(self.spectrum_toolbar)
        l.addWidget(self.spectrum_canvas)
        
        return w

    def _create_result_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        self.result_fig = Figure(figsize=(12, 8), facecolor='white')
        self.result_canvas = ZoomableCanvas(self.result_fig, self)
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
                
                cmap = ListedColormap(CLASS_COLORS[:len(unique_labels)])
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
            cmap = ListedColormap(CLASS_COLORS[:len(unique_labels)])
            ax4.imshow(self.hs_data.labels, cmap=cmap)
            ax4.set_title("真实标签", fontweight='bold')
            ax4.axis('off')
        
        ax5 = self.result_fig.add_subplot(gs[1, 1])
        y_pred_full = result.get('y_pred_full')
        if y_pred_full is not None:
            unique_labels = np.unique(self.hs_data.labels)
            cmap = ListedColormap(CLASS_COLORS[:len(unique_labels)])
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
