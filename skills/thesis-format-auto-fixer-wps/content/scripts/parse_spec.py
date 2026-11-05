#!/usr/bin/env python3
"""
格式规范文档解析器
支持输入：docx / pdf / markdown / txt
输出：结构化 JSON 规范字典
用法：python parse_spec.py <规范文档路径> <输出.json>
"""

import sys
import re
import json
from pathlib import Path


# ─────────────────────────────────────────────
# 文本提取
# ─────────────────────────────────────────────

def extract_text_from_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text_from_pdf(path: str) -> str:
    """
    尝试使用 pdfminer 提取，失败则返回提示。
    调用方可先通过 extract_pdfs_full_content 工具获取文本。
    """
    try:
        from pdfminer.high_level import extract_text
        return extract_text(path)
    except ImportError:
        # pdfminer 未安装，返回空字符串，由调用方通过工具填充
        return ''


def extract_text_from_md(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def extract_text(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext in ('.docx', '.doc'):
        return extract_text_from_docx(path)
    elif ext == '.pdf':
        return extract_text_from_pdf(path)
    elif ext in ('.md', '.txt'):
        return extract_text_from_md(path)
    else:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()


# ─────────────────────────────────────────────
# 规范提取
# ─────────────────────────────────────────────

def parse_number(text: str, default=None):
    """从文本中提取第一个数字"""
    m = re.search(r'(\d+\.?\d*)', text)
    return float(m.group(1)) if m else default


def parse_spec(text: str) -> dict:
    """
    从规范文本中提取格式参数，返回结构化字典
    采用关键词匹配 + 正则提取的启发式方法
    """
    spec = {
        'paper_size': 'A4',
        'page_margins': {'top': 2.5, 'bottom': 2.5, 'left': 3.0, 'right': 2.5, 'gutter': 0},
        'body': {
            'font': '宋体', 'size': 12, 'bold': False, 'italic': False,
            'line_spacing': 23, 'line_spacing_rule': 'fixed',
            'space_before': 0, 'space_after': 0,
            'first_line_indent': 0.85,
            'alignment': 'justify'
        },
        'heading_1': {'font': '黑体', 'size': 16, 'bold': True, 'space_before': 12, 'space_after': 6},
        'heading_2': {'font': '黑体', 'size': 14, 'bold': True, 'space_before': 10, 'space_after': 4},
        'heading_3': {'font': '黑体', 'size': 12, 'bold': True, 'space_before': 6, 'space_after': 3},
        'heading_4': {'font': '宋体', 'size': 12, 'bold': True, 'space_before': 3, 'space_after': 0},
        'abstract': {'font': '宋体', 'size': 12},
        'keywords': {'font': '宋体', 'size': 12, 'bold': False},
        'toc': {'font': '宋体', 'size': 12},
        'figures': {'numbering': '图{chapter}-{seq}', 'font': '宋体', 'size': 10.5, 'position': 'below'},
        'tables': {'numbering': '表{chapter}-{seq}', 'font': '宋体', 'size': 10.5, 'position': 'above'},
        'references': {
            'standard': 'GB/T 7714',
            'font': '宋体', 'size': 10.5,
            'line_spacing': 20, 'line_spacing_rule': 'fixed',
            'left_indent': 0, 'hanging_indent': 0.75
        },
        'page_header': {'content': '毕业论文', 'font': '宋体', 'size': 10.5},
        'page_footer': {
            'cover': 'none',
            'abstract': 'roman',
            'body': 'arabic',
            'position': 'center'
        },
        'raw_notes': []  # 无法结构化的原始要求
    }

    lines = text.split('\n')

    for i, line in enumerate(lines):
        line_s = line.strip()
        if not line_s:
            continue

        # ── 纸张大小 ──
        if '纸张' in line_s or 'paper' in line_s.lower():
            if 'A4' in line_s or 'a4' in line_s:
                spec['paper_size'] = 'A4'
            elif 'B5' in line_s or 'b5' in line_s:
                spec['paper_size'] = 'B5'

        # ── 页边距 ──
        margin_keys = {'上': 'top', '下': 'bottom', '左': 'left', '右': 'right', '装订线': 'gutter'}
        for cn, en in margin_keys.items():
            if cn in line_s and ('边距' in line_s or '页边' in line_s or cn == '装订线'):
                val = parse_number(line_s)
                if val:
                    spec['page_margins'][en] = val

        # ── 正文字体 ──
        if '正文' in line_s and ('字体' in line_s or '字号' in line_s):
            for font in ['宋体', '仿宋', '楷体', 'Times New Roman', 'Arial']:
                if font in line_s:
                    spec['body']['font'] = font
            for size_word, pt in [('小四', 12), ('四号', 14), ('五号', 10.5), ('小三', 15), ('三号', 16)]:
                if size_word in line_s:
                    spec['body']['size'] = pt

        # ── 行距 ──
        if '行距' in line_s:
            for kw, pt in [('1.5倍', 1.5), ('双倍', 2.0), ('固定值', None)]:
                if kw in line_s:
                    if kw == '固定值':
                        val = parse_number(line_s.split('固定值')[-1])
                        if val:
                            spec['body']['line_spacing'] = val
                            spec['body']['line_spacing_rule'] = 'fixed'
                    else:
                        spec['body']['line_spacing'] = pt
                        spec['body']['line_spacing_rule'] = 'multiple'

        # ── 图表编号规则 ──
        if '图' in line_s and '编号' in line_s:
            if re.search(r'图\d+-\d+', line_s):
                spec['figures']['numbering'] = '图{chapter}-{seq}'
            elif re.search(r'图\d+', line_s):
                spec['figures']['numbering'] = '图{seq}'
        if '表' in line_s and '编号' in line_s:
            if re.search(r'表\d+-\d+', line_s):
                spec['tables']['numbering'] = '表{chapter}-{seq}'

        # ── 参考文献标准 ──
        if 'GB/T' in line_s or 'gbt' in line_s.lower():
            m = re.search(r'GB/T\s*\d+', line_s)
            if m:
                spec['references']['standard'] = m.group()

        # ── 页眉 ──
        if '页眉' in line_s:
            spec['raw_notes'].append(f'页眉要求: {line_s}')

        # ── 收集无法结构化的特殊要求 ──
        if any(kw in line_s for kw in ['要求', '规定', '必须', '应', '需', '不得', '禁止']):
            if len(line_s) > 10:
                spec['raw_notes'].append(line_s)

    return spec


# ─────────────────────────────────────────────
# 命令行入口
# ─────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('用法: python parse_spec.py <规范文档> <输出.json>')
        sys.exit(1)

    spec_path = sys.argv[1]
    output_json = sys.argv[2]

    text = extract_text(spec_path)
    spec = parse_spec(text)

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    print(f'✅ 规范解析完成：{output_json}')
    print(f'   共提取 {len(spec)} 个顶级配置项，{len(spec.get("raw_notes", []))} 条原始备注')
