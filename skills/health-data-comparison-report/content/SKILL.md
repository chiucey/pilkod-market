---
name: health-data-comparison-report
description: Generate professional health data comparison reports from multiple medical examination reports (PDF/images). Extract health indicators across time, build longitudinal comparison tables, create premium trend charts for every data table, and output a formatted PDF or DOCX report. Use when the user needs to (1) compare health examination data across multiple dates, (2) create a longitudinal report with trend charts, (3) track lab results over time (blood work, glucose, lipids, liver/kidney function), (4) compile multiple checkup reports into one document, (5) compare imaging/endoscopy findings (ultrasound, CT, MRI, gastroscopy) over time, (6) re-typeset/re-layout (整理排版/重新排版) an existing health data report into the standard template, (7) compare CGM (动态葡萄糖监测) reports across wear periods, or (8) explain why abnormal indicators appeared from a functional-medicine perspective (疾病底层逻辑, 七大生理失衡). Also use when the user uploads medical reports or PDFs and asks for comparison, analysis, summary, or trend visualization.
---

# Health Data Comparison Report

Generate professional longitudinal health data comparison reports with premium trend charts from multiple medical examination files.

## Reference Source

- **Type**: Uploaded artifact (DOCX instruction file)
- **Artifact type**: DOCX
- **Reference File Type**: PDF (output-oriented; the reference describes PDF report generation specs)
- **Language**: Chinese (zh-CN), CJK-capable typography required

## Supported Outputs

| Format | Support | Notes |
|--------|---------|-------|
| PDF    | Primary | A4 portrait, HTML/CSS-based rendering preferred |
| DOCX   | Yes     | Same content, adapted to DOCX table/chart capabilities |
| PPTX   | No      | Not applicable for this report type |

**Default output**: PDF when user does not specify a format.

## Workflow Overview

1. **Receive & parse inputs** - Extract text/data from uploaded medical reports
2. **Data extraction** - Extract all health indicators page by page, line by line
3. **Data verification** - Cross-check every value against source, ensure no hallucination
4. **Chart generation** - Generate premium trend charts for each indicator category
5. **Layout optimization** - Apply compact layout with table-chart pairing
6. **Report generation** - Build structured report with optimized typography
7. **Quality check** - Run through the mandatory checklist before output

### Input Variants

- **Scanned PDFs (no text layer)**: render pages to images (`pdftoppm -png -r 150`), then read each page visually. Do not rely on OCR alone for numeric values - Chinese OCR packs are often unavailable and misread digits.
- **Text-layer PDFs**: extract with `pdftotext -layout`; if the reading order is jumbled, rebuild tables by word coordinates (e.g., pdfplumber `extract_words`) to avoid column shifts.
- **Re-typeset task (整理排版)**: when the user uploads an existing comparison report and asks to re-layout it, keep ALL data exactly as in the source - change only structure, charts, and typography to this contract.
- **CGM reports (动态葡萄糖监测)**: compare across wear periods the core metrics (eHbA1c, MG, SD, CV, TIR/TAR/TBR, 低血糖风险) plus daily TIR trend lines; use the report's own printed reference targets, never substitute outside standards.
- **Duplicate uploads**: before treating files as separate time points, confirm each file is a distinct exam (monitoring period, exam date, values). If two uploads are identical (observed 2026-07-28: a file dated 07.27 was byte-identical to the 07.11 report), do NOT fabricate an extra time point - proceed with the distinct reports and disclose the duplicate to the user.

## Core Principles (Non-Negotiable)

### Data Integrity
- All data must be extracted page-by-page, line-by-line from source reports
- **Strictly prohibited**: fabricating data, filling in missing values, inferring, or hallucinating
- If an item was not tested: mark as "未查" or "-"
- If a value is blurry or unreadable: mark "需核实", do not guess
- If different reports contradict: list all values and annotate the discrepancy
- Never "reasonably infer" missing values; missing is missing

