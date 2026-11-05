---
name: research_report2.0
description: "Institutional-grade equity research report generation. When you need to create a professional deep-dive research report (深度研报) for a publicly listed company, covering: company overview, industry analysis, financial analysis, competitive landscape, valuation model, investment recommendation, and risk assessment. Supports PPTX and DOCX output formats. Typical use cases: (1) Create a deep research report for a specific stock, (2) Generate an institutional-grade equity analysis presentation, (3) Build a comprehensive company research deck with financial data visualization."
license: Proprietary. LICENSE.txt has complete terms
---

# Research Report Skill 2.0

## Quick Reference

| Task | Guide |
|------|-------|
| Full workflow (recommended) | Read [workflow.md](workflow.md) — end-to-end pipeline |
| Chart generation guide | Read [chart_guide.md](chart_guide.md) — matplotlib chart templates |
| PPTX creation | Depends on `pptx` skill — invoke it first |
| DOCX creation | Depends on `docx` skill — invoke it first |
| Data collection | Use Explore subagents (max 3 parallel) |
| Chart assets | Use `scripts/generate_charts.py` template |

---

## Overview

This skill provides a **structured, repeatable workflow** for producing institutional-grade equity research reports (深度研报). It covers the entire pipeline from data collection to final deliverable.

### Key Principles (Three Iron Laws)

Every report must satisfy these three non-negotiable standards:

| Iron Law | Definition | Enforcement |
|----------|-----------|-------------|
| **1. Falsifiability (可证伪性)** | Every core thesis must include a "what if I'm wrong" condition. **No one-way optimistic narratives allowed.** | Each investment logic bullet must end with: "Reverse condition: If [X] does not happen, thesis is invalidated because [Y]." |
| **2. Valuation Anchoring (估值锚定)** | Target price derivation must use **≥2 valuation methods** with cross-validation. Single-point valuation is invalid. | Must present: (a) Relative valuation (PE/PB/EV-EBITDA vs peers), (b) Absolute valuation (simplified DCF or SOTP), (c) Scenario-weighted target price. |
| **3. Data Provenance (数据血缘)** | Every key figure must trace to a source. Approximations (`~`) are banned in main text. | All financial data, market share, and order values must carry a source tag (e.g., 来源：公司2025年报/Wind/IDC). Unsourced data goes into an "Unverified Appendix" or is removed. |

---

## Report Structure (Standard 8-Chapter Framework)

This is the default structure for a **30+ page institutional research report**. Each chapter has mandatory writing standards and anti-patterns.

| Chapter | Title | Typical Slides | Key Content | Writing Standard |
|---------|-------|---------------|-------------|------------------|
| Cover + TOC | 封面+目录 | 2 | Company name, ticker, **rating**, **target price**, **upside/downside %**, date | Rating must map to upside range: Buy ≥30%, Accumulate 15-30%, Hold -15%~+15%, Reduce < -15%. |
| Part 01 | 投资要点与核心观点 | 2-3 | Investment thesis, key metrics, rating rationale | Must open with **"One-Sentence Investment Logic"**. KPI table must include **EV, Net Cash/Debt**, not just market cap. |
| Part 02 | 公司概况与历史沿革 | 2-3 | Company snapshot, history timeline, strategy framework, shareholding structure | Management background must include **"Strategic Fit Assessment"** (e.g., non-R&D background CEO at tech-driven firm = execution risk). |
| Part 03 | 行业分析 | 2-4 | Market size, trends, policy, supply chain, channels | Market size charts must show **CAGR and data source**. Policy analysis must distinguish **systemic vs individual impact**. |
| Part 04 | 业务分析 | 2-4 | Product matrix, revenue structure, growth drivers, M&A | High-growth segments must decompose **Revenue = Volume × Price** with capacity utilization / certification / yield rate constraints. Declining segments must analyze **"active contraction vs passive loss"**. |
| Part 05 | 财务分析 | 3-5 | Revenue/profit trends, profitability, expenses, cash flow, dividends | **5-year full table mandatory**. Must include **DuPont decomposition** (ROE = margin × turnover × leverage). Cyclical stocks must add **historical percentile analysis**. |
| Part 06 | 竞争格局与护城河 | 2-3 | Competitive landscape, moat analysis, management | Peer comparison table must have **≥10 dimensions** including operational metrics (asset turnover, revenue per employee, R&D intensity). Moat claims must have **quantified evidence** (e.g., cost advantage → attach cost structure breakdown). |
| Part 07 | 估值分析与投资建议 | 2-3 | **PE/PB/DCF valuation**, earnings forecast, **scenario analysis** | **Scenario analysis must vary BOTH earnings AND multiple**. Must include **sensitivity matrix** (revenue ±5%, margin ±2pct → EPS elasticity). Must anchor to **peer valuation median**. |
| Part 08 | 风险提示 | 1-2 | Risk factors with **severity ratings + quantified financial impact** | Every High/Medium risk must attach: "If realized, estimated impact on [Year] net profit/ revenue: X%." Distinguish **systemic risks** (cycle, FX) from **idiosyncratic risks** (compliance, client loss, M&A integration). |
| Closing | 结语 | 1 | Disclaimer, contact | — |

