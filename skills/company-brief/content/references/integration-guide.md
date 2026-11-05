# 上下游交接指南

`company-brief` 是一份"基线画像",它的责任是又快、又有引用、又紧凑。它不应该重复任何下游工作流要做的事。

## 一、推荐执行顺序

1. `financial-source-of-truth`:确立来源路由与证据层级。
2. `financials-normalizer` 或 `excel-data-cleaner`:在底层数据杂乱时先清理。
3. `company-brief`:生成基线画像。
4. 下游角色技能:做分析、建模、备忘录、deck 或会议准备。
5. `deck-report-qc` 或 `model-audit-tieout`:在相关时做最终 QA。

## 二、向多市场股票研究的交接

- `earnings-preview`:用画像字段框定公司、分部 / KPI 上下文与当前争论。
- `earnings-deep-dive`:当业绩前公司背景不全时,用画像补齐。
- `equity-model-update`:仅作上下文使用;模型更新仍需标准化财务输入。
- `long-short-pitch`:作为论点、变量感知、估值、风险 / 收益之前的事实底座。
- `comps-valuation`、`dcf-model-builder`:在关键财务指标已有来源并标准化后再交接。
- 独立信用分析流程:用于信用尽调、不良、到期墙、流动性、资本结构或回收问题。
- `event-driven-analyzer`:用于并购、分拆、激进股东、诉讼、监管、重组等特殊情境的基线背景。
- `economic-impact-report`:仅当需要宏观、政策、商品、汇率、利率或跨资产上下文时;不要把公司画像变成宏观分析。
- `thesis-tracker` / `portfolio-risk-management`:当画像将作为持续监控、仓位规模或对冲工作的输入时使用。
- `memo-builder` / `meeting-prep` / `deck-report-qc`:当画像将进入 memo、电话准备或要发的 deck / 报告时使用。

## 三、向共享核心的交接

- `financial-source-of-truth`:负责落地来源层级、引用、陈旧检查、事实 / 假设标签与冲突处理。
- `financials-normalizer` / `excel-data-cleaner`:在画像使用之前清洗杂乱的财务来源。
- `model-audit-tieout`:在引用模型数值作为画像事实之前先审计。

## 四、边界判断

- 若用户问"这是不是好投资?",不要单靠速览作答;路由到对应投资技能。
- 若用户要完整信用 / 不良 memo,路由到 独立信用分析流程。
- 若用户要完整模型,先做画像,再交接到建模技能。
- 若用户要会议简报,先画像,再走 `meeting-prep`。
- 若源财务数据未结构化或不一致,先做归一化,再用于画像。
