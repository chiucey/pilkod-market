---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: ad1ca851c6fbe92e2d70bbfe9382dde7
    PropagateID: ad1ca851c6fbe92e2d70bbfe9382dde7
    ReservedCode1: 304402200c1596e9e53950e0d2ff493888ddfa52c1d2310df6c1e4b9aa80c4de6bb3b2f602207423929ac5042a734b747b15a79494059507636933fedbd966a59c08efdc59a7
    ReservedCode2: 304502201429c479557868a93c5dae77d558d86d2a25cdd105bcbcc75ce931b0856f7acf022100a3ef64bd8de57615a50e6e4a0679f9d34f7532e8ccc3f47d69bd8a78381063f6
description: AutoML Research 是一个借鉴 Karpathy autoresearch 理念的传统机器学习自动优化技能。当用户要求自动优化机器学习模型、超参数搜索、模型调优、使用随机森林/XGBoost/LightGBM/CatBoost进行分类/回归任务时使用。
name: automl-research
---

# AutoML Research Skill

## 概述

AutoML Research 是一个借鉴 Karpathy autoresearch 理念的传统机器学习自动优化技能。它让 AI 代理自主进行机器学习实验，通过迭代优化模型参数和结构，在 CPU 环境下自动寻找最佳模型配置。

**核心特性：**
- 支持多种传统 ML 模型：随机森林、XGBoost、LightGBM、CatBoost
- 纯 CPU 运行，无需 GPU 或 PyTorch
- 自动实验循环：修改 → 训练 → 评估 → 决策
- 完整的实验跟踪和结果记录
- 固定时间预算，公平比较不同配置

## 适用场景

- 结构化数据的分类/回归任务
- 超参数自动搜索和优化
- 特征工程策略验证
- 模型结构自动调优
- 集成策略优化

## 快速开始

### 1. 准备工作目录

```bash
# 创建实验目录
mkdir -p ./automl_exp
cd ./automl_exp

# 准备你的数据
cp your_data.csv ./data.csv
```

### 2. 启动自动研究

当用户提供数据路径、目标列、任务类型和时间预算后，AI 将自动进行实验优化。

### 3. 查看结果

实验结果会自动记录在 `results.tsv` 中，包含：
- 每次实验的提交哈希
- 评估指标（准确率/F1/AUC 等）
- 内存占用
- 实验状态（keep/discard/crash）
- 实验描述

## 核心文件结构

```
./automl_exp/
├── prepare.py          # 固定代码：数据加载、预处理、评估指标
├── train.py            # AI 修改：模型定义、训练循环、超参数
├── program.md          # 行为规范：实验流程、规则、输出格式
├── data.csv            # 你的数据文件
├── results.tsv         # 实验记录（自动生成）
└── .automl_cache/      # 缓存目录
```

## 支持的模型

| 模型 | 库 | 适用场景 | 关键超参数 |
|-----|---|---------|-----------|
| RandomForest | sklearn | 通用基准 | n_estimators, max_depth, min_samples_split |
| XGBoost | xgboost | 竞赛首选 | learning_rate, max_depth, n_estimators, subsample |
| LightGBM | lightgbm | 大规模数据 | num_leaves, learning_rate, feature_fraction |
| CatBoost | catboost | 类别特征多 | depth, learning_rate, iterations |
| GradientBoosting | sklearn | 小数据集 | n_estimators, learning_rate, max_depth |
| ExtraTrees | sklearn | 高维数据 | n_estimators, max_depth, min_samples_leaf |

## 评估指标

### 分类任务
- **accuracy**: 准确率（默认）
- **f1_macro**: 宏平均 F1
- **f1_weighted**: 加权 F1
- **roc_auc**: ROC AUC（二分类）

### 回归任务
- **rmse**: 均方根误差（默认）
- **mae**: 平均绝对误差
- **r2**: R² 分数
- **mape**: 平均绝对百分比误差

## 实验流程

### 阶段 1: 设置 (Setup)

1. 读取数据文件，分析特征类型
2. 划分训练/验证/测试集
3. 建立 baseline（默认配置）
4. 初始化 results.tsv

### 阶段 2: 实验循环 (Experiment Loop)

```
FOR each experiment:
    1. 分析当前最佳结果
    2. 提出改进假设（超参数/模型/特征）
    3. 修改 train.py
    4. 运行训练（固定时间预算）
    5. 评估模型性能
    6. 记录结果到 results.tsv
    7. IF 性能提升: git commit（保留）
       ELSE: git reset（回退）
```

