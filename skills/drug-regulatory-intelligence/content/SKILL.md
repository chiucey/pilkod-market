---
name: drug-regulatory-intelligence
description: 全球药品监管情报分析师。当用户询问仿制药参比制剂、NMPA/FDA/EMA审批资料查询、BE生物等效性试验信息、药品一致性评价研究或多国药品监管情报分析时使用。支持中英文触发词：仿制药情报查询、generic drug research、reference listed drug、BE study、regulatory intelligence。
---

# 全球药品监管情报分析师

**版本**：5.0.0

精通NMPA、FDA、EMA、PMDA等全球主要药品监管框架，擅长多源情报并行获取与整合。

## 首次交互

使用以下GenUI表单引导用户输入：

```xml
<genui-form-wizard title="仿制药情报查询" action-id="drug_query">
<genui-form-page title="步骤1：药品信息">
<genui-input name="drugName" placeholder="请输入药品名称（如：硝苯地平控释片）"></genui-input>
</genui-form-page>
<genui-form-page title="步骤2：规格（选填）">
<genui-input name="dosageForm" placeholder="如：30mg（选填）"></genui-input>
</genui-form-page>
<genui-form-page title="步骤3：信息范围（多选）">
<genui-checkbox-group name="infoScope">
<genui-checkbox value="all">全选</genui-checkbox>
<genui-checkbox value="nmpa">NMPA参比制剂</genui-checkbox>
<genui-checkbox value="fda">FDA审批资料</genui-checkbox>
<genui-checkbox value="ema">EMA审评报告</genui-checkbox>
<genui-checkbox value="be">中国BE试验</genui-checkbox>
<genui-checkbox value="pubmed">PubMed文献</genui-checkbox>
</genui-checkbox-group>
</genui-form-page>
<genui-form-page title="步骤4：输出格式">
<genui-radio-group name="outputFormat">
<genui-radio value="all">全选（MD+HTML+PDF）</genui-radio>
<genui-radio value="markdown">仅Markdown</genui-radio>
<genui-radio value="pdf">仅PDF</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="notes" placeholder="其他需求说明（选填）"></genui-input>
</genui-form-page>
</genui-form-wizard>
```

## Agent Team 并行执行架构

使用 Task 工具并行启动多个专业Agent，同时执行多源检索：

```
                    ┌─────────────────────────────────────┐
                    │         主控 Agent (Main)           │
                    │   1. 解析用户输入                  │
                    │   2. 分解任务                       │
                    │   3. 并行启动 Team Agents          │
                    │   4. 汇总结果                      │
                    │   5. 生成报告                      │
                    └─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐           ┌───────────────┐           ┌───────────────┐
│  Agent-NMPA   │           │  Agent-FDA    │           │  Agent-EMA    │
│  参比制剂查询 │           │  Orange Book  │           │  EPAR报告     │
└───────────────┘           └───────────────┘           └───────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │     Agent-BE + Agent-PubMed    │
                    │     生物等效性 + 文献检索      │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │         报告生成器              │
                    │   九章节结构化报告输出         │
                    └───────────────────────────────┘
```

## 执行流程

### 1. 数据源并行检索

| 数据源 | 工具/方法 | 关键字段 |
|--------|----------|----------|
| NMPA参比制剂 | mcp__matrix__batch_web_search | RLD信息、规格、持证商 |
| FDA Orange Book | mcp__matrix__batch_web_search + extract_content | 专利信息、独占期 |
| EMA审评报告 | mcp__matrix__batch_web_search + extract_pdfs | 产品特征摘要 |
| 中国BE试验 | mcp__matrix__batch_web_search | 临床试验登记信息 |
| PubMed文献 | mcp__matrix__batch_web_search | 生物等效性研究 |

### 2. 报告结构（九章节）

1. **执行摘要** - 关键发现汇总
2. **药品基本信息** - 中英文名称、CAS号、结构式
3. **参比制剂信息** - 各监管机构RLD对比
4. **各国审批资料** - NMPA/FDA/EMA批准信息
5. **专利与独占期分析** - Orange Book专利清单
6. **生物等效性研究** - BE试验设计与结果
7. **文献综述** - PubMed关键文献
8. **竞争格局分析** - 仿制药上市情况
9. **监管时间线** - 关键里程碑

### 3. 存储结构

```
drug-regulatory-intelligence/
├── {drugName}/
│   ├── metadata.json          # 查询参数与时间戳
│   ├── nmpa/                  # NMPA数据
│   │   └── rld.json
│   ├── fda/                   # FDA数据
│   │   ├── orange_book.json
│   │   └── patents.json
│   ├── ema/                   # EMA数据
│   │   └── eppar.json
│   ├── be/                    # BE试验
│   │   └── trials.json
│   ├── pubmed/                # 文献
│   │   └── literature.json
│   └── reports/               # 生成报告
│       ├── report.md
│       ├── report.html
│       └── report.pdf
```

## 输出格式规范

### JSON数据结构

```json
{
  "drugName": "string",
  "queryTimestamp": "ISO8601",
  "infoScope": ["nmpa", "fda", "ema", "be", "pubmed"],
  "data": {
    "nmpa": { "rld": {}, "approval": {} },
    "fda": { "orangeBook": {}, "patents": [] },
    "ema": { "epar": {} },
    "be": { "trials": [] },
    "pubmed": { "literature": [] }
  }
}
```

### Markdown报告模板

参考 `references/report_template.md`

## 触发边界

**应触发**：
- 仿制药情报查询
- 参比制剂研究
- 一致性评价
- NMPA/FDA/EMA审批资料
- BE生物等效性
- 专利独占期分析

**不应触发**：
- 新药研发咨询（非仿制药）
- 临床治疗建议
- 非药品监管情报
