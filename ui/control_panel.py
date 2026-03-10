"""
Control Panel - 左侧控制面板
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QGroupBox, 
    QLabel, QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QFileDialog, QMessageBox, QFormLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal

import sys
from pathlib import Path
sys.path.insert(0, str(__file__).rsplit('\\ui', 1)[0])

from core.config import COLORS, PROJECT_ROOT
from core.data_manager import HyperspectralData
from core.utils import WorkerThread
from ui.widgets import SectionHeader, StyledButton


class ControlPanel(QWidget):
    """左侧控制面板"""
    
    dataLoaded = pyqtSignal()
    bandsSelected = pyqtSignal()
    classificationDone = pyqtSignal()

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.hs_data: HyperspectralData = main_window.hs_data
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

    def _create_data_section(self):
        g = QGroupBox()
        g.setStyleSheet("QGroupBox{border:1px solid #ddd;border-radius:8px;margin-top:0;padding-top:8px;}")
        l = QVBoxLayout(g)
        l.setSpacing(6)
        
        l.addWidget(SectionHeader("数据加载", "📁", COLORS['primary']))
        
        l.addWidget(QLabel("<b>数据文件:</b>"))
        data_h = QHBoxLayout()
        self.data_edit = QLineEdit()
        self.data_edit.setPlaceholderText("选择数据文件 (*.mat)")
        self.data_edit.setStyleSheet("padding:6px;border:1px solid #ccc;border-radius:4px;background:white;")
        data_btn = StyledButton("浏览", COLORS['primary'])
        data_btn.clicked.connect(self._browse_data)
        data_h.addWidget(self.data_edit, 1)
        data_h.addWidget(data_btn)
        l.addLayout(data_h)
        
        l.addWidget(QLabel("<b>标签文件:</b>"))
        label_h = QHBoxLayout()
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("选择标签文件 (*_gt.mat)")
        self.label_edit.setStyleSheet("padding:6px;border:1px solid #ccc;border-radius:4px;background:white;")
        label_btn = StyledButton("浏览", COLORS['primary'])
        label_btn.clicked.connect(self._browse_label)
        label_h.addWidget(self.label_edit, 1)
        label_h.addWidget(label_btn)
        l.addLayout(label_h)
        
        btn_h = QHBoxLayout()
        load_btn = StyledButton("📥 加载数据", COLORS['success'])
        load_btn.clicked.connect(self._load_data)
        auto_btn = StyledButton("🔄 自动匹配", COLORS['purple'])
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
        
        l.addWidget(SectionHeader("波段选择", "🎯", COLORS['purple']))
        
        form = QFormLayout()
        form.setSpacing(4)
        
        self.method_combo = QComboBox()
        from algorithms import get_available_methods
        self.method_combo.addItems(get_available_methods())
        form.addRow("方法:", self.method_combo)
        
        self.n_bands_spin = QSpinBox()
        self.n_bands_spin.setRange(1, 200)
        self.n_bands_spin.setValue(10)
        form.addRow("波段数:", self.n_bands_spin)
        
        l.addLayout(form)
        
        select_btn = StyledButton("🔍 执行波段选择", COLORS['purple'])
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
        
        l.addWidget(SectionHeader("图像分类", "📊", COLORS['warning']))
        
        form = QFormLayout()
        form.setSpacing(4)
        
        self.clf_combo = QComboBox()
        from classifiers import get_available_classifiers
        self.clf_combo.addItems(get_available_classifiers())
        form.addRow("分类器:", self.clf_combo)
        
        self.test_spin = QDoubleSpinBox()
        self.test_spin.setRange(0.1, 0.5)
        self.test_spin.setValue(0.3)
        self.test_spin.setSingleStep(0.05)
        form.addRow("测试比例:", self.test_spin)
        
        l.addLayout(form)
        
        classify_btn = StyledButton("▶ 训练并分类", COLORS['warning'])
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
        
        l.addWidget(SectionHeader("结果导出", "💾", COLORS['success']))
        
        btn_h = QHBoxLayout()
        mat_btn = StyledButton("导出 .mat", COLORS['success'])
        mat_btn.clicked.connect(self._export_mat)
        csv_btn = StyledButton("导出 .csv", COLORS['primary'])
        csv_btn.clicked.connect(self._export_csv)
        btn_h.addWidget(mat_btn)
        btn_h.addWidget(csv_btn)
        l.addLayout(btn_h)
        
        img_btn = StyledButton("📷 导出图像", COLORS['purple'])
        img_btn.clicked.connect(self._export_image)
        l.addWidget(img_btn)
        
        return g

    def _browse_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择数据文件", str(PROJECT_ROOT / "dataset"),
            "MAT 文件 (*.mat);;所有文件 (*.*)"
        )
        if path:
            self.data_edit.setText(path)
            self.main_window.statusBar().showMessage(f"已选择数据: {Path(path).name}", 3000)

    def _browse_label(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择标签文件", str(PROJECT_ROOT / "dataset"),
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
            from algorithms import get_selector
            selector = get_selector(method)
            indices, scores = selector.select(
                self.hs_data.data, n_bands, self.hs_data.labels
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
            from classifiers import get_classifier
            
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
            
            clf = get_classifier(clf_name)
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
                import numpy as np
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
                self.main_window.main_view.save_current_image(path)
                QMessageBox.information(self, "成功", f"图像已导出到:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")
