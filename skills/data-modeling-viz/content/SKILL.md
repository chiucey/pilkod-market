---
name: data-modeling-viz
description: 对数据表进行数学建模分析并生成可视化图表。当用户提供CSV/Excel数据文件并要求分析数据关系、建立数学模型、绘制图表或解释数据规律时，必须使用此技能。适用于数据分析、统计建模、趋势预测、关联分析等场景。触发关键词：分析数据、建模、画图、预测趋势、找规律、可视化、相关性分析、CSV分析、Excel分析、数据挖掘、散点图、回归分析。
license: MIT
compatibility: Requires Python 3.8+ with pandas, numpy, matplotlib, seaborn, scikit-learn
metadata:
  agent_created: "true"
  author: WorkBuddy-User
  version: "1.0"
---

# 数据建模与可视化

此技能引导 AI 以标准数据科学工作流完成数据分析任务：从数据理解 → EDA → 模型选择（带决策判断）→ 建模验证 → 可视化解释。

---

## TL;DR（快速执行路径）

```
读数据 → 展示概览 → [检查点1：确认分析目标] → EDA → [检查点2：确认模型方向] → 建模 → 可视化 → 结论
```

---

## 适用场景

当用户提出以下请求时，必须触发此技能：
- 分析这个CSV/Excel文件
- 帮我建立一个数学模型
- 画图展示这两个变量的关系
- 预测未来的趋势
- 找出影响X的关键因素
- 这个数据有什么规律
- 做个相关性分析
- 用 matplotlib/seaborn 做可视化
- 数据挖掘、数据分析报告

---

## 工作流程

### 步骤0：读取文件（边界处理优先）

先处理常见文件问题再往下走：

```python
try:
    df = pd.read_csv(file_path, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(file_path, encoding='gbk')

# Excel 文件
df = pd.read_excel(file_path, sheet_name=0)

print(f"数据形状: {df.shape}")
print(f"列名: {df.columns.tolist()}")
print(f"数据类型:\n{df.dtypes}")
print(f"缺失值:\n{df.isnull().sum()}")
print(f"数值型列统计:\n{df.describe()}")
```

**数据质量边界处理：**

| 问题 | 处理方式 |
|------|---------|
| 行数 < 30 | 警告用户：样本量过少，仅做描述性分析，不建模 |
| 行数 < 10 | 仅描述统计+可视化，明确告知无法建模 |
| 缺失值 > 30% | 告知用户并询问处理策略（删除/填充/保留） |
| 全部是分类型变量 | 跳过回归，重点做频率分析、交叉表、卡方检验 |
| 列名有空格/特殊字符 | 执行 `df.columns = df.columns.str.strip().str.replace(' ', '_')` |

---

### 检查点1：确认分析目标（EDA前必须暂停）

展示数据概览后，**必须询问用户**：

> 我已看到你的数据有 [N 行 × M 列]，列包括：[列名列表]。
> 请告诉我：
> 1. 你最关心的是哪个变量？（目标变量）
> 2. 你的分析目的是？（预测 / 找规律 / 对比差异 / 其他）
>
> 如果不确定，我可以帮你探索所有变量关系后再决定。

**只有用户回答后，才进入步骤1（EDA）。**

---

### 步骤1：探索性数据分析（EDA）

关键原则：先看图，再建模

1. **单变量分析**：
   - 数值型：直方图/KDE，观察分布（正态/偏态/多峰）
   - 分类型：柱状图，统计各类别占比

2. **双变量关系分析**（按用户目标变量优先）：
   - 数值 vs 数值：散点图 + Pearson 相关系数（|r| > 0.7 为强相关）
   - 数值 vs 分类：箱线图（对比各组均值和分布）
   - 分类 vs 分类：交叉表 + 卡方检验

3. **多变量关系**：
   - 计算相关性矩阵（仅数值型列）
   - 绘制热力图（识别强相关/共线性）

---

### 检查点2：确认模型方向（建模前必须暂停）

EDA 完成后，**展示关键发现并询问用户**：

> 通过 EDA，我发现：
> - [最强相关的变量对]
> - [数据分布特征]
> - [潜在问题，如共线性]
>
> 建议使用 [推荐模型]，因为 [理由]。
> 你是否同意这个方向？

**等用户确认后，才进入步骤2（建模）。**

---

### 步骤2：选择合适的数学模型

