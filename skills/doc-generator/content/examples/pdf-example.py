"""
PDF 报告生成示例
生成一个带表格和图表的月度销售报告
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# 注册中文字体
pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))

def create_sales_report(data, output_path):
    """生成月度销售报告 PDF"""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # 自定义样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='SimHei',
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName='SimHei',
        fontSize=14,
        spaceAfter=12
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName='SimSun',
        fontSize=10,
        spaceAfter=6
    )

    # 构建文档内容
    elements = []

    # 标题
    elements.append(Paragraph("月度销售报告", title_style))
    elements.append(Spacer(1, 20))

    # 汇总信息
    summary_data = [
        ['报告周期', data['period']],
        ['总销售额', f"¥{data['total_sales']:,.2f}"],
        ['订单数量', str(data['order_count'])],
        ['平均客单价', f"¥{data['avg_order_value']:,.2f}"]
    ]

    summary_table = Table(summary_data, colWidths=[4*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'SimHei'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    # 销售明细表
    elements.append(Paragraph("销售明细", heading_style))

    table_data = [['产品类别', '销售额', '订单数', '占比', '环比增长']]

    for item in data['categories']:
        table_data.append([
            item['name'],
            f"¥{item['sales']:,.2f}",
            str(item['orders']),
            f"{item['share']:.1f}%",
            f"{item['growth']:+.1f}%"
        ])

    # 添加合计行
    table_data.append(['合计', f"¥{data['total_sales']:,.2f}", str(data['order_count']), '100%', ''])

    detail_table = Table(table_data, colWidths=[4*cm, 4*cm, 3*cm, 3*cm, 3*cm])
    detail_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'SimHei'),
        ('FONTNAME', (0, 1), (-1, -2), 'SimSun'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F5F5F5')]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8E8E8')),
        ('FONTNAME', (0, -1), (-1, -1), 'SimHei'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(detail_table)

    # 分页
    elements.append(PageBreak())

    # 分析说明
    elements.append(Paragraph("分析说明", heading_style))

    analysis_text = f"""
    本月销售表现分析：

    1. <b>整体情况</b>：总销售额 {data['total_sales']:,.2f} 元，环比{'增长' if data['growth'] > 0 else '下降'} {abs(data['growth']):.1f}%

    2. <b>品类表现</b>：{data['top_category']} 表现最佳，占总销售额的 {data['top_share']:.1f}%

    3. <b>趋势判断</b>：{data['trend']}
    """
    elements.append(Paragraph(analysis_text, body_style))

    # 页脚信息
    elements.append(Spacer(1, 50))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='SimSun',
        fontSize=8,
        alignment=TA_RIGHT,
        textColor=colors.grey
    )
    elements.append(Paragraph(f"生成时间：2024-01-15  |  文档版本：v1.0", footer_style))

    # 生成 PDF
    doc.build(elements)
    print(f"报告已生成：{output_path}")


# 示例数据
sample_data = {
    'period': '2024年1月',
    'total_sales': 1256800.50,
    'order_count': 3456,
    'avg_order_value': 363.66,
    'growth': 12.5,
    'top_category': '电子产品',
    'top_share': 45.2,
    'trend': '继续保持增长势头，建议加大热销品类库存',
    'categories': [
        {'name': '电子产品', 'sales': 568000, 'orders': 1234, 'share': 45.2, 'growth': 15.3},
        {'name': '服装鞋帽', 'sales': 289000, 'orders': 876, 'share': 23.0, 'growth': 8.5},
        {'name': '食品饮料', 'sales': 156800, 'orders': 654, 'share': 12.5, 'growth': -2.1},
        {'name': '家居用品', 'sales': 134500, 'orders': 423, 'share': 10.7, 'growth': 5.8},
        {'name': '其他', 'sales': 108500.50, 'orders': 269, 'share': 8.6, 'growth': 3.2},
    ]
}

if __name__ == '__main__':
    output = r"C:\Users\HP\Desktop\月度销售报告.pdf"
    create_sales_report(sample_data, output)
