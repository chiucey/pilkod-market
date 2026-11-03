#!/usr/bin/env python3
"""
订单汇总处理脚本
处理采购订单和委外订单，生成标准格式的汇总Excel文件
"""

import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

# 风险等级颜色配置
COLORS = {
    '超期': '#FF6B6B',      # 红色 - 需要立即跟进
    '临期': '#FFA94D',      # 橙色 - 3天内需关注
    '近期': '#FFE066',      # 黄色 - 7天内需关注
    '正常': '#69DB7C',      # 绿色 - 正常跟进
}

def calculate_status(required_date_str, current_date=None):
    """
    计算到货状态
    要求到货日期：有承诺到货日期用承诺，没有承诺用计划
    """
    if current_date is None:
        current_date = datetime.now()

    if not required_date_str:
        return "未知", 0

    try:
        if isinstance(required_date_str, str):
            required_date = pd.to_datetime(required_date_str)
        else:
            required_date = pd.to_datetime(required_date_str)

        days_diff = (required_date - current_date).days

        if days_diff < 0:
            return f"已超期{abs(days_diff)}天", days_diff
        elif days_diff == 0:
            return f"临期(0天)", days_diff
        elif days_diff <= 3:
            return f"临期({days_diff}天)", days_diff
        elif days_diff <= 7:
            return f"近期({days_diff}天)", days_diff
        else:
            return f"正常({days_diff}天)", days_diff
    except:
        return "日期错误", 0


def get_status_color(status_text):
    """根据状态文本返回对应的填充颜色"""
    if '已超期' in status_text:
        return COLORS['超期']
    elif '临期' in status_text:
        return COLORS['临期']
    elif '近期' in status_text:
        return COLORS['近期']
    else:
        return COLORS['正常']


def create_instruction_sheet(wb, current_date):
    """创建使用说明工作表"""
    ws = wb.active
    ws.title = "📖使用说明"

    # 标题
    ws.merge_cells('A1:E1')
    ws['A1'] = '供应商未到货订单跟进表'
    ws['A1'].font = Font(size=18, bold=True)
    ws['A1'].alignment = Alignment(horizontal='center')

    # 生成日期
    ws['A3'] = f'生成日期：{current_date.strftime("%Y-%m-%d")}'

    # 逻辑说明
    ws['A5'] = '📌 逻辑说明'
    ws['A5'].font = Font(bold=True)
    ws['A6'] = '• 要求到货日期：有承诺到货日期用承诺，没有承诺用计划'
    ws['A7'] = '• 到货状态判断：按当前时间和要求到货日期计算'

    # 颜色图例
    ws['A9'] = '🎨 颜色图例（风险等级）'
    ws['A9'].font = Font(bold=True)

    colors_data = [
        ('🔴 已超期', COLORS['超期'], '需要立即跟进处理'),
        ('🟠 临期', COLORS['临期'], '3天内需关注'),
        ('🟡 近期', COLORS['近期'], '7天内需关注'),
        ('🟢 正常', COLORS['正常'], '正常跟进'),
    ]

    for i, (label, color, desc) in enumerate(colors_data, start=10):
        ws.cell(row=i, column=1, value=label)
        cell = ws.cell(row=i, column=2)
        cell.fill = PatternFill(start_color=color, end_color=color, fill_type='solid')
        ws.cell(row=i, column=3, value=desc)

    # 设置列宽
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 25


def process_order_data(df, order_type, current_date=None):
    """
    处理订单数据，添加状态计算列
    """
    if current_date is None:
        current_date = datetime.now()

    df = df.copy()
    df['订单类型'] = order_type

    # 计算到货状态
    statuses = df['要求到货日期'].apply(lambda x: calculate_status(x, current_date))
    df['到货状态判断'] = statuses.apply(lambda x: x[0])
    df['days_diff'] = statuses.apply(lambda x: x[1])

    return df