**AI 判断数据特征的方法：**

```
① 看目标变量类型：
   - 连续数值（销售额、温度）→ 回归问题
   - 离散类别（是/否、A/B/C）→ 分类问题
   - 时间戳有序序列 → 时序预测问题

② 看自变量与目标的关系（通过散点图判断）：
   - 近似直线 → 线性关系
   - 弯曲/抛物线 → 非线性关系
   - 无规律、变量多 → 用随机森林探索重要性

③ 检查样本量：
   - < 100 行：线性/多项式回归
   - 100-1000 行：随机森林、梯度提升
   - > 1000 行：任何模型均可
```

**模型选择表：**

| 问题类型 | 数据特征 | 推荐模型 | 可视化方式 |
|---------|---------|---------|-----------|
| 回归 | 两变量线性（r绝对值>0.6） | 线性回归 | 散点图+回归线 |
| 回归 | 两变量非线性 | 多项式回归（先2阶再3阶） | 曲线拟合图 |
| 回归 | 多变量、关系未知 | 随机森林回归 | 特征重要性图 |
| 分类 | 二分类、线性可分 | 逻辑回归 | 决策边界图 |
| 分类 | 多分类或非线性 | 决策树/随机森林 | 混淆矩阵 |
| 时序 | 有明确时间列 | 趋势分解+线性拟合 | 时序图+预测区间 |
| 探索 | 变量间复杂关系 | 相关性分析+PCA | 热力图、主成分图 |

---

### 步骤3：建立模型并验证

```python
# 根据样本量决定是否划分
if len(df) >= 50:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
else:
    print("样本量较少，使用全部数据训练，结果仅供参考")
    model.fit(X, y)
    y_pred = model.predict(X)
```

**模型评估（必须输出）：**
- 回归：R²、RMSE、MAE
- 分类：准确率、混淆矩阵、F1分数
- R² < 0.3 时，主动告知"模型拟合较差"，建议检查遗漏变量/尝试非线性模型

---

### 步骤4：可视化与解释

**图表设计原则：**
- 使用 `fig, ax = plt.subplots()` 面向对象 API
- 最小 figsize=(10, 6)，多图面板 figsize=(14, 10)
- 每图必须有 xlabel, ylabel, title（标题说明核心发现）
- 色盲友好：推荐 "Set2" 或 "colorblind" 调色板，避免红绿配对

**代码占位符替换规则（执行时必须替换）：**

| 占位符 | 替换为 |
|-------|-------|
| '变量1' | 实际列名，如 '广告费' |
| '数值列' | 实际数值型列名 |
| '分类列' | 实际分类型列名 |
| '时间列' | 实际时间/日期列名 |

---

## 常用代码模板

### 基础设置
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams['figure.dpi'] = 100
```

### 散点图 + 回归线（含相关系数）
```python
fig, ax = plt.subplots(figsize=(10, 6))
sns.regplot(x='变量1', y='变量2', data=df,
            scatter_kws={'alpha': 0.5, 's': 50},
            line_kws={'color': 'red', 'linewidth': 2})
r, p = stats.pearsonr(df['变量1'].dropna(), df['变量2'].dropna())
ax.set_xlabel('变量1含义', fontsize=12)
ax.set_ylabel('变量2含义', fontsize=12)
ax.set_title(f'变量1 vs 变量2（r={r:.2f}, p={p:.3f}）', fontsize=14)
plt.tight_layout()
plt.savefig('scatter_regression.png', dpi=300, bbox_inches='tight')
```

### 相关性热力图
```python
corr = df.select_dtypes(include=[np.number]).corr()
fig, ax = plt.subplots(figsize=(max(8, len(corr)*1.2), max(6, len(corr))))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
            cmap='RdBu_r', center=0, square=True,
            linewidths=0.5, cbar_kws={'shrink': 0.8})
