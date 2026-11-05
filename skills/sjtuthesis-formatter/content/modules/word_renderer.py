"""
SJTU Thesis — Word (.docx) Renderer
====================================

Generates a Microsoft Word document strictly following the
SJTU 2022 thesis formatting specification using python-docx.
"""

import re
from pathlib import Path
from typing import Optional

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from docx.shared import Cm, Pt, Emu, RGBColor
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from .thesis_info import ThesisInfo


# ── Constants ──────────────────────────────────────────────────────

# Page margins in cm (SJTU 2022 spec)
MARGIN_TOP_CM = 3.7
MARGIN_BOTTOM_CM = 3.5
MARGIN_LEFT_CM = 2.8
MARGIN_RIGHT_CM = 2.6

# Font size mapping (Chinese hao number → pt)
FONT_SIZE = {
    "一号": Pt(26),    # Title page name
    "三号": Pt(16),    # Chapter heading, Abstract/ToC title
    "四号": Pt(14),    # Section heading
    "小四": Pt(12),    # Body text, subsection heading
    "五号": Pt(10.5),  # References, captions
}

# Line spacing: fixed 20磅 = 400 twips
LINE_SPACING_FIXED_20 = Pt(20)  # Twips = 1/20 of a point

# Colors
COLOR_BLACK = RGBColor(0x00, 0x00, 0x00)

# CJK font names
FONT_CJK_SONG = "宋体"
FONT_CJK_HEI = "黑体"
FONT_CJK_FANGSONG = "仿宋"
FONT_LATIN = "Times New Roman"
FONT_ARIAL = "Arial"

# Paragraph shading for odd/even page headers (subtle)
HEADER_SHADING = "D9E2F3"  # light blue-gray


# ── Style definitions ──────────────────────────────────────────────

def _set_font(run: Run, cn_font: str = FONT_CJK_SONG, en_font: str = FONT_LATIN,
              size: Pt = FONT_SIZE["小四"], bold: bool = False):
    """Set both CJK and Latin fonts on a run."""
    run.font.size = size
    run.font.bold = bold
    run.font.color.rgb = COLOR_BLACK
    run.font.name = en_font
    # Set CJK font via XML
    rpr = run._element.get_or_add_rPr()
    rpr.set(qn("w:rFonts"), f'{nsdecls("w")} w:eastAsia="{cn_font}" w:ascii="{en_font}" w:hAnsi="{en_font}"'.replace(
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" ', ""
    ))
    # Parse and set properly
    rFonts = rpr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="{cn_font}" w:ascii="{en_font}" w:hAnsi="{en_font}"/>')
        rpr.insert(0, rFonts)
    else:
        rFonts.set(qn("w:eastAsia"), cn_font)
        rFonts.set(qn("w:ascii"), en_font)
        rFonts.set(qn("w:hAnsi"), en_font)


def _set_line_spacing(paragraph: Paragraph, spacing_pt: float = 20,
                      line_spacing_rule=WD_LINE_SPACING.EXACTLY):
    """Set fixed line spacing in points (磅)."""
    pf = paragraph.paragraph_format
    pf.line_spacing_rule = line_spacing_rule
    pf.line_spacing = Pt(spacing_pt)


def _set_first_line_indent(paragraph: Paragraph, chars: int = 2):
    """Set first-line indent in number of characters (approx)."""
    # 小四 (12pt) → ~24pt per character → 2 chars = 48pt
    indent_pt = chars * 24
    paragraph.paragraph_format.first_line_indent = Pt(indent_pt)


