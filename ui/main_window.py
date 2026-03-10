"""
Main Window - 主窗口
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QScrollArea, QMenuBar, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

import sys
sys.path.insert(0, str(__file__).rsplit('\\ui', 1)[0])

from core.data_manager import HyperspectralData
from core.utils import LoadingWidget
from ui.control_panel import ControlPanel
from ui.main_view import MainViewArea


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.hs_data = HyperspectralData()
        self.loading = None
        self._init_ui()
        
    def _init_ui(self):
        self.setWindowTitle("高光谱图像波段选择与分类系统 v7.0 (模块化版)")
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
            "高光谱图像波段选择与分类系统 v7.0 (模块化版)\n\n"
            "模块结构:\n"
            "- core: 数据管理、工具类、配置\n"
            "- algorithms: 波段选择算法\n"
            "- classifiers: 分类器\n"
            "- ui: 界面组件\n\n"
            "工作流程:\n"
            "1. 加载数据文件和标签文件\n"
            "2. 执行波段选择\n"
            "3. 基于选中波段进行分类\n"
            "4. 查看结果并导出")

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
