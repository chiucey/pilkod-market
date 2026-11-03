---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 6428eba2799009379dbd7d62244e8c70
    PropagateID: 6428eba2799009379dbd7d62244e8c70
    ReservedCode1: 3044022056014f483f20214a2e9db692782cd9f440110bcf8ee57847f671174e201129f5022000db6106f15059b0e33e349289b01410463b6081ba811b5236f5180b6d573ab7
    ReservedCode2: 304502201e75cf05be4c9798b9b77645d389313af63436e44e54e188ac8a673722a6096b022100c4806047849102cf3a42deca0d0940fcb88c4f0597fb38283b2853323d1405d5
---

# Operational Analysis Skill (15 Tools · 4-Layer Framework)

> Good operational analysis doesn't make numbers more complex—it clarifies business problems and explains management actions.

---

## Core Value

This skill helps users accomplish:

1. **Operational Diagnosis**: Discover problems and identify risks from data
2. **Root Cause Analysis**: Trace from symptoms to root causes
3. **Decision Support**: Provide quantitative basis for management decisions
4. **Action Implementation**: Convert analysis conclusions into actionable management steps

---

## Master Framework: See Results → Find Causes → Drive Actions

| Layer | Core Question | Tools |
|-------|---------------|-------|
| **Layer 1: See Results** | Where is the problem? Look at trends and changes first | YoY/MoM, Trend Analysis |
| **Layer 2: See Structure** | What matters? Break down components, identify key few | Structure Analysis, Pareto Analysis, Boston Matrix |
| **Layer 3: Find Causes** | Why is this happening? Trace to factors, processes, mechanisms | Factor Decomposition, Funnel Analysis, 5Why, Fishbone |
| **Layer 4: Drive Actions** | What to do next? Focus on resources and actions | CVP Analysis, DuPont, Sensitivity, Productivity, Turnover, Cash Flow |

---

## Quick Start Examples

### Example 1: Monthly Operational Analysis Request

```
User: Help me analyze our company's March operational situation
```

**Execution Flow**:
1. Collect data: Revenue, gross profit, expenses, profit
2. Execute YoY analysis: Compare with last year's March
3. Execute MoM analysis: Compare with this year's February
4. Execute budget analysis: Compare with monthly target
5. If anomalies found, execute structural analysis
6. Trace root causes, output management action recommendations

**Output Example**:
```
## March Operational Analysis Report

### I. Key Metrics Overview
| Metric | March Actual | MoM | YoY | Budget Achievement |
|--------|-------------|-----|-----|-------------------|
| Sales Revenue | 50M | -4.6% | +12.4% | 91% |
| Gross Margin | 32.5% | -1.2% | -0.8% | 95% |
| Net Profit | 3.8M | -8.2% | +5.6% | 88% |

### II. Key Findings
1. YoY growth looks good, but MoM declined—momentum weakening
2. Gross margin under pressure, mainly due to increased low-margin product mix
3. Budget achievement below target—needs attention

### III. Recommended Actions
1. [Short-term] Strengthen high-margin product promotion, optimize product mix
2. [Medium-term] Re-evaluate pricing strategy, assess promotion intensity
3. [Long-term] Establish gross margin early warning mechanism with monthly monitoring
```

### Example 2: Business Decline Diagnosis Request

```
User: This quarter sales dropped 15%, please help analyze the reasons
```

**Execution Flow**:
1. Execute structural analysis: Break down by product/customer/region/channel
2. Execute factor decomposition: Price, volume, mix, cost contributions
3. Execute funnel analysis: If conversion stages are involved
4. Execute 5Why analysis: Trace to root causes
5. Output root cause conclusions and improvement actions

**Output Example**:
```
## Q1 Sales Decline Root Cause Analysis

### I. Structural Breakdown
| Dimension | Contribution to Decline | Key Issue |
|-----------|------------------------|-----------|
| Product | 70% | Low-margin product share increased, high-margin products declined |
| Customer | 20% | 6 of top 20 customers reduced orders |
| Region | 10% | South region declined significantly |

### II. Factor Decomposition
| Factor | Impact | Explanation |
|--------|--------|-------------|
| Price | -8% | Promotions reduced average selling price |
| Volume | -4% | Customer churn and demand decline |
| Mix | -3% | Product portfolio deteriorated |
| **Total** | **-15%** | |

### III. Root Cause Analysis (5Why Deep Dive)
- **Why1**: Why did price drop 8%? → Promotion intensity increased
- **Why2**: Why increase promotions? → Q1 customer acquisition target pressure
- **Why3**: Why so much acquisition pressure? → High churn last year, management emphasized replacement
- **Why4**: Why is考核 set this way? → Sales KPI only measures new customer count
- **Root Cause**: Sales考核 orientation mismatches profit objectives—promotions acquire customers short-term but damage margin

### IV. Recommended Actions
1. [Immediate] Stop excessive promotions, evaluate promotion ROI
2. [This Week] Adjust sales考核 scheme, add margin KPI weight
3. [This Month] Establish promotion approval mechanism with margin floor
```