def _add_paragraph_before(paragraph: Paragraph, text: str,
                          cn_font=FONT_CJK_SONG, en_font=FONT_LATIN,
                          size=FONT_SIZE["小四"], bold=False,
                          alignment=WD_ALIGN_PARAGRAPH.JUSTIFY,
                          first_indent_chars: int = 0,
                          space_before: float = 0,
                          space_after: float = 0,
                          line_spacing: float = 20,
                          keep_with_next: bool = False) -> Paragraph:
    """Add a formatted paragraph at the end of the document body."""
    p = paragraph
    if alignment is not None:
        p.alignment = alignment
    run = p.add_run(text)
    _set_font(run, cn_font, en_font, size, bold)
    _set_line_spacing(p, line_spacing)
    if first_indent_chars > 0:
        _set_first_line_indent(p, first_indent_chars)
    if space_before > 0:
        p.paragraph_format.space_before = Pt(space_before)
    if space_after > 0:
        p.paragraph_format.space_after = Pt(space_after)
    if keep_with_next:
        p.paragraph_format.keep_with_next = True
    return p


# ── Section setup ──────────────────────────────────────────────────

def setup_page(document: Document):
    """Set A4 page size and SJTU margins."""
    section = document.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(MARGIN_TOP_CM)
    section.bottom_margin = Cm(MARGIN_BOTTOM_CM)
    section.left_margin = Cm(MARGIN_LEFT_CM)
    section.right_margin = Cm(MARGIN_RIGHT_CM)
    section.different_first_page_header_footer = True
    section.odd_and_even_pages_header_footer = True


def setup_styles(document: Document):
    """Pre-configure built-in styles for SJTU compliance."""

    # ── Normal style ────────────────────────────────────────────────
    style = document.styles["Normal"]
    style.font.name = FONT_LATIN
    style.font.size = FONT_SIZE["小四"]
    style.font.color.rgb = COLOR_BLACK
    style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT_CJK_SONG)
    pf = style.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = LINE_SPACING_FIXED_20
    pf.first_line_indent = Pt(48)  # ~2 chars
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)

    # ── Heading 1 (章标题: 三号黑体居中) ────────────────────────────
    style = document.styles["Heading 1"]
    style.font.name = FONT_LATIN
    style.font.size = FONT_SIZE["三号"]
    style.font.bold = True
    style.font.color.rgb = COLOR_BLACK
    style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT_CJK_HEI)
    pf = style.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = LINE_SPACING_FIXED_20
    pf.space_before = Pt(24)
    pf.space_after = Pt(18)
    pf.keep_with_next = True
    pf.page_break_before = True

    # ── Heading 2 (节标题: 四号黑体加黑顶左) ────────────────────────
    style = document.styles["Heading 2"]
    style.font.name = FONT_LATIN
    style.font.size = FONT_SIZE["四号"]
    style.font.bold = True
    style.font.color.rgb = COLOR_BLACK
    style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT_CJK_HEI)
    pf = style.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = LINE_SPACING_FIXED_20
    pf.space_before = Pt(12)
    pf.space_after = Pt(6)
    pf.keep_with_next = True

    # ── Heading 3 (子节标题: 小四黑体加黑顶左) ──────────────────────
    style = document.styles["Heading 3"]
    style.font.name = FONT_LATIN
    style.font.size = FONT_SIZE["小四"]
    style.font.bold = True
    style.font.color.rgb = COLOR_BLACK
    style.element.rPr.rFonts.set(qn("w:eastAsia"), FONT_CJK_HEI)
    pf = style.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = LINE_SPACING_FIXED_20
    pf.space_before = Pt(6)
    pf.space_after = Pt(3)
    pf.keep_with_next = True


# ── Header / Footer ────────────────────────────────────────────────

