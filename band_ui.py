"""
经典流畅的波段选择系统UI界面
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

class ClassicButton(QPushButton):
    """经典风格按钮 - 现代且专业"""
    def __init__(self, text, icon=None, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(38)
        
        if icon:
            self.setIcon(QIcon(icon))
        
        # 专业蓝色调
        self.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border: 1px solid #34495E;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #3498DB;
                border-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #2980B9;
                border-color: #1C6EA4;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
            QPushButton:checked {
                background-color: #3498DB;
                border-color: #2980B9;
                font-weight: bold;
            }
        """)
        
        # 添加图标和文字的布局
        if icon:
            layout = QHBoxLayout()
            layout.addStretch()
            layout.addWidget(QLabel(text))
            layout.addStretch()
            self.setLayout(layout)

class MetricCard(QFrame):
    """指标卡片 - 用于显示各种数据指标"""
    def __init__(self, title, value="0", unit="", color="#3498DB", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.unit = unit
        self.color = color
        
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(1)
        self.setMaximumHeight(120)
        
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            font-size: 13px;
            color: #7F8C8D;
            font-weight: 500;
        """)
        
        # 数值
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {self.color};
        """)
        
        # 单位
        unit_label = QLabel(self.unit)
        unit_label.setStyleSheet("""
            font-size: 12px;
            color: #95A5A6;
            font-style: italic;
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(unit_label)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
    
    def update_value(self, new_value, new_color=None):
        """更新显示的值"""
        self.value_label.setText(str(new_value))
        if new_color:
            self.value_label.setStyleSheet(f"""
                font-size: 28px;
                font-weight: bold;
                color: {new_color};
            """)

class BandSelectorWidget(QWidget):
    """波段选择器 - 专业网格布局"""
    def __init__(self, total_bands=30, parent=None):
        super().__init__(parent)
        self.total_bands = total_bands
        self.selected_bands = []
        self.band_buttons = []
        
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # 标题栏
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("波段选择")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2C3E50;
        """)
        
        self.stats_label = QLabel("未选择波段")
        self.stats_label.setStyleSheet("""
            font-size: 12px;
            color: #7F8C8D;
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.stats_label)
        
        main_layout.addWidget(header)
        
        # 波段网格容器
        grid_container = QWidget()
        grid_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(6)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建波段按钮
        for i in range(self.total_bands):
            btn = QPushButton(f"{i+1:02d}")
            btn.setCheckable(True)
            btn.setFixedSize(45, 45)
            btn.setProperty("band_index", i)
            
            # 动态样式
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8F9FA;
                    border: 1px solid #DEE2E6;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    color: #495057;
                }
                QPushButton:hover {
                    background-color: #E9ECEF;
                    border-color: #CED4DA;
                }
                QPushButton:checked {
                    background-color: #3498DB;
                    color: white;
                    border-color: #2980B9;
                    font-weight: bold;
                }
            """)
            
            btn.clicked.connect(self.on_band_clicked)
            self.band_buttons.append(btn)
            
            # 布局 (5x6网格)
            row = i // 6
            col = i % 6
            grid_layout.addWidget(btn, row, col)
            
        main_layout.addWidget(grid_container)
        
        # 控制按钮
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 5, 0, 0)
        
        self.select_all_btn = ClassicButton("全选")
        self.clear_all_btn = ClassicButton("清空")
        self.random_btn = ClassicButton("随机选择")
        
        self.select_all_btn.clicked.connect(self.select_all_bands)
        self.clear_all_btn.clicked.connect(self.clear_all_bands)
        self.random_btn.clicked.connect(self.select_random_bands)
        
        control_layout.addWidget(self.select_all_btn)
        control_layout.addWidget(self.clear_all_btn)
        control_layout.addWidget(self.random_btn)
        control_layout.addStretch()
        
        main_layout.addWidget(control_widget)
        
        self.setLayout(main_layout)
    
    def on_band_clicked(self):
        """波段点击事件"""
        sender = self.sender()
        band_index = sender.property("band_index")
        
        if sender.isChecked():
            if band_index not in self.selected_bands:
                self.selected_bands.append(band_index)
        else:
            if band_index in self.selected_bands:
                self.selected_bands.remove(band_index)
        
        self.update_stats()
    
    def select_all_bands(self):
        """选择所有波段"""
        for i, btn in enumerate(self.band_buttons):
            btn.setChecked(True)
            if i not in self.selected_bands:
                self.selected_bands.append(i)
        self.update_stats()
    
    def clear_all_bands(self):
        """清空所有选择"""
        for btn in self.band_buttons:
            btn.setChecked(False)
        self.selected_bands.clear()
        self.update_stats()
    
    def select_random_bands(self):
        """随机选择波段"""
        import random
        n_bands = random.randint(3, 12)  # 随机选择3-12个波段
        
        self.clear_all_bands()
        random_bands = random.sample(range(self.total_bands), n_bands)
        
        for idx in random_bands:
            self.band_buttons[idx].setChecked(True)
            self.selected_bands.append(idx)
        
        self.update_stats()
    
    def update_stats(self):
        """更新统计信息"""
        count = len(self.selected_bands)
        if count == 0:
            self.stats_label.setText("未选择波段")
        else:
            self.stats_label.setText(f"已选择 {count} 个波段")
            if count > 0:
                bands_text = ", ".join([str(b+1) for b in sorted(self.selected_bands)])
                self.stats_label.setToolTip(f"选择的波段: {bands_text}")

