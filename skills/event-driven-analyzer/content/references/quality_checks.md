# Quality Checks

输出在送审/送外部之前,过一遍以下两层检查清单(通用 + 事件类型专项)。

## 通用检查(Universal)

按"是什么 → 怎么衡量 → 怎么收口"三段顺序自检:

**身份与口径**
- 事件类型已显式标记;多重身份(例如同时是 spin + activist)要把每个相关标签都挂出来。
- 证券表达方式(普通股 / 期权 / CDS / CVR / 套利组合)写明。
- 行情数据带时间戳;若不可得,显式标注"unavailable"。

**事实与判断分层**
- 事实、假设、判断在文中分区呈现,不混写。
- 一手文件(招股书 / 8-K / proxy / 法院文书)优先;缺关键文件就把缺哪份列出来。
- 时间表把"已知日期"和"估计日期"两类分开标注。

**风险与下行**
- gating item(决策卡点)指向具体的决策人或流程节点,不能是模糊条件。
- 下行 / break value 的方法学(被并购方价值锚、行业可比、流动性折扣等)写明。
- 任何期望回报和年化回报数字,旁边必须有对应的下行场景陪同呈现。

**情景与概率**
- 情景概率加总到 100%;概率和不为 1 时,先修正情景权重再计算任何加权结论,**不要**用未归一化的概率得出期望回报或加权年化。
- 概率未对齐时,**禁止**展示概率加权结论。

**结论与监控**
- 建议明确(买 / 卖 / 不交易);如选择不交易,把不交易的理由写到同等颗粒度。
- 监控计划包含四要素:日期 / 触发窗口 / 数据源 / 信号 → 行动映射。
- 自带 red-team 段:站在对立面解释这笔交易亏钱的最快路径。

## 事件专项检查(Event-specific)

### Merger arb
- Deal price and current price are confirmed, or explicitly marked unverified.
- Spread and annualized spread are calculated.
- Market-implied probability is calculated when downside is available.
- Merger agreement / proxy status is reviewed.
- Outside date and expected close date are presented as separate fields.
- Break fee / reverse termination fee and the financing condition are reviewed, or marked missing.
- Regulatory approvals and vote thresholds are named.
- Acquirer risk and hedge ratio are included on stock deals.

### Spin-off
- Distribution mechanics and dates are included.
- SpinCo and RemainCo financials are separated.
- Debt / cash / liability allocation is considered.
- Stranded costs and dis-synergies are considered.
- Forced selling, index, and holder-base analysis is included.
- Entry-timing question is addressed.

### Activism
- Activist ownership and demands are stated.
- Governance and nomination mechanics are considered.
- Vote math and shareholder base are assessed.
- Settlement vs. proxy-fight probability is included.
- Value-creation plan is judged, not just summarized.

### Litigation / regulatory
- Venue / agency and procedural posture are stated.
- Timeline and the next official date are included.
- Remedy / damages / settlement path is analyzed.
- The legal-advice boundary is respected.
- Official sources are prioritized.

### Restructuring / distressed
- A dated catalyst or process path is explicit.
- The probability / payoff tree uses sourced or clearly labeled recovery assumptions.
- When capital structure, covenants, liquidity, maturity wall, fulcrum security, priority, or recovery waterfall are central, the output routes to or incorporates work from 独立信用分析流程.
- Priming / LME / class-vote / court risk is treated as event-path risk, with legal conclusions reserved for counsel.

### Technical / special situations
- Flow mechanics and dates are included.
- Flow size is compared to liquidity.
- Crowding and pre-positioning are considered.
- An exit plan is stated.

## Senior-taste checks

Ask yourself:
- Would a PM know what to do after reading the first page?
- Is the variant view clear?
- Did the output find the real gating item, or only generic risks?
- Is the downside intellectually honest?
- Is the trade expression practical in real market conditions?
- Are we over-precise relative to source quality?
- Did we state what would change our mind?

## Common failure modes

- Summarizing news instead of underwriting outcomes.
- Treating annualized spread as the conclusion.
- Failing to calculate market-implied probability.
- Accepting an unaffected price as the break price without adjustment.
- Ignoring timing risk.
- Ignoring stock-deal acquirer risk.
- Ignoring borrow / liquidity / carry.
- Falling back on generic regulatory or litigation risk language.
- Omitting a monitoring plan.
- Giving a trade recommendation based on possible MNPI.
