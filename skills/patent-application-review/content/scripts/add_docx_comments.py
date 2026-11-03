#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为Word文档(.docx)添加批注(Comments)。
用法: python add_docx_comments.py <input.docx> <output.docx> [comments.json]

通过JSON传入批注列表，每个批注包含:
  - target_text: 要在文档中定位的原文片段
  - comment_text: 批注内容
  - severity: 严重程度 (严重/一般/建议)

不修改原文任何内容，仅在对应位置插入Word批注。
"""

import sys
import json
from datetime import datetime
from docx import Document
from docx.oxml.ns import qn
from docx.opc.part import Part
from docx.opc.packuri import PackURI
from lxml import etree


# ── Comments Part ──────────────────────────────────────────────────────

class CommentsPart(Part):
    """自定义 Comments Part，blob 从缓存的 XML element 按需序列化。"""

    def __init__(self, partname, content_type, element, package):
        blob = etree.tostring(element, xml_declaration=True,
                              encoding='UTF-8', standalone=True)
        super().__init__(partname, content_type, blob, package)
        self._comments_el = element

    @property
    def blob(self):
        return etree.tostring(self._comments_el, xml_declaration=True,
                              encoding='UTF-8', standalone=True)


# ── Constants ──────────────────────────────────────────────────────────

COMMENTS_XML_TEMPLATE = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
    '</w:comments>'
)
COMMENTS_CT = 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml'

# 全局缓存：part_name → comments element（避免每次 getter 重新解析）
_comments_cache = {}


# ── Text search ────────────────────────────────────────────────────────

def find_paragraph_with_text(doc, target_text):
    """在文档中查找包含目标文本的段落。
    返回 (paragraph, run_index, char_offset) 或 None。
    """
    for para in doc.paragraphs:
        full_text = para.text
        if target_text not in full_text:
            continue
        target_start = full_text.index(target_text)
        offset = 0
        for i, run in enumerate(para.runs):
            run_len = len(run.text)
            if offset <= target_start < offset + run_len:
                return para, i, target_start - offset
            offset += run_len
        # Fallback: run 文本拼接与段落文本不一致时
        if para.runs:
            return para, 0, 0
    return None


# ── Comments part management ──────────────────────────────────────────

def ensure_comments_part(doc):
    """确保文档有 comments part，返回可修改的 comments element（带缓存）。"""
    from docx.opc.constants import RELATIONSHIP_TYPE as RT

    main_part = doc.part

    for rel in main_part.rels.values():
        if 'comments' in rel.reltype:
            part = rel.target_part
            part_name = str(part.partname)
            if part_name in _comments_cache:
                return _comments_cache[part_name]
            el = etree.fromstring(part.blob)
            _comments_cache[part_name] = el
            return el

    # 创建新的 comments part
    comments_el = etree.fromstring(COMMENTS_XML_TEMPLATE.encode('utf-8'))
    comments_uri = PackURI('/word/comments.xml')
    comments_part = CommentsPart(comments_uri, COMMENTS_CT,
                                 comments_el, main_part.package)
    main_part.relate_to(comments_part, RT.COMMENTS)
    _comments_cache[str(comments_uri)] = comments_el
    return comments_el


def flush_comments(doc):
    """将缓存的 comments element 写回 part 的 blob（保存前调用）。"""
    from docx.opc.constants import RELATIONSHIP_TYPE as RT

    main_part = doc.part
    for rel in main_part.rels.values():
        if 'comments' in rel.reltype:
            part = rel.target_part
            part_name = str(part.partname)
            if part_name in _comments_cache:
                if not isinstance(part, CommentsPart):
                    el = _comments_cache[part_name]
                    part._blob = etree.tostring(
                        el, xml_declaration=True,
                        encoding='UTF-8', standalone=True)
    _comments_cache.clear()


# ── Comment building blocks ───────────────────────────────────────────

def get_next_comment_id(comments_el):
    existing = [int(c.get(qn('w:id'), 0))
                for c in comments_el.findall(qn('w:comment'))]
    return max(existing) + 1 if existing else 1


def make_comment(comments_el, cid, text, author, initial, date_str):
    """在 comments element 中追加一条 w:comment。"""
    c = etree.SubElement(comments_el, qn('w:comment'))
    c.set(qn('w:id'), str(cid))
    c.set(qn('w:author'), author)
    c.set(qn('w:initials'), initial)
    c.set(qn('w:date'), date_str)

    p = etree.SubElement(c, qn('w:p'))
    r = etree.SubElement(p, qn('w:r'))
    t = etree.SubElement(r, qn('w:t'))
    t.text = text
    t.set(qn('xml:space'), 'preserve')


def insert_markers(run_el, cid, position):
    """在 run element 内插入 commentRangeStart / End / Reference。"""
    cid_s = str(cid)
    rs = etree.Element(qn('w:commentRangeStart'))
    rs.set(qn('w:id'), cid_s)
    re_ = etree.Element(qn('w:commentRangeEnd'))
    re_.set(qn('w:id'), cid_s)

    ref_run = etree.Element(qn('w:r'))
    rpr = etree.SubElement(ref_run, qn('w:rPr'))
    rs_style = etree.SubElement(rpr, qn('w:rStyle'))
    rs_style.set(qn('w:val'), 'CommentReference')
    cr = etree.SubElement(ref_run, qn('w:commentReference'))
    cr.set(qn('w:id'), cid_s)

    if position == 'start':
        run_el.insert(0, rs)
        run_el.append(re_)
        run_el.append(ref_run)
    else:
        run_el.append(rs)
        run_el.append(re_)
        run_el.append(ref_run)


# ── Core: add one comment ─────────────────────────────────────────────

def add_comment(doc, target_text, comment_text,
                author="专利校核", initial="校核", date_str=None):
    """在文档中找到 target_text 并添加 Word 批注。不修改原文。
    返回 True 成功 / False 未找到目标文本。
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    result = find_paragraph_with_text(doc, target_text)
    if result is None:
        print(f"  [WARN] 未找到目标文本: '{target_text[:60]}'")
        return False

    para, run_idx, char_offset = result
    comments_el = ensure_comments_part(doc)
    cid = get_next_comment_id(comments_el)

    # 1) 在 comments part 中创建批注内容
    make_comment(comments_el, cid, comment_text, author, initial, date_str)

    # 2) 在文档段落的 target run 中插入标记
    run_el = para.runs[run_idx]._element
    t_elements = run_el.findall(qn('w:t'))
    if not t_elements:
        print(f"  [WARN] Run 无文本元素")
        return False

    t_el = t_elements[0]
    orig_text = t_el.text or ''

    if 0 < char_offset < len(orig_text):
        # 在 char_offset 处拆分 w:t
        t_el.text = orig_text[:char_offset]
        t_after = etree.SubElement(run_el, qn('w:t'))
        t_after.text = orig_text[char_offset:]
        t_after.set(qn('xml:space'), 'preserve')

        t_after_idx = list(run_el).index(t_after)
        rs = etree.Element(qn('w:commentRangeStart'))
        rs.set(qn('w:id'), str(cid))
        run_el.insert(t_after_idx, rs)

        re_ = etree.Element(qn('w:commentRangeEnd'))
        re_.set(qn('w:id'), str(cid))
        run_el.insert(t_after_idx + 2, re_)

        ref_run = etree.Element(qn('w:r'))
        rpr = etree.SubElement(ref_run, qn('w:rPr'))
        etree.SubElement(rpr, qn('w:rStyle')).set(qn('w:val'), 'CommentReference')
        cr = etree.SubElement(ref_run, qn('w:commentReference'))
        cr.set(qn('w:id'), str(cid))
        run_el.insert(t_after_idx + 3, ref_run)
    else:
        insert_markers(run_el, cid, 'start' if char_offset == 0 else 'end')

    print(f"  [OK] 批注 #{cid}: '{target_text[:50]}'")
    return True


# ── CLI entry point ───────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("用法: python add_docx_comments.py <input.docx> <output.docx> [comments.json]")
        print()
        print("comments.json 格式:")
        print('[{"target_text": "...", "comment_text": "...", "severity": "一般"}]')
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if len(sys.argv) >= 4:
        with open(sys.argv[3], 'r', encoding='utf-8') as f:
            comments = json.load(f)
    else:
        comments = json.loads(sys.stdin.read())

    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"批注数量: {len(comments)}")
    print()

    doc = Document(input_path)
    ok = fail = 0

    for i, cmt in enumerate(comments, 1):
        target = cmt.get('target_text', '')
        text = cmt.get('comment_text', '')
        severity = cmt.get('severity', '')
        prefix = f"[{severity}] " if severity else ""

        print(f"[{i}/{len(comments)}] 添加批注...")
        if add_comment(doc, target, prefix + text):
            ok += 1
        else:
            fail += 1

    flush_comments(doc)
    doc.save(output_path)
    print(f"\n完成: 成功 {ok}, 失败 {fail}")
    print(f"已保存至: {output_path}")


if __name__ == '__main__':
    main()
