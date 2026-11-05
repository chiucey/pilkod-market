#!/usr/bin/env python3
"""
BD分析报告 MD → HTML 转换脚本

使用 python-markdown 库将MD报告转换为带样式的HTML文件。
支持表格、代码块、列表、blockquote等完整Markdown语法。

用法：
    python scripts/md2html.py --input report.md --output report.html --enterprise "企业名" --phase "Phase X"
"""

import argparse
import json
import os
import re
import sys

import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<style>
:root {{--bg:#ffffff;--bg2:#f7f8fa;--text:#1a1a2e;--text2:#555;--accent:#2563eb;--accent2:#1d4ed8;--border:#e5e7eb;--ai-bg:#eff6ff;--ai-border:#2563eb}}
* {{margin:0;padding:0;box-sizing:border-box}}
body {{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;background:var(--bg);color:var(--text);line-height:1.7;max-width:1100px;margin:0 auto;padding:0}}
.header {{background:linear-gradient(135deg,#1a1a2e,#2d2d44);color:#fff;padding:48px 40px 36px;position:relative}}
.header h1 {{font-size:28px;font-weight:600;margin-bottom:12px}}
.header h1 span {{color:#93c5fd}}
.header .meta {{font-size:14px;color:#94a3b8;margin-top:8px}}
.badge {{display:inline-block;background:var(--accent);color:#fff;padding:4px 14px;border-radius:20px;font-size:13px;font-weight:500;margin-bottom:16px}}
.content {{padding:28px 40px}}
.content h2 {{font-size:22px;font-weight:600;color:var(--text);margin:32px 0 18px;padding-bottom:10px;border-bottom:2px solid var(--accent)}}
.content h3 {{font-size:17px;font-weight:600;color:var(--text);margin:24px 0 10px}}
.content h4 {{font-size:15px;font-weight:600;color:var(--text2);margin:18px 0 8px}}
.content p {{margin:8px 0;color:var(--text2);font-size:15px}}
.content ul,.content ol {{margin:8px 0 8px 24px;color:var(--text2);font-size:15px}}
.content li {{margin:4px 0}}
.content ul li {{list-style-type:disc}}
.content ol li {{list-style-type:decimal}}
table {{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px}}
thead {{background:var(--bg2)}}
thead th {{padding:10px 12px;text-align:left;font-weight:500;font-size:12px;color:var(--text2);border-bottom:2px solid var(--border)}}
tbody td {{padding:9px 12px;border-bottom:1px solid var(--border);color:var(--text2)}}
tbody td:first-child {{font-weight:500;color:var(--text)}}
tbody tr:hover {{background:rgba(37,99,235,.02)}}
strong {{color:var(--text);font-weight:600}}
em {{font-style:italic;color:var(--text2)}}
blockquote {{border-left:3px solid var(--accent);padding:10px 16px;margin:12px 0;background:var(--ai-bg);color:var(--text2);font-size:14px;border-radius:0 4px 4px 0}}
blockquote p {{margin:4px 0}}
hr {{border:none;border-top:1px solid var(--border);margin:24px 0}}
pre {{background:#1e293b;color:#e2e8f0;padding:16px 20px;border-radius:8px;font-size:13px;line-height:1.6;overflow-x:auto;margin:14px 0}}
pre code {{background:none;color:inherit;padding:0;font-size:inherit}}
code {{font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:13px;background:var(--bg2);padding:2px 6px;border-radius:3px;color:var(--accent)}}
.footer {{background:var(--bg2);padding:20px 40px;text-align:center;font-size:12px;color:#999;border-top:1px solid var(--border)}}
@media(max-width:768px) {{.header{{padding:28px 20px}}.content{{padding:20px}}.header h1{{font-size:22px}}table{{font-size:12px}}}}
</style>
</head>
<body>
{header}
<div class="content">
{body}
</div>
{footer}
</body>
</html>"""


def md_to_html(md_content: str, enterprise: str, phase: str) -> str:
    """
    使用 python-markdown 库将MD内容转换为带样式的HTML。

    Args:
        md_content: 完整的MD报告文本
        enterprise: 企业名称
        phase: Phase标签（如 "Phase 4"）

    Returns:
        完整的HTML字符串
    """
    # 提取分析日期
    date_match = re.search(r'\*\*分析日期\*\*:\s*(\d{4}-\d{2}-\d{2})', md_content)
    date_str = date_match.group(1) if date_match else "YYYY-MM-DD"

    # 构建HTML header
    header_html = f"""<div class="header">
<div class="badge">BD Analysis / {phase}</div>
<h1>企业BD分析范例：<span>{enterprise}</span></h1>
<div class="meta">分析日期：{date_str} </div>
</div>"""

    # 构建HTML footer
    footer_html = """<div class="footer">本报告基于行业细分画像评分及输出标准完成 · 仅供BD决策参考</div>"""

    # 预处理MD内容：去掉顶部标题和meta行（已在HTML header中呈现）
    lines = md_content.split('\n')
    filtered_lines = []
    skip_meta = False

    for line in lines:
        # 跳过顶级标题行
        if line.startswith('# ') and not line.startswith('## '):
            skip_meta = True
            continue
        # 跳过meta行
        if skip_meta and (line.startswith('> **分析日期**') or line.startswith('> **分析师**')):
            continue
        # 跳过标题后的分隔线
        if skip_meta and line.strip() == '---':
            skip_meta = False
            continue
        skip_meta = False
        filtered_lines.append(line)

    body_md = '\n'.join(filtered_lines)

    # 使用 python-markdown 转换，启用扩展
    md_converter = markdown.Markdown(
        extensions=[
            'tables',           # 表格支持
            'fenced_code',      # 代码块支持
            'toc',              # 目录支持
            'nl2br',            # 换行转<br>
            'sane_lists',       # 更好的列表解析
        ],
        extension_configs={
            'toc': {'title': ''},
        }
    )
    body_html = md_converter.convert(body_md)

    # 组装完整HTML
    title = f"企业BD分析范例：{enterprise}（{phase}）"
    return HTML_TEMPLATE.format(title=title, header=header_html, body=body_html, footer=footer_html)


def main():
    parser = argparse.ArgumentParser(description='将BD分析报告MD文件转换为HTML')
    parser.add_argument('--input', required=True, help='输入的MD文件路径')
    parser.add_argument('--output', required=True, help='输出的HTML文件路径')
    parser.add_argument('--enterprise', required=True, help='企业名称')
    parser.add_argument('--phase', required=True, help='Phase标签（如 Phase 4）')
    args = parser.parse_args()

    try:
        # 读取MD文件（确保UTF-8编码）
        with open(args.input, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 转换为HTML
        html = md_to_html(md_content, args.enterprise, args.phase)

        # 写入HTML文件（确保UTF-8编码）
        out_dir = os.path.dirname(os.path.abspath(args.output))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8', newline='') as f:
            f.write(html)

        result = {
            "status": "success",
            "input": args.input,
            "output": args.output,
            "enterprise": args.enterprise,
            "phase": args.phase,
            "md_size": len(md_content.encode("utf-8")),
            "html_size": len(html.encode("utf-8")),
        }
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        result = {"status": "error", "message": str(e)}
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
