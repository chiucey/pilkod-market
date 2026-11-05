---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402200df8728b563bbe30a68b55cff72531e8f341cdde0b8ca3fb6ae2261d0640f4860220519b9c18f025f1d22e76d9452b842cac532f2e18b855cd9fa9692c37bf666889
    ReservedCode2: 3045022100b3d399802dbc8b15e966590764e58f0ffe94d08b4c7e936f024080ab7ffcfe5a02207f81d7d7c40d5ab4505355facd46f8eaa46c91cc8706747a3f83d1afa3e8ffdb
description: 基于数据本体论的智能数据分析技能。当用户上传CSV/Excel/Parquet/JSON文件并要求分析、探索数据规律、了解数据质量、生成报告时使用。支持经济型数据（零售、订阅、金融等）和非经济型数据（科学测量、社交网络、文本等）。
name: universal-data-analyst
---

# Universal Data Analyst - 通用数据分析专家

基于数据本体论的智能数据分析技能，每次分析通过大模型进行推理判断，自动识别数据类型、选择分析方法、生成分析脚本并输出报告。

## 核心设计：四层分析框架

```
第一层：数据本体论（Data Ontology）
        ↓  这是关于什么的存在？实体类型？生成机制？
第二层：问题类型学（Problem Typology）
        ↓  描述型 / 诊断型 / 预测型 / 规范型 / 因果型？
第三层：方法论映射（Methodology Mapping）
        ↓  匹配领域公认分析框架
第四层：验证与输出（Validation & Output）
           数据质量报告 + 分析脚本 + HTML/MD报告
```

## 分析流程（7步）

| 步骤 | 内容 | 说明 |
|------|------|------|
| 1 | 数据加载 | 自动识别格式，支持多种文件类型 |
| 2 | 本体识别 | LLM 判断数据实体类型和生成机制 |
| 3 | 质量校验 | 自动检测缺失值、异常值、重复行等问题 |
| 4 | 方案规划 | LLM 结合用户诉求选择分析框架和路径 |
| 5 | 脚本生成 | LLM 生成可执行的 Python 分析脚本 |
| 6 | 执行分析 | 运行脚本，生成图表和数值结果 |
| 7 | 综合报告 | 输出 HTML + Markdown 双格式报告 |

## 支持的数据类型

### 经济型数据
- 零售经济（订单、价格、SKU）→ RFM、ABC-XYZ
- 订阅经济（用户、周期、Churn）→ LTV/Cohort、留存曲线
- 注意力经济（点击、加购、购买）→ 漏斗分析、AARRR
- 金融时序（OHLCV）→ 技术分析、波动率模型

### 非经济型数据
- 科学测量 → 时间序列分解、极值分析
- 社交网络 → 中心性分析、社区发现
- 文本语料 → 主题模型、情感分析

## 执行方式

### 命令行使用
```bash
python layers/orchestrator.py data.csv --intent "分析销售趋势"
```

### Python API 使用
```python
from universal_data_analyst import DataAnalysisOrchestrator

orchestrator = DataAnalysisOrchestrator(output_dir="./output")
results = orchestrator.run_full_analysis(
    file_path="data.csv",
    user_intent="探索性数据分析"
)
```

## 输出文件

每次分析生成以下内容：
```
session_YYYYMMDD_HHMMSS/
├── step2_ontology_prompt.txt     # 本体识别提示词
├── step3_validation_report.json  # 数据质量报告
├── step4_planning_prompt.txt     # 分析方案提示词
├── step5_script_prompt.txt       # 脚本生成提示词
├── analysis_report.html          # 综合 HTML 报告
├── analysis_report.md            # Markdown 报告
└── output/charts/                # 分析图表
```

## 依赖

- pandas >= 1.3
- numpy >= 1.21
- matplotlib >= 3.4
- seaborn >= 0.11
- scipy >= 1.7
- openpyxl >= 3.0
- chardet >= 4.0（编码检测）
- pyarrow >= 6.0（Parquet支持）

## 文件结构

```
universal-data-analyst/
├── SKILL.md                     # 本文件
├── _meta.json                   # 元数据
├── layers/
│   ├── __init__.py
│   ├── data_loader.py           # 多格式数据加载
│   ├── data_validator.py        # 数据质量校验
│   └── orchestrator.py          # 流程编排器
└── references/
    ├── supported_formats.md     # 支持的文件格式
    ├── analysis_frameworks.md   # 分析框架参考
    └── report_style.md          # 报告样式规范
```

## 版本

**v1.1.0** · 支持流程健康监控和编码容错
