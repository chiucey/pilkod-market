"""
ChineseDoc — a small builder on top of python-docx for producing
Simplified-Chinese academic Word documents that follow the user's
formatting rules:

    Body text          : 宋体  (SimSun)   小四 (12pt)  1.5 spacing
    L1 heading         : 黑体  (SimHei)   小四 (12pt)  1.5 spacing
    L2 / L3 heading    : 宋体  (SimSun)   小四 (12pt)  bold
    Box title          : 宋体  (SimSun)   小四 (12pt)  bold
    Table cell         : 楷体  (KaiTi)    小五 (9pt)
    Table caption/source/figure note : 宋体 (SimSun)  小五 (9pt)
    References (English) : Times New Roman 小四 (12pt)

IMPORTANT: python-docx does NOT set East-Asian (eastAsia) fonts via
`run.font.name` alone — that only sets the "ascii"/"hAnsi" attribute on
the underlying <w:rFonts> element. To make Chinese characters render in
SimSun / SimHei / KaiTi, the `w:eastAsia` attribute must be set
explicitly on the rPr's rFonts element. `_set_font()` below does this.

Inline emphasis convention used by this builder when parsing strings:
    **bold text**          → bold run
    *italic text*          → italic run
    ***bold-italic text*** → bold + italic run

This lets callers write:
    doc.add_box_body("***资金筹集***（Revenue collection）描述...")
"""

import re
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ---------- font / run helpers ----------

def _set_font(run, *, ascii_font: str, east_asia_font: str, size_pt: float,
              bold: bool = False, italic: bool = False):
    """Apply Western + East-Asian font and size to a run.

    Crucially sets the w:eastAsia attribute on rPr/rFonts so that Chinese
    characters render in the requested CJK font instead of the
    Word default.
    """
    run.font.name = ascii_font
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic

    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:ascii'), ascii_font)
    rFonts.set(qn('w:hAnsi'), ascii_font)
    rFonts.set(qn('w:eastAsia'), east_asia_font)
    rFonts.set(qn('w:cs'), ascii_font)


def _set_paragraph_spacing(paragraph, line_spacing=1.5,
                           space_before_pt: float = 0,
                           space_after_pt: float = 6):
    pf = paragraph.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line_spacing
    pf.space_before = Pt(space_before_pt)
    pf.space_after = Pt(space_after_pt)


# ---------- inline emphasis parser ----------

_INLINE_RE = re.compile(
    r'(\*\*\*[^*]+\*\*\*'    # ***bold italic***
    r'|\*\*[^*]+\*\*'        # **bold**
    r'|\*[^*]+\*)'           # *italic*
)


def _parse_inline(text: str):
    """Yield (segment, bold, italic) tuples by splitting on **/* markers."""
    parts = _INLINE_RE.split(text)
    for p in parts:
        if not p:
            continue
        if p.startswith('***') and p.endswith('***'):
            yield p[3:-3], True, True
        elif p.startswith('**') and p.endswith('**'):
            yield p[2:-2], True, False
        elif p.startswith('*') and p.endswith('*'):
            yield p[1:-1], False, True
        else:
            yield p, False, False


# ---------- the builder ----------

