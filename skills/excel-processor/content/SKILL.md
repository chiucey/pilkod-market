---
name: excel-processor
description: Process Excel files with data manipulation, formatting, and analysis. Use when users ask to read Excel files, create spreadsheets, analyze data, format cells, handle formulas, work with multiple sheets, export to Excel formats, or perform Excel-related data operations.
---

# Excel Processor

Excel data processing skill using Python with openpyxl and pandas libraries.

## Workflow

### Phase 1: Task Analysis
1. Identify user intent (read/write/transform/format/analyze)
2. Determine input file format (.xlsx, .xls, .csv)
3. Assess data complexity (single sheet/multi-sheet, data volume)
4. Clarify output requirements if ambiguous

### Phase 2: Implementation

**For Data Reading:**
```
- Load workbook with openpyxl.load_workbook()
- Read specific sheets or all sheets
- Extract data as list of dicts or DataFrame
- Handle headers, merged cells, empty values
```

**For Data Writing:**
```
- Create new Workbook with openpyxl.Workbook()
- Write data row by row or from DataFrame
- Apply formatting as specified
- Save with proper file extension
```

**For Data Transformation:**
```
- Use pandas for complex operations
- Filter, sort, group data
- Merge/split columns
- Handle missing values
```

**For Formatting:**
```
- Apply cell styles (font, fill, border)
- Set column widths and row heights
- Add borders and alignment
- Apply number formats
```

### Phase 3: Validation
1. Verify data integrity after operations
2. Check output file opens correctly
3. Confirm formatting applied as expected
4. Test formulas calculate correctly

## Quick Reference

**Common Patterns:**
- `pd.read_excel(file, sheet_name=0)` - Read first sheet
- `df.to_excel(file, sheet_name='Sheet1', index=False)` - Write DataFrame
- `wb.save(file)` - Save workbook
- `ws['A1'].value` - Read cell value
- `ws['A1'] = 'value'` - Write cell value

**Output Location:**
- Save processed files to user-specified location
- Default: `/workspace/output/` for new files
- Maintain original file if modifying in place

## Quality Standards

- Preserve original data unless transformation requested
- Handle encoding issues (UTF-8 default)
- Log all operations for transparency
- Provide summary of changes made
