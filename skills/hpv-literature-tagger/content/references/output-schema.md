# Output Schema

Create an Excel workbook with these sheets unless the user asks for a different format.

## Sheet: 标签结果

Required columns:

1. `No.`
2. `PDF/File name`
3. `Title`
4. `age`
5. `population`
6. `ethnicity/region`
7. `type/exposure`
8. `condition/relate disease`
9. `outcome`
10. `sample'size`
11. `time`
12. `Evidence/依据`
13. `Need review`

Recommended optional columns:

- `PMID/DOI`
- `Source page/section`
- `Reviewer note`
- `Validation status`

## Sheet: 说明与复核

Include:

- The tagging SOP version: V2.
- Whether the result is machine pre-labeling or gold-standard corrected labels.
- Known limitations.
- Fields needing manual review.

## Sheet: 8子目录规则简表

Include a compact summary of each of the 8 fields, format, allowed values, and missing-value rules.

## Formatting

- Freeze header row.
- Use filters or a table.
- Wrap text.
- Make evidence and review columns wide enough for full sentences.
- Preserve exact labels and capitalization.

## Validation report

If `scripts/validate_labels.py` is run, save the report as a `.txt` file next to the output workbook or include a `Validation_Report` sheet.