### Data Verification Workflow (Mandatory)
After extraction, verify in this order:
1. Per-indicator check: each indicator has data for all time points
2. Per-value check: each value matches the original report
3. Unit consistency check: units are unified and correct
4. Reference range check: ranges match the report
5. Missing item check: no indicators were skipped
6. Column-shift check: no data placed in wrong time column
7. Cross-assignment check: no data placed under wrong indicator, and every imaging finding attributed to the correct exam modality and date (user correction 2026-07-29: a nodule was wrongly attributed to the mediastinal CT - re-verify which exam actually reported each finding)

Confirm after verification: all data is accurate, complete, with no omissions or hallucinations.

### Client Privacy (Mandatory)
- Keep only surname (e.g., "Mr. Peng", "Ms. Li"); hide full name
- Hide all identifiers: phone, ID number, address, medical record number, insurance number, outpatient number
- Keep: examination institution name (for traceability), examination date (for timeline)
- Optional: use code instead of name if client requests (e.g., "Member A2025")
- No personally traceable information may appear in the report

## Report Structure (Fixed Order)

Read `references/structure_contract.md` for the complete section hierarchy, field semantics, and content specifications for each section.

Read `references/functional_medicine.md` for the functional-medicine root-cause section (疾病底层逻辑·功能医学视角, based on 曾强《功能医学概论》七大生理失衡 framework) - a mandatory section between 数据趋势评估 and 随访计划 that explains, in plain client-facing language, which physiological systems are out of balance and the bottom-level lifestyle/environmental causes behind the abnormal data. Data-driven only: explain only what the member's indicators actually signal; never diagnose.

Key structural rule: **Every data table must be immediately followed by a trend chart** (表+图组合). No exceptions.

## Visual Style

Read `references/style_contract.md` for the complete color palette, typography system, table styling, chart styling, and page layout specifications.

## Trend Chart Generation (Premium Line Charts)

Read `references/chart_generation.md` for complete chart generation rules, matplotlib code templates, and chart-table pairing specifications.

### Chart Coverage (Mandatory - Every Table Gets a Chart)
- **Glucose**: fasting + postprandial + HbA1c (multi-line or combo)
- **Pancreatic function**: C-peptide + insulin (dual Y-axis)
- **Lipids**: TG, TC, LDL-C, HDL-C (multi-line)
- **Renal function**: creatinine + eGFR (dual Y-axis, note opposite direction)
- **Liver function**: ALT + AST + GGT (multi-line)
- **Hematology**: WBC, RBC, Hb, PLT (multi-line or split charts)
- **Electrolytes**: K, Na, Cl (multi-line)
- **Urinalysis**: UACR, urine microalbumin (line chart)
- **Other**: Hcy, vitamin D, TSH, tumor markers (line charts as applicable)
- **Imaging measurements**: cyst/nodule/polyp max diameter line charts, one per measured item, two per row after the imaging comparison table; unmeasured time points marked "未测量", line breaks at gaps, never interpolate
- **Qualitative results** (e.g., HPV positive/negative, occult blood +/-): step chart mapping qualitative states to levels (e.g., 阴性=0 / 阳性=1) when a table alone cannot show the trend

### Chart Output Specs
- figsize=(12, 6), dpi=200
- Premium styling: hidden top/right spines, dashed Y-grid, data point labels
- Output as PNG, embed as base64 in HTML
- Chart width matches table width

## Layout Optimization (Compact Typography)

Read `references/layout_optimization.md` for detailed layout rules, spacing specifications, and compact排版 techniques.

### Key Layout Rules
- **Table-Chart pairing**: Every table immediately followed by its trend chart
- **Information density**: >= 85% content area per page
- **No page-spanning modules**: Each table+chart+findings unit stays on one page
- **Spacing**: 6pt between table and chart, 4pt between chart and findings, 12pt between modules
- **Compact tables**: 9pt header, 8.5pt data, 5pt 4pt cell padding