ax.set_title('特征相关性矩阵（下三角）', fontsize=14)
plt.tight_layout()
```

### 多图组合面板（EDA总览）
```python
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes[0, 0].hist(df['数值列'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
axes[0, 0].set_title('数值列分布')
axes[0, 0].set_xlabel('数值列名称')
axes[0, 0].set_ylabel('频次')
sns.boxplot(x='分类列', y='数值列', data=df, ax=axes[0, 1], palette='Set2')
axes[0, 1].set_title('按类别分组的数值分布')
axes[1, 0].plot(df['时间列'], df['数值列'], marker='o', markersize=3, linewidth=1)
axes[1, 0].set_title('时间趋势')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 1].scatter(df['变量1'], df['变量2'], alpha=0.5, s=30)
axes[1, 1].set_title('变量1 vs 变量2')
plt.tight_layout()
```

### 模型结果展示
```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].scatter(y_test, y_pred, alpha=0.6, s=40)
axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', linewidth=2)
rmse = mean_squared_error(y_test, y_pred, squared=False)
axes[0].set_xlabel('实际值')
axes[0].set_ylabel('预测值')
axes[0].set_title(f'预测效果 (R²={r2:.3f}, RMSE={rmse:.2f})')
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': abs(model.coef_)
}).sort_values('importance', ascending=True)
axes[1].barh(feature_importance['feature'], feature_importance['importance'], color='steelblue')
axes[1].set_xlabel('|系数值|（重要性）')
axes[1].set_title('特征重要性排序')
plt.tight_layout()
```

### 非线性拟合（多项式回归）
```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

for degree in [2, 3]:
    model_poly = make_pipeline(PolynomialFeatures(degree), LinearRegression())
    model_poly.fit(X_train, y_train)
    score = model_poly.score(X_test, y_test)
    print(f"{degree}阶多项式 R²={score:.3f}")

x_range = np.linspace(X.min(), X.max(), 300).reshape(-1, 1)
y_range = model_poly.predict(x_range)
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(X, y, alpha=0.5, label='原始数据')
ax.plot(x_range, y_range, 'r-', linewidth=2, label=f'{degree}阶多项式拟合')
ax.legend()
ax.set_title(f'非线性拟合 (R²={score:.3f})')
plt.tight_layout()
```

---

## 常见错误与避免方法

| 常见错误 | 正确做法 |
|---------|---------|
| 默认图表尺寸太小 | 始终设置 `figsize=(10, 6)` 或更大 |
| 颜色过于杂乱 | 使用 "Set2" 或 "colorblind" 调色板 |
| 缺少坐标轴标签 | 每图必须有 xlabel, ylabel, title |
| 不处理缺失值 | 先检查 `df.isnull().sum()`，再处理 |
| 不做训练测试集划分 | 样本 >= 50 时必须划分，报告测试集性能 |
| 不解释图表 | 必须用一句话说明图表核心发现 |
| 相关性等于因果 | 明确说明"相关不等于因果" |
| 占位符未替换 | 代码中的'变量1'、'数值列'必须替换为实际列名 |
| 忽略样本量限制 | 样本 < 30 时降级为描述性分析 |

---

## 输出要求

完成分析后，必须提供：

1. **数据概览**：行列数、缺失值情况、各列数据类型
2. **关键发现**：用通俗语言说明最重要的数据规律
3. **模型结果**：模型类型、关键参数、性能指标及其含义
4. **可视化图表**：至少关键关系图 + 模型结果图
5. **业务解释**：将统计结论翻译成业务建议（"也就是说……"）
6. **局限性说明**：相关性不等于因果性、样本量限制等

---

## 何时寻求外部技能

遇到以下情况，用 find-skills 搜索扩展技能：
- 高级统计检验（ANOVA、ARIMA 等）
- 地理信息图、网络关系图等特殊可视化
- XGBoost、神经网络等高级模型
- 交互式图表（Plotly、Bokeh）
- 大规模数据处理（Dask、Spark）

---

## 应用示例

以下两个完整示例展示了此技能在真实场景中的完整运行路径。

---

### 示例一：广告费 → 销售额 预测（简单线性回归）

**场景描述：**  
用户上传了一份包含 50 条记录的 CSV 文件，列名为 `广告投入(万元)` 和 `月销售额(万元)`，想知道"多花一万广告费，销售额能涨多少"。

**数据预览（前5行）：**

| 广告投入(万元) | 月销售额(万元) |
|------------|------------|
| 5.2 | 23.1 |
| 8.7 | 31.6 |
| 3.1 | 15.8 |
| 12.4 | 48.3 |
| 6.8 | 27.4 |

**AI 执行路径：**

1. 步骤0：成功读取 CSV（utf-8），50行×2列，无缺失值
2. 检查点1 话术：
   > "你的数据有 50行 × 2列，分别是`广告投入(万元)`和`月销售额(万元)`。你最关心预测销售额（目标变量），分析目的是建立预测关系，对吗？"
3. EDA：散点图显示强线性正相关，Pearson r = 0.97
4. 检查点2 话术：
   > "EDA发现两变量呈强线性相关（r=0.97），建议用线性回归建模。是否继续？"
5. 建模：R² = 0.94，RMSE = 2.1万
6. 结论：**每增加 1 万广告投入，预计带来约 3.6 万元销售额增长**

**生成代码片段：**
```python
# 实际替换了占位符：'变量1' → '广告投入(万元)'，'变量2' → '月销售额(万元)'
fig, ax = plt.subplots(figsize=(10, 6))
sns.regplot(x='广告投入(万元)', y='月销售额(万元)', data=df,
            scatter_kws={'alpha': 0.6, 's': 60},
            line_kws={'color': 'red', 'linewidth': 2})