class ChineseDoc:
    """Builder for a Simplified-Chinese academic .docx."""

    # Font shortcuts
    SIMSUN = 'SimSun'      # 宋体
    SIMHEI = 'SimHei'      # 黑体
    KAITI = 'KaiTi'        # 楷体
    TIMES = 'Times New Roman'

    # Size shortcuts
    XIAO_SI = 12.0   # 小四
    XIAO_WU = 9.0    # 小五

    def __init__(self):
        self.doc = Document()
        # Set the document's default style so that any unstyled run
        # still uses something reasonable.
        normal = self.doc.styles['Normal']
        normal.font.name = self.TIMES
        normal.font.size = Pt(self.XIAO_SI)
        rPr = normal.element.get_or_add_rPr()
        rFonts = rPr.find(qn('w:rFonts'))
        if rFonts is None:
            rFonts = OxmlElement('w:rFonts')
            rPr.insert(0, rFonts)
        rFonts.set(qn('w:ascii'), self.TIMES)
        rFonts.set(qn('w:hAnsi'), self.TIMES)
        rFonts.set(qn('w:eastAsia'), self.SIMSUN)

    # ---- structural elements ----

    def add_chapter_title(self, text: str):
        """e.g. '第九章  卫生筹资'  — large, bold, SimHei."""
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.5,
                               space_before_pt=12, space_after_pt=12)
        run = p.add_run(text)
        _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMHEI,
                  size_pt=18, bold=True)
        return p

    def add_authors(self, text: str):
        """Author block — SimSun, 小四, italic optional."""
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.5, space_after_pt=12)
        run = p.add_run(text)
        _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMSUN,
                  size_pt=self.XIAO_SI)
        return p

    def add_h1(self, text: str):
        """Level-1 heading — SimHei 小四."""
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.5,
                               space_before_pt=12, space_after_pt=6)
        run = p.add_run(text)
        _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMHEI,
                  size_pt=self.XIAO_SI, bold=True)
        return p

    def add_h2(self, text: str):
        """Level-2 heading — SimSun 小四 bold."""
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.5,
                               space_before_pt=8, space_after_pt=4)
        run = p.add_run(text)
        _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMSUN,
                  size_pt=self.XIAO_SI, bold=True)
        return p

    def add_h3(self, text: str):
        """Level-3 heading — SimSun 小四 bold italic."""
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.5,
                               space_before_pt=6, space_after_pt=4)
        run = p.add_run(text)
        _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMSUN,
                  size_pt=self.XIAO_SI, bold=True, italic=True)
        return p

    def add_body(self, text: str, indent_first_line: bool = True):
        """Body paragraph — SimSun 小四 1.5 spacing.

        Inline emphasis: **bold**, *italic*, ***bold italic***.
        First-line indent of 2 Chinese characters is applied by default.
        """
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.5, space_after_pt=6)
        if indent_first_line:
            # 2 Chinese characters ≈ 24pt at 12pt font
            p.paragraph_format.first_line_indent = Pt(24)
        for seg, bold, italic in _parse_inline(text):
            run = p.add_run(seg)
            _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMSUN,
                      size_pt=self.XIAO_SI, bold=bold, italic=italic)
        return p

    def add_box_title(self, text: str):
        """e.g. '专栏9.1 卫生筹资功能' — SimSun 小四 bold."""
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.5,
                               space_before_pt=10, space_after_pt=4)
        run = p.add_run(text)
        _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMSUN,
                  size_pt=self.XIAO_SI, bold=True)
        return p

    def add_box_body(self, text: str):
        """A paragraph inside a box. Same as body but no first-line indent
        (boxes typically use flush-left)."""
        return self.add_body(text, indent_first_line=False)

    def add_figure_caption(self, text: str):
        """e.g. '图9.1 ...' — SimSun 小四 bold."""
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.5,
                               space_before_pt=8, space_after_pt=4)
        run = p.add_run(text)
        _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMSUN,
                  size_pt=self.XIAO_SI, bold=True)
        return p

    def add_figure_note(self, text: str):
        """Note/source line under a figure — SimSun 小五 single spacing."""
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.0, space_after_pt=2)
        run = p.add_run(text)
        _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMSUN,
                  size_pt=self.XIAO_WU)
        return p

    def add_table_caption(self, text: str):
        """e.g. '表9.1 ...' — SimSun 小四 bold."""
        return self.add_figure_caption(text)

    def add_table(self, header_row, body_rows, source: str | None = None,
                  notes: list[str] | None = None):
        """Add a styled table.

        - header_row: list[str]
        - body_rows: list[list[str]]
        - source: optional source line shown below the table (小五 宋体)
        - notes: optional list of note strings shown below source (小五 宋体)

        Header cells use 宋体 小五 bold; body cells use 楷体 小五.
        """
        n_cols = len(header_row)
        table = self.doc.add_table(rows=1 + len(body_rows), cols=n_cols)
        table.style = 'Table Grid'

        # header
        for j, txt in enumerate(header_row):
            cell = table.rows[0].cells[j]
            cell.text = ''
            p = cell.paragraphs[0]
            run = p.add_run(txt)
            _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMSUN,
                      size_pt=self.XIAO_WU, bold=True)
            _set_paragraph_spacing(p, line_spacing=1.0, space_after_pt=0)

        # body
        for i, row in enumerate(body_rows, start=1):
            for j, txt in enumerate(row):
                cell = table.rows[i].cells[j]
                cell.text = ''
                p = cell.paragraphs[0]
                run = p.add_run(txt)
                _set_font(run, ascii_font=self.TIMES, east_asia_font=self.KAITI,
                          size_pt=self.XIAO_WU)
                _set_paragraph_spacing(p, line_spacing=1.0, space_after_pt=0)

        if source:
            self.add_figure_note(source)
        if notes:
            for note in notes:
                self.add_figure_note(note)

        return table

    def add_reference(self, text: str):
        """A bibliography entry. Kept in original English (Times New Roman)."""
        p = self.doc.add_paragraph()
        _set_paragraph_spacing(p, line_spacing=1.5, space_after_pt=4)
        # Hanging indent looks nice for bibliographies
        p.paragraph_format.left_indent = Pt(18)
        p.paragraph_format.first_line_indent = Pt(-18)
        run = p.add_run(text)
        _set_font(run, ascii_font=self.TIMES, east_asia_font=self.SIMSUN,
                  size_pt=self.XIAO_SI)
        return p

    def add_page_break(self):
        self.doc.add_page_break()

    def save(self, path: str):
        self.doc.save(path)


