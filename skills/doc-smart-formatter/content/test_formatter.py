#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文档格式化功能
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from doc_formatter import DocumentFormatter, format_document

def test_basic_formatting():
    """测试基本格式化功能"""
    print("=" * 50)
    print("测试1: 基本格式化功能")
    print("=" * 50)

    # 创建测试文档
    formatter = DocumentFormatter()

    from docx import Document

    doc = Document()
    # 添加测试内容
    doc.add_paragraph('第一章 绪论')
    doc.add_paragraph('这是绪论部分的正文内容，应该进行首行缩进处理。')
    doc.add_paragraph('1.1 研究背景')
    doc.add_paragraph('研究背景的详细描述内容，包含多个句子。')
    doc.add_paragraph('1.2 研究意义')
    doc.add_paragraph('研究意义的详细描述内容。')
    doc.add_paragraph('1.2.1 理论意义')
    doc.add_paragraph('理论意义的具体内容。')
    doc.add_paragraph('1.2.2 实践意义')
    doc.add_paragraph('实践意义的具体内容。')
    doc.add_paragraph('第二章 相关工作')
    doc.add_paragraph('第二章的正文内容。')

    # 保存测试文档
    test_input = '/tmp/test_input.docx'
    doc.save(test_input)

    # 格式化
    test_output = '/tmp/test_output.docx'
    result = format_document(test_input, test_output)

    print(f"✓ 输入文件: {test_input}")
    print(f"✓ 输出文件: {result}")

    return result


def test_heading_detection():
    """测试标题检测"""
    print("\n" + "=" * 50)
    print("测试2: 标题检测功能")
    print("=" * 50)

    formatter = DocumentFormatter()

    test_cases = [
        ('第一章 绪论', 1, '一级标题 - 第X章格式'),
        ('1.1 研究背景', 2, '二级标题 - X.X格式'),
        ('1.2.1 理论意义', 3, '三级标题 - X.X.X格式'),
        ('第一条 总则', 2, '二级标题 - 第X条格式'),
        ('这是一个普通的段落内容', None, '普通段落'),
        ('（一）研究目标', 2, '二级标题 - （一）格式'),
    ]

    print("\n标题检测测试结果:")
    print("-" * 60)

    for text, expected, description in test_cases:
        detected = formatter.detect_heading_level(text)
        status = "✓" if detected == expected else "✗"
        print(f"{status} {description}")
        print(f"   文本: {text}")
        print(f"   预期: {expected}, 检测: {detected}")
        print()


def test_custom_config():
    """测试自定义配置"""
    print("\n" + "=" * 50)
    print("测试3: 自定义配置功能")
    print("=" * 50)

    custom_config = {
        'body_font': '宋体',
        'body_size': 12,
        'title_font': '黑体',
        'h1_size': 18,
        'h2_size': 16,
        'h3_size': 14,
        'line_spacing': 28,
        'first_line_indent': 2,
    }

    formatter = DocumentFormatter(custom_config)

    print("自定义配置已应用:")
    print(f"  - 正文字号: {formatter.config['body_size']}")
    print(f"  - 一级标题字号: {formatter.config['h1_size']}")
    print(f"  - 行距: {formatter.config['line_spacing']}")
    print(f"  - 首行缩进: {formatter.config['first_line_indent']}字符")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Word文档智能排版技能 - 功能测试")
    print("=" * 60 + "\n")

    test_heading_detection()
    test_custom_config()
    test_basic_formatting()

    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)
