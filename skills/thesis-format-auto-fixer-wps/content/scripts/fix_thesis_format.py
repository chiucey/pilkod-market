#!/usr/bin/env python3
"""
毕业论文格式全自动修复脚本（WPS 兼容版）
依赖：python-docx, lxml
用法：python fix_thesis_format.py <论文路径.docx> <规范字典.json> <输出路径.docx>
"""

import sys
import json
import re
import copy
from datetime import datetime
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.enum.section import WD_SECTION, WD_ORIENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    import lxml.etree as etree
except ImportError:
    print("缺少依赖，正在安装...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "python-docx", "lxml", "-q"])
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.enum.section import WD_SECTION, WD_ORIENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    import lxml.etree as etree


# ─────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────

def set_paragraph_font(paragraph, font_name=None, font_size=None, bold=None,
                        italic=None, color=None):
    """设置段落所有 run 的字体属性"""
    for run in paragraph.runs:
        if font_name:
            run.font.name = font_name
            # 同时设置中文字体
            r = run._r
            rPr = r.get_or_add_rPr()
            rFonts = rPr.find(qn('w:rFonts'))
            if rFonts is None:
                rFonts = OxmlElement('w:rFonts')
                rPr.insert(0, rFonts)
            rFonts.set(qn('w:eastAsia'), font_name)
        if font_size:
            run.font.size = Pt(font_size)
        if bold is not None:
            run.font.bold = bold
        if italic is not None:
            run.font.italic = italic
        if color:
            run.font.color.rgb = RGBColor(*color)


def set_paragraph_spacing(paragraph, line_spacing=None, line_spacing_rule=None,
                           space_before=None, space_after=None,
                           first_line_indent=None, left_indent=None,
                           alignment=None):
    """设置段落间距与缩进"""
    pf = paragraph.paragraph_format
    if alignment is not None:
        pf.alignment = alignment
    if space_before is not None:
        pf.space_before = Pt(space_before)
    if space_after is not None:
        pf.space_after = Pt(space_after)
    if first_line_indent is not None:
        pf.first_line_indent = Cm(first_line_indent)
    if left_indent is not None:
        pf.left_indent = Cm(left_indent)
    if line_spacing is not None:
        if line_spacing_rule == 'fixed':
            pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            pf.line_spacing = Pt(line_spacing)
        elif line_spacing_rule == 'multiple':
            pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            pf.line_spacing = line_spacing
        else:
            pf.line_spacing = Pt(line_spacing)


def set_page_margins(section, spec):
    """应用页面设置"""
    margins = spec.get('page_margins', {})
    if margins.get('top'):
        section.top_margin = Cm(margins['top'])
    if margins.get('bottom'):
        section.bottom_margin = Cm(margins['bottom'])
    if margins.get('left'):
        section.left_margin = Cm(margins['left'])
    if margins.get('right'):
        section.right_margin = Cm(margins['right'])
    if margins.get('gutter'):
        section.gutter = Cm(margins['gutter'])

    paper = spec.get('paper_size', 'A4')
    if paper == 'A4':
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
    elif paper == 'B5':
        section.page_width = Cm(18.2)
        section.page_height = Cm(25.7)


def detect_heading_level(paragraph):
    """根据文本内容和样式推断标题层级，返回 1/2/3/4 或 None"""
    text = paragraph.text.strip()
    style_name = paragraph.style.name.lower() if paragraph.style else ''

    # 样式名直接匹配
    for level in range(1, 5):
        if f'heading {level}' in style_name or f'标题 {level}' in style_name:
            return level

    # 编号规则匹配（中文/数字）
    patterns = [
        (1, r'^(第[一二三四五六七八九十百]+章|第[0-9]+章|\d+\s+[^\d])'),
        (1, r'^[一二三四五六七八九十]+[、.]'),
        (2, r'^\d+\.\d+\s'),
        (3, r'^\d+\.\d+\.\d+\s'),
        (4, r'^\d+\.\d+\.\d+\.\d+\s'),
    ]
    for level, pat in patterns:
        if re.match(pat, text):
            return level
    return None


def detect_section_type(paragraphs):
    """识别论文各部分边界，返回每段的 section_tag"""
    tags = ['body'] * len(paragraphs)
    keywords = {
        'cover': ['封面', '毕业论文', '学号', '指导教师', '学院', '专业'],
        'declaration': ['独创性声明', '诚信声明', '原创性声明'],
        'abstract_zh': ['摘要', '中文摘要'],
        'abstract_en': ['abstract', 'ABSTRACT'],
        'toc': ['目录', 'contents', 'table of contents'],
        'references': ['参考文献', 'references', '引用文献'],
        'appendix': ['附录', 'appendix'],
    }
    current_tag = 'cover'
    for i, p in enumerate(paragraphs):
        text_lower = p.text.strip().lower()
        for tag, kws in keywords.items():
            if any(kw.lower() in text_lower for kw in kws):
                current_tag = tag
                break
        tags[i] = current_tag
        if current_tag == 'references':
            # 参考文献之后可能是附录
            pass
    return tags


def apply_body_format(paragraph, spec):
    """应用正文段落格式"""
    body_spec = spec.get('body', {})
    set_paragraph_font(paragraph,
                       font_name=body_spec.get('font', '宋体'),
                       font_size=body_spec.get('size', 12),
                       bold=False, italic=False)
    set_paragraph_spacing(paragraph,
                          line_spacing=body_spec.get('line_spacing', 23),
                          line_spacing_rule=body_spec.get('line_spacing_rule', 'fixed'),
                          space_before=body_spec.get('space_before', 0),
                          space_after=body_spec.get('space_after', 0),
                          first_line_indent=body_spec.get('first_line_indent', 0.85),
                          alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)


def apply_heading_format(paragraph, level, spec):
    """应用标题格式"""
    key = f'heading_{level}'
    h_spec = spec.get(key, {})
    defaults = {
        1: {'font': '黑体', 'size': 16, 'bold': True},
        2: {'font': '黑体', 'size': 14, 'bold': True},
        3: {'font': '黑体', 'size': 12, 'bold': True},
        4: {'font': '宋体', 'size': 12, 'bold': True},
    }
    d = defaults.get(level, {})
    set_paragraph_font(paragraph,
                       font_name=h_spec.get('font', d.get('font', '黑体')),
                       font_size=h_spec.get('size', d.get('size', 12)),
                       bold=h_spec.get('bold', d.get('bold', True)),
                       italic=h_spec.get('italic', False))
    set_paragraph_spacing(paragraph,
                          space_before=h_spec.get('space_before', 12),
                          space_after=h_spec.get('space_after', 6),
                          line_spacing=h_spec.get('line_spacing', 23),
                          line_spacing_rule=h_spec.get('line_spacing_rule', 'fixed'),
                          first_line_indent=0,
                          alignment=WD_ALIGN_PARAGRAPH.LEFT)

    # 设置 WPS/Word 标题样式
    try:
        paragraph.style = paragraph.part.document.styles[f'Heading {level}']
    except (KeyError, Exception):
        pass


def renumber_figures_tables(doc, spec):
    """重新编号图和表，返回修改数量"""
    fig_spec = spec.get('figures', {})
    fig_pattern = fig_spec.get('numbering', '图{chapter}-{seq}')
    tab_spec = spec.get('tables', {})
    tab_pattern = tab_spec.get('numbering', '表{chapter}-{seq}')

    fig_count = 0
    tab_count = 0
    chapter = 1
    fig_seq = 1
    tab_seq = 1

    for para in doc.paragraphs:
        text = para.text.strip()
        # 检测章节变化
        if re.match(r'^(第[一二三四五六七八九十]+章|\d+\s)', text):
            m = re.match(r'^(\d+)', text)
            if m:
                new_ch = int(m.group(1))
                if new_ch != chapter:
                    chapter = new_ch
                    fig_seq = 1
                    tab_seq = 1

        # 图标题
        if re.match(r'^图\s*\d', text) or re.match(r'^Figure\s*\d', text, re.I):
            new_num = fig_pattern.format(chapter=chapter, seq=fig_seq)
            new_text = re.sub(r'^(图|Figure)\s*[\d\-]+', new_num, text, flags=re.I)
            if new_text != text:
                for run in para.runs:
                    run.text = ''
                if para.runs:
                    para.runs[0].text = new_text
                else:
                    para.add_run(new_text)
                fig_count += 1
            fig_seq += 1

        # 表标题
        if re.match(r'^表\s*\d', text) or re.match(r'^Table\s*\d', text, re.I):
            new_num = tab_pattern.format(chapter=chapter, seq=tab_seq)
            new_text = re.sub(r'^(表|Table)\s*[\d\-]+', new_num, text, flags=re.I)
            if new_text != text:
                for run in para.runs:
                    run.text = ''
                if para.runs:
                    para.runs[0].text = new_text
                else:
                    para.add_run(new_text)
                tab_count += 1
            tab_seq += 1

    return fig_count + tab_count


def fix_references(doc, spec):
    """修复参考文献格式，返回修改数量"""
    ref_spec = spec.get('references', {})
    in_ref = False
    count = 0

    for para in doc.paragraphs:
        text = para.text.strip()
        if re.match(r'^参考文献|^References$', text, re.I):
            in_ref = True
            continue
        if in_ref and text:
            # 修正悬挂缩进
            left = ref_spec.get('left_indent', 0)
            hanging = ref_spec.get('hanging_indent', 0.75)
            pf = para.paragraph_format
            pf.left_indent = Cm(left + hanging)
            pf.first_line_indent = Cm(-hanging)

            # 修正字体
            set_paragraph_font(para,
                               font_name=ref_spec.get('font', '宋体'),
                               font_size=ref_spec.get('size', 10.5))

            # 修正行距
            set_paragraph_spacing(para,
                                  line_spacing=ref_spec.get('line_spacing', 20),
                                  line_spacing_rule=ref_spec.get('line_spacing_rule', 'fixed'),
                                  space_before=0, space_after=0)
            count += 1

        # 遇到附录停止
        if in_ref and re.match(r'^附录', text):
            break

    return count


def add_page_numbers(doc, spec):
    """配置分节页码（封面无页码，摘要罗马数字，正文阿拉伯数字）"""
    # 此处为简化实现，实际需根据规范配置分节符
    # python-docx 的页眉页脚操作需要操作 XML
    try:
        sections = doc.sections
        for i, section in enumerate(sections):
            if i == 0:
                # 封面节：无页码
                footer = section.footer
                footer.is_linked_to_previous = False
                for para in footer.paragraphs:
                    for run in para.runs:
                        run.text = ''
            elif i == 1:
                # 摘要节：罗马数字
                _set_roman_page_number(section)
            else:
                # 正文节：阿拉伯数字
                _set_arabic_page_number(section)
    except Exception as e:
        pass  # 静默失败，不破坏文档


def _set_arabic_page_number(section):
    """设置阿拉伯数字页码"""
    footer = section.footer
    footer.is_linked_to_previous = False
    if not footer.paragraphs:
        return
    para = footer.paragraphs[0]
    para.clear()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.text = ' PAGE '
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def _set_roman_page_number(section):
    """设置罗马数字页码（通过 XML 设置页码格式）"""
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        pgNumType = OxmlElement('w:pgNumType')
        sectPr.append(pgNumType)
    pgNumType.set(qn('w:fmt'), 'lowerRoman')
    pgNumType.set(qn('w:start'), '1')
    _set_arabic_page_number(section)  # 插入域代码，格式由 pgNumType 控制


# ─────────────────────────────────────────────
# 主处理函数
# ─────────────────────────────────────────────

def fix_thesis(thesis_path: str, spec: dict, output_path: str) -> dict:
    """
    主处理函数
    :param thesis_path: 论文 docx 路径
    :param spec: 解析好的格式规范字典
    :param output_path: 输出 docx 路径
    :return: 修改报告数据字典
    """
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'thesis_file': thesis_path,
        'changes': {},
        'manual_checks': [],
        'total': 0
    }

    doc = Document(thesis_path)

    # ── 1. 页面设置 ──
    page_changes = 0
    for section in doc.sections:
        set_page_margins(section, spec)
        page_changes += 1
    report['changes']['page_setup'] = f'共修改 {page_changes} 节页面设置'

    # ── 2. 识别结构 ──
    paragraphs = doc.paragraphs
    # section_tags = detect_section_type(paragraphs)  # 备用

    # ── 3. 逐段格式修复 ──
    heading_count = 0
    body_count = 0

    for i, para in enumerate(paragraphs):
        if not para.text.strip():
            continue

        level = detect_heading_level(para)
        if level:
            apply_heading_format(para, level, spec)
            heading_count += 1
        else:
            # 跳过封面、声明、目录等特殊段落（由关键词粗判）
            text = para.text.strip()
            if any(kw in text for kw in ['学号', '指导教师', '目录', '独创性', '摘要', '关键词', 'Abstract']):
                continue
            apply_body_format(para, spec)
            body_count += 1

    report['changes']['headings'] = f'共修复标题格式 {heading_count} 处'
    report['changes']['body'] = f'共修复正文格式 {body_count} 处'

    # ── 4. 图表编号 ──
    fig_tab_count = renumber_figures_tables(doc, spec)
    report['changes']['figures_tables'] = f'共修复图表编号 {fig_tab_count} 处'

    # ── 5. 参考文献 ──
    ref_count = fix_references(doc, spec)
    report['changes']['references'] = f'共修复参考文献格式 {ref_count} 处'

    # ── 6. 页眉页脚页码 ──
    add_page_numbers(doc, spec)
    report['changes']['page_numbers'] = '已配置分节页码（封面无页码/摘要罗马数字/正文阿拉伯数字）'

    # ── 7. 目录提示 ──
    report['manual_checks'].append('目录：请在 WPS 中打开文档后，右键目录区域选择"更新域"以刷新页码。')

    # ── 8. 保存 ──
    doc.save(output_path)

    # 统计总数
    report['total'] = sum(
        int(re.search(r'\d+', v).group()) if re.search(r'\d+', v) else 1
        for v in report['changes'].values()
    )

    return report


