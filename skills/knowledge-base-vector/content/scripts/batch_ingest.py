#!/usr/bin/env python3
"""
Batch Document Ingestion Script
Traverse directory and batch ingest into vector database
"""

import os
import argparse
from pathlib import Path
from typing import List

# Import ingestion function
from ingest_document import ingest_document, DEFAULT_CHUNK_SIZE

SUPPORTED_EXTENSIONS = {'.txt', '.md', '.markdown', '.html', '.htm', '.xml', '.json', '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.go', '.rs', '.sql'}

def collect_files(directory: str, recursive: bool = True) -> List[str]:
    """Collect document files from directory"""
    files = []
    path = Path(directory)

    if recursive:
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(path.rglob(f'*{ext}'))
    else:
        for ext in SUPPORTED_EXTENSIONS:
            files.extend(path.glob(f'*{ext}'))

    return [str(f) for f in files]

def batch_ingest(
    db_path: str,
    directory: str,
    collection: str = "default",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    recursive: bool = True
) -> dict:
    """Batch ingest documents"""

    files = collect_files(directory, recursive)

    if not files:
        print(f"No supported document files found: {directory}")
        return {"total": 0, "success": 0, "failed": 0}

    print(f"Found {len(files)} document files")
    print("-" * 50)

    results = {"total": len(files), "success": 0, "failed": 0, "errors": []}

    for i, file_path in enumerate(files, 1):
        try:
            print(f"[{i}/{len(files)}] Processing: {file_path}")
            count = ingest_document(db_path, file_path, collection, chunk_size)
            results["success"] += 1
        except Exception as e:
            print(f"  Failed: {e}")
            results["failed"] += 1
            results["errors"].append({"file": file_path, "error": str(e)})

    print("-" * 50)
    print(f"Batch ingestion complete: {results['success']}/{results['total']} succeeded")

    if results["errors"]:
        print("\nFailed files:")
        for err in results["errors"][:10]:
            print(f"  - {err['file']}: {err['error']}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch ingest documents into vector knowledge base")
    parser.add_argument("--db-path", default="./knowledge.db", help="Database path")
    parser.add_argument("--dir", required=True, help="Document directory")
    parser.add_argument("--collection", default="default", help="Collection name")
    parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size")
    parser.add_argument("--no-recursive", action="store_true", help="Do not recurse subdirectories")

    args = parser.parse_args()
    batch_ingest(
        args.db_path,
        args.dir,
        args.collection,
        args.chunk_size,
        not args.no_recursive
    )
