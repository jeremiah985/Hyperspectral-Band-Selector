"""
Configuration - 配置模块
"""

from pathlib import Path
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).parent.parent.absolute()

COLORS = {
    'primary': '#3498db',
    'success': '#27ae60',
    'warning': '#e67e22',
    'danger': '#e74c3c',
    'purple': '#9b59b6',
    'teal': '#1abc9c',
    'dark': '#2c3e50',
    'gray': '#95a5a6',
    'light': '#f8f9fa'
}

CLASS_COLORS = [
    '#000000', '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
    '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080',
    '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000'
]

def setup_chinese():
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

def darken_color(hex_color: str, factor: float = 0.75) -> str:
    c = hex_color.lstrip('#')
    rgb = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
    d = tuple(int(v * factor) for v in rgb)
    return f"#{d[0]:02x}{d[1]:02x}{d[2]:02x}"
