#!/usr/bin/env python3
"""
生成专业标准的政府采购投标文件DOCX
符合《政府采购货物和服务招标投标管理办法》格式要求
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsmap
from docx.oxml import OxmlElement
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import os
import re
import argparse
import json
import hashlib
import urllib.parse
import urllib.request
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

WEB_IMAGE_SEARCH_API_URL = os.getenv("WEB_IMAGE_SEARCH_API_URL", "https://metaso.cn/api/v1/search")
WEB_IMAGE_SEARCH_API_KEY = os.getenv("WEB_IMAGE_SEARCH_API_KEY", "mk-2F504DF474BE9B9BB0692A9649DC6179")
IMAGE_PLACEHOLDER_PATTERN = re.compile(r"\[insert_image_start\](.*?)\[insert_image_end\]")
CAPTION_PATTERN = re.compile(r"^(图|表)\s*\d+-\d+")
# Markdown 加粗：**片段** 内不可换行；未配对的 ** 保留在原文中
MARKDOWN_BOLD_PATTERN = re.compile(r"\*\*(.+?)\*\*")
REF_TOKEN_PATTERN = re.compile(r"(图\d+-\d+|表\d+-\d+|第[一二三四五六七八九十百千万0-9]+章)")

# 颜色配置 - 政府标准蓝色
GOV_BLUE = RGBColor(0x00, 0x32, 0x66)      # 政府采购蓝
DARK_BLUE = RGBColor(0x00, 0x50, 0x8C)     # 深蓝
ACCENT_BLUE = RGBColor(0x00, 0x70, 0xC0)   # 强调蓝
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)    # 浅灰背景
TABLE_HEADER_BG = RGBColor(0x00, 0x32, 0x66)  # 表头深蓝
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


def add_external_hyperlink(paragraph, text, url):
    """向段落追加外部可点击超链接。"""
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)

    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    r_style = OxmlElement("w:rStyle")
    r_style.set(qn("w:val"), "Hyperlink")
    r_pr.append(r_style)
    run.append(r_pr)

    text_node = OxmlElement("w:t")
    text_node.text = text
    run.append(text_node)

    hyperlink.append(run)
    paragraph._p.append(hyperlink)

def set_cell_background(cell, hex_color):
    """设置单元格背景色"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=0, bottom=0, left=0.1, right=0.1):
    """设置单元格边距（厘米）"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for edge, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{edge}')
        node.set(qn('w:w'), str(int(val * 567)))  # 厘米转twips
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_page_number_field(paragraph):
    """添加页码域"""
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar1)

    instrText = OxmlElement('w:instrText')
    instrText.text = ' PAGE '
    run2 = paragraph.add_run()
    run2._r.append(instrText)

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run2._r.append(fldChar2)

def add_total_pages_field(paragraph):
    """添加总页数域"""
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar1)

    instrText = OxmlElement('w:instrText')
    instrText.text = ' NUMPAGES '
    run2 = paragraph.add_run()
    run2._r.append(instrText)

    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run2._r.append(fldChar2)

def add_bookmark_around_run(paragraph, run, bookmark_name, bookmark_id):
    """在指定 run 周围插入书签，供 REF 域交叉引用。"""
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), bookmark_name)

    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))

    run._r.addprevious(start)
    run._r.addnext(end)

def _apply_run_font(run, font_name, font_size_pt, east_asia=True, rgb_color=None, is_bold=False):
    run.font.size = Pt(font_size_pt)
    run.font.name = font_name
    if east_asia:
        run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    if rgb_color is not None:
        run.font.color.rgb = rgb_color
    if is_bold:
        run.bold = True

def add_ref_field(
    paragraph,
    bookmark_name,
    display_text,
    font_name,
    font_size_pt,
    east_asia=True,
    rgb_color=None,
    is_bold=False,
):
    """插入 REF 交叉引用域（显示目标书签文本，支持跳转），并设置初始显示样式。"""
    run_begin = paragraph.add_run()
    _apply_run_font(run_begin, font_name, font_size_pt, east_asia, rgb_color, is_bold)
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    run_begin._r.append(fld_char_begin)

    run_instr = paragraph.add_run()
    _apply_run_font(run_instr, font_name, font_size_pt, east_asia, rgb_color, is_bold)
    instr_text = OxmlElement("w:instrText")
    instr_text.text = f" REF {bookmark_name} \\h "
    run_instr._r.append(instr_text)

    run_sep = paragraph.add_run()
    _apply_run_font(run_sep, font_name, font_size_pt, east_asia, rgb_color, is_bold)
    fld_char_sep = OxmlElement("w:fldChar")
    fld_char_sep.set(qn("w:fldCharType"), "separate")
    run_sep._r.append(fld_char_sep)

    run_text = paragraph.add_run(display_text)
    _apply_run_font(run_text, font_name, font_size_pt, east_asia, rgb_color, is_bold)

    run_end = paragraph.add_run()
    _apply_run_font(run_end, font_name, font_size_pt, east_asia, rgb_color, is_bold)
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run_end._r.append(fld_char_end)

def reserve_bookmark_name(doc, token, kind):
    """为引用 token 预留稳定且去重的书签名，支持前向引用。"""
    state = getattr(doc, "_cross_ref_state", None)
    if not state:
        return None
    existing = state["token_to_bookmark"].get(token)
    if existing:
        return existing

    safe = re.sub(r"[^A-Za-z0-9_]+", "_", token)
    base = f"{kind}_{safe}".strip("_")
    if not base:
        base = f"{kind}_ref"
    name = base
    seq = 2
    while name in state["used_bookmark_names"]:
        name = f"{base}_{seq}"
        seq += 1
    state["used_bookmark_names"].add(name)
    state["token_to_bookmark"][token] = name
    return name

def claim_bookmark_for_token(doc, token, kind):
    """获取（或创建）token 的书签名。"""
    return reserve_bookmark_name(doc, token, kind)

def register_token_bookmark(doc, token, kind, paragraph, run):
    """将 token 与书签绑定，并在 run 上落书签。"""
    state = getattr(doc, "_cross_ref_state", None)
    if not state:
        return None
    bookmark_name = claim_bookmark_for_token(doc, token, kind)
    if token in state["bookmarked_tokens"]:
        return bookmark_name
    add_bookmark_around_run(paragraph, run, bookmark_name, state["next_bookmark_id"])
    state["next_bookmark_id"] += 1
    state["bookmarked_tokens"].add(token)
    return bookmark_name

def enable_update_fields_on_open(doc):
    """设置 Word 打开文档时自动更新域。"""
    settings_el = doc.settings.element
    update_node = settings_el.find(qn("w:updateFields"))
    if update_node is None:
        update_node = OxmlElement("w:updateFields")
        settings_el.append(update_node)
    update_node.set(qn("w:val"), "true")

def setup_page_header_footer(doc, header_title="技术投标文件"):
    """设置页眉页脚"""
    for section in doc.sections:
        # 页眉
        header = section.header
        header.is_linked_to_previous = False
        header_para = header.paragraphs[0]
        header_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # 添加红色分隔线
        pPr = header_para._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), '003266')
        pBdr.append(bottom)
        pPr.append(pBdr)

        header_run = header_para.add_run(header_title)
        header_run.font.size = Pt(9)
        header_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        header_run.font.name = '宋体'
        header_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

        # 页脚 - 页码居中
        footer = section.footer
        footer.is_linked_to_previous = False
        footer_para = footer.paragraphs[0]
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 添加红色分隔线
        pPr2 = footer_para._p.get_or_add_pPr()
        pBdr2 = OxmlElement('w:pBdr')
        top = OxmlElement('w:top')
        top.set(qn('w:val'), 'single')
        top.set(qn('w:sz'), '6')
        top.set(qn('w:space'), '1')
        top.set(qn('w:color'), '003266')
        pBdr2.append(top)
        pPr2.append(pBdr2)

        footer_run1 = footer_para.add_run('第 ')
        footer_run1.font.size = Pt(10)
        footer_run1.font.name = '宋体'
        footer_run1._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

        add_page_number_field(footer_para)

        footer_run2 = footer_para.add_run(' 页  共 ')
        footer_run2.font.size = Pt(10)
        footer_run2.font.name = '宋体'
        footer_run2._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

        add_total_pages_field(footer_para)

        footer_run3 = footer_para.add_run(' 页')
        footer_run3.font.size = Pt(10)
        footer_run3.font.name = '宋体'
        footer_run3._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

def resolve_branding_from_generation_mode(mode_str):
    """
    根据标书模式字符串返回 (页眉标题, 封面大字)。
    支持英文：technical / commercial / full；中文：技术标、商务标、全套、商务技术标等。
    未传、空串或无法识别时默认技术标样式。
    """
    raw = (mode_str or "").strip()
    if not raw or raw == "full|commercial|technical" or "|" in raw:
        return "技术投标文件", "技  术  投  标  文  件"

    key = raw.lower().replace(" ", "")

    if key in ("full", "all") or raw in ("全套", "商务技术标"):
        return "投标文件", "投  标  文  件"
    if key == "commercial" or raw in ("商务标", "商务"):
        return "商务投标文件", "商  务  投  标  文  件"
    if key == "technical" or raw in ("技术标", "技术"):
        return "技术投标文件", "技  术  投  标  文  件"

    return "技术投标文件", "技  术  投  标  文  件"


def create_cover_page(
    doc,
    project_name="河南省普通公路干线路网监测系统",
    spaced_title="技  术  投  标  文  件",
):
    """创建蓝色专业投标文件封面"""
    # 顶部蓝色装饰线
    top_line = doc.add_paragraph()
    top_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    top_run = top_line.add_run('─' * 60)
    top_run.font.size = Pt(14)
    top_run.font.color.rgb = GOV_BLUE

    # 空白
    for _ in range(4):
        doc.add_paragraph()

    # 蓝色大标题
    title_box = doc.add_paragraph()
    title_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_box.add_run(spaced_title)
    title_run.bold = True
    title_run.font.size = Pt(40)
    title_run.font.name = '方正小标宋简体'
    title_run._element.rPr.rFonts.set(qn('w:eastAsia'), '方正小标宋简体')
    title_run.font.color.rgb = GOV_BLUE
    title_box.paragraph_format.space_before = Pt(36)

    # 蓝色装饰线
    line1 = doc.add_paragraph()
    line1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    line1_run = line1.add_run('━' * 35)
    line1_run.font.size = Pt(16)
    line1_run.font.color.rgb = GOV_BLUE
    line1_run.bold = True

    line2 = doc.add_paragraph()
    line2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    line2_run = line2.add_run('━' * 35)
    line2_run.font.size = Pt(12)
    line2_run.font.color.rgb = ACCENT_BLUE

    # 项目名称框
    for _ in range(3):
        doc.add_paragraph()

    proj_box = doc.add_paragraph()
    proj_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    proj_run = proj_box.add_run('『 ' + project_name + ' 』')
    proj_run.font.size = Pt(20)
    proj_run.font.name = '黑体'
    proj_run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    proj_run.font.color.rgb = GOV_BLUE
    proj_run.bold = True

    # 空白
    for _ in range(6):
        doc.add_paragraph()

    # 投标人信息框
    info_table = doc.add_table(rows=4, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.style = 'Table Grid'

    info_data = [
        ('投 标 人', '【待补充】'),
        ('地  址', '【待补充】'),
        ('法定代表人', '【待补充】'),
        ('日  期', '【  年  月  日】'),
    ]

    for i, (label, value) in enumerate(info_data):
        row = info_table.rows[i]
        label_cell = row.cells[0]
        value_cell = row.cells[1]

        label_cell.width = Cm(4)
        value_cell.width = Cm(10)

        # 标签 - 蓝色背景
        label_para = label_cell.paragraphs[0]
        label_run = label_para.add_run(label)
        label_run.font.size = Pt(14)
        label_run.font.name = '黑体'
        label_run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
        label_run.font.color.rgb = WHITE
        label_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(label_cell, '003266')

        # 值
        value_para = value_cell.paragraphs[0]
        value_run = value_para.add_run(value)
        value_run.font.size = Pt(14)
        value_run.font.name = '仿宋'
        value_run._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
        set_cell_background(value_cell, 'E8F0FE')

    # 底部装饰
    for _ in range(5):
        doc.add_paragraph()

    bottom_line = doc.add_paragraph()
    bottom_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    bottom_run = bottom_line.add_run('─' * 60)
    bottom_run.font.size = Pt(14)
    bottom_run.font.color.rgb = GOV_BLUE

    # 版权说明
    copyright_para = doc.add_paragraph()
    copyright_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    copyright_para.paragraph_format.space_before = Pt(24)
    copyright_prefix_run = copyright_para.add_run('该技能为中控技术旗下标书魔方团队制作，更多功能体验请至 ')
    copyright_prefix_run.font.size = Pt(11)
    copyright_prefix_run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    copyright_prefix_run.font.name = '宋体'
    copyright_prefix_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    add_external_hyperlink(copyright_para, "https://biaoshu.supcon.com/", "https://biaoshu.supcon.com/")

    # 二维码（封面底部）
    qr_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'static', 'QR_code.png')
    )
    if os.path.exists(qr_path):
        qr_para = doc.add_paragraph()
        qr_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qr_para.paragraph_format.space_before = Pt(8)
        qr_run = qr_para.add_run()
        qr_run.add_picture(qr_path, width=Cm(3.2))

        qr_caption_para = doc.add_paragraph()
        qr_caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qr_caption_para.paragraph_format.space_before = Pt(6)
        qr_caption_run = qr_caption_para.add_run("扫描上方二维码，如有任何问题，欢迎随时和我们交流。")
        qr_caption_run.font.size = Pt(11)
        qr_caption_run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
        qr_caption_run.font.name = '宋体'
        qr_caption_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    else:
        print(f"⚠ 未找到二维码图片，跳过插入: {qr_path}")

    doc.add_page_break()


def int_to_chinese_chapter_index(n):
    """将正整数转为章序号用中文数字（1→一，10→十，11→十一，…，99→九十九）。超出范围返回 None，由调用方改用阿拉伯数字。"""
    digits = "零一二三四五六七八九"
    if n <= 0 or n >= 999:
        return None
    if n < 10:
        return digits[n]
    if n == 10:
        return "十"
    if n < 20:
        return "十" + digits[n % 10] if n % 10 else "十"
    if n < 100:
        tens = n // 10
        ones = n % 10
        s = digits[tens] + "十"
        if ones:
            s += digits[ones]
        return s
    return None


def format_chapter_heading_label(chapter_num):
    """扉页「第X章」：使用阿拉伯数字"""
    if chapter_num >= 999:
        return "本册正文"
    return f"第{chapter_num}章"


def create_toc_page(doc, chapter_entries):
    """创建目录页：使用 Word TOC 域，支持自动更新页码与跳转。"""
    # 目录标题
    toc_title = doc.add_paragraph()
    toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    toc_run = toc_title.add_run('目    录')
    toc_run.bold = True
    toc_run.font.size = Pt(22)
    toc_run.font.name = '方正小标宋简体'
    toc_run._element.rPr.rFonts.set(qn('w:eastAsia'), '方正小标宋简体')
    toc_run.font.color.rgb = GOV_BLUE
    toc_title.paragraph_format.space_after = Pt(18)

    toc_para = doc.add_paragraph()
    toc_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_begin = toc_para.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    # 标记为 dirty，提示 Office/WPS 打开时优先刷新该域
    fld_begin.set(qn("w:dirty"), "true")
    run_begin._r.append(fld_begin)

    run_instr = toc_para.add_run()
    instr = OxmlElement("w:instrText")
    instr.text = ' TOC \\o "1-4" \\h \\z \\u '
    run_instr._r.append(instr)

    run_sep = toc_para.add_run()
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    run_sep._r.append(fld_sep)

    hint = toc_para.add_run("目录将在打开文档时自动更新。")
    hint.font.size = Pt(12)
    hint.font.name = "宋体"
    hint._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    hint.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    run_end = toc_para.add_run()
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run_end._r.append(fld_end)

    doc.add_page_break()

def create_chapter_header(doc, chapter_num, chapter_title):
    """创建章节标题页"""
    # 红色装饰条
    for _ in range(6):
        doc.add_paragraph()

    # 章节编号
    num_para = doc.add_paragraph()
    num_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    heading_label = format_chapter_heading_label(chapter_num)
    num_run = num_para.add_run(heading_label)
    num_run.bold = True
    num_run.font.size = Pt(26)
    num_run.font.name = '黑体'
    num_run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    num_run.font.color.rgb = GOV_BLUE

    if hasattr(doc, "_cross_ref_state") and chapter_num < 999:
        register_token_bookmark(doc, heading_label, "chap", num_para, num_run)
        register_token_bookmark(doc, f"第{chapter_num}章", "chap", num_para, num_run)

    # 章节标题
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.add_run(chapter_title)
    title_run.bold = True
    title_run.font.size = Pt(28)
    title_run.font.name = '方正小标宋简体'
    title_run._element.rPr.rFonts.set(qn('w:eastAsia'), '方正小标宋简体')
    title_run.font.color.rgb = GOV_BLUE
    title_para.paragraph_format.space_before = Pt(24)

    # 装饰线
    line1 = doc.add_paragraph()
    line1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    line1_run = line1.add_run('━' * 25)
    line1_run.font.size = Pt(14)
    line1_run.font.color.rgb = GOV_BLUE
    line1_run.bold = True

    doc.add_page_break()

def add_heading_1(doc, text):
    """一级标题：第X节"""
    p = doc.add_paragraph()
    p.style = "Heading 1"
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(16)
    run.font.name = '黑体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    run.font.color.rgb = GOV_BLUE
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(12)
    # 下划线装饰
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '0070C0')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

def add_heading_2(doc, text):
    """二级标题：X.X"""
    p = doc.add_paragraph()
    p.style = "Heading 2"
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(14)
    run.font.name = '黑体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
    run.font.color.rgb = ACCENT_BLUE
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    return p

def add_heading_3(doc, text):
    """三级标题"""
    p = doc.add_paragraph()
    p.style = "Heading 3"
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(12)
    run.font.name = '楷体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '楷体')
    run.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    return p

def add_heading_4(doc, text):
    """四级标题"""
    p = doc.add_paragraph()
    p.style = "Heading 4"
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(12)
    run.font.name = '仿宋'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '仿宋')
    run.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    return p


def _clear_paragraph_runs(paragraph):
    """移除段落内全部 w:r，便于在单元格等已有段落上重写内容。"""
    p_el = paragraph._p
    for child in list(p_el):
        if child.tag == qn("w:r"):
            p_el.remove(child)


def add_runs_markdown_bold(
    paragraph,
    text,
    font_name,
    font_size_pt,
    east_asia=True,
    rgb_color=None,
    base_bold=False,
    cross_ref_state=None,
):
    """按 **...** 拆分为多个 Run；base_bold 为 True 时非加粗片段也加粗（如表头）。"""
    pos = 0
    for m in MARKDOWN_BOLD_PATTERN.finditer(text):
        if m.start() > pos:
            chunk = text[pos : m.start()]
            _append_text_or_ref_runs(
                paragraph,
                chunk,
                font_name,
                font_size_pt,
                east_asia,
                rgb_color,
                base_bold,
                cross_ref_state,
            )
        _append_text_or_ref_runs(
            paragraph,
            m.group(1),
            font_name,
            font_size_pt,
            east_asia,
            rgb_color,
            True,
            cross_ref_state,
        )
        pos = m.end()
    if pos < len(text):
        _append_text_or_ref_runs(
            paragraph,
            text[pos:],
            font_name,
            font_size_pt,
            east_asia,
            rgb_color,
            base_bold,
            cross_ref_state,
        )


def _add_font_run(paragraph, chunk, font_name, font_size_pt, east_asia, rgb_color, is_bold):
    if not chunk:
        return
    run = paragraph.add_run(chunk)
    _apply_run_font(run, font_name, font_size_pt, east_asia, rgb_color, is_bold)

def _append_text_or_ref_runs(
    paragraph,
    text,
    font_name,
    font_size_pt,
    east_asia,
    rgb_color,
    is_bold,
    cross_ref_state,
):
    """将文本按交叉引用 token 拆分，命中时输出 REF 域。"""
    if not text:
        return

    if not cross_ref_state:
        _add_font_run(paragraph, text, font_name, font_size_pt, east_asia, rgb_color, is_bold)
        return

    pos = 0
    for m in REF_TOKEN_PATTERN.finditer(text):
        if m.start() > pos:
            _add_font_run(
                paragraph,
                text[pos:m.start()],
                font_name,
                font_size_pt,
                east_asia,
                rgb_color,
                is_bold,
            )

        token = m.group(1)
        expected_tokens = cross_ref_state.get("expected_ref_tokens", set())
        already_bookmarked = token in cross_ref_state.get("bookmarked_tokens", set())
        if not already_bookmarked and token not in expected_tokens:
            bookmark_name = None
        elif token.startswith("图"):
            bookmark_name = claim_bookmark_for_token(cross_ref_state["doc"], token, "fig")
        elif token.startswith("表"):
            bookmark_name = claim_bookmark_for_token(cross_ref_state["doc"], token, "tbl")
        else:
            bookmark_name = claim_bookmark_for_token(cross_ref_state["doc"], token, "chap")
        if bookmark_name:
            add_ref_field(
                paragraph,
                bookmark_name,
                token,
                font_name,
                font_size_pt,
                east_asia=east_asia,
                rgb_color=rgb_color,
                is_bold=is_bold,
            )
        else:
            _add_font_run(
                paragraph,
                token,
                font_name,
                font_size_pt,
                east_asia,
                rgb_color,
                is_bold,
            )
        pos = m.end()

    if pos < len(text):
        _add_font_run(
            paragraph,
            text[pos:],
            font_name,
            font_size_pt,
            east_asia,
            rgb_color,
            is_bold,
        )


def add_body_text(doc, text):
    """正文（支持 **加粗**）"""
    p = doc.add_paragraph()
    cross_ref_state = getattr(doc, "_cross_ref_state", None)
    add_runs_markdown_bold(
        p, text, "宋体", 12, east_asia=True, rgb_color=None, base_bold=False, cross_ref_state=cross_ref_state
    )
    p.paragraph_format.first_line_indent = Cm(0.85)  # 两个字符缩进
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_after = Pt(0)
    return p

def add_caption_text(doc, text):
    """标准图/表题注样式（支持 **加粗**）"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_runs_markdown_bold(p, text, "宋体", 10.5, east_asia=True, rgb_color=None, base_bold=False)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    return p

