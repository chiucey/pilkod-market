#!/usr/bin/env python3
"""
import_book.py - 导入书籍到本地知识库（增强版，无LLM调用）
用法: python3 import_book.py <文件路径> [书名]

功能：
1. 读取文件并按章节切分
2. 生成 index.json（每章摘要索引）
3. 生成 toc.md（目录）
4. 生成 metadata.json（元数据）
"""

import sys
import os
import json
import re
import argparse
import time
import zipfile
import html
from pathlib import Path
from html.parser import HTMLParser

def get_book_name(file_path: str, provided_name: str = None) -> str:
    """从文件名或提供名称生成规范书名"""
    if provided_name:
        return provided_name.strip().replace('/', '-').replace('\\', '-')
    name = os.path.splitext(os.path.basename(file_path))[0]
    name = re.sub(r'[_-](pdf|epub|mobi|txt|azw3|完整版|全集)$', '', name, flags=re.I)
    return name.strip()

def extract_chapters_pdf(file_path: str) -> list:
    """使用 pymupdf 提取 PDF 文字并按章节切分"""
    try:
        import fitz
    except ImportError:
        # 尝试 /tmp/pymupdf_install
        sys.path.insert(0, '/tmp/pymupdf_install')
        import fitz

    chapters = []
    doc = fitz.open(file_path)
    current = {"title": "序言", "content": ""}
    chapter_patterns = [
        r'^第[一二三四五六七八九十百千零\d]+[章节篇部卷辑]',
        r'^Chapter\s+\d+',
        r'^第[一二三四五六七八九十百千零\d]+篇',
        r'^[一二三四五六七八九十百千零\d]+[、\.]\s*\S',
    ]

    print(f"正在处理 {len(doc)} 页...", flush=True)
    for page_num, page in enumerate(doc):
        if page_num % 500 == 0:
            print(f"  处理到第 {page_num+1}/{len(doc)} 页...", flush=True)
        text = page.get_text("text")
        if not text.strip():
            continue

        lines = text.strip().split('\n')
        is_chapter = False
        first_line = lines[0].strip() if lines else ""
        
        for pattern in chapter_patterns:
            if re.match(pattern, first_line[:30]):
                is_chapter = True
                break

        # 页码独占一行 + 后续有大段文字 = 新章节
        if len(lines) > 3 and re.match(r'^\d+$', first_line) and len(first_line) < 5:
            is_chapter = True

        if is_chapter and len(text.strip()) < 300:
            if current["content"].strip():
                chapters.append(current)
            current = {"title": first_line[:60], "content": ""}
            if len(lines) > 1 and len(lines[1].strip()) < 100:
                current["content"] = '\n'.join(lines[2:]) if len(lines) > 2 else ""
        else:
            current["content"] += "\n" + text

    if current["content"].strip():
        chapters.append(current)

    doc.close()
    print(f"检测到 {len(chapters)} 个章节", flush=True)
    return chapters

class _EpubTextExtractor(HTMLParser):
    """EPUB专用HTML解析器"""
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_depth = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'nav'):
            self.skip_depth += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav'):
            self.skip_depth = max(0, self.skip_depth - 1)
    def handle_data(self, data):
        if self.skip_depth == 0:
            self.text_parts.append(data)

