"""Flask Web 检索服务：提供可视化检索、热门标签与文件打开接口。"""

import os
import sqlite3
import threading
import webbrowser
from datetime import datetime
from typing import Any

from flask import Flask, jsonify, render_template, request

import config
from category_paths import LEVEL1, LEVEL2, level1_folder_name, level2_folder_name
from db_manager import ensure_db
from index_manager import clean_missing_files

app = Flask(__name__)
ensure_db()
if not config.AI_API_KEY:
    print("[WARN] 未配置 AI_API_KEY：Web 服务仍可用，但归档将采用本地规则分类，效果有限。")
clean_missing_files()


def _db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _parse_tags(raw: str) -> list[str]:
    tags: list[str] = []
    for t in (raw or "").split(","):
        tag = t.strip()
        if not tag:
            continue
        pure = tag.lstrip("#").upper()
        if pure in {"A", "B", "C", "D", "E", "F"}:
            continue
        if len(pure) == 3 and pure[0] in {"A", "B", "C", "D", "E", "F"} and pure[1:].isdigit():
            continue
        tags.append(tag)
    return tags


def _format_processed_time(value: str) -> str:
    """将数据库时间标准化为 YYYY-MM-DD HH:MM。"""
    text = (value or "").strip()
    if not text:
        return ""
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return text[:16]


def _simplify_file_name(name: str) -> str:
    """简化文件名显示：去重复日期前缀与多余下划线。"""
    file_name = (name or "").strip()
    if not file_name:
        return ""
    stem, ext = os.path.splitext(file_name)
    stem = stem.replace("__", "_").strip("_")
    stem = stem.replace(" ", "")
    stem = stem.replace("“", "").replace("”", "").replace('"', "")
    # 例如 20260417_20260417_xxx -> 20260417_xxx
    stem = stem.replace("_", " ").strip()
    parts = [p for p in stem.split(" ") if p]
    if len(parts) >= 2 and parts[0].isdigit() and len(parts[0]) == 8 and parts[1] == parts[0]:
        parts.pop(1)
    compact = "_".join(parts).strip("_")
    return f"{compact}{ext}" if compact else file_name


def _build_category_path(category1: str, category2: str) -> str:
    c1 = (category1 or "").strip().upper()
    c2 = (category2 or "").strip().upper()
    return f"{level1_folder_name(c1)} / {level2_folder_name(c1, c2)}"


def _query_search(
    keyword: str, tags: list[str], categories: list[str], page: int, page_size: int
) -> dict[str, Any]:
    keyword = (keyword or "").strip()
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    offset = (page - 1) * page_size

    where_parts: list[str] = []
    params: list[Any] = []
    shared_root = os.path.abspath(config.SHARED_BASE_PATH)
    where_parts.append("file_path LIKE ?")
    params.append(shared_root + "%")
    if keyword:
        where_parts.append("(file_name LIKE ? OR content_snippet LIKE ?)")
        like_kw = f"%{keyword}%"
        params.extend([like_kw, like_kw])
    for tag in tags:
        where_parts.append("tags LIKE ?")
        params.append(f"%{tag}%")
    if categories:
        c_placeholders = ",".join("?" for _ in categories)
        where_parts.append(f"category2 IN ({c_placeholders})")
        params.extend(categories)

    where_sql = " AND ".join(where_parts) if where_parts else "1=1"
    count_sql = f"SELECT COUNT(DISTINCT file_path) AS cnt FROM files WHERE {where_sql}"
    list_sql = f"""
        SELECT id, file_name, file_path, category1, category2, file_date, tags, processed_time
        FROM (
            SELECT
                id, file_name, file_path, category1, category2, file_date, tags, processed_time,
                ROW_NUMBER() OVER (
                    PARTITION BY file_path
                    ORDER BY processed_time DESC, id DESC
                ) AS rn
            FROM files
            WHERE {where_sql}
        ) t
        WHERE t.rn = 1
        ORDER BY processed_time DESC
        LIMIT ? OFFSET ?
    """

    conn = _db_conn()
    try:
        total = conn.execute(count_sql, params).fetchone()["cnt"]
        rows = conn.execute(list_sql, [*params, page_size, offset]).fetchall()
    finally:
        conn.close()

    items = []
    for row in rows:
        tag_list = _parse_tags(row["tags"])
        items.append(
            {
                "id": row["id"],
                "file_name": _simplify_file_name(row["file_name"] or ""),
                "file_path": row["file_path"] or "",
                "category_path": _build_category_path(row["category1"] or "", row["category2"] or ""),
                "category2": (row["category2"] or "").strip().upper(),
                "file_date": row["file_date"] or "",
                "tags": tag_list,
                "processed_time": _format_processed_time(row["processed_time"] or ""),
            }
        )

    return {
        "items": items,
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "pages": (int(total) + page_size - 1) // page_size,
    }


@app.get("/")
def index() -> str:
    """首页：检索主界面。"""
    return render_template("index.html", category_tree={"level1": LEVEL1, "level2": LEVEL2})


@app.get("/api/search")
def api_search():
    """检索接口：支持关键词、标签筛选与分页。"""
    clean_missing_files()
    keyword = request.args.get("keyword", "", type=str)
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    tags_raw = request.args.get("tags", "", type=str)
    categories_raw = request.args.get("categories", "", type=str)
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    categories = [c.strip().upper() for c in categories_raw.split(",") if c.strip()]
    data = _query_search(
        keyword=keyword,
        tags=tags,
        categories=categories,
        page=page,
        page_size=page_size,
    )
    return jsonify({"ok": True, **data})


@app.get("/api/categories")
def api_categories():
    """分类树接口：用于前端筛选面板。"""
    return jsonify({"ok": True, "level1": LEVEL1, "level2": LEVEL2})


@app.get("/api/hot_tags")
def api_hot_tags():
    """热门标签接口：返回使用频率最高的前 20 个标签。"""
    clean_missing_files()
    conn = _db_conn()
    try:
        rows = conn.execute(
            "SELECT tags FROM files WHERE file_path LIKE ?",
            (os.path.abspath(config.SHARED_BASE_PATH) + "%",),
        ).fetchall()
    finally:
        conn.close()

    counter: dict[str, int] = {}
    for row in rows:
        for tag in _parse_tags(row["tags"] or ""):
            counter[tag] = counter.get(tag, 0) + 1

    top = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:20]
    return jsonify({"ok": True, "items": [{"tag": t, "count": c} for t, c in top]})


@app.get("/open_file")
def open_file():
    """打开文件接口：Windows 下通过 os.startfile 打开。"""
    file_path = request.args.get("path", "", type=str).strip().strip('"')
    if not file_path:
        return jsonify({"ok": False, "error": "path is required"}), 400
    file_path = file_path.replace("/", "\\")
    if not os.path.isabs(file_path):
        file_path = os.path.join(config.SHARED_BASE_PATH, file_path)
    file_path = os.path.normpath(file_path)
    if not os.path.exists(file_path):
        return (
            jsonify(
                {
                    "ok": False,
                    "error": f"文件可能已被移动或删除：{file_path}",
                    "code": "NOT_FOUND",
                }
            ),
            404,
        )
    try:
        os.startfile(file_path)  # type: ignore[attr-defined]
        return jsonify({"ok": True})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"ok": False, "error": str(exc)}), 500


if __name__ == "__main__":
    # 启动后自动打开本机浏览器，便于领导直接使用。
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5050")).start()
    app.run(host="127.0.0.1", port=5050, debug=True)
