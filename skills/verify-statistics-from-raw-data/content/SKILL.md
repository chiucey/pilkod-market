---
name: verify-statistics-from-raw-data
description: Verify published statistical claims by rerunning analyses on raw data. Use when users want to audit research papers, check statistical accuracy, validate p-values, sample sizes, and test results, or create verification workbooks for literature reviews.
---

# Verify Statistics from Raw Data

A systematic workflow for evaluating published statistics by checking them against raw data. This skill helps researchers develop deeper understanding of research methods and build critical reading skills.

## Required Inputs

- **Published manuscript** (PDF format)
- **Raw data files** (XLSX format)
- Optional: Enable Extended Thinking for more thorough verification

## Workflow Steps

### Step 1: Extract Statistical Claims

Ask the assistant to systematically go through the paper and extract every statistical claim:

> "Go through the paper systematically and pull out every p-value, mean, standard error, sample size, and test result they report."

### Step 2: Run Independent Analysis

Request the assistant to rerun each analysis using the provided raw data files.

### Step 3: Create Verification Report

For each statistical claim, document:
1. What the paper states
2. What was calculated from the raw data
3. Whether these match
4. Flag any problems found

### Step 4: Build Excel Workbook

Request a comprehensive audit workbook containing:
- Verification summary sheet
- Separate sheets for each analysis
- Step-by-step calculations
- Conditional formatting highlighting issues
- Dropdown filters for exploring results
- Professional formatting with frozen headers

## Example Prompt Template

```
I'm reading this paper that's central to my literature review, and I want to
understand it more deeply before citing it extensively. I've got the published
manuscript and their supplementary data files.

Can you help me verify their statistical claims? Go through the paper
systematically and pull out every p-value, mean, standard error, sample size,
and test result they report. Then run each analysis yourself using their actual data.

For each statistical claim, show me three things: what the paper states, what
you calculated from their data, and whether these match. Flag any problems you
notice - things like using wrong tests for the data type, sample sizes that
don't add up, or p-values that seem mathematically questionable.

Then build me a detailed Excel workbook where I can see your complete verification.
```

## Common Issues to Check

### Sample Size Discrepancies
- Verify stated sample sizes match the actual data rows
- Check if group sizes add up correctly
- Flag implications for statistical power

### Unit Conversion Errors
- Verify measurement units match between data and reported values
- Check for factor-of-10 or factor-of-100 errors
- Common in distance, weight, and volume measurements

### Inappropriate Statistical Tests
- Paired vs. unpaired t-tests for repeated measures
- Parametric vs. non-parametric test selection
- ANOVA assumptions and post-hoc corrections

### P-value Precision Errors
- Check reported p-values against recalculated values
- Flag discrepancies even when in same significance range
- Verify exact vs. threshold p-values (e.g., p=0.004 vs p=0.0001)

### Methods Description Inconsistencies
- Verify that statistical tests described match actual tests run
- Check if assumptions stated are actually followed
- Document any discrepancies between methods and analysis

## Follow-up Prompts

### Verify Figures
```
Check that all bar heights, error bars, and data points in Figure 2 match
the actual data values. Show me any discrepancies.
```

### Learn Warning Signs
```
Based on what we found here, teach me what warning signs I should look for
when reading other papers in my field. What patterns suggest I should be
skeptical, even when I can't verify the raw data?
```

### Draft Reviewer Comments
```
Turn these statistical problems into helpful reviewer comments that are clear
about what needs correcting but encouraging about how to fix it.
```

## Best Practices

1. **Start where you have domain expertise** - Your expertise helps discern what is plausible and allows you to judge whether flagged issues are real errors or field-specific practices.

2. **Open the actual Excel file** - Preview shows structure, but the real workbook contains working formulas, conditional formatting, and detailed calculation notes.

3. **Document all discrepancies** - Even minor issues should be noted, as they may indicate larger methodological problems.

4. **Check for patterns** - Multiple small errors may suggest systematic issues with data handling or analysis approach.

## Output Format

The verification should produce:
- **Verification Summary**: Total claims checked with breakdown (verified, minor discrepancies, require attention)
- **Detailed Findings**: For each statistical claim with paper statement vs. recalculated value
- **Excel Workbook**: With separate analysis sheets, formulas, and highlighted issues
- **Critical Issues List**: Prioritized findings requiring attention

## Technical Details

- **Input formats**: PDF (manuscript), XLSX (data files)
- **Best for**: Literature review preparation, peer review, research validation
- **Extended Thinking**: Recommended for thorough verification
