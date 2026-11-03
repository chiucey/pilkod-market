---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fbe19f42247738e49d613c06e98f6f04
    PropagateID: fbe19f42247738e49d613c06e98f6f04
    ReservedCode1: 3046022100d6cadd7239462420b93425f9d8c93db9bec5aa62cd9f5e59ca034fff3dd1f505022100b6ad1006e7f6304986c48d91bcd6fb9dea5d9bf06f00f1346b314a9ccbfb0f92
    ReservedCode2: 3046022100a2ad7bd31234cdab8f4919312c41b2ef6e690cde6b4756e39936235e2bd33c18022100fbba717aeb4844ee8046be5fe674fa6771aa22ff83547195373735e525ab12b0
---

# AutoML Research Program

这是一个让 AI 代理自主进行传统机器学习实验的程序。你的任务是优化机器学习模型，通过迭代修改超参数和结构，在固定时间预算内找到最佳配置。

---

## 核心原则

**你的目标**：最大化验证集上的评估指标（accuracy/f1/rmse 等，具体看任务）。

**约束条件**：
- 只能修改 `train.py` 文件
- 固定时间预算（每轮训练时间固定）
- 只能在已有依赖范围内工作（sklearn, xgboost, lightgbm, catboost）
- 不能安装新包或修改 `prepare.py`

**成功标准**：
- 指标比 baseline 显著提升
- 不引入过度复杂性（简单有效的改进优先）
- 内存占用在合理范围内

---

## 实验设置流程

### 阶段 1: 初始化 (一次性)

**用户首次启动时执行：**

1. **读取配置**
   - 查看环境变量或询问用户获取配置
   - 关键参数：数据路径、目标列、任务类型、评估指标、时间预算

2. **数据检查**
   - 确认 `data.csv` 存在且可读取
   - 检查目标列是否存在
   - 确认任务类型（classification/regression/multiclass）
   - 分析数据规模（行数、特征数、内存占用）

3. **创建实验目录结构**
   ```
   ./automl_exp/
   ├── prepare.py      # 从技能模板复制
   ├── train.py        # 从技能模板复制
   ├── data.csv        # 用户数据（或符号链接）
   ├── results.tsv     # 创建空文件，写入表头
   └── .automl_cache/  # 创建缓存目录
   ```

4. **验证环境**
   - 检查必要包是否安装：sklearn, xgboost, lightgbm, catboost, pandas, numpy
   - 如有缺失，提示用户安装

5. **建立 Baseline**
   - 使用默认配置运行一次训练
   - 记录 baseline 指标到 results.tsv
   - 初始 commit: `git init && git add . && git commit -m "baseline"`

6. **确认就绪**
   - 向用户确认设置完成
   - 说明即将开始自主实验循环

---

## 实验循环 (核心)

**一旦开始循环，不要停下来问用户是否继续。** 用户可能去睡觉了，期待你整夜运行实验。保持运行直到被手动停止。

### 每轮实验流程

#### Step 1: 分析历史结果

读取 `results.tsv` 分析：
- 当前最佳指标和对应的 commit
- 最近 10 轮实验的趋势（上升/下降/震荡）
- 哪些改动有效，哪些无效
- 是否还有未探索的方向

**决策策略：**
- 如果连续 5 轮没有提升，尝试更大的改变（换模型、调多个参数）
- 如果最近有提升，在此基础上微调
- 如果已经尝试多种模型，考虑集成或特征工程

#### Step 2: 设计实验

**可选的改进方向（按优先级）：**

1. **超参数调优**（首选，风险低）
   - learning_rate: [0.01, 0.05, 0.1, 0.2]
   - n_estimators/num_leaves/max_depth: 根据模型调整
   - subsample/colsample: [0.6, 0.8, 1.0]
   - reg_alpha/reg_lambda: 正则化参数

2. **模型切换**（如果当前模型进入瓶颈）
   - RandomForest → XGBoost/LightGBM
   - 尝试不同模型的组合

3. **特征工程**（如果数据允许）
   - 添加交互特征
   - 对数/平方根变换
   - 标准化/归一化

4. **训练策略**
   - 交叉验证折数
   - 采样策略（不平衡数据）

**设计原则：**
- 一次实验只改 1-2 个关键参数
- 有明确的假设（"增加树的数量可能减少欠拟合"）
- 避免随机搜索，要有策略性

#### Step 3: 修改代码

**只能修改 `train.py` 中的内容：**

```python
# 你可以修改的部分：
- 模型选择（MODEL_NAME）
- 超参数字典（MODEL_PARAMS）
- 数据预处理逻辑
- 训练循环细节

# 你不能修改：
- 导入语句（除非使用已有库）
- prepare.py 的任何内容
- 评估指标计算逻辑
```

