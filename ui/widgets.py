"""
UI Widgets - 基础UI组件
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sys
sys.path.insert(0, str(__file__).rsplit('\\ui', 1)[0])
from core.config import darken_color


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


class SectionHeader(QWidget):
    """分组标题组件"""
    
    def __init__(self, title: str, icon: str, color: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 {darken_color(color)});
                border-radius: 6px;
            }}
        """)
        h = QHBoxLayout(self)
        h.setContentsMargins(10, 6, 10, 6)
        h.addWidget(QLabel(f"<span style='font-size:14px'>{icon}</span>"))
        h.addWidget(QLabel(f"<b style='color:white;font-size:12px'>{title}</b>"))
        h.addStretch()


class StyledButton(QPushButton):
    """样式化按钮"""
    
    def __init__(self, text: str, color: str, height: int = 32, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(height)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{ background: {darken_color(color)}; }}
            QPushButton:pressed {{ background: {darken_color(darken_color(color))}; }}
            QPushButton:disabled {{ background: #95a5a6; }}
        """)
