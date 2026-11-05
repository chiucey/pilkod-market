#!/usr/bin/env python3
"""
标准公文格式生成器
基于标准公文格式规范，适用于工作汇报、进展报告、情况说明等正式公文
"""

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from datetime import datetime
import re
import os

# 公文格式配置
GONGWEN_CONFIG = {
    # 纸张与页边距
    'margin_top': Cm(3.6),
    'margin_bottom': Cm(3.5),
    'margin_left': Cm(2.8),
    'margin_right': Cm(2.6),

    # 字体配置
    'font_title': '方正小标宋简体',
    'font_heading1': '黑体',           # 一级标题：一、二、三...
    'font_heading2': '楷体_GB2312',     # 二级标题：（一）（二）...
    'font_heading3': '仿宋_GB2312',     # 三级标题：1. 2. 3...
    'font_body': '仿宋_GB2312',         # 正文
    'font_subtitle': '楷体_GB2312',     # 作者和日期
    'font_en': 'Times New Roman',       # 英文和数字字体

    # 字号配置
    'size_title': 22,      # 2号
    'size_subtitle': 16,   # 3号（汇报单位、日期）
    'size_heading1': 16,   # 3号
    'size_heading2': 16,   # 3号
    'size_heading3': 16,   # 3号
    'size_body': 16,       # 3号

    # 行距
    'line_spacing': 28,    # 固定值28磅
}


def set_first_line_indent_chars(paragraph, char_count):
    """设置首行缩进为指定字符数"""
    # 使用Twips单位：1字符≈240 twips（3号字体）
    twips = char_count * 240
    paragraph.paragraph_format.first_line_indent = Pt(twips / 20)  # 1pt = 20 twips


def convert_to_fullwidth(text):
    """将半角标点符号转换为全角"""
    # 半角转全角映射
    mapping = {
        '!': '！',
        '"': '＂',
        '#': '＃',
        '$': '＄',
        '%': '％',
        '&': '＆',
        "'": '＇',
        '(': '（',
        ')': '）',
        '*': '＊',
        '+': '＋',
        ',': '，',
        '-': '－',
        '.': '。',
        '/': '／',
        ':': '：',
        ';': '；',
        '<': '＜',
        '=': '＝',
        '>': '＞',
        '?': '？',
        '@': '＠',
        '[': '［',
        '\\': '＼',
        ']': '］',
        '^': '＾',
        '_': '＿',
        '`': '｀',
        '{': '｛',
        '|': '｜',
        '}': '｝',
        '~': '～',
    }

    result = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in mapping:
            result.append(mapping[char])
        else:
            result.append(char)
        i += 1

    return ''.join(result)


def set_chinese_font(run, font_name, font_size, bold=False):
    """设置中文字体"""
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(font_size)
    run.font.bold = bold


def set_en_font(run, font_size, bold=False):
    """设置英文字体（Times New Roman）"""
    run.font.name = GONGWEN_CONFIG['font_en']
    run._element.rPr.rFonts.set(qn('w:ascii'), GONGWEN_CONFIG['font_en'])
    run._element.rPr.rFonts.set(qn('w:hAnsi'), GONGWEN_CONFIG['font_en'])
    run.font.size = Pt(font_size)
    run.font.bold = bold


def add_text_with_mixed_fonts(para, text, font_name, font_size, bold=False):
    """添加混合字体的文本（中文用中文字体，英文/数字/标点用Times New Roman）"""
    # 先转换半角标点为全角
    text = convert_to_fullwidth(text)

    # 分割文本：中文字符和非中文字符（包括英文、数字、标点）
    parts = []
    current = []
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            # 中文字符
            if current and not ('\u4e00' <= current[0] <= '\u9fff'):
                parts.append(''.join(current))
                current = []
            current.append(char)
        else:
            # 非中文字符（英文、数字、标点）
            if current and ('\u4e00' <= current[0] <= '\u9fff'):
                parts.append(''.join(current))
                current = []
            current.append(char)
    if current:
        parts.append(''.join(current))

    for part in parts:
        if '\u4e00' <= part[0] <= '\u9fff':
            # 中文部分
            run = para.add_run(part)
            set_chinese_font(run, font_name, font_size, bold)
        else:
            # 非中文部分（英文、数字、标点）
            run = para.add_run(part)
            set_en_font(run, font_size, bold)


def parse_content_sections(content_text):
    """解析文本内容，自动识别标题层级"""
    sections = []
    lines = content_text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 识别一级标题：一、二、三...
        if re.match(r'^[一二三四五六七八九十]+[、.]', line):
            sections.append((1, line))
        # 识别二级标题：（一）（二）...
        elif re.match(r'^[/（\(]?[一二三四五六七八九十]+[/）\)]', line):
            sections.append((2, line))
        # 识别三级标题：1. 2. 3...
        elif re.match(r'^\d+[.、]', line):
            sections.append((3, line))
        else:
            sections.append((0, line))

    return sections


