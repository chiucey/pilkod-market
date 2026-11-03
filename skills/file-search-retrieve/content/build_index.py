# -*- coding: utf-8 -*-
"""Build or rebuild Whoosh index from database"""
import os, sys, shutil, sqlite3
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.analysis import StemmingAnalyzer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

SCHEMA = Schema(
    id=ID(stored=True, unique=True),
    file_name=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    file_path=ID(stored=True),
    content=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    tags=KEYWORD(stored=True, commas=True),
    category1=ID(stored=True),
    category2=ID(stored=True)
)


def get_db_connection():
    return sqlite3.connect(config.DATABASE_PATH) if os.path.exists(config.DATABASE_PATH) else None


def build_index(rebuild=False):
    if not os.path.exists(config.DATABASE_PATH):
        print(f"[ERROR] DB not found: {config.DATABASE_PATH}")
        return False
    if os.path.exists(config.INDEX_DIR):
        if rebuild:
            print(f"[INFO] Removing old index...")
            shutil.rmtree(config.INDEX_DIR)
        else:
            print("[INFO] Index exists. Use --rebuild to rebuild.")
            return False

    os.makedirs(config.INDEX_DIR, exist_ok=True)
    print("[INFO] Creating index...")
    ix = index.create_in(config.INDEX_DIR, SCHEMA)
    conn = get_db_connection()
    writer = ix.writer()
    count = 0

    try:
        print("[INFO] Reading records...")
        for row in conn.execute("SELECT id, file_name, file_path, content, tags, category1, category2 FROM files"):
            file_id, file_name, file_path, content, tags, cat1, cat2 = row
            writer.add_document(
                id=file_id or "", file_name=file_name or "", file_path=file_path or "",
                content=(content or "")[:config.CONTENT_MAX_LENGTH],
                tags=tags or "", category1=cat1 or "", category2=cat2 or ""
            )
            count += 1
        writer.commit()
        print(f"[SUCCESS] Index built with {count} documents.")
    except sqlite3.OperationalError as e:
        print(f"[ERROR] Table not found: {e}")
        writer.cancel()
        return False
    finally:
        conn.close()
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    sys.exit(0 if build_index(rebuild=args.rebuild) else 1)
