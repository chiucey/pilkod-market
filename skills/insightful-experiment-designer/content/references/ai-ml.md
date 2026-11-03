# AI/ML 实验设计参考

> 适用于机器学习、深度学习、强化学习等实验设计

---

## 超参数调优设计

### 调优策略对比
```
| 方法 | 效率 | 适用场景 | 缺点 |
|------|------|---------|------|
| Grid Search | 低 | 参数少 (<5) | 指数爆炸 |
| Random Search | 中 | 参数多 | 可能遗漏最优 |
| Bayesian Optimization | 高 | 连续参数 | 计算开销 |
| Hyperband | 高 | 大计算量 | 需早停机制 |
| Population-based | 高 | 分布式训练 | 复杂实现 |
```

### Bayesian Optimization 示例
```python
from skopt import BayesSearchCV
from sklearn.svm import SVC

search = BayesSearchCV(
    estimator=SVC(),
    search_spaces={
        'C': (1e-6, 1e+6, 'log-uniform'),
        'gamma': (1e-6, 1e+1, 'log-uniform'),
        'kernel': ['linear', 'rbf', 'poly'],
    },
    n_iter=50,
    cv=5,
    n_jobs=-1,
    random_state=42
)
search.fit(X_train, y_train)
```

### 参数空间设计原则
```
□ 优先调整最重要的参数
□ 使用对数尺度探索（如 learning rate）
□ 考虑参数间的依赖关系
□ 设置合理的搜索边界
```

---

## 模型评估设计

### 数据划分策略
```
□ 简单划分：70/15/15（训练/验证/测试）
□ K-Fold 交叉验证：k=5 或 10
□ 分层抽样：保持类别比例
□ 时间序列：时间切分，避免未来信息泄露
□ 分组交叉验证：group k-fold（避免同组数据泄漏）

注意：测试集只能使用一次！
```

### 评估指标选择
```
分类：
| 指标 | 公式 | 适用场景 |
|------|------|---------|
| Accuracy | (TP+TN)/Total | 平衡数据集 |
| Precision | TP/(TP+FP) | 假阳性代价高 |
| Recall | TP/(TP+FN) | 假阴性代价高 |
| F1-score | 2*P*R/(P+R) | 平衡 P 和 R |
| AUC-ROC | - | 阈值无关评估 |
| AUC-PR | - | 不平衡数据 |

回归：
| 指标 | 公式 | 适用场景 |
|------|------|---------|
| MSE | Σ(y-ŷ)²/n | 异常值敏感 |
| MAE | Σ|y-ŷ|/n | 鲁棒 |
| RMSE | √MSE | 与目标同单位 |
| R² | 1-SS_res/SS_tot | 解释方差 |
```

### 统计显著性检验
```
□ 配对 t 检验（同一数据集）
□ Wilcoxon 符号秩检验（非正态）
□ McNemar 检验（分类器比较）
□ Friedman 检验 + Nemenyi（多分类器）
□ 交叉验证 t 检验（5×2cv）

注意：多次比较需校正 α
```

---

## 对比实验设计

### 基线选择
```
必须包含：
□ 随机猜测基线
□ 简单模型基线（逻辑回归、k-NN）
□ 当前最佳方法（文献 SOTA）

建议包含：
□ 消融实验（ablation）
□ 退化实验（移除关键组件）
```

### 消融实验设计
```
消融顺序：
1. 完整模型 → 去除组件 A → 性能下降？
2. 完整模型 → 去除组件 B → 性能下降？
3. 完整模型 → 单独使用 A → 性能贡献？

报告模板：
| 配置 | Acc | Δ |
|------|-----|---|
| 完整模型 | 95.2 | - |
| - 组件 A | 93.1 | -2.1 |
| - 组件 B | 94.5 | -0.7 |
| 仅 A | 88.3 | -6.9 |
| 基线 | 82.1 | -13.1 |
```

---

## 数据集设计

### 数据集划分原则
```
□ 随机划分需设置 random_state
□ 验证集和测试集必须同分布
□ 记录划分参数，确保可复现
□ 考虑数据泄漏风险
```

### 数据泄漏检查清单
```
□ 特征包含未来信息
□ 数据预处理在划分前执行
□ 组内数据在不同集合中
□ 时间序列使用未来数据训练
□ 归一化参数来自全部数据
```

### 小样本策略
```
□ 交叉验证（充分利用每个样本）
□ Bootstrap 重采样
□ 留一法（LOOCV）：样本极少时
□ 多次随机划分取平均
```

---

## 实验复现性

### 记录清单
```python
# 必须记录的参数
experiment_config = {
    'random_seed': 42,
    'model_architecture': 'ResNet50',
    'learning_rate': 0.001,
    'batch_size': 32,
    'optimizer': 'Adam',
    'epochs': 100,
    'data_split': {'train': 0.7, 'val': 0.15, 'test': 0.15},
    'preprocessing_version': 'v2.1',
    'feature_engineering_hash': 'abc123',
}
```

### 硬件与环境
```
□ GPU 型号
□ CUDA/cuDNN 版本
□ 框架版本（PyTorch/TensorFlow）
□ Python 版本
□ 关键依赖库版本
□ 容器镜像/环境哈希
```

---

## 在线实验设计 (A/B 测试)

### 实验设计要素
```
□ 流量分配：如何分配用户到各组
□ 随机化单元：用户级 vs 会话级
□ 样本量计算（基于最小可检测效应）
□ 运行时间估算
□ 主要指标 vs 护栏指标
```

### 样本量计算
```python
from statsmodels.stats.power import NormalIndPower

effect = 0.02  # 2% 相对提升
baseline = 0.10  # 基线转化率
alpha = 0.05
power = 0.80

# 计算每组样本量
n = NormalIndPower().solve_power(
    effect_size=effect/baseline,  # Cohen's h
    alpha=alpha,
    power=power,
    alternative='larger'
)
```

### 常见陷阱
```
□ 提前停止（Peeking problem）
□ 新奇效应（Novelty effect）
□ 多重检验膨胀 α
□ 辛普森悖论
□ 季节性影响
```

---

## 预训练与微调设计

### 微调策略
```
□ 冻结层数：底层提取通用特征
□ 学习率调度：预训练层用小 LR
□ 数据量策略：
  - 充足：全量微调
  - 不足：冻结 + 特征提取
□ 正则化：防止过拟合预训练知识
```

### 迁移学习实验
```
□ 对比：随机初始化 vs 预训练
□ 消融：不同预训练任务的影响
□ 层冻结实验：哪些层可迁移
□ 数据集相似度评估
```

---

## 报告规范

### 必须报告内容
```
□ 数据集划分方法及参数
□ 评估指标及选择理由
□ 基线方法
□ 多次运行统计（mean ± std）
□ 计算资源
□ 超参数选择方法
```

### 可复现性最低要求
```
□ 代码公开
□ 随机种子固定
□ 环境/版本记录
□ 预处理流程文档化
□ 原始数据可获取
```
