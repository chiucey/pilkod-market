#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML to PPT Converter for Educational Content

将HTML文件转换为PowerPoint演示文稿，支持教学内容的结构化转换。
保留文档结构、格式、表格和图片，优化教育场景使用。

依赖库:
    pip install python-pptx beautifulsoup4 lxml

使用方法:
    python html_to_ppt.py --input example.html --output presentation.pptx
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from html.parser import HTMLParser

# 尝试导入依赖库，不存在时提供友好的错误提示
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("错误: 需要安装 beautifulsoup4 库")
    print("请运行: pip install beautifulsoup4")
    sys.exit(1)

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("错误: 需要安装 python-pptx 库")
    print("请运行: pip install python-pptx")
    sys.exit(1)


# ============================================================================
# 教学PPT主题配置
# ============================================================================

EDUCATION_THEMES = {
    "default": {
        "title_bg": RGBColor(0x00, 0x70, 0xC0),      # 蓝色标题背景
        "title_text": RGBColor(255, 255, 255),       # 白色标题文字
        "content_bg": RGBColor(255, 255, 255),       # 白色内容背景
        "content_text": RGBColor(51, 51, 51),       # 深灰正文
        "accent": RGBColor(0xFF, 0x66, 0x00),        # 橙色强调
        "header_bg": RGBColor(0xF5, 0xF5, 0xF5),    # 浅灰头部
        "font_title": "微软雅黑",
        "font_content": "微软雅黑",
    },
    "academic": {
        "title_bg": RGBColor(0x1A, 0x3C, 0x6E),      # 深蓝色标题
        "title_text": RGBColor(255, 255, 255),
        "content_bg": RGBColor(252, 252, 252),
        "content_text": RGBColor(33, 33, 33),
        "accent": RGBColor(0x00, 0x96, 0x88),        # 青绿色强调
        "header_bg": RGBColor(240, 240, 240),
        "font_title": "微软雅黑",
        "font_content": "宋体",
    },
    "modern": {
        "title_bg": RGBColor(0x6C, 0x5C, 0xEB),      # 紫色标题
        "title_text": RGBColor(255, 255, 255),
        "content_bg": RGBColor(255, 255, 255),
        "content_text": RGBColor(50, 50, 50),
        "accent": RGBColor(0xFF, 0x61, 0x75),        # 粉色强调
        "header_bg": RGBColor(245, 245, 245),
        "font_title": "微软雅黑",
        "font_content": "微软雅黑",
    },
    "nature": {
        "title_bg": RGBColor(0x22, 0x8B, 0x22),      # 绿色标题
        "title_text": RGBColor(255, 255, 255),
        "content_bg": RGBColor(255, 255, 255),
        "content_text": RGBColor(34, 34, 34),
        "accent": RGBColor(0xFF, 0xA5, 0x00),        # 橙色强调
        "header_bg": RGBColor(245, 250, 245),
        "font_title": "微软雅黑",
        "font_content": "微软雅黑",
    }
}


# ============================================================================
# 辅助类和函数
# ============================================================================

class HTMLContentExtractor(HTMLParser):
    """HTML内容提取器，解析HTML并提取结构化内容"""

    def __init__(self):
        super().__init__()
        self.content_stack = []  # 内容栈
        self.current_path = []   # 当前路径
        self.result = {
            "title": "",
            "slides": [],
            "metadata": {}
        }
        self.current_slide = None
        self.current_element = None
        self.list_items = []
        self.in_list = False
        self.table_data = []
        self.in_table = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # 标题标签，开始新幻灯片
            level = int(tag[1])
            self.current_slide = {
                "type": "slide",
                "title": "",
                "level": level,
                "content": [],
                "raw_content": ""
            }
            self.current_element = "title"

        elif tag == 'p':
            self.current_element = "paragraph"
            self.current_path.append("p")

        elif tag in ['ul', 'ol']:
            self.in_list = True
            self.list_items = []
            self.current_path.append(tag)

        elif tag == 'li':
            self.current_element = "list_item"
            self.list_items.append("")

        elif tag == 'table':
            self.in_table = True
            self.table_data = []
            self.current_path.append("table")

        elif tag == 'tr':
            self.table_data.append([])

        elif tag in ['td', 'th']:
            self.current_element = "table_cell"

        elif tag == 'img':
            # 图片处理
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            if self.current_slide is None:
                self.current_slide = {
                    "type": "slide",
                    "title": "",
                    "level": 2,
                    "content": [],
                    "raw_content": ""
                }
            self.current_slide["content"].append({
                "type": "image",
                "src": src,
                "alt": alt
            })

        elif tag == 'br':
            pass  # 忽略换行

    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if self.current_slide:
                # 提取标题内容
                self.result["slides"].append(self.current_slide)
            self.current_slide = None
            self.current_element = None

        elif tag == 'p':
            if self.current_slide and self.current_element == "paragraph":
                self.current_element = None
            if self.current_path and self.current_path[-1] == 'p':
                self.current_path.pop()

        elif tag in ['ul', 'ol']:
            if self.in_list and self.current_slide:
                self.current_slide["content"].append({
                    "type": "list",
                    "list_type": tag,
                    "items": self.list_items.copy()
                })
            self.in_list = False
            self.list_items = []
            if self.current_path and self.current_path[-1] in ['ul', 'ol']:
                self.current_path.pop()

        elif tag == 'li':
            self.current_element = None

        elif tag == 'table':
            if self.current_slide and self.table_data:
                self.current_slide["content"].append({
                    "type": "table",
                    "data": self.table_data.copy()
                })
            self.in_table = False
            self.table_data = []
            if self.current_path and self.current_path[-1] == 'table':
                self.current_path.pop()

        elif tag == 'tr':
            pass

        elif tag in ['td', 'th']:
            self.current_element = None

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return

        if self.current_element == "title":
            if self.current_slide:
                self.current_slide["title"] = text
            elif not self.result["title"]:
                self.result["title"] = text

        elif self.current_element == "paragraph":
            if self.current_slide:
                self.current_slide["content"].append({
                    "type": "paragraph",
                    "text": text
                })

        elif self.current_element == "list_item":
            if self.list_items:
                self.list_items[-1] = text

        elif self.current_element == "table_cell":
            if self.table_data:
                self.table_data[-1].append(text)


