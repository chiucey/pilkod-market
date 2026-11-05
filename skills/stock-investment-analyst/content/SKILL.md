---
name: stock-investment-analyst
description: "Professional stock investment analysis expert. Performs comprehensive fundamental analysis, technical analysis, business analysis, and market research to generate actionable investment reports with specific buy/sell prices, stop-loss levels, and position sizing. Trigger when users ask to analyze stocks, evaluate companies, interpret financial statements, analyze charts/technical indicators, or seek investment advice."
---

# Stock Investment Analysis Expert (股票投资分析专家)

## Overview

This skill provides comprehensive stock investment analysis by combining four analytical dimensions: fundamental analysis (financials, valuation), technical analysis (charts, indicators, price targets), business analysis (moats, competitive landscape, growth drivers), and market research (news, policy, fund flows, sentiment). It produces a complete investment research report with specific, actionable trading recommendations.

## Workflow

### Step 1: Comprehensive Data Collection

Gather all necessary data using web search and any available financial data tools. Search for the following in parallel:

1. **Price Data** — At least 6 months of historical price data (for technical analysis)
2. **Financial Data** — Complete financial statements (income statement, balance sheet, cash flow)
3. **Statistics & Valuation** — Key valuation metrics (PE, PB, PS, EV/EBITDA, etc.)
4. **Company Info** — Basic company information, sector, market cap
5. **Analyst Insights** — Analyst ratings, target prices, consensus estimates
6. **News** — At least 20 recent news articles about the company
7. **Industry Research** — Search for latest industry trends, policies, competitor news

Use web search with queries such as:
- "[Company name] financial results [year]"
- "[Company name] stock analysis"
- "[Industry] industry trends policy [year]"
- "[Company name] analyst ratings target price"
- "[Company name] latest news"
- "[Company name] competitors market share"
- "[Company name] fund flow institutional holdings"

### Step 2: Fundamental Analysis

Perform deep financial analysis covering:

1. Financial health assessment (DuPont analysis, cash flow quality)
2. Multi-dimensional valuation analysis (relative + absolute valuation)
3. Earnings quality and sustainability analysis
4. Growth analysis and forecasting
5. Financial risk screening

*(See Section: Fundamental Analysis Framework below for detailed methodology)*

### Step 3: Technical Analysis

Perform multi-timeframe technical analysis covering:

1. Monthly/Weekly/Daily trend analysis
2. Technical indicator matrix (MA, MACD, RSI, KDJ, BOLL, volume)
3. Chart pattern identification
4. Volume-price relationship analysis
5. Precise support/resistance and target price calculation

*(See Section: Technical Analysis Framework below for detailed methodology)*

### Step 4: Business Analysis

Perform deep business and competitive analysis covering:

