#!/usr/bin/env python3
"""Detect red-font cells in the career planning Excel template.

Usage:
    python detect_red_cells.py <excel_path>

Output: prints each red cell's reference, column header context, and current value.
"""
import sys
import openpyxl
from openpyxl.utils import get_column_letter


def detect_red_cells(path: str):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    red_cells = []
    for row in range(1, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):
            cell = ws.cell(row=row, column=col)
            if cell.value is None:
                continue
            color = cell.font.color
            if color and color.rgb and "FF0000" in str(color.rgb).upper():
                ref = f"{get_column_letter(col)}{row}"
                red_cells.append({
                    "ref": ref,
                    "value": str(cell.value),
                })
    return red_cells


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_red_cells.py <excel_path>")
        sys.exit(1)
    cells = detect_red_cells(sys.argv[1])
    for c in cells:
        print(f"\n=== {c['ref']} ===")
        preview = c["value"][:200] + "..." if len(c["value"]) > 200 else c["value"]
        print(preview)
    print(f"\nTotal red cells: {len(cells)}")