class MethodSelector(QWidget):
    """方法选择器 - 专业的下拉选择"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 波段选择方法
        band_group = QGroupBox("波段选择方法")
        band_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2C3E50;
            }
        """)
        
        band_layout = QVBoxLayout(band_group)
        self.band_method_combo = QComboBox()
        self.band_method_combo.addItems([
            "手动选择",
            "随机选择", 
            "等间隔选择",
            "方差排序法",
            "相关性分析法",
            "自定义方法1",
            "自定义方法2"
        ])
        self.band_method_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #CED4DA;
                border-radius: 4px;
                background: white;
                font-size: 13px;
                min-height: 36px;
            }
            QComboBox:hover {
                border-color: #3498DB;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #495057;
                margin-right: 10px;
            }
        """)
        band_layout.addWidget(self.band_method_combo)
        
        # 分类器选择
        classifier_group = QGroupBox("分类器选择")
        classifier_group.setStyleSheet(band_group.styleSheet())
        
        classifier_layout = QVBoxLayout(classifier_group)
        self.classifier_combo = QComboBox()
        self.classifier_combo.addItems([
            "支持向量机 (SVM)",
            "随机森林 (Random Forest)",
            "K近邻 (KNN)",
            "决策树 (Decision Tree)",
            "神经网络 (MLP)",
            "逻辑回归 (Logistic Regression)"
        ])
        self.classifier_combo.setStyleSheet(self.band_method_combo.styleSheet())
        classifier_layout.addWidget(self.classifier_combo)
        
        # 参数设置
        param_group = QGroupBox("参数设置")
        param_group.setStyleSheet(band_group.styleSheet())
        
        param_layout = QGridLayout(param_group)
        
        # 测试集比例
        test_label = QLabel("测试集比例:")
        test_label.setStyleSheet("font-size: 12px; color: #495057;")
        
        self.test_size_slider = QSlider(Qt.Horizontal)
        self.test_size_slider.setRange(10, 50)  # 10% - 50%
        self.test_size_slider.setValue(30)  # 默认30%
        self.test_size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #E9ECEF;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3498DB;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #3498DB;
                border-radius: 3px;
            }
        """)
        
        self.test_size_label = QLabel("30%")
        self.test_size_label.setStyleSheet("font-size: 12px; min-width: 40px;")
        
        self.test_size_slider.valueChanged.connect(
            lambda v: self.test_size_label.setText(f"{v}%")
        )
        
        param_layout.addWidget(test_label, 0, 0)
        param_layout.addWidget(self.test_size_slider, 0, 1)
        param_layout.addWidget(self.test_size_label, 0, 2)
        
        layout.addWidget(band_group)
        layout.addWidget(classifier_group)
        layout.addWidget(param_group)
        layout.addStretch()
        
        self.setLayout(layout)

