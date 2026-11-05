# Structure Contract - Health Data Comparison Report

## Document Section Hierarchy (Fixed Order)

### Section 1: Cover Page (Standalone)
- Brand name: "鑫瑞健康" (optional small "XINRUI HEALTH" English subtitle below)
- Main title: "健康数据对比报告"
- Member info line: surname + gender + age
- Comparison period: earliest date -> latest date
- Report generation date

### Section 2: Main Title + Subtitle (Body Start Page)
- Title: "{Surname}{Gender} 健康数据对比报告" (e.g., "彭先生 健康数据对比报告")
- Subtitle: "对比周期：{start_date} - {end_date} | 报告日期：{report_date}"

### Section 3: Member Basic Information
- Two-column table:
  - Name (surname only), Gender, Age
  - Height, Weight, BMI
  - Blood pressure
  - Examination dates and institutions

### Section 4: Health Status
- Diagnosis list as tag/label format
- Chief complaints highlighted with red background labels (#fdecea)
- Current report focus areas annotated

### Section 5: Current Medications (If Provided)
- Grouped by category: glucose-lowering / blood pressure / lipid-lowering / anticoagulant / other
- Each medication: generic name + brand name + specification + dosage + frequency

### Section 6: Key Data Timeline (Core Section)

Each subsection follows the "表+图" pattern: data table immediately followed by trend chart.

#### 6.1 Hematology
- Indicators: WBC, RBC, Hb, PLT, HCT, MCV, MCH
- Format: time-series comparison table + multi-line trend chart
- Columns: Indicator | Unit | Ref Range | Date1 | Date2 | ... | DateN

#### 6.2 Glucose & Glycemic Control
- Indicators: Fasting glucose, postprandial glucose, HbA1c, glycated albumin, fasting C-peptide, fasting insulin
- Format: table + combo trend chart (glucose multi-line, C-peptide/insulin dual axis)

#### 6.3 Lipids
- Indicators: TG, TC, LDL-C, HDL-C, ApoA1, ApoB
- Format: table + multi-line trend chart

#### 6.4 Liver Function
- Indicators: ALT, AST, GGT, ALP, total bilirubin, direct bilirubin, albumin, globulin
- Format: table + multi-line trend chart

#### 6.5 Renal Function
- Indicators: Creatinine, eGFR, uric acid, urea, cystatin C
- Format: table + dual-axis trend chart (creatinine + eGFR, opposite directions)

#### 6.6 Urinalysis
- Indicators: UACR, urine glucose, urine protein, urine occult blood
- Format: table + trend chart

#### 6.7 Coagulation
- Indicators: PT, INR, APTT, FIB, D-dimer
- Format: table

#### 6.8 Electrolytes
- Indicators: K, Na, Cl, Ca, Mg, P
- Format: table + multi-line trend chart

#### 6.9 Other (If Available)
- Indicators: Homocysteine, vitamin D, thyroid (TSH, FT3, FT4), tumor markers, etc.
- Format: table + charts as applicable

### Section 7: Imaging & Endoscopy Timeline (If Available)
- Chronological table of all imaging and endoscopy examinations
- Columns: Date | Exam Item | Key Findings & Diagnosis
- Group multiple exams on the same date with rowspan
- Content: lesion sizes with exact measurements (nodule/cyst/polyp dimensions), organ descriptions, endoscopy findings, pathology results, EF values, bone density conclusions
- Source: ultrasound, CT, MRI, echocardiography, endoscopy, bone density reports
- Keep institution names for traceability; keep exam dates for the timeline

### Section 8: Imaging Item Longitudinal Comparison (Mandatory when the same item was examined at >=2 time points)
- Re-organize imaging data BY ITEM across time points (not by date). The same exam item (e.g., chest CT, abdominal ultrasound) must be compared vertically across all its occurrences.
- One comparison table: Item | Date 1 | Date 2 | ... | Date N | Trend Judgment
- Items to include (as available in source reports): chest CT (nodules, other changes), abdominal ultrasound/CT (liver cyst, gallbladder, kidneys), echocardiography, carotid/lower-limb artery ultrasound, prostate ultrasound, thyroid ultrasound, breast ultrasound, gynecological ultrasound, gastroscopy, colonoscopy, bone density, spine imaging
- Each cell carries the exact measurement or conclusion from that exam (e.g., "右下肺较大结节 6mm", "多发，其一 1.72×1.10cm"); items not examined at a time point are marked "-"
- Trend judgment column: short, conservative, data-based wording (e.g., "连续3年稳定", "缓慢增大，良性进程", "已手术切除"); no diagnosis
- Measured-value trend charts: for items with numeric measurements (e.g., cyst max diameter, nodule max diameter), generate one line chart per item, placed two per row after the table; time points without a measurement must be explicitly marked "未测量" and the line must break there - never interpolate or fabricate a value
- Key-points block after table + charts: 3-5 bullets, one per key item, direct conclusions with numbers (e.g., "肺结节：右下肺较大结节连续3年6mm无增大，年度低剂量CT随访即可")

### Section 9: Data Trend Assessment
- Organized by system, bullet points
- Each point: max 3 lines
- Content: data description + trend judgment only (no diagnosis)
- Example: "HbA1c 在 7.0%-7.8% 区间波动，最新 7.3%，仍高于目标。"

### Section 10: Functional Medicine Root-Cause Analysis (疾病底层逻辑·功能医学视角)
- Read `functional_medicine.md` for the full framework (七大生理失衡), logic chain, indicator mapping, and writing rules.
- Placement: after 数据趋势评估, before 随访计划. Explains WHY the abnormal indicators appeared; Section 11 then tells WHAT TO DO.
- Pick 2-4 imbalance systems actually signaled by this member's data; never list all seven mechanically; never diagnose.
- Opening: 1-2 lines stating the logic chain (生活方式/环境输入 → 生理系统失衡 → 指标异常 → 器官损伤 → 疾病). Each system block: ①异常指标+数值 ②失衡环节（可用一个生活化比喻）③最常见诱因（与会员已知生活方式相符）. Closing: 1-2 sentences bridging to the follow-up/lifestyle section.
- Length: half to one page, plain client-facing Chinese.

### Section 11: Follow-up Plan & Lifestyle Prescription (随访计划与生活方式)

**Follow-up plan** - vertical timeline format (user-specified 2026-07-25, "3-6-9-年度体检" style):
- Nodes in fixed chronological order: 马上（1个月内）→ 3个月后 → 6个月后 → 9个月后（如适用）→ 1年后（年度体检）→ 1-2年后（胃肠镜等长周期专项）
- Render as a vertical timeline with colored node dots (one accent color per node), not as a plain bullet list or table
- Each node: bullet items of "复查项目：目的/数据依据" - every item must cite the report finding that justifies it (e.g., "甲状腺外科就诊：评估4a类结节，必要时穿刺活检")
- Timing must respect clinical intervals already implied by the data (e.g., post-polypectomy gastroscopy at 1 year)

**Lifestyle prescription** - concrete, executable, quantified actions only (user requirement 2026-07-25: "可执行的、容易执行的、可落地的，不要虚无缥缈不切实际的"):
- Every recommendation must be a specific action with a measurable quantity or frequency: e.g., "油每天2瓷勺", "盐每天1啤酒瓶盖", "快走每天6000步", "每周一/周四测血压", "每月1号称重"
- Adapt to the member's known conditions (e.g., 腰椎问题选靠墙静蹲而非弯腰运动)
- Strictly no vague advice: "清淡饮食/适量运动/注意休息/保持心情愉快" and similar empty phrases are banned - rewrite each as a concrete action or delete it

### Section 12: Disclaimer
- Fixed text: "本报告基于提供的检查数据整理，仅供医学参考。具体诊疗建议请咨询专业医生。"

## Data Table Format Rules

### Timeline Format
- Dates sorted ascending: earliest -> latest
- Column headers: YYYY.MM format (e.g., 2023.07, 2025.06)
- Multiple exams in same year: use full date to differentiate
- Missing data: fill with "-", do not interpolate or extrapolate

### Unit Standardization
- Same indicator must use consistent unit across entire table
- Common units:
  - Glucose: mmol/L
  - HbA1c: %
  - Creatinine/Uric acid: umol/L
  - Liver enzymes: U/L
  - C-peptide: nmol/L
  - Insulin: pmol/L or mU/L
  - Blood pressure: mmHg

### Reference Range
- Display reference range in the rightmost column of each row
- If different institutions have different ranges: use the latest as standard, footnote the difference

### Abnormal Marking in Tables
- Elevated value: red #E85D4E bold + red "↑" immediately after the value
- Decreased value: blue #005293 bold + blue "↓" immediately after the value
- Normal: default text, no arrow

### Imaging / Ultrasound Comparison Tables
- Lesion locations and sizes (结节、斑块、囊肿、结晶、钙化灶、肌瘤、息肉等) must be marked red #E85D4E bold
- Only highlight the anatomical site + measurement, not the whole finding sentence

### Table Column Layout
| Indicator Name | Unit | Ref Range | Date 1 | Date 2 | ... | Date N |
|---------------|------|-----------|--------|--------|-----|--------|

## Table-Chart Pairing Rules (Mandatory)

### Placement
- Each trend chart follows immediately after its corresponding data table
- Chart width matches table width (full content width)
- Chart height: 7cm standard, 7.5cm for dual-axis, 10cm for subplot combinations
- Gap between table and chart: 6pt
- Gap between chart and key findings: 4pt

### Alignment
- Chart horizontal center aligns with table center
- Chart title placed above chart, left-aligned
- Chart title format: "图N: {Indicator}趋势 ({Period})"

### Page Flow
- Prefer to keep table+chart+findings on the same page
- If a module would span a page break, insert page break before the module
- Each module separated by 12pt vertical space

## Content Generation Rules

### What to Include
- All indicators present in any of the source reports
- Every numerical value from source reports
- Reference ranges from source reports
- Units from source reports (standardized in output)
- Examination dates and institution names

### What NOT to Include
- Fabricated or inferred data
- Diagnostic conclusions (trend description only)
- AI filler phrases in body text
- Full names or personal identifiers
- Speculative interpretations

### Chart Placement
- Each trend chart follows immediately after its corresponding data table
- Charts embedded as images (PNG, base64 in HTML)