---

## Layer 1: See Results

### 1. YoY, MoM, Budget Execution Analysis [Basic Tool]

**When to Use**:
- "Help me see this month's operational situation"
- "Analyze this month's performance"
- "How does it compare to last month/last year"
- "How did budget execution go"

**Core Logic**: Operational review cannot look at just one number—it requires comparison relationships.

| Dimension | Comparison | Answers |
|-----------|------------|---------|
| YoY | Same period last year | Is it better than last year? |
| MoM | Last month | Is this month improving or weakening? |
| Budget | Target | Did we achieve what we should? |

**Key Principle**: YoY shows direction, MoM shows rhythm, budget shows results. All three dimensions must be reviewed together.

**Detailed Example**:
```
Scenario: March operational data for a company

Data Background:
- Last year's March revenue: 45M
- This year's February revenue: 52M
- This year's March target: 55M
- This year's March actual: 51M

Analysis Execution:
1. YoY: 51/45-1 = +13.3% (good growth)
2. MoM: 51/52-1 = -1.9% (slight decline)
3. Budget achievement: 51/55 = 92.7% (missed target)

Conclusion:
Surface view: YoY growth looks good
Actual findings:
- MoM decline indicates weakening momentum
- Budget miss indicates target management issue
- Need further structural analysis for specific causes
```

### 2. Trend Analysis [Decision Tool]

**When to Use**:
- "See the trend over the past few months"
- "Analyze performance trends"
- "Is this short-term volatility or long-term problem"
- "When did things start going wrong"

**Core Logic**: Many problems don't happen suddenly this month—they've been developing for several months.

**Analysis Points**:
- **Direction**: Overall improving, weakening, or flat
- **Rhythm**: One-time fluctuation or continuous change
- **Inflection Points**: When did improvement or decline start

**Key Principle**: Single month shows results, trends reveal truth. Longer time windows show true direction.

**Detailed Example**:
```
Scenario: 6-month revenue data for a company

Month    Revenue(M)  MoM     Trend
Jan      48.0        -       Flat
Feb      51.0       +6.3%    Improving
Mar      49.5       -2.9%   Pullback
Apr      52.0       +5.1%    Improving
May      51.5       -1.0%    Slight decline
Jun      50.0       -2.9%    Clear decline

Trend Analysis:
1. Direction: Overall fluctuating around 50M, no clear trend yet
2. Rhythm: Occasional fluctuations, but May-June consecutive decline needs attention
3. Inflection Point: June shows declining signal
4. Risk Alert: If July continues declining, launch problem diagnosis
5. Recommendation: Monitor July data closely, set early warning
```

---

## Layer 2: See Structure

### 3. Structural Analysis [Basic Tool]

**When to Use**:
- "Total looks fine but something feels wrong"
- "Help me break down the composition"
- "How are products/customers/regions performing"
- "Where is the money mainly going"

**Core Logic**: Many operational problems aren't in the total—they're in the composition.

**Four Structural Dimensions**:

| Dimension | Focus | Warning Signals |
|-----------|-------|----------------|
| Revenue Structure | Product/customer/region/channel mix | High-margin source share declining |
| Expense Structure | Marketing/G&A/R&D/HR | Abnormal growth in certain expense categories |
| Cost Structure | Material/labor/manufacturing/logistics | Cost composition changing |
| Profit Structure | Which products/customers/regions dragging down | Loss items share expanding |

**Key Principle**: Totals show surface, structure reveals truth.

**Detailed Example**:
```
Scenario: Two months both have 50M revenue, need to assess profit quality

January Revenue Structure:
- Product A (High margin 35%): 30M (60%)
- Product B (Medium margin 20%): 15M (30%)
- Product C (Low margin 8%): 5M (10%)
- Weighted gross margin: 27.4%

February Revenue Structure:
- Product A (High margin 35%): 15M (30%)
- Product B (Medium margin 20%): 20M (40%)
- Product C (Low margin 8%): 15M (30%)
- Weighted gross margin: 21.7%

Conclusion:
- Both months have same revenue, but January has much better profit quality
- February's low-margin product share increase is a danger signal
- Need further analysis: Customer requirements? Competitive pressure? Product mix strategy mistake?
```