class ResultsDashboard(QWidget):
    """结果仪表盘 - 专业数据展示"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # 标题
        header = QLabel("分析结果")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2C3E50;
            padding-bottom: 5px;
            border-bottom: 2px solid #3498DB;
        """)
        layout.addWidget(header)
        
        # 主要指标卡片网格
        metrics_grid = QWidget()
        grid_layout = QGridLayout(metrics_grid)
        grid_layout.setSpacing(12)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建指标卡片
        self.accuracy_card = MetricCard("分类准确率", "0.0000", "", "#2ECC71")
        self.f1_card = MetricCard("F1得分", "0.0000", "", "#3498DB")
        self.precision_card = MetricCard("精确率", "0.0000", "", "#9B59B6")
        self.recall_card = MetricCard("召回率", "0.0000", "", "#E74C3C")
        
        grid_layout.addWidget(self.accuracy_card, 0, 0)
        grid_layout.addWidget(self.f1_card, 0, 1)
        grid_layout.addWidget(self.precision_card, 1, 0)
        grid_layout.addWidget(self.recall_card, 1, 1)
        
        layout.addWidget(metrics_grid)
        
        # 详细信息区域
        detail_group = QGroupBox("详细信息")
        detail_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2C3E50;
            }
        """)
        
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(120)
        self.detail_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                background-color: #F8F9FA;
            }
        """)
        self.detail_text.setText("等待分析结果...")
        
        detail_layout.addWidget(self.detail_text)
        layout.addWidget(detail_group)
        
        # 时间戳
        self.timestamp_label = QLabel("最后运行: 从未运行")
        self.timestamp_label.setStyleSheet("""
            font-size: 11px;
            color: #95A5A6;
            font-style: italic;
        """)
        layout.addWidget(self.timestamp_label)
        
        self.setLayout(layout)
    
    def update_results(self, results):
        """更新结果展示"""
        # 更新卡片数值
        self.accuracy_card.update_value(f"{results.get('accuracy', 0):.4f}")
        self.f1_card.update_value(f"{results.get('f1_score', 0):.4f}")
        self.precision_card.update_value(f"{results.get('precision', 0):.4f}")
        self.recall_card.update_value(f"{results.get('recall', 0):.4f}")
        
        # 更新详细信息
        detail_text = f"""分类器: {results.get('classifier', 'N/A')}
运行时间: {results.get('run_time', 0):.3f} 秒
波段数量: {results.get('n_bands', 0)} 个
样本数量: {results.get('n_samples', 0)} 个
混淆矩阵大小: {results.get('confusion_matrix_shape', 'N/A')}
"""
        self.detail_text.setText(detail_text)
        
        # 更新时间戳
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.timestamp_label.setText(f"最后运行: {current_time}")

