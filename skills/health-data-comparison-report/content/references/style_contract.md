# Style Contract - Health Data Comparison Report

## Page Layout

- **Format**: A4 portrait
- **Margins**: top 2.8cm / bottom 2cm / left 2cm / right 2cm
- **Density**: Compact layout, minimize whitespace, high information density
- **Content area per page**: >= 85%

## Cover Page (Standalone First Page)

- No header or footer on cover page
- Content (all centered):
  - Brand name: "鑫瑞健康" - 16pt, deep blue #005293, letter-spacing ~6px
  - Optional English subtitle: "XINRUI HEALTH" - 10pt, #5983AF, letter-spacing ~3px (cover only, never in page headers)
  - Main title: "健康数据对比报告" - 36pt, deep blue #005293, bold
  - Member info: surname + gender + age - 12pt, dark gray
  - Comparison period: start date -> latest date - 10.5pt, gray
  - Report date: current date - 10.5pt, gray
- Optional brand accent line or decorative element at bottom

## Header (From Page 2 Onward)

- Top-right text: "鑫瑞健康 | 专业健康管理服务" - **Chinese brand only, NO pinyin/English in the page header** (user-confirmed 2026-07-21: "右上角页眉把拼音去掉")
- Font: 9pt, deep blue #005293
- Header line: 1pt light gray horizontal line #C8D2DC below text, full page width
- **Line sits tight under the text**: ~2pt gap between text baseline and the rule (user-confirmed 2026-07-21: "把页眉横线再往上方移一点"); keep ~8pt below the rule before body text

## Footer (From Page 2 Onward)

- Centered page number (1, 2, 3...)
- Font: 9pt, gray #808080
- Footer line: 1pt light gray horizontal line #C8D2DC above page number, full page width
- Line-to-number spacing: 4pt

## CSS @page Rules (for HTML-to-PDF)

```css
@page {
  margin: 2.8cm 2cm 2cm 2cm;
}
@page :first {
  /* Cover page: no header/footer */
  margin: 0;
  @top-right { content: none; }
  @bottom-center { content: none; }
}
@page :not(:first) {
  @top-right {
    content: "鑫瑞健康 | 专业健康管理服务";
    font-size: 9pt; color: #005293;
    border-bottom: 1pt solid #C8D2DC;
    padding-bottom: 2pt;   /* rule tight under text; ~8pt margin below rule */
    margin-bottom: 8pt;
  }
  @bottom-center {
    content: counter(page);
    font-size: 9pt; color: #808080;
    border-top: 1pt solid #C8D2DC;
    padding-top: 4pt;
  }
}
```

## Color Palette

| Usage | Color |
|-------|-------|
| Primary (titles/headers) | #005293 |
| Secondary (labels) | #5983AF |
| Body text | #333333 |
| Auxiliary gray | #808080 |
| Borders/dividers | #C8D2DC |
| Table row background | #F5F7FA |
| First column background | #eef1f5 |
| Red (above range) | #E85D4E |
| Blue (below range) | #005293 |
| Green (chart series only) | #4CAF50 |
| Chief complaint label bg | #fdecea |
| Chart background | #FAFBFC |

## Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Cover brand | 16pt | normal | #005293 |
| Cover title | 36pt | bold | #005293 |
| Cover member info | 12pt | normal | dark gray |
| Cover period/date | 10.5pt | normal | gray |
| Body text | 10pt | normal | #333333 |
| Main heading (h1) | 20pt | bold | #005293 |
| Section heading (h2) | 12pt | bold | #005293 |
| Sub-section (h3) | 10.5pt | bold | #005293 |
| Table header | 9pt | bold | white on #005293 |
| Table data | 8.5pt | normal | #333333 |
| Header text | 9pt | normal | #005293 |
| Footer page number | 9pt | normal | #808080 |

- **Font family**: "WenQuanYi Zen Hei", "Noto Sans CJK SC", sans-serif
- CJK-capable font required for all text paths

## Table Styling

