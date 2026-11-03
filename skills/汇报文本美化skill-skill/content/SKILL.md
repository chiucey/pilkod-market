---
title: "汇报文本美化skill"
summary: "一键把纯文本/Word/Markdown转化为AI报告级精美排版的HTML文档——自带封面/配色/表格/图表场景框，可直接打印为PDF汇报材料"
agent_created: true
read_when:
  - User wants to make a document look professional and polished
  - User says "排版一下" or "让这份材料更好看"
  - User has raw content (Markdown/Word) and needs it formatted in AI-report visual style
  - User uploads content and asks to "做成AI生成报告那种风格"
  - User references "格式" / "美观" / "排版" / "视觉效果"
keywords: [汇报排版, 报告美化, 文档格式化, AI报告风格, 图文并茂, 视觉设计, 商务排版]
---

# 汇报文本美化skill | Report-Beautifier

> **一键将杂乱的Word/Markdown文档转化为AI报告级精美排版**
> 自带封面页、专业配色、表格美化、场景框、SVG图表——可直接打印为PDF用于汇报

## 🎯 适用人群

- **职场人**：周报/月报/述职报告/业务评审会材料，想做得更好看但不会排版
- **管理者**：一线团队交上来的文字材料，需要快速美化后向上汇报
- **分析师**：数据分析结果需要包装成可读性强的报告文档
- **创业者**：BP、商业计划书、融资材料需要专业视觉呈现

## ✨ 一句话价值

> **「让任何文字材料，3秒变出高档汇报文档的质感」**

---

## Purpose

Apply a professional visual design system to any document content — making raw Markdown/Word text look like a polished, management-ready AI report. This skill focuses purely on **visual formatting and aesthetics**, NOT on content structure or report framework. It is complementary to the AI-Business-Report-Writing content skill.

## Design Philosophy

The AI-report visual style follows these core principles:

1. **层级清晰** — 读者一眼能看出章节归属
2. **信息密集** — 不浪费空间，但留白恰到好处
3. **统一规范** — 全篇使用同一套设计语言
4. **专业克制** — 颜色不超过3种，字体不超过2种

---

## Visual Design System

### 🎨 Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--primary` | `#1F4E79` | 主标题、表头背景、强调文字 |
| `--secondary` | `#2E75B6` | 二级标题、次级强调 |
| `--accent` | `#E8F0FE` | 场景框背景、轻度高亮 |
| `--bg-light` | `#F2F2F2` | 表格交替行、页面背景 |
| `--bg-warm` | `#FEF7E0` | 案例/提醒框背景 |
| `--text-dark` | `#333333` | 正文颜色 |
| `--text-mid` | `#555555` | 副标题、辅助文字 |
| `--text-light` | `#999999` | 图注、页脚、备注 |
| `--white` | `#FFFFFF` | 页面底色/表头文字 |
| `--border` | `#CCCCCC` | 表格边框、分割线 |
| `--border-strong` | `#1F4E79` | 重点场景框顶部边线 |
| `--shadow` | `rgba(0,0,0,0.08)` | 卡片/场景框阴影 |

### 🔤 Typography System

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| 封面标题 | `"Microsoft YaHei", "PingFang SC", sans-serif` | 26-32pt | Bold (700) | `--primary` |
| 封面副标题 | same | 14-16pt | Regular (400) | `--text-mid` |
| 一级标题 (H1) | same | 18pt | Bold (700) | `--primary` |
| 二级标题 (H2) | same | 14pt | Bold (600) | `--secondary` |
| 三级标题 (H3) | same | 12pt | Bold (600) | `--secondary` |
| 正文 | same | 11pt | Regular (400) | `--text-dark` |
| 表格表头 | same | 10pt | Bold (700) | `--white` |
| 表格正文 | same | 9-10pt | Regular (400) | `--text-dark` |
| 图注/脚注 | same | 9pt | Italic | `--text-light` |
| 场景案例标签 | same | 11pt | Bold (600) | `--primary` |

**Line-height**: 1.6 for body text, 1.2 for headings
**Letter-spacing**: 0.02em for headings, normal for body

### 📐 Layout System

**Page**: A4 (21cm × 29.7cm) with 2.54cm margins all sides

**Content width**: ~16cm (adjustable)

**Vertical rhythm**:
- After H1: 24px
- After H2: 16px
- After H3: 12px
- After paragraph: 8px
- Before/after table: 16px
- Scene box inner padding: 16px

