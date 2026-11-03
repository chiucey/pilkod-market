#!/usr/bin/env python3
"""
Markdown与Word文档互转脚本
支持: md <-> docx, md <-> doc
"""

import sys
import os
import argparse
from pathlib import Path
import re

def markdown_to_docx(input_path: str, output_path: str) -> bool:
    """Markdown转Word (docx)"""
    try:
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
        from docx.enum.style import WD_STYLE_TYPE

        doc = Document()

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        in_code_block = False
        code_buffer = []

        for line in lines:
            # 代码块处理
            if line.strip().startswith('```'):
                if in_code_block:
                    # 代码块结束，添加到文档
                    for code_line in code_buffer:
                        p = doc.add_paragraph(code_line)
                        p.style = 'No Spacing'
                        run = p.runs[0] if p.runs else p.add_run(code_line)
                        run.font.name = 'Courier New'
                        run.font.size = Pt(10)
                    code_buffer = []
                in_code_block = not in_code_block
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            # 处理标题
            heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                p = doc.add_heading(text, level=level)
                continue

            # 处理列表
            list_match = re.match(r'^[-*+]\s+(.*)', line)
            if list_match:
                p = doc.add_paragraph(list_match.group(1), style='List Bullet')
                continue

            num_list_match = re.match(r'^\d+\.\s+(.*)', line)
            if num_list_match:
                p = doc.add_paragraph(num_list_match.group(1), style='List Number')
                continue

            # 处理引用
            if line.strip().startswith('>'):
                text = line.strip()[1:].strip()
                p = doc.add_paragraph(text)
                p.style = 'Quote'
                continue

            # 处理加粗和斜体
            processed = line
            # 处理 **bold** 和 __bold__
            processed = re.sub(r'\*\*(.+?)\*\*', r'\1', processed)
            processed = re.sub(r'__(.+?)__', r'\1', processed)
            # 处理 *italic* 和 _italic_
            processed = re.sub(r'\*(.+?)\*', r'\1', processed)
            processed = re.sub(r'_(.+?)_', r'\1', processed)
            # 处理行内代码 `code`
            processed = re.sub(r'`(.+?)`', r'\1', processed)

            # 处理链接 [text](url)
            processed = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', processed)

            if processed.strip():
                p = doc.add_paragraph(processed)
                p.paragraph_format.line_spacing = 1.5

        doc.save(output_path)
        return True
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install python-docx")
        return False
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def markdown_to_doc(input_path: str, output_path: str) -> bool:
    """Markdown转旧版Word (doc) - 先转docx再转doc"""
    import subprocess

    # 先转为docx
    temp_docx = os.path.join(os.path.dirname(output_path), '__temp_convert.docx')
    if not markdown_to_docx(input_path, temp_docx):
        return False

    try:
        # 使用LibreOffice转换为doc
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'doc',
             '--outdir', os.path.dirname(output_path), temp_docx],
            capture_output=True,
            text=True,
            timeout=120
        )

        # LibreOffice会生成同名doc文件
        expected_doc = os.path.join(os.path.dirname(output_path), '__temp_convert.doc')
        if os.path.exists(expected_doc):
            os.rename(expected_doc, output_path)
            os.remove(temp_docx)
            return True

        # 如果转换失败，手动复制
        if os.path.exists(temp_docx):
            os.rename(temp_docx, output_path)
            return True

        return False
    except Exception as e:
        print(f"转换失败: {e}")
        # 备份：直接使用docx
        if os.path.exists(temp_docx):
            os.rename(temp_docx, output_path)
        return os.path.exists(output_path)


