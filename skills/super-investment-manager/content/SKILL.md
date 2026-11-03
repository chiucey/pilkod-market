---
name: super-investment-manager
description: Super Investment Manager - Professional investment analysis skill based on the 7-step Danbin investment advisor method. Use when users request stock analysis, investment advisory, company valuation, investment target selection, portfolio construction, market bull/bear analysis, industry trend analysis, financial statement analysis, PEG valuation, competitive advantage analysis, or position-building timing assessment. Trigger phrases: investment analysis, stock selection, valuation analysis, market analysis, bull/bear judgment, industry analysis, financial statements, PEG calculation, position-building timing.
---

# Super Investment Manager

An intelligent investment analysis system based on the 7-step Danbin investment advisor method. Execute the investment analysis process strictly following these steps.

## Core Workflow

### Step 1: Market Bull/Bear Analysis

**Objective**: Determine current market bull/bear status and provide daily market recommendations

**Execution Steps**:
1. Use `mcp__matrix__batch_web_search` to search for latest quotes of A-share/H-share/US stock major indices
2. Search analyst market views and trend judgments
3. Collect macroeconomic data (GDP, CPI, interest rates, etc.)
4. Analyze market sentiment indicators

**Output Format**:
```markdown
## Market Analysis Report

### Current Market Status
- Shanghai Composite: [level] [change%]
- Shenzhen Component: [level] [change%]
- ChiNext Index: [level] [change%]
- CSI 300: [level] [change%]

### Technical Analysis
[MA system, candlestick patterns, volume analysis]

### Macro Analysis
[Economic data, policy direction, capital flows]

### Bull/Bear Judgment
[ ] Early Bull  [ ] Mid Bull  [ ] Late Bull  [ ] Early Bear  [ ] Mid Bear  [ ] Late Bear

### Daily Market Recommendation
- Position Recommendation: [Conservative/Neutral/Aggressive]
- Action Recommendation: [Build/Observe/Reduce]
- Risk Alert: [Key risk factors]
```

---

### Step 2: Industry Dividend Period Analysis

**Objective**: Identify industries in the era of dividend period

**Execution Steps**:
1. Use `mcp__matrix__batch_web_search` to search "14th Five-Year Plan", "Industrial Policy", "Tech Trends"
2. Search keywords like "Platform Enterprises", "AI", "New Energy", "Semiconductors"
3. Analyze policy support for each industry
4. Assess industry life cycle stage

**Current Era Dividend Industries (2024-2026)**:
| Industry | Dividend Type | Driving Factors | Representative Companies |
|----------|---------------|----------------|-------------------------|
| Platform+AI | Platform+Tech Dividend | Traffic aggregation+LLM applications | Alibaba, Tencent, Baidu |
| New Energy Vehicles | Policy+Market Dividend | Carbon neutrality+Penetration rate increase | BYD, CATL |
| Semiconductors | Localization Dividend | Tech blockade+Self-controllability | SMIC, Cambricon |
| Innovative Drugs | Demographics Dividend | Demand surge+Faster approval | BeiGene, Hengrui |

**Output Format**:
```markdown
## Industry Dividend Period Analysis

### Current Era Background
[Macroeconomic environment analysis]

### Core Dividend Industries
1. **[Industry Name]**
   - Dividend Type: [Platform/Tech/Policy/Market/Demographic]
   - Driving Factors: [Specific factors]
   - Policy Support: [Relevant policies]
   - Industry Scale: [Market size forecast]
   - Investment Logic: [Core investment rationale]

### Recommended Industries
- First Tier: [Industry 1], [Industry 2]
- Second Tier: [Industry 3], [Industry 4]
```

---

### Step 3: High-Growth Company Screening

**Objective**: Find high-growth companies in early growth-stage industries, download and analyze financial statements

**Execution Steps**:
1. **Industry Screening**: Use `mcp__matrix__batch_web_search` to search "Industry Life Cycle", "Growth-stage Industries"
2. **Company Search**: Search for high-growth businesses in target industries
3. **Financial Report Download**:
   - Visit company official websites (e.g., `investor.xxx.com`)
   - Use `mcp__matrix__extract_content_from_websites` to extract financial data
   - Or use `mcp__matrix__batch_web_search` to search "[Company] Annual Report", "[Company] Quarterly Report"
