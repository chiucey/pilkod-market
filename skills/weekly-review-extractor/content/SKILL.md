---
name: weekly-review-extractor
description: Extract content from weekly review PDFs (2026-W19 format) and generate concise reports for labmate communication, including last week's summary and next week's plan with yellow highlight formatting. Use when users need to convert weekly review documents into concise communication reports.
---

# Weekly Review Extractor

This skill converts your weekly review PDFs (YYYY-Wnn format) into concise communication reports for sharing progress with labmates and advisors.

## Input Requirements

- **File Format**: PDF file
- **File Naming**: `YYYY-Wnn` format (e.g., 2026-W19.pdf)
- **Content Structure**: Should include weekly overview, daily summary, completed items, data statistics, pattern recognition, and next week adjustments

## Output Format

The output uses yellow highlight blocks containing two core sections:

### Last Week Review
1. **Main Outputs**: Progress on thesis, Python learning, fault analysis, etc.
2. **Key Data**: Progress numbers, days completed
3. **What Went Well / Challenges**: Brief points on lessons learned
4. **Weekly Insight**: One-sentence core takeaway

### Next Week Plan
1. **Continuing Tasks**: Next steps for ongoing projects
2. **Adjustment Measures**: Improvement plans based on last week's issues
3. **Key Milestones**: Deadlines or important dates

## Usage Flow

### Step 1: Input PDF
Provide your weekly review PDF (YYYY-Wnn format). The system will:
1. Extract PDF content
2. Analyze review structure
3. Extract key information

### Step 2: Generate Report
Based on extracted content, generate the report in this format:

```
[Date Range]
[Yellow Highlight Block - Last Week Review]
[Yellow Highlight Block - Next Week Plan]
```

### Step 3: Edit and Adjust
You can:
- Request content detail adjustments
- Add or remove specific information
- Modify formatting style

## Example Output

For input "2026-W19.pdf", output:

**Last Week Review**: This week thesis plagiarism check passed (9%), Python learning progressed from 66 to 94 lessons (+28), fault analysis resumed and advanced to page 47. What went well: specific, divisible tasks. Challenge: Python learning was squeezed by thesis work.

**Next Week Plan**: 1) Lower Python threshold to "mark as done when learned", complete remaining 32 lessons before 5/14; 2) Confirm final plagiarism system with advisor; 3) Confirm undergraduate thesis word count requirements; 4) Keep fault analysis at 10-minute daily minimum; 5) Recovery required by day 2 for any exercise interruption.

## Notes

- Output content is in Chinese for local use
- Numbers use Arabic numerals
- Yellow highlight background emphasizes key content
- Keep concise for quick reading and communication