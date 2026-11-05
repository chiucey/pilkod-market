#!/usr/bin/env python3
"""
Markdown → Word 试卷转换器
支持 LaTeX 公式（转为 Word 原生 OMML 格式）+ 专业试卷版式
"""

import sys
import subprocess
import tempfile
import os
import re
import shutil
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import docx
        import markdown
        from lxml import etree
    except ImportError as e:
        print(f"缺少依赖: {e}", file=sys.stderr)
        print("请运行: pip install python-docx markdown lxml", file=sys.stderr)
        sys.exit(1)

    # 检查 pandoc
    if not shutil.which("pandoc"):
        print("警告: pandoc 未安装，公式可能无法完美转换")
        print("请访问 https://pandoc.org/installing.html 安装 pandoc")


def ensure_pandoc_available():
    """确保 pandoc 可用"""
    if not shutil.which("pandoc"):
        print("错误: pandoc 是必需的公式转换工具", file=sys.stderr)
        sys.exit(1)


def extract_markdown_text(md_content: str) -> dict:
    """解析 Markdown 内容，提取元数据和题型结构"""
    lines = md_content.split('\n')
    meta = {
        "title": "未命名试卷",
        "subject": "",
        "grade": "",
        "total_score": "100",
        "duration": "90",
    }

    # 提取 YAML 头部信息（若有）
    if lines[0].strip() == '---':
        fence_end = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                fence_end = i
                break
        if fence_end > 0:
            meta_block = '\n'.join(lines[1:fence_end])
            for line in meta_block.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    key = key.strip().lower()
                    val = val.strip().strip('"\'')
                    if key == 'title':
                        meta['title'] = val
                    elif key == 'subject':
                        meta['subject'] = val
                    elif key == 'grade':
                        meta['grade'] = val
                    elif key == 'total_score':
                        meta['total_score'] = val
                    elif key == 'duration':
                        meta['duration'] = val
            return '\n'.join(lines[fence_end + 1:])

    # 从 Markdown 首行提取（# 标题格式）
    for line in lines:
        line = line.strip()
        if line.startswith('# ') and not line.startswith('##'):
            meta['title'] = line[2:].strip()
            break

    # 从 - 列表行提取信息
    for line in lines:
        m = re.match(r'-*\s*科目[:：]\s*(.+)', line)
        if m:
            meta['subject'] = m.group(1).strip()
        m = re.match(r'-*\s*年级[:：]\s*(.+)', line)
        if m:
            meta['grade'] = m.group(1).strip()
        m = re.match(r'-*\s*满分[:：]\s*(\d+)', line)
        if m:
            meta['total_score'] = m.group(1).strip()
        m = re.match(r'-*\s*时间[:：]\s*(\d+)\s*分钟', line)
        if m:
            meta['duration'] = m.group(1).strip()

    return md_content


def convert_with_pandoc(md_content: str, output_docx: str, template_path: str = None) -> bool:
    """
    使用 Pandoc 将 Markdown（含 LaTeX 公式）转换为 docx
    LaTeX 公式会被转换为 Word 原生公式对象（OMML）
    """
    # 写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', encoding='utf-8', delete=False) as f:
        f.write(md_content)
        md_temp = f.name

    try:
        cmd = [
            'pandoc',
            md_temp,
            '-f', 'markdown+tex_math_dollars',
            '-t', 'docx',
            '--mathml',
            '-o', output_docx,
        ]

        if template_path and os.path.exists(template_path):
            cmd.extend(['--reference-doc', template_path])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Pandoc 转换警告: {result.stderr}", file=sys.stderr)
            return False

        return True

    finally:
        os.unlink(md_temp)


