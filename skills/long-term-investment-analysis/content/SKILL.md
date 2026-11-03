---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: c1734154c111850d3be1553548cb6bae
    PropagateID: c1734154c111850d3be1553548cb6bae
    ReservedCode1: 3045022026238586fd997354f1aee0977d83a5c76be58960863a8b079db943a463111cdf02210087024a16d2b12d4b6ccd4f7abe8dde679ab1d4969caa1862654a3032ad8d62b0
    ReservedCode2: 3046022100ae45e38148b12ca94e8439574773429e17fa221f2e3f7457c8f6a55bf50cf96c022100af9c383375f03e269567233d726137a7472475baa59bddfe236f1d02d4a2d323
description: Long-term investment analysis framework. Use when users request analysis of A-share, Hong Kong, Beijing Stock Exchange, or New Third Board stocks for long-term investment value, including fundamental analysis, financial due diligence, valuation calculation, and moat assessment. Supports investment memo, analysis report, and decision assistant output formats.
name: long-term-investment-analysis
---

# Long-term Investment Analysis Framework

## Trigger Conditions

This skill is triggered when users provide a stock code/name and request analysis for **investment periods over 1 year**.

**Applicable Markets**: A-share, Hong Kong, Beijing Stock Exchange, New Third Board

**Output Formats** (user must select one):
- `Investment Memo`: ≤3 pages, core logic + non-consensus assumptions + risk points + position recommendations
- `Analysis Report`: 5-8 pages, key charts and calculation processes retained (default)
- `Decision Assistant`: 1 page, direction judgment + 3 core reasons + stop-loss price + target price only

## Pre-analysis Data Collection

Before analysis, guide users to provide the following information (required fields marked):

| Field | Required | Description |
|-------|----------|-------------|
| Stock code/name | ✓ | — |
| Market type | ✓ | A-share / Hong Kong / Beijing / New Third Board |
| Investment period | — | Default >1 year |
| Report detail level | ✓ | Choose one of three |
| Special focus | — | Optional |

## Core Workflow

### Step 1: Execute Compliance Self-Check

Before generating any analysis content, the following checks must pass:

**Phase 1: Data Baseline Verification**
- [ ] Time anchoring: Determine current date, assess annual report disclosure status
- [ ] Calibration unification: Flow indicators annualized and noted
- [ ] Market adaptation: Hong Kong/Beijing/New Third Board special attributes marked
- [ ] Delisting risk screening

**Phase 2: Process Completeness Verification**
- [ ] Anomaly check (section 6.2) executed
- [ ] Industry identification (section 4.3.3) determined
- [ ] Valuation method decision tree (section 4.3.1) executed
- [ ] Moat seven-step checklist (section 6.4) executed

**Self-check Result Output Format** (mandatory):
```markdown
> ⚠️ **Compliance Self-Check Results**
> - Passed: X/X items
> - Failed items: "none" if none
> - Data calibration: [含XXXX年报/年化方法]
> - Market adaptation: [e.g., marked for Hong Kong stocks]
> - Data degradation summary: "none" if none
> - Market environment: [🔴Systemic risk/🟡Weak market/🟢Active themes/none]
```

### Step 2: Financial Data Timeliness Confirmation

1. **Determine current time Tnow**
2. **Assess annual report disclosure status**:
   - A-share/Beijing/New Third Board: By April 30 of the following year
   - Hong Kong: By March 31 of the following year
3. **Data window selection** (dynamic 5 periods):
   - Annual report not disclosed: (Ylatest-4) to (Ylatest-1) + latest quarterly report
   - Annual report disclosed: (Ylatest-4) to Ylatest

### Step 3: Industry-Valuation Method Adaptation Decision Tree

Follow decision branches to select 2-3 most suitable methods:

