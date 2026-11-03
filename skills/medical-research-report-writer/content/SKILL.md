---
name: medical-research-report-writer
description: Write illustrated medical research reports. Use when users request medical research reports, clinical study reports, basic medical research, case reports, literature reviews, or need research reports with data visualizations. Supports flowcharts, data visualizations, and result displays with illustrations.
---

# Medical Research Report Writer

## Core Capabilities

This skill specializes in writing professional, rigorous, and illustrated medical research reports covering various types and formats.

## Supported Report Types

1. **Clinical Study Reports**
   - Randomized Controlled Trial (RCT) Reports
   - Observational Studies (Cohort, Case-Control, Cross-sectional)
   - Drug Clinical Trial Reports

2. **Basic Medical Research Reports**
   - Molecular Biology Research
   - Cell Biology Research
   - Animal Experiment Reports

3. **Case Reports**
   - Rare Case Reports
   - Complex Case Analysis
   - Clinical Experience Sharing

4. **Literature Reviews**
   - Systematic Reviews
   - Meta-Analysis Reports
   - Narrative Reviews

5. **Medical Professional Reports**
   - Epidemiological Survey Reports
   - Public Health Assessment Reports
   - Disease Burden Analysis Reports

## Report Structure Templates

### Standard Medical Research Report Structure

```markdown
# [Report Title]

## Abstract
- Background
- Methods
- Results
- Conclusions

## Keywords

## 1. Introduction
### 1.1 Research Background
### 1.2 Research Objectives
### 1.3 Research Hypotheses

## 2. Methods
### 2.1 Study Design
### 2.2 Study Population
### 2.3 Intervention/Exposure
### 2.4 Outcome Measures
### 2.5 Statistical Analysis

## 3. Results
### 3.1 Baseline Characteristics
### 3.2 Primary Outcomes
### 3.3 Secondary Outcomes
### 3.4 Subgroup Analysis

## 4. Discussion
### 4.1 Key Findings
### 4.2 Comparison with Previous Studies
### 4.3 Clinical Implications
### 4.4 Limitations
### 4.5 Conclusions

## 5. References

## Appendices
```

## Illustration Requirements

### Data Visualization Types

1. **Statistical Charts**
   - Bar Charts
   - Line Charts
   - Pie/Donut Charts
   - Box Plots
   - Scatter Plots
   - Forest Plots
   - Heat Maps

2. **Flowcharts**
   - CONSORT Flowchart
   - STROBE Flowchart
   - Study Design Flowchart
   - Patient Enrollment Flowchart

3. **Diagrams**
   - Study Design Diagram
   - Molecular Pathway Diagrams
   - Mechanism Diagrams

4. **Tables**
   - Baseline Characteristics Table (Table 1)
   - Univariate/Multivariate Analysis Tables
   - Sensitivity Analysis Tables

### Chart Generation Guidelines

- Use `genui-chart` tool for statistical charts
- Use `render_mermaid` for flowcharts and diagrams
- Charts should meet medical journal publication standards
- All figures should be numbered and titled

## Output Format Standards

### Document Format
- Write in Markdown format
- Support LaTeX mathematical formulas
- Charts in standard formats (PNG/SVG)

### Language Style
- Academically rigorous
- Precise terminology
- Clear logic
- Objective presentation

### Citation Standards
- Support multiple citation formats (Vancouver, APA, AMA)
- Auto-generate reference lists

## Execution Workflow

### 1. Requirements Confirmation
- Determine report type
- Clarify research topic
- Confirm data sources

### 2. Content Writing
- Write according to standard structure
- Generate supporting figures
- Ensure text-figure alignment

### 3. Quality Review
- Check logical coherence
- Verify data accuracy
- Optimize figure presentation

### 4. Final Output
- Generate complete report document
- Output supporting figures
- Provide format adjustment options

## Common Medical Research Reporting Guidelines

- **CONSORT**: Randomized Controlled Trial Reporting Guidelines
- **STROBE**: Observational Study Reporting Guidelines
- **PRISMA**: Systematic Review Reporting Guidelines
- **STARD**: Diagnostic Accuracy Study Reporting Guidelines
- **ARRIVE**: Animal Research Reporting Guidelines

## Reference Resources

See detailed guide documents in the `references/` directory.
