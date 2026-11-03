---
name: excel-data-analyst
description: 专业的 Excel / CSV 数据分析技能。当用户上传 .xlsx、.xls、.csv、.tsv 文件并希望进行数据分析、数据清洗、生成图表、透视统计、发现规律趋势、输出分析报告时使用。触发关键词：分析数据、看看这份数据、帮我整理表格、数据有什么规律、画个图、做个统计、数据清洗、找出异常值、对比各分类、Excel 分析、CSV 处理。
---

# Excel / CSV 数据分析 Skill

## 目标

将用户上传的表格数据转化为**清晰的洞察 + 可交付的成果**，包括：

- 数据概览与质量评估
- 统计摘要（均值、分布、异常值等）
- 分类/分组对比分析
- 趋势分析（时间序列）
- 可视化图表（内嵌展示）
- 结构化分析报告（.xlsx 或 .md 输出）

## 执行流程

### Step 1：读取文件

文件在 `/mnt/user-data/uploads/` 目录。根据扩展名选择读取方式：

```python
import pandas as pd

# Excel
df = pd.read_excel("/mnt/user-data/uploads/example.xlsx")

# CSV（自动检测编码）
df = pd.read_csv("/mnt/user-data/uploads/example.csv", encoding='utf-8-sig')

# 快速探查
print(df.shape)         # 行列数
print(df.dtypes)        # 字段类型
print(df.head())        # 前几行
print(df.isnull().sum()) # 缺失值
```

如果文件名未知，先列出目录：

```bash
ls /mnt/user-data/uploads/
```

### Step 2：数据概览（必做）

向用户汇报以下内容（用自然语言，不要只贴代码输出）：

| 维度 | 要说明的内容 |
|------|------------|
| 规模 | X 行 × Y 列，代表什么数据 |
| 字段 | 列名、类型、含义推断 |
| 质量 | 缺失值、重复行、格式异常 |
| 亮点 | 数据里最值得关注的第一眼发现 |

### Step 3：理解分析需求

如果用户没有明确说要分析什么，根据数据内容**主动推荐 3 个分析方向**，例如：

> 我注意到这份数据包含销售额、地区、月份字段，建议我可以帮你：
> 1. 各地区销售额对比（找出最强/最弱区域）
> 2. 月度销售趋势（看增长还是下滑）
> 3. 找出销售额异常低的订单（潜在问题排查）
> 你想先看哪个？还是全部都分析？

### Step 4：执行分析

根据需求选择合适的分析方法：

#### 4a. 统计摘要

```python
df.describe()                          # 数值字段统计
df['字段'].value_counts()              # 类别分布
df.groupby('分类字段')['数值字段'].agg(['mean','sum','count'])
```

#### 4b. 时间趋势

```python
df['日期'] = pd.to_datetime(df['日期'])
df.set_index('日期').resample('M')['值'].sum()
```

#### 4c. 异常值检测

```python
Q1 = df['字段'].quantile(0.25)
Q3 = df['字段'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['字段'] < Q1 - 1.5*IQR) | (df['字段'] > Q3 + 1.5*IQR)]
```

#### 4d. 相关性分析

```python
df.corr(numeric_only=True)
```

### Step 5：可视化

使用 matplotlib / seaborn 生成图表，保存到 `/home/claude/` 再展示：

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']  # 避免中文乱码

# 如有中文标签，用英文替代或安装字体

fig, ax = plt.subplots(figsize=(10, 5))
# ... 绘图逻辑 ...
plt.tight_layout()
plt.savefig('/home/claude/chart.png', dpi=150, bbox_inches='tight')
plt.close()
```

图表类型选择指南：

- **柱状图** → 分类对比
- **折线图** → 时间趋势
- **散点图** → 相关性
- **箱线图** → 分布与异常值
- **热力图** → 相关矩阵

### Step 6：输出成果

#### 选项 A：分析报告（Markdown）

```markdown
# 数据分析报告

## 数据概览
- 数据集：XXX
- 规模：X 行 × Y 列
- 时间范围：...

## 核心发现
1. ...
2. ...
3. ...

## 详细分析
...

## 建议
...
```

#### 选项 B：输出 Excel 报告

```python
with pd.ExcelWriter('/mnt/user-data/outputs/analysis_report.xlsx', engine='openpyxl') as writer:
    df_summary.to_excel(writer, sheet_name='统计摘要')
    df_grouped.to_excel(writer, sheet_name='分组分析')
    outliers.to_excel(writer, sheet_name='异常值')
```

## 输出质量标准

**好的分析输出应该：**
- 用业务语言解释数字，不只是罗列数字
- 给出"所以呢"——数字背后的含义和建议
- 图表清晰，有标题和轴标签
- 指出数据的局限性（样本小、缺失多等）

**避免：**
- 直接粘贴 `df.describe()` 原始输出给用户
- 分析结论不联系用户的业务场景
- 图表无标题、无单位

## 常见问题处理

| 问题 | 解决方案 |
|------|---------|
| CSV 乱码 | 尝试 `encoding='gbk'` 或 `encoding='gb18030'` |
| 日期格式混乱 | `pd.to_datetime(df['日期'], format='mixed', dayfirst=False)` |
| 数值字段含文字 | `pd.to_numeric(df['字段'], errors='coerce')` |
| 内存不足（大文件）| `pd.read_csv(..., chunksize=10000)` 分块读取 |
| 多 sheet Excel | `pd.read_excel(..., sheet_name=None)` 读取所有 sheet |

## 依赖库

```
pandas >= 1.5
openpyxl >= 3.0
matplotlib >= 3.5
seaborn >= 0.12
```

安装：`pip install pandas openpyxl matplotlib seaborn --break-system-packages`
