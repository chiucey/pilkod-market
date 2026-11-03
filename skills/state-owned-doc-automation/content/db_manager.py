"""SQLite 数据库管理模块。"""

import os
import sqlite3
from datetime import datetime
from typing import Dict

from config import DB_PATH


def ensure_db() -> None:
    """确保数据库与表结构存在。"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                file_name TEXT,
                original_name TEXT,
                file_path TEXT,
                category1 TEXT,
                category2 TEXT,
                file_date TEXT,
                company TEXT,
                version TEXT,
                subject TEXT,
                tags TEXT,
                content_snippet TEXT,
                processed_time TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_file_record(record: Dict[str, str]) -> int:
    """插入文件元数据记录并返回主键。"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO files (
                file_name, original_name, file_path, category1, category2,
                file_date, company, version, subject, tags, content_snippet, processed_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.get("file_name", ""),
                record.get("original_name", ""),
                record.get("file_path", ""),
                record.get("category1", ""),
                record.get("category2", ""),
                record.get("file_date", ""),
                record.get("company", ""),
                record.get("version", ""),
                record.get("subject", ""),
                record.get("tags", ""),
                record.get("content_snippet", ""),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

