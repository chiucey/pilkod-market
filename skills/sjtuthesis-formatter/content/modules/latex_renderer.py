"""
SJTU Thesis — LaTeX (.tex) Renderer
====================================

Generates LaTeX source files compatible with the SJTUThesis template.
Also supports standalone .tex output for users without SJTUThesis installed.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .thesis_info import ThesisInfo


# ── Templates ──────────────────────────────────────────────────────

SJTUTHESIS_PREAMBLE = """\
% !TEX program = xelatex
\\documentclass[
    type={degree_type},
    % lang=cn
]{{sjtuthesis}}

% ── Thesis Info ────────────────────────────────────────────────────
\\title{{{title_cn}}}
\\title*{{{title_en}}}
\\author{{{author}}}
\\date{{{date}}}

% Keywords
\\keywords{{{keywords_cn}}}
\\keywords*{{{keywords_en}}}

% Supervisor
\\supervisor{{{supervisor}}}

\\begin{{document}}

% ── Front Matter ───────────────────────────────────────────────────
% Abstract
\\begin{{abstract}}
{abstract_cn}
\\end{{abstract}}

\\begin{{abstract*}}
{abstract_en}
\\end{{abstract*}}

% Table of Contents
\\tableofcontents

% ── Main Body ──────────────────────────────────────────────────────
{body_content}

% ── Bibliography ───────────────────────────────────────────────────
{references}

% ── Acknowledgements ──────────────────────────────────────────────
{acknowledgements}