def docx_to_markdown(input_path: str, output_path: str) -> bool:
    """Word (docx) 转 Markdown"""
    try:
        from docx import Document

        doc = Document(input_path)
        lines = []

        for para in doc.paragraphs:
            text = para.text.strip()

            if not text:
                lines.append('')
                continue

            # 根据样式处理
            style_name = para.style.name.lower()

            if 'heading 1' in style_name or style_name.startswith('heading 1'):
                lines.append(f"# {text}")
            elif 'heading 2' in style_name or style_name.startswith('heading 2'):
                lines.append(f"## {text}")
            elif 'heading 3' in style_name or style_name.startswith('heading 3'):
                lines.append(f"### {text}")
            elif 'heading 4' in style_name or style_name.startswith('heading 4'):
                lines.append(f"#### {text}")
            elif 'heading 5' in style_name or style_name.startswith('heading 5'):
                lines.append(f"##### {text}")
            elif 'heading 6' in style_name or style_name.startswith('heading 6'):
                lines.append(f"###### {text}")
            elif 'list' in style_name and 'bullet' in style_name:
                lines.append(f"- {text}")
            elif 'list' in style_name and 'number' in style_name:
                # 需要跟踪编号，这里简化处理
                lines.append(f"1. {text}")
            elif 'quote' in style_name:
                lines.append(f"> {text}")
            else:
                # 处理富文本格式
                md_text = text
                for run in para.runs:
                    if run.bold:
                        md_text = f"**{md_text}**"
                    if run.italic:
                        md_text = f"*{md_text}*"
                lines.append(md_text)

        # 清理多余的空行
        result = []
        prev_empty = False
        for line in lines:
            curr_empty = (line == '')
            if not (curr_empty and prev_empty):
                result.append(line)
            prev_empty = curr_empty

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result))

        return True
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install python-docx")
        return False
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def doc_to_markdown(input_path: str, output_path: str) -> bool:
    """旧版Word (doc) 转 Markdown - 先转docx再转md"""
    import subprocess

    # 先转为docx
    temp_docx = os.path.join(os.path.dirname(output_path), '__temp_convert.docx')
    try:
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'docx',
             '--outdir', os.path.dirname(output_path), input_path],
            capture_output=True,
            text=True,
            timeout=120
        )

        expected_docx = os.path.join(os.path.dirname(output_path),
                                     os.path.splitext(os.path.basename(input_path))[0] + '.docx')
        if os.path.exists(expected_docx):
            os.rename(expected_docx, temp_docx)

        if not os.path.exists(temp_docx):
            print("doc转docx失败")
            return False

        success = docx_to_markdown(temp_docx, output_path)
        os.remove(temp_docx)
        return success
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def convert_file(input_path: str, output_path: str = None) -> bool:
    """自动检测格式并转换"""
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"文件不存在: {input_path}")
        return False

    # 如果未指定输出路径，自动生成
    if output_path is None:
        stem = input_path.stem
        ext = input_path.suffix.lower()

        # 根据输入格式确定输出格式
        conversions = {
            '.md': ['.docx', '.doc'],
            '.markdown': ['.docx', '.doc'],
            '.docx': ['.md'],
            '.doc': ['.md'],
        }

        if ext in conversions:
            output_path = input_path.parent / f"{stem}_converted{conversions[ext][0]}"
        else:
            print(f"不支持的格式: {ext}")
            return False

    output_path = Path(output_path)

    # 获取扩展名
    in_ext = input_path.suffix.lower()
    out_ext = output_path.suffix.lower()

    print(f"正在转换: {input_path} -> {output_path}")

    # 根据输入输出格式选择转换函数
    if in_ext in ['.md', '.markdown']:
        if out_ext == '.docx':
            return markdown_to_docx(str(input_path), str(output_path))
        elif out_ext == '.doc':
            return markdown_to_doc(str(input_path), str(output_path))
    elif in_ext == '.docx':
        if out_ext in ['.md']:
            return docx_to_markdown(str(input_path), str(output_path))
    elif in_ext == '.doc':
        if out_ext in ['.md']:
            return doc_to_markdown(str(input_path), str(output_path))

    print(f"不支持的转换: {in_ext} -> {out_ext}")
    return False


def main():
    parser = argparse.ArgumentParser(description='Markdown与Word文档互转工具')
    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选，自动生成）')

    args = parser.parse_args()

    success = convert_file(args.input, args.output)

    if success:
        print("转换成功!")
        sys.exit(0)
    else:
        print("转换失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
