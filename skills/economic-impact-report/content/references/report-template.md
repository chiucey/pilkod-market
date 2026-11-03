# 上市股票经济影响报告 · 模板骨架

本骨架是默认产出形态。除非用户在请求里明确写出"摘要 / 快读 / TL;DR / 单页 / 只要某一段",否则一律按完整结构落稿,顺序、字段、留白都不要省。

> 章节命名说明:下方代码块里的 `## ` 英文标题是经济影响报告的稳定内容锚点，便于整理 `visual-page brief`；每节内部的中文导语、bullet、解释文字可以按写作需要打磨。

```markdown
# [事件标题]: Public Equity Impact

## Executive Call
[用一段紧凑文字回答以下五件事,顺序可调:本次到底发生了什么、相比此前的预期有哪些是真正新的、为什么这件事对上市股票而非私募 / 信用 / 商品更要紧、第一条被打开的传导链是哪条、置信度最高的发行人 / 板块 / 组合层面的判断落在哪里。]

## Strongest Counterview
- 与本文主论点相对的最强反方陈述:
- 反方可能成立的具体情境或证据:
- 反方比主论点更弱、更晚或已被市场定价的理由:

## Scenario Matrix
### Base Case ([x]%)
- 关键假设:
- 对股票价格 / 估值 / 资金面的后果:
- 在该情境下变化最大的标的或因子:

### Upside / Bull Case ([x]%)
- 关键假设:
- 对股票价格 / 估值 / 资金面的后果:
- 与基准情境相比走势不同的标的或因子:

### Downside / Bear Case ([x]%)
- 关键假设:
- 对股票价格 / 估值 / 资金面的后果:
- 与基准情境相比走势不同的标的或因子:

## Event Status And Market Baseline
- 事件状态:已确认 / 已被报道但未确认 / 假设情境 / 各方说法冲突 / 仍未尘埃落定
- 支撑事件成立的核心证据及其时间戳:
- 研究截止时间 (research cut-off):若引用了盘中观察值,务必写明时间和时区
- 相关市场观察:点名基准 (benchmark);视情况标注现货 vs 期货、合约 / 月份、盘中 vs 收盘、时间戳、来源 (source_id)
- 期初价 / 一致预期里已经反映了哪些信息:
- 仍未核实的关键缺口 (material verification gaps):

## Source And Freshness
- Data cut-off: 填写 as_of_date,精确到时区
- Sources used: 用 source_id 列表的形式给出
- Evidence posture: decision-grade / research-grade / preliminary / assumption-led / not supportable
- Stale or missing data: 若无重大缺失填 none material;否则逐项列出并保持 draft 状态
- 不同来源相互冲突时的处理:

## What Is New Vs. Expected
- 事件发生前的基准 / 一致预期:
- 真正的增量信息 (genuine delta):
- 该增量为什么对股票端要紧:
- 哪些信息其实是旧闻、背景或市场早已知晓:

## Why Now
- 短期内 vs 近端 vs 中期 vs 结构性的不同影响:
- 大致的重新定价顺序 (repricing sequence):
- 哪些反应会快速消退、哪些会持续:

## Event-To-Equity Transmission Map
### Transmission Map
1. [事件 / 触发因素] -> [传导渠道] -> [发行人 / 板块层面的驱动变量] -> [财务报表上首先受影响的科目] -> [对个股 / 组合的含义]
2. [事件 / 触发因素] -> [传导渠道] -> [发行人 / 板块层面的驱动变量] -> [财务报表上首先受影响的科目] -> [对个股 / 组合的含义]
3. [事件 / 触发因素] -> [传导渠道] -> [发行人 / 板块层面的驱动变量] -> [财务报表上首先受影响的科目] -> [对个股 / 组合的含义]

## Ranked Equity Impact Map
### Issuer And Sector Impact
凡是被点名的发行人,如果手里没有公司层面的具体证据,只能写成"代表性敞口候选" (representative exposure candidate) 或挂进研究队列 (research queue),不可直接给出证券层面的结论。
只在多个敞口共用同一条传导渠道、首要受影响的报表科目相同、方向性判断也一致时才并入同一行;否则拆开为多个候选。

| Rank | 候选发行人 / 板块 | 方向 | 直接性 | 传导机制 | 首先受影响的报表科目 | 时序 | 置信度 | 已被定价程度 | 研究 / PM 行动 |
|---|---|---|---|---|---|---|---|---|---|

## Public Equity Bottom Line
- 多头层面暴露度最高的候选:
- 空头 / 回避层面暴露度最高的候选:
- 同板块 / 同类公司层面的横向解读 (peer-group read-through):
- 组合行动姿态: add / press / hold / trim / exit / hedge / watchlist / pass / wait for proof / re-underwrite
- 若用户没有提供组合或观察名单,直接标注 portfolio-specific action unavailable,改用通用敞口图、观察名单、研究队列、等待证据成熟、跳过该选题、或重新审视候选这几种姿态之一。
- 市场大概率已经定价进去的部分:
- 仍可能被错误定价、值得继续挖的部分:

## General Exposure Map If No Portfolio Was Provided
| 敞口桶 | 涉及行业 / 国家 / 货币 / 公司 / 商品 | 公开市场的传导机制 | 首先被改写的估值 / 盈利科目 | 仓位 / 资金流向的解读 | 下一步研究 workflow |
|---|---|---|---|---|---|

## Public Equity Framing
- 股票市场最先会关心的点:
- 共识 (consensus) 可能已经过时的位置:
- 看似显而易见、但其实可能拥挤 / 噪音过大的交易方向:
- 最适合的股票表达方式 (best equity expression):
- 即使非股票市场的信号,如果对股票判断关键,也单独列出:

## Earnings, Valuation, And Positioning Read-Through
- 盈利预测 (estimate) 的修订路径:
- 利润率 / FCF / 资产负债表层面的影响:
- 估值倍数层面的含义:
- 因子 / 基准 / ETF / 指数 / 持股结构 / 拥挤度 / 流动性 / 空头利益的隐含信号:
- 信用利差 / 利率 / 汇率 / 商品 / 波动率 / 期货等,用作判断上市股票时的输入信号:

## What Is Priced In Vs. What Requires Proof
- 当前股价或商品价格似乎已经反映的部分:
- 支撑"已定价"判断的一手证据(受影响个股 / 板块、预测修订、估值变动,或相关传导市场):
- 若用到了宽基指数作为参考,务必明确标注它仅是辅助证据而非主证据:
- 仍属于推断或情境假设的部分:
- 若要触发预测修订或估值倍数变化,需要哪些证据:
- 反之,哪些证据会推翻或显著削弱本次结论:

## Second-, Third-, And Fourth-Order Equity Effects
### Second-order
- ...
### Third-order
- ...
### Fourth-order
- ...

## Monitoring Triggers And Research Queue
- 列出会让论点失效或必须显著修订的具体监测项:数据发布、监管申报、宏观数据、管理层表态、政策动作、市场信号、卖方预测修订、仓位变化等。
- 研究队列:在拿到对应发行人侧的证据之前,不要把代表性敞口候选直接升级为证券层面的结论。

## What Would Change The View
- 用可证伪的语言写明证据门槛:达到什么程度足以推翻或显著修订当前论点,以及对应会切换到哪个行动姿态。

## Bottom-Line Judgment
- 最关键的事是什么:
- 哪些其实是噪音:
- 当下可以执行的动作:
- 需要继续跟踪的项目:
- 推荐的下一步多市场股票研究 workflow:
```

排版与呈现建议:输出独立 HTML 报告时,首屏可读层尽量做轻,把 `Executive Call`、`Event Status And Market Baseline`、传导图、`Ranked Equity Impact Map` 放在情境矩阵、监测清单、来源台账之前可见;关键事实的引用挂在使用点附近即可,如果同一来源支撑相邻的多个模块,只在节级别写一条来源备注,避免每个 bullet 都重复挂同一标签。

交互对齐:交给 `visual-page` 时,按 SKILL.md「HTML 交付」的组件映射与交互规格落地——传导图用可点击 Mermaid、`Ranked Equity Impact Map` 可排序并按方向/直接性筛选、`Scenario Matrix` 用 Base/Bull/Bear tab + 概率滑块联动、高阶影响用 accordion;主题维持冰白纸 + 液态玻璃 + 中国红(利好/受益)/ 稳绿(利空/受损)。