### 4. Pareto Analysis (80/20 Rule) [Decision Tool]

**When to Use**:
- "Which customers/products are most important"
- "Where should resources be invested"
- "What are the highest priorities"
- "How to focus on what matters"

**Core Logic**: Operational analysis fears spreading efforts thin—true effectiveness comes from focusing on key items first.

**Application Scenarios**:

| Application | Purpose | Typical Questions |
|-------------|---------|-------------------|
| Product Pareto | Identify core products | Which products contribute 80% revenue/profit |
| Customer Pareto | Identify high-value customers | Which customers need priority maintenance |
| Problem Pareto | Identify critical issues | Which problems cause 80% of losses |
| Region Pareto | Identify priority regions | Which regions need more investment |

**Key Principle**: The top 20% of key items contribute 80% of results. Focus on the vital few first—management actions become more effective.

**Detailed Example**:
```
Scenario: A company has 120 customers, needs to identify priority customers

Data Collection:
Customer  Revenue(M)  Share  Cumulative  Classification
K001      8.5        18.5%  18.5%       ★ Core
K002      6.2        13.5%  32.0%       ★ Core
K003      4.8        10.4%  42.4%       ★ Core
K004      3.5        7.6%   50.0%       Key
K005      2.8        6.1%   56.1%       Key
...
(Skip middle customers)
K018      1.2        2.6%   76.2%       Key
...
K120      0.25       0.5%   100%        General

Pareto Analysis Conclusion:
1. Top 18 customers (15%) contribute 76.2% of revenue
2. Top 3 customers (2.5%) contribute 42.4% of revenue
3. Bottom 50 customers (42%) only contribute 5.3% of revenue

Management Action Recommendations:
- [High Priority] Focus resources on top 18 core customers
- [Evaluate] Assess maintenance cost vs. revenue for bottom 50
- [Strategy] Develop specialized service plans for top 3 mega customers
```

### 5. Boston Matrix [Decision Tool]

**When to Use**:
- "How are different business units performing"
- "How should resources be allocated"
- "Which businesses to invest more or less"
- "Is our business portfolio healthy"

**Core Logic**: Not all businesses deserve equal investment—resources should go where they're most valuable.

| Quadrant | Characteristics | Management Action |
|----------|----------------|------------------|
| **Star** | High growth, high contribution | Accelerate: Continue investing, capture share |
| **Cash Cow** | Slow growth, but steady profit | Maintain: Preserve profit and cash, improve efficiency |
| **Question Mark** | Potential, unstable results | Verify: Set milestones, monitor conversion, limit time |
| **Dog** | Slow growth, low contribution | Reduce: Assess synergy value, exit or integrate if none |

**Key Principle**: Boston Matrix's value isn't classification—it's resource allocation decisions.

**Detailed Example**:
```
Scenario: A company has 4 product lines, needs resource allocation strategy

Product Line Data:
Line    Market Share  Growth Rate  Margin  Profit Contribution
A       25%          35%          28%     8M
B       40%          8%           35%     12M
C       15%          28%          18%     3M
D       8%           5%           5%      0.5M

Boston Matrix Positioning:
        High Growth
           ↑
    Question    Star
      (C)       (A)
           |
Low Share←----→High Share
           |
       Dog     Cash Cow
        (D)      (B)

Resource Allocation Recommendations:

| Line | Position | Strategy | Specific Actions |
|------|----------|----------|------------------|
| A | Star | Accelerate | Increase R&D investment, expand capacity, target 35% share next year |
| B | Cash Cow | Maintain | Maintain current investment, harvest profit, optimize operations |
| C | Question | Verify | 6-month observation period, shrink if no margin improvement |
| D | Dog | Reduce | Assess synergy value, phase out if none, free up resources |
```

---

## Layer 3: Find Causes

### 6. Factor Decomposition Analysis [Decision Tool]

**When to Use**:
- "Why did gross margin decline"
- "What caused revenue increase/decrease"
- "Help me decompose profit changes"
- "How much impact from price, volume, and mix each"

**Core Logic**: Operational analysis can't just say results changed—it must explain WHY they changed.

**Four Major Factors**:

| Factor | Expression | Focus |
|--------|-----------|-------|
| Price | Selling higher or lower | Impact of price increases, decreases, discounts, promotions |
| Volume | Selling more or less | Demand changes vs. execution changes |
| Mix | High-margin product share changed | Product/customer/channel/region mix changes |
| Cost | Material, labor, logistics changed | Unit cost and cost composition changes |

