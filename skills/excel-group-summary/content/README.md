# Excel Group Summary

Excel multi-dimensional group summary skill for batch data aggregation.

## Quick Start

```bash
python scripts/group_summary.py \
  --source-file data.xlsx \
  --source-sheet Sheet1 \
  --group-cols "项目类别,项目名称" \
  --sum-col 金额 \
  --output-file summary.xlsx \
  --merge-cols "项目类别"
```

## Features

- Multi-dimensional grouping
- Automatic cell merging
- Currency formatting
- Subtotal and total calculation

## Requirements

- Python 3.8+
- openpyxl
- pandas
