# 医学统计分析 Visualizer - 使用指南

## 目录

1. [快速开始](#快速开始)
2. [数据准备](#数据准备)
3. [分析方法](#分析方法)
4. [输出说明](#输出说明)
5. [常见问题](#常见问题)

---

## 快速开始

### 安装依赖

```bash
pip install lifelines statsmodels scipy scikit-learn matplotlib seaborn pandas openpyxl
```

### 基本使用

```python
from scripts.main_analyzer import MedicalStatisticsAnalyzer

# 初始化分析器
analyzer = MedicalStatisticsAnalyzer(output_dir='./output')

# 加载数据
analyzer.load_data('survival_data.csv')

# 执行分析
results = analyzer.analyze('比较A组和B组的总生存期，画K-M曲线')

# 生成报告
report = analyzer.generate_report()
```

---

## 数据准备

### 支持的数据格式

| 格式 | 文件扩展名 | 说明 |
|------|-----------|------|
| CSV | .csv | 逗号分隔值文件 |
| Excel | .xlsx, .xls | Excel电子表格 |
| JSON | .json | JSON格式数据 |

### 数据格式要求

#### 生存分析数据

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| time | 数值 | 生存时间 | 24.5, 12.3 |
| event | 0/1 | 生存状态 | 1=死亡/复发, 0=删失 |
| group | 字符串 | 分组名称 | "A组", "B组" |

#### ROC分析数据

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| marker | 数值 | 生物标志物值 | 35.6, 120.5 |
| diagnosis | 0/1 | 诊断结果 | 1=阳性, 0=阴性 |

### 示例数据 (CSV格式)

```csv
patient_id,group,time,event,age,stage,CEA,CA19_9
1,A组,24.5,1,55,III,5.2,35.6
2,A组,36.0,0,62,II,3.1,28.4
3,B组,18.2,1,58,III,8.9,156.2
4,B组,42.0,0,51,I,2.8,22.1
...
```

---

## 分析方法

### 1. 生存分析

#### Kaplan-Meier生存曲线

```python
# 方法1: 自然语言
results = analyzer.analyze('比较A组和B组的总生存期')

# 方法2: 参数指定
results = analyzer.analyze(
    command='',
    time_col='time',
    event_col='event',
    group_col='group',
    groups=['A组', 'B组']
)
```

**输出内容:**
- K-M生存曲线图 (PNG, 300dpi)
- Log-rank检验P值
- 各组中位生存期

#### Cox比例风险回归

```python
results = analyzer.analyze(
    'Cox回归',
    time_col='time',
    event_col='event',
    covariates=['age', 'stage', 'treatment']
)
```

**输出内容:**
- 森林图
- HR值及95%CI
- 各变量P值
- C-index

### 2. 统计检验

#### 连续变量比较

```python
# t检验或Mann-Whitney U检验 (自动根据正态性选择)
results = analyzer.analyze(
    '比较两组的CEA水平',
    group_col='group',
    marker_col='CEA',
    groups=['A组', 'B组']
)
```

**输出内容:**
- 箱线图+散点图
- 描述性统计 (均值、标准差、中位数、四分位距)
- 正态性检验结果
- 假设检验P值

#### 分类变量比较

```python
results = analyzer.stats.compare_categorical(
    data, value_col='outcome', group_col='treatment'
)
```

### 3. 回归分析

#### Logistic回归

```python
from scripts.regression_analysis import RegressionAnalyzer

reg = RegressionAnalyzer()
results = reg.logistic_regression(
    data,
    outcome_col='mortality',  # 二分类结局
    covariates=['age', 'stage', 'ki67'],  # 协变量
    output_path='./output/logistic_forest.png'
)
```

#### 线性回归

```python
results = reg.linear_regression(
    data,
    outcome_col='length_of_stay',  # 连续结局
    covariates=['age', 'bmi', 'albumin']
)
```

### 4. ROC曲线分析

```python
results = analyzer.analyze(
    '评估CA19-9的诊断效能',
    marker_col='CA19_9',
    outcome_col='diagnosis'
)
```

**输出内容:**
- ROC曲线图
- AUC值及95%CI
- 最佳截断值
- 敏感度、特异度
- 阳性预测值、阴性预测值

### 5. 相关性分析

```python
results = analyzer.analyze(
    '分析标志物相关性',
    covariates=['CEA', 'CA19_9', 'AFP', 'CA125']
)
```

---

## 输出说明

### 文件结构

```
output/
├── km_analysis_km.png        # Kaplan-Meier曲线
├── km_analysis_forest.png    # Cox回归森林图
├── roc_analysis_curve.png    # ROC曲线
├── comparison_boxplot.png    # 箱线图
├── correlation_heatmap.png   # 相关性热力图
└── analysis_report.md        # 分析报告
```

### 报告格式 (Markdown)

```markdown
# 医学统计分析报告

## 数据概况
- 样本量: 200
- 变量数: 8

## 生存分析结果

### Kaplan-Meier分析
| 组别 | 中位生存期 | 95% CI | Log-rank P值 |
|------|------------|--------|--------------|
| A组  | 24.5月     | 20.1-28.9 | 0.003       |
| B组  | 18.2月     | 15.0-21.4 |             |

### Cox回归结果
| 变量 | HR | 95% CI | P值 |
|------|-----|--------|-----|
| 年龄 | 1.02 | 1.01-1.04 | 0.001 |
```

---

## 常见问题

### Q1: 如何处理缺失值?

```python
# 方法1: 删除含缺失值的行
data_clean = data.dropna()

# 方法2: 填充缺失值
data_filled = data.fillna(data.mean())
```

### Q2: 如何处理非标准列名?

```python
# 重命名列
data = data.rename(columns={
    '生存时间': 'time',
    '生存状态': 'event',
    '分组': 'group'
})
```

### Q3: 事件列不是0/1编码怎么办?

```python
# 转换编码
data['event'] = data['status'].map({
    'Dead': 1,
    'Alive': 0,
    'Censored': 0
})
```

### Q4: 如何调整图表样式?

```python
from scripts.visualization import set_sci_style

# 设置SCI期刊标准样式
set_sci_style()

# 或自定义
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'Arial'
```

---

## 联系方式

如有问题或建议，请联系开发团队。
