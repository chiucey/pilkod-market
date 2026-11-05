#!/usr/bin/env python3
"""
create_docx.py
俄语写作批改结果 Word 文档生成脚本

用法:
    python create_docx.py --data <json_file> --output <output_path>

JSON 数据结构:
{
    "original_text": "原文内容",
    "corrected_text": "带批注的批改文本（批注格式：[错误: X → Y（说明）]）",
    "scores": {
        "vocabulary": {"score": 25, "max": 30},
        "syntax": {"score": 16, "max": 20},
        "spelling": {"score": 18, "max": 20},
        "content": {"score": 16, "max": 20},
        "register": {"score": 8, "max": 10}
    },
    "total_score": 83,
    "comment": "综合评语文本",
    "non_russian": false
}

非对应语种时 JSON:
{
    "original_text": "原文内容",
    "corrected_text": "",
    "scores": null,
    "total_score": 0,
    "comment": "非对应语种",
    "non_russian": true
}
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("正在安装 python-docx...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "-q"])
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement


# ── 颜色常量 ──────────────────────────────────────────────
COLOR_RED    = RGBColor(0xC0, 0x00, 0x00)   # 错误批注
COLOR_BLUE   = RGBColor(0x1F, 0x49, 0x7D)   # 标题
COLOR_GRAY   = RGBColor(0x59, 0x59, 0x59)   # 分隔线
COLOR_GREEN  = RGBColor(0x37, 0x5A, 0x38)   # 评语标题
COLOR_BLACK  = RGBColor(0x00, 0x00, 0x00)   # 正文


def set_font(run, size_pt=11, bold=False, color=None, font_name="Times New Roman"):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    # 中文字体
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), '宋体')
    rPr.insert(0, rFonts)


def add_section_title(doc, title, color=COLOR_BLUE):
    """添加区块标题段落"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(title)
    set_font(run, size_pt=13, bold=True, color=color)
    return p


def add_divider(doc):
    """添加分隔线段落"""
    p = doc.add_paragraph("─" * 45)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    run = p.runs[0]
    set_font(run, size_pt=9, color=COLOR_GRAY)


def add_plain_paragraph(doc, text, size_pt=11):
    """添加普通正文段落"""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    set_font(run, size_pt=size_pt, color=COLOR_BLACK)
    return p


def add_corrected_paragraph(doc, text):
    """
    解析带批注标记的文本，将 [错误: X → Y（说明）] 片段以红色渲染，
    其余内容以黑色正常渲染。一段文字可能有多处批注。
    """
    # 正则：匹配 [错误: ... ] 块
    pattern = re.compile(r'(\[错误:.*?\])', re.DOTALL)
    parts = pattern.split(text)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)

    for part in parts:
        if not part:
            continue
        if pattern.match(part):
            # 红色批注
            run = p.add_run(part)
            set_font(run, size_pt=11, color=COLOR_RED, bold=False)
        else:
            # 普通文本
            run = p.add_run(part)
            set_font(run, size_pt=11, color=COLOR_BLACK)
    return p


def add_score_table(doc, scores, total_score):
    """添加评分明细表格"""
    labels = {
        "vocabulary": ("词汇使用", 30),
        "syntax":     ("句法结构", 20),
        "spelling":   ("拼写与标点", 20),
        "content":    ("内容与逻辑", 20),
        "register":   ("语体适当性", 10),
    }

    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"

    # 表头
    hdr_cells = table.rows[0].cells
    headers = ["评分维度", "得分", "满分"]
    for i, h in enumerate(headers):
        p = hdr_cells[i].paragraphs[0]
        run = p.add_run(h)
        set_font(run, size_pt=11, bold=True, color=COLOR_BLUE)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 数据行
    for key, (label, max_score) in labels.items():
        row_cells = table.add_row().cells
        score_val = scores[key]["score"] if scores and key in scores else 0
        row_data = [label, str(score_val), str(max_score)]
        for i, val in enumerate(row_data):
            p = row_cells[i].paragraphs[0]
            run = p.add_run(val)
            set_font(run, size_pt=11, color=COLOR_BLACK)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 总分行
    total_row = table.add_row().cells
    total_row[0].merge(total_row[1])
    p_label = total_row[0].paragraphs[0]
    run = p_label.add_run("总  分")
    set_font(run, size_pt=12, bold=True, color=COLOR_BLUE)
    p_label.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_score = total_row[2].paragraphs[0]
    run = p_score.add_run(f"{total_score} / 100")
    set_font(run, size_pt=12, bold=True, color=COLOR_RED if total_score < 60 else COLOR_GREEN)
    p_score.alignment = WD_ALIGN_PARAGRAPH.CENTER


def build_document(data: dict, output_path: str):
    doc = Document()

    # ── 页面设置 ──────────────────────────────────────────
    section = doc.sections[0]
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.5)

    # ── 文档标题 ──────────────────────────────────────────
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("俄语写作批改报告（ТРКИ A2层级）")
    set_font(title_run, size_pt=16, bold=True, color=COLOR_BLUE)
    title_p.paragraph_format.space_after = Pt(10)

    # ── 原文区域 ──────────────────────────────────────────
    add_section_title(doc, "【原文】")
    add_divider(doc)
    for line in data["original_text"].splitlines():
        add_plain_paragraph(doc, line if line.strip() else " ")

    # ── 批改区域 ──────────────────────────────────────────
    add_divider(doc)
    if data.get("non_russian"):
        add_section_title(doc, "【批改结果】", color=COLOR_RED)
        add_divider(doc)
        add_plain_paragraph(doc, "本文非俄语文本，不在批改范围内。")
    else:
        add_section_title(doc, "【批改】")
        add_divider(doc)
        corrected = data.get("corrected_text", "").strip()
        if corrected:
            for line in corrected.splitlines():
                if line.strip():
                    add_corrected_paragraph(doc, line)
                else:
                    doc.add_paragraph()
        else:
            add_plain_paragraph(doc, "【本文未发现语言错误】")

    # ── 评分明细 ──────────────────────────────────────────
    add_divider(doc)
    add_section_title(doc, "【评分明细】")
    doc.add_paragraph()

    if data.get("non_russian"):
        p = doc.add_paragraph()
        run = p.add_run("总分：0 / 100（非对应语种）")
        set_font(run, size_pt=12, bold=True, color=COLOR_RED)
    else:
        add_score_table(doc, data.get("scores"), data.get("total_score", 0))

    # ── 综合评语 ──────────────────────────────────────────
    add_divider(doc)
    add_section_title(doc, "【综合评语】", color=COLOR_GREEN)
    add_divider(doc)
    comment = data.get("comment", "")
    for line in comment.splitlines():
        add_plain_paragraph(doc, line if line.strip() else " ")

    # ── 保存 ──────────────────────────────────────────────
    doc.save(output_path)
    print(f"文档已保存至: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="生成俄语写作批改Word文档")
    parser.add_argument("--data",   required=True, help="JSON数据文件路径")
    parser.add_argument("--output", required=True, help="输出.docx文件路径")
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    build_document(data, args.output)


if __name__ == "__main__":
    main()