**Total: ~25-35 slides** for a standard institutional report.

---

## Chapter-by-Chapter Writing Standards

### Part 01: Investment Thesis (投资要点)

**Mandatory Elements:**
1. **One-Sentence Logic**: E.g., "This is a 'cycle bottom + capacity clearance + new product ramp' triple-inflection play."
2. **Rating-Price Consistency Matrix**:
   - Buy: Target price ≥ Current price × 1.30
   - Accumulate: Target price between Current price × 1.15 and 1.30
   - Hold: Target price between Current price × 0.85 and 1.15
   - Reduce: Target price < Current price × 0.85
3. **KPI Dashboard** must include: Market Cap, EV, Net Cash/Debt, PE(TTM), PB, Dividend Yield, 52W High/Low.

**Anti-Patterns:**
- ❌ "增持" with <15% upside.
- ❌ KPI table with only revenue/profit; missing balance sheet strength.

---

### Part 04: Business Analysis (业务分析)

**Mandatory Elements:**
1. **Revenue Bridge**: Current year revenue vs prior year = Price effect + Volume effect + Mix effect.
2. **Growth Driver Constraints**: For any segment projected to grow >30%, list:
   - Capacity utilization ceiling
   - Customer certification timeline
   - Yield rate assumption
   - Order backlog visibility (if disclosed)
3. **Declining Segment Diagnosis**: If a segment drops >20%, state whether it is strategic withdrawal or competitive loss, and how the revenue gap is filled.

**Anti-Patterns:**
- ❌ "Second curve will grow 300%" without capacity/customer/yield proof.
- ❌ Mixing "active strategic adjustment" with "passive market share loss" without distinction.

---

### Part 05: Financial Analysis (财务分析)

**Mandatory Elements:**
1. **5-Year Full Financial Table**: Revenue, Gross Profit, Gross Margin, Operating Profit, Net Profit, Net Margin, ROE, ROA, Operating Cash Flow, CapEx, Interest-Bearing Debt.
2. **DuPont Analysis**: Decompose ROE into Net Margin × Asset Turnover × Equity Multiplier. Identify which lever drives changes.
3. **Cash Flow Quality**: Operating CF / Net Profit ratio. If <80%, explain working capital drag.
4. **Cyclical Positioning** (for cyclical stocks): Current gross margin/net margin percentile vs 5-year history.

**Anti-Patterns:**
- ❌ Empty chart placeholders (title only, no content). If data is unavailable, remove the slide or state "Data unavailable; chart omitted."
- ❌ Presenting revenue/profit without YoY/QoQ growth rates.