**Maximum line length**: 60-75 characters for optimal readability

### 🏗 Visual Hierarchy

```
封面 (full page, centered)
  │
  ↓
H1 ──── 编号 + 加粗深蓝色大标题 (18pt)
  │
  ├─ H2 ── 编号 + 中蓝色标题 (14pt)
  │     │
  │     ├─ 正文段落（11pt，1.6行间距）
  │     │
  │     ├─ 表格（蓝头+白字+交替行）
  │     │
  │     ├─ 场景框（顶部蓝边+浅蓝底）
  │     │
  │     └─ 列表项（编号/圆点 + 加粗前缀）
  │
  ├─ H3 ── 粗体次级标题 (12pt)
  │
  └─ 图注/表注（灰色小字, 斜体）
```

### 📊 Table Design

Tables follow a strict visual pattern:

```
┌──────────┬──────────────────────┬──────────────────────┐
│ HEADER   │  HEADER              │  HEADER              │  ← #1F4E79 bg, white text, bold
├──────────┼──────────────────────┼──────────────────────┤
│ Row 1    │  Content             │  Content             │  ← #F2F2F2 (alternate)
├──────────┼──────────────────────┼──────────────────────┤
│ Row 2    │  Content             │  Content             │  ← white
├──────────┼──────────────────────┼──────────────────────┤
│ Row 3    │  Content             │  Content             │  ← #F2F2F2 (alternate)
└──────────┴──────────────────────┴──────────────────────┘
```