def create_gongwen_document(title='', unit='', date=None, content_sections=None):
    """
    创建公文文档

    参数:
        title: 标题（如：关于XXX的汇报）
        unit: 汇报单位（如：江苏金服）
        date: 日期，默认今天
        content_sections: 内容段落列表，每个元素是 (级别, 内容)
                          级别：0=正文, 1=一级标题, 2=二级标题, 3=三级标题
    """
    doc = Document()
    config = GONGWEN_CONFIG

    if date is None:
        date = datetime.now()

    # 设置页边距
    sections = doc.sections[0]
    sections.top_margin = config['margin_top']
    sections.bottom_margin = config['margin_bottom']
    sections.left_margin = config['margin_left']
    sections.right_margin = config['margin_right']

    # 标题（2号方正小标宋简体，居中，不加粗）
    if title:
        title_para = doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_para.paragraph_format.line_spacing = Pt(config['line_spacing'])
        title_para.paragraph_format.space_before = Pt(0)
        title_para.paragraph_format.space_after = Pt(0)
        add_text_with_mixed_fonts(title_para, title, config['font_title'], config['size_title'], False)

    # 汇报单位（3号楷体_GB2312，居中，大标题下不空行）
    if unit:
        unit_para = doc.add_paragraph()
        unit_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        unit_para.paragraph_format.line_spacing = Pt(config['line_spacing'])
        unit_para.paragraph_format.space_before = Pt(0)
        unit_para.paragraph_format.space_after = Pt(0)
        add_text_with_mixed_fonts(unit_para, unit, config['font_subtitle'], config['size_subtitle'])

    # 日期（3号楷体_GB2312，居中）
    date_para = doc.add_paragraph()
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.paragraph_format.line_spacing = Pt(config['line_spacing'])
    date_para.paragraph_format.space_before = Pt(0)
    date_para.paragraph_format.space_after = Pt(0)
    date_str = date.strftime('%Y年%m月%d日') if isinstance(date, datetime) else date
    add_text_with_mixed_fonts(date_para, date_str, config['font_subtitle'], config['size_subtitle'])

    # 空行
    empty_para = doc.add_paragraph()
    empty_para.paragraph_format.line_spacing = Pt(config['line_spacing'])
    empty_para.paragraph_format.space_before = Pt(0)
    empty_para.paragraph_format.space_after = Pt(0)

    # 正文内容
    if content_sections:
        for level, text in content_sections:
            para = doc.add_paragraph()
            para.paragraph_format.line_spacing = Pt(config['line_spacing'])
            para.paragraph_format.space_before = Pt(0)
            para.paragraph_format.space_after = Pt(0)

            # 所有标题和正文都首行缩进2字符
            set_first_line_indent_chars(para, 2)

            if level == 0:
                # 正文：两端对齐
                para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                add_text_with_mixed_fonts(para, text, config['font_body'], config['size_body'])
            elif level == 1:
                # 一级标题：一、二、三...（黑体，不加粗）
                add_text_with_mixed_fonts(para, text, config['font_heading1'], config['size_heading1'], False)
            elif level == 2:
                # 二级标题：（一）（二）...（楷体_GB2312）
                add_text_with_mixed_fonts(para, text, config['font_heading2'], config['size_heading2'])
            elif level == 3:
                # 三级标题：1. 2. 3...（仿宋_GB2312加粗）
                add_text_with_mixed_fonts(para, text, config['font_heading3'], config['size_heading3'], True)

    return doc


def generate_gongwen(title, unit, content_sections, date=None, output_path=None):
    """
    一键生成公文

    参数:
        title: 标题
        unit: 汇报单位
        content_sections: 内容段落列表，每个元素是 (级别, 内容)
        date: 日期，默认今天
        output_path: 输出路径

    返回:
        输出文件路径
    """
    doc = create_gongwen_document(title, unit, date, content_sections)

    if output_path is None:
        # 确保输出目录存在
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        # 清理标题中的特殊字符
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title)[:20]
        output_path = os.path.join(output_dir, f'{safe_title}.docx')

    doc.save(output_path)
    return output_path


def generate_gongwen_from_text(title, unit, content_text, date=None, output_path=None):
    """
    从纯文本生成公文（自动识别标题层级）

    参数:
        title: 标题
        unit: 汇报单位
        content_text: 正文内容（纯文本，自动识别标题）
        date: 日期，默认今天
        output_path: 输出路径

    返回:
        输出文件路径
    """
    sections = parse_content_sections(content_text)
    return generate_gongwen(title, unit, sections, date, output_path)


if __name__ == '__main__':
    # 测试示例
    test_content = [
        (1, '一、研究院筹建进展'),
        (0, '已完成理事会组建，确定首批理事单位15家，涵盖政府、高校、金融机构等多元主体。研究院设立秘书处、研究部、培训部、合作交流部四个职能部门，配备专职人员8名。2025年全年预算为RMB 5,000,000元。'),
        (2, '（一）组织架构'),
        (0, '设立秘书处、研究部、培训部、合作交流部四个部门，明确各部门职责分工，建立高效运行机制。部门编号分别为：DEP-001、DEP-002、DEP-003、DEP-004。'),
        (2, '（二）制度建设'),
        (0, '制定完善《章程》《理事会工作规则》《财务管理办法》等8项核心制度，确保规范运营。所有制度符合ISO 9001质量管理体系标准。'),
        (1, '二、业务开展情况'),
        (2, '（一）培训工作'),
        (0, '围绕数字人民币、金融科技等主题，开展专题培训12场，覆盖800余人次。与央行郑州培训学院建立合作，打造"季度讲堂"品牌。平均满意度达4.8/5.0分。'),
        (2, '（二）研究工作'),
        (0, '启动发展指数编制工作，完成数据收集和模型构建。发布应用研究报告，获领导批示肯定。报告编号：RPT-2025-001。'),
        (1, '三、下一步工作计划'),
        (0, '一是加快实体化运营，完成办公场所装修和设备采购；二是启动首批研究课题招标，吸引优质研究团队参与；三是筹备高峰论坛。预计2026年Q1完成全部准备工作。'),
    ]

    output = generate_gongwen(
        title='关于近期工作进展的汇报',
        unit='江苏金服',
        content_sections=test_content,
        output_path='测试公文.docx'
    )
    print(f'公文已生成：{output}')