**Key Principle**: Without decomposition, you only say "margin declined"; with decomposition, you know if the problem is price erosion, mix deterioration, or cost increase.

**Detailed Example**:
```
Scenario: A company's gross margin dropped from 28.6% to 25.8%, need to find why

Factor Decomposition Calculation:
Margin change = Reporting period - Base period = 25.8% - 28.6% = -2.8%

Factor Contribution Breakdown:
Factor      Impact     Explanation
Price       -1.2%      Promotions reduced average price by 0.8/unit
Mix         -0.9%      High-margin product share dropped from 52% to 45%
Cost        -1.1%      Raw material price increase raised unit cost by 0.6
Volume      +0.4%      Volume growth partially offset margin loss
Total       -2.8%

Root Cause Follow-up:
1. Price factor -1.2%: Why such aggressive promotions?
   → Sales team透支 margin to meet quarterly targets

2. Mix factor -0.9%: Why did high-margin product share drop?
   → Large customers demanded more low-end products, mix passively lowered

3. Cost factor -1.1%: Can cost increase be passed on?
   → Competition fierce, dare not raise prices, absorbed internally

Management Actions:
1. Re-evaluate promotion strategy, set margin floor
2. Renegotiate with major customers, optimize product mix
3. Find alternative raw materials, reduce cost dependency
```

### 7. Funnel Analysis [Operational Tool]

**When to Use**:
- "Why is conversion rate so low"
- "Where are customers dropping off"
- "Which stage of the sales funnel has problems"
- "How to improve customer acquisition efficiency"

**Core Logic**: Many poor results aren't from lack of effort at the end—it's because something leaked badly in the middle.

**Analysis Points**:
- **Top of Funnel**: Sufficient leads, prospects, touchpoints determine if there's something to convert
- **Leakage Points**: Which stage loses the most—that's the priority improvement area
- **Conversion**: Not every stage needs simultaneous improvement—focus on the key bottleneck

**Key Principle**: Funnel analysis value isn't seeing the endpoint—it's finding which stage is leaking.

**Detailed Example**:
```
Scenario: Sales funnel analysis for a company

Funnel Data:
Stage              Total   Current  Prior   Change   Drop-off Rate
Lead Generation    1,200   1,200    1,100   +9.1%    -
Lead → Opportunity 420     420      400     +5.0%    65.0%
Opp → Quote         180     180      190     -5.3%    57.1%
Quote → Negotiation  96      96      105     -8.6%    46.7%
Negotiation → Close  38      38       42     -9.5%    60.4%

Overall conversion rate: 3.2% (Prior: 3.8%)

Stage-by-Stage Analysis:
1. Top of funnel (Lead Gen): Good growth, lead quality not an issue
2. Lead → Opportunity: 65% drop-off, normal for industry, no improvement needed
3. Opportunity → Quote: 57.1% drop-off, slightly above normal (50%), monitor
4. Quote → Negotiation: 46.7% drop-off, clearly above normal (30-40%), KEY IMPROVEMENT NEEDED
5. Negotiation → Close: 60.4% drop-off, above normal, need negotiation skill improvement

Key Finding:
Quote to Negotiation stage has serious leakage (57.1%)—this is the biggest bottleneck

Root Cause Analysis:
- Long customer response time after quoting
- High competitive pricing transparency, customers comparison shop
- Sales lacks value presentation skills

Management Actions:
1. [Immediate] Optimize quote template, add differentiated value presentation
2. [This Week] Establish 48-hour follow-up mechanism after quoting
3. [This Month] Conduct value selling training for sales team
4. [Long-term] Build competitive comparison analysis tool
```

### 8. 5Why Analysis [Decision Tool]

**When to Use**:
- "What is the root cause"
- "Why did this problem happen"
- "Please help me analyze deeply"
- "Can't find the root cause no matter how much I look"

**Core Logic**: Many operational problems aren't invisible—they just haven't been traced deeply enough.

**Analysis Steps** (Complete Example):
```
Problem Statement: A company's sales declined for 3 consecutive months

Why1: Which customers reduced orders?
→ Key customers (annual purchase > 5M) had 8 accounts with reduced orders

Why2: Why did these customers reduce?
→ 5 of them said they switched to competitors

Why3: Why did customers switch to competitors?
→ Competitor launched new products with better performance at similar price

Why4: Why don't we have similar products?
→ R&D cycle long, new product launch 6 months behind competitor

Why5: Why is R&D cycle so long?
→ R&D process executes serially, long wait times between departments

Root Cause: Product planning disconnected from market demand, slow R&D response

Further Follow-up (Optional Why6):
Why6: Why is product planning disconnected from market?
→ Missing market intelligence collection mechanism, sales feedback chain too long

Root Cause (Deeper): Market-to-R&D transmission mechanism malfunctioned
```