def _setup_header_footer(doc: Document, info: ThesisInfo,
                         first_chapter_name: str = ""):
    """Configure odd/even page headers and footers with page numbers.

    Args:
        doc: Document instance
        info: Thesis metadata
        first_chapter_name: Name of first chapter for odd header
    """
    degree_label = info.get_degree_label()
    odd_text = info.header_odd or first_chapter_name or degree_label
    even_text = info.header_even or degree_label

    for section in doc.sections:
        # ── Odd page header ─────────────────────────────────────────
        header_odd = section.header
        if header_odd.is_linked_to_previous:
            header_odd.is_linked_to_previous = False
        hp = header_odd.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = hp.add_run(odd_text)
        _set_font(run, FONT_CJK_SONG, FONT_LATIN, Pt(9), bold=False)
        # Add underline border below header
        pPr = hp._element.get_or_add_pPr()
        pBdr = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            '  <w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/>'
            '</w:pBdr>'
        )
        pPr.append(pBdr)

        # ── Even page header ────────────────────────────────────────
        header_even = section.even_page_header
        if header_even.is_linked_to_previous:
            header_even.is_linked_to_previous = False
        hp = header_even.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = hp.add_run(even_text)
        _set_font(run, FONT_CJK_SONG, FONT_LATIN, Pt(9), bold=False)
        pPr = hp._element.get_or_add_pPr()
        pBdr = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            '  <w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/>'
            '</w:pBdr>'
        )
        pPr.append(pBdr)

        # ── Footer (page numbers) ───────────────────────────────────
        footer = section.footer
        if footer.is_linked_to_previous:
            footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Insert PAGE field
        run = fp.add_run()
        _set_font(run, FONT_LATIN, FONT_LATIN, Pt(9), bold=False)
        fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        run._element.append(fldChar1)
        run2 = fp.add_run()
        instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
        run2._element.append(instrText)
        run3 = fp.add_run()
        fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run3._element.append(fldChar2)


# ── Content builders ───────────────────────────────────────────────

def render_cover_page(doc: Document, info: ThesisInfo):
    """Render the thesis cover page."""
    body = doc.add_paragraph()
    # Vertical spacing
    for _ in range(6):
        doc.add_paragraph()

    # University name
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("上海交通大学")
    _set_font(run, FONT_CJK_HEI, FONT_LATIN, Pt(26), bold=True)

    # Degree thesis title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"{info.degree_type}学位论文")
    _set_font(run, FONT_CJK_HEI, FONT_LATIN, Pt(22), bold=True)

    doc.add_paragraph()

    # Thesis title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(info.title_cn)
    _set_font(run, FONT_CJK_HEI, FONT_LATIN, Pt(16), bold=True)

    if info.title_en:
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(info.title_en)
        _set_font(run, FONT_LATIN, FONT_LATIN, Pt(14), bold=True)

    # Spacer
    for _ in range(4):
        doc.add_paragraph()

    # Info lines
    info_items = [
        f"学    院：{info.college}",
        f"专    业：{info.major}",
        f"姓    名：{info.author}",
        f"学    号：{info.student_id}",
        f"指导老师：{info.supervisor}",
    ]
    for item in info_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(item)
        _set_font(run, FONT_CJK_SONG, FONT_LATIN, Pt(14), bold=False)

    doc.add_page_break()


def render_abstract(doc: Document, info: ThesisInfo):
    """Render Chinese abstract page."""
    # ── Title ───────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(18)
    run = p.add_run("摘  要")
    _set_font(run, FONT_CJK_HEI, FONT_LATIN, FONT_SIZE["三号"], bold=False)

    # ── Abstract body ───────────────────────────────────────────────
    if info.abstract_cn:
        p = doc.add_paragraph()
        _add_paragraph_before(p, info.abstract_cn,
                              first_indent_chars=2, space_before=0, space_after=0)

    # ── Keywords ────────────────────────────────────────────────────
    if info.keywords_cn:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        _set_line_spacing(p, 20)
        run = p.add_run("关键词：")
        _set_font(run, FONT_CJK_SONG, FONT_LATIN, FONT_SIZE["小四"], bold=True)
        run2 = p.add_run("，".join(info.keywords_cn))
        _set_font(run2, FONT_CJK_SONG, FONT_LATIN, FONT_SIZE["小四"], bold=False)

    doc.add_page_break()