# ---------- self-test ----------
if __name__ == '__main__':
    import os
    os.makedirs('/tmp/chinese-doc-test', exist_ok=True)
    out = '/tmp/chinese-doc-test/sample.docx'

    d = ChineseDoc()
    d.add_chapter_title('第九章  卫生筹资')
    d.add_authors('卡拉·汉森（Kara Hanson）、马塞尔·韦内马（Marcel Venema）')
    d.add_h1('关键信息')
    d.add_body('卫生筹资（Health financing）的职能是调动充足资源，'
               '保障初级卫生保健（Primary Health Care，PHC）有效运转。')
    d.add_h1('9.1 引言')
    d.add_body('卫生筹资安排是卫生部门政策制定者推动卫生体系'
               '重心转向初级卫生保健的关键工具。')
    d.add_box_title('专栏9.1 卫生筹资功能')
    d.add_box_body('***资金筹集***（Revenue collection）描述卫生资金筹集方式，'
                   '并根据资金来源进行分类。')
    d.add_table_caption('表9.1 各收入组国家初级卫生保健支出均值')
    d.add_table(
        header_row=['收入组', '人均卫生总支出 (美元)', '人均PHC支出 (美元)'],
        body_rows=[
            ['低收入', '38', '21'],
            ['中低收入', '103', '48'],
            ['中高收入', '472', '188'],
            ['高收入', '3 471', '1 362'],
        ],
        source='资料来源：作者基于WHO，2023和OECD，2023计算所得',
        notes=['注：a. 数据取自最新可得年份，主要为2019年和2020年。'],
    )
    d.add_h1('参考文献')
    d.add_reference('Hanson K et al. (2022). The Lancet Global Health '
                    'Commission on financing primary health care: putting '
                    'people at the centre. Lancet Glob Health, 10(5):e715–72.')
    d.save(out)
    print(f'Wrote {out}')
