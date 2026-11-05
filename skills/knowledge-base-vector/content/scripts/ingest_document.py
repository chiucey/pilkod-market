#!/usr/bin/env python3
"""
Document Ingestion Script
Chunk documents and store vectors in the vector database
"""

import sqlite3
import os
import argparse
import hashlib
from typing import List, Tuple

# Embedding model configuration
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50

def get_embedding(text: str, model: str = DEFAULT_EMBEDDING_MODEL) -> List[float]:
    """Get text embedding vector"""
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.embeddings.create(
            model=model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding API call failed: {e}")
        # Return mock vector for testing
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [float((hash_val >> (i * 8)) & 0xFF) / 255.0 for i in range(1536)]

def read_document(file_path: str) -> str:
    """Read document content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[str]:
    """Split text into chunks"""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to split at sentence boundary or newline
        if end < len(text):
            last_period = max(chunk.rfind('。'), chunk.rfind('\n'), chunk.rfind('.'))
            if last_period > chunk_size // 2:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1

        chunks.append(chunk.strip())
        start = end - overlap if end < len(text) else end

    return [c for c in chunks if c]

def vector_to_bytes(vector: List[float]) -> bytes:
    """Convert vector to bytes for storage"""
    import struct
    return struct.pack(f'{len(vector)}f', *vector)

def bytes_to_vector(data: bytes) -> List[float]:
    """Restore vector from bytes"""
    import struct
    return list(struct.unpack(f'{len(data)//4}f', data))

def ingest_document(
    db_path: str,
    file_path: str,
    collection: str = "default",
    chunk_size: int = DEFAULT_CHUNK_SIZE
) -> int:
    """Ingest document into database"""

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Read document
    content = read_document(file_path)
    title = os.path.basename(file_path)

    # Chunk text
    chunks = chunk_text(content, chunk_size)
    print(f"Document chunked: {len(chunks)} chunks")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert document record
    cursor.execute(
        "INSERT INTO documents (collection, file_path, title, content) VALUES (?, ?, ?, ?)",
        (collection, file_path, title, content)
    )
    doc_id = cursor.lastrowid

    # Insert chunks and embeddings
    embeddings_list = []
    for idx, chunk in enumerate(chunks):
        # Insert chunk
        cursor.execute(
            "INSERT INTO chunks (doc_id, chunk_index, content) VALUES (?, ?, ?)",
            (doc_id, idx, chunk)
        )
        chunk_id = cursor.lastrowid

        # Get embedding vector
        embedding = get_embedding(chunk)
        embedding_bytes = vector_to_bytes(embedding)

        # Store vector
        cursor.execute(
            "INSERT INTO embeddings (chunk_id, collection, embedding) VALUES (?, ?, ?)",
            (chunk_id, collection, embedding_bytes)
        )

        embeddings_list.append(embedding)
        print(f"  Chunk {idx + 1}/{len(chunks)} ingested")

    conn.commit()
    conn.close()

    print(f"Document ingested: {title}, {len(chunks)} chunks")
    return len(chunks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest document into vector knowledge base")
    parser.add_argument("--db-path", default="./knowledge.db", help="Database path")
    parser.add_argument("--file", required=True, help="Document path")
    parser.add_argument("--collection", default="default", help="Collection name")
    parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size")

    args = parser.parse_args()
    count = ingest_document(args.db_path, args.file, args.collection, args.chunk_size)
    print(f"Successfully ingested {count} knowledge chunks")