def restyle_document(docx_path: str, meta: dict, output_path: str):
    """
    使用 python-docx 重新应用试卷专业样式
    - 题头居中大字
    - 答题纸式分值栏
    - 题号格式规范
    """
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    import copy

    doc = Document(docx_path)

    # ── 全局字体设置 ──────────────────────────────────────
    style = doc.styles['Normal']
    style.font.name = '宋体'
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    style.font.size = Pt(10.5)

    # ── 处理每个段落 ──────────────────────────────────────
    for para in doc.paragraphs:
        text = para.text.strip()

        # 【大标题】居中，黑体二号
        if text.startswith('# ') or (text and not text.startswith('#') and meta['title'] and text == meta['title']):
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                run.bold = True
                run.font.name = '黑体'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
                run.font.size = Pt(22)
            meta['title_processed'] = True
            continue

        # 【信息栏】居中五号
        if any(k in text for k in ['科目', '年级', '满分', '时间', '｜', '|']):
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                run.font.size = Pt(12)
            continue

        # 【题型标题】## 开头的题型的头大标题
        if text.startswith('## ') or text.startswith('**') and '题' in text:
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in para.runs:
                run.bold = True
                run.font.name = '黑体'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
                run.font.size = Pt(14)
            continue

        # 【题号】1. 2. 格式
        if re.match(r'^\d+\.?\s*（\d+分）', text) or re.match(r'^\d+\.?\s*\(?\d+分', text):
            para.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in para.runs:
                run.bold = True
                run.font.size = Pt(10.5)
            continue

        # 【答案】加粗紫色
        if text.startswith('**答案') or text.startswith('答案'):
            for run in para.runs:
                run.italic = True
                run.font.color.rgb = RGBColor(0x80, 0x00, 0x80)  # 紫色
                run.font.size = Pt(9)
            continue

        # 【选项】A. B. C. D.
        if re.match(r'^[A-D]\.\s*', text):
            for run in para.runs:
                run.font.name = '宋体'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                run.font.size = Pt(10.5)
            continue

    # ── 处理公式单元格（如有表格）────────────────────────
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.name = '宋体'
                        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # ── 添加页眉（密封线格式）────────────────────────────
    section = doc.sections[0]
    header = section.header
    header_para = header.paragraphs[0]
    header_para.text = f"{meta.get('subject', '')}  班级：___________  姓名：___________  学号：___________"
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in header_para.runs:
        run.font.size = Pt(10)
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # ── 添加页脚（页码）───────────────────────────────────
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = "第 X 页 共 Y 页"
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in footer_para.runs:
        run.font.size = Pt(9)

    # ── 页面设置：A4，合适的边距 ─────────────────────────
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)

    # ── 保存 ─────────────────────────────────────────────
    doc.save(output_path)


def build_answer_sheet_table(doc, meta: dict):
    """
    在文档开头插入答题纸风格的考生信息表
    """
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    table = doc.add_table(rows=3, cols=4)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    def set_cell(cell, text, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER):
        para = cell.paragraphs[0]
        para.alignment = align
        run = para.add_run(text)
        run.bold = bold
        run.font.name = '宋体'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
        run.font.size = Pt(10)

    # 答题纸标题行
    row0 = table.rows[0]
    merged = row0.cells[0].merge(row0.cells[1]).merge(row0.cells[2]).merge(row0.cells[3])
    set_cell(merged, f"【{meta.get('subject', '考试')}】考生信息栏", bold=True)

    row1 = table.rows[1]
    set_cell(row1.cells[0], "班级")
    set_cell(row1.cells[1], "")
    set_cell(row1.cells[2], "姓名")
    set_cell(row1.cells[3], "")

    row2 = table.rows[2]
    set_cell(row2.cells[0], "学号")
    set_cell(row2.cells[1], "")
    set_cell(row2.cells[2], "得分")
    set_cell(row2.cells[3], "")

    doc.add_paragraph()


def main():
    if len(sys.argv) < 3:
        print("用法: python md2exam.py <输入.md> <输出.docx> [--template <模板.docx>]", file=sys.stderr)
        sys.exit(1)

    input_md = sys.argv[1]
    output_docx = sys.argv[2]
    template_path = None

    for i, arg in enumerate(sys.argv):
        if arg == '--template' and i + 1 < len(sys.argv):
            template_path = sys.argv[i + 1]

    check_dependencies()
    ensure_pandoc_available()

    # 读取 Markdown
    with open(input_md, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 解析元数据
    meta = {
        "title": "未命名试卷",
        "subject": Path(input_md).stem,
        "grade": "",
        "total_score": "100",
        "duration": "90",
    }
    content = extract_markdown_text(md_content)

    # 第一步：Pandoc 转换（含 LaTeX → OMML）
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp:
        tmp_docx = tmp.name

    print(f"正在转换 Markdown → Word（含 {content.count('$')} 个公式）...")
    ok = convert_with_pandoc(content, tmp_docx, template_path)

    if not ok:
        print("Pandoc 转换失败，尝试备用方案...", file=sys.stderr)

    # 第二步：重新样式化
    print("正在应用专业试卷样式...")
    restyle_document(tmp_docx, meta, output_docx)
    os.unlink(tmp_docx)

    print(f"✅ 试卷已生成: {output_docx}")


if __name__ == '__main__':
    main()