### 阶段 3: 输出最佳模型

- 导出最佳模型配置
- 生成特征重要性分析
- 输出模型文件（joblib 格式）

## 配置选项

### 环境变量

```bash
# 实验配置
AUTOML_TIME_BUDGET=120          # 每轮训练时间（秒）
AUTOML_MAX_EXPERIMENTS=100      # 最大实验次数
AUTOML_CV_FOLDS=5               # 交叉验证折数
AUTOML_RANDOM_SEED=42           # 随机种子

# 模型选择（可选）
AUTOML_MODELS="lgb,xgb,rf"      # 启用的模型，逗号分隔
AUTOML_METRIC="f1_macro"        # 优化目标指标

# 输出配置
AUTOML_WORKSPACE="./automl_exp"
AUTOML_VERBOSE=1                # 日志级别
```

### 数据格式要求

**CSV 文件格式：**
```csv
feature1,feature2,feature3,target
1.0,2.0,3.0,0
2.0,3.0,4.0,1
...
```

**支持的数据类型：**
- 数值特征（自动标准化）
- 类别特征（自动编码）
- 缺失值（自动填充）

## 使用示例

### 示例 1: 二分类任务

用户输入：
```
请帮我使用 AutoML Research 优化客户流失预测模型：
- 数据：./customer_churn.csv
- 目标列：churn
- 任务：classification
- 评估指标：roc_auc
- 时间预算：每轮 3 分钟
- 最多 50 轮实验
```

### 示例 2: 回归任务

用户输入：
```
请帮我使用 AutoML Research 优化房价预测模型：
- 数据：./house_prices.csv
- 目标列：price
- 任务：regression
- 评估指标：rmse
- 只使用 LightGBM 和 XGBoost
```

### 示例 3: 多分类任务

用户输入：
```
请帮我使用 AutoML Research 优化多分类模型：
- 数据：./iris_extended.csv
- 目标列：species
- 任务：multiclass
- 评估指标：f1_macro
```

## 结果解读

### results.tsv 格式

```tsv
commit  metric  memory_mb       status  description
abc1234 0.8542  125.3   keep    baseline random forest
def5678 0.8712  156.7   keep    increase n_estimators to 500, tune max_depth
ghi9012 0.8698  203.4   discard add xgboost with default params, overfitting
jkl3456 0.0000  0.0     crash   learning_rate too high, numerical overflow
```

### 字段说明

| 字段 | 说明 |
|-----|------|
| commit | Git commit 哈希（前7位） |
| metric | 主要评估指标值（越高越好） |
| memory_mb | 峰值内存占用（MB） |
| status | keep=保留, discard=废弃, crash=崩溃 |
| description | 实验描述（人工/AI填写） |

## 最佳实践

### 1. 实验设计
- 每次实验只改 1-2 个超参数，便于定位效果
- 从 baseline 开始，逐步优化
- 记录失败原因，避免重复踩坑

### 2. 参数搜索策略
- 粗调 → 细调：先大范围搜索，再精确调优
- 网格搜索关键参数：learning_rate, max_depth/num_leaves
- 固定其他参数，逐一验证

### 3. 防止过拟合
- 监控 train_metric vs val_metric 差距
- 使用 early stopping
- 控制模型复杂度（正则化参数）

### 4. 实验管理
- 定期查看 results.tsv 总结经验
- 对 crash 的实验进行根因分析
- 保留简单有效的改进，拒绝复杂低效的变化

## 故障排除

### 问题 1: 训练时间过长

**解决方案：**
- 减少 AUTOML_TIME_BUDGET
- 降低数据采样率（大数据集）
- 减少交叉验证折数

### 问题 2: 内存不足

**解决方案：**
- 减少 n_estimators/num_leaves
- 使用更简单的模型（如 RandomForest 替代 XGBoost）
- 启用特征选择

### 问题 3: 所有实验都 crash

**可能原因：**
- 数据格式错误（检查目标列是否存在）
- 超参数范围设置不合理
- 类别不平衡导致某些指标计算失败

**调试方法：**
```python
# 手动运行 prepare.py 检查
python prepare.py --check-data

# 查看详细日志
tail -n 50 run.log
```

## 参考资料

- [Karpathy autoresearch](https://github.com/karpathy/autoresearch)
- [LightGBM 文档](https://lightgbm.readthedocs.io/)
- [XGBoost 文档](https://xgboost.readthedocs.io/)
- [scikit-learn 文档](https://scikit-learn.org/)
