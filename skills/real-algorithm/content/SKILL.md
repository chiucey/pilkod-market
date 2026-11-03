---
name: real-algorithm
description: |
  REAL 算法 v2.0：观点-事实分离与可信度评估引擎。当需要分析金融文本（研报、新闻、公告、分析师观点）时使用本技能：
  (1) 将文本区分为"事实"与"观点"两类（含句首引导词特殊处理）；
  (2) 对事实节点进行证据类型判断（人证/物证）和量化可信度评分；
  (3) 对观点节点进行多维度逻辑质量评估；
  (4) 自动建立事实-观点支撑关系链接；
  (5) 输出结构化批量分析报告（JSON格式）及人类可读摘要。
  触发词：REAL、观点-事实分离、可信度评估、研报分析、事实核查、观点置信度、金融信息分析。
---

# REAL 算法 v2.0 — 观点-事实分离与可信度评估

适用：金融分析、研报解读、新闻验证、投资建议审查

> 本技能对应文档：【产品】REAL算法(2.0).docx
> 核心类：`REALAnalyzer`（通用引擎）、`FinancialReportAnalyzer`（金融研报专用）

---

## 架构概览

```
输入文本 + 来源信息
    │
    ▼
 REALAnalyzer.analyze_single()
    │
    ├── classify_info_type()  →  FACT / OPINION / UNKNOWN
    │
    ├── [FACT]
    │   ├── detect_evidence_type()  →  HUMAN / PHYSICAL
    │   ├── evaluate_human_credibility() 或 evaluate_physical_credibility()
    │   └── → Fact 节点（进入 facts_db）
    │
    └── [OPINION]
        ├── classify_opinion_type()  →  PREDICTION / RECOMMENDATION / ...
        ├── evaluate_logic_quality()  →  STRONG / ACCEPTABLE / WEAK / INVALID
        ├── _find_supporting_facts()  →  查询 facts_db 取 Top3
        └── → Opinion 节点（含支撑链接）
```

---

## 核心概念

### 信息分类（InfoType）
| 类型 | 说明 | 触发条件 |
|---|---|---|
| `FACT` | 客观事实 | 数据模式≥3 且观点词≤1，或数据模式分>观点分 |
| `OPINION` | 主观观点 | 观点词≥2，或含"预计/预测" |
| `UNKNOWN` | 待分类 | 其余情况 |

> **句首引导词处理**：`classify_info_type` 会先去除"我们认为/我们预计/本研究"等句首短语，
> 再做判断，减少"我们认为营收增长X%"被误判为观点的常见问题。

### 证据类型（EvidenceType）
| 类型 | 说明 | 典型来源 |
|---|---|---|
| `HUMAN_TESTIMONY` | 人证（带主观表达） | 分析师点评、高管发言 |
| `PHYSICAL_EVIDENCE` | 物证（客观记录/数据） | 年报、公告、监管文件 |
| `UNKNOWN` | 无法判断 | 匿名来源 |

### 可信度等级（CredibilityLevel）
`very_high → high → medium → low → very_low`（五级）

---

## 快速开始

### 方式一：批量分析（推荐）

```python
from scripts.real_engine import batch_analyze

report = batch_analyze([
    {
        "item_id": "001",
        "text": "贵州茅台2024年营收1505亿元，同比增长18.04%。",
        "source": {
            "name": "贵州茅台2024年报",
            "source_type": "上市公司年报",
            "author": "贵州茅台董事会",
            "author_title": "董事会",
            "publish_time": "2024-03-30"
        }
    },
    {
        "item_id": "002",
        "text": "中金公司认为贵州茅台2025年营收有望突破1700亿元。",
        "source": {
            "name": "中金公司研报",
            "source_type": "券商研报",
            "author_title": "首席分析师"
        }
    },
    {
        "item_id": "003",
        "text": "基于以上数据，我们给予买入评级，目标价1800元。",
        "source": {
            "name": "中金公司研报",
            "source_type": "券商研报",
            "author_title": "首席分析师"
        }
    }
], link_threshold=0.22)

print(report.to_json(indent=2))
```

### 方式二：面向对象（状态化，适合多次追加分析）

```python
from scripts.real_engine import FinancialReportAnalyzer, Source
from datetime import datetime

analyzer = FinancialReportAnalyzer(support_threshold=0.22)

# 追加分析（事实库会持久化，支持跨条目链接）
analyzer.analyze_single(
    "公司2024年净利润747亿元，同比增长19.2%。",
    Source(name="年报", source_type="上市公司年报",
           publish_time=datetime(2024, 3, 30))
)
analyzer.analyze_single(
    "基于净利润表现，我们预计2025年业绩将继续向好。",
    Source(name="研报", source_type="券商研报", author_title="首席分析师")
)

# 生成可读摘要
print(analyzer.generate_readable_summary())

# 获取报告
report = analyzer.generate_report()
for link in report.links:
    print(f"事实 {link.fact_id} → 观点 {link.opinion_id} (支持度:{link.support_score:.2f})")
```

