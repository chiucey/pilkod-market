# 输出契约

默认使用本文件给出的完整结构,所有决策关键行都保留。仅当用户明确要"摘要 / 快读 / 一页纸 / 简版 / TL;DR / 某一节"时才做压缩。

## 跟踪器更新:GUI 优先

对于附件中或既有的论点跟踪器更新,默认主交付物是一份由 `visual-page` 生成的 GUI/HTML 审查页。只有当用户明确要求 Excel/CSV、需要导入外部系统或需要审计附件时，才额外生成 XLSX/CSV。

> 交互对齐:GUI 审查页按 SKILL.md「HTML 交付」的组件映射与交互规格落地——支柱表可排序 + 状态 chips + 行内展开、论点状态 KV cards 可展开、公司论点 vs 证券论点 side-by-side 可 toggle、决策日志仅追加可行内展开并带批准 badges、KPI/股价 >8 日期才上 Chart.js;主题维持冰白纸 + 液态玻璃 + 中国红(改善/增持)/ 稳绿(恶化/减持)。

若生成 XLSX,`Cover` 选项卡必须**先让决策可读**,再呈现审计轨迹:

| 首屏分区 | 必须呈现的内容 |
|---|---|
| 公司论点 | 前期状态、当前状态、确认了什么、走弱了什么、下一个基本面验证点 |
| 证券论点就绪度 | `Ready` / `Conditional` / `Re-underwrite` / `Not decision-grade`;当前股价与市场数据截至时间;估值就绪度与被阻塞的输入 |
| 仓位行动 | `Add` / `Hold` / `Trim` / `Exit` / `Wait for proof` / `Re-underwrite`,并写明行动条件 |
| 行动规则摘要 | 当前行动、适用规则的批准状态、下一个审查关口;完整触发条件 / 来源 / 必需材料留在 `Action Rules` 选项卡 |
| 证据缺口摘要 | 主要决策阻碍及其对就绪度的影响;完整的尽调 / 待解问题登记表留在专属选项卡 |

首屏支柱视图要保持紧凑:支柱、优先级 / 继承权重、前期 / 当前状态、论点驱动证据、下一个验证点、行动含义。详细阈值定义、引用、模型影响、后续事项放进专属监控或证据选项卡,不要横向拓宽支柱表。

继承的核心支柱处于 `Impaired` 时,公司论点汇总为 `Watch` 需要写出**有证据支撑的明确覆盖理由**。多个核心支柱 `Impaired` 时,除非给出该覆盖理由,汇总默认为 `Impaired`。

`Cover` 保持精简:不在其上重复完整的行动规则矩阵或完整的尽调 / 待解问题登记表。

每条行动触发条件都打上 `Inherited threshold`、`Draft threshold for PM confirmation`、`Approved monitoring rule` 之一。**不要**把生成的阈值当作已批准的持有 / 减持 / 退出规则来呈现。

除非前期跟踪器已定义评分方法或用户明确要求,不要追加支柱汇总得分或评分图。默认用定性的信号 / 状态格式即可。

## 默认更新备忘录

```markdown
# [Company / Ticker] Marginal Tracker Update
As of: [date/time] | Direction/mandate: [long/short/rating/etc.] | Company thesis status: [current vs prior] | Security thesis readiness: [readiness] | Recommendation: [action] | Next decision point: [date/catalyst/threshold]

## PM Summary
[3-6 句:本次变化 / 证据是否确认或削弱公司论点 / 证券论点是否够格决策 / 风险回报改善还是恶化 / 应取何行动。]

## What Changed
| Item | Prior house view | Consensus / market setup | New evidence | Thesis read-through |
|---|---|---|---|---|

## Pillar Tracker
| Pillar | Weight | Prior | Current | Latest evidence | Signal | Next proof point |
|---|---:|---|---|---|---|---|

## KPI / Estimate / Catalyst Update
[只放影响决策的指标、修正、事件。]

## Model, Valuation, Risk/Reward
[变化的假设、目标价 / 公允值 / 下行影响、预测与倍数的对照、是否过门槛。]

## Action Thresholds
| Trigger | Threshold/date | Origin | Approval status | Required source | Action |
|---|---|---|---|---|---|

## Operating Model
| Cadence item | Value | Decision responsibility | Next date / SLA | Escalation trigger |
|---|---|---|---|---|
| Review cadence |  | tracker refresh |  |  |
| Post-catalyst update SLA |  | rapid update |  |  |

## Red-Team / Open Questions / Changelog
Best opposing view: [view]. What makes it right: [evidence]. Open questions: [asks].
| Date | Change | Source | Rationale | Next step |
|---|---|---|---|---|
```

## 空白跟踪器骨架

用户未提供论点时使用;**不编造事实**。

必备分区 / 表格:Topic 索引(主题、状态)、Events(每个 topic 一条事件链:date、headline、fact、source、signal、marginal_change、interpretation、impact、follow_up)、可选汇总(Catalyst Calendar、Model Changelog、Decision Log、Sources、Open Questions)。

最小字段集:

- Dashboard:发行人 / 证券、方向、授权、期限、公司论点状态、证券论点就绪度、仓位行动、市场数据截至时间、可佐证时的基础 / 乐观 / 悲观值、下一个催化剂、建议、下一次审查、被阻塞的输入。
- Operating model:决策权限、审查节奏、催化剂后更新 SLA、升级触发条件、下一审查关口、仅追加决策日志流程。
- Underwriting:论点、差异化认知、市场框架、估值锚、催化剂、风险、终止标准、尽调。
- Pillars:支柱、优先级或继承权重及其来源、主张、KPI / 证据、确认 / 警告 / 失效阈值、状态、下一个验证点。
- Evidence:日期、来源、事实、所属支柱、信号、幅度、模型影响、行动含义、后续事项。
- Action rules:触发、阈值 / 日期、阈值来源、阈值批准状态、必需来源、行动、下次审查。
- Decision log:日期、决策、依据、证据、公司论点状态、证券论点就绪度、仓位 / 评级变化、下次审查。

## PM 仪表板

```markdown
Company thesis: [status/change] | Security readiness: [readiness] | Action: [recommendation] | Conviction: [level/change] | Risk/reward: [upside/downside/skew or blocked] | Next catalyst: [event/date] | Key call: [one sentence]

| Dimension | Current read | PM judgment |
|---|---|---|
| Fundamentals / estimates / valuation / setup / catalyst path / thesis risk |  |  |
```

## 投资组合复核

必含:优先行动、出现恶化的标的、证据改善但风险回报变差的标的、即将到来的催化剂观察列表。

## 授权特定语言

- 卖方:评级 / 目标价含义、预测变化、估值桥、关键风险、客户辩论。
- 多空:交易含义、仓位 / 走势设置、催化剂路径、借券 / 逼空 / 因子风险、对冲 / 减持阈值。
- 股权风险中的信用信号:流动性、到期、契约压力、CDS / 利差预警、普通股下行行动;信用证券与回收分析路由至独立信用分析流程。

## 语气示例

**鼓励**:"论点正在兑现,但估值重估比预测更快;业务论点更强,股票论点变得不那么有吸引力。"

**避免**:"业绩不错股价也涨,继续观察。"
