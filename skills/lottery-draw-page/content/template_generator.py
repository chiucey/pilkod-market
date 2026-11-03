#!/usr/bin/env python3
"""
Excel抽奖模板生成器
生成标准格式的抽奖Excel模板文件
"""

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import os


def create_lottery_template():
    """创建抽奖模板"""
    wb = Workbook()

    # 设置默认字体
    default_font = Font(name='微软雅黑', size=12)
    header_font = Font(name='微软雅黑', size=14, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_alignment = Alignment(horizontal='center', vertical='center')

    # ========== Sheet1: 参与人员 ==========
    ws1 = wb.active
    ws1.title = '参与人员'

    # 标题行
    headers = ['姓名', '部门', '工号']
    for col, header in enumerate(headers, 1):
        cell = ws1.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_alignment
        cell.border = border

    # 示例数据
    sample_data = [
        ['张小明', '技术部', 'EMP001'],
        ['李小红', '市场部', 'EMP002'],
        ['王小华', '财务部', 'EMP003'],
        ['刘小丽', '人事部', 'EMP004'],
        ['陈小军', '技术部', 'EMP005'],
    ]

    for row_idx, row_data in enumerate(sample_data, 2):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws1.cell(row=row_idx, column=col_idx, value=value)
            cell.font = default_font
            cell.alignment = center_alignment
            cell.border = border

    # 设置列宽
    ws1.column_dimensions['A'].width = 15
    ws1.column_dimensions['B'].width = 15
    ws1.column_dimensions['C'].width = 15

    # ========== Sheet2: 一等奖 ==========
    ws2 = wb.create_sheet('一等奖')

    headers = ['奖品名称', '数量']
    for col, header in enumerate(headers, 1):
        cell = ws2.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = PatternFill(start_color='FFD700', end_color='FFD700', fill_type='solid')
        cell.alignment = center_alignment
        cell.border = border

    # 一等奖示例
    ws2.cell(row=2, column=1, value='iPhone 15 Pro Max').alignment = center_alignment
    ws2.cell(row=2, column=2, value=3).alignment = center_alignment

    for row in ws2.iter_rows(min_row=1, max_row=2):
        for cell in row:
            cell.font = default_font
            cell.border = border

    ws2.column_dimensions['A'].width = 25
    ws2.column_dimensions['B'].width = 10

    # ========== Sheet3: 二等奖 ==========
    ws3 = wb.create_sheet('二等奖')

    headers = ['奖品名称', '数量']
    for col, header in enumerate(headers, 1):
        cell = ws3.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = PatternFill(start_color='C0C0C0', end_color='C0C0C0', fill_type='solid')
        cell.alignment = center_alignment
        cell.border = border

    # 二等奖示例
    ws3.cell(row=2, column=1, value='AirPods Pro 2').alignment = center_alignment
    ws3.cell(row=2, column=2, value=5).alignment = center_alignment

    for row in ws3.iter_rows(min_row=1, max_row=2):
        for cell in row:
            cell.font = default_font
            cell.border = border

    ws3.column_dimensions['A'].width = 25
    ws3.column_dimensions['B'].width = 10

    # ========== Sheet4: 三等奖 ==========
    ws4 = wb.create_sheet('三等奖')

    headers = ['奖品名称', '数量']
    for col, header in enumerate(headers, 1):
        cell = ws4.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = PatternFill(start_color='CD7F32', end_color='CD7F32', fill_type='solid')
        cell.alignment = center_alignment
        cell.border = border

    # 三等奖示例
    ws4.cell(row=2, column=1, value='小米手环8').alignment = center_alignment
    ws4.cell(row=2, column=2, value=10).alignment = center_alignment

    for row in ws4.iter_rows(min_row=1, max_row=2):
        for cell in row:
            cell.font = default_font
            cell.border = border

    ws4.column_dimensions['A'].width = 25
    ws4.column_dimensions['B'].width = 10

    # ========== Sheet5: 纪念奖 ==========
    ws5 = wb.create_sheet('纪念奖')

    headers = ['奖品名称', '数量']
    for col, header in enumerate(headers, 1):
        cell = ws5.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = PatternFill(start_color='FF69B4', end_color='FF69B4', fill_type='solid')
        cell.alignment = center_alignment
        cell.border = border

    # 纪念奖示例
    ws5.cell(row=2, column=1, value='定制马克杯').alignment = center_alignment
    ws5.cell(row=2, column=2, value=30).alignment = center_alignment

    for row in ws5.iter_rows(min_row=1, max_row=2):
        for cell in row:
            cell.font = default_font
            cell.border = border

    ws5.column_dimensions['A'].width = 25
    ws5.column_dimensions['B'].width = 10

    return wb


def save_template(filepath=None):
    """保存模板到文件"""
    if filepath is None:
        filepath = '抽奖模板.xlsx'

    wb = create_lottery_template()
    wb.save(filepath)
    print(f'模板已保存到: {os.path.abspath(filepath)}')
    return filepath


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='生成抽奖Excel模板')
    parser.add_argument('-o', '--output', help='输出文件路径', default='抽奖模板.xlsx')
    args = parser.parse_args()

    save_template(args.output)


if __name__ == '__main__':
    main()
