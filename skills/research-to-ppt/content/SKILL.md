---
name: research-to-ppt
description: "Research-to-Presentation generator combining industry research, investment analysis, and PowerPoint creation. Produces professional research presentations with data-driven insights. Triggers: 研究报告PPT, 行业分析演示, 投资分析PPT, 股票研究演示, 市场研究报告, research presentation, investment deck"
---

# Research to PPT - 研究到演示文稿

## Overview

This skill transforms comprehensive research and investment analysis into professional PowerPoint presentations. It combines the research methodology from industry-research-report, the multi-dimensional analysis framework from investment-research-analyst, and the presentation generation capabilities from pptx-generator.

**This is NOT a simple Q&A tool. Your ONLY output is professionally formatted research presentations in PPTX format.**

## Workflow

### Phase 1: Research & Data Collection

#### 1.1 Scope Definition
- Define research objectives and key questions
- Identify industry boundaries and geographic scope
- Establish key metrics to collect

#### 1.2 Multi-Source Data Collection

**For Stock/Company Analysis:**
```python
# A-share data (akshare)
import akshare as ak
stock_info = ak.stock_individual_info_em(symbol="600519")
balance_sheet = ak.stock_balance_sheet_by_report_em(symbol="600519")
income = ak.stock_profit_sheet_by_report_em(symbol="600519")

# US stocks (yfinance)
import yfinance as yf
stock = yf.Ticker("AAPL")
info = stock.info
financials = stock.financials
```

#### 1.3 Research Output
Save research materials to `docs/`:
- `research_summary.md` - Executive research summary
- `market_data.md` - Quantitative findings
- `sources_list.md` - Complete source documentation

---

### Phase 2: Multi-Dimensional Analysis

#### 2.1 Fundamental Analysis
- Financial statement deep-dive
- Profitability metrics (ROE, margins)
- Valuation analysis (PE, PB, PS)
- Institutional predictions

#### 2.2 News & Sentiment Analysis
- Recent company news (7-30 days)
- Industry developments
- Market sentiment indicators
- Analyst ratings

#### 2.3 Technical Analysis
- Price trends and patterns
- Key support/resistance levels
- Momentum indicators (RSI, MACD)
- Volume analysis

#### 2.4 Risk Assessment
- Business risks
- Financial risks
- Market risks
- Risk mitigation factors

#### 2.5 Bull/Bear Debate
- Bull case arguments
- Bear case arguments
- Key catalysts and risks

---

### Phase 3: PPT Generation

#### 3.1 PPT Structure Design

| Slide # | Type | Content |
|---------|------|---------|
| 01 | Cover | Title, company/industry, date |
| 02 | TOC | Report structure overview |
| 03 | Executive Summary | Key findings and recommendations |
| 04 | Company Overview | Business description, market position |
| 05 | Industry Analysis | Market size, trends, competitive landscape |
| 06 | Financial Analysis | Key metrics, growth trends, charts |
| 07 | Valuation | PE/PB/PS comparison, target prices |
| 08 | Technical Analysis | Price charts, key levels |
| 09 | Risk Assessment | Major risks, mitigation |
| 10 | Conclusion | Investment thesis, recommendation |
| 11 | Summary | Key takeaways |

#### 3.2 Color Palette Selection

**Financial/Business Reports:**
```javascript
const theme = {
  primary: "1A365D",    // Deep blue - professional
  secondary: "2D3748",  // Dark gray - text
  accent: "C9A227",     // Gold - highlights
  light: "E2E8F0",      // Light gray - backgrounds
  bg: "FFFFFF"          // White - clean base
};
```

**Tech/Growth Companies:**
```javascript
const theme = {
  primary: "1E3A5F",    // Navy
  secondary: "4A5568",  // Gray
  accent: "38B2AC",     // Teal
  light: "E6FFFA",      // Light teal
  bg: "FFFFFF"
};
```

#### 3.3 Slide Generation

Create slides following the pptx-generator skill format:

```javascript
// slides/slide-01.js
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'cover',
  index: 1,
  title: 'Research Presentation Title'
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  slide.addText(slideConfig.title, {
    x: 0.5, y: 2.2, w: 9, h: 1.2,
    fontSize: 44, fontFace: "Arial",
    color: "FFFFFF", bold: true, align: "center"
  });

  return slide;
}

module.exports = { createSlide, slideConfig };
```

#### 3.4 Chart Integration

Generate data visualizations using matplotlib, then embed in PPT:

```python
import matplotlib.pyplot as plt

def generate_financial_chart(data, output_path):
    plt.figure(figsize=(10, 5))
    plt.plot(data['year'], data['revenue'], marker='o')
    plt.title('Revenue Trend', fontsize=14, fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel('Revenue (Billion CNY)')
    plt.grid(True, alpha=0.3)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
```

---

## Data Sources

### Tier 1 Sources
- Official company filings (annual reports, 10-K)
- Regulatory filings (SEC, CSRC)
- Government statistics

### Tier 2 Sources
- Bloomberg, Reuters
- Major investment bank research
- McKinsey, BCG reports

### Tier 3 Sources
- Industry associations
- Trade publications
- Financial news

---

## Output Structure

```
output/
├── research-to-ppt/
│   ├── docs/
│   │   ├── research_summary.md
│   │   ├── market_data.md
│   │   └── sources_list.md
│   ├── charts/
│   │   ├── revenue_trend.png
│   │   ├── valuation_comparison.png
│   │   └── technical_chart.png
│   ├── slides/
│   │   ├── slide-01.js
│   │   ├── slide-02.js
│   │   ├── ...
│   │   └── compile.js
│   └── output/
│       └── presentation.pptx
```

---

## Quality Standards

1. **Data Accuracy**: All statistics must be sourced and verified
2. **Visual Consistency**: Use consistent theme colors across all slides
3. **Professional Tone**: Business-appropriate language and design
4. **Citation**: Include sources for all key data points
5. **Charts**: Embed generated charts at relevant positions

---

## Reference Files

| File | Contents |
|------|----------|
| [references/slide-types.md](references/slide-types.md) | Slide type patterns from pptx-generator |
| [references/design-system.md](references/design-system.md) | Color palettes and typography |
| [references/pptxgenjs.md](references/pptxgenjs.md) | Complete API reference |

---

## Common Mistakes to Avoid

- ❌ Skipping research phase and jumping to PPT
- ❌ Using generic slides without data visualizations
- ❌ Inconsistent color scheme across slides
- ❌ Missing page number badges (except cover)
- ❌ Forgetting to cite data sources
- ❌ Outputting content in conversation instead of files
