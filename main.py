"""
高光谱图像波段选择与分类系统 v7.0 (模块化版)
=============================================

模块结构:
- core: 数据管理、工具类、配置
- algorithms: 波段选择算法 (PCA, ICA, JM距离, 互信息, 方差, 随机)
- classifiers: 分类器 (SVM, RandomForest, KNN, LogisticRegression)
- ui: 界面组件 (控制面板、视图区域、主窗口)

工作流程:
1. 加载数据文件 (.mat) 和标签文件 (*_gt.mat)
2. 可视化高光谱图像 (鼠标滚轮缩放)
3. 波段选择 (降维) - 选择重要波段
4. 基于选中波段进行分类
5. 结果对比与导出

运行方式: python main.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor, QPalette

from core.config import setup_chinese
from ui.main_window import MainWindow


def main():
    setup_chinese()
    
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
