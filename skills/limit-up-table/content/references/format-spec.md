# Format Spec — 涨停个股表.xlsx

The deliverable produced by this skill is a single `.xlsx` file. This document
defines the *exact* layout the skill promises. Any deviation is a bug.

## 1. Column order (left → right)

| # | Column       | Source field        | Notes                                       |
|---|--------------|---------------------|---------------------------------------------|
| 1 | 板块         | `sector`            | **Derived from the image's section heading**; not a fixed list |
| 2 | 涨停时间     | `time`              | Format `HH:MM:SS` (24h)                     |
| 3 | 个股-代码    | `name` + `code`     | **Merged** as `"{name}-{code}"`             |
| 4 | 板数         | `board`             | e.g. `1`, `2天2板`, `10天6板`                |
| 5 | 流通市值(亿) | `mcap`              | Number, 1 decimal place                     |
| 6 | 成交额(亿)   | `turnover`          | Number, 1 decimal place                     |
| 7 | 涨停关键词   | `keywords`          | `+`-separated theme tags                    |

> Column 1 (`板块`) is the *grouping* key. It is **not** present as a
> column in the source image; the build script copies the section
> heading that the row belongs to (e.g. `医疗医药`, `AI硬件`, `公告`,
> or any other heading the image shows). The vision-extraction prompt
> must record the **exact** heading text per row — do not normalise
> the strings to a fixed enumeration.

## 2. Merge rule

The third column is **not** a copy of `name` or `code`; it is the single cell
`{name}-{code}`:

```
誉衡药业-002437
神奇制药-600613
澳洋健康-002172
```

The stock code is written as 6 raw digits, **without** any exchange suffix
(`.SH`, `.SZ`, `.BJ`).

## 3. Styling

| Element             | Value                                |
|---------------------|--------------------------------------|
| Font (body)         | Calibri 11                           |
| Font (header)       | Calibri 11, bold, white              |
| Header fill         | `#305496` (deep blue)                |
| Body borders        | thin `#BFBFBF` on all 4 sides        |
| Body text alignment | center for sector/time/board; left for merged/keywords; right for numerics |
| Number format       | `0.0` for mcap and turnover          |
| Freeze panes        | row 1                                |
| Sheet name          | `涨停个股`                           |

### 3.1 Sector background colors — random

Each unique `板块` value is assigned a **random soft pastel** background
fill. The rules:

- One unique color per sector (all rows of a sector share the same
  fill).
- Colors are sampled at random per run from a soft-pastel palette
  (HSL with high lightness, low-to-moderate saturation). Two sectors
  in the same run may coincidentally get the same color, but distinct
  sectors are more likely than not to look different.
- The color choice is **not** part of the contract — the only contract
  is that (a) every sector has a non-white fill, and (b) the contrast
  with `#000000` text is reasonable.
- If the user wants a deterministic palette later, the build script
  is the only file to change; this spec stays the same.

### 3.2 Why random?

A fixed palette would force the spec to enumerate every possible
sector name. Since the `板块` value is image-derived, the sector set
is open-ended and varies per source image. Random assignment keeps the
contract minimal and avoids stale color tables.

## 4. Column widths

| Column | Width |
|--------|-------|
| A (板块)        | 14 |
| B (涨停时间)    | 14 |
| C (个股-代码)   | 22 |
| D (板数)        | 12 |
| E (流通市值)    | 14 |
| F (成交额)      | 14 |
| G (涨停关键词)  | 50 |

## 5. JSON input contract (for `scripts/build_from_json.py`)

```json
{
  "rows": [
    {
      "sector":   "医疗医药",
      "name":     "誉衡药业",
      "code":     "002437",
      "time":     "9:48:18",
      "board":    "10天6板",
      "mcap":     99.3,
      "turnover": 22.2,
      "keywords": "创新药+CDMO+降脂药+化学药+中成药"
    }
  ]
}
```

All fields are **required**. `mcap` and `turnover` are JSON numbers; all
others are JSON strings. `code` is the 6-digit numeric string, no suffix.

The `sector` field carries the **exact** section heading from the image
(verbatim, no normalisation). It is the build script's job to discover
the unique sector set and assign colors.

## 6. Output filename

`涨停个股表.xlsx`, written next to the input JSON by default.
