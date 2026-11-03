---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8
    PropagateID: c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8
    ReservedCode1: 30450220712f58e532066532ba823ecca175bc20b7cfa2d968189fdb98dc8f2bd2bc9b55022100f2e0b88490d8ae18e6dbff9288ceb424ca61b13cf84eae56d12941a3d19a4982
    ReservedCode2: 304502201a341a1899871c909b4c6738f70e7cc0ef890b57414e85e8bf2c740d668b2f40022100950d259dc783092e6b1029cde19d9e8a35feb205349a16b8c3338b27878549fb
---

# 深度学习算法工程师面试准备示例

## 深度学习第一面：基础理论

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | 基础 | BP 反向传播的原理？链式法则？ | 优化 |
| 002 | 基础 | 激活函数的作用？sigmoid、tanh、ReLU？ | 激活 |
| 003 | 基础 | 为什么 ReLU 比 sigmoid 更常用？ Dying ReLU？ | 激活 |
| 004 | 基础 | 权重初始化方法？Xavier、He 初始化？ | 初始化 |
| 005 | 基础 | Batch Normalization 的原理？为什么有效？ | 归一化 |
| 006 | 基础 | Dropout 的原理？为什么能防止过拟合？ | 正则化 |
| 007 | 基础 | L1/L2 正则化的区别？ | 正则化 |
| 008 | 优化 | 梯度下降的变种？SGD、Momentum、Adam？ | 优化器 |
| 009 | 优化 | Adam 优化器的原理？动量和自适应学习率？ | 优化器 |
| 010 | 优化 | 什么是学习率调度？常见的策略？ | 学习率 |
| 011 | 优化 | 梯度消失和梯度爆炸的原因？解决方案？ | 梯度 |
| 012 | 优化 | 什么是 Batch Size？大 batch 的问题？ | 训练 |
| 013 | CNN | 卷积神经网络的核心操作？卷积、池化？ | CNN |
| 014 | CNN | 为什么卷积有效？局部连接和权值共享？ | CNN |
| 015 | CNN | 1x1 卷积的作用？ | 卷积 |
| 016 | CNN | 空洞卷积（Dilated Convolution）？ | 卷积 |
| 017 | CNN | 经典的 CNN 架构？LeNet、AlexNet、VGG、ResNet？ | 架构 |
| 018 | CNN | ResNet 为什么有效？残差连接？ | 架构 |
| 019 | CNN | 空洞残差网络（DRN）？ | 架构 |
| 020 | 目标检测 | RCNN 系列？Faster RCNN 的流程？ | 检测 |
| 021 | 目标检测 | YOLO 的原理？为什么快？ | 检测 |
| 022 | 目标检测 | FPN、RetinaNet 的改进？ | 检测 |
| 023 | 语义分割 | FCN 的原理？全卷积网络？ | 分割 |
| 024 | 语义分割 | U-Net 的结构？跳跃连接？ | 分割 |
| 025 | 语义分割 | DeepLab 系列？空洞空间金字塔池化？ | 分割 |
| 026 | RNN | RNN 的梯度问题？LSTM 和 GRU？ | 序列 |
| 027 | RNN | LSTM 的三个门？遗忘门、输入门、输出门？ | 序列 |
| 028 | RNN | Seq2Seq 模型？Encoder-Decoder？ | 序列 |
| 029 | Attention | Attention 机制的本质？Query、Key、Value？ | Attention |
| 030 | Attention | Soft Attention vs Hard Attention？ | Attention |

---

## 深度学习第二面：前沿与工程

### 设计题示例

**题目：设计一个实时目标检测系统**

考察维度：
1. 模型选择（精度 vs 速度）
2. 模型压缩与量化
3. 部署优化（TensorRT、ONNX）
4. 多尺度目标处理
5. 端侧部署（移动端、嵌入式）

---

## 深度学习强化训练示例

### 强化训练 001：CNN 反向传播

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. 如何推导卷积层的梯度？
2. 为什么卷积可以用矩阵乘法实现？
3. 池化层如何反向传播？Max Pooling 和 Average Pooling？
4. 如何手动实现一个卷积层的 forward 和 backward？
5. PyTorch/TensorFlow 的自动求导机制？

---

## 深度学习晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| 基础理论 | 优化理论、收敛性 | 反向传播 |
| CNN | 架构设计、模块 | 目标检测/分割 |
| 序列模型 | Attention、Transformer | RNN/LSTM |
| 优化 | 梯度裁剪、分布式 | 调参 |
| 工程 | 模型压缩、部署 | TensorRT/ONNX |