**Key Principles**:
- Don't stop at "results are bad"—find direct cause first, then dig deeper
- Many problems ultimately trace to mechanisms, coordination, KPIs, processes
- Focus isn't finding who to blame—it's finding the true root cause
- Superficial causes lead to superficial actions; accurate root causes lead to effective improvements

### 9. Fishbone Diagram Analysis [Knowledge Card]

**When to Use**:
- "Help me analyze this problem systematically"
- "What are the possible causes"
- "Get all departments involved in analysis"
- "Comprehensively map out influencing factors"

**Core Logic**: Complex problems fear arbitrary judgment—fishbone diagram's value is systematically laying out all causes.

**Analysis Dimensions**: People, Process, Product, Price, Cost, Data & Mechanisms

**Analysis Template**:
```
                    Problem: Gross Margin Decline
                          ↑
    ┌───────┬───────┬───────┬───────┬───────┬───────┐
    ↓       ↓       ↓       ↓       ↓       ↓
   People  Process Product  Price   Cost   Mechanism

People: Sales skills insufficient, product knowledge lacking, incentive misalignment
Process: Slow order processing, long delivery cycles, quality issues
Product: Slow new product development, competitive substitutes, poor mix
Price: Excessive promotions, uncontrolled discounts, missing pricing strategy
Cost: Raw material price increases, labor cost increases, low efficiency
Mechanism: KPIs measure revenue only, missing margin KPIs, coordination failure
```

**Detailed Example**:
```
Scenario: A company's gross margin declined for 2 consecutive months

Fishbone Analysis (Complete):

Problem: Gross margin dropped from 28% to 24%

├── People
│   ├── Sales team: Overused discounts to hit targets
│   ├── Product managers: Lacked control over low-margin products
│   └── Customer service: Didn't effectively block discount requests
│
├── Process
│   ├── Pricing process: Discount approval authority too broad
│   ├── Product switching: Lacked margin assessment step
│   └── Promotion process: Launched promotions without CVP analysis
│
├── Product
│   ├── Product A: Forced to cut price to compete
│   ├── Product B: End of product lifecycle, actively discounting inventory
│   └── New products: Launched with low initial pricing
│
├── Price
│   ├── Competitor price war: Forced to follow price cuts
│   ├── Discount policy: Too aggressive, lacking control
│   └── Customer bargaining: Major customers have strong negotiating power
│
├── Cost
│   ├── Raw material price increase: Cost up, didn't adjust selling price timely
│   ├── Production efficiency: Yield rate declined
│   └── Logistics cost: Freight rates increased
│
└── Mechanism
    ├── Sales KPI: Only measures revenue, not margin
    ├── Product KPI: Missing margin achievement assessment
    └── Promotion approval: Missing margin floor requirement

Root Cause Identification:
After weighted assessment, biggest impact factors:
1. [Primary] Sales KPI only measures revenue, not margin (contributes 40%)
2. [Secondary] Promotion policy lacks margin floor control (contributes 30%)
3. [Secondary] Competitor price war forced price cuts (contributes 20%)
```

---

## Layer 4: Drive Actions

### 10. Cost-Volume-Profit (CVP) Analysis [Basic Tool]

**When to Use**:
- "Can we lower this price"
- "Is accepting this order worthwhile"
- "How much do we need to sell to break even"
- "How much profit will this promotion bring"

**Core Logic**: Many seemingly positive operational actions need one question first—after doing this, will we really be more profitable?

**Three Core Applications**:

| Application | Formula | Description |
|-------------|---------|-------------|
| Break-even point | Break-even volume = Fixed cost / Unit contribution margin | Calculate minimum sales to avoid loss |
| Contribution margin | CM = Selling price - Variable cost | See how much each additional unit earns |
| Target profit | Target volume = (Fixed cost + Target profit) / Unit CM | Calculate sales needed for target profit |

**Key Principle**: Many promotion action problems aren't about not being able to sell—it's that even if you sell, you may not be more profitable.