```
Is the target's core value in stock assets (land reserves, fleet, pipelines)?
├─ Yes → Stock asset branch:
│      ├─ Physical assets/land reserves → NAV (preferred), P/B (alternative)
│      ├─ Pipelines/patents → DCF pipeline NPV (preferred), P/S (alternative)
│      └─ Fleet/capacity → Cycle-adjusted PE+NAV (preferred), P/B (alternative)
└─ No → Operating entity branch:
       ├─ Mature heavy assets/fixed-income-like (banks/ports) → P/B, DDM, P/CF
       ├─ User/traffic-driven (internet/SaaS) → P/S or DCF(LTV)
       ├─ Brand consumption (food & beverage/white goods) → DCF + P/E relative
       ├─ Capital/technology-driven (high-end manufacturing) → ROIC-WACC + P/B
       ├─ Strong cycle/resources (energy/coal) → Cycle-adjusted PE + NAV
       └─ High-speed growth (AI applications/startups) → PEG
```

### Step 4: Deep Financial Analysis

Execute the following steps (5-period data dimension):

1. **DuPont Analysis** (ROE decomposition)
2. **CFOR Decomposition** (cash return on operating assets)
3. **FCF conversion rate and earnings quality**
4. **FCF-ROE synergy analysis**
5. **Capital operation capability analysis**
6. **ROIC vs WACC comparison** (cycle stocks use cycle-average ROIC)
7. **PB-ROE matrix matching**
8. **Price-to-Ratio (PR) supplementary check**
9. **Margin of safety calculation** (4 calibers)
10. **Trend analysis and peer comparison**

### Step 5: Moat Seven-Step Checklist

**Mandatory execution**, terminate if Step 1 fails:

| Step | Content |
|------|---------|
| Step 1 | Hard threshold screening (ROIC>15% and >WACC) → fail = quit |
| Step 2 | Industry profit pool scan (entry threat/downstream bargaining power) |
| Step 3 | Moat source qualitative analysis (network effects/switching costs/cost advantages) |
| Step 4 | Moat trend and dynamic testing |
| Step 5 | Capital allocation and management evaluation |
| Step 6 | Valuation and margin of safety mapping |
| Step 7 | Holding period monitoring list (exit red lines) |

### Step 6: Valuation Analysis

**Data transfer**: If 6.2 triggers anomaly check, all valuation profit bases use adjusted data.

1. **Absolute valuation: Reverse DCF model**
   - Perpetual growth rate per industry anchoring rules (no arbitrary values)
   - Cycle stocks use normalized profit, perpetual growth rate = 0%
   - Output "market-implied perpetual growth rate"

2. **Relative valuation**
   - PE/PB/PS/EV/EBITDA historical ranges and industry comparison
   - PEG protection mechanism: disabled if growth rate <15%

3. **Scenario analysis**: Valuation ranges under optimistic/neutral/pessimistic assumptions

4. **Liquidity risk stress test**

### Step 7: Comprehensive Investment Recommendations

1. **Valuation price summary table**
2. **Risk assessment matrix** (including industry black swan stress tests)
3. **Operation recommendations** (including position constraint principles)
4. **Portfolio compatibility assessment**

## Market Differentiation Handling

| Dimension | A-share | Hong Kong | Beijing/New Third Board |
|-----------|---------|-----------|-------------------------|
| Accounting standards | CAS | IFRS | CAS |
| Price limit | Main ±10%, ChiNext/STAR ±20% | None | Beijing ±30%; New Third Board market-making ±50% |
| Short selling mechanism | Limited | Can short sell | Basically cannot short sell |
| Penny stock risk | Low | Requires special screening | Low |

**Hong Kong penny stock screening**: 2+ high-weight items or 3+ any-weight items → initiate deep due diligence
- 2+ consolidations/rights issues/placements in 5 years
- Related party transaction revenue >30%
- 2+ auditor changes in 3 years
- 30+ consecutive days stock price <1 HKD and market cap <500M

**New Third Board agreement transfer special handling**: Triggers simplified analysis mode
- Skip technical analysis
- Valuation only allows P/B or NAV
- Liquidity discount increased by additional 30-50%
- Must display severe liquidity risk warning at top of report

## Output Specifications

- **Format**: HTML, clear structure, sufficient data support
- **Data calibration**: All flow indicators must note annualized method
- **Risk classification**: High/Medium/Low must follow unified standards
- **Currency**: RMB for A-share/Beijing/New Third Board; HKD for Hong Kong

## Resource Index

Detailed industry analysis templates, financial calculation formulas, and stress test scenarios are in the `references/` directory.