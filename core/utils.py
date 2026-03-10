"""
Utils - 工具类模块
==================

包含异步线程、加载动画等工具类
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer


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
    """加载动画组件"""
    
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
