#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word文档智能排版工具
自动识别文档结构并应用专业排版格式
"""

import os
import re
import sys
from typing import List, Tuple, Optional, Dict, Any

try:
    from docx import Document
    from docx.shared import Pt, Cm, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("请先安装 python-docx: pip install python-docx")
    sys.exit(1)


class DocumentFormatter:
    """Word文档智能排版类"""

    # 排版配置
    DEFAULT_CONFIG = {
        'body_font': '宋体',
        'body_size': 12,  # 小四
        'title_font': '黑体',
        'h1_size': 16,  # 三号
        'h2_size': 15,  # 小三
        'h3_size': 14,  # 四号
        'h4_size': 12,  # 小四
        'line_spacing': 24,  # 固定值24磅
        'first_line_indent': 2,  # 首行缩进2字符
        'space_before': 0,
        'space_after': 0,
    }

    # 标题识别模式
    TITLE_PATTERNS = {
        'h1': [
            r'^第[一二三四五六七八九十百千零\d]+[章节篇部卷集]',
            r'^(第一|第二|第三|第四|第五|第六|第七|第八|第九|第十)[章节篇部]',
            r'^(第[一二三四五六七八九十]+部|第[一二三四五六七八九十]+卷)',
            r'^[一二三四五六七八九十]+、',
        ],
        'h2': [
            r'^\d+\.\d+[\s　]',
            r'^(第一|第二|第三|第四|第五|第六|第七|第八|第九|第十)[条款节项]',
            r'^\d+[条款节项][\s　]',
            r'^[（(]\d+[）)]',
            r'^[（(][一二三四五六七八九十][）)]',
            r'^[（(][①②③④⑤⑥⑦⑧⑨⑩][）)]',
        ],
        'h3': [
            r'^\d+\.\d+\.\d+',
            r'^\d+[.．]\d+[\s　]',
            r'^[（(][0-9a-zA-Z]+[）)]\s*\d+',
        ],
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化排版器"""
        self.config = {**self.DEFAULT_CONFIG}
        if config:
            self.config.update(config)

    def set_cell_font(self, cell, font_name: str, font_size: int, bold: bool = False):
        """设置单元格字体"""
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.name = font_name
                run.font.size = Pt(font_size)
                run.font.bold = bold
                run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)

    def set_paragraph_format(self, paragraph, first_line_indent: int = None,
                             line_spacing: float = None, space_before: int = 0,
                             space_after: int = 0):
        """设置段落格式"""
        pf = paragraph.paragraph_format

        if first_line_indent is not None:
            # 首行缩进（单位：字符）
            pf.first_line_indent = Pt(first_line_indent * self._get_char_width())

        if line_spacing is not None:
            pf.line_spacing = Pt(line_spacing)
            pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY

        pf.space_before = Pt(space_before)
        pf.space_after = Pt(space_after)

    def _get_char_width(self) -> float:
        """获取中文字符宽度（磅）"""
        return self.config['body_size'] * 0.5

    def detect_heading_level(self, text: str, font_size: float = None,
                             is_bold: bool = False) -> Optional[int]:
        """检测标题级别

        Args:
            text: 段落文本
            font_size: 当前字号
            is_bold: 是否加粗

        Returns:
            标题级别（1-4），None表示普通段落
        """
        text = text.strip()
        if not text:
            return None

        # 过滤掉过长的段落（不太可能是标题）
        if len(text) > 50:
            return None

        # 检查一级标题模式
        for pattern in self.TITLE_PATTERNS['h1']:
            if re.match(pattern, text):
                return 1

        # 检查二级标题模式
        for pattern in self.TITLE_PATTERNS['h2']:
            if re.match(pattern, text):
                return 2

        # 检查三级标题模式
        for pattern in self.TITLE_PATTERNS['h3']:
            if re.match(pattern, text):
                return 3

        # 基于字号判断（较大的字号可能是标题）
        if font_size and font_size > self.config['body_size']:
            if font_size >= self.config['h1_size']:
                return 1
            elif font_size >= self.config['h2_size']:
                return 2
            elif font_size >= self.config['h3_size']:
                return 3

        # 加粗且较短的文本可能是标题
        if is_bold and len(text) < 30:
            if '第' in text or re.match(r'^\d+', text):
                return 3

        return None

    def format_paragraph(self, paragraph, level: Optional[int] = None):
        """格式化段落"""
        text = paragraph.text.strip()

        if not text:
            return

        # 获取当前段落的字体信息
        runs = paragraph.runs
        current_size = None
        current_bold = False

        if runs:
            first_run = runs[0]
            if first_run.font.size:
                current_size = first_run.font.size.pt
            current_bold = first_run.font.bold or False

        # 检测标题级别
        if level is None:
            level = self.detect_heading_level(text, current_size, current_bold)

        # 应用格式化
        for run in runs:
            if level and level <= 3:
                # 标题格式化
                run.font.bold = True
                run.font.name = self.config['title_font']
                run._element.rPr.rFonts.set(qn('w:eastAsia'), self.config['title_font'])

                if level == 1:
                    run.font.size = Pt(self.config['h1_size'])
                elif level == 2:
                    run.font.size = Pt(self.config['h2_size'])
                elif level == 3:
                    run.font.size = Pt(self.config['h3_size'])
                else:
                    run.font.size = Pt(self.config['h4_size'])

                # 标题居中（一级标题）
                if level == 1:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

                self.set_paragraph_format(paragraph,
                                          line_spacing=self.config['line_spacing'])

            else:
                # 正文格式化
                run.font.name = self.config['body_font']
                run.font.size = Pt(self.config['body_size'])
                run._element.rPr.rFonts.set(qn('w:eastAsia'), self.config['body_font'])

                self.set_paragraph_format(paragraph,
                                          first_line_indent=self.config['first_line_indent'],
                                          line_spacing=self.config['line_spacing'],
                                          space_before=self.config['space_before'],
                                          space_after=self.config['space_after'])

    def format_document(self, doc: Document) -> Document:
        """格式化整个文档"""
        for paragraph in doc.paragraphs:
            self.format_paragraph(paragraph)

        # 格式化表格
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        self.format_paragraph(paragraph)

        return doc

    def format_from_file(self, input_path: str, output_path: str = None) -> str:
        """从文件格式化文档

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径，默认为输入文件名 + '_formatted.docx'

        Returns:
            输出文件路径
        """
        # 确定输出路径
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_formatted.docx"

        # 读取文档
        doc = Document(input_path)

        # 格式化
        doc = self.format_document(doc)

        # 保存
        doc.save(output_path)
        return output_path


