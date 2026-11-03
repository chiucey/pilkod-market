# Phase 1 — 4-Step Data Collection Workflow

**CRITICAL: Complete these 4 steps BEFORE starting any analysis. Do NOT skip steps 1-4.**

---

## Step 1: Check Today's Date

Write down today's date. Confirm the earnings release you find in Step 2 is within the last 3 months.

**If the earnings release is older than 3 months → STOP. Do not proceed. Inform the user the data is stale.**

---

## Step 2: Search for Latest Earnings

Use `batch_web_search` to find the latest earnings materials:

```
Queries to run (use search_type="news" for recency):
1. "[Company] [ticker] earnings Q[X] 202[Y] results"
2. "[Company] latest quarterly results [year]"
3. "[Company] Q[X] [year] earnings release"
```

**Target:** Form 10-Q / 10-K (quarterly/annual filing) + Earnings Release + Earnings Call Transcript

**Acceptable sources:**
- SEC EDGAR (10-Q, 10-K, 8-K filings) ✅
- Company investor relations website ✅
- Bloomberg/FactSet consensus estimates ✅
- Seeking Alpha transcript ✅
- Reuters / WSJ / FT coverage ✅

**Avoid:** Wikipedia, stock screeners with no source links, expired paywalled content

---

## Step 3: Verify Release Date

Confirm:
- [ ] Earnings release date is within last 3 months of today's date
- [ ] Transcript date matches earnings release date
- [ ] 10-Q/10-K has been filed (if cited)

**If dates don't match → Search again for the correct transcript.**

**If no transcript available → Note this in the report and use earnings release only.**

---

## Step 4: Document Source List

Before writing a single word, write down all sources:

```
CONFIRMED SOURCES:
□ Earnings Release: [URL] — dated [DATE]
□ 10-Q/10-K Filing: [URL] — filed [DATE]
□ Earnings Call Transcript: [URL] — dated [DATE]
□ Investor Presentation: [URL] — dated [DATE]
□ Consensus Estimates: [Source name] — dated [DATE]
□ Prior Guidance: [Source] — from [Quarter/Year]
```

**MANDATORY: You must have at minimum:**
1. Earnings release (URL required)
2. 10-Q or 10-K (EDGAR link preferred)

If you cannot find both → note the limitation in the report and proceed with available sources.

---

## Phase 2: Analysis Framework

### 2.1 Beat/Miss Analysis

For each key metric, determine:

```
Metric: Revenue
Consensus Estimate: $X.XXM
Reported: $X.XXM
Variance: $+X.XXM / +X%
Beat/Miss: BEAT / MISS / IN-LINE
```

**Table format for beat/miss:**

| Metric | Consensus | Actual | Variance | Beat/Miss |
|--------|-----------|--------|----------|-----------|
| Revenue | $X.XM | $X.XM | +X% | BEAT |
| Adj. EBITDA | $X.XM | $X.XM | -X% | MISS |
| Adj. EPS | $X.XX | $X.XX | +X% | BEAT |

### 2.2 Segment / Geographic Breakdown

Always analyze:
- Revenue by segment (product/ geography/ channel)
- Gross margin by segment (if disclosed)
- Key operating metrics specific to the company

### 2.3 Margin Analysis

```
FY2025 Gross Margin: XX.X% (+Xpp YoY)
  → Driver: [Mix shift / Pricing / Input costs]
  
FY2025 Adj. EBITDA Margin: XX.X% (-Xpp YoY)
  → Driver: [higher R&D / S&M investment vs. revenue growth]
  
FY2025 Net Margin: XX.X% (vs. XX.X% in FY2024)
```

### 2.4 Guidance Analysis

- Compare new guidance to prior guidance
- Identify changes (raised/ lowed/ maintained)
- Assess whether guidance is conservative or aggressive
- Note consensus vs. company guidance

---

## Phase 3: Chart Generation

**Generate these 8-12 charts per company:**

### Revenue Charts
1. **Quarterly Revenue Trend** — Bar chart: Q1 → Q4, last 8 quarters
   - Add consensus estimate as horizontal line if available
   - Label beat/miss above each bar

2. **Annual Revenue Trend** — Bar chart: last 5 years
   - Show revenue and YoY % growth on dual axis

### Profitability Charts
3. **Adj. EBITDA Margin Trend** — Line chart: quarterly margins
   - Add company margin guidance band if available

4. **Earnings Revision Trail** — Bar chart: estimate revisions over time
   - Current vs. prior estimates side by side

### Segment Charts
5. **Revenue by Segment** — Stacked bar or pie
   - Show mix shift YoY

6. **Geographic Revenue Mix** — Bar or map if applicable

### Valuation Charts
7. **NPV / DCF Scenario** — Table or bar
   - Bull / Base / Bear price targets

8. **Peer Valuation Comparison** — Bar chart: P/E, EV/EBITDA, PS by company
   - Label MiniMax vs. peers

### Key Metrics (company-specific)
9-12. **Operating Metrics** — KPIs unique to the business

**Chart style requirements:**
- Font: Times New Roman 10pt
- Color: Blue (#1F4E79) for primary bars, Grey (#595959) for comparators
- Source footnote: bottom left, Times New Roman 8pt
- No gridlines (or very light grey)
- Y-axis: clear units ($M, %, etc.)

---

## Phase 4: Report Creation

See `references/report-structure.md` for page-by-page templates.

---

## Phase 5: Quality Checklist

**Before delivery, verify:**

- [ ] All data has a source footnote
- [ ] All URLs are clickable hyperlinks (not plain text)
- [ ] Beat/miss analysis cites consensus with date
- [ ] Guidance changes cite current and prior quarter sources
- [ ] Tables are 1-3 only (not comprehensive)
- [ ] Report is 8-12 pages
- [ ] 8-12 charts included
- [ ] Word count 3,000-5,000
- [ ] Sources section at end with all URLs
- [ ] File named: `[Company]_Q[X]_[Year]_Earnings_Update.docx`

**Common mistakes:**
❌ Using earnings release as sole source (need 10-Q/10-K)
❌ Forgetting to update price target
❌ Including full P&L when only summary needed
❌ Missing source footnotes on charts
❌ Plain text URLs instead of hyperlinks