- **Header row**: Deep blue background #005293, white text, 9pt bold
- **Data rows**: Light gray background #F5F7FA, dark gray text
- **First column**: #eef1f5 background, bold, left-aligned
- **Borders**: **No left/right frame and no inner vertical lines** (user-confirmed preference 表格去边框, 2026-07-29) - tables are open on both sides; use horizontal borders only (0.5pt solid #C8D2DC between rows, below the header row, and at table top/bottom edges). In HTML/CSS: `table { border: none; border-top: 0.5pt solid #C8D2DC; border-bottom: 0.5pt solid #C8D2DC; } th, td { border: none; border-bottom: 0.5pt solid #C8D2DC; }`; in DOCX: remove all vertical borders (outer left/right and insideV), keep insideH plus top/bottom horizontal borders
- **Cell padding**: 5pt 4pt

## Abnormal Value Marking (Mandatory Arrow + Color Rule)

| Status | Style | Color |
|--------|-------|-------|
| Above upper limit | bold, value followed by red "↑" | #E85D4E (red) |
| Below lower limit | bold, value followed by blue "↓" | #005293 (blue) |
| Normal | regular, no arrow | #333333 (black) |
| Not tested | "-" | #808080 (gray) |

- Elevated values: red text + red up arrow (e.g. `6.01 ↑`), both in #E85D4E, bold
- Decreased values: blue text + blue down arrow (e.g. `2.94 ↓`), both in #005293, bold
- The arrow immediately follows the numeric value in the same table cell
- Applies to every data table in the report (lab data, vitals, body composition, etc.)

## Lesion Marking in Imaging / Ultrasound Tables (Mandatory)

- In imaging comparison tables (甲状腺/乳腺/腹部/妇科/颈动脉/胸部CT等), any lesion's **location and size/dimension** must be highlighted: red #E85D4E, bold
- Applies to: 结节、斑块、囊肿、结晶、钙化灶、肌瘤、息肉、导管扩张、低密度灶等病灶描述
- Highlight only the anatomical site and measurement (e.g. `左叶 1.30×0.65cm`), not the whole sentence
- Diagnosis grade labels (C-TIRADS、BI-RADS) remain in default text color

## Chart Styling (Premium Line Charts)

### Global Chart Configuration
- **figsize**: (12, 6) standard, (14, 7) for complex multi-line
- **dpi**: 200 (high quality output)
- **Background**: #FAFBFC (chart area), #FFFFFF (figure area)

### Axis and Spine Styling
- Top/right spines: hidden
- Left/bottom spines: #C8D2DC, linewidth 1.2
- Y-axis grid: dashed, alpha 0.4, color #E8ECF0
- Grid rendered below data points (zorder=0 for grid, zorder=5 for lines)

### Line Styling
- Line width: 2.5px (primary), 2.2px (secondary)
- Marker size: 7px
- Line colors: #005293, #E85D4E, #4CAF50, #5983AF, #FF9800, #9C27B0
- Marker styles: o, s, D, ^, v, <

### Reference Line Styling
- Color: matching indicator color, alpha 0.7
- Linestyle: dashed (--) or dash-dot (-.)
- Linewidth: 1.5px
- Label on right side of chart area

### Data Label Styling
- Position: above data points (offset 12pt)
- Font: 8pt bold
- Color: matching line color
- Format: 1 decimal for most, 2 decimals for precision indicators
- **Precision rule**: labels and table values must preserve the source report's precision - never round to integer (e.g., WBC 5.27 must not render as 5)

### Legend Styling
- Position: upper left or best fit
- Frame: white background, #C8D2DC border, alpha 0.9
- Font: 9pt

### Chart Title Styling
- Position: left-aligned, pad 20pt
- Font: 16pt bold #005293

### Dual-Axis Charts
- Left axis color: #005293
- Right axis color: #E85D4E
- Right spine visible but styled to match axis color

## Module Spacing (Table + Chart Combinations)

```
h2 section title     <- 距上方内容 16pt
[system description]  <- 1-2 lines, 10pt
[8pt gap]
[data table]          <- header 9pt, data 8.5pt
[6pt gap]
[trend chart]         <- width matches table, height 7cm
[4pt gap]
[key findings]        <- 2-3 lines, 10pt, direct conclusions
[12pt gap]            <- module separator
[next module]
```