def render_abstract_en(doc: Document, info: ThesisInfo):
    """Render English abstract page."""
    # ── Title ───────────────────────────────────────────────────────
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(18)
    run = p.add_run("ABSTRACT")
    _set_font(run, FONT_ARIAL, FONT_ARIAL, FONT_SIZE["三号"], bold=True)

    # ── Abstract body ───────────────────────────────────────────────
    if info.abstract_en:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        _set_line_spacing(p, 20)
        _set_first_line_indent(p, 2)
        run = p.add_run(info.abstract_en)
        _set_font(run, FONT_LATIN, FONT_LATIN, FONT_SIZE["小四"], bold=False)

    # ── Keywords ────────────────────────────────────────────────────
    if info.keywords_en:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        _set_line_spacing(p, 20)
        run = p.add_run("Key words: ")
        _set_font(run, FONT_LATIN, FONT_LATIN, FONT_SIZE["小四"], bold=True)
        run2 = p.add_run(", ".join(info.keywords_en))
        _set_font(run2, FONT_LATIN, FONT_LATIN, FONT_SIZE["小四"], bold=False)

    doc.add_page_break()


def render_toc_page(doc: Document):
    """Render table of contents page.

    Note: python-docx does not directly insert TOC fields.
    We insert a placeholder and a TOC field code.
    """
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(18)
    run = p.add_run("目  录")
    _set_font(run, FONT_CJK_HEI, FONT_LATIN, FONT_SIZE["三号"], bold=False)

    # Add a hint for the user to update TOC in Word
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("（请在 Word 中右键此处 → 更新域 → 更新整个目录）")
    _set_font(run, FONT_CJK_SONG, FONT_LATIN, Pt(9), bold=False)
    run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    # Insert TOC field
    p = doc.add_paragraph()
    run = p.add_run()
    _set_font(run, FONT_CJK_SONG, FONT_LATIN, FONT_SIZE["四号"], bold=False)

    # TOC field XML
    fld_begin = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    run._element.append(fld_begin)

    run2 = p.add_run()
    instr = (' TOC \\o "1-3" \\h \\z \\u ')
    instr_xml = parse_xml(
        f'<w:instrText {nsdecls("w")} xml:space="preserve">{instr}</w:instrText>'
    )
    run2._element.append(instr_xml)

    run3 = p.add_run()
    fld_separate = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>')
    run3._element.append(fld_separate)

    run4 = p.add_run("（请更新域以生成目录）")
    _set_font(run4, FONT_CJK_SONG, FONT_LATIN, Pt(9), bold=False)
    run4.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

    run5 = p.add_run()
    fld_end = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run5._element.append(fld_end)

    doc.add_page_break()


def render_body(doc: Document, info: ThesisInfo):
    """Render the main body content.

    Parses the user's raw content and applies heading/body formatting.
    """
    content = info.body_content.strip()
    if not content:
        # Placeholder
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("（请在此处粘贴您的论文正文内容）")
        _set_font(run, FONT_CJK_SONG, FONT_LATIN, Pt(12), bold=False)
        run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
        return

    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Detect headings by pattern
        heading_level = _detect_heading_level(line, info.numbering_system)
        if heading_level == 1:
            p = doc.add_paragraph(line, style="Heading 1")
        elif heading_level == 2:
            p = doc.add_paragraph(line, style="Heading 2")
        elif heading_level == 3:
            p = doc.add_paragraph(line, style="Heading 3")
        elif _is_list_item(line):
            p = doc.add_paragraph()
            _add_paragraph_before(p, line, first_indent_chars=2,
                                  space_before=2, space_after=2)
        else:
            p = doc.add_paragraph()
            _add_paragraph_before(p, line, first_indent_chars=2)
        i += 1