**Detailed Example**:
```
Scenario: Product pricing decision analysis

Product Data:
- Current price: 120/unit
- Variable cost: 72/unit
- Fixed cost: 4.8M/month
- Current volume: 150K units/month
- Current CM: 120-72 = 48/unit

Current Operational Status:
- Monthly CM: 48 × 150 = 7.2M
- Monthly profit: 7.2 - 4.8 = 2.4M
- Break-even: 4.8 / 48 = 100K units

Scenario 1: Impact of 10% price reduction
- New price: 108/unit
- New CM: 108 - 72 = 36/unit
- New break-even: 4.8 / 36 = 133K units
- To maintain 2.4M profit: 7.2 / 36 = 200K units
- Conclusion: After 10% reduction, need 33% volume growth to maintain profit—extremely risky

Scenario 2: Sensitivity of 3% price reduction
- New price: 116.4/unit
- New CM: 116.4 - 72 = 44.4/unit
- New break-even: 4.8 / 44.4 = 108K units
- To maintain 2.4M profit: 7.2 / 44.4 = 162K units
- Conclusion: 3% reduction is acceptable range, but need >10% volume growth assurance

Management Actions:
1. Establish pricing strategy, clarify discount authority and floor
2. All promotions must complete CVP analysis before launching
3. Set gross margin early warning line—promotions prohibited below 28%
```

### 11. DuPont Analysis [Operational Tool]

**When to Use**:
- "Why is ROE high/low"
- "How is profitability really"
- "What's the quality of returns"
- "Which matters more: profit margin or turnover"

**Core Logic**: Same high returns can come from high profit margin, high turnover, or high leverage—management implications are completely different.

**Formula**: ROE = Net margin × Asset turnover × Equity multiplier

| Metric | Meaning | Focus |
|--------|---------|-------|
| Net margin | How much profit stays from each revenue dollar | Selling price, margin, expense control |
| Asset turnover | How fast assets are working | Inventory turnover, AR turnover, asset efficiency |
| Equity multiplier | How much leverage is used | Whether debt usage is reasonable, whether risk is proportionally magnified |

**Detailed Example**:
```
Scenario: Compare ROE composition of two companies

Company A vs. Company B (Both have 18% ROE)

Company A:
- Net margin: 15% (High)
- Asset turnover: 0.9x (Normal)
- Equity multiplier: 1.33 (Low leverage)
- ROE = 15% × 0.9 × 1.33 = 18%

Company B:
- Net margin: 8% (Normal)
- Asset turnover: 1.8x (Fast)
- Equity multiplier: 1.40 (High leverage)
- ROE = 8% × 1.8 × 1.4 = 18%

Operational Quality Assessment:

Dimension        Company A    Company B    Conclusion
Profitability    ★★★★★      ★★★☆☆       A is stronger
Operational eff  ★★★☆☆      ★★★★★       B is stronger
Risk level       ★★★★★      ★★★☆☆       A is more stable
Sustainability   ★★★★☆      ★★★☆☆       A is better

Management Recommendations:
Company A: Maintain current strategy, focus on efficiency improvement
Company B: Beware of high leverage risk, improve net margin
```

### 12. Sensitivity Analysis [Decision Tool]

**When to Use**:
- "How big is the risk in this decision"
- "What if sales decline"
- "What's the worst-case scenario"
- "How much safety margin is needed"

**Core Logic**: Truly stable operational decisions aren't made by intuition—they're made by first looking at results after variable fluctuations.

**Three Core Applications**:

| Application | Description |
|-------------|-------------|
| Find most sensitive variables | Not all variables are equally important—find what impacts profit/cash flow most |
| Stress testing | Don't just look at normal scenarios—test if the floor can hold up under sales decline or cost increase |
| Pre-plan responses | Know where the floor is, set early warning lines and response actions in advance |

**Detailed Example**:
```
Scenario: Annual budget sensitivity analysis

Budget Baseline:
- Projected volume: 500K units
- Selling price: 100/unit
- Unit cost: 65/unit
- Fixed cost: 12M
- Projected net profit: 5.5M

Variable Fluctuation Sensitivity Matrix:

              Change %
Variable      -20%    -10%   Base    +10%   +20%
-------------------------------------------------
Volume (K)    400     450    500     550    600
Profit (M)    0.9     3.2    5.5     7.8    10.1
Change         -4.6   -2.3   0      +2.3   +4.6

Price       80     90    100    110    120
Profit (M)  -2.5   1.5    5.5    9.5   13.5
Change      -8.0   -4.0   0      +4.0   +8.0

Unit Cost   85     75    65     55     45
Profit (M)  1.5    3.5    5.5    7.5    9.5
Change      -4.0   -2.0   0      +2.0   +4.0

Key Findings:
1. Price is most sensitive variable: every 10% price drop reduces profit by 2.3M
2. Break-even point: Loss occurs if price drops below 68
3. Safety margin: Current margin can withstand 15% price drop

Early Warning Mechanism Design:
- Yellow alert: Price drops 5% or volume drops 10%
- Orange alert: Price drops 10% or volume drops 15%
- Red alert: Price drops 15% or volume drops 20%

Management Actions:
1. Establish pricing adjustment approval authority—>5% requires VP approval
2. Build monthly sensitivity monitoring dashboard
3. Develop price protection agreements with key customers
```

