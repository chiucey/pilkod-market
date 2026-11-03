#!/usr/bin/env python3
"""
generate_docx.py — Helper script for the english-history-writing skill.

Usage:
  # Topic generation mode
  python generate_docx.py topic \
    --questions '[{"type":"Term Explanation","type_cn":"名词解释","question":"...","word_count_note":"150-250 words"}]' \
    --output ./history_writing_questions.docx

  # Grading mode
  python generate_docx.py grade \
    --original "..." \
    --annotated "..." \
    --score_table '[{"dimension":"Thesis & Argument","max":25,"score":20}, ...]' \
    --total_score 78 \
    --commentary "中文评语..." \
    --output ./history_essay_graded.docx
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("python-docx not found. Installing...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "-q"])
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement


# ─────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────

def set_cell_bg(cell, hex_color: str):
    """Set a table cell background colour."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def add_horizontal_rule(doc):
    """Insert a thin horizontal line."""
    para = doc.add_paragraph()
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '4')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'AAAAAA')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return para


def set_doc_margins(doc, top=2.0, bottom=2.0, left=2.5, right=2.5):
    """Set document page margins in cm."""
    section = doc.sections[0]
    section.top_margin = Cm(top)
    section.bottom_margin = Cm(bottom)
    section.left_margin = Cm(left)
    section.right_margin = Cm(right)


def style_heading(para, level=1):
    """Apply consistent heading styles."""
    for run in para.runs:
        run.font.bold = True
        if level == 0:
            run.font.size = Pt(16)
            run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
        elif level == 1:
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
        elif level == 2:
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(0x44, 0x72, 0xC4)


# ─────────────────────────────────────────────
# Topic generation
# ─────────────────────────────────────────────

TYPE_COLORS = {
    "Term Explanation": "D6E4F0",
    "Source Analysis": "D5E8D4",
    "Event Commentary": "FFF2CC",
    "Person Evaluation": "F8CECC",
}

DEFAULT_COLOR = "F0F0F0"


def build_topic_doc(questions: list, output_path: str):
    doc = Document()
    set_doc_margins(doc)

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("English History Academic Writing — Practice Questions")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = subtitle.add_run("英语历史学学术写作练习题")
    sub_run.font.size = Pt(12)
    sub_run.font.color.rgb = RGBColor(0x70, 0x70, 0x70)

    add_horizontal_rule(doc)
    doc.add_paragraph()

    for idx, q in enumerate(questions, start=1):
        q_type = q.get("type", "Question")
        q_type_cn = q.get("type_cn", "")
        q_text = q.get("question", "")
        wc_note = q.get("word_count_note", "")

        # Question header
        header_para = doc.add_paragraph()
        bg_color = TYPE_COLORS.get(q_type, DEFAULT_COLOR)
        header_run = header_para.add_run(
            f"Question {idx}  |  {q_type}（{q_type_cn}）"
        )
        header_run.bold = True
        header_run.font.size = Pt(12)
        header_run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

        # Question body
        body_para = doc.add_paragraph()
        body_para.paragraph_format.left_indent = Cm(0.5)
        body_para.paragraph_format.space_before = Pt(4)
        body_para.paragraph_format.space_after = Pt(4)
        body_run = body_para.add_run(q_text)
        body_run.font.size = Pt(11)

        # Word count note
        if wc_note:
            wc_para = doc.add_paragraph()
            wc_para.paragraph_format.left_indent = Cm(0.5)
            wc_run = wc_para.add_run(f"📝 Required length: {wc_note}")
            wc_run.italic = True
            wc_run.font.size = Pt(10)
            wc_run.font.color.rgb = RGBColor(0x70, 0x70, 0x70)

        doc.add_paragraph()  # spacer

    doc.save(output_path)
    print(f"[generate_docx] Topic document saved → {output_path}")


# ─────────────────────────────────────────────
# Grading output
# ─────────────────────────────────────────────

COMMENT_PATTERN = re.compile(r'(\[COMMENT:.*?\])', re.DOTALL)

COMMENT_COLOR = RGBColor(0xCC, 0x00, 0x00)   # red
COMMENT_BG = RGBColor(0xFF, 0xF0, 0xF0)       # light pink (not natively supported in runs)

DIMENSION_HEADER_BG = "2E74B5"  # dark blue
SCORE_ROW_EVEN = "EAF2FB"
SCORE_ROW_ODD  = "FFFFFF"
TOTAL_ROW_BG   = "1F497D"


def add_annotated_paragraph(doc, text: str):
    """Write annotated text: normal parts in black, [COMMENT:...] in red."""
    parts = COMMENT_PATTERN.split(text)
    # Group lines so each original line → one paragraph
    lines = []
    current = []
    for part in parts:
        if '\n' in part and not part.startswith('[COMMENT:'):
            sub = part.split('\n')
            current.append(sub[0])
            lines.append(current)
            for s in sub[1:-1]:
                lines.append([s])
            current = [sub[-1]]
        else:
            current.append(part)
    lines.append(current)

    for line_parts in lines:
        para = doc.add_paragraph()
        para.paragraph_format.space_after = Pt(4)
        for part in line_parts:
            if not part:
                continue
            run = para.add_run(part)
            run.font.size = Pt(11)
            if part.startswith('[COMMENT:'):
                run.font.color.rgb = COMMENT_COLOR
                run.font.size = Pt(9.5)
                run.bold = True


