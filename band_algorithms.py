
"""
算法实现模块
"""

import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.metrics import confusion_matrix, classification_report
import time

class BandSelectionAlgorithms:
    """波段选择算法"""
    
    @staticmethod
    def random_selection(n_total, n_select):
        """随机选择"""
        return list(np.random.choice(range(n_total), n_select, replace=False))
    
    @staticmethod
    def equal_interval_selection(n_total, n_select):
        """等间隔选择"""
        indices = np.linspace(0, n_total-1, n_select, dtype=int)
        return list(indices)
    
    @staticmethod
    def variance_based_selection(data, n_select):
        """基于方差的波段选择"""
        variances = np.var(data, axis=0)
        return list(np.argsort(variances)[-n_select:][::-1])
    
    @staticmethod
    def correlation_based_selection(data, n_select):
        """基于相关性的波段选择"""
        # 简化实现：选择与其他波段平均相关性最低的波段
        corr_matrix = np.corrcoef(data.T)
        mean_corr = np.mean(np.abs(corr_matrix - np.eye(corr_matrix.shape[0])), axis=1)
        return list(np.argsort(mean_corr)[:n_select])
    
    @classmethod
    def custom_method_1(cls, data, n_select=None):
        """自定义方法1 - 组合策略"""
        if n_select is None:
            n_select = min(10, data.shape[1] // 2)
        
        # 组合方差和相关性的策略
        variance_indices = cls.variance_based_selection(data, n_select * 2)
        correlation_indices = cls.correlation_based_selection(data, n_select * 2)
        
        # 取并集并选择前n_select个
        combined = list(set(variance_indices + correlation_indices))
        if len(combined) > n_select:
            return combined[:n_select]
        return combined
    
    @classmethod
    def custom_method_2(cls, data, n_select=None):
        """自定义方法2 - 优化策略"""
        if n_select is None:
            n_select = min(8, data.shape[1] // 3)
        
        # 基于类间可分性的简单实现
        if hasattr(cls, '_labels'):
            unique_labels = np.unique(cls._labels)
            if len(unique_labels) > 1:
                # 计算类间距离
                class_means = []
                for label in unique_labels:
                    class_data = data[cls._labels == label]
                    class_means.append(np.mean(class_data, axis=0))
                
                # 计算类间方差
                inter_class_var = np.var(np.array(class_means), axis=0)
                return list(np.argsort(inter_class_var)[-n_select:][::-1])
        
        # 如果没有标签信息，退回方差选择
        return cls.variance_based_selection(data, n_select)

class ClassificationAlgorithms:
    """分类算法"""
    
    def __init__(self):
        self.classifiers = {}
        self.init_classifiers()
        
    def init_classifiers(self):
        """初始化分类器"""
        try:
            from sklearn.svm import SVC
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.neighbors import KNeighborsClassifier
            from sklearn.tree import DecisionTreeClassifier
            from sklearn.neural_network import MLPClassifier
            from sklearn.gaussian_process import GaussianProcessClassifier
            
            self.classifiers = {
                'SVM': {
                    'object': SVC(kernel='rbf', C=1.0, probability=True, random_state=42),
                    'color': '#FF2D55',
                    'icon': '🎯'
                },
                '随机森林': {
                    'object': RandomForestClassifier(n_estimators=100, random_state=42),
                    'color': '#34C759',
                    'icon': '🌲'
                },
                'KNN': {
                    'object': KNeighborsClassifier(n_neighbors=5),
                    'color': '#007AFF',
                    'icon': '👥'
                },
                '决策树': {
                    'object': DecisionTreeClassifier(max_depth=10, random_state=42),
                    'color': '#FF9500',
                    'icon': '🌿'
                },
                '神经网络': {
                    'object': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, 
                                          random_state=42, alpha=0.01),
                    'color': '#AF52DE',
                    'icon': '🧠'
                }
            }
        except ImportError as e:
            print(f"❌ 导入分类器失败: {e}")
    
    def evaluate_classifier(self, classifier_name, X, y, test_size=0.3):
        """评估分类器性能"""
        if classifier_name not in self.classifiers:
            raise ValueError(f"未知的分类器: {classifier_name}")
        
        start_time = time.time()
        
        # 分割数据
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # 获取分类器
        classifier = self.classifiers[classifier_name]['object']
        
        # 训练
        classifier.fit(X_train, y_train)
        
        # 预测
        y_pred = classifier.predict(X_test)
        
        # 计算指标
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        
        # 计算运行时间
        run_time = time.time() - start_time
        
        # 获取详细报告
        report = classification_report(y_test, y_pred, output_dict=True)
        
        results = {
            'classifier': classifier_name,
            'accuracy': accuracy,
            'f1_score': f1,
            'precision': precision,
            'recall': recall,
            'run_time': run_time,
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'classification_report': report,
            'y_test': y_test,
            'y_pred': y_pred,
            'feature_importance': self.get_feature_importance(classifier, X.shape[1])
        }
        
        return results
    
    def get_feature_importance(self, classifier, n_features):
        """获取特征重要性"""
        if hasattr(classifier, 'feature_importances_'):
            return classifier.feature_importances_
        elif hasattr(classifier, 'coef_'):
            # 对于线性模型，使用系数的绝对值平均值
            return np.abs(classifier.coef_).mean(axis=0)
        elif hasattr(classifier, 'named_steps'):
            # 对于Pipeline
            return np.ones(n_features) / n_features
        else:
            # 默认返回均匀分布
            return np.ones(n_features) / n_features
    
    def get_available_classifiers(self):
        """获取可用的分类器列表"""
        return list(self.classifiers.keys())

# %% [markdown]
# ## 4. 🚀 创建主应用程序