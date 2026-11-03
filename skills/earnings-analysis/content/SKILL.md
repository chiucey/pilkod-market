---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e526d2a7bbe9ee1f379cec96a7e31770
    PropagateID: e526d2a7bbe9ee1f379cec96a7e31770
    ReservedCode1: 3045022100fca662c7409742de4670a82a3b769df570ff93897908d5c358de8566e9fb9c5a02206dd7a23abb49b70bb3b4edc1acd938471504aa62eb8663447d0214d02448224b
    ReservedCode2: 3045022016e0e53f66dac135514048011849707e180953c8e2d94823a85c9eaab3d39902022100daaf94cdd001eaecfe2a06044d5e77107520612b1a10da6996900e356e726023
---

# SKILL.md — Earnings Analysis Skill

**Skill Name:** earnings-analysis
**Trigger Phrases:** "earnings update", "quarterly update", "Q1/Q2/Q3/Q4 results", "post-earnings report", "earnings analysis"
**Output:** 8-12 page DOCX report

---

## Activation

**Use when user says (or implies):**
- "Create an earnings update for [Company] Q[X] [Year]"
- "Analyze [Company]'s quarterly results"
- "Post-earnings report for [Company]"
- "Q[X] update for [Company]"

**Do NOT use if:**
- User requests "initiation report" → different skill
- User requests "flash note" or "quick take" → different format
- Company not already covered → need initiation first

---

## Workflow

```
Phase 1: Data Collection (30-60 min)
  → Search latest earnings (news search)
  → Verify release date within 3 months
  → Collect: 10-Q/10-K + Earnings Release + Transcript + Presentation

Phase 2: Analysis (2-3 hrs)
  → Beat/miss analysis per key metric
  → Segment/geographic breakdown
  → Margin and guidance analysis
  → Update financial estimates

Phase 3: Chart Generation (1-2 hrs)
  → 8-12 charts: revenue trends, margins, valuation, peer comparison

Phase 4: Report Creation (2-3 hrs)
  → 8-12 page DOCX per page-by-page template

Phase 5: Quality Check (30 min)
  → Verify sources, hyperlinks, beat/miss analysis, estimates
```

---

## Critical Rules

### ⏰ Timing
- Publish within **24-48 hours** of earnings release
- Focus on **what's NEW** — don't rehash company background
- User has already seen the initiation — assume familiarity

### 📊 Format
- **Length:** 8-12 pages
- **Word count:** 3,000-5,000 words
- **Tables:** 1-3 summary only (NOT comprehensive)
- **Charts:** 8-12 embedded
- **Font:** Times New Roman throughout

### 🔗 Citations — MANDATORY

**Every figure and table must have a source footnote.**

Example:
```
Source: MiniMax FY2025 Annual Results (March 2, 2026)
[Link: https://finance.yahoo.com/news/minimax-announces-full-2025-financial-...]
```

**Sources section must be at the END with clickable hyperlinks.**

Required minimum sources:
1. Earnings release (with URL and date)
2. 10-Q or 10-K (EDGAR link preferred)
3. Earnings call transcript (with date)

---

## Tool Usage

### batch_web_search
```
Queries for earnings search:
1. "[Company] [ticker] earnings Q[X] [year] results"
2. "[Company] latest quarterly results [year]"
3. "[Company] Q[X] [year] earnings release"
```
Use `search_type="news"` for recency.

### extract_content_from_websites
Extract earnings releases, transcripts, presentations.

### DOCX Creation
Use Python `zipfile` approach (raw XML) — no external DOCX libraries needed:

```python
import zipfile
DOC = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:body>[content]</w:body></w:document>'
)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', CT)
    z.writestr('_rels/.rels', ROOT_RELS)
    z.writestr('word/document.xml', DOC)
    z.writestr('word/styles.xml', STYLES)
    z.writestr('word/_rels/document.xml.rels', RELS)
```

---

## Report Structure (8-12 pages)

| Page | Content |
|------|---------|
| 1 | Investment Summary + Rating + PT + Key Takeaways |
| 2 | Detailed Beat/Miss Analysis |
| 3 | Segment & Margin Analysis |
| 4 | Key Metrics + Updated Guidance |
| 5 | Updated Investment Thesis |
| 6 | Valuation + DCF Scenarios |
| 7 | Updated Financial Estimates |
| 8-10 | Charts Gallery (8-12 charts) |
| 11-12 | Appendix (optional) |

---

## References

- `references/workflow.md` — Phase 1-5 step-by-step procedures
- `references/report-structure.md` — Page-by-page template with table formats
- `references/best-practices.md` — Quality checklist, common mistakes, color coding

---

## Output File

**Name:** `[Company]_[Ticker]_Q[X]_[Year]_Earnings_Update.docx`
**Example:** `MiniMax_03696.HK_Q4_2025_Earnings_Update.docx`
**Save to:** `/workspace/`

---

## ⚠️ CRITICAL FAILURE MODES

1. **Using stale training data** → Always search for latest earnings first
2. **No source footnotes** → Every figure/table MUST cite a source
3. **Plain text URLs** → All links must be clickable hyperlinks
4. **Too many tables** → 1-3 only, not comprehensive P&L
5. **No thesis connection** → Every update must answer "so what?"
6. **Missing PT update** → Always revisit PT after earnings
7. **Ignoring deceleration** → Always flag slowing growth trends