1. Business model and profit model dissection
2. Moat evaluation (brand, technology, scale, network effects, switching costs)
3. Industry chain position and bargaining power
4. Competitive landscape (Porter's Five Forces)
5. Growth driver analysis and ceiling estimation

*(See Section: Business Analysis Framework below for detailed methodology)*

### Step 5: Market Research

Perform comprehensive market intelligence gathering covering:

1. Latest material news and events (last 30 days)
2. Policy and regulatory environment
3. Fund flow analysis (institutional, northbound/foreign, margin trading)
4. Market sentiment indicators
5. Analyst consensus and divergence analysis

*(See Section: Market Research Framework below for detailed methodology)*

### Step 6: Synthesis and Investment Recommendation

Integrate all four analyses into a unified investment report:

1. Assign ratings (1-5 stars) for each dimension
2. Determine overall investment rating
3. Formulate specific trading plans (aggressive/moderate/conservative)
4. Identify key risks and monitoring points
5. Output the complete report following the Report Template

---

## Fundamental Analysis Framework

### 1. Financial Health Deep Analysis

#### 1.1 Balance Sheet Analysis
- **Asset Quality**:
  - Accounts receivable quality (aging analysis, bad debt provision adequacy)
  - Inventory quality (turnover rate, impairment provisions)
  - Goodwill and intangible assets (proportion, impairment risk)
  - Fixed assets (capacity utilization, depreciation policy)
- **Debt Structure**:
  - Interest-bearing debt ratio and financing costs
  - Short-term vs long-term debt structure
  - Off-balance-sheet liabilities (guarantees, leases)
- **Capital Structure**:
  - Shareholder equity composition
  - Retained earnings vs share capital
  - Minority interest proportion

#### 1.2 DuPont Analysis Deep Decomposition

```
ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
    = (Net Income/Revenue) × (Revenue/Total Assets) × (Total Assets/Equity)
```

- Decompose ROE change drivers
- Compare with historical periods to identify change causes
- Compare with peers to identify strengths/weaknesses

#### 1.3 Cash Flow Deep Analysis
- **Operating Cash Flow**:
  - OCF/Net Income ratio (>1 is high quality)
  - OCF trend changes
  - Working capital movement analysis
- **Investing Cash Flow**:
  - CapEx intensity and direction
  - M&A activity
  - Investment income quality
- **Financing Cash Flow**:
  - Dividend policy and payout ratio
  - Financing needs and costs
  - Buyback plans
- **Free Cash Flow**:
  - FCF = Operating Cash Flow - CapEx
  - FCF Yield = FCF / Market Cap
  - FCF stability assessment

### 2. Profitability Deep Analysis

#### 2.1 Income Statement Decomposition
- **Gross Profit Analysis**: Margin trends, product mix impact, cost changes
- **Expense Analysis**: SG&A ratio trends, R&D investment, expense control
- **Profit Quality**: Non-recurring items proportion, government subsidy dependence

#### 2.2 Profitability Indicator Matrix

| Indicator | Current | YoY | 3-Year Avg | Industry Avg | Industry Rank |
|-----------|---------|-----|------------|--------------|---------------|
| Gross Margin | | | | | |
| Net Margin | | | | | |
| ROE | | | | | |
| ROA | | | | | |
| ROIC | | | | | |

### 3. Growth Analysis

#### 3.1 Historical Growth

| Indicator | 1-Year | 3-Year CAGR | 5-Year CAGR | Volatility |
|-----------|--------|-------------|-------------|------------|
| Revenue Growth | | | | |
| Net Income Growth | | | | |
| Core Earnings Growth | | | | |
| OCF Growth | | | | |

#### 3.2 Growth Quality Assessment
- **Revenue Growth Quality**: Organic vs M&A growth; volume vs price driven; new vs existing customers
- **Profit Growth Quality**: Gross profit driven vs expense cuts; core business vs other income; cash flow support

### 4. Multi-Dimensional Valuation Analysis

#### 4.1 Relative Valuation Matrix

| Metric | Current | 1Y Avg | 3Y Avg | 5Y Avg | Historical Percentile | Industry Avg | Industry Percentile |
|--------|---------|--------|--------|--------|----------------------|--------------|---------------------|
| PE(TTM) | | | | | | | |
| Forward PE | | | | | | | |
| PB | | | | | | | |
| PS | | | | | | | |
| EV/EBITDA | | | | | | | |
| PEG | | | | | | | |

#### 4.2 Valuation Reasonableness
- **PE Reasonableness**: ROE match (high ROE supports high PE); growth match (PEG analysis); cycle position
- **PB Reasonableness**: ROE match; asset-heavy vs asset-light; net asset quality

#### 4.3 Absolute Valuation Reference (Simplified DCF)
- **Core Assumptions**: 5-year growth rate, terminal growth rate, WACC
- **Valuation Range**: Optimistic / Base / Pessimistic scenarios
- **Margin of Safety**: Current price vs intrinsic value

### 5. Financial Risk Warning

#### 5.1 Financial Fraud Warning Signals
- [ ] AR growth far exceeds revenue growth
- [ ] Abnormal inventory increase
- [ ] OCF persistently below net income
- [ ] Gross margin abnormally higher than peers
- [ ] Excessive related-party transactions
- [ ] Non-standard audit opinion
- [ ] Frequent auditor changes
- [ ] Major shareholder high pledge ratio

#### 5.2 Financial Health Scorecard

| Dimension | Score (1-10) | Weight | Weighted Score | Basis |
|-----------|-------------|--------|----------------|-------|
| Solvency | | 20% | | |
| Profitability | | 25% | | |
| Operational Efficiency | | 15% | | |
| Growth | | 20% | | |
| Cash Flow | | 20% | | |
| **Overall** | | 100% | | |

---

## Technical Analysis Framework

### 1. Multi-Timeframe Trend Analysis

#### 1.1 Monthly (Long-term Trend)
- Trend judgment: bull/bear/range
- Key levels: historical highs/lows, long-term moving averages
- Cycle position: current stage in the major cycle

#### 1.2 Weekly (Medium-term Trend)
- Trend judgment: up/down/sideways
- Wave count: current wave position
- Medium-term MAs: MA20/60 weekly status

#### 1.3 Daily (Short-term Trend)
- Trend judgment: short-term direction and strength
- MA system: bullish/bearish alignment
- Recent patterns and breakouts

#### 1.4 Multi-Timeframe Confluence

| Timeframe | Trend Direction | Trend Strength | Key Levels | Signal |
|-----------|----------------|----------------|------------|--------|
| Monthly | | | | |
| Weekly | | | | |
| Daily | | | | |
| **Confluence** | | | | |

### 2. Technical Indicator Matrix

#### 2.1 Trend Indicators
- **MA System**: MA5/10/20/60/120/250 alignment, golden/death crosses, slope changes
- **MACD**: DIF/DEA values, crosses above/below zero axis, histogram trend, divergences
- **Trendlines/Channels**: ascending/descending trendlines, channel boundaries

#### 2.2 Momentum Indicators
- **RSI**: RSI(6)/RSI(14) values, overbought(>70)/oversold(<30), divergences
- **KDJ**: K/D/J values, crosses, overbought/oversold zones, stagnation
- **CCI**: CCI value and trend, +100/-100 breakouts

#### 2.3 Volatility Indicators
- **Bollinger Bands**: Upper/Middle/Lower band values, bandwidth (expansion/contraction), price position
- **ATR**: Volatility level, use for stop-loss reference

#### 2.4 Volume Indicators
- **Volume**: Level (heavy/light/normal), comparison to average volume, volume-price coordination
- **OBV**: Trend direction, divergences with price
- **Turnover Rate**: Level and anomalies

#### 2.5 Comprehensive Indicator Matrix

| Category | Indicator | Current Value | Signal Type | Signal Strength | Direction |
|----------|-----------|---------------|-------------|-----------------|-----------|
| Trend | MA System | | | | |
| Trend | MACD | | | | |
| Momentum | RSI | | | | |
| Momentum | KDJ | | | | |
| Volatility | BOLL | | | | |
| Volume | Volume | | | | |

### 3. Chart Pattern Analysis

#### 3.1 Reversal Patterns
- Head & Shoulders (top/bottom), Double Top/Bottom, Triple Top/Bottom, Rounding Top/Bottom
- Identification criteria, confirmation conditions, target measurement

#### 3.2 Continuation Patterns
- Ascending/Descending/Symmetric Triangles, Flags/Wedges, Rectangles
- Breakout direction, target measurement

#### 3.3 Candlestick Signals
- Hammer, Engulfing, Doji, Morning/Evening Star
- Position context, signal strength, forecast

### 4. Volume-Price Relationship Analysis

| Volume-Price Combo | Market Meaning | Current Status | Action Signal |
|-------------------|----------------|----------------|---------------|
| Volume up + Price up | Strong advance | | |
| Volume down + Price up | Weakening momentum | | |
| Volume up + Price down | Panic selling | | |
| Volume down + Price down | Reluctant selling | | |
| Volume up + Sideways | Growing divergence | | |
| Volume down + Sideways | Wait-and-see mood | | |

### 5. Key Price Level Calculation

#### 5.1 Support Levels

| Support | Price | Calculation Basis | Strength | Validation |
|---------|-------|-------------------|----------|------------|
| S1 (Strong) | | | | |
| S2 | | | | |
| S3 (Weak) | | | | |

**Methods**: Previous lows, MA support (MA20/60/120/250), Bollinger lower band, Fibonacci retracement (0.382/0.5/0.618), gap support, round numbers

#### 5.2 Resistance Levels

| Resistance | Price | Calculation Basis | Strength | Breakout Condition |
|------------|-------|-------------------|----------|--------------------|
| R1 (Weak) | | | | |
| R2 | | | | |
| R3 (Strong) | | | | |

**Methods**: Previous highs, MA resistance, Bollinger upper band, Fibonacci extensions, gap resistance, round numbers, trapped position clusters

#### 5.3 Target Price Calculation

| Target | Price | Gain % | Basis | Probability |
|--------|-------|--------|-------|-------------|
| Target 1 | | | | |
| Target 2 | | | | |
| Ultimate Target | | | | |

**Methods**: Pattern measurement (height projection), Fibonacci extension (1.618/2.618), previous high breakout projection, channel upper boundary

### 6. Trading Plan

#### 6.1 Buy Signal Matrix

| Buy Type | Trigger Condition | Current Status | Entry Price | Stop Loss | Target |
|----------|-------------------|----------------|-------------|-----------|--------|
| Breakout | | | | | |
| Pullback | | | | | |
| Bottom Pattern | | | | | |
| Indicator Cross | | | | | |

#### 6.2 Sell Signal Matrix

| Sell Type | Trigger Condition | Current Status | Risk Level |
|-----------|-------------------|----------------|------------|
| Break down | | | |
| Top pattern | | | |
| Indicator divergence | | | |
| Target reached | | | |

#### 6.3 Risk-Reward Analysis
- Expected return: xx%
- Maximum risk: xx%
- Risk-reward ratio: x:1
- Trade assessment: [Worthwhile / Cautious / Not recommended]

---

## Business Analysis Framework

### 1. Business Model Analysis

#### 1.1 Value Creation
- **Value Proposition**: What problem does the company solve? What value does it create?
- **Target Customers**: Core customer segments, customer profiles and needs
- **Value Delivery**: Channels and methods to reach customers
- **Customer Relationships**: Customer retention, stickiness metrics

#### 1.2 Profit Model

| Business Segment | Revenue Share | Gross Margin | Growth Trend | Competition |
|-----------------|--------------|-------------|--------------|-------------|

- Revenue quality: Recurring vs one-time revenue, advance receipts
- Pricing power: Pricing mechanism, ability to raise prices
- Revenue recognition: Whether policies are aggressive

#### 1.3 Cost Structure
- Fixed vs variable costs
- Scale effects: How costs change with revenue growth
- Break-even analysis

### 2. Moat Evaluation

| Moat Type | Strength (1-5) | Sustainability | Description |
|-----------|----------------|----------------|-------------|
| Brand Barrier | | | Brand awareness, premium ability, loyalty |
| Technology Barrier | | | Tech leadership, R&D intensity, patents |
| Scale Effects | | | Cost advantages from scale |
| Network Effects | | | Value increase with user growth |
| Switching Costs | | | Migration costs, data lock-in, habit dependency |
| Franchise/License | | | Government licenses, regulatory barriers, resource exclusivity |

### 3. Industry Chain Analysis

#### 3.1 Industry Chain Position
```
Upstream: [Suppliers] → Midstream: [Company Position] → Downstream: [Customers]
```

#### 3.2 Bargaining Power

| Direction | Bargaining Power | Basis | Trend |
|-----------|-----------------|-------|-------|
| vs Upstream | Strong/Medium/Weak | | |
| vs Downstream | Strong/Medium/Weak | | |

#### 3.3 Supply Chain Risks
- Key supplier concentration
- Customer concentration
- Supply chain disruption risk

### 4. Competitive Landscape (Porter's Five Forces)

- **Existing Competitors**: Competition intensity
- **Potential Entrants**: Entry barrier height
- **Substitute Threats**: Substitute product/service threats
- **Supplier Power**: Supplier bargaining power
- **Buyer Power**: Customer bargaining power

#### Competitor Comparison

| Competitor | Market Share | Core Advantage | Core Weakness | Strategic Direction | Threat Level |
|-----------|-------------|----------------|---------------|---------------------|--------------|

### 5. Growth Driver Analysis

| Growth Factor | Type | Contribution | Duration | Certainty | Description |
|--------------|------|-------------|----------|-----------|-------------|
| | Organic/External/Industry | High/Med/Low | X years | High/Med/Low | |

#### 5.1 Organic Growth Drivers
- Volume growth, price increases, product mix optimization, operational efficiency

#### 5.2 External Growth Drivers
- New products, new markets/regions, new channels, M&A

#### 5.3 Industry Growth Drivers
- Industry cycle position, penetration rate increase, import substitution, policy-driven

### 6. Growth Ceiling Estimation

- **TAM (Total Addressable Market)**: Overall market size
- **SAM (Serviceable Addressable Market)**: Reachable market
- **SOM (Serviceable Obtainable Market)**: Obtainable market share
- **Revenue Ceiling**: Based on market space and share
- **Market Cap Ceiling**: Based on valuation assumptions
- **Distance to Ceiling**: Current gap as percentage

### 7. Management Assessment

| Dimension | Score | Description |
|-----------|-------|-------------|
| Management Capability | | |
| Execution Ability | | |
| Integrity | | |
| Incentive Alignment | | |

- Equity structure, controlling shareholder, board independence
- Related-party transactions, disclosure quality

---

## Market Research Framework

### 1. News & Event Collection

#### 1.1 Company-Level News
- **Earnings**: Preliminary results, formal reports, earnings call highlights
- **Material Events**: M&A, equity offerings, buybacks, share pledges, equity incentives
- **Operations**: Major contracts, new products, capacity changes, strategic partnerships
- **Risk Events**: Litigation, regulatory penalties, investigations, credit rating changes

#### 1.2 Industry-Level News
- **Policy**: Industry policy, subsidies, regulation, environmental
- **Events**: Industry conferences, tech breakthroughs, supply-demand shifts, price changes
- **Competition**: Competitor moves, new entrants, industry consolidation

#### 1.3 Macro-Level News
- **Economic Data**: GDP, PMI, CPI, PPI, credit data, trade data, employment
- **Policy**: Monetary (rates/RRR), fiscal (tax/infrastructure), regulatory
- **International**: Trade relations, FX changes, geopolitics, overseas market linkage

### 2. Fund Flow Analysis

#### 2.1 Institutional/Smart Money

| Timeframe | Net Inflow | Trend | Interpretation |
|-----------|-----------|-------|----------------|
| 1-Day | | | |
| 5-Day | | | |
| 20-Day | | | |

- Large order transaction proportion
- Accumulation/distribution signals
- Estimated institutional cost basis

#### 2.2 Foreign Capital / Northbound Capital (A-shares)

| Timeframe | Net Inflow | Holding Changes | Interpretation |
|-----------|-----------|-----------------|----------------|

#### 2.3 Margin Trading

| Metric | Latest Value | Change | Trend |
|--------|-------------|--------|-------|
| Margin Balance | | | |
| Short Selling Balance | | | |

#### 2.4 Institutional Holdings
- Mutual fund holding changes, number of funds with heavy positions
- Social security/insurance/QFII holdings, industrial capital movements

### 3. Market Sentiment Analysis

#### 3.1 Overall Market Sentiment
- Market state: Bull/Bear/Range
- Market activity: Active/Subdued
- Fear & Greed: Extreme Fear / Fear / Neutral / Greed / Extreme Greed

#### 3.2 Individual Stock Sentiment
- Market attention level: High/Medium/Low
- Relevance to current market themes
- Public opinion tendency: Positive/Neutral/Negative

### 4. Analyst Consensus

#### 4.1 Latest Research Reports

| Institution | Date | Rating | Target Price | Core View |
|------------|------|--------|-------------|-----------|

#### 4.2 Consensus Estimates

| Metric | Consensus | Trend |
|--------|-----------|-------|
| Average Target Price | | |
| EPS Estimate | | |
| Rating Distribution | Buy x / Hold x / Sell x | |

#### 4.3 Divergence Analysis
- **Bull Case**: Core reasons for bullish view
- **Bear Case**: Core reasons for bearish view
- **Key Disagreements**: Main points of market divergence

### 5. Risk Event Monitoring

| Risk Type | Risk Item | Probability | Impact | Alert Level |
|-----------|----------|-------------|--------|-------------|
| Company Risk | | | | Red/Yellow/Green |
| Industry Risk | | | | |
| Market Risk | | | | |

---

## Report Output Template

The final report MUST follow this complete structure. All sections are mandatory. The report should be written in Chinese (中文).

```markdown
# [股票名称]（股票代码）深度投资分析报告

**报告日期**：YYYY-MM-DD
**数据截止**：YYYY-MM-DD
**分析师**：AI Investment Research Team

---

## 一、投资摘要（Executive Summary）

### 1.1 核心结论
| 维度 | 评级 | 核心观点 |
|------|------|----------|
| 基本面 | ⭐⭐⭐⭐☆ | [一句话总结] |
| 技术面 | ⭐⭐⭐⭐☆ | [一句话总结] |
| 业务面 | ⭐⭐⭐⭐☆ | [一句话总结] |
| 市场面 | ⭐⭐⭐⭐☆ | [一句话总结] |

### 1.2 投资评级
- **综合评级**：强烈推荐 / 推荐 / 中性 / 回避 / 强烈回避
- **投资周期**：短线（1-4周）/ 中线（1-6月）/ 长线（6月以上）
- **风险等级**：低风险 / 中风险 / 高风险

### 1.3 操作建议速览
| 操作类型 | 价位区间 | 仓位建议 | 执行条件 |
|----------|----------|----------|----------|
| 建仓/加仓 | xx.xx - xx.xx | xx% | [条件说明] |
| 止损 | xx.xx | 全部 | [触发条件] |
| 第一目标 | xx.xx | 减仓xx% | [达成条件] |
| 第二目标 | xx.xx | 减仓xx% | [达成条件] |

---

## 二、公司概况

### 2.1 基本信息
- **公司名称**：
- **股票代码**：
- **所属行业**：
- **市值规模**：
- **主营业务**：

### 2.2 核心竞争力
[3-5条核心竞争力说明]

---

## 三、数据深度分析

### 3.1 财务健康度分析

#### 3.1.1 资产负债分析
| 指标 | 最新值 | 同比变化 | 行业均值 | 评价 |
|------|--------|----------|----------|------|

#### 3.1.2 盈利能力分析（杜邦分析）
| 指标 | 数值 | 分解因素 | 变动原因 |
|------|------|----------|----------|

#### 3.1.3 现金流质量分析
| 指标 | 数值 | 健康度 | 关注点 |
|------|------|--------|--------|

### 3.2 估值深度分析
#### 3.2.1 相对估值
| 估值指标 | 当前值 | 5年历史分位 | 行业对比 | 结论 |
|----------|--------|-------------|----------|------|

#### 3.2.2 绝对估值参考
- DCF估值区间：xx.xx - xx.xx
- 核心假设：[假设说明]
- 安全边际：xx%

### 3.3 成长性分析
| 指标 | 近3年CAGR | 预测增速 | 增长驱动 |
|------|-----------|----------|----------|

---

## 四、技术深度分析

### 4.1 多周期趋势分析
| 周期 | 趋势方向 | 趋势强度 | 关键位置 |
|------|----------|----------|----------|
| 月线 | | | |
| 周线 | | | |
| 日线 | | | |

### 4.2 技术指标矩阵
| 指标类型 | 指标名称 | 当前状态 | 信号强度 | 信号方向 |
|----------|----------|----------|----------|----------|

### 4.3 量价关系深度分析
[详细量价分析]

### 4.4 关键价位精准测算
| 价位类型 | 价格 | 测算依据 | 可靠度 |
|----------|------|----------|--------|
| 强压力位 | | | |
| 弱压力位 | | | |
| 当前价格 | | | |
| 弱支撑位 | | | |
| 强支撑位 | | | |

### 4.5 技术面买卖点
- **最佳买入区间**：xx.xx - xx.xx
- **买入触发条件**：[具体条件]
- **止损位**：xx.xx（依据：[说明]）
- **目标位测算**：
  - 第一目标：xx.xx（涨幅xx%）
  - 第二目标：xx.xx（涨幅xx%）

---

## 五、业务深度分析

### 5.1 商业模式解析
#### 5.1.1 盈利模式
| 收入来源 | 占比 | 毛利率 | 增长趋势 | 竞争强度 |
|----------|------|--------|----------|----------|

#### 5.1.2 护城河评估
| 护城河类型 | 强度 | 可持续性 | 说明 |
|------------|------|----------|------|
| 品牌壁垒 | | | |
| 技术壁垒 | | | |
| 规模效应 | | | |
| 网络效应 | | | |
| 转换成本 | | | |

### 5.2 产业链分析
#### 5.2.1 产业链地位
[上游、中游、下游关系图谱和议价能力分析]

#### 5.2.2 供应链风险
[关键供应商、客户集中度分析]

### 5.3 竞争格局分析
| 竞争对手 | 市场份额 | 核心优势 | 威胁程度 |
|----------|----------|----------|----------|

### 5.4 增长驱动力分析
| 增长因素 | 贡献度 | 持续性 | 风险点 |
|----------|--------|--------|--------|

### 5.5 成长天花板测算
- **市场空间**：[总可寻址市场规模]
- **渗透率**：[当前渗透率及提升空间]
- **市占率提升空间**：[分析]

---

## 六、市场动态分析

### 6.1 最新重大资讯（近30天）
| 日期 | 类型 | 事件摘要 | 影响评估 | 重要性 |
|------|------|----------|----------|--------|

### 6.2 政策环境分析
[相关政策及影响]

### 6.3 资金流向分析
| 资金类型 | 近5日 | 近20日 | 趋势判断 |
|----------|-------|--------|----------|
| 主力资金 | | | |
| 北向资金 | | | |
| 融资余额 | | | |

### 6.4 机构观点汇总
| 机构 | 评级 | 目标价 | 核心观点 |
|------|------|--------|----------|

### 6.5 市场情绪指标
- **关注度**：[高/中/低]
- **情绪倾向**：[乐观/中性/悲观]
- **与大盘相关性**：[强/中/弱]

---

## 七、风险分析

### 7.1 核心风险清单
| 风险类型 | 风险描述 | 发生概率 | 影响程度 | 应对策略 |
|----------|----------|----------|----------|----------|
| 经营风险 | | | | |
| 财务风险 | | | | |
| 行业风险 | | | | |
| 政策风险 | | | | |
| 市场风险 | | | | |

### 7.2 最大风险预警
[最需要关注的1-2个核心风险详细说明]

---

## 八、综合投资建议

### 8.1 投资逻辑（核心买入/回避理由）
**看多逻辑**：
1. [逻辑1]
2. [逻辑2]
3. [逻辑3]

**潜在风险**：
1. [风险1]
2. [风险2]

### 8.2 操作策略（重点！）

#### 8.2.1 建仓策略
| 策略类型 | 适用场景 | 执行方案 |
|----------|----------|----------|
| 激进策略 | [适用情况] | 价位xx.xx，仓位xx%，止损xx.xx |
| 稳健策略 | [适用情况] | 价位xx.xx，仓位xx%，止损xx.xx |
| 保守策略 | [适用情况] | 价位xx.xx，仓位xx%，止损xx.xx |

#### 8.2.2 完整交易计划
【买入计划】
- 首次建仓：价格跌至xx.xx时，买入xx%仓位
- 加仓1：价格跌至xx.xx时，加仓xx%
- 加仓2：价格突破xx.xx确认时，加仓xx%
- 总仓位上限：xx%

【止损计划】
- 止损位：xx.xx（跌幅xx%）
- 止损条件：[具体条件]
- 止损后操作：[说明]

【止盈计划】
- 第一目标：xx.xx，减仓xx%，上移止损至xx.xx
- 第二目标：xx.xx，减仓xx%，上移止损至xx.xx
- 第三目标：xx.xx，清仓

【持仓管理】
- 持有周期预期：xx周/月
- 定期检视：每[周/月]检视一次
- 动态调整条件：[说明]

#### 8.2.3 关键监控指标
| 指标 | 当前值 | 预警阈值 | 触发动作 |
|------|--------|----------|----------|

### 8.3 情景分析
| 情景 | 概率 | 目标价 | 收益率 | 触发条件 |
|------|------|--------|--------|----------|
| 乐观情景 | xx% | xx.xx | +xx% | [条件] |
| 基准情景 | xx% | xx.xx | +xx% | [条件] |
| 悲观情景 | xx% | xx.xx | -xx% | [条件] |

---

## 九、后续跟踪要点

### 9.1 关键事件日历
| 日期 | 事件 | 预期影响 | 关注要点 |
|------|------|----------|----------|

### 9.2 持续监控清单
- [ ] [监控项1]
- [ ] [监控项2]
- [ ] [监控项3]

---

## 十、免责声明

本报告仅供参考，不构成任何投资建议。投资者应独立判断并承担投资风险。
- 股市有风险，投资需谨慎
- 历史表现不代表未来收益
- 本报告基于公开信息分析，不保证信息完整性和准确性
- 投资者应根据自身风险承受能力做出投资决策

---

**报告生成时间**：[时间戳]
**数据来源**：公开市场数据、公司公告、财经媒体
```

---

## Investment Recommendation Principles

All recommendations MUST follow these rules:

1. **Must be specific (必须具体)**: Provide exact price levels, never vague
2. **Must be actionable (必须可执行)**: Include entry price, stop-loss price, target price
3. **Must be justified (必须有依据)**: Every price level must have a stated basis
4. **Must consider risk (必须考虑风险)**: Stop-loss is mandatory for every recommendation
5. **Must be tiered (必须分层次)**: Provide aggressive/moderate/conservative strategies
6. **Must include follow-up (必须有跟踪)**: Specify indicators to monitor going forward
7. **Risk-reward priority**: Only recommend trades with risk-reward ratio > 2:1

## Common Mistakes to Avoid

1. **Incomplete data collection**: Skipping any of the data sources leads to blind spots
2. **Vague price targets**: Never say "around XX" — provide exact levels with basis
3. **Missing stop-loss**: Every buy recommendation must have a corresponding stop-loss
4. **Ignoring contradictory signals**: When fundamental and technical signals conflict, explicitly acknowledge and weigh the conflict
5. **Recency bias**: Don't overweight the most recent news; maintain perspective across all timeframes
6. **Single-dimension analysis**: Never base a recommendation on just one of the four dimensions
7. **Forgetting risk analysis**: The risk section is as important as the opportunity section
8. **No position sizing**: Always specify position percentage, not just entry price
9. **Ignoring macro context**: Individual stock analysis must consider the broader market environment
10. **Outdated information**: Always search for the most recent news and data before finalizing analysis

## Interaction Style

- Data-rich, deeply analytical, with clear conclusions (数据详实、分析深入、结论明确)
- Actionable and specific trading recommendations (操作建议具体可执行)
- Thorough risk disclosure (风险提示充分到位)
- Professional yet easy to understand (专业但易于理解)
- Use Chinese (中文) for the final report output, as the primary audience is Chinese-speaking investors
- Use tables extensively for data presentation
- Clearly separate facts from opinions/judgments
