---
name: amazon-product-analyst
description: Expert skill for comprehensive Amazon product analysis across global marketplaces. Use when analyzing Amazon product performance, sales data, market trends, review analysis, and pricing strategies. Trigger phrases: analyze Amazon products, product research, Amazon data analysis, sales performance, review sentiment analysis.
---

# Amazon Product Analyst Expert

Professional Amazon product analysis skill for comprehensive marketplace intelligence.

## Core Analysis Dimensions

### 1. Sales Performance Analysis

**Key Metrics to Evaluate:**

- Monthly/quarterly revenue trends
- Sales velocity and seasonality patterns
- Inventory turnover rates
- FBA vs FBM performance comparison
- Buy Box winning percentage

**Analysis Framework:**

```
Product Performance Score = f(Revenue, Velocity, Reviews, Competition)
```

### 2. Review & Sentiment Analysis

**Metrics Framework:**

- Overall rating distribution (1-5 stars)
- Sentiment classification: Positive (4-5★), Neutral (3★), Negative (1-2★)
- Common pain points extraction
- Feature-specific satisfaction rates
- Review velocity trends

**Sentiment Analysis Prompt Template:**

```
Analyze product reviews focusing on:
1. What do customers praise most?
2. What are the common complaints?
3. Which features generate most satisfaction?
4. Comparison with similar products
```

### 3. Pricing Strategy Analysis

**Price Intelligence Factors:**

- Current price vs historical price range
- Buy Box price distribution
- Competitor pricing patterns
- MAP (Minimum Advertised Price) compliance
- Promotional pricing impact

### 4. Keyword & SEO Analysis

**Essential Keywords:**

- Main keywords with search volume
- Long-tail keyword opportunities
- Category-specific terms
- Brand-specific searches
- Seasonal keyword trends

## European Market Specific Metrics

### Multi-Country Analysis Framework

| Market | Key Focus Areas | Data Sources |
|--------|-----------------|--------------|
| UK | Seasonality, Brand preference | Jungle Scout, Helium 10 |
| Germany | Quality standards, Technical specs | AMZScout, Algopix |
| France | Price sensitivity, Style preferences | Official Amazon data |
| Italy | Growing market, Lower competition | Market trends |
| Spain | Emerging opportunities, Local preferences | Consumer insights |

### European Compliance Requirements

- CE marking requirements
- Packaging regulations (EPR)
- VAT compliance across EU states
- Product safety standards
- Language localization needs

## Analysis Output Templates

### Product Viability Score

```
Score Components:
├── Market Demand (30%)
│   ├── Search volume: ___
│   ├── Sales velocity: ___
│   └── Seasonality: ___
├── Competition Level (25%)
│   ├── Number of competitors: ___
│   ├── Review barrier: ___
│   └── Brand concentration: ___
├── Profit Potential (25%)
│   ├── Buy cost: ___
│   ├── Landed cost: ___
│   └── FBA fees: ___
└── Differentiation (20%)
    ├── Unique features: ___
    ├── Brand strength: ___
    └── Review quality: ___
```

### Competitor Landscape Map

```
Tier 1 (Market Leaders): [Brand names with >30% share]
Tier 2 (Strong Challengers): [Brands with 10-30% share]
Tier 3 (Niche Players): [Small brands with <10% share]
Opportunity Zones: [Underserved segments]
```

## Recommended Tools Integration

### Primary Research Tools

- **Jungle Scout**: Sales estimates, product database
- **Helium 10**: Keyword research, reverse ASIN lookup
- **SellerSprite**: AI-powered review analysis
- **AMZScout**: Product tracker, niche finder

### Secondary Research Sources

- Keepa: Price history tracking
- CamelCamelCamel: Historical pricing data
- ReviewMeta: Review authenticity analysis
- Sorftime: Category bestsellers analysis

## Research Prompt Templates

### Basic Product Analysis

```
Analyze the following Amazon product for [MARKETPLACE] market:
Product URL/ASIN: [INSERT]
Focus areas:
1. Sales performance and trends
2. Review sentiment breakdown
3. Pricing strategy analysis
4. Competitive positioning
5. Market opportunity assessment
```

### Comprehensive Market Entry Analysis

```
Conduct a full market entry analysis for [PRODUCT CATEGORY] on Amazon [MARKETPLACE]:
1. Market Size & Growth Rate
2. Top Players & Market Share
3. Average Price Points
4. Review Distribution of Top Sellers
5. Seasonal Trends
6. Key Success Factors
7. Potential Risks & Barriers
8. Recommended Entry Strategy
```

## Best Practices for AI Platform Usage

### Getting Accurate Results

1. **Provide Specific Data**: Include ASIN, marketplace, and time period
2. **Ask for Sources**: Request citation of data sources
3. **Cross-validate**: Use multiple analysis angles
4. **Request Limitations**: Ask about data accuracy and sample size
5. **Iterative Refinement**: Build on initial findings

### Structured Output Requests

```
Format the analysis as:
1. Executive Summary (3 bullet points)
2. Key Findings (numbered list)
3. Detailed Analysis (with data tables)
4. Recommendations (prioritized action items)
5. Data Sources & Limitations
```
