---
name: limit-up-table
description: Convert a Chinese A-share limit-up stock table image (涨停个股表) into a styled Excel (.xlsx) file. The skill is triggered when the user provides a single image URL (typically hosted at cdn.jiuyangongshe.com or similar) and asks to convert it into an Excel table. The output applies a fixed column layout — 板块 | 涨停时间 | 个股-代码 | 板数 | 流通市值(亿) | 成交额(亿) | 涨停关键词 — with "{name}-{code}" merged into one cell, sectors derived from the image's section headings, sector rows highlighted with random soft pastel colors, header in deep-blue with white bold text, and row 1 frozen. Use this skill whenever the user pastes such an image link and says "处理成excel表格", "做成excel", "导出表格", "做个xlsx", or similar.
---

# limit-up-table — Image → 涨停个股表.xlsx

This skill turns one user-supplied image URL into a single styled Excel
file. The output format is **baked in** (see `references/format-spec.md`);
do not improvise column order or merge rules.

## When to use

Invoke this skill when **all** of the following hold:

1. The user provides exactly one image URL (HTTP/HTTPS).
2. The image is a Chinese A-share limit-up recap — it shows a table with
   columns resembling 板数 / 代码 / 个股 / 涨停时间 / 流通市值 / 成交额 /
   涨停关键词, organised into themed sections (the section headings —
   e.g. 医疗医药, AI硬件, 公告 — define the `板块` column in the
   output).
3. The user wants an Excel (`.xlsx`) file as the deliverable.

If any of these is missing, ask the user for clarification **before**
proceeding.

## What you produce

A single file `涨停个股表.xlsx` in the current working directory. The
layout is fixed:

```
| 板块 | 涨停时间 | 个股-代码    | 板数    | 流通市值(亿) | 成交额(亿) | 涨停关键词 |
|------|----------|--------------|---------|--------------|------------|------------|
| 医疗 | 9:48:18  | 誉衡药业-002437 | 10天6板 | 99.3         | 22.2       | 创新药+... |
| 医疗 | 9:30:04  | 神奇制药-600613 | 6天5板  | 41           | 5.1        | 医药+...   |
```

Full spec: read `references/format-spec.md` first. It is the single
source of truth for headers, merge rule, colors, widths, freeze pane,
and number format.

## Workflow

The skill has four deterministic steps. Do them in order; do not skip
the verification step at the end.

### Step 1 — Download the image (only if needed)

`images_understand` accepts both URLs and local paths. Try the URL
directly first:

```python
mcp__matrix__images_understand(
    image_info=[{
        "url":  "<user image URL>",
        "prompt": "<see Step 2>",
    }],
)
```

If the URL is blocked or returns a transport error, download to
`data/source_image.png` and retry with `"file": "data/source_image.png"`.

### Step 2 — Extract rows with vision

Use the `images_understand` tool with this exact prompt. The prompt is
intentionally exhaustive so the model returns *every* row with every
field, in tabular form. **Do not shorten it.**

```
This is a Chinese A-share limit-up recap table. Extract EVERY row.

For each row, give me:
  - sector   : the section heading under which this stock is grouped
               in the image. Use the EXACT heading text shown in the
               image — do NOT normalise it to a fixed list. Common
               headings include 医疗医药, AI硬件, 大消费, 消费电子,
               贵金属, 房地产链, 半导体, 机器人, 公告, 其他, but
               any other heading the image shows is also valid.
  - name     : 个股 / stock name (e.g. 誉衡药业)
  - code     : 代码 / ticker, 6 raw digits, no .SH/.SZ/.BJ suffix
               (e.g. 002437 — strip any exchange suffix)
  - time     : 涨停时间 in HH:MM:SS (e.g. 9:48:18)
  - board    : 板数 verbatim, e.g. "1", "2天2板", "10天6板"
  - mcap     : 流通市值(亿) as a JSON number (e.g. 99.3)
  - turnover : 成交额(亿) as a JSON number (e.g. 22.2)
  - keywords : 涨停关键词 verbatim

Return ONLY a single JSON object of the form:
{
  "rows": [
    {"sector": "...", "name": "...", "code": "...",
     "time": "...", "board": "...", "mcap": 0.0, "turnover": 0.0,
     "keywords": "..."},
    ...
  ]
}

Do not omit any row. If a field is unreadable, use null — do not guess.
```