class PlotCanvas(QWidget):
    """绘图画布 - 专业图表展示"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 工具栏
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 5)
        
        plot_type_label = QLabel("图表类型:")
        plot_type_label.setStyleSheet("font-size: 12px; color: #495057;")
        
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems([
            "光谱曲线",
            "混淆矩阵",
            "特征重要性",
            "性能对比",
            "ROC曲线"
        ])
        self.plot_type_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #CED4DA;
                border-radius: 4px;
                background: white;
                font-size: 12px;
                min-width: 120px;
            }
        """)
        
        toolbar_layout.addWidget(plot_type_label)
        toolbar_layout.addWidget(self.plot_type_combo)
        toolbar_layout.addStretch()
        
        # 导出按钮
        self.export_plot_btn = ClassicButton("导出图表")
        toolbar_layout.addWidget(self.export_plot_btn)
        
        layout.addWidget(toolbar_widget)
        
        # Matplotlib画布
        self.figure = plt.figure(figsize=(10, 6), dpi=100)
        self.figure.patch.set_facecolor('#FFFFFF')
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
        """)
        
        # 导航工具栏
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px;
                spacing: 4px;
            }
            QToolButton {
                border: 1px solid #CED4DA;
                border-radius: 3px;
                padding: 4px;
                background: white;
                min-width: 28px;
                min-height: 28px;
            }
            QToolButton:hover {
                background-color: #E9ECEF;
                border-color: #ADB5BD;
            }
            QToolButton:pressed {
                background-color: #DEE2E6;
            }
        """)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
    
    def plot_spectral(self, data, selected_bands=None):
        """绘制光谱曲线"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if selected_bands and len(selected_bands) > 0:
            # 绘制选择的波段
            for i, band in enumerate(selected_bands[:8]):  # 最多显示8个波段
                ax.plot(data[:100, band], label=f'波段 {band+1}', 
                       linewidth=1.5, alpha=0.8)
        else:
            # 绘制所有波段的均值
            mean_spectrum = data.mean(axis=0)
            ax.plot(mean_spectrum, color='#3498DB', linewidth=2, label='平均光谱')
        
        ax.set_xlabel('样本索引', fontsize=11)
        ax.set_ylabel('反射率', fontsize=11)
        ax.set_title('光谱曲线', fontsize=13, fontweight='bold', pad=12)
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#F8F9FA')
        
        self.figure.tight_layout()
        self.canvas.draw()

class StatusBar(QWidget):
    """状态栏 - 显示系统状态"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 8, 15, 8)
        
        # 状态指示器
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            font-size: 14px;
            color: #2ECC71;
            font-weight: bold;
        """)
        
        self.status_text = QLabel("系统就绪")
        self.status_text.setStyleSheet("font-size: 12px; color: #495057;")
        
        layout.addWidget(self.status_indicator)
        layout.addWidget(self.status_text)
        layout.addSpacing(20)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #E9ECEF;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setVisible(False)
        
        layout.addWidget(self.progress_bar, 1)
        layout.addSpacing(20)
        
        # 内存使用
        self.memory_label = QLabel("内存: --")
        self.memory_label.setStyleSheet("font-size: 11px; color: #7F8C8D;")
        
        # 时间显示
        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size: 11px; color: #7F8C8D;")
        
        layout.addWidget(self.memory_label)
        layout.addSpacing(15)
        layout.addWidget(self.time_label)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top: 1px solid #E0E0E0;
            }
        """)
        
        # 启动时钟
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
    
    def update_time(self):
        """更新时间显示"""
        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.time_label.setText(current_time)
    
    def set_status(self, text, status_type="info"):
        """设置状态信息"""
        self.status_text.setText(text)
        
        colors = {
            "info": "#3498DB",      # 蓝色
            "success": "#2ECC71",   # 绿色
            "warning": "#F39C12",   # 橙色
            "error": "#E74C3C",     # 红色
            "processing": "#9B59B6" # 紫色
        }
        
        color = colors.get(status_type, "#3498DB")
        self.status_indicator.setStyleSheet(f"""
            font-size: 14px;
            color: {color};
            font-weight: bold;
        """)
    
    def set_progress(self, value, maximum=100):
        """设置进度"""
        if value == 0:
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(maximum)
            self.progress_bar.setValue(value)