def create_summary_sheets(wb, all_data, suppliers_list, current_date):
    """创建汇总和供应商工作表"""
    # 定义列顺序
    columns = ['订单类型', '供应商', '订单编号', '存货编码', '存货名称', '规格型号',
               '数量', '累计到货数量', '累计入库数量', '计划到货日期',
               '承诺到货日期', '要求到货日期', '到货状态判断', '预计货期']

    # 准备表头
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_font = Font(color='FFFFFF', bold=True)

    # 1. 创建超期临期汇总表
    ws_warning = wb.create_sheet("⚠️超期临期需跟进")
    warning_data = all_data[all_data['days_diff'] <= 3].sort_values('days_diff')
    warning_data = warning_data[columns[:-1]]  # 排除预计货期列

    # 写入表头
    for col_idx, col_name in enumerate(warning_data.columns, 1):
        cell = ws_warning.cell(row=1, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font

    # 写入数据
    for row_idx, row_data in enumerate(warning_data.values, 2):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws_warning.cell(row=row_idx, column=col_idx, value=value)
            # 添加颜色
            status = row_data[columns.index('到货状态判断') - 1] if '到货状态判断' in columns else ''
            if '到货状态判断' in warning_data.columns:
                status_idx = list(warning_data.columns).index('到货状态判断')
                status = row_data[status_idx]
            cell.fill = PatternFill(start_color=get_status_color(status),
                                   end_color=get_status_color(status), fill_type='solid')

    # 2. 创建全部汇总表
    ws_all = wb.create_sheet("📋全部未到货汇总")
    all_sorted = all_data.sort_values(['days_diff', '供应商'])
    all_sorted = all_sorted[columns]

    # 写入表头
    for col_idx, col_name in enumerate(columns, 1):
        cell = ws_all.cell(row=1, column=col_idx, value=col_name)
        cell.fill = header_fill
        cell.font = header_font

    # 写入数据
    for row_idx, row_data in enumerate(all_sorted.values, 2):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws_all.cell(row=row_idx, column=col_idx, value=value)
            status_idx = columns.index('到货状态判断')
            status = row_data[status_idx]
            cell.fill = PatternFill(start_color=get_status_color(status),
                                   end_color=get_status_color(status), fill_type='solid')

    # 3. 按供应商创建工作表
    for supplier in suppliers_list:
        supplier_data = all_data[all_data['供应商'] == supplier].sort_values('days_diff')
        # 简化供应商名称用于工作表名
        short_name = supplier[:10]  # 取前10个字符

        ws = wb.create_sheet(short_name)
        supplier_sorted = supplier_data[columns]

        # 写入表头
        for col_idx, col_name in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_name)
            cell.fill = header_fill
            cell.font = header_font

        # 写入数据
        for row_idx, row_data in enumerate(supplier_sorted.values, 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                status_idx = columns.index('到货状态判断')
                status = row_data[status_idx]
                cell.fill = PatternFill(start_color=get_status_color(status),
                                       end_color=get_status_color(status), fill_type='solid')

        # 设置列宽
        for col_idx in range(1, len(columns) + 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = 18


def generate_order_summary(purchase_file, outsource_file, output_file):
    """
    主函数：生成订单汇总Excel文件
    """
    current_date = datetime.now()

    # 读取数据
    try:
        purchase_df = pd.read_excel(purchase_file)
        outsource_df = pd.read_excel(outsource_file)
    except Exception as e:
        print(f"读取文件失败: {e}")
        return False

    # 处理数据
    purchase_processed = process_order_data(purchase_df, '采购订单', current_date)
    outsource_processed = process_order_data(outsource_df, '委外订单', current_date)

    # 合并数据
    all_data = pd.concat([purchase_processed, outsource_processed], ignore_index=True)

    # 获取供应商列表
    suppliers_list = all_data['供应商'].unique().tolist()

    # 创建工作簿
    wb = openpyxl.Workbook()

    # 创建使用说明
    create_instruction_sheet(wb, current_date)

    # 创建汇总表
    create_summary_sheets(wb, all_data, suppliers_list, current_date)

    # 保存文件
    try:
        wb.save(output_file)
        print(f"汇总文件已生成: {output_file}")
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法: python process_orders.py <采购订单文件> <委外订单文件> <输出文件>")
        sys.exit(1)

    purchase_file = sys.argv[1]
    outsource_file = sys.argv[2]
    output_file = sys.argv[3]

    success = generate_order_summary(purchase_file, outsource_file, output_file)
    sys.exit(0 if success else 1)
