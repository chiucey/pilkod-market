#!/usr/bin/env python3
"""
Vector Retrieval Script
Semantic similarity search in knowledge base
"""

import sqlite3
import argparse
import numpy as np
from typing import List, Tuple

# Embedding model configuration
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"

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
        import hashlib
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [float((hash_val >> (i * 8)) & 0xFF) / 255.0 for i in range(1536)]

def bytes_to_vector(data: bytes) -> List[float]:
    """Restore vector from bytes"""
    import struct
    return list(struct.unpack(f'{len(data)//4}f', data))

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity"""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def vector_search(
    db_path: str,
    query: str,
    collection: str = "default",
    top_k: int = 5
) -> List[dict]:
    """Vector similarity search"""

    # Get query embedding
    query_embedding = get_embedding(query)
    print(f"Query vector dimension: {len(query_embedding)}")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query all vectors
    cursor.execute(
        """
        SELECT e.chunk_id, e.embedding, c.content, d.title, d.file_path
        FROM embeddings e
        JOIN chunks c ON e.chunk_id = c.id
        JOIN documents d ON c.doc_id = d.id
        WHERE e.collection = ?
        """,
        (collection,)
    )

    results = []
    for row in cursor.fetchall():
        chunk_id, embedding_bytes, content, title, file_path = row
        embedding = bytes_to_vector(embedding_bytes)
        similarity = cosine_similarity(query_embedding, embedding)

        results.append({
            "chunk_id": chunk_id,
            "content": content,
            "title": title,
            "file_path": file_path,
            "similarity": float(similarity)
        })

    conn.close()

    # Sort and return top_k
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]

def retrieve(
    db_path: str,
    query: str,
    collection: str = "default",
    top_k: int = 5
) -> List[dict]:
    """Retrieve relevant knowledge"""

    print(f"Retrieval query: {query}")
    print(f"Collection: {collection}, Top-k: {top_k}")
    print("-" * 50)

    results = vector_search(db_path, query, collection, top_k)

    if not results:
        print("No relevant results found")
        return []

    print(f"Found {len(results)} relevant results:\n")

    for i, r in enumerate(results, 1):
        print(f"[Result {i}] Similarity: {r['similarity']:.4f}")
        print(f"Source: {r['title']}")
        print(f"Content: {r['content'][:200]}..." if len(r['content']) > 200 else f"Content: {r['content']}")
        print("-" * 50)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vector database semantic retrieval")
    parser.add_argument("--db-path", default="./knowledge.db", help="Database path")
    parser.add_argument("--query", required=True, help="Retrieval query")
    parser.add_argument("--collection", default="default", help="Collection name")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")

    args = parser.parse_args()
    results = retrieve(args.db_path, args.query, args.collection, args.top_k)