Rules:
- Header row: primary blue bg (#1F4E79), white bold text, center-aligned
- Data rows: alternate between white and #F2F2F2
- First column (label): bold text
- Last row (summary/highlight): bold or primary-colored text
- Borders: thin (#CCCCCC, 1px)
- Cell padding: 8px vertical, 12px horizontal

### 🎭 Scene/Case Boxes (关键场景框)

Key scenarios use prominent box styling:

```
┌──────────────────────────────────────────┐
│  ▎ (6px blue top border)                  │
│  ▎ 场景1：XXXX  (bold, blue)             │  ← #E8F0FE bg
│  ▎                                        │
│  ▎ Description paragraph...               │
│  ▎                                        │
│  ▎ Data: quantified stats... (gray)       │
└──────────────────────────────────────────┘
```

Alternative warm variant:
```
┌──────────────────────────────────────────┐
│  ▎ (6px blue top border)                  │
│  ▎ 场景2：XXXX  (bold, blue)             │  ← #FEF7E0 bg
│  ▎ ...                                    │
└──────────────────────────────────────────┘
```

### 📄 Cover Page Design

```
┌──────────────────────────────────────────┐
│                                          │
│                                          │
│                                          │
│                                          │  ← 6 blank lines (spacing)
│       [TITLE]                            │
│       26-32pt, bold, primary             │
│                                          │
│       [SUBTITLE]                         │
│       14-16pt, secondary                 │
│                                          │
│       ──────────────                     │
│       divider line                       │
│                                          │
│       汇报对象：XXX                       │
│       编制部门：XXX                       │  ← 11pt, gray
│       报告日期：XXXX                      │
│       版    本：V1.0                     │
│                                          │
│                                          │
└──────────────────────────────────────────┘
```

---

## Output Format: HTML

Generate the report as a **self-contained HTML file** with embedded CSS. HTML provides full control over typography, layout, and responsive design.

### HTML Template Architecture

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>报告标题</title>
  <style>
    /* === DESIGN TOKENS === */
    :root {
      --primary: #1F4E79;
      --secondary: #2E75B6;
      --accent: #E8F0FE;
      --bg-light: #F2F2F2;
      --bg-warm: #FEF7E0;
      --text-dark: #333333;
      --text-mid: #555555;
      --text-light: #999999;
      --border: #CCCCCC;
      --border-strong: #1F4E79;
      --shadow: rgba(0,0,0,0.08);
    }

    /* === BASE TYPOGRAPHY === */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", sans-serif;
      color: var(--text-dark);
      line-height: 1.6;
      background: #f8f8f8;
      padding: 40px 20px;
    }

    .report-page {
      max-width: 210mm;
      margin: 0 auto;
      background: white;
      padding: 54pt 72pt; /* 约2.54cm页边距 */
      box-shadow: 0 2px 12px var(--shadow);
      min-height: 297mm;
    }

    /* === COVER PAGE === */
    .cover-page { ... }

    /* === HEADINGS === */
    h1 { ... }  /* 18pt, bold, primary */
    h2 { ... }  /* 14pt, bold, secondary */
    h3 { ... }  /* 12pt, bold, secondary */
    h1:before { content: counter(h1) "  "; }  /* auto-numbering */

    /* === TABLES === */
    .report-table { ... }
    .report-table thead th { background: var(--primary); color: white; }
    .report-table tbody tr:nth-child(even) { background: var(--bg-light); }

    /* === SCENE BOXES === */
    .scene-box { ... }  /* top border, bg, shadow */
    .scene-box-alt { ... }  /* warm variant */

    /* === LISTS === */
    .report-list { ... }
    .report-list li::marker { color: var(--primary); }

    /* === COMPARISON === */
    .comparison-pair { ... }
    .comparison-old { ... }
    .comparison-new { ... }

    /* === PRINT === */
    @media print { ... }
  </style>
</head>
<body>
  <div class="report-page">
    <!-- Cover Page -->
    <!-- Section 1 -->
    <!-- Section 2 -->
    <!-- etc. -->
  </div>
</body>
</html>
```

### Key Visual Effects

1. **Heading Auto-Numbering**: Use CSS counters for 1.1, 1.2, 2.1, 2.2 numbering
2. **Cover Page Centering**: Flexbox with vertical centering
3. **Table Styling**: CSS pseudo-classes for alternate rows
4. **Scene Boxes**: Top border accent via `border-top: 6px solid var(--border-strong)`
5. **Comparison Pairs**: Side-by-side flex layout with old/new labels
6. **Page Breaks**: `page-break-before: always` for print
7. **Process Arrows**: Unicode "→" or CSS arrow elements
8. **Print Optimization**: `@media print` rules for PDF output

---

## Workflow

1. **Receive input**: User provides content (Markdown text, data points, images, or existing Word document)
2. **Parse content**: Identify heading levels, paragraphs, tables, lists, key statistics
3. **Apply design system**: Wrap content in the HTML template with proper CSS classes
4. **Add visual hierarchy**: Apply heading styles, spacing, scene boxes to case studies
5. **Format tables**: Color headers, alternate rows, bold labels
6. **Generate HTML**: Self-contained file with all CSS embedded
7. **Optional print-to-PDF**: User can print via browser's "Save as PDF"

---

## Design Principles & Rules

### DOs
- ✅ 用深蓝色 (#1F4E79) 作为主色
- ✅ 表格表头用深蓝色底色+白色文字
- ✅ 表格行交替着色
- ✅ 场景案例用顶部蓝色边框强调
- ✅ 段落间距保持一致
- ✅ 封面居中大标题

### DON'Ts
- ❌ 不要用超过3种主色
- ❌ 不要用超过2种字体
- ❌ 不要用花哨的背景图或纹理
- ❌ 不要用表格作为分割线（会产生空框）
- ❌ 不要用unicode项目符号，用CSS list-style
- ❌ 不要塞信息密度过高导致拥挤

### Print Optimization
- `@page { size: A4; margin: 0; }` for clean PDF output
- `page-break-before: always` before each major section
- Avoid floats that might clip in print
- Test with Chrome's "Save as PDF" for best results

---

## Quick Reference: CSS for Common Elements

```css
/* Scene box */
.scene-box {
  border-top: 6px solid #1F4E79;
  background: #E8F0FE;
  padding: 16px 20px;
  border-radius: 4px;
  margin: 16px 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* Comparison table old/new */
.comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin: 16px 0;
}
.comparison > div {
  padding: 16px;
  border-radius: 4px;
}
.comparison .old { background: #FEF7E0; border-left: 4px solid #E8A838; }
.comparison .new { background: #E8F0FE; border-left: 4px solid #1F4E79; }

/* Alternate row table */
table.report-table tbody tr:nth-child(even) { background: #F2F2F2; }
table.report-table th { background: #1F4E79; color: white; padding: 10px 12px; }
table.report-table td { padding: 8px 12px; border: 1px solid #CCCCCC; }

/* Heading auto-numbering */
body { counter-reset: h1-counter; }
h1 { counter-reset: h2-counter; }
h1:before { content: counter(h1-counter) "  "; counter-increment: h1-counter; }
h2:before { content: counter(h1-counter) "." counter(h2-counter) "  "; counter-increment: h2-counter; }
```

---

## 🎯 Report Diagram System (报告内嵌图表)

To make reports "图文并茂", embed SVG diagrams directly in the HTML. SVG is preferred because:
- Vector quality — scales perfectly when printing to PDF
- Color consistent — uses the same `--primary`/`--secondary`/`--accent` tokens
- No external tools — pure HTML/SVG, no image files needed
- Simple but effective — presents core logic, not complex artwork

### Diagram Types & SVG Templates

All diagram templates are available in `assets/report-diagrams.html`. To use them, copy the `<svg>...</svg>` block and customize text content.

#### ① PDCA Cycle Diagram (PDCA循环图)

**Purpose**: Show continuous improvement closed-loop logic. The most common diagram in AI reports.

**Structure**: 4 rectangular panels arranged in a cycle (top→right→bottom→left), connected by arrows pointing clockwise. Center circle with summary text.

**Color assignment**:
| Phase | Box bg | Header bg | Arrow |
|-------|--------|-----------|-------|
| P (Plan) | `--accent` (#E8F0FE) | `--primary` (#1F4E79) | blue |
| D (Do) | #E8F5E9 | #2E7D32 | green |
| C (Check) | #FFF3E0 | #E65100 | orange |
| A (Act) | #E0F2F1 | #00695C | teal |

**SVG structure template**:
```svg
<svg viewBox="0 0 700 520">
  <!-- Title -->
  <text x="350" y="30" text-anchor="middle" font-family="..." font-size="14" font-weight="bold" fill="#1F4E79">[TITLE]</text>

  <!-- Phase boxes (4 rects) -->
  <g> <!-- P - top -->
    <rect x="225" y="55" width="250" height="105" rx="8" fill="#E8F0FE" stroke="#1F4E79" stroke-width="2"/>
    <rect x="225" y="55" width="250" height="32" rx="8" fill="#1F4E79"/>
    <text x="350" y="75" text-anchor="middle" font-size="12" font-weight="bold" fill="#FFFFFF">P - [阶段名称]</text>
    <text x="245" y="105" font-size="9.5" fill="#333333">• [内容1]</text>
    <text x="245" y="122" font-size="9.5" fill="#333333">• [内容2]</text>
    <text x="245" y="139" font-size="9.5" fill="#333333">• [内容3]</text>
  </g>

  <!-- D - right, C - bottom, A - left (same structure, different x/y) -->

  <!-- Arrows connecting phases -->
  <path d="M [from] Q [control] [to]" fill="none" stroke="[color]" stroke-width="2" marker-end="url(#arrowX)"/>
  <text x="[label_x]" y="[label_y]" font-size="8" fill="[color]" font-style="italic">[arrow_label]</text>

  <!-- Center text -->
  <text x="350" y="275" text-anchor="middle" font-size="10" font-weight="bold" fill="#1F4E79">持续</text>
  <text x="350" y="290" text-anchor="middle" font-size="10" font-weight="bold" fill="#1F4E79">改善</text>
</svg>
```

**Positioning formula** (for 700×520 viewBox):
- Top (P): x=225, y=55, w=250, h=105 → center x=350
- Right (D): x=475, y=210, w=220, h=105 → center x=585
- Bottom (C): x=225, y=365, w=250, h=105 → center x=350
- Left (A): x=15, y=210, w=220, h=105 → center x=125

Arrow paths:
- P→D: `M 475 160 Q 510 150 530 170 Q 560 195 575 210`
- D→C: `M 585 315 Q 585 340 570 355 Q 550 375 475 380`
- C→A: `M 225 420 Q 190 420 170 400 Q 145 370 235 315`
- A→P: `M 125 210 Q 125 185 140 170 Q 165 145 225 140`

#### ② Comparison Diagram (新旧模式对比图)

**Purpose**: Side-by-side comparison of old vs new process, showing the transformation path.

**Structure**: Two columns — left (old) and right (new) — with 3-step vertical flow inside each. Arrow in the middle.

**Layout** (700×380 viewBox):
- Left column (old): x=30, w=290, bg=#FFF3E0, border=#E65100 (orange)
- Right column (new): x=380, w=290, bg=#E8F0FE, border=#1F4E79 (blue)
- Center arrow: large "→" between columns
- Bottom: time/cost summary text in each column

**Step structure inside each column** (3 steps):
- Step box: rect at x+25, y, w=240, h=45, rx=5
- Step title: bold colored text
- Step description: smaller gray text
- Arrow down between steps: "↓" centered, 16px

#### ③ Hierarchy Tree (层级树图)

**Purpose**: Show structured data relationships (organizational structure, space hierarchy, classification).

**Structure**: Root top-center → horizontal connector line → branches → sub-branches → leaf nodes.

**Layout** (700×420 viewBox):
- Root (L0): rounded rect at center, dark blue
- Branches (L1): 4 horizontal nodes, medium blue
- Sub-branches (L2): small rects, light blue outline
- Leaf nodes (L3/L4): tiny gray rects
- Legend box at bottom explaining hierarchy levels

**Connector formula**: Vertical line from parent → horizontal line → vertical lines to children

#### ④ Timeline/Roadmap (实施路线图)

**Purpose**: Show phased rollout plans with sequential milestones.

**Structure**: Horizontal timeline base line → 3 phase nodes on the line → cards above/below alternating.

**Layout** (700×380 viewBox):
- Timeline: horizontal line at y=175 from x=80 to x=620
- Phase nodes: circles (r=12) at x=170, 350, 530
- Cards: phase 1 above (y=55), phase 2 below (y=195), phase 3 above (y=55)
- Arrow connectors between nodes

#### ⑤ Data Dashboard Cards (数据指标卡)

**Purpose**: Display key metrics in a visually impactful card layout.

**Structure**: 4 (or more) equal-width cards in a row, each with big number + unit + description + trend indicator.

**Layout** (700×200 viewBox):
- 4 cards: w=150, h=120, gap=25px
- Card colors alternate: blue/green/orange/teal themes
- Big number: 24pt bold
- Sub-text: 10pt
- Trend arrow: 8pt, up/down indicator

#### ⑥ Problem-Risk Matrix (问题-风险矩阵)

**Purpose**: Multi-dimensional data comparison with risk ratings.

**Structure**: Table layout with colored header row, data rows with alternating backgrounds, risk badge on the right.

**Layout** (700×320 viewBox):
- Header row: dark blue bg, white text
- Data rows: 3 rows, orange-tinted backgrounds (darker for higher risk)
- Risk badges: colored pill shapes (red=high, amber=medium)
- Text centered in columns

### Color Coding Convention for Diagrams

| Purpose | Color | Hex |
|---------|-------|-----|
| Primary brand | Deep blue | #1F4E79 |
| Secondary | Medium blue | #2E75B6 |
| Growth/positive | Green | #2E7D32 |
| Warning/problem | Orange | #E65100 |
| Stability/neutral | Teal | #00695C |
| Light bg (primary) | Light blue | #E8F0FE |
| Light bg (growth) | Light green | #E8F5E9 |
| Light bg (warning) | Light orange | #FFF3E0 |
| Light bg (neutral) | Light teal | #E0F2F1 |

### Workflow for Adding Diagrams

1. **Identify diagram type**: Choose from the 6 types above based on content
2. **Customize text**: Replace placeholder text in the SVG template
3. **Adjust colors**: Keep the standard palette — only change if the user has specific brand requirements
4. **Position text**: Ensure text fits within box boundaries (test long titles)
5. **Add diagram wrapper**: Use the `.diagram-wrapper` CSS class (centers, adds margins)
6. **Add caption**: Add `p.note` below the diagram
7. **Test print**: Verify the diagram looks correct when printed to PDF

### Example: Adding a PDCA Diagram to HTML

```html
<div class="diagram-wrapper">
  <!-- Copy SVG from assets/report-diagrams.html -->
  <svg viewBox="0 0 700 520">
    <!-- customize content here -->
  </svg>
  <p class="note">图：[图表标题]</p>
</div>
```

### Key Principles for Diagrams

- ✅ **Keep it simple**: Max 4-6 nodes per diagram. If more, split.
- ✅ **Use the color palette**: Don't introduce new colors.
- ✅ **Label everything**: Every node needs a short label.
- ✅ **Show flow direction**: Arrows or numbered steps.
- ✅ **Add time context**: For timelines, show duration/period.
- ❌ **Don't over-decorate**: No gradients, 3D effects, or shadows on elements.
- ❌ **Don't crowd**: Leave breathing room between elements.
