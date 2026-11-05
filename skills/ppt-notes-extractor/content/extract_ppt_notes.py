#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPT演示文稿备注提取器
从PowerPoint演示文稿（PPT/PPTX文件）中提取演讲者备注
"""

import os
import sys
import json
import argparse
from pathlib import Path

try:
    from pptx import Presentation
except ImportError:
    print("正在安装 python-pptx 库...")
    os.system(f"{sys.executable} -m pip install python-pptx -q")
    from pptx import Presentation


def extract_notes_from_pptx(pptx_path, output_format='text'):
    """
    从PPTX文件中提取所有幻灯片的备注

    参数:
        pptx_path: PPTX文件路径
        output_format: 输出格式 ('text', 'markdown', 'json')

    返回:
        格式化后的备注内容列表或字符串
    """
    try:
        prs = Presentation(pptx_path)
    except Exception as e:
        raise FileNotFoundError(f"无法打开文件: {pptx_path}, 错误: {str(e)}")

    notes_data = []

    for index, slide in enumerate(prs.slides, start=1):
        notes_slide = slide.notes_slide
        if notes_slide and notes_slide.notes_text_frame:
            notes_text = notes_slide.notes_text_frame.text.strip()
            notes_data.append({
                'slide_number': index,
                'notes': notes_text if notes_text else "",
                'has_content': bool(notes_text)
            })

    return format_output(notes_data, output_format)


def format_output(notes_data, output_format):
    """根据格式要求格式化输出"""
    # 统计有备注的幻灯片数
    slides_with_notes = sum(1 for item in notes_data if item['has_content'])

    if output_format == 'json':
        return json.dumps({
            'total_slides': len(notes_data),
            'slides_with_notes': slides_with_notes,
            'notes': [item for item in notes_data if item['has_content']]
        }, ensure_ascii=False, indent=2)
    elif output_format == 'markdown':
        return format_as_markdown(notes_data, slides_with_notes)
    else:
        return format_as_text(notes_data, slides_with_notes)


def format_as_text(notes_data, slides_with_notes):
    """格式化为纯文本"""
    lines = []
    lines.append("=" * 50)
    lines.append("       PPT 演示文稿备注提取结果")
    lines.append("=" * 50)
    lines.append(f"总幻灯片数: {len(notes_data)}")
    lines.append(f"有备注的幻灯片: {slides_with_notes}")
    lines.append("=" * 50)
    lines.append("")

    for item in notes_data:
        slide_num = item['slide_number']
        notes = item['notes']
        lines.append(f"【第 {slide_num} 页】")
        if notes:
            lines.append(notes)
        else:
            lines.append("(此页无备注)")
        lines.append("-" * 40)

    return '\n'.join(lines)


def format_as_markdown(notes_data, slides_with_notes):
    """格式化为Markdown"""
    lines = []
    lines.append("# PPT 演示文稿备注")
    lines.append("")
    lines.append(f"**总幻灯片数:** {len(notes_data)}")
    lines.append(f"**有备注的幻灯片:** {slides_with_notes}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for item in notes_data:
        slide_num = item['slide_number']
        notes = item['notes']
        lines.append(f"## 第 {slide_num} 页")
        lines.append("")
        if notes:
            lines.append(notes)
        else:
            lines.append("*（此页无备注）*")
        lines.append("")

    return '\n'.join(lines)


def save_output(content, output_path):
    """保存输出到文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return output_path


def process_file(pptx_path, output_format='text', output_path=None):
    """处理单个文件"""
    if not os.path.exists(pptx_path):
        return {"success": False, "error": f"文件不存在: {pptx_path}"}

    try:
        notes = extract_notes_from_pptx(pptx_path, output_format)

        if output_path:
            saved_path = save_output(notes, output_path)
            return {
                "success": True,
                "message": f"备注已保存到: {saved_path}",
                "content": notes
            }
        else:
            return {
                "success": True,
                "content": notes
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description='从PPT演示文稿中提取演讲者备注',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python extract_ppt_notes.py presentation.pptx
  python extract_ppt_notes.py presentation.pptx -f markdown
  python extract_ppt_notes.py presentation.pptx -o notes.md -f markdown
  python extract_ppt_notes.py presentation.pptx --format json
        """
    )

    parser.add_argument('pptx_file', help='PPTX文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选）')
    parser.add_argument('-f', '--format', choices=['text', 'markdown', 'json'],
                        default='text', help='输出格式 (默认: text)')

    args = parser.parse_args()

    result = process_file(args.pptx_file, args.format, args.output)

    if result['success']:
        print(result['content'])
        if args.output:
            print(f"\n✓ 已保存到: {args.output}")
    else:
        print(f"✗ 错误: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