\\end{{document}}
"""

STANDALONE_PREAMBLE = r"""
\documentclass[a4paper,12pt]{article}
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont{SimSun}
\setCJKsansfont{SimHei}
\setCJKmonofont{FangSong}
\usepackage[top=3.7cm, bottom=3.5cm, left=2.8cm, right=2.6cm]{geometry}
\usepackage{setspace}
\usepackage{fancyhdr}
\usepackage{tocloft}
\usepackage{graphicx}
\usepackage{caption}
\usepackage{booktabs}
\usepackage{amsmath,amssymb}
\usepackage[super,square,sort&compress]{natbib}
\usepackage[UTF8]{ctex}
% CJK font shorthand commands
\newcommand{\hei}{\CJKfontspec{SimHei}}
\newcommand{\song}{\CJKfontspec{SimSun}}
\newcommand{\fs}{\CJKfontspec{FangSong}}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[CE]{\small EVEN_HEADER_PLACEHOLDER}
\fancyhead[CO]{\small ODD_HEADER_PLACEHOLDER}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\usepackage{titlesec}
\titleformat{\section}{\centering\hei\fontsize{16pt}{20pt}\selectfont}{\thesection}{1em}{}
\titlespacing{\section}{0pt}{24pt}{18pt}
\titleformat{\subsection}{\raggedright\hei\fontsize{14pt}{20pt}\selectfont}{\thesubsection}{1em}{}
\titlespacing{\subsection}{0pt}{12pt}{6pt}
\titleformat{\subsubsection}{\raggedright\hei\fontsize{12pt}{20pt}\selectfont}{\thesubsubsection}{1em}{}
\titlespacing{\subsubsection}{0pt}{6pt}{3pt}
\renewcommand{\normalsize}{\fontsize{12pt}{20pt}\selectfont}
\setlength{\parindent}{2em}
\setlength{\parskip}{0pt}
\renewcommand{\contentsname}{\centering\hei\fontsize{16pt}{20pt}\selectfont 目{}录}
\begin{document}
\begin{titlepage}
\centering
\vspace*{4cm}
{\hei\fontsize{26pt}{30pt}\selectfont 上海交通大学}\\[0.5cm]
{\hei\fontsize{22pt}{26pt}\selectfont DEGREE_LABEL_PLACEHOLDER学位论文}\\[2cm]
{\hei\fontsize{16pt}{20pt}\selectfont TITLE_CN_PLACEHOLDER}\\[0.5cm]
{\fontsize{14pt}{18pt}\selectfont TITLE_EN_PLACEHOLDER}\\[3cm]
{\song\fontsize{14pt}{18pt}\selectfont
学\hspace{1em}院：COLLEGE_PLACEHOLDER\\
专\hspace{1em}业：MAJOR_PLACEHOLDER\\
姓\hspace{1em}名：AUTHOR_PLACEHOLDER\\
学\hspace{1em}号：STUDENT_ID_PLACEHOLDER\\
指导老师：SUPERVISOR_PLACEHOLDER\\[2cm]
DATE_PLACEHOLDER
\end{titlepage}
\newpage
\begin{center}
\hei\fontsize{16pt}{20pt}\selectfont 摘{}要
\end{center}
\vspace{18pt}
ABSTRACT_CN_PLACEHOLDER
\vspace{12pt}
\noindent{\bf\song\fontsize{12pt}{20pt}\selectfont 关键词：}KEYWORDS_CN_PLACEHOLDER
\newpage
\begin{center}
\fontsize{16pt}{20pt}\selectfont\bfseries ABSTRACT
\end{center}
\vspace{18pt}
ABSTRACT_EN_PLACEHOLDER
\vspace{12pt}
\noindent{\bfseries\fontsize{12pt}{20pt}\selectfont Key words: }KEYWORDS_EN_PLACEHOLDER
\newpage
\tableofcontents
BODY_CONTENT_PLACEHOLDER
REFERENCES_PLACEHOLDER
ACKNOWLEDGEMENTS_PLACEHOLDER
\end{document}
"""


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    replacements = {
        '\\': '\\textbackslash{}',
        '{': '\\{',
        '}': '\\}',
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _format_degree_type(degree: str) -> str:
    """Convert Chinese degree type to sjtuthesis class option."""
    mapping = {
        "学士": "bachelor",
        "硕士": "master",
        "博士": "doctor",
    }
    return mapping.get(degree, "bachelor")


def _render_acknowledgements(info: ThesisInfo) -> str:
    """Render acknowledgement section."""
    if not info.include_acknowledgements:
        return ""
    return (
        "\\newpage\n"
        "\\section*{致  谢}\n"
        "\\addcontentsline{toc}{section}{致  谢}\n\n"
        "（请在此处填写致谢内容）\n"
    )


def _render_references(info: ThesisInfo) -> str:
    """Render references section."""
    if info.references_raw:
        refs = [r.strip() for r in info.references_raw.split("\n") if r.strip()]
        lines = ["\\begin{thebibliography}{99}"]
        for ref in refs:
            lines.append(ref)
        lines.append("\\end{thebibliography}")
        return "\n".join(lines)
    return (
        "% \\begin{thebibliography}{99}\n"
        "% \\bibitem{...} ...\n"
        "% \\end{thebibliography}\n"
    )


def _render_body_content(info: ThesisInfo) -> str:
    """Parse and convert raw body content to LaTeX."""
    content = info.body_content.strip()
    if not content:
        return "% (请在此处粘贴您的论文正文内容)\n\\section*{绪论}\n请在此写入正文内容。\n"

    lines = content.split("\n")
    output_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            output_lines.append("")
            i += 1
            continue

        heading_level = _detect_latex_heading_level(stripped, info.numbering_system)
        if heading_level == 1:
            # Extract heading text
            text = _extract_heading_text(stripped, info.numbering_system)
            output_lines.append(f"\\section{{{text}}}")
        elif heading_level == 2:
            text = _extract_heading_text(stripped, info.numbering_system)
            output_lines.append(f"\\subsection{{{text}}}")
        elif heading_level == 3:
            text = _extract_heading_text(stripped, info.numbering_system)
            output_lines.append(f"\\subsubsection{{{text}}}")
        elif _is_latex_list_item(stripped):
            output_lines.append(f"\\begin{{itemize}}\n  \\item {stripped[2:].strip()}\n\\end{{itemize}}")
        else:
            output_lines.append(stripped + "\\\\")

        i += 1

    return "\n".join(output_lines)


def _detect_latex_heading_level(line: str, numbering_system: str) -> int:
    """Detect heading level for LaTeX output."""
    if numbering_system == "中文序号":
        if re.match(r"^[一二三四五六七八九十百千]+[、．]", line):
            return 1
        if re.match(r"^（[一二三四五六七八九十百千]+）", line):
            return 2
        if re.match(r"^\d+[、．]", line):
            return 3
    else:
        if re.match(r"^((第[一二三四五六七八九十百千]+章)|(\d+[\.．]))\s", line):
            return 1
        if re.match(r"^\d+[\.．]\d+\s", line):
            return 2
        if re.match(r"^\d+[\.．]\d+[\.．]\d+\s", line):
            return 3

    return 0


def _extract_heading_text(line: str, numbering_system: str) -> str:
    """Extract heading title text without numbering."""
    if numbering_system == "中文序号":
        # Remove "一、" type prefixes
        text = re.sub(r"^[一二三四五六七八九十百千]+[、．]\s*", "", line)
        text = re.sub(r"^（[一二三四五六七八九十百千]+）\s*", "", text)
    else:
        text = re.sub(r"^(第[一二三四五六七八九十百千]+章|[\d\.]+)[\s　]*", "", line)
    return text.strip()


def _is_latex_list_item(line: str) -> bool:
    """Detect list items."""
    return bool(re.match(r"^[\(（]?\d+[\)）]\s", line))


# ── Main render functions ──────────────────────────────────────────

def render_sjtuthesis_latex(info: ThesisInfo, output_path: Path) -> Path:
    """Generate LaTeX source compatible with SJTUThesis template.

    Args:
        info: Collected thesis metadata.
        output_path: Where to save the .tex file.

    Returns:
        Path to the generated .tex file.
    """
    degree = _format_degree_type(info.degree_type)
    date_str = datetime.now().strftime("%Y年%m月")

    body = _render_body_content(info)
    refs = _render_references(info)
    ack = _render_acknowledgements(info)

    content = SJTUTHESIS_PREAMBLE.format(
        degree_type=degree,
        title_cn=_escape_latex(info.title_cn),
        title_en=_escape_latex(info.title_en) if info.title_en else "TITLE",
        author=_escape_latex(info.author),
        date=date_str,
        keywords_cn=", ".join(info.keywords_cn) if info.keywords_cn else "关键词",
        keywords_en=", ".join(info.keywords_en) if info.keywords_en else "keywords",
        supervisor=_escape_latex(info.supervisor),
        abstract_cn=info.abstract_cn or "摘要内容（300-500字）",
        abstract_en=info.abstract_en or "ABSTRACT content",
        body_content=body,
        references=refs,
        acknowledgements=ack,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def render_standalone_latex(info: ThesisInfo, output_path: Path) -> Path:
    """Generate a self-contained LaTeX file (no SJTUThesis dependency).

    The standalone .tex applies all SJTU formatting manually via LaTeX packages.
    Uses string replacement to avoid Python .format() brace conflicts with LaTeX.
    """
    degree_label = info.get_degree_label()
    date_str = datetime.now().strftime("%Y年%m月")
    odd_header = _escape_latex(info.header_odd or info.title_cn[:20])
    even_header = _escape_latex(info.header_even or degree_label)

    body = _render_body_content(info)
    ack = _render_acknowledgements(info)

    # Render references as plain text for standalone
    ref_text = ""
    if info.references_raw:
        refs = [r.strip() for r in info.references_raw.split("\n") if r.strip()]
        ref_text = (
            "\\newpage\n"
            "\\section*{参考文献}\n"
            "\\addcontentsline{toc}{section}{参考文献}\n\n"
            + "\n\n".join(_escape_latex(r) for r in refs)
            + "\n"
        )

    replacements = {
        "EVEN_HEADER_PLACEHOLDER": even_header,
        "ODD_HEADER_PLACEHOLDER": odd_header,
        "DEGREE_LABEL_PLACEHOLDER": _escape_latex(info.degree_type),
        "TITLE_CN_PLACEHOLDER": _escape_latex(info.title_cn),
        "TITLE_EN_PLACEHOLDER": _escape_latex(info.title_en) if info.title_en else "TITLE",
        "COLLEGE_PLACEHOLDER": _escape_latex(info.college),
        "MAJOR_PLACEHOLDER": _escape_latex(info.major),
        "AUTHOR_PLACEHOLDER": _escape_latex(info.author),
        "STUDENT_ID_PLACEHOLDER": _escape_latex(info.student_id),
        "SUPERVISOR_PLACEHOLDER": _escape_latex(info.supervisor),
        "DATE_PLACEHOLDER": date_str,
        "ABSTRACT_CN_PLACEHOLDER": info.abstract_cn or "摘要内容（300-500字）",
        "ABSTRACT_EN_PLACEHOLDER": info.abstract_en or "ABSTRACT content",
        "KEYWORDS_CN_PLACEHOLDER": "，".join(info.keywords_cn) if info.keywords_cn else "关键词",
        "KEYWORDS_EN_PLACEHOLDER": ", ".join(info.keywords_en) if info.keywords_en else "keywords",
        "BODY_CONTENT_PLACEHOLDER": body,
        "REFERENCES_PLACEHOLDER": ref_text,
        "ACKNOWLEDGEMENTS_PLACEHOLDER": ack,
    }

    content = STANDALONE_PREAMBLE
    for key, value in replacements.items():
        content = content.replace(key, value)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def render_latex_from_json(json_path: Path, output_path: Path,
                           standalone: bool = False) -> Path:
    """Load ThesisInfo from JSON and render LaTeX.

    Args:
        json_path: Path to thesis_info.json
        output_path: Where to save .tex
        standalone: If True, generate self-contained .tex

    Returns:
        Path to generated .tex
    """
    info = ThesisInfo.load(json_path)
    if standalone:
        return render_standalone_latex(info, output_path)
    return render_sjtuthesis_latex(info, output_path)
