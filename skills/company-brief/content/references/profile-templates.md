# 速览模板库

本文件提供四类落地模板。挑你当前任务最贴合的一份，把里面的字段填上来源、证据、置信度即可。

## 1. 通用单页速览（Markdown 起手稿）

```markdown
# [主体名称] Brief
**Profile type:** [public_company / equity_issuer_profile / public_sector_peer]
**As of:** [日期 / 时间]
**Scope:** [需求场景、期间、来源说明]
**Source caveat:** [latest / limited / stale / partial / source package only]

## One-line view
[一句话说明这是什么主体，以及它对用户当前工作流的意义。]

## Business snapshot
| Field | Detail | Source | Evidence | Confidence |
|---|---|---|---|---|
| Business model |  |  |  |  |
| HQ / footprint |  |  |  |  |
| Listing / identifiers |  |  |  |  |
| Segments / products |  |  |  |  |
| Customers / end markets |  |  |  |  |

## Key metrics
| Metric | Period | Value | Units | Source | Evidence | Confidence |
|---|---:|---:|---|---|---|---|

## Recent developments
- [有来源支撑的要点]
- [有来源支撑的要点]

## Relevance for this workflow
- [对公开股票 / 业绩 / 估值 / 会议准备的影响；信用相关含义交接到独立信用分析流程]

## Risks, gaps, and evidence flags
- [缺失来源、陈旧、冲突、证据请求或有来源支撑的风险]

## Recommended next step
[下游技能或仍缺的来源。]
```

## 2. 公开公司 / 公开股票画像

应优先纳入：

- 股票代码、交易所、市值、企业价值、股价 / 日期、财年截止。
- 收入、EBITDA / 经营利润、相关时的 EPS / FCF、利润率、增速、净债务 / 杠杆、分部结构。
- 最近一次披露事件、指引、有来源时的一致预期背景、近期股价 / 信用变动（仅当时效新）。
- 与论点相关的争论点、催化剂、风险；不下投资建议。

适用上游场景：在跑 `earnings-preview`、`earnings-deep-dive`、`equity-model-update`、`long-short-pitch`、`comps-valuation`、`dcf-model-builder` 或 `memo-builder` 之前作为底座。

## 3. 独立 HTML 速览

当用户在意图收集阶段挑选 HTML、或主动要求 HTML 时，先整理一份精炼的 `visual-page brief`，再调用 `visual-page` 产出独立 HTML 速览；不要把它做成旧式仪表板外壳或首次覆盖报告。

读者首次阅读应按以下顺序展开：

1. **Investor read**：一句话说清盈利引擎，以及最重要的一个尚未解决的尽调问题。
2. **Metric strip**：四到五项有来源支撑的指标，覆盖规模、盈利、估值背景、资产负债 / 资本配置相关性。
3. **Earnings drivers**：紧凑的表或卡片，呈现真正驱动审阅视角的少数分部 / KPI。
4. **Valuation context**：仅在有来源时呈现 trailing 或衍生倍数、远期一致预期或同业。
5. **Catalysts and risks**：与审阅问题挂钩的短矩阵。
6. **Evidence gaps and next route**：只列影响后续工作的缺口，附加紧凑的来源台账。

> 交互对齐：交给 `visual-page` 时，按 SKILL.md「HTML / 仪表板交付」的组件映射与交互规格落地——指标 KV cards 可 hover / 点击展开来源与置信度、bench bars 带绝对值/同比切换、催化剂风险 2×2 可筛选、来源台账可排序并行内展开；主题维持冰白纸 + 液态玻璃 + 中国红（好）/ 稳绿（坏）。

仅有历史数据或分析师推导的 trailing 倍数时，标题用 `Trailing Valuation Snapshot` 或 `Valuation Context`；只有当远期估计、相关同业、目标价证据或显式的市场预期证据有来源支撑时，才能在标题中出现 `Debate`。

