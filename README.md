# Hyperspectral-Band-Selector

## V1.0 传统编码方式
##### 2026.2.6
仅仅是粗略的设计了一个前端界面，看一下前后端的逻辑能不能跑通
<img width="2559" height="1368" alt="image" src="https://github.com/user-attachments/assets/821fe487-7e57-4c0d-b0f2-60610b294f7d" />

## V2.0 angent编码方式
##### 2026.2.8
重写了大部分代码，完成mat文件上传加载和数据可视化的部分功能，但是界面并不美观

## v3.0
##### 2026.2.12
这一过程尝试使用不同的angent来进行编码，基于deepseek,glm等基础模型的angent，此外尝试了不同的编辑器，像通义灵码，cursor，trae等
系统性的重构了不同功能的代码段，分到不同的文件夹下去存放

## v3.1
#### 2026.3.3
梳理了框架，增强了鲁棒性，解决数据加载和原始数据可视化的部分问题
现在进行一个系统上的集成测试
1，数据加载功能，选取文件后点击加载数据，稍等片刻，就有一个可视化的界面，右侧可以选择（RGB合成，伪彩色，单波段不同的可视化显示选项）
2，放大缩小无法选择区域
3，降维选择，目标检测，图像分类逻辑上十分混乱
<img width="1491" height="984" alt="image" src="https://github.com/user-attachments/assets/c05badc1-a97b-4928-95cc-1aa04d46d08c" />

## v3.2
#### 2026.3.4
针对3.1版本的问题进行了优化，增加了标签图的读取与可视化展示，同时完成了数据展示的放大缩小等功能
同时用pca的基础方法进行了一个demo的演示，目前看起来效果还不错

<img width="1701" height="1203" alt="image" src="https://github.com/user-attachments/assets/f1622419-6126-4d89-98f9-a7cceb372b83" />