def add_bullet_point(doc, text, level=0):
    """项目符号段落（符号在前；正文支持 **加粗**）"""
    p = doc.add_paragraph()

    if level == 0:
        p.paragraph_format.left_indent = Cm(0.85)
        p.paragraph_format.first_line_indent = Cm(-0.42)
        bullet = "●"
    else:
        p.paragraph_format.left_indent = Cm(1.27)
        p.paragraph_format.first_line_indent = Cm(-0.42)
        bullet = "○"

    bullet_run = p.add_run(bullet + " ")
    bullet_run.font.size = Pt(12)
    bullet_run.font.name = "仿宋"
    bullet_run._element.rPr.rFonts.set(qn("w:eastAsia"), "仿宋")

    cross_ref_state = getattr(doc, "_cross_ref_state", None)
    add_runs_markdown_bold(
        p, text, "仿宋", 12, east_asia=True, rgb_color=None, base_bold=False, cross_ref_state=cross_ref_state
    )
    p.paragraph_format.space_after = Pt(0)
    return p

def add_table(doc, markdown_table):
    """专业表格"""
    lines = markdown_table.strip().split('\n')
    cross_ref_state = getattr(doc, "_cross_ref_state", None)
    if len(lines) < 2:
        return None

    header_line = lines[0]
    headers = [h.strip() for h in header_line.split('|') if h.strip()]

    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.split('|') if c.strip()]
        if cells:
            rows.append(cells)

    # 创建表格
    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # 设置表格整体宽度
    for cell in table.rows[0].cells:
        cell.width = Cm(14.8 / len(headers))

    # 表头
    header_row = table.rows[0]
    for i, header in enumerate(headers):
        cell = header_row.cells[i]
        set_cell_background(cell, '003266')  # 深蓝背景

        para = cell.paragraphs[0]
        _clear_paragraph_runs(para)
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_runs_markdown_bold(
            para,
            header,
            "黑体",
            10,
            east_asia=True,
            rgb_color=WHITE,
            base_bold=True,
            cross_ref_state=cross_ref_state,
        )

        set_cell_margins(cell, 0.1, 0.1, 0.1, 0.1)

    # 数据行
    for row_idx, row_data in enumerate(rows):
        row = table.rows[row_idx + 1]
        bg_color = 'FFFFFF' if row_idx % 2 == 0 else 'F2F7FF'

        for col_idx, cell_text in enumerate(row_data):
            if col_idx < len(headers):
                cell = row.cells[col_idx]
                set_cell_background(cell, bg_color)

                para = cell.paragraphs[0]
                _clear_paragraph_runs(para)
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
                add_runs_markdown_bold(
                    para,
                    cell_text,
                    "仿宋",
                    10,
                    east_asia=True,
                    rgb_color=None,
                    base_bold=False,
                    cross_ref_state=cross_ref_state,
                )

                set_cell_margins(cell, 0.05, 0.05, 0.1, 0.1)

    return table