**修改示例：**
```python
# 修改前（baseline）
MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 6,
    'learning_rate': 0.1
}

# 修改后（实验）
MODEL_PARAMS = {
    'n_estimators': 300,      # 增加树的数量
    'max_depth': 8,           # 增加深度
    'learning_rate': 0.05,    # 降低学习率，更精细
    'subsample': 0.8,         # 添加子采样
    'colsample_bytree': 0.8   # 添加特征子采样
}
```

#### Step 4: 运行实验

执行命令：
```bash
cd ./automl_exp
python train.py > run.log 2>&1
```

**重要：**
- 重定向所有输出到 `run.log`，不要污染终端
- 设置超时：如果超过 2×时间预算，强制终止
- 等待进程结束

#### Step 5: 解析结果

从 `run.log` 提取关键信息：
```bash
# 提取指标
grep "^val_" run.log

# 提取内存
grep "^memory_mb:" run.log

# 提取时间
grep "^train_time:" run.log
```

**预期输出格式：**
```
val_accuracy: 0.8542
val_f1_macro: 0.8491
memory_mb: 156.7
train_time: 118.3
status: success
```

#### Step 6: 记录结果

更新 `results.tsv`：
```tsv
commit  metric      memory_mb   status  description
abc1234 0.8542      156.7       keep    increase n_estimators to 300, max_depth to 8
```

**字段说明：**
- `commit`: git commit 的前 7 位
- `metric`: 主指标（由任务决定，越高越好）
- `memory_mb`: 峰值内存（MB）
- `status`: keep/discard/crash
- `description`: 简短描述这次改动

#### Step 7: 决策 (Keep or Discard)

**Keep 的条件（满足其一）：**
- 指标比当前最佳提升 ≥ 0.001（分类）或降低 ≥ 0.001（回归）
- 指标相同但模型更简单（参数更少、更快）
- 指标略降但内存显著减少（≥20%）且业务可接受

**Discard 的条件：**
- 指标下降且无其他收益
- 训练崩溃或超时
- 内存暴增（>2×baseline）

**操作：**
```bash
# Keep: 保留修改
git add train.py
git commit -m "experiment: [你的描述]"

# Discard: 回退到上次成功的 commit
git checkout train.py
# 或者
git reset --hard HEAD~1  # 如果已 commit 但要撤销
```

#### Step 8: 循环

回到 Step 1，继续下一轮实验。

---

## 实验策略指南

### 阶段策略

**早期（0-20 轮）：探索阶段**
- 快速尝试不同模型的 baseline
- 大范围扫描关键超参数
- 建立对数据难度的感知

**中期（20-50 轮）：优化阶段**
- 基于最佳模型深度调优
- 组合多个有效策略
- 尝试特征工程

**后期（50+ 轮）：精炼阶段**
- 微调最优参数组合
- 尝试集成学习
- 验证稳定性

### 模型选择策略

**小数据 (<10K 样本)：**
- 首选：RandomForest, ExtraTrees
- 原因：不易过拟合，无需太多调参

**中等数据 (10K-100K)：**
- 首选：XGBoost, LightGBM
- 原因：速度快，性能好

**大数据 (>100K)：**
- 首选：LightGBM
- 原因：训练速度最快，内存效率高

**类别特征多：**
- 首选：CatBoost, LightGBM
- 原因：原生支持类别特征

### 超参数调优优先级

**XGBoost/LightGBM：**
1. `n_estimators/num_trees` + `learning_rate`（配对调节）
2. `max_depth/num_leaves`（控制复杂度）
3. `subsample` + `colsample_bytree`（正则化）
4. `reg_alpha` + `reg_lambda`（L1/L2 正则化）

**RandomForest：**
1. `n_estimators`（通常越多越好，到边际效应）
2. `max_depth`（控制过拟合）
3. `min_samples_split` + `min_samples_leaf`

### 避免常见陷阱

**陷阱 1: 学习率过高**
- 现象：训练 loss 震荡或发散
- 解决：降低 learning_rate，增加 n_estimators

**陷阱 2: 树的数量过多**
- 现象：训练时间长，内存占用高，边际收益低
- 解决：使用 early stopping

**陷阱 3: 过拟合**
- 现象：train_metric >> val_metric
- 解决：增加正则化，降低模型复杂度，增加数据

**陷阱 4: 类别不平衡**
- 现象：准确率虚高，f1 很低
- 解决：使用 class_weight，采样策略，或换 metric（用 f1）

---

## 输出格式规范

### 实验记录 (results.tsv)

必须使用制表符分隔（不是逗号），避免描述中的逗号干扰：

