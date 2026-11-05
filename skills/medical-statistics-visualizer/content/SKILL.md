---
name: medical-statistics-visualizer
description: 医学统计分析与可视化工具。当用户要求进行临床数据分析、生存分析、统计检验、回归分析、ROC曲线绘制时使用。触发词：生存分析、K-M曲线、Cox回归、Log-rank检验、t检验、卡方检验、ROC曲线、森林图、箱线图、热力图、临床统计、医学图表、统计分析、回归分析、诊断效能。
---

# 医学统计分析与可视化 Skill

## 概述

本技能为医学研究人员提供专业的统计分析能力，支持生存分析、常用统计检验、多因素回归分析及高质量可视化图表生成。输出符合SCI期刊发表标准。

## 核心功能

### 1. 生存分析（最高优先级）

| 功能 | 描述 | 输出 |
|------|------|------|
| Kaplan-Meier曲线 | 多组生存曲线对比 | PNG/PDF + 风险表 |
| Log-rank检验 | 组间生存差异显著性检验 | P值 + 统计量 |
| Cox比例风险回归 | 多因素生存分析 | HR + 95%CI + P值 |
| 森林图 | 可视化Cox回归结果 | PNG/PDF |

### 2. 常用统计检验

| 变量类型 | 方法 | 适用场景 |
|----------|------|----------|
| 连续变量 | t检验、Mann-Whitney U检验 | 两组计量数据比较 |
| 分类变量 | 卡方检验、Fisher精确检验 | 两组或多组计数数据 |
| 多因素 | Logistic回归 | 二分类结局 |
| 多因素 | 线性回归 | 连续性结局 |

### 3. 可视化图表

- **森林图**：展示HR、OR及95%CI
- **热力图**：相关性矩阵、聚类分析
- **箱线图+散点叠加**：分布可视化
- **ROC曲线**：诊断效能评估
- **生存曲线**：含风险表

## 使用方法

### 数据输入格式

**支持的格式**：CSV / Excel (.xlsx) / JSON

**必需列（根据分析类型）**：
- 生存分析：`time`（生存时间）、`event`（生存状态：1=死亡/复发，0=删失）、`group`（分组）
- 回归分析：`outcome`（结局变量）、`covariates`（协变量）
- ROC分析：`marker`（标志物数值）、`diagnosis`（诊断结果：0/1）

### 自然语言指令示例

```
1. "比较A组和B组的总生存期，画K-M曲线并标注P值"
2. "做Cox回归，分析年龄、分期、治疗方式对生存的影响"
3. "评估CA19-9对胰腺癌的诊断效能，画ROC曲线"
4. "比较两组患者的CA19-9水平，用箱线图展示"
5. "做多因素Logistic回归，分析影响预后的因素"
```

## 执行流程

### Step 1: 数据解析

```python
# 自动识别数据格式
def parse_input_data(file_path):
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
```

### Step 2: 自然语言意图解析

系统解析用户指令，识别：
- 分析类型（生存分析/统计检验/回归分析/ROC）
- 目标变量
- 分组变量
- 协变量

### Step 3: 执行统计分析

调用对应的Python分析模块：
- `survival_analysis.py`：生存分析
- `statistical_tests.py`：统计检验
- `regression_analysis.py`：回归分析
- `roc_analysis.py`：ROC曲线
- `visualization.py`：图表生成

### Step 4: 结果输出

| 输出类型 | 格式 | 说明 |
|----------|------|------|
| 图表 | PNG (300dpi) / PDF | 符合SCI标准 |
| 统计结果 | 文本 | P值、HR、95%CI等 |
| 表格 | Markdown | 可直接复制到论文 |

## 输出规范

### SCI期刊图表标准

- **分辨率**：PNG ≥ 300 dpi
- **字体**：Arial / Times New Roman
- **字号**：轴标签 10pt，图例 9pt
- **线条粗细**：0.5-1.0 pt
- **配色**：专业配色方案，避免过度鲜艳

### 统计结果格式

```markdown
## 统计结果摘要

### Kaplan-Meier生存分析
| 组别 | 中位生存期 | 95% CI | Log-rank P值 |
|------|------------|--------|--------------|
| A组  | 24.5月     | 20.1-28.9 | 0.003       |
| B组  | 18.2月     | 15.0-21.4 |             |

### Cox回归分析
| 变量 | HR | 95% CI | P值 |
|------|-----|--------|-----|
| 年龄 | 1.02 | 1.01-1.04 | 0.001 |
| 分期 | 2.15 | 1.73-2.67 | <0.001 |
```

## 技术栈

- **Python 3.8+**
- **lifelines**：生存分析（Kaplan-Meier、Cox回归）
- **statsmodels**：回归分析、统计检验
- **scipy**：假设检验、P值计算
- **scikit-learn**：ROC曲线、AUC计算
- **matplotlib / seaborn**：可视化
- **pandas**：数据处理

## 依赖安装

```bash
pip install lifelines statsmodels scipy scikit-learn matplotlib seaborn pandas openpyxl
```

## 常见场景

### 场景1：临床生存分析

**输入**：患者随访表（group, time, event）
**指令**：`"比较手术组和化疗组的总生存期"`
**输出**：K-M曲线 + Log-rank P值

### 场景2：预后因素分析

**输入**：临床病理因素表
**指令**：`"做Cox回归，分析年龄、分期、治疗方式对生存的影响"`
**输出**：森林图 + 回归系数表

### 场景3：诊断效能评估

**输入**：肿瘤标志物 + 诊断结果
**指令**：`"评估CA19-9对胰腺癌的诊断效能"`
**输出**：ROC曲线 + AUC值 + 最佳cut-off值

### 场景4：组间比较

**输入**：两组计量数据
**指令**：`"比较两组的CEA水平"`
**输出**：箱线图 + 统计检验结果

## 注意事项

1. 生存时间单位需统一（建议月或年）
2. 删失数据标记为0，事件发生标记为1
3. 回归分析前检查变量共线性
4. 多重比较需校正显著性水平
