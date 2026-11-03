#!/usr/bin/env python3
"""
Knowledge Base Vector Database Main Interface
Provides unified API for knowledge base operations
"""

import os
import sqlite3
import argparse
from typing import List, Optional
from pathlib import Path

# Import modules
from ingest_document import ingest_document, DEFAULT_CHUNK_SIZE
from batch_ingest import batch_ingest
from retrieve import retrieve as vector_search
from rag_query import rag_query

class KnowledgeBase:
    """Knowledge Base Vector Database Class"""

    def __init__(self, db_path: str = "./knowledge.db", collection: str = "default"):
        self.db_path = db_path
        self.collection = collection

    def init(self):
        """Initialize database"""
        from init_knowledge_base import init_database
        init_database(self.db_path)

    def add_document(self, file_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> int:
        """Add a single document"""
        return ingest_document(self.db_path, file_path, self.collection, chunk_size)

    def add_directory(self, directory: str, chunk_size: int = DEFAULT_CHUNK_SIZE, recursive: bool = True) -> dict:
        """Batch add directory"""
        return batch_ingest(self.db_path, directory, self.collection, chunk_size, recursive)

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """Semantic search"""
        return vector_search(self.db_path, query, self.collection, top_k)

    def query(self, question: str, top_k: int = 5, model: str = "gpt-4") -> str:
        """RAG Q&A"""
        return rag_query(self.db_path, question, self.collection, top_k, model)

    def stats(self) -> dict:
        """Get statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM documents WHERE collection = ?", (self.collection,))
        doc_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chunks c JOIN documents d ON c.doc_id = d.id WHERE d.collection = ?", (self.collection,))
        chunk_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM embeddings WHERE collection = ?", (self.collection,))
        vector_count = cursor.fetchone()[0]

        conn.close()

        return {
            "collection": self.collection,
            "documents": doc_count,
            "chunks": chunk_count,
            "vectors": vector_count
        }

def main():
    """Command line main entry"""
    parser = argparse.ArgumentParser(description="Knowledge base vector database")
    parser.add_argument("--db-path", default="./knowledge.db", help="Database path")
    parser.add_argument("--collection", default="default", help="Collection name")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # init command
    subparsers.add_parser("init", help="Initialize database")

    # add command
    add_parser = subparsers.add_parser("add", help="Add document")
    add_parser.add_argument("--file", help="Single file path")
    add_parser.add_argument("--dir", help="Directory path")
    add_parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size")

    # search command
    search_parser = subparsers.add_parser("search", help="Search")
    search_parser.add_argument("--query", required=True, help="Query content")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of results")

    # query command
    query_parser = subparsers.add_parser("query", help="Q&A")
    query_parser.add_argument("--question", required=True, help="Question")
    query_parser.add_argument("--top-k", type=int, default=5, help="Retrieval count")
    query_parser.add_argument("--model", default="gpt-4", help="Model")

    # stats command
    subparsers.add_parser("stats", help="Statistics")

    args = parser.parse_args()
    kb = KnowledgeBase(args.db_path, args.collection)

    if args.command == "init":
        kb.init()
    elif args.command == "add":
        if args.file:
            count = kb.add_document(args.file, args.chunk_size)
            print(f"Document added: {count} chunks")
        elif args.dir:
            results = kb.add_directory(args.dir, args.chunk_size)
            print(f"Batch add complete: {results['success']}/{results['total']} succeeded")
    elif args.command == "search":
        results = kb.search(args.query, args.top_k)
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r['title']} (similarity: {r['similarity']:.4f})")
            print(r['content'][:200])
    elif args.command == "query":
        kb.query(args.question, args.top_k, args.model)
    elif args.command == "stats":
        stats = kb.stats()
        print(f"Collection: {stats['collection']}")
        print(f"Documents: {stats['documents']}")
        print(f"Chunks: {stats['chunks']}")
        print(f"Vectors: {stats['vectors']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