## Typography & Font Strategy

- **Reference fonts**: WenQuanYi Zen Hei, Noto Sans CJK SC
- **Font family**: Sans-serif CJK
- **Script support**: Primary content is Chinese (zh-CN). Use a CJK-capable font consistently across all text paths.
- If reference fonts are unavailable, substitute with any available CJK sans-serif font (e.g., Source Han Sans, Microsoft YaHei, PingFang SC) that preserves the clean modern sans-serif character.
- Apply the same font family to body text, headings, tables, captions, headers, footers, cover text, and chart labels.

## Writing Style (Anti-AI Tone, 去AI味)

Write like a senior health-management consultant's work product, not an AI summary.

- Do NOT use: "首先/其次/再次/最后", "值得注意的是", "综上所述", "不难发现", "总的来说", "由此可见", "在一定程度上", "与此同时" or similar AI filler phrases
- Do NOT use: "我们需要关注的是/这意味着/可以推测/可能表明/或许与……有关" or speculative language - state the value and the fact, never narrate reasoning
- Do NOT use: 三段式排比 ("不仅……而且……更……"), empty transitions between modules, or repeating the section title in the first sentence
- Do NOT use: rhetorical metaphors, exclamation marks, emoji, hollow closings ("健康是福"类)
- Conclusions must be direct, sentences short, information density high; delete any sentence that adds neither data nor judgment
- Judgment wording stays in flat clinical register: "偏高/较上次上升/建议复查" instead of "令人担忧/明显改善/非常理想"
- **Correct example**: "HbA1c 7.3%，仍高于目标。" "eGFR从94.5降至75.5，需关注肾功能变化。"
- **Wrong example**: "值得注意的是，HbA1c目前仍处于较高水平，这可能意味着血糖控制不够理想。综上所述，建议……"

## Quality Checklist (Mandatory - Verify Before Output)