def convert_txt_to_docx(txt_path: str, docx_path: str = None) -> Document:
    """将TXT文件转换为Document对象"""
    if docx_path is None:
        base = os.path.splitext(txt_path)[0]
        docx_path = f"{base}.docx"

    doc = Document()
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按段落分割
    paragraphs = content.split('\n')
    for para in paragraphs:
        if para.strip():
            doc.add_paragraph(para.strip())

    return doc, docx_path


def format_document(input_path: str, output_path: str = None,
                    config: Optional[Dict[str, Any]] = None) -> str:
    """格式化文档的主入口函数

    Args:
        input_path: 输入文件路径（.docx, .doc, .txt）
        output_path: 输出文件路径
        config: 排版配置

    Returns:
        输出文件路径
    """
    formatter = DocumentFormatter(config)

    # 根据文件类型处理
    ext = os.path.splitext(input_path)[1].lower()

    if ext == '.txt':
        # TXT文件先转换为docx
        doc, temp_docx = convert_txt_to_docx(input_path)
        # 保存临时docx
        doc.save(temp_docx)
        # 格式化
        result = formatter.format_from_file(temp_docx, output_path)
        # 删除临时文件
        if os.path.exists(temp_docx):
            os.remove(temp_docx)
        return result
    else:
        # Word文档直接格式化
        return formatter.format_from_file(input_path, output_path)


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python doc_formatter.py <输入文件> [输出文件]")
        print("示例: python doc_formatter.py input.docx output.docx")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 - {input_file}")
        sys.exit(1)

    try:
        result = format_document(input_file, output_file)
        print(f"排版完成！输出文件: {result}")
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
