#!/usr/bin/env python3
"""
翻译文档导出工具
支持导出为 PDF、Word、HTML 格式
"""

import sys
import os
import re

def validate_html_for_export(html_path):
    """验证HTML文件是否可导出"""
    if not os.path.exists(html_path):
        return False, f"文件不存在: {html_path}"

    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否有中文字符残留
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
    if chinese_chars:
        return False, f"发现中文字符残留: {''.join(chinese_chars[:10])}..."

    return True, "验证通过"

def generate_export_filename(original_name, export_format):
    """生成导出文件名"""
    base_name = os.path.splitext(original_name)[0]
    timestamp = "2026.03.26"
    return f"{base_name}_{timestamp}.{export_format}"

def main():
    if len(sys.argv) < 2:
        print("用法: python export_utils.py <html文件路径> [格式]")
        print("格式选项: pdf, docx, html")
        sys.exit(1)

    html_path = sys.argv[1]
    export_format = sys.argv[2] if len(sys.argv) > 2 else "pdf"

    # 验证文件
    valid, message = validate_html_for_export(html_path)
    print(message)

    if not valid:
        sys.exit(1)

    # 生成输出文件名
    output_name = generate_export_filename(html_path, export_format)
    print(f"导出文件名: {output_name}")

if __name__ == "__main__":
    main()