def _safe_filename_from_text(text, max_len=48):
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", text).strip("_")
    if not slug:
        slug = "image"
    return slug[:max_len]

def _request_json(url, payload, headers, timeout=20):
    req = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return json.loads(resp.read().decode(charset))

def search_best_image(description):
    """调用图片搜索API并返回最优图片URL"""
    return search_multiple_images(description, count=10)

def search_multiple_images(description, count=10):
    """调用图片搜索API并返回多个图片URL列表"""
    if not WEB_IMAGE_SEARCH_API_KEY:
        return []

    payload = {
        "q": description,
        "scope": "image",
        "includeSummary": False,
        "size": str(count),
        "conciseSnippet": False,
    }
    headers = {
        "Authorization": f"Bearer {WEB_IMAGE_SEARCH_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    data = None
    last_exc = None
    for _ in range(2):
        try:
            data = _request_json(WEB_IMAGE_SEARCH_API_URL, payload, headers)
            break
        except Exception as exc:
            last_exc = exc
    if data is None:
        print(f"⚠ 图片检索失败: {description} ({last_exc})")
        return []

    images = data.get("images") or []
    if not images:
        return []

    return [(img.get("imageUrl"), img.get("title")) for img in images]

def download_image(image_url, description, image_cache_dir):
    """下载远程图片到本地缓存目录"""
    if not image_url:
        return None

    os.makedirs(image_cache_dir, exist_ok=True)
    query_hash = hashlib.md5(f"{description}|{image_url}".encode("utf-8")).hexdigest()[:10]
    parsed = urllib.parse.urlparse(image_url)
    guessed_ext = os.path.splitext(parsed.path)[1].lower()
    if guessed_ext not in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}:
        guessed_ext = ".jpg"
    filename = f"{_safe_filename_from_text(description)}_{query_hash}{guessed_ext}"
    local_path = os.path.join(image_cache_dir, filename)
    if os.path.exists(local_path):
        return local_path

    parsed_url = urllib.parse.urlparse(image_url)
    if parsed_url.scheme not in {"http", "https"}:
        print(f"⚠ 非法图片协议，跳过: {image_url}")
        return None

    last_exc = None
    for _ in range(2):
        try:
            req = urllib.request.Request(
                image_url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "image/*,*/*;q=0.8",
                },
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                content_type = resp.headers.get("Content-Type", "")
                if content_type and "image" not in content_type:
                    print(f"⚠ 非图片内容，跳过: {image_url}")
                    return None
                binary = resp.read()
                if not binary:
                    continue
                with open(local_path, "wb") as out:
                    out.write(binary)
                return local_path
        except Exception as exc:
            last_exc = exc

    print(f"⚠ 图片下载失败: {image_url} ({last_exc})")
    return None

