# Cover Template — LSAT LR Blind Review Workbook

> **Last updated 2026-09-28** — Initial release, parameterized for all future `lsat-blind-review` workbook deliveries.

## What this is

A reusable A4 cover PNG template that every LSAT LR Blind Review workbook should ship with. Replaces the previous "single workbook, single cover" ad-hoc workflow with a parametric generator so the cover stays consistent across all deliveries.

Reference image (design language): Kaplan PrepTest 2 cover — clean composition, large `LSAT` mark, single subtitle line, light-gray arc decoration, restrained palette. This template adopts the same visual language but uses the user's `[R.Cap]` brand and `[subtitle · Blind Review]` instead of Kaplan / PrepTest branding.

## Design layout (A4 @ 300 dpi, 2481 × 3508)

```
┌─────────────────────────────────────────────────┐
│                                                  │
│  [R.Cap]                                          │  ← top-left, Arial Black 110pt
│  LSAT PREP                                       │  ← Arial Regular 36pt
│                                                  │
│                                                  │
│                                                  │
│                                                  │
│   LSAT                                           │  ← main title, Arial Black 360pt
│                                                  │
│                                                  │
│   {subtitle}                                     │  ← parameter, Arial Bold 80pt
│                                                  │
│   Blind Review                                   │  ← Arial Regular 50pt (固定)
│                                                  │
│                                                  │
│  ~~~~~  ← 浅灰弧形装饰（2 条）               📖  │  ← bottom-right book silhouette
│                                                  │
│  R.Cap · J. Hu · Blind Review · {year}            │  ← bottom-left meta, 32pt
└─────────────────────────────────────────────────┘
```

### 固定元素（每个 workbook 一致）

| 元素 | 位置 | 字体 / 颜色 / 尺寸 |
|---|---|---|
| `[R.Cap]` logo | top-left (180, 220) | Arial Black 110pt, black |
| `LSAT PREP` sub-logo | top-left (180, 360) | Arial Regular 36pt, black |
| `LSAT` main title | center-left (180, 1200) | Arial Black 360pt, black |
| `Blind Review` 用途标识 | center-left (180, 1980) | Arial Regular 50pt, black |
| 浅灰弧形 swoosh × 2 | background | `#d9d9d9`, width 80 / 60 |
| 右下角书本剪影 | bottom-right | 几何外框 `#888888` width 8 |
| 底部 meta `R.Cap · J. Hu · Blind Review · {year}` | bottom-left (180, H-180) | Arial Regular 32pt, `#666666` |

### 参数化元素（每次生成传入）

| 字段 | 类型 | 示例 |
|---|---|---|
| `subtitle` | str | `PrepTest 01 · Section 3 & 4` / `Day 1` / `Principle Identify · Section 3` |
| `year` | int (optional) | `2026`；默认取本地系统年 |

## Red lines（不可触犯）

1. **封面不含版本号 v1**。版本号仅出现在文件名 `_v{n}.docx`，属于文件名元数据，不入封面。
2. **封面只有一页**。不要在封面加额外段、QR code、二维码或其他内容；保持 Kaplan PrepTest 2 的极简风格。
3. **不用真实书本照片**。避免版权问题；统一用几何书本剪影。
4. **不用 Kaplan / LSAC 等真实品牌名**。封面只用 `[R.Cap]` + `LSAT PREP`。
5. **不写明用户错题数 / Section 长度 / 题型统计**。封面只做 brand + 范围标识，不暴露内部数据。

## Usage

### CLI

```bash
python /Users/log/.agents/skills/lsat-blind-review/scripts/render_cover.py \
    "PrepTest 01 · Section 3 & 4" \
    /Users/log/LSAT_LR_PT01_cover.png \
    2026
```

### As a Python function

```python
from pathlib import Path
from render_cover import render_cover

render_cover(
    subtitle="PrepTest 01 · Section 3 & 4",
    output_path=Path("/Users/log/LSAT_LR_PT01_cover.png"),
    year=2026,  # optional, defaults to current year
)
```

### Subtitle naming convention

The `subtitle` parameter should match the workbook scope (no version suffix):

| Scope 标识 | subtitle 写法 |
|---|---|
| `LSAT_LR_PT01_Section3_Section4_Blind_Review_解析_v1.docx` | `PrepTest 01 · Section 3 & 4` |
| `LSAT_LR_PT109_Section3_Blind_Review_解析_v1.docx` | `PrepTest 109 · Section 3` |
| `LSAT_LR_Day1_Blind_Review_解析_v1.docx` | `Day 1` |
| `LSAT_LR_Principle_Identify_Section3_Blind_Review_解析_v1.docx` | `Principle Identify · Section 3` |

The docx filename carries `_v{n}`; the cover PNG mirrors the file stem without the version suffix.

## Insert cover into docx as page 1（默认行为，2026-09-28 起所有 workbook 必做）

每交付一个 workbook 必须把 cover PNG 嵌入为 docx 第 1 页（不再是可选）。用 `scripts/insert_cover.py` 或直接调 python-docx：

```python
from pathlib import Path
from docx import Document
from docx.shared import Cm
from docx.enum.text import WD_BREAK

PATH = "/Users/log/LSAT_LR_<scope>_Blind_Review_解析_v{n}.docx"
COVER = "/Users/log/LSAT_LR_<scope>_cover.png"

doc = Document(PATH)
first_p = doc.paragraphs[0]

# Insert cover page BEFORE the existing first paragraph
cover_p = first_p.insert_paragraph_before("")
run = cover_p.add_run()
run.add_picture(COVER, width=Cm(17.0))  # A4 width = 21cm − 2cm × 2 margin
cover_p.add_run().add_break(WD_BREAK.PAGE)

doc.save(PATH)
```

**Do NOT** rebuild the workbook content — only prepend the cover PNG + page break. The existing 4-part structure (Part I Blind Review / Part II 速览表 + 4 段式 / Part III 弱势报告) and the `LSAT LR · <scope> · Blind Review Workbook v{n}` header line stay intact on page 2.

`scripts/insert_cover.py` 完整脚本参数化：`python insert_cover.py <workbook.docx> <cover.png>`；新 workbook 直接命令行调用复用。

## Dependencies

- Python 3.8+
- Pillow (`pip3 install Pillow`)
- macOS system fonts at `/System/Library/Fonts/Arial*.ttf` and `/System/Library/Fonts/Supplemental/Arial Black.ttf`

For non-macOS hosts, adjust `_FONTS` in `render_cover.py` to point at local Arial / Liberation Sans / DejaVu Sans equivalents.

## Validation

After generating a cover, confirm:

```bash
file LSAT_LR_<scope>_cover.png
# → PNG image data, 2481 x 3508, ...

python3 -c "from PIL import Image; im = Image.open('LSAT_LR_<scope>_cover.png'); print(im.size, im.mode)"
# → (2481, 3508) RGB
```

Visual self-check (open in Preview / Finder Quick Look):

- LSAT 主标题超大、居左
- 副标题 `PrepTest 01 · Section 3 & 4` 在 LSAT 下方
- `Blind Review` 在副标题下方
- `[R.Cap]` + `LSAT PREP` 在左上
- 两条浅灰弧形装饰可见但不抢戏
- 右下角有书本剪影
- 底部左下角 meta 行
- **不**含 `v1` 或任何版本号

## Related

- `SKILL.md` — overall skill, references this template from "What this skill produces"
- `references/output-format.md` §3.1 — describes the page-1 header line that follows the cover in the docx
- `scripts/render_cover.py` — the implementation