### 13. Productivity Analysis [Decision Tool]

**When to Use**:
- "How's productivity"
- "Is headcount appropriate"
- "Should we hire more people"
- "How's organizational efficiency"
- "Is labor cost ratio high"

**Core Logic**: Low productivity isn't necessarily because labor is expensive—often it's because organizational input is disconnected from business output.

**Analysis Points**:

| Dimension | Metrics | Focus |
|-----------|---------|-------|
| Per capita output | Revenue per person, profit per person | Can't just look at headcount and labor cost |
| Input matching | Headcount growth vs. revenue growth | Headcount growing faster than business is a danger signal |
| Organizational structure | Back-office vs. front-line ratio | Productivity problems often stem from structural imbalance |

**Detailed Example**:
```
Scenario: Annual productivity analysis for a company

Baseline Comparison:
Metric                  Prior Year   Current   Change
Headcount               210         248       +18%
Labor cost (M)          21          27.3      +30%
Revenue (M)            150         159       +6%
Gross profit (M)        42          43.3      +3%

Productivity Metrics:
Metric                  Prior Year   Current   Change
Revenue per person (K)  714         641       -10.2%
Profit per person (K)   200         174       -13.0%
Margin per person (K)   71          48        -32.4%
Labor cost ratio        14.0%       17.2%     +3.2pp

Headcount Structure Analysis:
Category        Count   %       Output     Assessment
Front-line      80      32%     19.8M      Normal
Production      70      28%     -          Needs review
Tech support    30      12%     -          Needs review
Back-office     68      28%     -          High

Problem Diagnosis:
1. [Primary] Headcount up 18%, revenue up 6%—productivity severely declined
2. [Structural] Back-office at 28% is clearly high—input/output ratio imbalanced
3. [Cost] Labor cost ratio increased from 14% to 17.2%—profit being eroded

Management Actions:
1. [Freeze] Freeze all non-frontline hiring
2. [Review] Conduct workload assessment for back-office positions
3. [Optimize] Target back-office ratio down to 22%
4. [Monitor] Build monthly productivity dashboard with early warning
```

### 14. Turnover Analysis [Operational Tool]

**When to Use**:
- "How's cash turnover"
- "Is there inventory buildup"
- "Are collection periods long"
- "Where is cash being tied up"
- "Why is cash tight despite good profit"

**Core Logic**: Much operational pressure isn't insufficient profit—it's imbalance in inventory, AR, and AP cycles. Profit shows if you're making money; turnover shows if cash is flowing fast.

**Cash Conversion Cycle** = Inventory days + AR days - AP days

| Dimension | Meaning | Focus |
|-----------|---------|-------|
| Inventory turnover | Slow inventory turns, cash tied in warehouse | Overstocking, structural imbalance, slow-moving goods increasing |
| AR turnover | Revenue recognized doesn't mean cash received | Extended payment terms, delayed collection, key customer credit |
| AP turnover | Both buffer and potential pressure | Healthy payment rhythm, whether being delayed |

**Detailed Example**:
```
Scenario: Capital situation analysis for a company

Baseline Data:
Metric                      Prior Year   Current   Industry Avg
Inventory days              52 days      68 days   45 days
AR days                     31 days      42 days   35 days
AP days                     40 days      38 days   42 days
Cash conversion cycle        43 days      72 days   38 days

Problem Identification:
1. Inventory days +16 days → Inventory pressure clearly rising
2. AR days +11 days → Collection slowing down
3. AP days -2 days → Payment pressure not relieved
4. Cash conversion cycle +29 days → Capital efficiency significantly declined

Deep Dive Analysis:

Inventory Issues:
- Overall inventory up 35%
- Slow-moving inventory up 80%
- Mix: Old products share rising, new products slow to sell

AR Issues:
- Customers with >90 day terms increased from 3 to 8
- Key customer payment terms extended
- Some disputed amounts exist

Management Actions:
1. [Immediate] Launch slow-moving inventory clearance, target 50% reduction in 3 months
2. [This Week] Visit customers with >90 day terms, develop collection plan
3. [This Month] Optimize procurement planning, reduce unnecessary stocking
4. [Long-term] Establish customer credit management system with payment term red lines
```