def prefetch_images(image_descriptions, image_cache_dir, max_workers=5):
    """并发预下载所有图片描述对应的图片，返回 {description: (local_path, image_title)}"""
    os.makedirs(image_cache_dir, exist_ok=True)
    results = {}

    def fetch_single_image(description):
        image_list = search_multiple_images(description, count=10)
        for image_url, image_title in image_list:
            local_path = download_image(image_url, description, image_cache_dir)
            if local_path:
                return (description, local_path, image_title)
        return (description, None, None)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_single_image, desc): desc for desc in image_descriptions}
        for future in as_completed(futures):
            try:
                desc, local_path, image_title = future.result()
                if local_path:
                    results[desc] = (local_path, image_title)
            except Exception as exc:
                desc = futures[future]
                print(f"⚠ 图片预下载失败: {desc} ({exc})")

    return results

def insert_image_from_description(doc, description, image_cache_dir, chapter_num, figure_index, prefetched=None):
    """根据占位描述搜索并插入图片，并在图片下方自动添加题注。
    尝试多张图片，依次顺延直到成功插入。"""
    if prefetched and description in prefetched:
        local_path, image_title = prefetched[description]
        if local_path:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            try:
                run.add_picture(local_path, width=Cm(12.5))
                caption_text = f"图{chapter_num}-{figure_index + 1} {description}"
                add_caption_text(doc, caption_text)
                if image_title:
                    print(f"✓ 已插入图片: {caption_text} <- {image_title}")
                else:
                    print(f"✓ 已插入图片: {caption_text}")
                return figure_index + 1
            except Exception as exc:
                print(f"  ⏭ 预下载图片插入失败({exc})，尝试搜索其他...")
                try:
                    os.remove(local_path)
                except:
                    pass
    
    image_list = search_multiple_images(description, count=10)
    
    for idx, (image_url, image_title) in enumerate(image_list):
        local_path = download_image(image_url, description, image_cache_dir)
        if not local_path:
            print(f"  ⏭ 图片{idx+1}下载失败，尝试下一个...")
            continue
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        try:
            run.add_picture(local_path, width=Cm(12.5))
            
            caption_text = f"图{chapter_num}-{figure_index + 1} {description}"
            add_caption_text(doc, caption_text)
            
            if image_title:
                print(f"✓ 已插入图片: {caption_text} <- {image_title}")
            else:
                print(f"✓ 已插入图片: {caption_text}")
            return figure_index + 1
        except Exception as exc:
            print(f"  ⏭ 图片{idx+1}插入失败({exc})，尝试下一个...")
            try:
                os.remove(local_path)
            except:
                pass
            continue
    
    print(f"⚠ 所有图片均失败: {description}")
    add_body_text(doc, f"【图片待补充：{description}】")
    return figure_index