4. **Data Organization**: Organize financial report data into standard format

**Financial Statement Key Metrics**:
| Metric Category | Core Metrics |
|-----------------|--------------|
| Profitability | Revenue, Net Profit, Gross Margin, Net Margin |
| Growth | Revenue Growth, Net Profit Growth, Non-GAAP Net Profit |
| Financial Health | Debt-to-Asset Ratio, Cash Flow, Receivables |
| Valuation | PE, PB, PEG |

**Output Format**:
```markdown
## High-Growth Company Screening

### Target Industries
1. **[Industry Name]** - Stage: [Introduction/Growth/Mature/Decline]

### Initial Screening List
| # | Company | Ticker | Core Business | Revenue Growth | Net Profit Growth |
|---|---------|--------|---------------|----------------|-------------------|
| 1 | XXX | XXXX | XXX | XX% | XX% |
| 2 | XXX | XXXX | XXX | XX% | XX% |

### Financial Statement Analysis
#### [Company Name]
- 3-Year Revenue: [X Bn] -> [X Bn] -> [X Bn] (CAGR: XX%)
- 3-Year Net Profit: [X Bn] -> [X Bn] -> [X Bn] (CAGR: XX%)
- Non-GAAP Net Profit: [X Bn] -> [X Bn] -> [X Bn]
- Gross Margin: XX%
- Debt-to-Asset Ratio: XX%
```

---

### Step 4: PEG Valuation Calculation

**Objective**: Calculate company valuations and select reasonably valued companies

**Execution Steps**:
1. **Data Collection**:
   - Use `mcp__matrix__stocks_info` to get company basic info
   - Use `mcp__matrix__stocks_financial_data` to get financial data
   - Calculate: PE = Current Price / EPS (TTM)
2. **Profit Growth Calculation**:
   - Use `mcp__matrix__batch_web_search` to search "[Company] Non-GAAP Net Profit 3-Year"
   - Calculate 3-year minimum non-GAAP net profit growth rate
   - Value = min(This Year Growth, Last Year Growth, Year Before Last Growth)
3. **PEG Calculation**: PEG = PE / Profit Growth Rate

**Valuation Standards**:
| PEG Range | Valuation Judgment | Investment Recommendation |
|------------|-------------------|--------------------------|
| PEG < 0.5 | Extremely Undervalued | Strong Buy |
| 0.5 <= PEG < 1 | Relatively Undervalued | Consider Buying |
| 1 <= PEG < 2 | Reasonably Valued | Observe or Light Position |
| PEG >= 2 | Relatively Overvalued | Not Recommended |
| PE > 2x Profit Growth | Overvalued | Clear Position/Avoid |

**Output Format**:
```markdown
## PEG Valuation Analysis

### Valuation Screening Results
| Company | Ticker | Current PE | 3-Year Min Profit Growth | PEG | Valuation | Rating |
|---------|--------|------------|-------------------------|-----|-----------|--------|
| XXX | XXXX | XXx | XX% | X.XX | [Under/ Fair/ Over] | X/5 |

### PEG Calculation Details
#### [Company Name]
- Current Price: [X]
- P/E Ratio (PE): [X]x
- EPS: [X]
- 3-Year Non-GAAP Net Profit:
  - 2024: [X] Bn, Growth: XX%
  - 2023: [X] Bn, Growth: XX%
  - 2022: [X] Bn, Growth: XX%
- Minimum Growth Rate: XX%
- PEG = [PE] / [Growth] = X.XX

### Recommended Investments (PEG < 1)
[List of undervalued candidates]
```

---

### Step 5: Competitive Landscape & Product Analysis

**Objective**: Analyze industry competitive relationships and evaluate market prospects for new products/technologies

**Execution Steps**:
1. **Competitive Landscape Analysis**:
   - Use `mcp__matrix__batch_web_search` to search "[Industry] Competitive Landscape", "[Industry] Market Share"
   - Search "Porter Five Forces [Industry]"
2. **Product/Technology Analysis**:
   - Search "[Company] New Product", "[Company] New Technology"
   - Use `mcp__matrix__batch_web_search` to search "[Product] Launch", "[Product] Commercialization"
3. **Competitor Analysis**:
   - Search "[Competitor] [Similar Product]"
   - Compare product launch timelines across competitors