### 方式三：研报全文解析

```python
from scripts.real_engine import FinancialReportAnalyzer, Source

analyzer = FinancialReportAnalyzer(support_threshold=0.20)
report_text = open("研报全文.txt").read()
source = Source(name="某券商研报", source_type="券商研报",
                author_title="首席分析师")

results = analyzer.parse_report(report_text, source)
# parse_report 按"。！？\n"分句，逐句分析
```

---

## 评估逻辑详解

### 物证可信度（evaluate_physical_credibility）

来源模糊匹配，优先级如下：

| 来源关键词 | 基准分 |
|---|---|
| 监管机构文件 | 0.95 |
| 年报/半年报/季报/上市公告/财报 | 0.90 |
| 审计报告 | 0.88 |
| 主流财经媒体（证券时报/财新/Wind/东方财富等） | 0.78 |
| 券商研报/研究机构 | 0.75 |
| 行业数据库 | 0.72 |
| 专家分析 | 0.68 |
| 一般新闻/报道 | 0.55 |
| 社交媒体/论坛/股吧 | 0.40 |
| 匿名 | 0.30 |

加成项：发布时间≤7天 +0.05；超过1年 -0.10

### 人证可信度（evaluate_human_credibility）

| 人物角色 | 基准分 |
|---|---|
| 监管官员 | 0.95 |
| 高管（董事长/CEO/总经理） | 0.85 |
| 明星分析师（首席） | 0.80 |
| 行业专家 | 0.70 |
| 资深分析师 | 0.65 |
| 财经记者 | 0.60 |
| 普通分析师/研究员 | 0.50 |
| 散户/KOL | 0.42 |
| 匿名 | 0.25 |

来源类型调整：研报 +0.05，公告 +0.10，新闻 -0.10

### 逻辑质量评估（evaluate_logic_quality）

| 维度 | 触发条件 | 加分 |
|---|---|---|
| 推理链条 | 含≥2个逻辑连接词 | +0.40 |
| 推理链条 | 含1个逻辑连接词 | +0.20 |
| 前提条件 | 含"如果/假设/基于/前提" | +0.10 |
| 数据引用 | 含数字 | +0.10 |
| 信息量 | 文本越长奖励越高（上限0.15） | +0~0.15 |

基础分 0.15；总分 ≥0.70 → strong，≥0.50 → acceptable，≥0.30 → weak，<0.30 → invalid

### 观点综合可信度公式

```
有事实支撑：0.7 × 加权事实可信度 + 0.3 × 逻辑分
无事实支撑：0.4 × 逻辑分 + 0.1（基础分）
```

### 事实-观点支撑链接（semantic_support_score）

- 词汇重叠率 × 0.7 + 数字精确匹配率 × 0.3
- 超过 `support_threshold`（默认0.22）则建立链接，取匹配度最高的前3条事实
- 生产级替换方案：sentence-transformers 余弦相似度 或 NLI 蕴含模型

---

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `support_threshold` | 0.22 | 事实-观点链接阈值 |
| 观点词列表 | 36个 | 见 `OPINION_INDICATORS` |
| 事实词列表 | 29个 | 见 `FACT_INDICATORS` |
| 逻辑连接词 | 16个 | 见 `LOGIC_CONNECTORS` |

---

## 输出字段说明

```json
{
  "summary": {
    "total_facts": 3,
    "total_opinions": 2,
    "high_credibility_facts": 2,
    "high_credibility_facts_ratio": "66.7%",
    "supported_opinions": 1,
    "supported_opinions_ratio": "50.0%",
    "average_fact_credibility": 0.82,
    "average_opinion_credibility": 0.61
  },
  "facts": [{ "fact_id": "FACT_ITEM_0001", "credibility": {"level":"high","score":0.85}, ... }],
  "opinions": [{ "opinion_id": "OP_ITEM_0002", "credibility": {"level":"medium","score":0.62}, ... }],
  "links": [{ "fact_id": "FACT_ITEM_0001", "opinion_id": "OP_ITEM_0002", "support_score": 0.45 }]
}
```

---

## 注意事项

1. **事实/观点区分**基于规则（关键词+数据模式），无法做到100%准确；
   如需更高精度，可对关键条目调用 LLM 进行二次验证
2. **逻辑质量评估**依赖关键词匹配，对复杂长句可能低估
3. **semantic_support_score**为简化版（词汇重叠），高分链接不等于强因果；
   重要分析建议替换为向量化语义匹配
4. **`batch_analyze`**每次调用会创建新分析器实例，事实库不跨次保留；
   如需追加分析，请使用 `FinancialReportAnalyzer` 实例
5. 支持中文金融文本；英文或其他语言文本效果有限
