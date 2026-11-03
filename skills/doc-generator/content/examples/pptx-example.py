"""
PowerPoint 演示文稿生成示例
生成专业的数据汇报 PPT
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import nsmap
from pptx.oxml import parse_xml

def hex_to_rgb(hex_color):
    """HEX颜色转RGB"""
    hex_color = hex_color.lstrip('#')
    return RGBColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def add_title_slide(prs, title, subtitle=""):
    """添加标题页"""
    slide_layout = prs.slide_layouts[6]  # 空白布局
    slide = prs.slides.add_slide(slide_layout)

    # 背景色块
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, prs.slide_height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb('#1a365d')  # 深蓝色
    shape.line.fill.background()

    # 标题
    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(1.5))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    p.alignment = PP_ALIGN.CENTER

    # 副标题
    if subtitle:
        subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(4.2), Inches(11), Inches(1))
        tf = subtitle_box.text_frame
        p = tf.paragraphs[0]
        p.text = subtitle
        p.font.size = Pt(24)
        p.font.color.rgb = RGBColor(200, 200, 200)
        p.alignment = PP_ALIGN.CENTER

    return slide


def add_content_slide(prs, title, content_items, has_chart=False):
    """添加内容页"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    # 顶部装饰条
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, Inches(1.2)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb('#4472C4')
    shape.line.fill.background()

    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    # 内容区域
    content_top = Inches(1.6)
    if has_chart:
        content_top = Inches(1.6)

    content_box = slide.shapes.add_textbox(Inches(0.5), content_top, Inches(12), Inches(5))
    tf = content_box.text_frame
    tf.word_wrap = True

    for i, item in enumerate(content_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()

        p.text = f"• {item}"
        p.font.size = Pt(20)
        p.font.color.rgb = RGBColor(50, 50, 50)
        p.space_after = Pt(12)
        p.level = 0

    # 页脚装饰
    footer = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), prs.slide_height - Inches(0.3),
        prs.slide_width, Inches(0.3)
    )
    footer.fill.solid()
    footer.fill.fore_color.rgb = hex_to_rgb('#E8E8E8')
    footer.line.fill.background()

    return slide


def add_data_slide(prs, title, headers, data_rows):
    """添加数据表格页"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    # 顶部装饰
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, Inches(1.2)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb('#4472C4')
    shape.line.fill.background()

    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.8))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    # 表格
    rows = len(data_rows) + 1
    cols = len(headers)

    table = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(1.6), Inches(12), Inches(0.5 * rows)).table

    # 表头
    for col, header in enumerate(headers):
        cell = table.cell(0, col)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = hex_to_rgb('#4472C4')
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.font.size = Pt(14)
        p.alignment = PP_ALIGN.CENTER

    # 数据行
    for row_idx, row_data in enumerate(data_rows):
        for col_idx, value in enumerate(row_data):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = str(value)
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(12)
            p.alignment = PP_ALIGN.CENTER
            # 隔行变色
            if row_idx % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = hex_to_rgb('#F5F5F5')

    # 页脚
    footer = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), prs.slide_height - Inches(0.3),
        prs.slide_width, Inches(0.3)
    )
    footer.fill.solid()
    footer.fill.fore_color.rgb = hex_to_rgb('#E8E8E8')
    footer.line.fill.background()

    return slide


def add_summary_slide(prs, key_points, conclusion):
    """添加总结页"""
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)

    # 背景
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        prs.slide_width, prs.slide_height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb('#1a365d')
    shape.line.fill.background()

    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = "总结"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

    # 要点
    content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.8), Inches(12), Inches(4))
    tf = content_box.text_frame
    tf.word_wrap = True

    for i, point in enumerate(key_points):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = f"✓ {point}"
        p.font.size = Pt(22)
        p.font.color.rgb = RGBColor(200, 255, 200)
        p.space_after = Pt(18)

    # 结论
    conclusion_box = slide.shapes.add_textbox(Inches(0.5), Inches(5.5), Inches(12), Inches(1.5))
    tf = conclusion_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = conclusion
    p.font.size = Pt(18)
    p.font.italic = True
    p.font.color.rgb = RGBColor(255, 220, 100)

    return slide


def create_presentation(data, output_path):
    """生成完整演示文稿"""

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 1. 封面
    add_title_slide(prs, data['title'], data['subtitle'])

    # 2. 目录
    add_content_slide(prs, "目录", [f"{i+1}. {item}" for i, item in enumerate(data['toc'])])

    # 3. 背景介绍
    add_content_slide(prs, "背景介绍", data['background'])

    # 4. 数据展示
    add_data_slide(prs, "数据分析", data['table_headers'], data['table_data'])

    # 5. 关键发现
    add_content_slide(prs, "关键发现", data['findings'])

    # 6. 建议方案
    add_content_slide(prs, "建议方案", data['recommendations'])

    # 7. 总结
    add_summary_slide(prs, data['summary_points'], data['conclusion'])

    # 8. 致谢
    add_title_slide(prs, "谢谢", data.get('contact', ''))

    prs.save(output_path)
    print(f"演示文稿已生成：{output_path}")


# ============ 示例数据 ============
sample_data = {
    'title': '2024年Q1季度汇报',
    'subtitle': '销售业绩与市场分析',
    'toc': ['背景介绍', '数据分析', '关键发现', '建议方案', '总结'],
    'background': [
        '市场竞争加剧，需优化产品结构',
        '用户需求多元化，推动服务升级',
        '数字化转型成为行业趋势',
        '成本控制压力持续增大'
    ],
    'table_headers': ['部门', 'Q1目标', 'Q1实际', '完成率', '同比增长率'],
    'table_data': [
        ['销售一部', '500万', '580万', '116%', '+15%'],
        ['销售二部', '400万', '420万', '105%', '+8%'],
        ['市场部', '200万', '185万', '92.5%', '+3%'],
        ['运营部', '150万', '162万', '108%', '+12%'],
    ],
    'findings': [
        '整体完成率达108%，超预期完成目标',
        '销售一部表现突出，增速领先',
        '产品A销量增长显著，成为新的增长点',
        '华南区域市场份额提升至28%'
    ],
    'recommendations': [
        '加大产品A的生产和推广力度',
        '复制销售一部的成功经验',
        '加强华南区域深耕',
        '优化成本结构，提升利润率'
    ],
    'summary_points': [
        'Q1业绩超预期，同比增长9.5%',
        '拳头产品市场份额稳步提升',
        '团队执行力显著增强',
        '建议保持当前策略，稳步推进'
    ],
    'conclusion': '在团队共同努力下，Q1圆满完成目标，为全年打下坚实基础。',
    'contact': '联系方式：xxx@company.com'
}

if __name__ == '__main__':
    output = r"C:\Users\HP\Desktop\季度汇报.pptx"
    create_presentation(sample_data, output)