---

### Part 06: Competitive Landscape (竞争格局)

**Mandatory Elements:**
1. **Peer Comparison Table (≥10 dimensions)**:
   - Financial: Revenue, Net Profit, Gross Margin, Net Margin, ROE
   - Operational: Asset Turnover, Inventory Days, Revenue per Employee, R&D/Sales
   - Market: Market Share, Capacity, Export Ratio
2. **Moat Quantification**:
   - Cost advantage: Show cost structure differential (%)
   - Customer stickiness: Average client tenure, top 5 client retention rate
   - Certification barrier: List DMF/CEP/IATF counts and approval timeline

**Anti-Patterns:**
- ❌ "Industry leader" without market share % or ranking source.
- ❌ Moat analysis with only qualitative adjectives ("strong", "deep").

---

### Part 07: Valuation & Investment Recommendation (估值分析)

**Mandatory Elements:**

**A. Valuation Methodology (must include ≥2 methods)**

| Method | Requirements |
|--------|-------------|
| **Relative Valuation** | Select 3-5 comparable companies. Show PE(TTM), Forward PE, PB, EV/EBITDA, PEG median. Justify premium/discount (±x%) based on growth/ROE differential. |
| **Absolute Valuation** | Simplified DCF: 3-5 year explicit forecast, perpetuity growth ≤ GDP growth rate, WACC assumption disclosed. Or SOTP for conglomerates. |
| **Scenario Analysis** | 3 scenarios (Optimistic/Base/Pessimistic). **Both EPS and target multiple must vary by scenario.** Weighted target price = Σ(Price_i × Probability_i). |

**B. Sensitivity Matrix**

Present a 3×3 matrix:
- Rows: Revenue growth (-5% / Base / +5%)
- Columns: Gross margin (-2pct / Base / +2pct)
- Cells: Implied EPS and target price

**C. Catalyst Timeline**

| Time | Catalyst | Verifiable Metric | If Missed: Downside |
|------|----------|-------------------|---------------------|
| 2026Q2 | Asetek consolidation | Revenue ≥ $35M | Cut EPS by 5% |
| 2026H2 | AIPC order ramp | New orders ≥ $1.8B | Cut target multiple by 2x |

**Anti-Patterns:**
- ❌ Optimistic/Base scenarios with identical EPS (only multiple changes).
- ❌ Target price inconsistent with weighted scenario result without explanation.
- ❌ "Based on 30x PE" without explaining why 30x is justified vs peers.

---

### Part 08: Risk Assessment (风险提示)

**Mandatory Elements:**

1. **Risk Taxonomy**:
   - **Systemic**: Industry cycle, FX, interest rates, geopolitics
   - **Idiosyncratic**: Compliance, client concentration, M&A integration, product liability

2. **Quantified Impact** (for High/Medium risks):
   - Format: "If [Risk] materializes (e.g., product included in next national procurement with 60% price cut), estimated impact on 2026E net profit: -X%."
   - Must include **probability-weighted expected loss** if possible.

3. **Risk Matrix Visualization**:
   - X-axis: Probability (Low/Medium/High)
   - Y-axis: Impact severity (Low/Medium/High)
   - Bubble size: Estimated revenue/profit at risk

**Anti-Patterns:**
- ❌ Risk list with only severity labels (高/中/低) and no financial impact.
- ❌ Cross-border M&A risks (e.g., Asetek) without cultural/integration/tariff sub-risks.

---

## End-to-End Workflow

### Phase 1: Requirements Clarification

Before starting, clarify with the user:

| Question | Options | Default |
|----------|---------|---------|
| Output format | PPTX / DOCX / Markdown | PPTX |
| Report depth | 精简版(~15p) / 标准版(~25p) / 机构级(~35p) | 机构级 |
| Data source | Web search / Knowledge only / User-provided | Web search |
| Company | Ticker or name | (required) |
| Focus areas | Financial / Strategic / Industry / All | All |