```tsv
commit  metric  memory_mb       status  description
abc1234 0.8542  156.7   keep    increase n_estimators 100→300, add subsample=0.8
def5678 0.8521  142.3   discard decrease max_depth 6→4, underfitting
ghi9012 0.0000  0.0     crash   learning_rate=1.0 caused divergence
```

### 描述编写规范

**好的描述：**
- "increase n_estimators 100→300, add subsample=0.8"
- "switch from xgb to lgb, default params"
- "add feature interaction: feat1*feat2"

**差的描述：**
- "tune params"（太笼统）
- "try something"（无信息量）
- "fix bug"（应该说明是什么 bug）

---

## 特殊情况处理

### 情况 1: 运行崩溃 (Crash)

**诊断：**
```bash
tail -n 50 run.log
```

**常见原因和修复：**
- **OOM**: 降低 n_estimators, max_depth，或减少 batch_size
- **参数类型错误**: 检查 int/float/string 类型
- **数据类型不匹配**: 确保类别特征正确编码
- **除零错误**: 添加 epsilon（1e-8）避免除零

**决策：**
- 容易修复（拼写错误、类型错误）：修复后继续
- 原理性问题（OOM 无法避免）：标记 crash，跳过这个方向

### 情况 2: 运行超时

**处理：**
```bash
# 设置超时机制
timeout 600 python train.py > run.log 2>&1
```

**如果超时：**
- 可能是模型太大或数据太多
- 减少复杂度或采样数据
- 标记为 discard

### 情况 3: 指标没有提升

**连续 10 轮无提升时：**
1. 回顾 results.tsv，总结已尝试的方向
2. 尝试更大的改变（换模型、改特征工程）
3. 检查是否陷入了局部最优
4. 尝试随机搜索打破僵局

### 情况 4: 用户数据有问题

**常见数据问题：**
- 目标列不存在：询问用户正确的列名
- 数据格式错误：尝试自动修复或报错
- 缺失值过多：使用自动填充策略
- 类别不平衡：使用采样或权重

---

## 与用户交互

### 启动时 (必须交互)

收集必要信息：
```
欢迎使用 AutoML Research！

我需要以下信息来开始实验：
1. 数据文件路径：[默认: ./data.csv]
2. 目标列名：[必须提供]
3. 任务类型：[classification/regression/multiclass]
4. 评估指标：[可选，我会推荐合适的]
5. 每轮时间预算：[默认 120 秒]
6. 最大实验轮数：[默认 100]

确认后开始初始化...
```

### 运行时 (尽量不交互)

**不要询问：**
- "要继续吗？"（用户可能去睡觉了）
- "这个方向好吗？"（你应该自主决策）
- "要停止吗？"（除非用户主动说停止）

**可以报告：**
- 每 10 轮简要总结进度
- 发现重大提升时通报
- 遇到无法解决的问题时求助

### 结束时

当达到最大轮数或用户手动停止时：

```
实验完成！总结如下：
- 总实验轮数：X
- 最佳指标：X (提升了 Y%)
- 最佳配置：[简要描述]
- 结果文件：./automl_exp/results.tsv
- 最佳模型：./automl_exp/best_model.joblib

建议：
[基于实验结果给出下一步建议]
```

---

## 代码规范

### train.py 结构

```python
#!/usr/bin/env python3
"""训练脚本 - 只能修改此文件"""
import os
import sys
import json
import time
import pickle
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score

# prepare.py 提供数据加载和评估
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path)
from prepare import load_data, evaluate_model, get_task_config

# ========== 可修改部分开始 ==========

# 模型选择: 'rf', 'xgb', 'lgb', 'catboost', 'gbdt', 'extra'
MODEL_NAME = 'lgb'

# 模型超参数 - 这是你最常修改的部分
MODEL_PARAMS = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 6,
    'num_leaves': 31,  # LightGBM 专用
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'reg_alpha': 0.0,
    'reg_lambda': 0.0,
    'random_state': 42,
    'n_jobs': -1,
}

# 数据预处理
FEATURE_ENGINEERING = False  # 是否启用特征工程

# ========== 可修改部分结束 ==========

def create_model(model_name, params):
    """创建模型实例"""
    if model_name == 'rf':
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        Model = RandomForestClassifier if task_type == 'classification' else RandomForestRegressor
        return Model(**{k: v for k, v in params.items() if k in ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf', 'random_state', 'n_jobs']})

    elif model_name == 'xgb':
        import xgboost as xgb
        return xgb.XGBClassifier(**params) if task_type == 'classification' else xgb.XGBRegressor(**params)

    elif model_name == 'lgb':
        import lightgbm as lgb
        return lgb.LGBMClassifier(**params) if task_type == 'classification' else lgb.LGBMRegressor(**params)

    # ... 其他模型

def main():
    # 加载配置
    config = get_task_config()
    task_type = config['task_type']
    metric = config['metric']
    time_budget = config['time_budget']

    # 加载数据
    X_train, X_val, y_train, y_val = load_data()

    # 特征工程（可选）
    if FEATURE_ENGINEERING:
        X_train, X_val = engineer_features(X_train, X_val)

    # 创建模型
    model = create_model(MODEL_NAME, MODEL_PARAMS)

    # 训练（带时间控制）
    start_time = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start_time

    # 评估
    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)

    train_metric = evaluate_model(y_train, train_pred, task_type, metric)
    val_metric = evaluate_model(y_val, val_pred, task_type, metric)

    # 输出结果（固定格式，不要改）
    print(f"train_{metric}: {train_metric:.6f}")
    print(f"val_{metric}: {val_metric:.6f}")
    print(f"train_time: {train_time:.1f}")
    print(f"memory_mb: {get_memory_usage():.1f}")
    print(f"status: success")

    # 保存模型
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

if __name__ == '__main__':
    main()
```

