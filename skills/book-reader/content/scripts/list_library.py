#!/usr/bin/env python3
"""
list_library.py - 列出本地知识库中的所有书籍
用法: python3 list_library.py
"""

import json
from pathlib import Path

def main():
    library_dir = Path("/workspace/library")
    if not library_dir.exists():
        print("📚 知识库为空（/workspace/library 目录不存在）")
        print("请先使用 import_book.py 导入书籍")
        return

    books = [d for d in library_dir.iterdir() if d.is_dir()]
    if not books:
        print("📚 知识库为空，请先导入书籍")
        return

    print(f"📚 本地知识库 - 共 {len(books)} 本书\n")
    for book_dir in sorted(books):
        meta_path = book_dir / "metadata.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            chapters = meta.get("chapters", "?")
            fmt = meta.get("format", "?")
            source = meta.get("source", "未知")
            print(f"📖 {book_dir.name}")
            print(f"   章节: {chapters} 章 | 格式: {fmt}")
            print(f"   来源: {source}")
        else:
            print(f"📖 {book_dir.name} (无元数据)")
        print()

if __name__ == "__main__":
    main()
