"""
Classifiers Module - 分类器模块
===============================

包含各种分类器实现
"""

from .base import BaseClassifier
from .svm_classifier import SVMClassifier
from .rf_classifier import RFClassifier
from .knn_classifier import KNNClassifier
from .lr_classifier import LRClassifier

CLASSIFIER_REGISTRY = {
    'SVM': SVMClassifier,
    'RandomForest': RFClassifier,
    'KNN': KNNClassifier,
    'LogisticRegression': LRClassifier
}

def get_available_classifiers():
    return list(CLASSIFIER_REGISTRY.keys())

def get_classifier(classifier_name: str, **kwargs):
    if classifier_name not in CLASSIFIER_REGISTRY:
        raise ValueError(f"未知的分类器: {classifier_name}")
    return CLASSIFIER_REGISTRY[classifier_name](**kwargs)

__all__ = [
    'BaseClassifier',
    'SVMClassifier',
    'RFClassifier',
    'KNNClassifier',
    'LRClassifier',
    'get_available_classifiers',
    'get_classifier',
    'CLASSIFIER_REGISTRY'
]