def extract_html_content(html_content: str) -> Dict:
    """
    提取HTML内容为结构化数据

    Args:
        html_content: HTML字符串

    Returns:
        包含标题、幻灯片内容的字典
    """
    extractor = HTMLContentExtractor()
    extractor.feed(html_content)
    return extractor.result


def create_presentation(theme: Dict) -> Presentation:
    """
    创建演示文稿实例，应用主题配置

    Args:
        theme: 主题配置字典

    Returns:
        配置好的Presentation对象
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 比例
    prs.slide_height = Inches(7.5)
    return prs


def add_title_slide(prs: Presentation, title: str, subtitle: str = "", theme: Dict = None):
    """
    添加标题幻灯片

    Args:
        prs: 演示文稿对象
        title: 标题文字
        subtitle: 副标题文字
        theme: 主题配置
    """
    if theme is None:
        theme = EDUCATION_THEMES["default"]

    # 使用空白布局
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)

    # 添加标题背景矩形
    left = Inches(0)
    top = Inches(2.5)
    width = prs.slide_width
    height = Inches(2.5)

    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = theme["title_bg"]
    shape.line.fill.background()

    # 添加标题文本框
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(2.8), Inches(12.333), Inches(1.2)
    )
    title_frame = title_box.text_frame
    title_frame.paragraphs[0].text = title
    title_frame.paragraphs[0].font.size = Pt(44)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = theme["title_text"]
    title_frame.paragraphs[0].font.name = theme["font_title"]
    title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # 添加副标题
    if subtitle:
        subtitle_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(4.2), Inches(12.333), Inches(0.8)
        )
        subtitle_frame = subtitle_box.text_frame
        subtitle_frame.paragraphs[0].text = subtitle
        subtitle_frame.paragraphs[0].font.size = Pt(24)
        subtitle_frame.paragraphs[0].font.color.rgb = theme["title_text"]
        subtitle_frame.paragraphs[0].font.name = theme["font_content"]
        subtitle_frame.paragraphs[0].alignment = PP_ALIGN.CENTER


def add_content_slide(prs: Presentation, title: str, content: List[Dict], theme: Dict = None):
    """
    添加内容幻灯片

    Args:
        prs: 演示文稿对象
        title: 幻灯片标题
        content: 内容列表
        theme: 主题配置
    """
    if theme is None:
        theme = EDUCATION_THEMES["default"]

    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)

    # 添加标题栏背景
    header_height = Inches(1.2)
    header_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0), prs.slide_width, header_height
    )
    header_shape.fill.solid()
    header_shape.fill.fore_color.rgb = theme["title_bg"]
    header_shape.line.fill.background()

    # 添加标题文本
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.25), Inches(12.333), Inches(0.7)
    )
    title_frame = title_box.text_frame
    title_frame.paragraphs[0].text = title
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = theme["title_text"]
    title_frame.paragraphs[0].font.name = theme["font_title"]

    # 添加内容区域
    content_top = Inches(1.5)
    content_height = Inches(5.5)

    y_offset = content_top
    for item in content:
        if item["type"] == "paragraph":
            para_box = slide.shapes.add_textbox(
                Inches(0.7), y_offset, Inches(11.9), Inches(0.5)
            )
            para_frame = para_box.text_frame
            para_frame.paragraphs[0].text = item["text"]
            para_frame.paragraphs[0].font.size = Pt(18)
            para_frame.paragraphs[0].font.color.rgb = theme["content_text"]
            para_frame.paragraphs[0].font.name = theme["font_content"]
            y_offset += Inches(0.5)

        elif item["type"] == "list":
            list_box = slide.shapes.add_textbox(
                Inches(0.7), y_offset, Inches(11.9), Inches(len(item["items"]) * 0.4)
            )
            list_frame = list_box.text_frame
            list_frame.word_wrap = True

            for i, list_item in enumerate(item["items"]):
                if i == 0:
                    p = list_frame.paragraphs[0]
                else:
                    p = list_frame.add_paragraph()
                p.text = f"• {list_item}"
                p.font.size = Pt(18)
                p.font.color.rgb = theme["content_text"]
                p.font.name = theme["font_content"]
                p.space_after = Pt(8)

            y_offset += Inches(len(item["items"]) * 0.4)

        elif item["type"] == "table":
            rows = len(item["data"])
            cols = max(len(row) for row in item["data"]) if item["data"] else 0

            if rows > 0 and cols > 0:
                table = slide.shapes.add_table(
                    rows, cols,
                    Inches(0.7), y_offset,
                    Inches(11.9), Inches(rows * 0.4)
                ).table

                for r_idx, row in enumerate(item["data"]):
                    for c_idx, cell_text in enumerate(row):
                        cell = table.cell(r_idx, c_idx)
                        cell.text = cell_text
                        cell.text_frame.paragraphs[0].font.size = Pt(14)
                        cell.text_frame.paragraphs[0].font.color.rgb = theme["content_text"]
                        cell.text_frame.paragraphs[0].font.name = theme["font_content"]

                        if r_idx == 0:
                            cell.fill.solid()
                            cell.fill.fore_color.rgb = theme["header_bg"]
                            cell.text_frame.paragraphs[0].font.bold = True

                y_offset += Inches(rows * 0.4 + 0.2)

        elif item["type"] == "image":
            # 图片处理（需要图片可访问）
            pass


def add_ending_slide(prs: Presentation, text: str = "谢谢观看", theme: Dict = None):
    """
    添加结束幻灯片

    Args:
        prs: 演示文稿对象
        text: 结束语文字
        theme: 主题配置
    """
    if theme is None:
        theme = EDUCATION_THEMES["default"]

    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)

    # 添加背景
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0), prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = theme["title_bg"]
    bg_shape.line.fill.background()

    # 添加结束语
    text_box = slide.shapes.add_textbox(
        Inches(0), Inches(3), prs.slide_width, Inches(1.5)
    )
    text_frame = text_box.text_frame
    text_frame.paragraphs[0].text = text
    text_frame.paragraphs[0].font.size = Pt(48)
    text_frame.paragraphs[0].font.bold = True
    text_frame.paragraphs[0].font.color.rgb = theme["title_text"]
    text_frame.paragraphs[0].font.name = theme["font_title"]
    text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER


def html_to_pptx(input_path: str, output_path: str, theme_name: str = "default") -> bool:
    """
    将HTML文件转换为PPTX演示文稿

    Args:
        input_path: 输入HTML文件路径
        output_path: 输出PPTX文件路径
        theme_name: 主题名称

    Returns:
        转换是否成功
    """
    try:
        # 读取HTML文件
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 提取内容
        content_data = extract_html_content(html_content)

        # 获取主题配置
        theme = EDUCATION_THEMES.get(theme_name, EDUCATION_THEMES["default"])

        # 创建演示文稿
        prs = create_presentation(theme)

        # 添加标题幻灯片
        add_title_slide(
            prs,
            content_data.get("title", "演示文稿"),
            "教育课件",
            theme
        )

        # 添加内容幻灯片
        for slide_data in content_data.get("slides", []):
            title = slide_data.get("title", "")
            content = slide_data.get("content", [])

            if title or content:
                add_content_slide(prs, title, content, theme)

        # 添加结束幻灯片
        add_ending_slide(prs, "谢谢观看", theme)

        # 保存演示文稿
        prs.save(output_path)
        print(f"✓ 转换成功: {output_path}")
        return True

    except Exception as e:
        print(f"✗ 转换失败: {str(e)}")
        return False


# ============================================================================
# 主程序入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="将HTML文件转换为PowerPoint演示文稿（支持教学内容）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --input example.html --output presentation.pptx
  %(prog)s --input course.html --output course.pptx --theme academic
  %(prog)s --input notes.html --output notes.pptx --theme modern

可用主题:
  default  - 默认蓝色主题（通用）
  academic - 学术蓝色主题（论文、课程）
  modern   - 现代紫色主题（创意、展示）
  nature   - 自然绿色主题（自然科学）
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入HTML文件路径"
    )

    parser.add_argument(
        "--output", "-o",
        required=True,
        help="输出PPTX文件路径"
    )

    parser.add_argument(
        "--theme", "-t",
        default="default",
        choices=list(EDUCATION_THEMES.keys()),
        help="选择演示文稿主题 (默认: default)"
    )

    args = parser.parse_args()

    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)

    # 执行转换
    success = html_to_pptx(args.input, args.output, args.theme)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
