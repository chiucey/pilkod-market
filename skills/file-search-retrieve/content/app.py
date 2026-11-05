# -*- coding: utf-8 -*-
"""
Flask Web Service for file-search-retrieve
Provides REST API for searching archived files in the state-owned asset management database.
"""

import os
import sys
import json
import sqlite3
import webbrowser
import threading
import subprocess
from urllib.parse import unquote

from flask import Flask, render_template, request, jsonify
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from whoosh.query import And, Or, Every

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

app = Flask(__name__, template_folder="templates")
_search_index = None

SCHEMA = Schema(
    id=ID(stored=True, unique=True),
    file_name=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    file_path=ID(stored=True),
    content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    tags=KEYWORD(stored=True, commas=True, scorable=True),
    category1=ID(stored=True),
    category2=ID(stored=True)
)


def get_db_connection():
    db_path = config.DATABASE_PATH
    if not os.path.exists(db_path):
        return None
    return sqlite3.connect(db_path)


def init_index():
    global _search_index
    if not os.path.exists(config.INDEX_DIR):
        os.makedirs(config.INDEX_DIR)
    if index.exists_in(config.INDEX_DIR):
        _search_index = index.open_dir(config.INDEX_DIR)
    else:
        _search_index = index.create_in(config.INDEX_DIR, SCHEMA)
        build_index_from_db()
    return _search_index


def build_index_from_db():
    conn = get_db_connection()
    if not conn:
        print("[WARNING] Database not found. Run Skill 2 first.")
        return
    ix = _search_index
    writer = ix.writer()
    try:
        cursor = conn.execute("SELECT id, file_name, file_path, content, tags, category1, category2 FROM files")
        for row in cursor.fetchall():
            file_id, file_name, file_path, content, tags, category1, category2 = row
            indexed_content = content[:config.CONTENT_MAX_LENGTH] if content else ""
            writer.add_document(
                id=file_id or "", file_name=file_name or "", file_path=file_path or "",
                content=indexed_content, tags=tags or "", category1=category1 or "", category2=category2 or ""
            )
        writer.commit()
        print("[INFO] Index built from database.")
    except sqlite3.OperationalError as e:
        print(f"[WARNING] Table 'files' not found: {e}")
    finally:
        conn.close()


def search_files(q=None, tags=None, categories=None, page=1, limit=20):
    if not _search_index:
        return [], 0
    results = []
    ix = _search_index
    with ix.searcher() as searcher:
        query_parts = []
        if q:
            parser = MultifieldParser(["file_name", "content"], ix.schema, group=OrGroup)
            query_parts.append(parser.parse(q))
        if tags:
            for tag in [t.strip() for t in tags.split(",") if t.strip()]:
                query_parts.append(QueryParser("tags", ix.schema).parse(tag))
        if categories:
            cat_queries = [QueryParser("category2", ix.schema).parse(c.strip()) for c in categories.split(",") if c.strip()]
            if cat_queries:
                query_parts.append(Or(cat_queries))
        if query_parts:
            query = And(query_parts)
        else:
            query = Every()
        whoosh_results = searcher.search(query, limit=None)
        total = len(whoosh_results)
        start, end = (page - 1) * limit, (page - 1) * limit + limit
        page_results = whoosh_results[start:end]
        conn = get_db_connection()
        if conn:
            try:
                ids = [r["id"] for r in page_results]
                if ids:
                    placeholders = ",".join("?" * len(ids))
                    cursor = conn.execute(f"SELECT id, file_name, file_path, category1, category2, tags, processed_time FROM files WHERE id IN ({placeholders})", ids)
                    metadata_map = {row[0]: row[1:] for row in cursor.fetchall()}
                    for r in page_results:
                        meta = metadata_map.get(r["id"])
                        if meta:
                            file_name, file_path, cat1, cat2, tags_str, processed_time = meta
                            cat_path = f"{cat1}/{cat2}" if cat1 and cat2 else ""
                            if cat2 in config.CATEGORY_CODES:
                                cat_path = f"{cat1}/{cat2}_{config.CATEGORY_CODES[cat2]['category_name']}"
                            try:
                                tag_list = json.loads(tags_str) if tags_str else []
                            except:
                                tag_list = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
                            highlight = ""
                            if q and "content" in r:
                                content_text = r["content"]
                                idx = content_text.lower().find(q.lower())
                                if idx >= 0:
                                    s, e = max(0, idx - 50), min(len(content_text), idx + len(q) + 50)
                                    highlight = f"...{content_text[s:e]}..."
                                    highlight = highlight.replace(q, f"<em>{q}</em>")
                            results.append({
                                "id": r["id"], "file_name": file_name, "file_path": file_path,
                                "category1": cat1 or "", "category2": cat2 or "", "category_path": cat_path,
                                "tags": tag_list, "processed_time": processed_time or "", "highlight": highlight
                            })
            except Exception as e:
                print(f"[ERROR] DB query: {e}")
            finally:
                conn.close()
    return results, total


