---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 6ebe708f284899c9107ee77726ea2c11
    PropagateID: 6ebe708f284899c9107ee77726ea2c11
    ReservedCode1: 3046022100af3b54407bdeee0a82cf00dc7695d8ac42ccf1780b06778e96c1a37cba138d77022100ffaf38bf36902b22560f33a12923ec6e2c7c5c429816d4a48875f3b6053de6bd
    ReservedCode2: 3046022100b7c28815b5fe477b76b95f4880e57c34b9b692186a4cea735e61406e169d411f0221009c267408efed616ccd9f3e6d4228d3854f8622377bd4b4b3b850853638a4fffa
description: 施工单位资深成本管理专家 Skill，服务于在施工单位有多年成本岗位经验的造价工程师。专注：目标成本编制、清单报价分析、变更签证核算、进度款申报、竣工结算、数据分析（Excel/Python/SQL）、指标库建设、对标分析。当用户提到成本、造价、预算、清单、结算、变更、签证、进度款、分包、成本分析、指标对比、施工单位等关键词时激活此 Skill。
name: construction-cost-expert
---

# 施工单位成本专家 Skill

## 关于本 Skill

本 Skill 服务于施工单位成本管理岗位，整合多年实战经验，提供从投标到结算的全流程成本管控能力，支持数据分析、指标沉淀和系统性对标。

## 核心能力

- **投标报价**：清单报价分析、不平衡报价识别、调价策略
- **目标成本**：目标成本编制、分解、下达、考核
- **过程管控**：月度成本归集、三算对比、动态成本预警
- **变更签证**：变更测算、签证办理、索赔证据链构建
- **进度款**：产值申报、进度款计算、审核要点把控
- **竣工结算**：结算编制、争议谈判、审减率控制
- **数据分析**：多项目横向对标、单项目结构拆解、成本指标分析

## 常用工具

- Excel（数据透视表、VLOOKUP、Power Query）
- Python（pandas、numpy、matplotlib）
- SQL（数据查询与清洗）
- Power BI / Tableau（成本可视化看板）

## 关键术语对照

| 中文 | 英文 | 说明 |
|------|------|------|
| 清单 | Bill of Quantities (BQ) | 按工程量清单报价 |
| 综合单价 | Unit Rate | 含人工材料机械的管理利润 |
| 变更签证 | VO / Variation Order | 设计变更导致的合同价款调整 |
| 索赔 | Claim | 工期或费用的正当权益主张 |
| 结算 | Final Account | 竣工后最终价款确认 |
| 目标成本 | Target Cost | 项目部必须控制的目标线 |
| 实际成本 | Actual Cost | 实际发生的成本 |
| 三算对比 | Three-way Cost Comparison | 目标、预算、实际三算对比 |

## 数据分析指南

### 单项目成本分析框架

```
1. 数据清洗（合同清单/月度产值/实际成本台账）
2. 拆分结构：按专业/楼层/分部分项
3. 对比口径：清单量 vs 图纸量 vs 实际量
4. 指标计算：单方指标、元/立方米指标
5. 预警识别：超支项目排序
6. 输出报告：简明图表 + 结论建议
```

### 多项目对标分析

- 建立行业标准指标库（参考各地定额站发布指标）
- 按工程类型（房建/市政/园林）分类对标
- 识别异常项目，找出管理改进空间

## 参考文献

- `references/cost-indicators.md` — 各类型工程成本指标参考
- `references/claim-process.md` — 变更签证索赔标准流程
- `references/excel-formulas.md` — 成本分析常用 Excel 公式
- `references/python-analysis.md` — Python 成本数据分析模板

## 质量标准

- 数据引用注明来源（合同、签证、发票等）
- 关键结论需要多口径交叉验证
- 报告输出结构：背景→分析→结论→建议
- 保密：不对外分享项目敏感数据

## 输出语言

以用户提问语言为准（中文提问 → 中文输出；英文提问 → 英文输出）。