def _register_caption_bookmark_if_needed(doc, paragraph, text):
    """若题注以 图X-X / 表X-X 开头，则给编号部分打书签。"""
    m = re.match(r"^(图\d+-\d+|表\d+-\d+)", text)
    if not m:
        return

    token = m.group(1)
    kind = "fig" if token.startswith("图") else "tbl"
    first_run = paragraph.runs[0] if paragraph.runs else paragraph.add_run(token)
    register_token_bookmark(doc, token, kind, paragraph, first_run)

def parse_markdown_to_docx(
    doc,
    markdown_content,
    image_cache_dir,
    chapter_num,
    section_num=0,
    level1_title="",
    level2_title="",
    prefetched=None,
):
    """解析 Markdown 并转换为 DOCX。

    标准章节文件命名：{一级序号}_{一级标题名}_{二级序号}_{二级标题名}_content.md
    - 正文一级、二级标题以文件名为准（不再用 MD 中的 # / ## 生成标题，避免重复与错号）。
    - 三级标题仅来自 MD 中的 ### 行；编号为 {二级序号}.{小节序号}（无二级文件名段时为 {一级序号}.{小节序号}）。
    chapter_num >= 999 时回退为旧逻辑：按 # / ## / ### 解析标题。
    """
    lines = markdown_content.split("\n")
    use_filename_headings = chapter_num < 999 and bool((level1_title or "").strip())

    if not hasattr(doc, "_emitted_h1_chapters"):
        doc._emitted_h1_chapters = set()

    i = 0
    in_table = False
    table_lines = []
    pending_table_caption = None
    if not hasattr(doc, "_chapter_figure_counts"):
        doc._chapter_figure_counts = {}
    figure_index = doc._chapter_figure_counts.get(chapter_num, 0)
    level1_index = chapter_num if use_filename_headings else 0
    level2_index = 0
    level3_index = 0
    NUMBERED_HEADING_PATTERN = re.compile(r"^(\d+[\.、]\d*)*\d+[\.、]?\s*")

    l1 = (level1_title or "").strip()
    l2 = (level2_title or "").strip()

    level2_current = 0

    if use_filename_headings:
        if chapter_num not in doc._emitted_h1_chapters:
            h1_text = l1 if NUMBERED_HEADING_PATTERN.match(l1) else f"{chapter_num} {l1}"
            add_heading_1(doc, h1_text)
            doc._emitted_h1_chapters.add(chapter_num)
        if l2 and section_num > 0:
            h2_text = l2 if NUMBERED_HEADING_PATTERN.match(l2) else f"{chapter_num}.{section_num} {l2}"
            add_heading_2(doc, h2_text)
            level2_current = section_num
        level3_index = 0
    else:
        top_level_title = ""
        chapter_title = f"{l1}_{l2}".strip("_") if (l1 or l2) else ""
        if chapter_title and "_" in chapter_title:
            top_level_title = chapter_title.split("_", 1)[0].strip()

        def _normalize_top_heading(text):
            """归一化一级标题文本，兼容 '# 技术部分' / '# 1 技术部分' / '# 1. 技术部分'。"""
            normalized = text.strip()
            normalized = re.sub(r"^\d+(?:[\.、]\d+)*[\.、]?\s*", "", normalized)
            return normalized.strip()

        normalized_top_level_title = _normalize_top_heading(top_level_title) if top_level_title else ""
        if not hasattr(doc, "_seen_top_level_titles"):
            doc._seen_top_level_titles = set()

    while i < len(lines):
        line = lines[i].strip()

        # 跳过元数据块
        if line.startswith('---'):
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('---'):
                i += 1
            i += 1
            continue

        # 检测表格
        if '|' in line and line.count('|') >= 2:
            in_table = True
            table_lines.append(line)
            i += 1
            continue

        # 处理表格结束
        if in_table and table_lines:
            if pending_table_caption:
                add_caption_text(doc, pending_table_caption)
                pending_table_caption = None
            add_table(doc, '\n'.join(table_lines))
            table_lines = []
            in_table = False
            continue

        # 标准命名：忽略 MD 中的 # / ##（### / #### 仍以正文为准）
        if use_filename_headings:
            if line.startswith("### ") or line.startswith("#### "):
                pass
            elif line.startswith("## "):
                if not l2 or section_num == 0:
                    text = line[3:].strip()
                    level2_current += 1
                    level3_index = 0
                    if NUMBERED_HEADING_PATTERN.match(text):
                        add_heading_2(doc, text)
                    else:
                        add_heading_2(doc, f"{chapter_num}.{level2_current} {text}")
                i += 1
                continue
            elif line.startswith("# "):
                i += 1
                continue

        # 一级标题（仅 legacy）
        if line.startswith('# ') and not use_filename_headings:
            text = line[2:].strip()
            normalized_text = _normalize_top_heading(text)
            if normalized_top_level_title and normalized_text == normalized_top_level_title:
                top_key = f"{chapter_num}:{normalized_top_level_title}"
                if top_key in doc._seen_top_level_titles:
                    i += 1
                    continue
                doc._seen_top_level_titles.add(top_key)
            if '技术部分' not in text:
                level1_index += 1
                level2_index = 0
                level3_index = 0
                if NUMBERED_HEADING_PATTERN.match(text):
                    add_heading_1(doc, text)
                else:
                    add_heading_1(doc, f"{level1_index} {text}")
            else:
                add_heading_1(doc, text)

        # 二级标题（仅 legacy）
        elif line.startswith('## ') and not use_filename_headings:
            text = line[3:].strip()
            level2_index += 1
            level3_index = 0
            if NUMBERED_HEADING_PATTERN.match(text):
                add_heading_2(doc, text)
            else:
                add_heading_2(doc, f"{level1_index}.{level2_index} {text}")

        # 三级标题
        elif line.startswith('### '):
            text = line[4:].strip()
            if use_filename_headings:
                level3_index += 1
                sec_prefix = level2_current if level2_current > 0 else 1
                if NUMBERED_HEADING_PATTERN.match(text):
                    add_heading_3(doc, text)
                else:
                    add_heading_3(doc, f"{chapter_num}.{sec_prefix}.{level3_index} {text}")
            else:
                if level2_index == 0:
                    level2_index = 1
                level3_index += 1
                if NUMBERED_HEADING_PATTERN.match(text):
                    add_heading_3(doc, text)
                else:
                    add_heading_3(doc, f"{level1_index}.{level2_index}.{level3_index} {text}")

        # 四级标题
        elif line.startswith('#### '):
            text = line[5:].strip()
            add_heading_4(doc, text)

        # 空行：不插入空白段落，段间仅保留相邻段落换行
        elif line == '':
            pass

        # 正文
        elif line:
            if CAPTION_PATTERN.match(line):
                p = add_caption_text(doc, line)
                _register_caption_bookmark_if_needed(doc, p, line)
                i += 1
                continue

            if IMAGE_PLACEHOLDER_PATTERN.search(line):
                parts = IMAGE_PLACEHOLDER_PATTERN.split(line)
                for idx, part in enumerate(parts):
                    if idx % 2 == 0:
                        plain = part.strip()
                        if plain:
                            text = plain.replace('★满足', '★').replace('▲满足', '▲')
                            add_body_text(doc, text)
                    else:
                        description = part.strip()
                        if description:
                            new_figure_index = insert_image_from_description(
                                doc, description, image_cache_dir, chapter_num, figure_index, prefetched
                            )
                            if new_figure_index != figure_index:
                                doc._chapter_figure_counts[chapter_num] = new_figure_index
                                figure_index = new_figure_index
                i += 1
                continue

            text = line.replace('★满足', '★').replace('▲满足', '▲')
            add_body_text(doc, text)

        i += 1

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='从章节 Markdown 目录生成专业 DOCX 投标文件')
    parser.add_argument(
        '--chapters-dir',
        default='/workspace/output/content_skill/chapters',
        help='章节 Markdown 目录（*.md；标准命名 一级序号_一级名_二级序号_二级名_content.md，'
        '正文一二级标题取自文件名，三级标题仅来自 ###；chapter_num>=999 时回退按 #/##/### 解析）',
    )
    parser.add_argument(
        '--output-path',
        default='/workspace/output/content_skill/final_bid_document.docx',
        help='输出 DOCX 文件路径',
    )
    parser.add_argument(
        '--document-title',
        default='',
        help='封面所示文档/项目名称',
    )
    parser.add_argument(
        '--generation-mode',
        default='',
        help='标书类型，影响页眉与封面大字：technical|commercial|full 或 技术标|商务标|全套|商务技术标；默认技术标',
    )
    parser.add_argument(
        '--image-cache-dir',
        default='',
        help='图片缓存目录（默认输出目录同级 images）',
    )
    return parser.parse_args()


