# SCENE Methodology Reference

## Pain Point Classification System

### Revenue Impact Sorting (High to Low)

Sort all identified pain points using this hierarchy:

| Priority | Category | Description | Examples |
|----------|----------|-------------|----------|
| 1 | Direct Revenue Loss | Immediately impacts sales, pricing, or customer acquisition | Customer churn, pricing pressure, market share decline |
| 2 | Growth Bottleneck | Limits expansion into new markets or segments | Slow market entry, limited distribution, regulatory barriers |
| 3 | Operational Efficiency | Increases cost-to-serve or reduces throughput | Manual processes, system downtime, resource waste |
| 4 | Customer Experience | Indirectly affects retention and lifetime value | Slow response times, poor UX, limited self-service |
| 5 | Compliance & Risk | Potential fines or reputational damage | Regulatory non-compliance, data security gaps |
| 6 | Back-office Efficiency | Internal productivity only | HR processes, administrative overhead |

### Company Positioning Categories

When classifying a company's position in their industry:

- **Market Leader**: Top 3 by revenue/share; focus on retention, efficiency, innovation
- **Challenger**: Growing rapidly; focus on scaling operations, competitive differentiation
- **Niche Player**: Specialized segment; focus on deepening expertise, selective expansion
- **Follower**: Established but not leading; focus on operational excellence, cost optimization
- **New Entrant**: Recently entered; focus on market fit, establishing credibility

## Decision-Maker Archetypes

### By Seniority Level

| Level | Typical Titles | Primary Concerns | Time Horizon |
|-------|---------------|-----------------|--------------|
| C-Suite | CEO, CFO, CTO, COO | Strategic growth, shareholder value, competitive positioning | 3-5 years |
| VP/Director | VP Sales, Dir. Operations | Departmental KPIs, team performance, budget optimization | 1-2 years |
| Manager | Sales Manager, IT Manager | Execution, daily metrics, problem resolution | Quarterly |
| Individual Contributor | Analyst, Specialist | Task efficiency, tool usability, workload reduction | Immediate |

### Functional Area Mapping

Map each functional area to typical pain point categories:

- **Sales/Revenue**: Customer acquisition cost, win rates, sales cycle length, forecast accuracy
- **Marketing**: Lead quality, attribution, campaign ROI, brand awareness
- **Operations**: Throughput, quality control, supply chain resilience, capacity planning
- **Finance**: Cash flow, working capital, reporting accuracy, compliance
- **IT/Tech**: System uptime, technical debt, security posture, integration complexity
- **HR/Talent**: Time-to-hire, retention, engagement, skills gaps
- **Customer Success**: Churn rate, NPS, expansion revenue, support costs
- **Product/R&D**: Time-to-market, feature adoption, technical debt, innovation pipeline

## Quadrant Chart Construction Rules

### Axis Design

- **Horizontal Axis**: Pain points sorted by revenue impact (Category 1 leftmost, Category 6 rightmost)
- **Vertical Axis**: Decision-maker's functional areas of responsibility

### Intersection Priority Scoring

For each intersection cell, calculate priority:

```
Priority Score = (7 - Revenue_Category_Rank) * Functional_Area_Weight
```

Where Functional_Area_Weight:
- Core responsibility area: 3.0
- Secondary responsibility area: 2.0
- Influenced area: 1.0
- Peripheral area: 0.5

### Visualization Rules

- Highlight cells with score >= 12 as "Critical Focus"
- Highlight cells with score 8-11 as "High Priority"
- Highlight cells with score 4-7 as "Medium Priority"
- Leave cells below 4 unhighlighted
- Mark the single highest-score cell as "Primary SCENE Anchor"

## Output Templates

### Pain Point Map Output

```
# [Industry] Pain Point Map - [Company Position]

## Revenue-Critical Pain Points (Direct)
1. [Pain Point] - [Evidence/Source]
2. [Pain Point] - [Evidence/Source]
...

## Growth-Critical Pain Points
1. [Pain Point] - [Evidence/Source]
2. [Pain Point] - [Evidence/Source]
...

## Operational Pain Points
[...]

## Experience & Efficiency Pain Points
[...]

> Sorted by estimated revenue impact. Sources: [list]
```

### Decision-Maker Focus Output

```
# Decision-Maker Focus: [Name/Title] at [Company]

## Profile Summary
- Company: [Name], [Industry], [Position]
- Role: [Title], [Seniority Level]
- Functional Areas: [List]

## Likely Focus Areas (Ranked)
1. [Area] - [Reasoning with source evidence]
2. [Area] - [Reasoning with source evidence]
...

## Potential Blind Spots
- [Areas they may not be prioritizing but should]
```

### Quadrant Analysis Output

```
# SCENE Quadrant Analysis

## Primary Anchor (Highest Priority Intersection)
- Pain Point: [X-axis item]
- Decision-Maker Focus: [Y-axis item]
- Score: [Value]
- Recommended SCENE Opening: [Narrative hook]

## Secondary Anchors (Score >= 12)
1. [Pain Point] x [Focus Area] - Score: [Value]
2. [...]

## Supporting Context (Score 8-11)
[...]

## Recommended Narrative Arc
1. Open with Primary Anchor (revenue impact + personal relevance)
2. Bridge to Secondary Anchors (expand the problem scope)
3. Transition to solution (connect to your product's capabilities)
```
