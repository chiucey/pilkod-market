---
name: mck-ppt-design
description: >-
  Create professional McKinsey/BCG/Bain consulting-grade PowerPoint presentations
  using MckEngine Python library. Use when users ask to create slides, pitch decks,
  strategy decks, quarterly reviews, board presentations, business proposals, consulting
  deliverables, or any professional PPTX with consultant-style design. Supports 65+
  layout patterns (cover, TOC, charts, matrices, timelines, dashboards), BLOCK_ARC native
  charts, automated QA pipeline, and CJK font handling. AI calls eng.cover(), eng.donut(),
  eng.timeline() etc. NOT for simple text-to-PPT conversion without design requirements.
---

# McKinsey PPT Design Framework

> **Version**: 2.3.3 · **License**: Apache-2.0 · **Author**: Kaku Li (likaku)
> **Python Runtime**: mck_ppt/ engine with 67 high-level methods

## When to Use

**Use this skill when:**
1. User asks to create presentations (pitch decks, strategy, quarterly reviews, board meetings)
2. Consulting-style design required (minimalist, flat, no shadows)
3. Data visualization needed (charts, matrices, dashboards)
4. Chinese + English mixed content (CJK font handling)
5. Professional slide templates required (65+ layout patterns)

**Do NOT use when:**
- Simple text-to-PPT without design requirements
- Non-PPTX output needed (use HTML presentation skill)
- User only needs basic slides without consulting aesthetics

## Quick Start

### Setup
```bash
pip install python-pptx lxml
```

### Core Pattern
```python
import sys, os
sys.path.insert(0, '/workspace/temp-skills/mck-ppt-design')
from mck_ppt import MckEngine
from mck_ppt.constants import *

eng = MckEngine(total_slides=12)

# Structure
eng.cover(title='Q1 2026 战略回顾', subtitle='董事会汇报')
eng.toc(items=[('1', '市场概览', '当前竞争格局'),
               ('2', '财务分析', '营收与利润趋势')])

# Content slides
eng.section_divider(section_label='第一部分', title='市场概览')
eng.big_number(title='市场规模', number='¥850亿', description='2026年预估总量')
eng.donut(title='市场份额', segments=[(0.35, NAVY, '我们'), (0.25, ACCENT_BLUE, '竞品A')])
eng.grouped_bar(title='季度趋势', categories=['Q1','Q2','Q3'], series=[('产品', NAVY)], data=[[120,145,160]])

# Closing
eng.closing(title='谢谢')

eng.save('output/deck.pptx')
```

## Design Principles