class MainWindow(QMainWindow):
    """主窗口 - 经典专业设计"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 窗口设置
        self.setWindowTitle("智能波段选择与分类系统")
        self.setGeometry(100, 50, 1600, 900)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon())
        
        # 设置全局样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QWidget {
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
        """)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部工具栏
        self.create_toolbar(main_layout)
        
        # 主内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # 左侧面板 (控制面板)
        left_panel = self.create_left_panel()
        content_layout.addWidget(left_panel)
        
        # 右侧面板 (显示面板)
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 1)
        
        main_layout.addWidget(content_widget, 1)
        
        # 底部状态栏
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)
        
        # 设置窗口标志
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
    
    def create_toolbar(self, parent_layout):
        """创建顶部工具栏"""
        toolbar = QWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                border-bottom: 1px solid #34495E;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # 应用图标和标题
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_icon = QLabel("🌐")
        title_icon.setStyleSheet("font-size: 24px;")
        
        title_text = QLabel("智能波段选择系统")
        title_text.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            margin-left: 10px;
        """)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        
        # 工具栏按钮
        toolbar_buttons = QWidget()
        buttons_layout = QHBoxLayout(toolbar_buttons)
        buttons_layout.setSpacing(10)
        
        # 创建工具栏按钮
        toolbar_btns = [
            ("🏠 主页", "#home"),
            ("📊 数据", "#data"),
            ("🔧 设置", "#settings"),
            ("❓ 帮助", "#help")
        ]
        
        for text, obj_name in toolbar_btns:
            btn = ClassicButton(text)
            btn.setObjectName(obj_name)
            btn.setFixedHeight(36)
            buttons_layout.addWidget(btn)
        
        buttons_layout.addStretch()
        
        layout.addWidget(title_widget)
        layout.addWidget(toolbar_buttons)
        
        parent_layout.addWidget(toolbar)
    
    def create_left_panel(self):
        """创建左侧控制面板"""
        panel = QWidget()
        panel.setMaximumWidth(400)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(20)
        
        # 波段选择器
        self.band_selector = BandSelectorWidget()
        layout.addWidget(self.band_selector)
        
        # 方法选择器
        self.method_selector = MethodSelector()
        layout.addWidget(self.method_selector)
        
        # 控制按钮组
        control_group = QGroupBox("分析控制")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2C3E50;
            }
        """)
        
        control_layout = QVBoxLayout(control_group)
        
        # 按钮网格
        button_grid = QGridLayout()
        
        self.load_data_btn = ClassicButton("📂 加载数据")
        self.generate_data_btn = ClassicButton("🔄 生成数据")
        self.run_analysis_btn = ClassicButton("🚀 开始分析")
        self.stop_analysis_btn = ClassicButton("⏹️ 停止分析")
        self.export_results_btn = ClassicButton("💾 导出结果")
        self.reset_all_btn = ClassicButton("🗑️ 重置系统")
        
        # 设置按钮颜色
        self.run_analysis_btn.setStyleSheet(self.run_analysis_btn.styleSheet() + """
            QPushButton {
                background-color: #27AE60;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)
        
        button_grid.addWidget(self.load_data_btn, 0, 0)
        button_grid.addWidget(self.generate_data_btn, 0, 1)
        button_grid.addWidget(self.run_analysis_btn, 1, 0)
        button_grid.addWidget(self.stop_analysis_btn, 1, 1)
        button_grid.addWidget(self.export_results_btn, 2, 0)
        button_grid.addWidget(self.reset_all_btn, 2, 1)
        
        control_layout.addLayout(button_grid)
        layout.addWidget(control_group)
        
        # 结果仪表盘
        self.results_dashboard = ResultsDashboard()
        layout.addWidget(self.results_dashboard)
        
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self):
        """创建右侧显示面板"""
        panel = QWidget()
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # 图表区域
        chart_group = QGroupBox("可视化分析")
        chart_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #2C3E50;
            }
        """)
        
        chart_layout = QVBoxLayout(chart_group)
        self.plot_canvas = PlotCanvas()
        chart_layout.addWidget(self.plot_canvas)
        
        layout.addWidget(chart_group, 1)
        
        # 数据表格区域
        table_group = QGroupBox("数据预览")
        table_group.setStyleSheet(chart_group.styleSheet())
        table_group.setMaximumHeight(250)
        
        table_layout = QVBoxLayout(table_group)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(['波段', '最小值', '最大值', '均值', '标准差'])
        self.data_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #2C3E50;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                alternate-background-color: #F8F9FA;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)
        
        table_layout.addWidget(self.data_table)
        layout.addWidget(table_group)
        
        return panel
    
    def update_status(self, message, status_type="info"):
        """更新状态栏"""
        self.status_bar.set_status(message, status_type)
    
    def update_progress(self, value, maximum=100):
        """更新进度条"""
        self.status_bar.set_progress(value, maximum)