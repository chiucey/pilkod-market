#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成月度/年度工作总结Word文档"""

import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def set_chinese_font(run, font_name='宋体', font_size=12, bold=False):
    """设置中文字体"""
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)

def add_heading(doc, text, level=1):
    """添加带样式标题

    Args:
        doc: Document对象
        text: 标题文本
        level: 标题级别(1=一级, 2=二级)

    Returns:
        paragraph对象
    """
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.name = '黑体'
        run.font.bold = True
        run.font.size = Pt(16 if level == 1 else 14)
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    return heading

def add_bullet(doc, text, indent_level=0):
    """添加项目符号段落

    Args:
        doc: Document对象
        text: 文本内容
        indent_level: 缩进级别

    Returns:
        paragraph对象
    """
    para = doc.add_paragraph()
    para.style = 'List Bullet'
    run = para.add_run(text)
    run.font.name = '宋体'
    run.font.size = Pt(12)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    if indent_level > 0:
        para.paragraph_format.left_indent = Cm(0.75 * indent_level)
    return para

def create_summary(title_text, sections, output_dir='outputs'):
    """生成工作总结文档

    Args:
        title_text: 文档标题，如"2026年1月份工作总结"
        sections: 字典，key为模块名称(如"一、考勤管理")，value为该模块的工作事项列表
        output_dir: 输出目录，默认为'outputs'

    Returns:
        str: 保存的文件路径
    """
    doc = Document()

    # 设置页面边距
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)

    # 添加文档标题
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run(title_text)
    title_run.font.name = '黑体'
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')

    doc.add_paragraph()  # 空行

    # 添加各模块内容
    for section_name, items in sections.items():
        add_heading(doc, section_name, 1)
        for item in items:
            add_bullet(doc, item)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 生成文件名
    safe_title = title_text.replace(' ', '').replace('年', '').replace('月', '').replace('日', '')
    output_path = f"{output_dir}/工作总结--{title_text}.docx"

    # 保存文档
    doc.save(output_path)
    print(f"[成功] 文档已保存至: {output_path}")
    return output_path

def create_monthly_summary(year, month, sections, output_dir='outputs'):
    """生成月度工作总结的便捷函数

    Args:
        year: 年份，如"2026"
        month: 月份，如"1"
        sections: 工作事项字典
        output_dir: 输出目录

    Returns:
        str: 保存的文件路径
    """
    title_text = f"{year}年{month}月份工作总结"
    return create_summary(title_text, sections, output_dir)

def create_yearly_summary(year, sections, output_dir='outputs'):
    """生成年度工作总结的便捷函数

    Args:
        year: 年份，如"2026"
        sections: 工作事项字典
        output_dir: 输出目录

    Returns:
        str: 保存的文件路径
    """
    title_text = f"{year}年度工作总结"
    return create_summary(title_text, sections, output_dir)

if __name__ == '__main__':
    # 示例用法
    example_sections = {
        '一、考勤管理': [
            '完成全月飞书考勤系统日常审批统计',
            '处理考勤异常问题',
        ],
        '二、行政事务': [
            '办公环境维护',
            '后勤保障',
        ],
    }
    create_monthly_summary('2026', '1', example_sections)