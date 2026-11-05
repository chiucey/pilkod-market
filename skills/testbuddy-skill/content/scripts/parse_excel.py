#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 文件解析脚本
将 Excel 文件转换为测试节点 JSON 格式

支持的 Excel 格式：
1. 标准格式：每行一个节点，包含 uid, name, kind, parent_uid, description 等列
2. 层级格式：通过缩进或层级列表示父子关系
3. 自定义格式：通过配置文件指定列映射

使用方式:
    python parse_excel.py <excel_file> [--sheet <sheet_name>] [--format <format_type>]
    python parse_excel.py <excel_file> --output json
    python parse_excel.py <excel_file> --output yaml
"""
import json
import sys
import os
import argparse

if sys.version_info[0] < 3:
    print("错误：此脚本需要 Python 3", file=sys.stderr)
    sys.exit(1)

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

try:
    import xlrd
    HAS_XLRD = True
except ImportError:
    HAS_XLRD = False


def generate_uid(kind):
    """生成节点的唯一ID"""
    import random
    import string
    chars = string.ascii_letters + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(10))
    return "{}-{}".format(kind.lower().replace('_', '-'), random_str)


def parse_xlsx(file_path, sheet_name=None, format_type='standard'):
    """解析 .xlsx 文件"""
    if not HAS_OPENPYXL:
        return None, "缺少 openpyxl 库，请安装: pip install openpyxl"
    
    try:
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        
        if sheet_name:
            if sheet_name not in workbook.sheetnames:
                return None, "工作表 '{}' 不存在，可用工作表: {}".format(sheet_name, workbook.sheetnames)
            sheet = workbook[sheet_name]
        else:
            sheet = workbook.active
        
        rows = list(sheet.iter_rows(values_only=True))
        
        if len(rows) == 0:
            return None, "Excel 文件为空"
        
        if format_type == 'standard':
            return parse_standard_format(rows)
        elif format_type == 'hierarchical':
            return parse_hierarchical_format(rows)
        else:
            return parse_standard_format(rows)
            
    except Exception as e:
        return None, "Excel 解析失败: {}".format(str(e))


def parse_xls(file_path, sheet_name=None, format_type='standard'):
    """解析 .xls 文件"""
    if not HAS_XLRD:
        return None, "缺少 xlrd 库，请安装: pip install xlrd"
    
    try:
        workbook = xlrd.open_workbook(file_path, ignore_workbook_corruption=True)
        
        if sheet_name:
            sheet_indices = [i for i in range(workbook.nsheets) if workbook.sheet_names()[i] == sheet_name]
            if not sheet_indices:
                return None, "工作表 '{}' 不存在，可用工作表: {}".format(sheet_name, workbook.sheet_names())
            sheet = workbook.sheet_by_index(sheet_indices[0])
        else:
            sheet = workbook.sheet_by_index(0)
        
        rows = []
        for row_idx in range(sheet.nrows):
            row = []
            for col_idx in range(sheet.ncols):
                cell = sheet.cell(row_idx, col_idx)
                row.append(cell.value)
            rows.append(row)
        
        if len(rows) == 0:
            return None, "Excel 文件为空"
        
        if format_type == 'standard':
            return parse_standard_format(rows)
        elif format_type == 'hierarchical':
            return parse_hierarchical_format(rows)
        else:
            return parse_standard_format(rows)
            
    except Exception as e:
        return None, "Excel 解析失败: {}".format(str(e))


def parse_standard_format(rows):
    """
    解析标准格式的 Excel
    动态识别所有列，提取全量字段作为参考
    """
    if len(rows) < 2:
        return None, "Excel 至少需要包含表头和一行数据"
    
    header = [str(cell).strip() if cell else '' for cell in rows[0]]
    
    cases = []
    for row_idx, row in enumerate(rows[1:], start=2):
        if not any(row):
            continue
        
        case = {}
        
        for col_idx, col_name in enumerate(header):
            if not col_name:
                continue
            
            if col_idx < len(row) and row[col_idx] is not None:
                value = row[col_idx]
                
                if isinstance(value, float):
                    if value.is_integer():
                        value = int(value)
                    value = str(value)
                elif value is not None:
                    value = str(value).strip()
                else:
                    continue
                
                if value:
                    case[col_name] = value
        
        if case:
            cases.append(case)
    
    return cases, None


def parse_hierarchical_format(rows):
    """
    解析层级格式的 Excel
    动态识别所有列，提取全量字段作为参考
    """
    if len(rows) < 2:
        return None, "Excel 至少需要包含表头和一行数据"
    
    header = [str(cell).strip() if cell else '' for cell in rows[0]]
    
    cases = []
    for row_idx, row in enumerate(rows[1:], start=2):
        if not any(row):
            continue
        
        case = {}
        
        for col_idx, col_name in enumerate(header):
            if not col_name:
                continue
            
            if col_idx < len(row) and row[col_idx] is not None:
                value = row[col_idx]
                
                if isinstance(value, float):
                    if value.is_integer():
                        value = int(value)
                    value = str(value)
                elif value is not None:
                    value = str(value).strip()
                else:
                    continue
                
                if value:
                    case[col_name] = value
        
        if case:
            cases.append(case)
    
    return cases, None


def parse_excel_file(file_path, sheet_name=None, format_type='standard'):
    """根据文件扩展名选择解析方法"""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.xlsx':
        return parse_xlsx(file_path, sheet_name, format_type)
    elif ext == '.xls':
        return parse_xls(file_path, sheet_name, format_type)
    else:
        return None, "不支持的文件格式: {}，支持的格式: .xlsx, .xls".format(ext)


def main():
    parser = argparse.ArgumentParser(description='解析 Excel 文件为测试节点格式')
    parser.add_argument('excel_file', help='Excel 文件路径')
    parser.add_argument('--sheet', help='工作表名称（可选）')
    parser.add_argument('--format', choices=['standard', 'hierarchical'], default='standard',
                        help='Excel 格式类型：standard（标准格式）或 hierarchical（层级格式）')
    parser.add_argument('--output', choices=['json', 'yaml'], default='json', help='输出格式')
    parser.add_argument('--output-file', help='输出文件路径（可选）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.excel_file):
        error_msg = json.dumps({
            'status': 'error',
            'msg': '文件不存在: {}'.format(args.excel_file)
        }, ensure_ascii=False, indent=2)
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)
        else:
            print(error_msg)
        sys.exit(1)
    
    nodes, error = parse_excel_file(args.excel_file, args.sheet, args.format)
    
    if error:
        error_msg = json.dumps({
            'status': 'error',
            'msg': error
        }, ensure_ascii=False, indent=2)
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)
        else:
            print(error_msg)
        sys.exit(1)
    
    if args.output == 'yaml':
        try:
            import yaml
            output_str = yaml.dump(nodes, allow_unicode=True, default_flow_style=False)
        except ImportError:
            output_str = json.dumps(nodes, ensure_ascii=False, indent=2)
    else:
        output_str = json.dumps(nodes, ensure_ascii=False, indent=2)
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(output_str)
    else:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        print(output_str)


if __name__ == "__main__":
    main()
