"""
Excel 统计报表生成示例
生成带图表和条件格式的数据分析报表
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule

def style_range(ws, start_row, end_row, start_col, end_col, 
                font=None, fill=None, alignment=None, border=None):
    """批量设置单元格样式"""
    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            cell = ws.cell(row=row, column=col)
            if font:
                cell.font = font
            if fill:
                cell.fill = fill
            if alignment:
                cell.alignment = alignment
            if border:
                cell.border = border


def create_data_report(data, output_path):
    """生成数据分析报表"""

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "数据分析"

    # ============ 样式定义 ============
    # 标题样式
    title_font = Font(name='微软雅黑', size=16, bold=True, color='FFFFFF')
    title_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

    # 表头样式
    header_font = Font(name='微软雅黑', size=11, bold=True)
    header_fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")

    # 数据样式
    data_font = Font(name='微软雅黑', size=10)
    data_fill_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    data_fill_even = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

    # 数字格式
    money_format = '#,##0.00'
    percent_format = '0.0%'

    # 居中对齐
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')

    # 边框
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # ============ 标题区域 ============
    ws.merge_cells('A1:H1')
    ws['A1'] = data['title']
    ws['A1'].font = title_font
    ws['A1'].fill = title_fill
    ws['A1'].alignment = center_align
    ws.row_dimensions[1].height = 35

    # 副标题
    ws.merge_cells('A2:H2')
    ws['A2'] = f"统计周期：{data['period']}"
    ws['A2'].font = Font(name='微软雅黑', size=10, italic=True)
    ws['A2'].alignment = center_align

    # ============ 数据表格 ============
    headers = ['序号', '部门', '指标A', '指标B', '指标C', '总计', '占比', '排名']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border

    ws.row_dimensions[4].height = 25

    # 填充数据
    for row_idx, item in enumerate(data['items'], 5):
        # 序号
        ws.cell(row=row_idx, column=1, value=row_idx - 4)
        # 部门
        ws.cell(row=row_idx, column=2, value=item['name'])
        # 指标A
        ws.cell(row=row_idx, column=3, value=item['metric_a'])
        # 指标B
        ws.cell(row=row_idx, column=4, value=item['metric_b'])
        # 指标C
        ws.cell(row=row_idx, column=5, value=item['metric_c'])
        # 总计
        total = item['metric_a'] + item['metric_b'] + item['metric_c']
        ws.cell(row=row_idx, column=6, value=total)
        # 占比
        ws.cell(row=row_idx, column=7, value=item['share'])
        # 排名
        ws.cell(row=row_idx, column=8, value=item['rank'])

        # 应用样式
        fill = data_fill_odd if (row_idx - 5) % 2 == 0 else data_fill_even
        for col in range(1, 9):
            cell = ws.cell(row=row_idx, column=col)
            cell.font = data_font
            cell.fill = fill
            cell.border = thin_border
            if col != 2:
                cell.alignment = center_align
            else:
                cell.alignment = left_align

        # 数字格式
        ws.cell(row=row_idx, column=3).number_format = money_format
        ws.cell(row=row_idx, column=4).number_format = money_format
        ws.cell(row=row_idx, column=5).number_format = money_format
        ws.cell(row=row_idx, column=6).number_format = money_format
        ws.cell(row=row_idx, column=7).number_format = percent_format

    # 合计行
    last_row = 5 + len(data['items'])
    ws.merge_cells(f'A{last_row}:B{last_row}')
    ws.cell(row=last_row, column=1, value='合计')
    ws.cell(row=last_row, column=1).font = Font(name='微软雅黑', size=11, bold=True)
    ws.cell(row=last_row, column=1).alignment = center_align

    for col in range(3, 7):
        col_letter = get_column_letter(col)
        formula = f"=SUM({col_letter}5:{col_letter}{last_row-1})"
        ws.cell(row=last_row, column=col, value=formula)
        ws.cell(row=last_row, column=col).number_format = money_format
        ws.cell(row=last_row, column=col).font = Font(name='微软雅黑', size=11, bold=True)

    ws.cell(row=last_row, column=7, value=1)
    ws.cell(row=last_row, column=7).number_format = percent_format
    ws.cell(row=last_row, column=7).font = Font(name='微软雅黑', size=11, bold=True)

    for col in range(1, 9):
        cell = ws.cell(row=last_row, column=col)
        cell.fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
        cell.border = thin_border
        cell.alignment = center_align

    # ============ 图表 ============
    chart_row = last_row + 2

    # 条形图
    chart1 = BarChart()
    chart1.type = "col"
    chart1.title = "各部门指标对比"
    chart1.y_axis.title = '金额'
    chart1.x_axis.title = '部门'

    data_ref = Reference(ws, min_col=3, min_row=4, max_row=last_row-1, max_col=5)
    cats_ref = Reference(ws, min_col=2, min_row=5, max_row=last_row-1)
    chart1.add_data(data_ref, titles_from_data=True)
    chart1.set_categories(cats_ref)
    chart1.shape = 4
    chart1.width = 15
    chart1.height = 10

    ws.add_chart(chart1, f'A{chart_row}')

    # 饼图
    chart2 = PieChart()
    chart2.title = "占比分布"
    data_ref2 = Reference(ws, min_col=7, min_row=5, max_row=last_row-1)
    cats_ref2 = Reference(ws, min_col=2, min_row=5, max_row=last_row-1)
    chart2.add_data(data_ref2, titles_from_data=True)
    chart2.set_categories(cats_ref2)
    chart2.dataLabels = DataLabelList()
    chart2.dataLabels.showPercent = True
    chart2.dataLabels.showCatName = True
    chart2.width = 10
    chart2.height = 10

    ws.add_chart(chart2, f'H{chart_row}')

    # ============ 列宽设置 ============
    column_widths = {'A': 8, 'B': 15, 'C': 15, 'D': 15, 'E': 15, 'F': 15, 'G': 10, 'H': 8}
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # ============ 条件格式 ============
    # 占比热力图
    ws.conditional_formatting.add(
        f'G5:G{last_row-1}',
        ColorScaleRule(
            start_type='min', start_color='F8696B',
            mid_type='percentile', mid_value=50, mid_color='FFEB84',
            end_type='max', end_color='63BE7B'
        )
    )

    # ============ 冻结窗格 ============
    ws.freeze_panes = 'C5'

    # 保存
    wb.save(output_path)
    print(f"报表已生成：{output_path}")


# ============ 示例数据 ============
sample_data = {
    'title': '部门业绩统计报表',
    'period': '2024年第一季度',
    'items': [
        {'name': '销售部', 'metric_a': 125000, 'metric_b': 89000, 'metric_c': 45600, 'share': 0.32, 'rank': 1},
        {'name': '市场部', 'metric_a': 98000, 'metric_b': 76500, 'metric_c': 32100, 'share': 0.25, 'rank': 2},
        {'name': '技术部', 'metric_a': 87000, 'metric_b': 65400, 'metric_c': 28900, 'share': 0.22, 'rank': 3},
        {'name': '运营部', 'metric_a': 65000, 'metric_b': 54300, 'metric_c': 19800, 'share': 0.17, 'rank': 4},
        {'name': '人事部', 'metric_a': 12000, 'metric_b': 8900, 'metric_c': 4500, 'share': 0.04, 'rank': 5},
    ]
}

if __name__ == '__main__':
    output = r"C:\Users\HP\Desktop\部门业绩统计.xlsx"
    create_data_report(sample_data, output)
