#!/usr/bin/env python3
"""
文档格式转换脚本 - 支持txt/pdf/word互转
支持格式: txt, pdf, docx, doc
"""

import sys
import os
import argparse
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

def txt_to_pdf(input_path: str, output_path: str) -> bool:
    """文本文件转PDF"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import textwrap

        # 尝试注册中文字体
        font_name = "Helvetica"
        try:
            # Linux常见中文字体路径
            font_paths = [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                "/usr/share/fonts/truetype/arphic/uming.ttc",
            ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    font_name = 'ChineseFont'
                    break
        except Exception:
            pass

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        style = ParagraphStyle(
            'CustomStyle',
            fontName=font_name,
            fontSize=11,
            leading=16,
            spaceAfter=6
        )

        story = []
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 按段落分割处理
        paragraphs = content.split('\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                story.append(Spacer(1, 6))
            else:
                # 长段落自动换行
                wrapped = textwrap.fill(para, width=80)
                story.append(Paragraph(wrapped, style))
                story.append(Spacer(1, 3))

        doc.build(story)
        return True
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install reportlab")
        return False
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def txt_to_docx(input_path: str, output_path: str) -> bool:
    """文本文件转Word"""
    try:
        from docx import Document
        from docx.shared import Pt, Inches
        from docx.enum.text import WD_LINE_SPACING

        doc = Document()

        # 设置默认字体
        style = doc.styles['Normal']
        font = style.font
        font.name = 'SimSun'
        font.size = Pt(12)

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        paragraphs = content.split('\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                p = doc.add_paragraph()
            else:
                p = doc.add_paragraph(para)
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


def docx_to_pdf(input_path: str, output_path: str) -> bool:
    """Word转PDF - 使用LibreOffice"""
    import subprocess

    try:
        # 使用LibreOffice转换
        result = subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf',
             '--outdir', os.path.dirname(output_path), input_path],
            capture_output=True,
            text=True,
            timeout=120
        )

        # LibreOffice会生成同名pdf文件
        expected_pdf = os.path.join(os.path.dirname(output_path),
                                    os.path.splitext(os.path.basename(input_path))[0] + '.pdf')

        if os.path.exists(expected_pdf) and expected_pdf != output_path:
            os.rename(expected_pdf, output_path)

        return os.path.exists(output_path)
    except FileNotFoundError:
        print("错误: 未找到LibreOffice，请安装: sudo apt install libreoffice")
        return False
    except subprocess.TimeoutExpired:
        print("转换超时")
        return False
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def docx_to_txt(input_path: str, output_path: str) -> bool:
    """Word转文本"""
    try:
        from docx import Document

        doc = Document(input_path)
        lines = []

        for para in doc.paragraphs:
            lines.append(para.text)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return True
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install python-docx")
        return False
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def pdf_to_txt(input_path: str, output_path: str) -> bool:
    """PDF转文本"""
    try:
        from pypdf import PdfReader

        reader = PdfReader(input_path)
        lines = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                lines.append(text)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(lines))

        return True
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install pypdf")
        return False
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def pdf_to_docx(input_path: str, output_path: str) -> bool:
    """PDF转Word - 提取文本并创建DOCX"""
    try:
        from pypdf import PdfReader
        from docx import Document
        from docx.shared import Pt
        import re

        reader = PdfReader(input_path)
        doc = Document()

        style = doc.styles['Normal']
        font = style.font
        font.name = 'SimSun'
        font.size = Pt(11)

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # 清理文本
                text = re.sub(r'\n\s*\n', '\n\n', text)
                text = text.strip()

                if text:
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            # 保留换行作为新段落
                            for line in para.split('\n'):
                                line = line.strip()
                                if line:
                                    p = doc.add_paragraph(line)

            # 页面之间添加分隔（可选）
            if page_num < len(reader.pages) - 1:
                pass

        doc.save(output_path)
        return True
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install pypdf python-docx")
        return False
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def doc_to_docx(input_path: str, output_path: str) -> bool:
    """旧版Word格式转新版"""
    import subprocess

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

        if os.path.exists(expected_docx) and expected_docx != output_path:
            os.rename(expected_docx, output_path)

        return os.path.exists(output_path)
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
            '.txt': ['.pdf', '.docx'],
            '.pdf': ['.txt', '.docx'],
            '.doc': ['.docx', '.pdf', '.txt'],
            '.docx': ['.pdf', '.txt'],
        }

        if ext in conversions:
            # 默认转为第一个可用格式
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
    if in_ext == '.txt':
        if out_ext == '.pdf':
            return txt_to_pdf(str(input_path), str(output_path))
        elif out_ext in ['.docx', '.doc']:
            return txt_to_docx(str(input_path), str(output_path))
    elif in_ext in ['.docx']:
        if out_ext == '.pdf':
            return docx_to_pdf(str(input_path), str(output_path))
        elif out_ext == '.txt':
            return docx_to_txt(str(input_path), str(output_path))
    elif in_ext == '.doc':
        if out_ext == '.docx':
            return doc_to_docx(str(input_path), str(output_path))
        elif out_ext == '.pdf':
            # 先转docx，再转pdf
            temp_docx = input_path.parent / f"{input_path.stem}_temp.docx"
            if doc_to_docx(str(input_path), str(temp_docx)):
                result = docx_to_pdf(str(temp_docx), str(output_path))
                temp_docx.unlink(missing_ok=True)
                return result
            return False
        elif out_ext == '.txt':
            # 先转docx，再转txt
            temp_docx = input_path.parent / f"{input_path.stem}_temp.docx"
            if doc_to_docx(str(input_path), str(temp_docx)):
                result = docx_to_txt(str(temp_docx), str(output_path))
                temp_docx.unlink(missing_ok=True)
                return result
            return False
    elif in_ext == '.pdf':
        if out_ext == '.txt':
            return pdf_to_txt(str(input_path), str(output_path))
        elif out_ext in ['.docx', '.doc']:
            return pdf_to_docx(str(input_path), str(output_path))

    print(f"不支持的转换: {in_ext} -> {out_ext}")
    return False


def main():
    parser = argparse.ArgumentParser(description='文档格式转换工具')
    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选，自动生成）')

    args = parser.parse_args()

    success = convert_file(args.input, args.output)

    if success:
        print("✓ 转换成功!")
        sys.exit(0)
    else:
        print("✗ 转换失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