### prepare.py 结构（只读）

```python
#!/usr/bin/env python3
"""数据准备和评估 - 不要修改此文件"""
import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, mean_squared_error, mean_absolute_error, r2_score

# 缓存配置
CACHE_DIR = '.automl_cache'
os.makedirs(CACHE_DIR, exist_ok=True)

def get_task_config():
    """从环境变量或配置文件读取任务配置"""
    config_file = os.path.join(CACHE_DIR, 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)

    # 默认配置
    return {
        'data_path': os.environ.get('AUTOML_DATA', './data.csv'),
        'target_col': os.environ.get('AUTOML_TARGET', 'target'),
        'task_type': os.environ.get('AUTOML_TASK', 'classification'),
        'metric': os.environ.get('AUTOML_METRIC', 'accuracy'),
        'time_budget': int(os.environ.get('AUTOML_TIME_BUDGET', '120')),
        'random_seed': int(os.environ.get('AUTOML_SEED', '42')),
    }

def load_data():
    """加载和预处理数据"""
    config = get_task_config()

    # 读取数据
    df = pd.read_csv(config['data_path'])

    # 分离特征和目标
    X = df.drop(columns=[config['target_col']])
    y = df[config['target_col']]

    # 编码目标（分类任务）
    if config['task_type'] in ['classification', 'multiclass']:
        le = LabelEncoder()
        y = le.fit_transform(y)
        # 保存编码器
        import pickle
        with open(os.path.join(CACHE_DIR, 'label_encoder.pkl'), 'wb') as f:
            pickle.dump(le, f)

    # 划分数据集
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=config['random_seed'], stratify=y if config['task_type'] != 'regression' else None
    )

    # 预处理特征
    X_train, X_val = preprocess_features(X_train, X_val)

    return X_train, X_val, y_train, y_val

def preprocess_features(X_train, X_val):
    """特征预处理：编码类别特征，标准化数值特征"""
    # 识别数值和类别特征
    numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()

    # 类别特征编码
    for col in categorical_cols:
        le = LabelEncoder()
        X_train[col] = le.fit_transform(X_train[col].astype(str))
        X_val[col] = le.transform(X_val[col].astype(str))

    # 数值特征标准化
    if numeric_cols:
        scaler = StandardScaler()
        X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
        X_val[numeric_cols] = scaler.transform(X_val[numeric_cols])

    return X_train, X_val

def evaluate_model(y_true, y_pred, task_type, metric):
    """评估模型性能"""
    if task_type == 'regression':
        if metric == 'rmse':
            return np.sqrt(mean_squared_error(y_true, y_pred))
        elif metric == 'mae':
            return mean_absolute_error(y_true, y_pred)
        elif metric == 'r2':
            return r2_score(y_true, y_pred)
    else:
        if metric == 'accuracy':
            return accuracy_score(y_true, y_pred)
        elif metric == 'f1_macro':
            return f1_score(y_true, y_pred, average='macro')
        elif metric == 'f1_weighted':
            return f1_score(y_true, y_pred, average='weighted')
        elif metric == 'roc_auc':
            if len(np.unique(y_true)) == 2:
                from sklearn.metrics import roc_auc_score
                return roc_auc_score(y_true, y_pred)
            else:
                return f1_score(y_true, y_pred, average='macro')  # 多分类用 f1

    return 0.0

def get_memory_usage():
    """获取当前内存占用（MB）"""
    import psutil
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024
```

---

## 最后提醒

**永远不要：**
- 修改 prepare.py
- 安装新依赖包
- 询问用户是否继续实验
- 在没有明确失败原因时放弃

**永远要：**
- 仔细分析历史结果
- 有策略地设计实验
- 清晰记录每个改动
- 从失败中学习

**记住：** 用户可能去睡觉了，期待你整夜运行实验。你是自主的研究者！