- [ ] All data extracted page-by-page from original reports, no fabrication, no hallucination
- [ ] Per-indicator verification completed after extraction, no omissions, no shifts, no cross-assignments
- [ ] Client info de-identified (surname only, all personal identifiers hidden)
- [ ] Cover page complete: brand name, main title, member info, comparison period, report date
- [ ] Header line and footer line added (light gray #C8D2DC, 1pt)
- [ ] Timeline complete, missing items marked
- [ ] Abnormal values marked with arrows: elevated = red bold + red "↑", decreased = blue bold + blue "↓"
- [ ] No arrows on missing/untested values - "-" stays plain gray (observed failure 2026-07-29: a missing PLT value was wrongly marked with ↓)
- [ ] Cross-institution reference-range differences footnoted, and each arrow judgment traceable to the range used (observed failure 2026-07-29: an HCT arrow needed the 树兰 range annotated)
- [ ] Tables have no left/right frame and no inner vertical lines (horizontal borders only; user-confirmed preference 表格去边框, 2026-07-29)
- [ ] In imaging/ultrasound tables, lesion locations and sizes (结节/斑块/囊肿等) marked red bold
- [ ] Imaging & endoscopy timeline table included (if source reports contain imaging/endoscopy exams)
- [ ] Imaging item longitudinal comparison table included: same item compared across time points with trend judgment column; measured-value trend charts for numeric items (cyst/nodule diameter etc.), unmeasured points marked, no fabricated values
- [ ] **Every data table has a corresponding trend chart (表+图组合)**
- [ ] Charts use premium styling (hidden spines, dashed grid, data labels)
- [ ] Chart data labels preserve source precision (never round to integer)
- [ ] Layout is compact, no large blank areas, information density >= 85%
- [ ] Table-chart pairs do not span page breaks
- [ ] Charts clear, data points non-overlapping
- [ ] Header/footer on every page; page-header text is Chinese brand only (e.g., "鑫瑞健康 | 专业健康管理服务"), NO pinyin/English; header rule sits tight under the text (~2pt gap)
- [ ] Functional medicine root-cause section included (七大生理失衡 framework): 2-4 data-supported systems only, plain language, logic chain stated, no diagnosis, bridges to follow-up section
- [ ] Medication info complete (if provided)
- [ ] Body text free of AI filler phrases
- [ ] Disclaimer included

## Key Indicator Categories

| System | Key Indicators |
|--------|---------------|
| Hematology | WBC, RBC, Hb, PLT, HCT, MCV, MCH |
| Glucose | Fasting glucose, postprandial glucose, HbA1c, glycated albumin, fasting C-peptide, fasting insulin |
| Lipids | TG, TC, LDL-C, HDL-C, ApoA1/B |
| Liver function | ALT, AST, GGT, ALP, total bilirubin, direct bilirubin, albumin, globulin |
| Renal function | Creatinine, eGFR, uric acid, urea, cystatin C |
| Urinalysis | UACR, urine glucose, urine protein, urine occult blood |
| Coagulation | PT, INR, APTT, FIB, D-dimer |
| Electrolytes | K, Na, Cl, Ca, Mg, P |
| Other | Homocysteine, vitamin D, thyroid function, tumor markers (if available) |

## Adapting the Report

- Brand name defaults to "鑫瑞健康" (cover may add "XINRUI HEALTH" as a small English subtitle); adapt to user's actual brand if different
- **Page header text must be Chinese-only** (e.g., "鑫瑞健康 | 专业健康管理服务") - never put pinyin/English in the running page header (user-confirmed preference, 2026-07-21)
- Color scheme, page margins, and typography are fixed per style contract
- If client provides medication info, include the medications section
- If client provides specific focus areas, highlight them in the health status section
- Follow-up plan uses the vertical "3-6-9-年度体检" timeline and lifestyle advice must be concrete/quantified/executable - see `references/structure_contract.md` Section 11
- Comparison period auto-detected from earliest to latest examination date

## Rendering & Pagination Pitfalls (HTML -> PDF)

Read `references/layout_optimization.md` for the full set of hard-won pagination fixes and sandbox environment workarounds. Key points:

- **Renderer choice**: WeasyPrint is the default renderer for this report - Chromium headless print-to-PDF cannot render `@page` margin-box headers/footers/page numbers (verified 2026-08-03).
- **Cover and body render best as separate passes** when using margin-box headers/footers - cover uses `@page :first { margin: 0 }` with header/footer suppressed.
- **Chromium miscalculates page-break heights for flex layouts** - modules get pushed onto their own pages leaving large blanks. Use block/float layout or explicit manual page breaks instead of relying on `page-break-inside: avoid` alone.
- **A module overflowing by only 1-2 lines**: shrink PDF scale slightly (e.g., 0.95 -> 0.92) or compress table row height / trim long cell text; do not reflow the whole document.
- **Always verify the final PDF page-by-page with rendered screenshots** (montage overviews + zoomed crops of header, charts, and table footers) before delivery.
- **Keep working files outside /tmp** (it can be wiped mid-task): persist `gen_report.py`, HTML, and charts under `/mnt/agents/work/<task>/` so later user adjustments only need a small edit + re-render.
- **Sandbox pip installs stall on large wheels** from pythonhosted.org (verified 2026-08-03: 5MB fonttools wheel timed out repeatedly) - install via Chinese mirror: `pip install -i https://mirrors.aliyun.com/pypi/simple/ <pkg>`.
- **fontTools import name is camelCase**: `import fontTools`, not `fonttools`. If `pip show fonttools` claims installed but import fails, the install is broken (dist-info only) - `pip install --user --force-reinstall --no-deps fonttools` (WeasyPrint depends on it).
- **Batch `pdftoppm` rendering to the /mnt mount can segfault** (libpng write error on the portal mount, verified 2026-08-03) - write transient validation page images to local /tmp (regenerable), keep only persistent work files under /mnt/agents/work.