如果当前出现成交、传闻、监管事项或其他实时事件，并且重要但不在用户要求的重点之中，把它放进 Investor read 和 catalysts/risks，并在 evidence-gaps 块中标记缺失的一手证据；除非它直接改变其他章节，否则不要在 earnings drivers、估值、倍数摘要中重复呈现。

证据标签的对外呈现使用自然投资者用语：

| 内部支持标签 | 读者侧 HTML 标签 |
|---|---|
| `fact_source_reported` | Reported |
| `fact_provider_standardized` | Provider data |
| `derived_calculation` | Derived |
| `issuer_management_claim` | Management statement |
| `management_adjusted` | Company-defined |
| `missing_required_source` | Not yet sourced |

## 4. 公开发行人 / 信用画像

应优先纳入：

- 发行人、可披露的母公司 / 担保人、可得的代码（ticker / CUSIP / ISIN）、评级、债务结构、到期墙、价 / 收益率 / 利差。
- 收入、EBITDA / 经营利润、FCF、债务、流动性、杠杆、利息覆盖、公开或用户提供的契约条款。
- 再融资风险、抵押 / 结构优先级、现金消耗、回收背景、成交价水平、评级行动、重组里程碑。
- 缺失的信用文件、陈旧的成交水平、口径定义冲突。

适用上游场景：在跑 独立信用分析流程、`scenario-sensitivity-generator`、`equity-model-update`、`portfolio-risk-management` 或 `memo-builder` 之前作为底座。

## 5. 行业同业 / 竞争对手画像

应优先纳入：

- 同业主体身份、业务模式、分部、地域、KPI、市值 / EV、当前估值、最近一次业绩。
- 与焦点公司的差异：增速、利润率、结构、杠杆、资本配置、披露质量、催化剂敞口。
- 用于支撑可比、论点验证或同业映射的估值 / 经营指标。

适用上游场景：在跑 `comps-valuation`、`earnings-preview`、`earnings-deep-dive`、`equity-model-update`、`long-short-pitch` 或 `memo-builder` 之前作为同业垫。

## 6. 超紧凑画像块

在 deck、memo 或会议简报里位置局促时使用：

```markdown
**[主体]** 是 [商业模式 / 战略]，服务 [客户 / 终端市场]，覆盖 [地域]。最新有来源支撑的规模：[指标 1]、[指标 2]、[指标 3]（截至 [期间]）。当前相关性：[为何重要]。关键缺口 / 旗标：[缺口或风险]。
```

## 7. 公开股票投资者画像增项

可用且与审阅相关时，补上证券与流动性快照、指数成分身份、ETF 持仓 / 资金流相关性、因子敞口、卖空、持股集中度、公司治理、资本配置、资产负债风险，以及下一分析路径。整体保持事实型，不下投资建议。

默认的"证券设置 / 持仓 / 头寸"块：

| Field | Value | As-of | Source | Confidence | Why it matters |
|---|---|---|---|---|---|
| Market cap / EV |  |  |  |  | Valuation and investability anchor |
| Float / free float |  |  |  |  | Capacity, passive flow, squeeze risk |
| ADV / liquidity / days-to-exit |  |  |  |  | Can a PM build or exit the position? |
| Index membership / benchmark weight |  |  |  |  | Active-weight and passive-flow relevance |
| ETF/passive ownership or flow signal |  |  |  |  | Rebalance and flow pressure |
| Top holders / ownership concentration |  |  |  |  | Governance, sponsorship, overhang |
| Short interest / borrow / days to cover |  |  |  |  | Short crowding and squeeze risk |
| Factor exposure / beta |  |  |  |  | Stock-specific versus factor-driven risk |
| Governance / capital allocation |  |  |  |  | Management quality and minority-holder risk |
| Sell-side coverage / consensus setup |  |  |  |  | Estimate path and variant wedge |

字段缺失时，在支持材料里保留 `missing_required_source` 标签并写出所需的提供商 / 导出 / 来源；面向读者的 HTML 中，把这些非核心缺口整合进一个精炼的 evidence-gaps 区块，不要展示冗长低信息量的占位表。