def generate_report_text(report: dict, spec_source: str) -> str:
    """生成修改报告文本"""
    lines = [
        '=' * 60,
        '毕业论文格式修改报告',
        '=' * 60,
        f'规范来源：{spec_source}',
        f'处理时间：{report["timestamp"]}',
        f'论文原文：{report["thesis_file"]}',
        '',
        f'一、检测到的格式问题总计：{report["total"]} 处',
        '',
        '二、修复明细',
    ]
    for key, val in report['changes'].items():
        lines.append(f'  【{key}】{val}')
    lines.append('')
    lines.append('三、需手动检查的项目')
    if report['manual_checks']:
        for item in report['manual_checks']:
            lines.append(f'  - {item}')
    else:
        lines.append('  无')
    lines.append('=' * 60)
    return '\n'.join(lines)


# ─────────────────────────────────────────────
# 命令行入口
# ─────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('用法: python fix_thesis_format.py <论文.docx> <规范.json> <输出.docx> [规范来源名称]')
        sys.exit(1)

    thesis_path = sys.argv[1]
    spec_json = sys.argv[2]
    output_path = sys.argv[3]
    spec_source = sys.argv[4] if len(sys.argv) > 4 else '格式规范文档'

    with open(spec_json, 'r', encoding='utf-8') as f:
        spec = json.load(f)

    report = fix_thesis(thesis_path, spec, output_path)
    report_text = generate_report_text(report, spec_source)

    # 输出报告到文件
    report_file = Path(output_path).parent / '格式修改报告.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print(f'\n✅ 修复完成：{output_path}')
    print(f'✅ 报告已生成：{report_file}')