4. **Revenue Forecast**:
   - Search "[Company] Sales Data", "[Company] Revenue Forecast"
   - Estimate future revenue based on market penetration assumptions

**Porter Five Forces Framework**:
1. **Supplier Bargaining Power**: Raw material supply, core components
2. **Buyer Bargaining Power**: Customer concentration, switching costs
3. **Threat of New Entrants**: Technology barriers, capital barriers, policy barriers
4. **Threat of Substitutes**: Technology substitution, model substitution
5. **Industry Rivalry**: Competition intensity, market concentration

**Output Format**:
```markdown
## Competitive Landscape & Product Analysis

### [Company Name] - Porter Five Forces Analysis
#### Supplier Bargaining Power
[Analysis content]

#### Buyer Bargaining Power
[Analysis content]

#### Threat of New Entrants
[Analysis content]

#### Threat of Substitutes
[Analysis content]

#### Industry Rivalry
[Analysis content]

### New Product/Technology Evaluation
#### [Product Name]
- Product Stage: [R&D/Testing/Launch/Scale]
- Market Demand: [Market size estimate]
- Competition: [Competitor similar products]
- Launch Time: [Expected time]
- Estimated Revenue Contribution: [Expected revenue in X years]

### Revenue CAGR Forecast
| Time Point | Base Revenue | Conservative | Optimistic |
|------------|--------------|--------------|------------|
| 2025 | X Bn | X Bn (+XX%) | X Bn (+XX%) |
| 2026 | X Bn | X Bn (+XX%) | X Bn (+XX%) |
| 2027 | X Bn | X Bn (+XX%) | X Bn (+XX%) |

### Comprehensive Assessment
- Competitive Advantages: [Core advantages]
- Potential Risks: [Key risks]
- Future Growth Trend: [Growth expectations]
```

---

### Step 6: Fundamental Deterioration Assessment

**Objective**: Assess whether targets show fundamental deterioration signals

**Execution Steps**:
1. **Financial Warning Signals**:
   - Use `mcp__matrix__batch_web_search` to search "[Company] Financial Warning", "[Company] Guidance Cut"
   - Search "[Company] Debt Default", "[Company] Goodwill Impairment"
2. **Operational Warning Signals**:
   - Search "[Company] Executive Departure", "[Company] Major Shareholder Selling"
   - Search "[Company] Lawsuit", "[Company] Regulatory Letter"
3. **Industry Warning Signals**:
   - Search "[Industry] Overcapacity", "[Industry] Policy Change"
4. **Comprehensive Judgment**: Assess fundamental deterioration based on all signals

**Deterioration Signal Checklist**:
| Signal Type | Specific Performance | Severity |
|-------------|---------------------|----------|
| Financial | Revenue/Profit decline, Cash flow deterioration | High |
| Operational | Frequent executive turnover, Major shareholder selling | High |
| Industry | Policy shift, Demand contraction | Medium |
| Market | Intensified competition, Market share decline | Medium |

**Output Format**:
```markdown
## Fundamental Deterioration Assessment

### [Company Name]

#### Financial Health
- Revenue Trend: [Growing/Flat/Declining]
- Profit Trend: [Growing/Flat/Declining]
- Cash Flow: [Healthy/Tight]
- Debt Level: [Safe/High/Dangerous]

#### Operational Risks
- Management Changes: [Stable/Changed]
- Major Shareholder Actions: [Buying/Selling/Unchanged]
- Major Litigation: [Yes/No]

#### Industry Environment
- Policy Changes: [Favorable/Neutral/Unfavorable]
- Market Demand: [Strong/Stable/Weak]
- Competition Trend: [Improving/Worsening]

### Comprehensive Assessment
- Deterioration Signals: [Yes/No]
- Deterioration Degree: [Severe/Medium/Mild]
- Clear Position Recommendation: [Yes/No]
- Clear Position Reason: [Specific reasons]

### Final Position-Building List
[Final recommended list after fundamental deterioration screening]
```

---

### Step 7: Position-Building Timing Assessment

**Objective**: Provide position-building timing signals

**Execution Steps**:
1. **Technical Analysis**:
   - Use `mcp__matrix__stocks_price` to get K-line data
   - Analyze MA system, MACD, KDJ and other technical indicators
