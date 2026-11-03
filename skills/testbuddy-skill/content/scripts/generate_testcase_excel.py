#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例Excel生成脚本
将测试用例数据生成Excel格式的文件

使用方式:
    python generate_testcase_excel.py --testcases <testcases_json_file> --requirement-id <需求ID>
    python generate_testcase_excel.py --testcases testcases.json --requirement-id 1167410840001329364
"""
import json
import sys
import os
import argparse
from datetime import datetime

if sys.version_info[0] < 3:
    print("错误：此脚本需要 Python 3", file=sys.stderr)
    sys.exit(1)

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


def create_testcase_excel(testcases, requirement_id, output_file):
    """创建测试用例Excel文件"""
    if not HAS_OPENPYXL:
        return None, "缺少 openpyxl 库，请安装: pip install openpyxl"
    
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "测试用例"
        
        header_font = Font(bold=True, size=11)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font_white = Font(bold=True, size=11, color="FFFFFF")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        cell_alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        headers = ["用例名称", "需求ID", "前置条件", "用例步骤", "预期结果", "用例等级"]
        
        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font_white
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
        
        ws.column_dimensions['A'].width = 40
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 30
        ws.column_dimensions['D'].width = 60
        ws.column_dimensions['E'].width = 40
        ws.column_dimensions['F'].width = 12
        
        ws.row_dimensions[1].height = 25
        
        for row_idx, testcase in enumerate(testcases, start=2):
            name = testcase.get('name', '')
            preconditions = testcase.get('preconditions', '')
            steps = testcase.get('steps', '')
            expected_result = testcase.get('expected_result', '')
            priority = testcase.get('priority', '中')
            
            steps_text = format_steps(steps)
            
            ws.cell(row=row_idx, column=1, value=name)
            ws.cell(row=row_idx, column=2, value=requirement_id)
            ws.cell(row=row_idx, column=3, value=preconditions)
            ws.cell(row=row_idx, column=4, value=steps_text)
            ws.cell(row=row_idx, column=5, value=expected_result)
            ws.cell(row=row_idx, column=6, value=priority)
            
            for col_idx in range(1, 7):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.alignment = cell_alignment
                cell.border = thin_border
            
            ws.row_dimensions[row_idx].height = max(60, len(steps_text) // 3)
        
        wb.save(output_file)
        
        return {
            'file_path': output_file,
            'total_cases': len(testcases),
            'requirement_id': requirement_id
        }, None
        
    except Exception as e:
        return None, "Excel生成失败: {}".format(str(e))


def format_steps(steps):
    """格式化用例步骤"""
    if isinstance(steps, list):
        steps_text = ""
        for idx, step in enumerate(steps, start=1):
            step_desc = step.get('step', step.get('description', ''))
            step_expected = step.get('expected', step.get('expected_result', ''))
            
            steps_text += "步骤{}：{}\n".format(idx, step_desc)
            if step_expected:
                steps_text += "预期：{}\n".format(step_expected)
            steps_text += "\n"
        return steps_text.strip()
    elif isinstance(steps, str):
        return steps
    else:
        return ""


def main():
    parser = argparse.ArgumentParser(description='生成测试用例Excel文件')
    parser.add_argument('--testcases', required=True, help='测试用例JSON文件路径')
    parser.add_argument('--requirement-id', required=True, help='需求ID')
    parser.add_argument('--output', help='输出文件路径（可选）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.testcases):
        print(json.dumps({
            'status': 'error',
            'msg': '测试用例文件不存在: {}'.format(args.testcases)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    try:
        with open(args.testcases, 'r', encoding='utf-8') as f:
            testcases = json.load(f)
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'msg': '测试用例文件解析失败: {}'.format(str(e))
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    if not isinstance(testcases, list):
        print(json.dumps({
            'status': 'error',
            'msg': '测试用例文件格式错误，应该是一个数组'
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.getcwd(), '.testbuddy', 'md')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'testcases_{}_{}.xlsx'.format(args.requirement_id, timestamp))
    
    result, error = create_testcase_excel(testcases, args.requirement_id, output_file)
    
    if error:
        print(json.dumps({
            'status': 'error',
            'msg': error
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    print(json.dumps({
        'status': 'success',
        'msg': '测试用例Excel文件生成成功',
        'result': result
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