### McKinsey Style
1. **Extreme Minimalism** - Remove all non-essential elements
2. **Consistency** - Unified colors (NAVY #051C2C), fonts (Georgia/Arial), spacing
3. **Hierarchy** - Title (22pt) → Sub-header (18pt) → Body (14pt) → Footnote (9pt)
4. **Flat Design** - No shadows, gradients, or 3D effects

### Color System
| Token | Hex | Usage |
|-------|-----|-------|
| NAVY | #051C2C | Primary titles, key elements |
| ACCENT_BLUE | #006BA6 | Charts, highlights |
| ACCENT_GREEN | #007A53 | Positive indicators |
| ACCENT_ORANGE | #D46A00 | Warnings, attention |
| ACCENT_RED | #C62828 | Critical alerts |
| BG_GRAY | #F2F2F2 | Backgrounds, bars |
| DARK_GRAY | #333333 | Body text |

## Layout Categories (65+ Patterns)

### Structure (#1-5)
| Method | Use Case |
|--------|----------|
| `eng.cover()` | Title slide with optional AI-generated image |
| `eng.toc()` | Table of contents with numbered items |
| `eng.section_divider()` | Chapter transition slides |
| `eng.closing()` | Thank you / end slide |

### Data & Statistics (#6-12)
| Method | Use Case |
|--------|----------|
| `eng.big_number()` | Single impactful metric |
| `eng.two_stat()` | Side-by-side KPIs |
| `eng.three_stat()` | Three key indicators dashboard |
| `eng.data_table()` | Structured data rows |
| `eng.metric_cards()` | 3-4 parallel metric cards |

### Frameworks (#13-18)
| Method | Use Case |
|--------|----------|
| `eng.matrix_2x2()` | BCG matrix, priority grid |
| `eng.staircase()` | Evolution phases with icons |
| `eng.process_chevron()` | 3-5 step linear flow |
| `eng.venn()` | Concept intersections |

### Charts (#37-39, #48-56)
| Method | Use Case |
|--------|----------|
| `eng.donut()` | Part-of-whole with center label |
| `eng.pie()` | Simple part-of-whole |
| `eng.gauge()` | KPI health indicator |
| `eng.grouped_bar()` | Multi-category comparison |
| `eng.stacked_bar()` | Part-to-whole over time |
| `eng.horizontal_bar()` | Category ranking |
| `eng.line_chart()` | Multi-series trends |

### Dashboards (#57-58)
| Method | Use Case |
|--------|----------|
| `eng.dashboard_kpi_chart()` | KPIs + chart + takeaways |
| `eng.dashboard_table_chart()` | Table + chart + factoids |

## Chart Rendering (BLOCK_ARC)

**CRITICAL**: Always use BLOCK_ARC for circular charts (donut, pie, gauge).

```python
# WRONG: Block stacking (v1.x legacy)
for angle in range(0, 360):
    add_rect(slide, x + cos(angle)*r, ...)  # 2,800 shapes!

# CORRECT: Native BLOCK_ARC (v2.0+)
eng.donut(title='Revenue', segments=[(0.45, NAVY, 'A'), (0.35, ACCENT_BLUE, 'B')])
# 3-4 shapes only, <1 sec render time
```

## Production Guard Rails

| # | Rule | Why |
|---|------|-----|
| 1 | Never use connectors | File corruption from connector p:style |
| 2 | Always call `_clean_shape()` | Prevent shadow/3D artifacts |
| 3 | Run `full_cleanup()` after save | Remove residual theme effects |
| 4 | Set `set_ea_font()` on CJK text | Chinese characters rendering as boxes |
| 5 | Use `add_hline()` not `add_line()` | Connector-based lines cause repair prompts |
| 6 | Dynamic sizing for variable-count | 3 vs 7 items need different spacing |
| 7 | Post-generation QA gate | 0 ERROR mandatory before delivery |

## QA Pipeline (v2.3)

### Auto-fix Priority Chain
1. Remove redundancy (weak hedging, filler phrases)
2. Compress sentences ("因为A所以B" → "A→B")
3. Restructure (trim excess clauses)
4. Font micro-adjust (shrink 1pt/round, floor: title≥20pt, body≥11pt)

### Usage
```python
from mck_ppt.review import autofix

result = autofix('output/deck.pptx', max_rounds=5)
result.print_summary()  # ✅ PASS or ❌ FAIL
```

## CJK Font Handling

Chinese text requires explicit font setting:
```python
from mck_ppt.core import set_ea_font

for run in paragraph.runs:
    set_ea_font(run, 'KaiTi')  # Automatic in engine methods
```

## Typography Constants

| Constant | Size | Usage |
|----------|------|-------|
| COVER_TITLE_SIZE | 44pt | Cover page titles |
| SECTION_TITLE_SIZE | 28pt | Section headers |
| ACTION_TITLE_SIZE | 22pt | Slide action titles |
| SUB_HEADER_SIZE | 18pt | Sub-headers |
| BODY_SIZE | 14pt | Body text |
| FOOTNOTE_SIZE | 9pt | Source attributions |

## Slide Dimensions

- **Standard**: 16:9 (13.333" × 7.5")
- **Left Margin**: 0.8"
- **Right Margin**: 0.8"
- **Content Width**: 11.733"
- **Title Area**: Top 1.3" of slide

## File References

- Detailed layout specs: `references/layout-catalog.md`
- Color palette: `references/color-palette.md`
- Python engine: `mck_ppt/` (see `__init__.py` for public API)
- Examples: `examples/` directory

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chinese text renders as boxes | Call `set_ea_font()` on all runs |
| File "needs repair" on open | Run `full_cleanup()` after save |
| Text overflow | Use QA auto-fix pipeline |
| Font inconsistency | Run peer harmonization |
| Slow chart rendering | Use BLOCK_ARC, not block stacking |