### 15. Cash Flow Analysis [Basic Tool]

**When to Use**:
- "How's cash flow"
- "Is there cash on hand"
- "Why is cash flow poor despite good profit"
- "How long can we survive"
- "What's the operational quality"

**Core Logic**: Many companies' problems aren't inability to make profit—it's that profit isn't converting to cash in a timely manner.

**Analysis Points**:

| Dimension | Focus |
|-----------|-------|
| Profit-cash alignment | Good profit doesn't mean good cash flow—key is whether net profit and operating cash flow move together |
| Capital deployment analysis | Much cash pressure isn't from losses—it's cash being tied up in AR, inventory, prepayments |
| Cash source health | Operating cash flow is the most solid cash—key is whether company survives on operating collections or borrowing |

**Detailed Example**:
```
Scenario: Profit vs. cash flow divergence analysis

Profit Statement vs. Cash Flow Statement:
Metric                  YoY Change   Assessment
Net profit              +15%         Good ↑
Operating cash flow     -8%          Poor ↓
Net profit cash content  0.65         Below 1

Cash Flow Quality Diagnosis:
Item                    Change (M)  Explanation
Net profit increase     +1.5        Book profit growth
AR increase             +1.8         Customer credit extended
Inventory increase      +2.4        Inventory buildup
Prepayments increase    +0.8        Advanced payments to suppliers
AP increase             +0.6        Normal fluctuation

Operating cash flow change = 1.5 - 1.8 - 2.4 - 0.8 + 0.6 = -2.9M

Problem Classification:
- Profit grew, but cash was eaten by AR and inventory
- This is a "paper wealth" type company
- If this continues, faces cash flow chain rupture risk

Cash Flow Rupture Risk Assessment:
- Current cash on hand: 5M
- Monthly fixed expenses: 2M (labor + rent + interest)
- Survival months: 5/2 = 2.5 months
- Risk level: HIGH

Management Actions:
1. [Immediate] Launch AR collection, target 3M collection this month
2. [This Week] Evaluate inventory liquidation possibility
3. [This Month] Negotiate with banks for credit lines, reserve liquidity
4. [Long-term] Add cash flow to KPIs with equal weight to profit
```

---

## Tool Selection Quick Reference

| Problem You Want to Solve | Recommended Tools |
|---------------------------|-------------------|
| How was this month's operation? | YoY/MoM + Trend Analysis |
| Total looks fine but feels wrong? | Structure Analysis |
| How to allocate resources? | Pareto Analysis + Boston Matrix |
| Why did the result change? | Factor Decomposition |
| Which stage is leaking? | Funnel Analysis |
| What is the root cause? | 5Why Analysis + Fishbone |
| Is this decision worthwhile? | CVP Analysis + Sensitivity Analysis |
| What's the quality of returns? | DuPont Analysis |
| Is headcount sufficient? | Productivity Analysis |
| Why cash tight despite good profit? | Turnover Analysis + Cash Flow Analysis |

---

## Five Iron Rules (Must Follow Every Analysis)

1. **Never look at just one number** — Review YoY, MoM, and budget all together
2. **Never stop at surface symptoms** — Always drill down to root cause (5Why)
3. **Every analysis must produce actions** — Operational analysis without management actions equals no analysis
4. **Totals only show surface** — Structural breakdown reveals truth
5. **Profit is the result, cash is survival** — Cash flow health is true health

---

## Common Analysis Scenario Templates

### Scenario 1: Monthly Operational Review

```
Input: Monthly data (revenue, cost, expenses, profit)
Output:
1. YoY/MoM/Budget three-dimension analysis
2. Key metric achievement assessment
3. Priority problem identification
4. Next month action recommendations
```

### Scenario 2: Business Decline Diagnosis

```
Input: Decline metric + relevant dimension data
Output:
1. Structural positioning (where is decline)
2. Factor decomposition (why decline)
3. Root cause follow-up (deepest reason)
4. Improvement actions (specific steps)
```

### Scenario 3: Management Decision Evaluation

```
Input: Proposed decision + relevant data
Output:
1. CVP calculation
2. Sensitivity analysis
3. Risk assessment
4. Recommendations
```

---

_This document will continuously evolve. Each new operational analysis scenario encountered will add corresponding cases and tool combinations._