def parse_chapter_filename(filename):
    """从文件名提取一级/二级序号与标题名。

    优先支持命名：
    1) {一级标题序号}_{一级标题名}_{二级标题序号}_{二级标题名}_content.md
    2) {一级标题序号}_{一级标题名}_content.md（无二级段时 section_num=0、level2 为空）
    若不匹配，回退到宽松解析以兼容历史命名（level2 为空，title 写入 level1）。
    """
    stem = os.path.splitext(filename)[0]

    # 标准四段命名：1_技术部分_1_项目需求分析_content
    m = re.match(r"^(\d+)_([^_]+)_(\d+)_([^_]+)_content$", stem)
    if m:
        return int(m.group(1)), int(m.group(3)), m.group(2).strip(), m.group(4).strip()

    # 标准两段命名：2_技术规格偏差表_content
    m = re.match(r"^(\d+)_([^_]+)_content$", stem)
    if m:
        return int(m.group(1)), 0, m.group(2).strip(), ""

    parts = [p for p in stem.split("_") if p != ""]

    chapter_num = 999
    section_num = 999
    title_parts = parts[:]

    # 章序号：优先取文件名首段数字；若不满足规则，回退旧逻辑
    if parts and parts[0].isdigit():
        chapter_num = int(parts[0])
        title_parts = parts[1:]
        # 节序号：可选
        if title_parts and title_parts[0].isdigit():
            section_num = int(title_parts[0])
            title_parts = title_parts[1:]
        else:
            section_num = 0
    else:
        match = re.search(r"_(\d+)_", stem)
        if match:
            chapter_num = int(match.group(1))
            title_parts = [stem[match.end() :]]

    if title_parts and title_parts[-1].lower() == "content":
        title_parts = title_parts[:-1]
    title = "_".join(title_parts).strip("_- ")
    level1 = title or stem
    return chapter_num, section_num, level1, ""