Verify the returned JSON has a `rows` array and that `len(rows) > 0`.
If empty, **stop** and tell the user the image was not recognised as a
limit-up table.

### Step 3 — Write JSON and run the build script

Save the extracted rows to `data/limit_up_rows.json`:

```python
import json, pathlib
pathlib.Path("data").mkdir(exist_ok=True)
pathlib.Path("data/limit_up_rows.json").write_text(
    json.dumps({"rows": rows}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
```

Then invoke the skill's build script:

```bash
python /workspace/.minimax/skills/limit-up-table/scripts/build_from_json.py \
  data/limit_up_rows.json \
  data/涨停个股表.xlsx
```

The script applies every rule from `references/format-spec.md`
deterministically — you do not need to set column widths, fills,
alignment, freeze pane, or the merged `{name}-{code}` cell yourself.
**Sector colors are picked at random per run** from a soft pastel
palette; the build script handles that, not the LLM.

### Step 4 — Verify and deliver

Before handing the file to the user, read it back and confirm:

```python
from openpyxl import load_workbook
wb = load_workbook("data/涨停个股表.xlsx")
ws = wb.active
assert ws.title == "涨停个股"
assert ws.freeze_panes == "A2"
assert [c.value for c in ws[1]] == [
    "板块", "涨停时间", "个股-代码", "板数",
    "流通市值(亿)", "成交额(亿)", "涨停关键词",
]
# Spot-check: the merged cell is "name-code"
assert ws["C2"].value == f"{name1}-{code1}"
# Spot-check: numeric format
assert ws["E2"].number_format == "0.0"
# Spot-check: each sector has a fill assigned
sectors = {ws.cell(row=r, column=1).value for r in range(2, ws.max_row + 1)}
fills   = {ws.cell(row=r, column=1).fill.start_color.rgb for r in range(2, ws.max_row + 1)}
assert len(fills) >= 2, "expected ≥2 distinct sector fills, got " + str(fills)
print("OK", ws.max_row - 1, "data rows across", len(sectors), "sectors")
```

Note: do **not** assert specific sector colors — they are random and
will differ between runs. Only assert that each sector has a non-white
fill.

If any assertion fails, fix the JSON and re-run. Do not ship an
unverified file.

Finally, deliver with the standard `<deliver_assets>` block pointing at
`data/涨停个股表.xlsx`.

## Format reference (quick lookup)

| Rule | Value |
|------|-------|
| Sheet name        | `涨停个股` |
| Header fill       | `#305496` (white bold text) |
| Merge rule        | `"{name}-{code}"` in column C |
| Column order      | 板块 / 涨停时间 / 个股-代码 / 板数 / 流通市值(亿) / 成交额(亿) / 涨停关键词 |
| Numeric format    | `0.0` for E and F |
| Freeze pane       | `A2` |
| Sector (板块)     | derived from image; no fixed list |
| Sector colors     | random soft pastel per run (see `format-spec.md` §3.1) |
| Output filename   | `涨停个股表.xlsx` |

## What this skill does NOT do

- It does not fetch the image without the user's URL.
- It does not invent rows the image does not show.
- It does not change the column order, merge rule, or filename. Those
  are the user's contract with the skill.
- It does not post to IM, upload to cloud storage, or call any API
  beyond `images_understand` and local Python.
- It does not assign sector colors deterministically — colors are
  picked at random per run for visual variety; only the *existence* of
  a non-white fill per sector is guaranteed.