def _extract_epub_text(raw_html: str) -> str:
    """从HTML中提取纯文本"""
    text = re.sub(r'<script[^>]*>.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL | re.IGNORECASE)
    p = _EpubTextExtractor()
    try:
        p.feed(text)
    except:
        pass
    text = ''.join(p.text_parts)
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def _get_epub_heading(raw_html: str) -> str:
    """从HTML中提取章节标题"""
    for tag in ['h1', 'h2', 'h3']:
        m = re.search(f'<{tag}[^>]*>(.*?)</{tag}>', raw_html, re.DOTALL)
        if m:
            t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            t = html.unescape(t)
            if t:
                return t
    m = re.search(r'<title[^>]*>(.*?)</title>', raw_html, re.IGNORECASE)
    if m:
        t = re.sub(r'<[^>]+>', '', m.group(1)).strip()[:60]
        t = html.unescape(t).replace('&amp;', '&')
        if t:
            return t
    return None

def extract_chapters_epub(file_path: str) -> list:
    """提取 EPUB 文字并按章节切分"""
    SKIP_KEYWORDS = {'toc', 'cover', 'nav', '版权', '目录', 'contents', 'titlepage'}
    chapters = []

    with zipfile.ZipFile(file_path, 'r') as z:
        html_files = sorted([
            n for n in z.namelist()
            if re.search(r'\.xhtml?$', n)
        ])
        print(f"  EPUB共 {len(html_files)} 个HTML文件", flush=True)

        for i, f in enumerate(html_files):
            fname_lower = f.lower()
            if any(k in fname_lower for k in SKIP_KEYWORDS):
                continue

            raw = z.read(f).decode('utf-8', errors='replace')
            heading = _get_epub_heading(raw)
            text = _extract_epub_text(raw)

            if heading in (None, '模型思维', '模型思维：24种让人终身受益的思维模型'):
                if len(text) < 200:
                    continue
                heading = f"第{i+1}节"

            heading = re.sub(r'\s+', ' ', heading).strip()[:60]

            chapters.append({
                "title": heading,
                "content": text
            })
            print(f"  [{len(chapters):02d}] {heading[:45]}: {len(text)}字", flush=True)

    print(f"  → 有效章节 {len(chapters)} 个", flush=True)
    return chapters

def extract_chapters_txt(file_path: str) -> list:
    """导入纯文本文件，按章节标记切分"""
    chapters = []
    current = {"title": "前言", "content": ""}
    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")

    chapter_patterns = [
        r'^第[一二三四五六七八九十百千零\d]+[章节篇部卷辑]',
        r'^Chapter\s+\d+',
        r'^[一二三四五六七八九十百千零\d]+[、\.]\s*\S',
    ]

    lines = content.split('\n')
    for line in lines:
        is_chapter = any(re.match(p, line.strip()[:30]) for p in chapter_patterns)
        if is_chapter and len(line.strip()) < 60:
            if current["content"].strip():
                chapters.append(current)
            current = {"title": line.strip()[:60], "content": ""}
        else:
            current["content"] += "\n" + line

    if current["content"].strip():
        chapters.append(current)

    return chapters

def save_chapters(chapters: list, book_dir: Path) -> list:
    """保存章节文件，返回章节元数据"""
    chapter_list = []
    for i, ch in enumerate(chapters):
        filename = f"chapter_{i+1:03d}.md"
        filepath = book_dir / filename
        filepath.write_text(f"# {ch['title']}\n\n{ch['content'].strip()}", encoding="utf-8")
        chapter_list.append({
            "id": i + 1,
            "title": ch["title"],
            "file": filename,
            "summary": ""  # 稍后由AI填写
        })
        if (i + 1) % 50 == 0:
            print(f"  已保存 {i+1}/{len(chapters)} 章...", flush=True)
    return chapter_list

def main():
    parser = argparse.ArgumentParser(description="导入书籍到本地知识库")
    parser.add_argument("file_path", help="书籍文件路径")
    parser.add_argument("book_name", nargs="?", help="书籍名称（可选）")
    args = parser.parse_args()

    file_path = args.file_path
    if not os.path.exists(file_path):
        print(f"ERROR: 文件不存在: {file_path}")
        sys.exit(1)

    book_name = get_book_name(file_path, args.book_name)
    library_dir = Path("/workspace/library")
    book_dir = library_dir / book_name

    if book_dir.exists():
        print(f"INFO: 书籍已存在: {book_name}")
        print(f"  如需重新导入，请先删除: rm -rf {book_dir}")
        sys.exit(0)

    book_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file_path)[1].lower()
    print(f"正在提取文本（{ext}）...", flush=True)
    if ext == ".pdf":
        chapters = extract_chapters_pdf(file_path)
    elif ext in [".txt", ".md"]:
        chapters = extract_chapters_txt(file_path)
    elif ext in [".epub"]:
        chapters = extract_chapters_epub(file_path)
    else:
        print(f"ERROR: 暂不支持格式: {ext}，支持: .pdf, .txt, .md, .epub")
        sys.exit(1)

    if not chapters:
        print("WARNING: 未检测到章节，内容可能较少")
        chapters = [{"title": "全文", "content": Path(file_path).read_text(errors="ignore")}]

    print(f"正在保存 {len(chapters)} 个章节...", flush=True)
    chapter_list = save_chapters(chapters, book_dir)

    # 保存 index.json（核心文件）
    index_data = {"chapters": chapter_list}
    (book_dir / "index.json").write_text(
        json.dumps(index_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # 生成 toc.md
    toc_content = f"# {book_name} - 目录\n\n共 {len(chapters)} 章\n\n"
    for ch in chapter_list:
        toc_content += f"- [第{ch['id']}章：{ch['title']}]({ch['file']})\n"
    (book_dir / "toc.md").write_text(toc_content, encoding="utf-8")

    # 生成 metadata.json
    metadata = {
        "name": book_name,
        "source": file_path,
        "imported": time.strftime("%Y-%m-%d %H:%M:%S"),
        "chapters": len(chapters),
        "format": ext.lstrip("."),
        "version": "route_b_no_llm"
    }
    (book_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n✅ 导入成功！")
    print(f"   书名: {book_name}")
    print(f"   章节: {len(chapters)} 章")
    print(f"   路径: {book_dir}")
    print(f"\n注意: summary字段为空，请告知用户需要我为每章生成摘要")

if __name__ == "__main__":
    main()
