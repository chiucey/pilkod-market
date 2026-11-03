#!/usr/bin/env python3
"""
Knowledge Base Vector Database Initialization
Supports sqlite-vec extension for vector storage
"""

import sqlite3
import os
import sys

def init_database(db_path: str):
    """Initialize SQLite vector database"""

    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable vector extension
    try:
        cursor.execute("SELECT load_extension('vec0');")
    except Exception as e:
        print(f"Note: vec extension loading failed, using pure SQL: {e}")

    # Create documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection TEXT NOT NULL,
            file_path TEXT,
            title TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create chunks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES documents(id)
        )
    """)

    # Create embeddings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id INTEGER NOT NULL,
            collection TEXT NOT NULL,
            embedding BLOB NOT NULL,
            FOREIGN KEY (chunk_id) REFERENCES chunks(id)
        )
    """)

    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_docs_collection ON documents(collection)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_emb_collection ON embeddings(collection)")

    conn.commit()
    conn.close()

    print(f"Knowledge base database initialized: {db_path}")
    return db_path

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize knowledge base vector database")
    parser.add_argument("--db-path", default="./knowledge.db", help="Database path")

    args = parser.parse_args()
    init_database(args.db_path)
