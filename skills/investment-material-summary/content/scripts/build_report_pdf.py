#!/usr/bin/env python3
"""
将 Markdown 投资分析报告转换为研报风格的 PDF。

样式特点：
- 二级、三级标题深蓝色加粗
- 正文 11pt，行高舒适
- 表格表头浅蓝背景
- 引用块浅灰背景 + 蓝色左边条
- 项目符号 • 优先

用法:
    python build_report_pdf.py input.md output.pdf

依赖:
    pip install weasyprint markdown
"""
import sys
import re
from pathlib import Path

import mistune
from weasyprint import HTML, CSS

# 主色（与截图深蓝接近）
PRIMARY_COLOR = "#1F4E79"
HEADER_BG = "#D9E2F3"
BORDER_COLOR = "#BFBFBF"
QUOTE_BG = "#F2F2F2"

CSS_TEMPLATE = """
@page {
    size: A4;
    margin: 2.2cm 2.0cm 2.2cm 2.0cm;
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-family: "Noto Sans CJK SC", sans-serif;
        font-size: 9pt;
        color: #888;
    }
}

* {
    box-sizing: border-box;
}

body {
    font-family: "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #222;
    margin: 0;
}

/* 一级标题 - 报告标题 */
h1 {
    font-size: 20pt;
    font-weight: 700;
    color: #000;
    text-align: center;
    margin: 0 0 0.6em 0;
    padding-bottom: 0.4em;
    border-bottom: 2px solid PRIMARY_COLOR_PLACEHOLDER;
}

/* 二级标题 - 章 */
h2 {
    font-size: 16pt;
    font-weight: 700;
    color: PRIMARY_COLOR_PLACEHOLDER;
    margin: 1.4em 0 0.6em 0;
    padding-bottom: 0.2em;
    page-break-after: avoid;
}

/* 三级标题 - 节 */
h3 {
    font-size: 13pt;
    font-weight: 700;
    color: PRIMARY_COLOR_PLACEHOLDER;
    margin: 1.1em 0 0.4em 0;
    page-break-after: avoid;
}

/* 四级标题 - 小节 */
h4 {
    font-size: 11.5pt;
    font-weight: 700;
    color: PRIMARY_COLOR_PLACEHOLDER;
    margin: 0.9em 0 0.3em 0;
    page-break-after: avoid;
}

/* 段落 */
p {
    margin: 0.4em 0;
    text-align: justify;
}

/* 项目符号 */
ul {
    margin: 0.4em 0;
    padding-left: 1.4em;
}
ul li {
    margin: 0.3em 0;
    line-height: 1.65;
}
ul li::marker {
    color: PRIMARY_COLOR_PLACEHOLDER;
}
/* 嵌套 ul 进一步缩进，使用空心圆圈做次级标记 */
ul ul {
    margin: 0.25em 0 0.25em 0;
    padding-left: 1.4em;
    list-style-type: circle;
}
ul ul li::marker {
    color: #6B8AB8;
}
ul ul ul {
    list-style-type: square;
}

/* 编号列表 */
ol {
    margin: 0.4em 0;
    padding-left: 1.6em;
}
ol li {
    margin: 0.4em 0;
    line-height: 1.65;
}
ol li::marker {
    color: PRIMARY_COLOR_PLACEHOLDER;
    font-weight: 700;
}

/* 强调 */
strong {
    font-weight: 700;
    color: #111;
}
em {
    font-style: italic;
}

/* 引用块 */
blockquote {
    background: QUOTE_BG_PLACEHOLDER;
    border-left: 3px solid PRIMARY_COLOR_PLACEHOLDER;
    margin: 0.7em 0;
    padding: 0.5em 0.9em;
    color: #444;
    font-size: 10.5pt;
}
blockquote p {
    margin: 0.2em 0;
}

/* 分隔线 */
hr {
    border: 0;
    border-top: 1px solid #E0E0E0;
    margin: 1.2em 0;
}

/* 表格 */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.7em 0;
    font-size: 10.5pt;
    page-break-inside: avoid;
}
th {
    background: HEADER_BG_PLACEHOLDER;
    color: #111;
    font-weight: 700;
    text-align: left;
    padding: 0.5em 0.7em;
    border: 1px solid BORDER_COLOR_PLACEHOLDER;
}
td {
    padding: 0.5em 0.7em;
    border: 1px solid BORDER_COLOR_PLACEHOLDER;
    vertical-align: top;
    line-height: 1.55;
}
tr:nth-child(even) td {
    background: #FAFBFC;
}

/* 内联代码 */
code {
    font-family: "Source Code Pro", monospace;
    background: #F5F5F5;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 0.9em;
}

/* 报告说明部分（首个 ul 紧跟 h2[报告说明]） */
.report-meta {
    background: #F8F9FB;
    border-left: 3px solid PRIMARY_COLOR_PLACEHOLDER;
    padding: 0.6em 1em;
    margin: 0.5em 0 1em 0;
}
.report-meta ul {
    margin: 0;
    padding-left: 1.3em;
}
"""

CSS_FINAL = (
    CSS_TEMPLATE
    .replace("PRIMARY_COLOR_PLACEHOLDER", PRIMARY_COLOR)
    .replace("HEADER_BG_PLACEHOLDER", HEADER_BG)
    .replace("BORDER_COLOR_PLACEHOLDER", BORDER_COLOR)
    .replace("QUOTE_BG_PLACEHOLDER", QUOTE_BG)
)


def md_to_pdf(md_path: str, pdf_path: str):
    md_text = Path(md_path).read_text(encoding="utf-8")

    # 使用 mistune（支持 2 空格嵌套列表 + 表格）
    md_renderer = mistune.create_markdown(
        plugins=["table", "strikethrough", "footnotes"],
    )
    html_body = md_renderer(md_text)

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Report</title></head>
<body>
{html_body}
</body></html>
"""

    HTML(string=full_html).write_pdf(
        pdf_path,
        stylesheets=[CSS(string=CSS_FINAL)],
    )
    print(f"PDF generated: {pdf_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python build_report_pdf.py input.md output.pdf")
        sys.exit(1)
    md_to_pdf(sys.argv[1], sys.argv[2])