### Phase 2: Data Collection (Parallel)

Use **max 3 Explore subagents** in parallel to collect:

| Agent 1: Financial Data | Agent 2: Industry Data | Agent 3: Company Strategy |
|------------------------|------------------------|--------------------------|
| Latest annual/quarterly reports | Market size & growth | Strategy framework |
| Revenue, profit, margins (3-5yr) | Industry trends & policy | Product portfolio |
| Balance sheet, cash flow | Competitive landscape | Management team & governance |
| Valuation metrics (PE/PB/PS) | Supply chain dynamics | Recent events/M&A |
| Analyst consensus | Consumer/channel shifts | Shareholder structure & pledging |

**Search budget**: 5-10 searches total across all agents.

**Additional mandatory data points** (often missed):
- Management shareholding pledging ratio
- Top 5 customer concentration (%)
- Export revenue % and main currency exposure
- Historical procurement penalties/compliance issues
- Capacity utilization by segment

### Phase 3: Asset Pre-Generation

Generate all chart assets **before** writing the presentation script.

Standard chart set for equity research:

| # | Chart Type | Purpose | Recommended Tool |
|---|-----------|---------|-----------------|
| 1 | Revenue & Profit Bar | 营收净利润趋势 | matplotlib |
| 2 | Profitability Line | 毛利率/净利率/ROE | matplotlib |
| 3 | Revenue Pie | 收入结构 | matplotlib |
| 4 | Regional Bar | 地区分布 | matplotlib |
| 5 | Market Size Bar+Forecast | 行业规模预测 | matplotlib |
| 6 | Competition Bar | 竞争格局 | matplotlib |
| 7 | Supply Chain Dual-axis | 供给/进口依赖 | matplotlib |
| 8 | Channel Stacked Bar | 渠道变化 | matplotlib |
| 9 | Expense Ratio Line | 费用率趋势 | matplotlib |
| 10 | Cash Flow & Dividend | 现金流分红 | matplotlib |
| 11 | **PE Band** | 估值区间 | matplotlib |
| 12 | **PB-ROE Scatter** | 估值锚定 | matplotlib |
| 13 | **Sensitivity Heatmap** | 盈利敏感性 | matplotlib |
| 14 | **DuPont Waterfall** | ROE拆解 | matplotlib |

See [chart_guide.md](chart_guide.md) for detailed chart templates and CJK font setup.

### Phase 4: Presentation Creation

**CRITICAL**: Invoke the `pptx` skill before creating the presentation.

```javascript
// Required: invoke pptx skill first for best practices
// Then use pptxgenjs to build the presentation

// Key requirements:
// 1. Declare slide dimensions FIRST
// 2. Use Container System for overflow protection
// 3. Every slide must have at least one visible element
// 4. Call slide.render() at end of each slide
// 5. No blank slides allowed
```

---

## Design System for Research Reports

### Color Palette Selection

Choose a palette that reflects the industry/sector:

| Industry | Primary | Secondary | Accent | Theme |
|----------|---------|-----------|--------|-------|
| TCM / Healthcare | `8B2500` | `C17817` | `2C3E50` | Warm Terracotta |
| Banking / Finance | `1E2761` | `CADCFC` | `FFFFFF` | Midnight Executive |
| Technology | `028090` | `00A896` | `02C39A` | Teal Trust |
| Consumer | `F96167` | `F9E795` | `2F3C7E` | Coral Energy |
| Energy / Resources | `2C5F2D` | `97BC62` | `F5F5F5` | Forest & Moss |
| Real Estate | `36454F` | `F2F2F2` | `212121` | Charcoal Minimal |
| Pharma / Biotech | `6D2E46` | `A26769` | `ECE2D0` | Berry & Cream |

### Typography

