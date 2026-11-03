"""Whoosh 索引管理模块。"""

import os
import sqlite3
from typing import List

from whoosh import index
from whoosh.fields import ID, KEYWORD, TEXT, Schema
from whoosh.qparser import MultifieldParser

from config import DB_PATH, INDEX_PATH


def _schema() -> Schema:
    return Schema(
        doc_id=ID(stored=True, unique=True),
        file_name=TEXT(stored=True),
        content=TEXT(stored=True),
        tags=KEYWORD(stored=True, commas=True),
    )


def ensure_index() -> None:
    """确保索引目录与索引结构存在。"""
    os.makedirs(INDEX_PATH, exist_ok=True)
    if not index.exists_in(INDEX_PATH):
        index.create_in(INDEX_PATH, _schema())


def index_document(doc_id: str, file_name: str, content: str, tags: List[str]) -> None:
    """写入或更新索引文档。"""
    ix = index.open_dir(INDEX_PATH)
    writer = ix.writer()
    writer.update_document(
        doc_id=doc_id,
        file_name=file_name,
        content=content,
        tags=",".join(tags),
    )
    writer.commit()


def search(keyword: str) -> list[dict]:
    """按关键词搜索文件名和内容。"""
    ix = index.open_dir(INDEX_PATH)
    parser = MultifieldParser(["file_name", "content", "tags"], schema=ix.schema)
    q = parser.parse(keyword or "*")
    with ix.searcher() as searcher:
        results = searcher.search(q, limit=20)
        return [
            {"doc_id": r["doc_id"], "file_name": r["file_name"], "tags": r.get("tags", "")}
            for r in results
        ]


def clean_missing_files() -> int:
    """清理已不存在的文件记录：同步删除 SQLite 与 Whoosh 索引。"""
    if not os.path.exists(DB_PATH):
        return 0

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, file_path FROM files")
        rows = cur.fetchall()

        missing_ids: list[int] = []
        for row_id, file_path in rows:
            if not file_path or not os.path.exists(file_path):
                missing_ids.append(int(row_id))

        if not missing_ids:
            return 0

        placeholders = ",".join(["?"] * len(missing_ids))
        cur.execute(f"DELETE FROM files WHERE id IN ({placeholders})", missing_ids)
        conn.commit()
    finally:
        conn.close()

    ensure_index()
    ix = index.open_dir(INDEX_PATH)
    writer = ix.writer()
    for row_id in missing_ids:
        writer.delete_by_term("doc_id", str(row_id))
    writer.commit()
    return len(missing_ids)

