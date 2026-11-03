import logging
import os
import re
import shutil
import sqlite3
from datetime import datetime
from typing import Dict

from flask import Flask, jsonify, request

import config
from utils.classifier import classify_document
from utils.file_parser import parse_file_content
from utils.search_engine import SearchEngine
from utils.tag_generator import generate_tags


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("auto-archive")

app = Flask(__name__)


def ensure_dirs() -> None:
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.INDEX_DIR, exist_ok=True)
    os.makedirs(config.UPLOADS_TEMP_DIR, exist_ok=True)
    os.makedirs(config.SHARED_BASE_PATH, exist_ok=True)


def init_db() -> None:
    conn = sqlite3.connect(config.DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_path TEXT NOT NULL,
                archived_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                primary_category TEXT,
                secondary_category TEXT,
                doc_date TEXT,
                company TEXT,
                version TEXT,
                subject TEXT,
                tags TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def sanitize_name(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"[\\/:*?\"<>|]+", "_", value)
    value = re.sub(r"\s+", "", value)
    return value[:60]


def build_new_filename(meta: Dict[str, str], ext: str) -> str:
    date_str = meta.get("date") or datetime.now().strftime("%Y%m%d")
    company = sanitize_name(meta.get("company") or "集团")
    subject = sanitize_name(meta.get("subject") or "未命名主题")
    version = sanitize_name(meta.get("version") or "")
    parts = [date_str, company, subject]
    if version:
        parts.append(version)
    return "_".join(parts) + ext


def archive_file(file_path: str, meta: Dict[str, str]) -> str:
    ext = os.path.splitext(file_path)[1]
    new_name = build_new_filename(meta, ext)
    target_dir = os.path.join(
        config.SHARED_BASE_PATH,
        meta["primary_category"],
        meta["secondary_category"],
    )
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, new_name)
    shutil.move(file_path, target_path)
    return target_path


def save_to_db(original_path: str, archived_path: str, meta: Dict[str, str], tags: list[str]) -> int:
    conn = sqlite3.connect(config.DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO documents (
                original_path, archived_path, file_name,
                primary_category, secondary_category, doc_date,
                company, version, subject, tags, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                original_path,
                archived_path,
                os.path.basename(archived_path),
                meta.get("primary_category"),
                meta.get("secondary_category"),
                meta.get("date"),
                meta.get("company"),
                meta.get("version"),
                meta.get("subject"),
                ",".join(tags),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


ensure_dirs()
init_db()
search_engine = SearchEngine(config.INDEX_DIR)


@app.post("/api/auto_archive")
def auto_archive():
    payload = request.get_json(silent=True) or {}
    file_path = payload.get("file_path", "").strip()
    if not file_path:
        return jsonify({"ok": False, "error": "file_path is required"}), 400
    if not os.path.exists(file_path):
        return jsonify({"ok": False, "error": f"file not found: {file_path}"}), 404

    try:
        text = parse_file_content(file_path, max_chars=config.MAX_READ_CHARS)
        meta = classify_document(file_path, text)
        tags = generate_tags(meta, text)
        original_path = file_path
        archived_path = archive_file(file_path, meta)
        doc_id = save_to_db(original_path, archived_path, meta, tags)
        search_engine.index_document(
            {
                "doc_id": str(doc_id),
                "file_name": os.path.basename(archived_path),
                "file_path": archived_path,
                "content": text,
                "tags": tags,
            }
        )
        return jsonify(
            {
                "ok": True,
                "doc_id": doc_id,
                "archived_path": archived_path,
                "metadata": meta,
                "tags": tags,
            }
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to process file: %s", file_path)
        return jsonify({"ok": False, "error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=True)