| Element | Font | Size | Style |
|---------|------|------|-------|
| Cover title | Georgia (serif) | 36-44pt | Bold |
| Slide title | Georgia (serif) | 20-28pt | Bold |
| Body text | Calibri / system sans | 10-14pt | Regular |
| KPI numbers | Calibri | 20-24pt | Bold |
| Captions | Calibri | 7-9pt | Regular, muted |
| Table headers | Calibri | 9-10pt | Bold |

**CJK fonts**: Use `Noto Sans CJK SC` or `Noto Serif CJK SC` for Chinese text in charts.

### Layout Patterns

| Pattern | Use Case | Key Elements |
|---------|----------|-------------|
| **KPI Dashboard** | Key metrics slide | 6 cards in 2×3 grid, colored left border |
| **Chart + Insight** | Data analysis slides | Chart (60%) + bullet insights (40%) |
| **Dual Chart** | Comparison slides | Two charts side by side |
| **Table + Summary** | Financial data | Data table + right-side highlights |
| **Card Grid** | Strategy/moat slides | 3-4 cards with icon, title, description |
| **Timeline** | History slides | Horizontal timeline with alternating labels |
| **Scenario Analysis** | Valuation slides | 3 columns (bull/base/bear) with color coding; **must show different EPS assumptions** |
| **Risk Matrix** | Risk slides | Cards with severity badges **and financial impact estimates** |
| **Sensitivity Heatmap** | Valuation deep-dive | 3×3 matrix with color-coded EPS/target price cells |

---

## Helper Functions (Reusable Code Patterns)

### Section Divider Slide

```javascript
function addSectionDivider(num, title, subtitle) {
  const s = pres.addSlide();
  s.background = { color: C.primary };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.15, h: SLIDE_H, fill: { color: C.secondary } });
  s.addText(`PART ${num}`, { x: 1.0, y: 1.2, w: 3, h: 0.6, fontSize: 16, color: C.gold, charSpacing: 3 });
  s.addText(title, { x: 1.0, y: 1.8, w: 8, h: 1.0, fontSize: 36, color: C.white, fontFace: 'Georgia', bold: true });
  if (subtitle) s.addText(subtitle, { x: 1.0, y: 3.0, w: 7, h: 0.5, fontSize: 14, color: C.gold, italic: true });
  s.render();
  return s;
}
```

### Content Slide Template

```javascript
function addContentSlide(title) {
  const s = pres.addSlide();
  s.background = { color: C.white };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: SLIDE_W, h: 0.06, fill: { color: C.primary } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0.06, w: SLIDE_W, h: 0.75, fill: { color: C.cream } });
  s.addText(title, { x: 0.6, y: 0.12, w: 8.5, h: 0.6, fontSize: 20, color: C.primary, fontFace: 'Georgia', bold: true });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 0.72, w: 1.5, h: 0.04, fill: { color: C.secondary } });
  return s;
}
```

### KPI Card

```javascript
function addKPI(slide, x, y, w, h, label, value, subtext, color) {
  const card = slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, fill: { color: C.white },
    shadow: { type: 'outer', blur: 6, offset: 2, color: '000000', opacity: 0.08 },
    rectRadius: 0.1
  });
  card.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: h, fill: { color: color || C.primary } });
  card.addText(value, { x: 0.2, y: 0.1, w: w - 0.3, h: 0.5, fontSize: 22, color: color || C.primary, bold: true });
  card.addText(label, { x: 0.2, y: 0.55, w: w - 0.3, h: 0.3, fontSize: 9, color: C.accent });
  if (subtext) card.addText(subtext, { x: 0.2, y: 0.85, w: w - 0.3, h: 0.25, fontSize: 8, color: C.green });
}
```

### Bullet List with Custom Markers

```javascript
function addBulletList(slide, x, y, w, h, items, fontSize = 11) {
  const textArr = items.map(item => ({
    text: item,
    options: { bullet: { code: '2022', color: C.secondary }, fontSize, color: C.accent, breakLine: true, paraSpaceAfter: 4 }
  }));
  slide.addText(textArr, { x, y, w, h, valign: 'top', lineSpacingMultiple: 1.3 });
}
```

