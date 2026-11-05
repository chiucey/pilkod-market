# Category Lifecycle Methodology Reference

## Data Source Guide

### E-commerce Platforms

| Platform | Stage Relevance | Key Metrics | How to Query |
|----------|----------------|-------------|--------------|
| Amazon | 10-100 primary, 1-10 secondary | Review count, BS rank, price distribution, brand count | Search category keyword, analyze first 3 pages |
| Walmart | 10-100 | Shelf density, price compression, private label presence | Category search + filter analysis |
| eBay | 1-10 critical, 10-100 secondary | Resale value, used/new ratio, listing velocity | Sold listings filter, price trend |
| 1688/Alibaba | 1-10, 10-100 | White-label supplier density, MOQ trends, module pricing | Supplier search, price comparison |
| Temu/SHEIN | 10-100 | Extreme price points, listing density, SKU proliferation | Category search, price floor analysis |

### Search & Trend Data

| Source | Stage Relevance | Key Metrics |
|--------|----------------|-------------|
| Google Trends | All stages | Search volume index, related queries, geographic distribution |
| Google Patents | 0-1 primary | Filing volume, assignee concentration, citation network |
| Arxiv | 0-1 primary | Paper volume, recency, author institution diversity |

### Social & Community

| Source | Stage Relevance | Key Metrics |
|--------|----------------|-------------|
| Reddit | 0-1, 1-10 | Subreddit size, post frequency, comment sentiment, technical depth |
| TikTok | 1-10 primary | Hashtag volume, creator count, emotional/premium content ratio |
| YouTube | 1-10 | Review video count, view distribution, affiliate link density |
| Kickstarter/Indiegogo | 0-1, 1-10 | Campaign count, funding success rate, average pledge |

### Professional & Financial

| Source | Stage Relevance | Key Metrics |
|--------|----------------|-------------|
| TechCrunch/Crunchbase | 0-1, 1-10 | Funding rounds, startup count, acquisition activity |
| Professional Forums | 1-10 | Thread depth, expert engagement, technical benchmark discussions |

## Stage Differentiation Checklist

Use this checklist to avoid misjudgment:

### 0-1 vs 1-10
- [ ] Are there >3 white-label suppliers on 1688?
- [ ] Is there a dedicated subreddit with >10k members?
- [ ] Are there >100 Amazon reviews for top products?
- [ ] Is Google Trends showing sustained growth (not just spikes)?
- [ ] Are there scene-based search queries (not just technical terms)?

### 1-10 vs 10-100
- [ ] Do users search by mature category terms (not scene descriptions)?
- [ ] Is there clear style differentiation with stable market share?
- [ ] Are M2C platforms (Temu/SHEIN) dominant channels?
- [ ] Is price compression >50% from early-stage pricing?
- [ ] Are there established "performance benchmark" products?

## Common Misjudgment Patterns

1. **Mistaking media hype for market maturity**: High media coverage does not mean 1-10 if e-commerce data is absent
2. **Confusing enthusiast market with mainstream**: Niche communities != mental model formation
3. **Overweighting patent activity**: Patents indicate 0-1 tech activity, not market readiness
4. **Ignoring geographic lag**: A category may be 10-100 globally but 1-10 or 0-1 in specific regions

## Cross-Validation Thresholds

Require minimum 3 independent data sources confirming the same stage before high confidence:

- **High confidence**: 4+ sources align, quantitative metrics consistent
- **Medium confidence**: 3 sources align, some metrics ambiguous
- **Low confidence**: <3 sources, significant data gaps, or conflicting signals

## Global-Local Analysis Framework

When analyzing a non-global scope:

1. Determine global stage first (use same framework on global data)
2. Compare local vs global on:
   - Regulatory environment (approval timelines, import restrictions)
   - Supply chain maturity (local manufacturing, logistics infrastructure)
   - Consumption capacity (disposable income, category penetration rate)
   - Infrastructure readiness (required complementary technologies)
3. Classify relationship: lagging (typically 1-2 stages behind), synchronous, or leading (often due to policy or cultural factors)