def build_score_table(doc, score_rows: list, total_score: int):
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'

    # Header row
    hdr_cells = table.rows[0].cells
    for i, txt in enumerate(["Dimension", "Max Points", "Score"]):
        hdr_cells[i].text = txt
        set_cell_bg(hdr_cells[i], DIMENSION_HEADER_BG)
        for para in hdr_cells[i].paragraphs:
            for run in para.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.size = Pt(11)

    for idx, row in enumerate(score_rows):
        cells = table.add_row().cells
        cells[0].text = row.get("dimension", "")
        cells[1].text = str(row.get("max", ""))
        cells[2].text = str(row.get("score", ""))
        bg = SCORE_ROW_EVEN if idx % 2 == 0 else SCORE_ROW_ODD
        for cell in cells:
            set_cell_bg(cell, bg.lstrip('#'))
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(11)

    # Total row
    total_cells = table.add_row().cells
    total_cells[0].text = "TOTAL"
    total_cells[1].text = "100"
    total_cells[2].text = str(total_score)
    for cell in total_cells:
        set_cell_bg(cell, TOTAL_ROW_BG.lstrip('#'))
        for para in cell.paragraphs:
            for run in para.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.size = Pt(11)


def build_grade_doc(original: str, annotated: str, score_rows: list,
                    total_score: int, commentary: str, output_path: str):
    doc = Document()
    set_doc_margins(doc)

    # ── Cover title ──────────────────────────────────────
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_run = title_para.add_run("History Essay — Grading Report")
    t_run.bold = True
    t_run.font.size = Pt(16)
    t_run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    score_para = doc.add_paragraph()
    score_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    grade_label = "Distinction" if total_score >= 90 else \
                  "First Class" if total_score >= 80 else \
                  "Upper Second" if total_score >= 70 else \
                  "Lower Second" if total_score >= 60 else \
                  "Third" if total_score >= 50 else "Fail"
    s_run = score_para.add_run(f"Total Score: {total_score} / 100   ({grade_label})")
    s_run.bold = True
    s_run.font.size = Pt(13)
    s_run.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

    add_horizontal_rule(doc)

    # ── Part 1: Original essay ───────────────────────────
    doc.add_page_break()
    h1 = doc.add_heading("Part 1 — Original Essay", level=1)
    style_heading(h1, 1)
    doc.add_paragraph()

    for line in original.split('\n'):
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(4)
        for run in p.runs:
            run.font.size = Pt(11)

    # ── Part 2: Annotated essay ──────────────────────────
    doc.add_page_break()
    h2 = doc.add_heading("Part 2 — Annotated Essay", level=1)
    style_heading(h2, 1)

    note_para = doc.add_paragraph()
    note_run = note_para.add_run(
        "Inline comments follow the format: "
        "[COMMENT: TYPE | original → suggestion | explanation]  "
        "(shown in red)"
    )
    note_run.italic = True
    note_run.font.size = Pt(9.5)
    note_run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
    doc.add_paragraph()

    add_annotated_paragraph(doc, annotated)

    # ── Part 3: Score breakdown ──────────────────────────
    doc.add_page_break()
    h3 = doc.add_heading("Part 3 — Score Breakdown", level=1)
    style_heading(h3, 1)
    doc.add_paragraph()
    build_score_table(doc, score_rows, total_score)

    # ── Part 4: Commentary ───────────────────────────────
    doc.add_page_break()
    h4 = doc.add_heading("Part 4 — Teacher's Commentary（教师评语）", level=1)
    style_heading(h4, 1)
    doc.add_paragraph()

    for line in commentary.split('\n'):
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(4)
        for run in p.runs:
            run.font.size = Pt(11)

    doc.save(output_path)
    print(f"[generate_docx] Grading document saved → {output_path}")


# ─────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate DOCX for english-history-writing skill")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # topic sub-command
    tp = subparsers.add_parser("topic", help="Generate question document")
    tp.add_argument("--questions", required=True, help="JSON array of question objects")
    tp.add_argument("--output", required=True, help="Output .docx path")

    # grade sub-command
    gp = subparsers.add_parser("grade", help="Generate grading document")
    gp.add_argument("--original", required=True, help="Original essay text")
    gp.add_argument("--annotated", required=True, help="Annotated essay text")
    gp.add_argument("--score_table", required=True, help="JSON array of score rows")
    gp.add_argument("--total_score", required=True, type=int, help="Total score out of 100")
    gp.add_argument("--commentary", required=True, help="Chinese commentary (200-300 words)")
    gp.add_argument("--output", required=True, help="Output .docx path")

    args = parser.parse_args()

    if args.mode == "topic":
        questions = json.loads(args.questions)
        build_topic_doc(questions, args.output)

    elif args.mode == "grade":
        score_rows = json.loads(args.score_table)
        build_grade_doc(
            original=args.original,
            annotated=args.annotated,
            score_rows=score_rows,
            total_score=args.total_score,
            commentary=args.commentary,
            output_path=args.output,
        )


if __name__ == "__main__":
    main()