def get_hot_tags(limit=20):
    conn = get_db_connection()
    if not conn:
        return []
    tag_counts = {}
    try:
        for row in conn.execute("SELECT tags FROM files WHERE tags IS NOT NULL AND tags != ''"):
            try:
                tags = json.loads(row[0])
            except:
                tags = [t.strip() for t in row[0].split(",") if t.strip()]
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return [{"name": t, "count": c} for t, c in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]]
    except:
        return []
    finally:
        conn.close()


def open_file(file_path):
    if not file_path:
        return False, "No path provided"
    file_path = unquote(file_path)
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    try:
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", file_path], check=True)
        else:
            subprocess.run(["xdg-open", file_path], check=True)
        return True, "Opened"
    except Exception as e:
        return False, str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search")
def api_search():
    q, tags = request.args.get("q", ""), request.args.get("tags", "")
    categories = request.args.get("categories", "")
    page, limit = int(request.args.get("page", 1)), min(int(request.args.get("limit", 20)), 100)
    results, total = search_files(q, tags, categories, page, limit)
    return jsonify({"success": True, "total": total, "page": page, "limit": limit, "results": results})


@app.route("/api/hot_tags")
def api_hot_tags():
    return jsonify({"success": True, "hot_tags": get_hot_tags()})


@app.route("/api/categories")
def api_categories():
    return jsonify({"success": True, "categories": config.CATEGORIES})


@app.route("/api/open")
def api_open():
    success, msg = open_file(request.args.get("path", ""))
    return jsonify({"success": success, "message": msg})


@app.route("/api/index/add", methods=["POST"])
def api_index_add():
    if not _search_index:
        return jsonify({"success": False, "error": "Index not initialized"}), 500
    data = request.get_json()
    try:
        writer = _search_index.writer()
        writer.add_document(
            id=data.get("id", ""), file_name=data.get("file_name", ""), file_path=data.get("file_path", ""),
            content=data.get("content", "")[:config.CONTENT_MAX_LENGTH], tags=data.get("tags", ""),
            category1=data.get("category1", ""), category2=data.get("category2", "")
        )
        writer.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/index/update", methods=["PUT"])
def api_index_update():
    if not _search_index:
        return jsonify({"success": False, "error": "Index not initialized"}), 500
    data = request.get_json()
    try:
        writer = _search_index.writer()
        writer.update_document(
            id=data.get("id", ""), file_name=data.get("file_name", ""), file_path=data.get("file_path", ""),
            content=data.get("content", "")[:config.CONTENT_MAX_LENGTH], tags=data.get("tags", ""),
            category1=data.get("category1", ""), category2=data.get("category2", "")
        )
        writer.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/index/delete", methods=["DELETE"])
def api_index_delete():
    if not _search_index:
        return jsonify({"success": False, "error": "Index not initialized"}), 500
    doc_id = request.get_json().get("id", "")
    if not doc_id:
        return jsonify({"success": False, "error": "No ID"}), 400
    try:
        writer = _search_index.writer()
        writer.delete_by_term("id", doc_id)
        writer.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/index/rebuild", methods=["POST"])
def api_index_rebuild():
    global _search_index
    try:
        import shutil
        if os.path.exists(config.INDEX_DIR):
            shutil.rmtree(config.INDEX_DIR)
        _search_index = index.create_in(config.INDEX_DIR, SCHEMA)
        build_index_from_db()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "index_initialized": _search_index is not None, "database_exists": os.path.exists(config.DATABASE_PATH)})


def open_browser():
    import time
    time.sleep(1.5)
    webbrowser.open(f"http://{config.HOST}:{config.PORT}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=config.HOST)
    parser.add_argument("--port", type=int, default=config.PORT)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    print("[INFO] Initializing index...")
    if args.rebuild and os.path.exists(config.INDEX_DIR):
        import shutil
        shutil.rmtree(config.INDEX_DIR)
    init_index()
    threading.Thread(target=open_browser, daemon=True).start()
    print(f"[INFO] Server at http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