def _detect_heading_level(line: str, numbering_system: str) -> int:
    """Detect heading level by pattern matching.

    Returns 0 for body text, 1/2/3 for heading levels.
    """
    if numbering_system == "中文序号":
        # 一、二、三、... → Level 1
        if re.match(r"^[一二三四五六七八九十百千]+[、．]", line):
            return 1
        # （一）（二）... → Level 2
        if re.match(r"^（[一二三四五六七八九十百千]+）", line):
            return 2
        # 1. 2. ... in Chinese context → Level 3
        if re.match(r"^\d+[、．]", line):
            return 3
    else:
        # 阿拉伯数字体系
        # 1. or 第一章 → Level 1
        if re.match(r"^((第[一二三四五六七八九十百千]+章)|(\d+[\.．]))\s", line):
            return 1
        # 1.1 → Level 2
        if re.match(r"^\d+[\.．]\d+\s", line):
            return 2
        # 1.1.1 → Level 3
        if re.match(r"^\d+[\.．]\d+[\.．]\d+\s", line):
            return 3
        # (1) type → Level 4 (body)
        if re.match(r"^\(\d+\)", line):
            return 0

    return 0


def _is_list_item(line: str) -> bool:
    """Detect numbered or bullet list items."""
    return bool(re.match(r"^[\(（]?\d+[\)）]|^[•·\-*]", line))


def render_references(doc: Document, info: ThesisInfo):
    """Render references section."""
    p = doc.add_paragraph("参考文献", style="Heading 1")

    if info.references_raw:
        refs = [r.strip() for r in info.references_raw.split("\n") if r.strip()]
        for ref in refs:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(ref)
            _set_font(run, FONT_CJK_SONG, FONT_LATIN, FONT_SIZE["五号"], bold=False)
    else:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("（请在此处添加您的参考文献）")
        _set_font(run, FONT_CJK_SONG, FONT_LATIN, Pt(10.5), bold=False)
        run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)


def render_acknowledgements(doc: Document, info: ThesisInfo):
    """Render acknowledgements (致谢) page."""
    if not info.include_acknowledgements:
        return

    p = doc.add_paragraph("致  谢", style="Heading 1")
    p = doc.add_paragraph()
    _add_paragraph_before(p, "（请在此处填写致谢内容）", first_indent_chars=2)


def render_appendix(doc: Document, info: ThesisInfo):
    """Render appendix (附录) page."""
    if not info.include_appendix:
        return

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(18)
    run = p.add_run("附  录")
    _set_font(run, FONT_CJK_HEI, FONT_LATIN, FONT_SIZE["三号"], bold=False)

    p = doc.add_paragraph()
    _add_paragraph_before(p, "（请在此处填写附录内容）", first_indent_chars=2)


# ── Main render function ───────────────────────────────────────────

def render_docx(info: ThesisInfo, output_path: Path,
                first_chapter_name: str = "第一章 绪论") -> Path:
    """Generate a complete SJTU thesis Word document.

    Args:
        info: Collected thesis metadata and content.
        output_path: Where to save the .docx file.
        first_chapter_name: Name of first chapter for header.

    Returns:
        Path to the generated .docx file.
    """
    doc = Document()

    # ── Page setup ──────────────────────────────────────────────────
    setup_page(doc)
    setup_styles(doc)

    # ── Cover page ──────────────────────────────────────────────────
    render_cover_page(doc, info)

    # ── Chinese abstract ────────────────────────────────────────────
    render_abstract(doc, info)

    # ── English abstract ────────────────────────────────────────────
    render_abstract_en(doc, info)

    # ── Table of Contents ───────────────────────────────────────────
    if info.include_toc:
        render_toc_page(doc)

    # ── Body ────────────────────────────────────────────────────────
    render_body(doc, info)

    # ── References ──────────────────────────────────────────────────
    render_references(doc, info)

    # ── Acknowledgements ────────────────────────────────────────────
    render_acknowledgements(doc, info)

    # ── Appendix ────────────────────────────────────────────────────
    render_appendix(doc, info)

    # ── Headers and Footers (after all content) ─────────────────────
    _setup_header_footer(doc, info, first_chapter_name)

    # ── Save ────────────────────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    return output_path


def render_word_from_json(json_path: Path, output_path: Path) -> Path:
    """Load ThesisInfo from JSON and render Word document."""
    info = ThesisInfo.load(json_path)
    return render_docx(info, output_path)
