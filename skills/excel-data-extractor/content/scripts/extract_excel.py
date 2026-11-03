#!/usr/bin/env python3
"""Excel数据提取工具 - 将Excel中的非结构化数据提取为标准化JSON"""

import sys
import os
import json
import argparse
import re
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

try:
    import openpyxl
    from openpyxl.utils import get_column_letter
except ImportError:
    print("ERROR: openpyxl is required. Install with: pip install openpyxl", file=sys.stderr)
    sys.exit(1)


def read_all_cells(wb_path):
    """读取Excel文件的所有单元格数据（值和公式）"""
    wb = openpyxl.load_workbook(wb_path, data_only=False)
    result = {}
    for sn in wb.sheetnames:
        ws = wb[sn]
        sheet_data = {
            "max_row": ws.max_row,
            "max_col": ws.max_column,
            "cells": [],
            "merged_cells": [str(m) for m in ws.merged_cells.ranges]
        }
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column, values_only=False):
            for cell in row:
                if cell.value is not None:
                    cell_info = {
                        "ref": cell.coordinate,
                        "value": cell.value,
                        "type": type(cell.value).__name__,
                        "is_formula": isinstance(cell.value, str) and cell.value.startswith("=")
                    }
                    sheet_data["cells"].append(cell_info)
        result[sn] = sheet_data
    return result


def extract_kv_table(ws, max_col=None):
    """从工作表中提取键值对表格（标题行+数据行模式）"""
    wb = openpyxl.load_workbook(ws, data_only=False)
    wb_name = ws
    results = []
    for sn in wb.sheetnames:
        sheet = wb[sn]
        if sheet.max_row < 2:
            continue
        # 读取第一行作为字段名
        headers = []
        for col in range(1, (max_col or sheet.max_column) + 1):
            cell = sheet.cell(row=1, column=col)
            if cell.value is not None:
                headers.append((col, str(cell.value).strip()))
        # 读取后续数据行
        for row_idx in range(2, sheet.max_row + 1):
            row_data = {}
            for col, header in headers:
                cell = sheet.cell(row=row_idx, column=col)
                val = cell.value
                if val is not None and isinstance(val, str) and val.startswith("="):
                    row_data[header] = {
                        "formula": val,
                        "value": None,
                        "is_formula": True
                    }
                else:
                    row_data[header] = val
            results.append(row_data)
    return results


def extract_structured_sheet(ws_path):
    """提取结构化工作表（如报价单），包含键值对和表格区域"""
    wb = openpyxl.load_workbook(ws_path, data_only=False)
    results = []
    for sn in wb.sheetnames:
        sheet = wb[sn]
        all_cells = {}
        for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row, max_col=sheet.max_column, values_only=False):
            for cell in row:
                if cell.value is not None:
                    all_cells[cell.coordinate] = {
                        "value": cell.value,
                        "type": type(cell.value).__name__,
                        "is_formula": isinstance(cell.value, str) and cell.value.startswith("=")
                    }
        results.append({
            "sheet_name": sn,
            "max_row": sheet.max_row,
            "max_col": sheet.max_column,
            "cells": all_cells
        })
    return results


def safe_decimal(val):
    """安全转换为Decimal"""
    if val is None:
        return Decimal('0')
    if isinstance(val, Decimal):
        return val
    try:
        return Decimal(str(val))
    except:
        return Decimal('0')


def calculate_formula_product(formula, cells_map):
    """计算简单的乘法公式（如 =X61*Z61）"""
    match = re.match(r'^=(\w+)\*(\w+)$', formula)
    if not match:
        return None
    ref1, ref2 = match.group(1), match.group(2)
    v1 = _get_cell_value(ref1, cells_map)
    v2 = _get_cell_value(ref2, cells_map)
    if v1 is not None and v2 is not None:
        return safe_decimal(v1) * safe_decimal(v2)
    return None