2. **Valuation Timing**:
   - Determine current PE historical percentile
   - Find valuation bottom areas
3. **Market Timing**:
   - Determine if market is at relative bottom
   - Find signals of market panic or excessive optimism
4. **Position-Building Signal**: Provide comprehensive position-building success/failure signals

**Position-Building Signal Standards**:
| Signal Type | Position Success | Position Failure |
|-------------|------------------|------------------|
| Technical | Above 20-day MA | Below 20-day MA |
| Valuation | PE below historical median | PE above 75th percentile |
| Volume | Breakout with volume | Decline with shrinking volume |
| Market | Market stabilized | Market broken |

**Output Format**:
```markdown
## Position-Building Timing Analysis

### [Company Name]

#### Technical Analysis
- MA System: [Bullish/Bearish/Consolidating]
- MACD: [Golden Cross/Dead Cross]
- KDJ: [Overbought/Oversold/Neutral]
- Support: [X]
- Resistance: [X]

#### Valuation Timing
- Current PE: [X]x
- Historical Percentile: [XX%]
- Valuation Rating: [Low/Mid/High]

#### Position-Building Signal
| Signal Dimension | Status | Position Signal |
|------------------|--------|-----------------|
| Technical | [Status] | [Success/Failure] |
| Valuation | [Status] | [Success/Failure] |
| Volume | [Status] | [Success/Failure] |
| Market | [Status] | [Success/Failure] |

#### Comprehensive Position Recommendation
- Position Success: [Success/Pending/Failure]
- Recommended Position: [Light/Standard/Heavy]
- Entry Price Range: [X] - [X]
- Stop Loss: [X]
```

---

## Final Output: Investment Recommendation List

### Comprehensive Investment Recommendations

```markdown
# Investment Analysis Report

## I. Market Assessment
[Step 1 Analysis Results]

## II. Industry Selection
[Step 2 Analysis Results]

## III. Company Screening
[Step 3-4 Analysis Results]

## IV. Competitive Analysis
[Step 5 Analysis Results]

## V. Risk Assessment
[Step 6 Analysis Results]

## VI. Position-Building Timing
[Step 7 Analysis Results]

## VII. Investment Recommendation List

### Recommended Buy List
| # | Company | Ticker | Rationale | Target Price | Current Price | Upside | Timing |
|---|---------|--------|-----------|--------------|---------------|--------|--------|
| 1 | XXX | XXXX | [Reason] | X | X | XX% | [Timing] |

### Watch List
| # | Company | Ticker | Watch Rationale |
|---|---------|--------|----------------|
| 1 | XXX | XXXX | [Reason] |

### Avoid List
| # | Company | Ticker | Avoid Rationale |
|---|---------|--------|----------------|
| 1 | XXX | XXXX | [Reason] |

## VIII. Risk Disclosure
[Key risk factors]
```

---

## Report Generation Capabilities

### Word Report Generation
After collecting data with `mcp__matrix__extract_content_from_websites`, call `Skill("expert-skills:minimax-docx")` to generate Word reports.

### PPT Presentation Generation
After collecting analysis data, call `Skill("expert-skills:pptx-generator")` to generate PPT presentations.

### Chart Generation
After getting historical data with `mcp__matrix__stocks_price`, use Python matplotlib to generate analysis charts.

---

## Tool Usage Priority

1. **Information Search**: `mcp__matrix__batch_web_search` > `mcp__matrix__extract_content_from_websites`
2. **Stock Data**: `mcp__matrix__stocks_info` > `mcp__matrix__stocks_financial_data` > `mcp__matrix__stocks_price`
3. **Financial Report Download**: Official website > Search engine > Data platform
4. **Report Generation**: `expert-skills:minimax-docx` or `expert-skills:pptx-generator`

---

## Quality Control Checklist

After completing each step, verify:
- [ ] Data source is reliable (Official announcements/Authoritative media)
- [ ] Calculations are accurate (PE, PEG formula verification)
- [ ] Logic is consistent (Analysis across steps not contradictory)
- [ ] Recommendations are clear (Buy/Observe/Avoid)
- [ ] Risks are fully disclosed

---

## Disclaimer

This analysis is for reference only and does not constitute investment advice. Investors should make investment decisions based on their own risk tolerance. Stock markets involve risks, investment requires caution.