r, p = stats.pearsonr(df['广告投入(万元)'], df['月销售额(万元)'])
ax.set_title(f'广告投入 vs 月销售额（r={r:.2f}, p<0.001）', fontsize=14)
ax.set_xlabel('广告投入（万元）')
ax.set_ylabel('月销售额（万元）')
plt.tight_layout()
plt.savefig('ad_sales_regression.png', dpi=300, bbox_inches='tight')
```

**业务解释输出示例：**
> 也就是说：广告费和销售额之间存在非常强的线性关系（r=0.97）。根据模型，每多投入1万元广告费，预期月销售额增加约3.6万元。不过请注意，相关性不等于因果性——可能同时存在其他影响因素（如季节、促销活动等）。

---

### 示例二：学生成绩多变量影响因素分析（随机森林回归）

**场景描述：**  
用户上传了 300 名学生的数据，包含 `学习时长(h/天)`、`睡眠时长(h/天)`、`课外活动次数`、`家长教育水平`（低/中/高）、`期末成绩`，希望找出"哪些因素对成绩影响最大"。

**AI 执行路径：**

1. 步骤0：读取 CSV，300行×5列，`家长教育水平` 为分类型，其他为数值型，缺失值3行（<1%）→ 直接删除
2. 检查点1 话术：
   > "数据中既有数值型变量（学习时长、睡眠时长等）也有分类型变量（家长教育水平）。目标变量是`期末成绩`，分析目的是找出关键影响因素，对吗？"
3. EDA 发现：
   - 学习时长与成绩相关最强（r=0.76）
   - 家长教育水平高的学生平均分比低水平高约18分（箱线图）
   - 睡眠与成绩呈弱正相关（r=0.31）
4. 检查点2：多变量+分类型变量混合 → 推荐随机森林回归（不需要手动编码，能处理非线性）
5. 建模：使用 `LabelEncoder` 处理分类变量，随机森林 R²=0.82
6. 特征重要性排名：学习时长(0.51) > 家长教育水平(0.23) > 睡眠时长(0.14) > 课外活动(0.12)

**关键代码：**
```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# 处理分类变量
le = LabelEncoder()
df['家长教育水平_encoded'] = le.fit_transform(df['家长教育水平'])

X = df[['学习时长(h/天)', '睡眠时长(h/天)', '课外活动次数', '家长教育水平_encoded']]
y = df['期末成绩']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)  # 0.82

# 特征重要性图
importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=True)

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(importance_df['feature'], importance_df['importance'],
        color=['#4C72B0', '#55A868', '#C44E52', '#8172B2'])
ax.set_xlabel('特征重要性')
ax.set_title(f'影响期末成绩的关键因素（随机森林 R²={r2:.2f}）')
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
```

**业务解释输出示例：**
> 也就是说：影响期末成绩最关键的因素是**学习时长**（重要性51%），其次是家长教育水平（23%）。增加1小时/天的学习时间，预计可带来约8-12分的成绩提升。睡眠和课外活动也有正向影响，但相对较弱。建议优先保证充足的学习时间，同时适当引导家长参与学生教育。

---

### 🧭 示例选择指南

| 你的情况 | 参考示例 |
|---------|---------|
| 两个数值变量，想看关系 | 示例一（线性回归） |
| 多个变量，分类+数值混合 | 示例二（随机森林） |
| 散点图呈明显弯曲 | 使用"非线性拟合模板" |
| 只想看各变量分布和相关性 | 直接做 EDA，不必建模 |
