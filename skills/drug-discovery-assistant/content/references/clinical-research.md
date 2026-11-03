# Clinical Research Reference

## 研究设计指南

### CONSORT - 随机对照试验

**必需条目清单**:

1. **标题和摘要**
   - 明确为随机试验

2. **背景和目的**
   - 科学背景
   - 具体研究目的

3. **方法**
   - 试验设计
   - 受试者
   - 干预措施
   - 主要/次要结局
   - 样本量计算
   - 随机方法
   - 盲法实施

4. **结果**
   - 受试者流程
   - 招募和随访
   - 基线数据
   - 结局数据
   - 不良事件

5. **讨论**
   - 结果解释
   - 局限性
   - 通用性

### STROBE - 观察性研究

**主要章节**:

1. **标题和摘要**
2. **引言**
   - 背景和理由
3. **方法**
   - 研究设计
   - 参与者
   - 变量定义
   - 数据来源
   - 偏倚控制
   - 统计方法
4. **结果**
   - 参与者描述
   - 描述性数据
   - 结局数据
   - 主要分析
5. **讨论**
   - 关键结果
   - 局限性
   - 解释
   - 通用性

### PRISMA - 系统评价

**流程图要求**:

1. **识别**
   - 数据库检索
   - 注册库检索
   - 其他来源

2. **筛选**
   - 标题和摘要
   - 全文评估

3. **纳入**
   - 最终分析

## 统计分析

### 假设检验

| 检验类型 | 应用场景 | 前提条件 |
|----------|----------|----------|
| t检验 | 两组均值比较 | 正态分布 |
| ANOVA | 多组均值比较 | 正态、方差齐 |
| 卡方检验 | 分类变量关联 | 期望频数≥5 |
| 非参数检验 | 非正态数据 | - |

### 回归分析

```python
import statsmodels.api as sm

# 线性回归
X = sm.add_constant(X_data)
model = sm.OLS(y, X).fit()

# 逻辑回归
model = sm.Logit(y_binary, X).fit()

# 泊松回归 (计数数据)
model = sm.GLM(y_count, X, family=sm.families.Poisson()).fit()
```

## 生存分析

### Kaplan-Meier估计

```python
from lifelines import KaplanMeierFitter

kmf = KaplanMeierFitter()
kmf.fit(durations, event_observed=events)
kmf.plot()
```

### Log-rank检验

```python
from lifelines.statistics import logrank_test

results = logrank_test(
    duration_A, duration_B,
    event_A, event_B
)
```

### Cox比例风险模型

```python
from lifelines import CoxPHFitter

cph = CoxPHFitter()
cph.fit(df, duration_col='time', event_col='event')
cph.print_summary()
```

### 假设检验

| 变量 | HR | 95% CI | p值 |
|------|-----|--------|-----|
| 变量1 | 1.5 | 1.2-1.9 | <0.001 |
| 变量2 | 0.7 | 0.5-0.9 | 0.02 |

## 报告指南

### 报告清单

#### 标题
- 描述性、明确

#### 摘要
- 结构化格式
- 主要发现

#### 引言
- 研究背景
- 研究目的

#### 方法
- 设计明确
- 设置描述
- 参与者选择
- 变量定义
- 统计方法

#### 结果
- 参与者流程
- 描述性统计
- 结局数据
- 辅助分析

#### 讨论
- 主要发现
- 局限性
- 解释
- 通用性

#### 其他
- 伦理审批
- 数据共享
- 利益冲突

## 样本量计算

### 基本公式

```
n = 2 * (Zα/2 + Zβ)² * σ² / δ²
```

其中:
- Zα/2: 置信水平
- Zβ: 统计效能
- σ: 标准差
- δ: 效应量

### 在线工具

- G*Power
- PASS
- R (pwr包)