### Data Table

```javascript
function addDataTable(slide, x, y, w, headers, rows, colWidths) {
  const tableData = [
    headers.map(h => ({ text: h, options: { fill: { color: C.primary }, color: C.white, bold: true, fontSize: 9, align: 'center' } })),
    ...rows.map((row, ri) => row.map((cell, ci) => ({
      text: cell,
      options: {
        fill: { color: ri % 2 === 0 ? C.cream : C.white },
        fontSize: 9, color: ci === 0 ? C.primary : C.accent, bold: ci === 0, align: ci === 0 ? 'left' : 'center'
      }
    })))
  ];
  slide.addTable(tableData, { x, y, w, colW: colWidths, border: { pt: 0.5, color: C.lightGray } });
}
```

### Scenario Analysis Block (NEW)

```javascript
function addScenarioAnalysis(slide, x, y, w, h, scenarios) {
  // scenarios: [{name, probability, eps, pe, targetPrice, color}]
  const colW = w / 3;
  scenarios.forEach((sc, i) => {
    const left = x + i * colW;
    // Header
    slide.addShape(pres.shapes.RECTANGLE, { x: left, y, w: colW - 0.1, h: 0.6, fill: { color: sc.color } });
    slide.addText(`${sc.name}\n${sc.probability}`, { x: left + 0.1, y: y + 0.1, w: colW - 0.3, h: 0.4, fontSize: 11, color: C.white, bold: true, align: 'center' });
    // Body
    slide.addShape(pres.shapes.RECTANGLE, { x: left, y: y + 0.6, w: colW - 0.1, h: 1.8, fill: { color: C.cream } });
    slide.addText(`2027E EPS: ${sc.eps}元\n目标PE: ${sc.pe}x\n目标价: ¥${sc.targetPrice}`, { 
      x: left + 0.1, y: y + 0.8, w: colW - 0.3, h: 1.4, fontSize: 10, color: C.accent, align: 'center' 
    });
  });
  // Weighted price
  const weighted = scenarios.reduce((sum, sc) => sum + sc.targetPrice * parseFloat(sc.probability) / 100, 0);
  slide.addText(`加权目标价: ¥${weighted.toFixed(2)}`, { x: x, y: y + 2.6, w: w, h: 0.4, fontSize: 12, color: C.primary, bold: true, align: 'center' });
}
```

---

## Quality Checklist (Institutional-Grade)

Before delivering the report, verify:

### Content Integrity
- [ ] **Falsifiability check**: Every core thesis has a "Reverse condition" stated explicitly.
- [ ] **Valuation cross-validation**: ≥2 methods used; target price explained, not asserted.
- [ ] **Scenario consistency**: Optimistic/Base/Pessimistic EPS assumptions are **different**; multiple varies accordingly.
- [ ] **Rating-price alignment**: Target upside % matches rating definition (Buy ≥30%, etc.).
- [ ] **Data provenance**: All key figures have source tags. No `~` approximations in main text.

### Financial Depth
- [ ] **5-year table**: Complete with YoY growth rates.
- [ ] **DuPont analysis**: ROE decomposed into margin × turnover × leverage.
- [ ] **Cash flow quality**: Operating CF / Net Profit ratio disclosed.
- [ ] **Cyclical positioning**: Historical percentile for margins (if cyclical).

### Business Logic
- [ ] **Growth constraints**: High-growth segments have capacity/certification/yield proof.
- [ ] **Declining segment diagnosis**: Active vs passive contraction clarified.
- [ ] **Customer concentration**: Top 5 / largest single client % disclosed.

### Competitive & Management
- [ ] **Peer comparison ≥10 dimensions**: Including operational metrics.
- [ ] **Moat quantification**: Cost advantage %, client tenure years, certification counts.
- [ ] **Management fit**: Background assessed against current strategic task.