def _get_cell_value(ref, cells_map):
    """从cells_map中获取单元格的值（跳过公式取原始值）"""
    cell_info = cells_map.get(ref.upper())
    if cell_info is None:
        return None
    v = cell_info.get("value")
    if isinstance(v, str) and v.startswith("="):
        return None  # 引用的也是公式，无法递归
    return v


def number_to_chinese(num):
    """将数字转换为大写中文金额"""
    d = Decimal(str(num)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if d == 0:
        return "零圆整"
    int_part = int(d)
    dec_part = d - int_part
    digits = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    units_int = ['', '拾', '佰', '仟']
    units_big = ['', '万', '亿']
    result = []
    int_str = str(int_part)
    n = len(int_str)
    zero_flag = False
    for i, ch in enumerate(int_str):
        digit = int(ch)
        pos = n - 1 - i
        big_unit = pos // 4
        small_unit = pos % 4
        if digit == 0:
            zero_flag = True
            if small_unit == 0 and big_unit > 0:
                result.append(units_big[big_unit])
                zero_flag = False
        else:
            if zero_flag:
                result.append('零')
                zero_flag = False
            result.append(digits[digit])
            result.append(units_int[small_unit])
            if small_unit == 0 and big_unit > 0:
                result.append(units_big[big_unit])
    if result:
        result.append('圆')
    # 角分
    jiao = int((dec_part * 10).quantize(Decimal('0')))
    fen = int(((dec_part * 100) % 10).quantize(Decimal('0')))
    if jiao > 0:
        result.append(digits[jiao] + '角')
    if fen > 0:
        result.append(digits[fen] + '分')
    elif jiao == 0:
        result.append('整')
    return ''.join(result)


def extract_wx_number(filename):
    """从文件名中提取WX开头的维修编号"""
    match = re.search(r'(WX[A-Za-z0-9]+)', filename)
    if match:
        return match.group(1)
    return None


def compare_totals(cost_part_fee, detail_subtotal):
    """比较费用核算中的部件费与部件明细小计，返回差异信息或None"""
    diff = safe_decimal(cost_part_fee) - safe_decimal(detail_subtotal)
    if diff != 0:
        return {
            "费用核算_部件费": float(safe_decimal(cost_part_fee)),
            "部件明细_小计": float(safe_decimal(detail_subtotal)),
            "差额": float(abs(diff)),
            "差额方向": "费用核算大于明细" if diff > 0 else "明细大于费用核算"
        }
    return None


def main():
    parser = argparse.ArgumentParser(description="Excel数据提取工具")
    parser.add_argument("files", nargs="+", help="Excel文件路径")
    parser.add_argument("--output-dir", "-o", default=".", help="JSON输出目录")
    parser.add_argument("--mode", choices=["auto", "kv", "raw", "structured"], default="auto",
                        help="提取模式: auto=自动, kv=键值对, raw=原始, structured=结构化")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    for fpath in args.files:
        fpath = os.path.abspath(fpath)
        if not os.path.exists(fpath):
            print(f"SKIP: {fpath} (not found)", file=sys.stderr)
            continue

        fname = os.path.basename(fpath)
        print(f"Processing: {fname}")

        if args.mode == "kv":
            data = extract_kv_table(fpath)
        elif args.mode == "raw":
            data = read_all_cells(fpath)
        elif args.mode == "structured":
            data = extract_structured_sheet(fpath)
        else:
            # auto mode: try to detect structure
            wb = openpyxl.load_workbook(fpath, data_only=False)
            if any(ws.max_row <= 2 for ws in wb.worksheets):
                data = extract_kv_table(fpath)
            else:
                data = extract_structured_sheet(fpath)

        output = {
            "文件信息": {
                "原始文件名": fname,
                "维修编号": extract_wx_number(fname),
            },
            "提取数据": data
        }

        out_name = Path(fname).stem + ".json"
        out_path = os.path.join(args.output_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)
        print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
