#!/usr/bin/env python3
"""读取 Excel 文件所有 Sheet 的内容，用于产品质量文档检查"""
import sys
import openpyxl

def read_excel(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        print(f"\n{'='*60}")
        print(f"Sheet: {sheet_name}")
        print('='*60)
        for row in ws.iter_rows(values_only=True):
            if any(cell is not None for cell in row):
                print(row)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 read_excel.py <文件路径>")
        sys.exit(1)
    read_excel(sys.argv[1])