### Risk & Catalyst
- [ ] **Quantified risks**: High/Medium risks have estimated profit/revenue impact %.
- [ ] **Catalyst timeline**: Quarterly milestones with verifiable metrics and "if missed" downside.
- [ ] **M&A risk drill-down**: Cross-border deals include integration/culture/tariff sub-risks.

### Visual & Technical
- [ ] **No blank slides**: Every slide has at least one visible element.
- [ ] **No empty charts**: If data unavailable, remove slide or state omission reason.
- [ ] **Charts visible**: All matplotlib assets render correctly with CJK fonts.
- [ ] **Consistent styling**: Color palette, fonts, and layout patterns uniform.
- [ ] **Disclaimer present**: Every content slide has a disclaimer footnote.
- [ ] **Page numbers**: All slides except cover/section dividers have page numbers.
- [ ] **Layout QA passed**: `validate_layout.py` reports 0 issues.
- [ ] **Content QA passed**: `markitdown` extraction shows correct content.

---

## Dependencies

- `pptx` skill — for PPTX creation and QA tools
- `docx` skill — for DOCX creation (alternative output)
- `matplotlib` (Python) — for chart generation
- `pptxgenjs` (Node.js) — for presentation creation
- `markitdown` (Python) — for content extraction/verification

---

## Anti-Patterns to Avoid (2.0 Additions)

### Content & Logic
1. **Don't skip data collection** — never rely solely on training data for financial figures.
2. **Don't create text-only slides** — every slide needs at least one visual element.
3. **Don't use default blue** — choose industry-specific color palettes.
4. **Don't repeat the same layout** — vary layouts across slides.
5. **Don't hardcode coordinates** — use dimension constants (SLIDE_W, SLIDE_H, etc.).
6. **Don't skip QA** — always run fix_pptx.py + validate_layout.py.
7. **Don't exceed search budget** — max 10 searches total, batch similar queries.
8. **Don't spawn more than 3 subagents** — respect the parallel agent limit.
9. **Don't forget CJK fonts** — always configure Noto Sans CJK SC for Chinese charts.
10. **Don't leave placeholder text** — verify all content is substantive.

### Research Quality (NEW)
11. **Don't deliver one-way optimism** — every bull case must have a bear case counterweight.
12. **Don't use single-point valuation** — PE alone is insufficient; always cross-validate.
13. **Don't approximate key data** — `~2.86亿` is banned; use exact figures or cite ranges with sources.
14. **Don't leave chart windows empty** — if a chart cannot be generated due to missing data, remove the slide or explicitly state "Data unavailable; chart omitted."
15. **Don't list management resumes without analysis** — always assess strategic fit (e.g., "Sales-background CEO at R&D-heavy firm = execution risk on innovation pipeline").
16. **Don't state risks without quantification** — "High risk of price cut" is weak; "60% procurement price cut → 2026E net profit -18%" is strong.
17. **Don't project hyper-growth without constraints** — "300% growth" must be backed by capacity plan, customer POs, and yield assumptions.
18. **Don't ignore cyclical stress-testing** — for cyclical stocks, always include "If downturn repeats 2023 scenario, EPS drops to X."
19. **Don't mix up scenario variables** — Optimistic scenario must have higher EPS **and** higher multiple than Base; identical EPS with different multiples is a logic error.
20. **Don't omit "if catalyst missed" downside** — every catalyst timeline must include a "missed → cut EPS by X%" branch.

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.0 | — | Initial release with standard 8-chapter framework. |
| **2.0** | **2026-04-28** | **Added Three Iron Laws (Falsifiability, Valuation Anchoring, Data Provenance); chapter-specific writing standards; quantified risk requirements; scenario analysis with dual-variable constraints; management fit assessment; sensitivity heatmap; anti-patterns 11-20.** |
