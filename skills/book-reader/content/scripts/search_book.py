#!/usr/bin/env python3
"""
search_book.py - 在书籍知识库中搜索关键词（增强版）
用法: python3 search_book.py <书名> <关键词> [--limit N]

优先从 index.json 摘要索引搜索，快速定位相关章节
"""

import os
import json
import argparse
from pathlib import Path

def search_index(book_name: str, keyword: str, limit: int = 10) -> list:
    """在 index.json 摘要索引中搜索"""
    index_path = Path(f"/workspace/library/{book_name}/index.json")
    if not index_path.exists():
        return None
    
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except:
        return None
    
    results = []
    for ch in index.get("chapters", []):
        if keyword in ch["title"] or keyword in ch["summary"]:
            results.append({
                "id": ch["id"],
                "title": ch["title"],
                "summary": ch["summary"],
                "file": ch["file"],
                "match_type": "title" if keyword in ch["title"] else "summary"
            })
            if len(results) >= limit:
                break
    
    return results

def search_full_text(book_name: str, keyword: str, limit: int = 10) -> list:
    """在完整章节文本中搜索"""
    book_dir = Path(f"/workspace/library/{book_name}")
    results = []
    
    for chapter_file in sorted(book_dir.glob("chapter_*.md")):
        content = chapter_file.read_text(encoding="utf-8", errors="ignore")
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if keyword in line and len(line.strip()) > 5:
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                snippet = '\n'.join(
                    f"{'[命中] ' if j == i else '       '}{lines[j][:100]}"
                    for j in range(start, end)
                )
                results.append({
                    "chapter": chapter_file.name,
                    "line": i + 1,
                    "snippet": snippet
                })
                if len(results) >= limit:
                    break
        
        if len(results) >= limit:
            break
    
    return results

def get_library_list():
    """列出所有已入库书籍"""
    library_dir = Path("/workspace/library")
    if not library_dir.exists():
        return []
    return [d.name for d in library_dir.iterdir() if d.is_dir()]

def main():
    parser = argparse.ArgumentParser(description="在书籍中搜索关键词（增强版）")
    parser.add_argument("book_name", help="书籍名称")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--limit", type=int, default=10, help="最多返回结果数")
    args = parser.parse_args()

    if args.book_name == "--list":
        books = get_library_list()
        if books:
            print("📚 已入库书籍:")
            for b in books:
                meta_path = Path(f"/workspace/library/{b}/metadata.json")
                if meta_path.exists():
                    meta = json.loads(meta_path.read_text())
                    print(f"  - {b} ({meta.get('chapters', '?')}章, v{meta.get('version', '?')})")
                else:
                    print(f"  - {b}")
        else:
            print("📚 知识库为空，请先导入书籍")
        return

    # 先搜索 index.json 摘要
    index_results = search_index(args.book_name, args.keyword, args.limit)
    
    if index_results:
        print(f"🔍 在《{args.book_name}》摘要索引中找到 {len(index_results)} 条结果:\n")
        for r in index_results:
            match_icon = "📌" if r["match_type"] == "title" else "📄"
            print(f"{match_icon} 第{r['id']}章：{r['title']}")
            print(f"   摘要：{r['summary'][:80]}...")
            print()
    else:
        print(f"📚 书籍《{args.book_name}》索引不存在，请先导入书籍")
        return

    # 再搜索完整文本（显示更详细）
    full_results = search_full_text(args.book_name, args.keyword, args.limit)
    if full_results:
        print(f"\n📜 在正文中的命中（共 {len(full_results)} 处）:\n")
        for r in full_results[:5]:
            print(f"  📖 {r['chapter']} 第{r['line']}行")
            print(f"  {r['snippet'][:150]}")
            print()

if __name__ == "__main__":
    main()