def discover_chapters(chapters_dir):
    """自动发现章节文件并按序号排序"""
    if not os.path.isdir(chapters_dir):
        return []

    chapters = []
    for filename in os.listdir(chapters_dir):
        if not filename.lower().endswith(".md"):
            continue
        chapter_num, section_num, level1, level2 = parse_chapter_filename(filename)
        chapters.append((filename, chapter_num, section_num, level1, level2))

    chapters.sort(key=lambda item: (item[1], item[2], item[0]))
    return chapters


def collect_expected_reference_tokens(chapter_payloads):
    """预扫描章节内容，收集可被引用的章节/图表编号，避免无源 REF 域。"""
    expected = set()
    for _filename, chapter_num, _section_num, _l1, _l2, content in chapter_payloads:
        heading_label = format_chapter_heading_label(chapter_num)
        expected.add(heading_label)
        if chapter_num < 999:
            expected.add(f"第{chapter_num}章")

        for line in content.split("\n"):
            s = line.strip()
            m = re.match(r"^(图\d+-\d+|表\d+-\d+)", s)
            if m:
                expected.add(m.group(1))
    return expected


def try_update_doc_fields_with_word(output_path):
    """在 Windows 上尝试通过 Word COM 更新目录/域，避免目录页码停留在初始值。"""
    if os.name != "nt":
        return

    abs_output = os.path.abspath(output_path)
    if not os.path.exists(abs_output):
        return
    escaped_output = abs_output.replace("'", "''")

    # 使用 PowerShell 调用 Word COM，无需额外 Python 依赖（如 pywin32）。
    ps_script = (
        "$ErrorActionPreference='Stop';"
        "$word=New-Object -ComObject Word.Application;"
        "$word.Visible=$false;"
        "$word.DisplayAlerts=0;"
        f"$doc=$word.Documents.Open('{escaped_output}');"
        "$doc.Fields.Update() | Out-Null;"
        "foreach($toc in $doc.TablesOfContents){$toc.Update() | Out-Null};"
        "$doc.Save();"
        "$doc.Close();"
        "$word.Quit();"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        print("✓ 已通过 Word COM 自动更新目录与页码域")
    except Exception as exc:
        print(f"⚠ 自动更新目录失败（可在 Word 中全选后按 F9 手动更新）：{exc}")


def main():
    """主函数"""
    args = parse_args()
    output_path = args.output_path
    image_cache_dir = args.image_cache_dir or os.path.join(
        os.path.dirname(output_path), 'images'
    )

    chapter_payloads = []
    chapter_meta = []

    chapters_dir = args.chapters_dir
    chapters = discover_chapters(chapters_dir)
    if not chapters:
        print(f"✗ 未在目录中发现章节 Markdown 文件: {chapters_dir}")
        return
    for filename, num, section_num, level1, level2 in chapters:
        filepath = os.path.join(chapters_dir, filename)
        if not os.path.exists(filepath):
            print(f"✗ 文件不存在: {filepath}")
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            chapter_payloads.append((filename, num, section_num, level1, level2, f.read()))
        chapter_meta.append((filename, num, section_num, level1, level2))

    if not chapter_payloads:
        print("✗ 未读取到可用章节内容")
        return

    header_title, cover_spaced_title = resolve_branding_from_generation_mode(
        args.generation_mode
    )
    project_name = args.document_title or '【待填写项目名称】'

    # 创建文档
    doc = Document()
    enable_update_fields_on_open(doc)
    doc._chapter_figure_counts = {}
    expected_ref_tokens = collect_expected_reference_tokens(chapter_payloads)
    doc._cross_ref_state = {
        "doc": doc,
        "next_bookmark_id": 1,
        "used_bookmark_names": set(),
        "token_to_bookmark": {},
        "bookmarked_tokens": set(),
        "expected_ref_tokens": expected_ref_tokens,
    }

    # 设置页面
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)

    # 设置页眉页脚
    setup_page_header_footer(doc, header_title=header_title)

    # 创建封面
    create_cover_page(doc, project_name=project_name, spaced_title=cover_spaced_title)

    # 创建目录（与即将合并的章节列表一致，避免固定示例章数造成误解）
    create_toc_page(doc, chapter_meta)

    print("🔄 正在并发预下载图片...")
    all_image_descriptions = set()
    for _filename, _num, _section_num, _l1, _l2, content in chapter_payloads:
        for match in IMAGE_PLACEHOLDER_PATTERN.finditer(content):
            desc = match.group(1).strip()
            if desc:
                all_image_descriptions.add(desc)
    prefetched_images = {}
    if all_image_descriptions:
        prefetched_images = prefetch_images(list(all_image_descriptions), image_cache_dir, max_workers=5)
        print(f"✓ 图片预下载完成，成功 {len(prefetched_images)}/{len(all_image_descriptions)}")

    # 处理章节：同一章（chapter_num）仅在首次出现时插入章节扉页，
    # 后续同章拆分文件（如 技术部分_项目需求分析 / 技术部分_总体实施方案）不再重复插入。
    rendered_chapter_headers = set()
    for filename, num, section_num, level1, level2, content in chapter_payloads:
        if num != 0 and num not in rendered_chapter_headers:
            create_chapter_header(doc, num, level1)
            rendered_chapter_headers.add(num)
        parse_markdown_to_docx(
            doc, content, image_cache_dir, num, section_num, level1, level2, prefetched_images
        )
        doc.add_page_break()
        display = f"{level1}_{level2}".strip("_") if level2 else level1
        print(f"✓ 已处理: {display}")

    # 保存
    doc.save(output_path)
    try_update_doc_fields_with_word(output_path)
    print(f"\n✓ 专业投标文件已生成: {output_path}")

if __name__ == '__main__':
    main()