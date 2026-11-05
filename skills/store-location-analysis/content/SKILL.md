---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022045e48843a7d02f265f871656a532323dc30d6597b0b80a5816abbe1f6bbd8ddc022100dd726d094a8fb2488d90bb240a22036e672f5726f18ba91c4d8b434c9b91d251
    ReservedCode2: 3046022100ce6b8cc1e6df61800d3a0695fcb919c1af1d92ef1215dd5e11aff524778d2fc2022100f8f70a9584c8b337fe6430dbcaab238569d6b3031d5f8dbf6306100559fe5a4f
description: Store location analysis assistant. Use when users request store location analysis, market research, business district evaluation, customer matching analysis, sales forecasting, competitive landscape analysis, break-even analysis, or need to generate professional location decision reports.
name: store-location-analysis
---

# 门店选址分析智能助手

## 技能概述

作为专业的"门店选址：客群匹配与销量预估"分析师，整合数据科学能力、商业分析框架与MBA战略思维，为用户提供全面的选址决策支持。

---

## 核心能力

### 1. 数据获取与预处理
- 联网检索目标区域近三年多维度数据
- **自动标注数据来源URL与更新时间**
- 数据清洗：缺失值处理、异常值检测
- 中文地名拼音转译

### 2. 六大分析模块（Python驱动）

| 模块 | 核心指标 | 输出 |
|------|----------|------|
| ① 商圈画像 | TAM/SAM/SOM | 金字塔图表 |
| ② 竞争强度 | HHI、POI密度、最近邻距离 | 竞争热力地图 |
| ③ 客群匹配 | 匹配指数(0-100) | 雷达图 |
| ④ 销量预测 | 12个月销售曲线 | 回归/时序模型 |
| ⑤ 成本效益 | BEP、Payback Period、NPV/IRR | 瀑布图、Tornado图 |
| ⑥ 选址评分 | 综合评分矩阵 | 排序条形图 |

### 3. MBA战略框架
- **PEST分析**：政策、经济、社会、技术宏观影响
- **波特五力**：行业结构评估
- **SWOT总结**：机会、威胁、优势、劣势
- **行动计划**：3步可执行方案

### 4. 专业HTML报告
- 单页响应式设计
- 浮动目录导航
- 可折叠章节
- 中英双语图表标签
- 完整代码附录

---

## 执行流程

### Step 1: 输入收集
```
用户输入 → 城市/商圈 + 店铺类型
默认值自动执行：
- 候选点数量: 3
- 分析时间范围: 近3年
- 置信水平: 90%
```

### Step 2: 数据获取
1. **联网检索以下数据**（标注来源）：
   - 人口密度、年龄结构、家庭收入、消费水平
   - 客流数据、高峰时段热力图
   - 竞品POI（位置、数量、评分、评论）
   - 租金成本、人力成本
   - 交通可达性（地铁距离、公交、停车）

2. **数据缺口处理**：
   - 显式列出假设条件
   - 量化假设影响程度（高/中/低）

### Step 3: Python分析
```python
# 必须导入的库
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

# 字体设置（强制英文标签）
plt.rcParams['font.family'] = 'DejaVu Sans'
```

**分析模块详细规格见 references/analysis_modules.md**

### Step 4: 战略框架分析
- PEST：宏观环境评估（中文输出）
- 波特五力：供应商/买家议价能力、进入壁垒等
- SWOT：矩阵式总结
- 行动方案：优先级排序的3步计划

### Step 5: HTML报告渲染
```
报告结构：
├── 封面（决策摘要：进入/不进入）
├── 浮动目录锚点
├── 六大分析模块（可折叠）
├── MBA战略分析
├── 方法与假设
├── 代码附录
└── 页脚（数据来源、版本信息）
```

---

## 关键公式

### 销量预测模型
```
Sales = Footfall × Conversion × AOV × Seasonal_Factor

简化版：
Sales = N × r × AOV × (1 + β×Promotion)

回归模型：
log(Sales) = β₀ + β₁×log(Footfall) + β₂×Price + β₃×Promo + ε
```

### 盈亏平衡点
```
BEP = Fixed_Costs / (Unit_Price - Unit_Variable_Cost)
Payback = Initial_Investment / (Monthly_Net_Income)
```

### HHI指数
```
HHI = Σ(Market_Share_i)² × 10000
```

### 客群匹配度
```
Match_Score = w₁×Age_Match + w₂×Income_Match + w₃×Preference_Match
```

---

## 输出规范

### 图表标签（英文）
- 所有Python图表：英文标签
- 表格：英文表头 + 中文注释
- 字体：DejaVu Sans / Noto Sans

### 决策输出
```
【决策判定】
┌─────────────────────────────────────┐
│  ✅ 推荐进入 / ❌ 建议不进入          │
│  置信度: XX%                         │
│  核心依据: 1-2句话总结               │
└─────────────────────────────────────┘
```

### 数据来源标注
```
数据来源：[来源名称]
URL: [链接]
更新时间: [日期]
置信度: [高/中/低]
```

---

## 假设透明化模板

```markdown
## 数据缺口与假设

| 缺口项 | 假设条件 | 影响程度 | 缓解措施 |
|--------|----------|----------|----------|
| 竞品评分 | 使用第三方平台均值 | 中 | 增加样本量 |
| 租金成本 | 假设年增长率3% | 低 | 敏感性分析 |
| ... | ... | ... | ... |
```

---

## 技术栈

| 组件 | 版本要求 |
|------|----------|
| Python | >= 3.8 |
| pandas | >= 1.3 |
| numpy | >= 1.21 |
| matplotlib | >= 3.4 |
| seaborn | >= 0.11 |
| scipy | >= 1.7 |
| scikit-learn | >= 1.0 |

---

## 参考文档

- `references/analysis_modules.md` - 六大模块详细规格
- `references/formulas.md` - 完整公式推导
- `references/html_template.md` - HTML报告模板
- `scripts/analysis_runner.py` - 可复现分析脚本
- `scripts/validate_data.py` - 数据验证脚本

---

## 触发检查清单

触发此技能时，确保：
- [ ] 用户提供了城市/商圈信息
- [ ] 用户指定了店铺类型
- [ ] 任务涉及选址决策分析

不触发场景：
- 通用数据分析（无选址意图）
- 仅价格比较
- 交通路线规划

---

*最后更新: 2026-04-25*
