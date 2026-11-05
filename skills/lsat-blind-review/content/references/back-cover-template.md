# Back Cover Template — LSAT LR Blind Review Workbooks

> **Added 2026-09-28** — Reusable A4 back cover PNG template for all future `lsat-blind-review` workbook deliveries.

## What this is

A reusable A4 back cover PNG template that **every** LSAT LR Blind Review workbook should ship with — but only when the workbook's final page count is odd. The back cover contains:

1. A detailed **English-language** workbook introduction (4 sub-sections: WHAT THIS IS / METHODOLOGY / HOW TO USE / CAVEAT).
2. A standard copyright block.
3. R.Cap + author + year meta.

All text rendered at **≤9pt** per user 2026-09-28 preference. The total word count of the introduction (4 sub-sections + sub-section titles + top R.Cap / LSAT PREP) is **≤350 words**.

## Design layout (A4 @ 300 dpi, 2481 × 3508)

```
┌─────────────────────────────────────────────────┐
│  R.Cap                                          │  ← Arial Bold 9pt
│  LSAT PREP                                     │  ← Arial Regular 9pt
│  ─────────────────────────────────────         │  ← 水平分隔线（黑色 1pt）
│                                                 │
│  ABOUT THIS WORKBOOK                            │  ← Arial Bold 9pt
│                                                 │
│  The Blind Review Workbook you are reading is  │  ← Arial Regular 9pt
│  a 7Sage-style compilation of argument-by-     │
│  argument analysis for the user's wrong answers │
│  on LSAT PrepTest N, Section X.                │
│                                                 │
│  METHODOLOGY                                    │  ← Arial Bold 9pt
│                                                 │
│  Each wrong question is reduced to a four-     │  ← Arial Regular 9pt
│  section annotation: question type + task,     │
│  stimulus structure, why the correct answer     │
│  closes the argument, and a transferable pattern │
│  that recurs across LSAT items.                 │
│                                                 │
│  HOW TO USE                                    │  ← Arial Bold 9pt
│                                                 │
│  Read Part I blind, without referring to Part  │  ← Arial Regular 9pt
│  II. Then verify with Part II's speed table    │
│  and per-question 4-section analysis. Read Part │
│  III for cross-question weakness patterns.       │
│                                                 │
│  CAVEAT                                         │  ← Arial Bold 9pt
│                                                 │
│  The 4-section analysis is one practitioner's   │  ← Arial Regular 9pt
│  opinionated reading; use it as a study aid,    │
│  not as the only source of truth. Where public  │
│  prep sites disagree, trust them.               │
│                                                 │
│  ─────────────────────────────────────         │  ← 水平分隔线（黑色 1pt）
│                                                 │
│  © 2026 J. Hu. All rights reserved.             │  ← Arial Bold 9pt
│  Unauthorized reproduction or distribution of   │  ← Arial Regular 9pt
│  this document, in whole or in part, is         │
│  strictly prohibited without the prior written  │
│  consent of the author.                        │
│                                                 │
│  R.Cap · J. Hu · {year}                        │  ← Arial Regular 9pt
└─────────────────────────────────────────────────┘
```

## Font rules (all ≤9pt)

| Element | Font | Size |
|---|---|---|
| Top R.Cap / LSAT PREP | Arial Bold / Regular | 9pt |
| Section titles (ABOUT / METHODOLOGY / HOW TO USE / CAVEAT) | Arial Bold | 9pt |
| Body paragraphs | Arial Regular | 9pt |
| Separator | 1pt black horizontal line | — |
| Copyright first line (© 2026 J. Hu ...) | Arial Bold | 9pt |
| Copyright continuation (Unauthorized ...) | Arial Regular | 9pt |
| Bottom meta (R.Cap · J. Hu · {year}) | Arial Regular | 9pt |

**Paragraph spacing**: 8pt before / 4pt after, line spacing 1.0.

**Total word count constraint (hard)**: `ABOUT THIS WORKBOOK` section (4 sub-sections + sub-section titles + top R.Cap / LSAT PREP) ≤ **350 words**. Default body content fits within 169 words. Use `render_back_cover.py` CLI which auto-checks this.

## Default body content (4 sub-sections)

The default English text shipped in `render_back_cover.py`:

1. **WHAT THIS IS** — Blind Review Workbook introduction (PT N / Section X; Part I/II/III structure).
2. **METHODOLOGY** — Four-section annotation; four canonical wrong-answer buckets (conditional logic / scope control / method recognition / principle matching).
3. **HOW TO USE** — Read Part I blind, then verify with Part II's speed table + per-question 4-section; review Part III for cross-question patterns.
4. **CAVEAT** — One practitioner's opinionated reading; cross-check with public prep sites.

## Red lines (硬约束)

1. **All text ≤9pt** (2026-09-28 user preference). No 10pt / 12pt / 14pt anywhere.
2. **Total word count of the `ABOUT THIS WORKBOOK` section ≤350** (4 sub-section bodies + sub-section titles + top R.Cap / LSAT PREP lines). Copyright + bottom meta not counted.
3. **English only** in body. No Chinese in any sub-section. Title `ABOUT THIS WORKBOOK` is English.
4. **No parenthetical explanations** in body text (`(...)` / `（...）`). Matches the Part III weakness table constraint.
5. **No version number** in back cover (e.g., no `v1`). Consistent with front cover.
6. **No front cover design reuse** — back cover has **no light-gray swoosh arcs**. Functional separation between front and back.
7. **Copyright block is fixed**: `© [Year] J. Hu. All rights reserved. Unauthorized reproduction or distribution of this document, in whole or in part, is strictly prohibited without the prior written consent of the author.` Only the year digit may change.
8. **Odd page count only** — back cover inserted only when workbook page count is odd. Even-page workbooks skip back cover.

## Usage

### CLI

```bash
python /Users/log/.agents/skills/lsat-blind-review/scripts/render_back_cover.py \
    "PrepTest 01 · Section 3 & 4" \
    /Users/log/LSAT_LR_PT01_back_cover.png \
    2026
```

The CLI auto-checks total word count ≤ 350 and exits 1 if exceeded.

### Library

```python
from pathlib import Path
from render_back_cover import render_back_cover, word_count, DEFAULT_BODY

render_back_cover(
    subtitle="PrepTest 01 · Section 3 & 4",
    output_path=Path("/Users/log/LSAT_LR_PT01_back_cover.png"),
    year=2026,
    body=DEFAULT_BODY,  # default; can be overridden
)
```

### Inserting into docx as last page (only if odd)

```bash
python /Users/log/.agents/skills/lsat-blind-review/scripts/insert_back_cover.py \
    /Users/log/LSAT_LR_<scope>_Blind_Review_解析_v1.docx \
    /Users/log/LSAT_LR_<scope>_back_cover.png
```

The script:
1. Converts the docx to PDF via LibreOffice headless, reads `/Pages` metadata.
2. If `page_count % 2 == 1` → appends back cover as last page.
3. Else → skips with informational message (use `--force` to override).

Fallback chain: `soffice + pypdf/pikepdf` → `lastRenderedPageBreak` heuristic.

## Dependencies

- Python 3.8+
- Pillow (`pip3 install Pillow`)
- macOS system fonts at `/System/Library/Fonts/Arial*.ttf`
- Optional (for page count): `soffice` / `libreoffice` + `pypdf` or `pikepdf`

For non-macOS hosts, adjust `_FONTS` in `render_back_cover.py` to point at local Arial / Liberation Sans / DejaVu Sans equivalents.

## Validation

After generating a back cover, confirm:

```bash
file LSAT_LR_<scope>_back_cover.png
# → PNG image data, 2481 x 3508, ...

python3 -c "from PIL import Image; im = Image.open('LSAT_LR_<scope>_back_cover.png'); print(im.size, im.mode)"
# → (2481, 3508) RGB

# ≤9pt hard check (PIL)
python3 -c "
from PIL import Image
import struct
# (font.size check is performed inside render_back_cover.py at CLI level;
#  below is a Pythonic spot-check on the saved PNG)
im = Image.open('LSAT_LR_<scope>_back_cover.png')
print(f'Image OK: {im.size}')
"
```

Word count self-check (CLI auto-runs this):

```bash
python render_back_cover.py "<subtitle>" <out.png> [year]
# Output includes: "ABOUT THIS WORKBOOK 部分 word count = N ≤ 350 ✓"
# Or FAIL with "请精简 DEFAULT_BODY 中的 4 段内容" if exceeded.
```

## Related

- `references/cover-template.md` — Front cover template (separate design; both are 2026-09-28 additions).
- `scripts/render_back_cover.py` — Implementation.
- `scripts/insert_back_cover.py` — Page-count detection + conditional insertion.
- `SKILL.md` — Overall skill, references this template from "What this skill produces".