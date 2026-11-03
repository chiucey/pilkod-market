#!/usr/bin/env python3
"""
RAG Query Script
Combine vector retrieval with LLM for answering questions
"""

import os
import sqlite3
import argparse
from typing import List, Tuple, Optional

# Import retrieval function
from retrieve import retrieve, get_embedding

def build_prompt(question: str, context_chunks: List[dict]) -> str:
    """Build RAG prompt"""

    context = "\n\n".join([
        f"[Document {i+1}]{chunk['content']}"
        for i, chunk in enumerate(context_chunks)
    ])

    prompt = f"""You are a knowledge base Q&A assistant. Please answer the user's question based on the following reference documents.

## Reference Documents
{context}

## User Question
{question}

## Answer Requirements
1. Only answer based on information in the reference documents
2. If the documents don't contain relevant information, state so honestly
3. Answers should be accurate, concise, and well-organized

## Answer
"""
    return prompt

def rag_query(
    db_path: str,
    question: str,
    collection: str = "default",
    top_k: int = 5,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """RAG-based Q&A using knowledge base"""

    print(f"Question: {question}")
    print("-" * 50)

    # 1. Retrieve relevant knowledge
    results = retrieve(db_path, question, collection, top_k)

    if not results:
        return "Sorry, no relevant content found in the knowledge base."

    # 2. Build prompt
    prompt = build_prompt(question, results)

    # 3. Call LLM to generate answer
    try:
        from openai import OpenAI
        client = OpenAI()

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional knowledge base Q&A assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        answer = response.choices[0].message.content

        print("=" * 50)
        print("[Answer]")
        print(answer)

        return answer

    except Exception as e:
        print(f"LLM API call failed: {e}")
        print("\nRetrieved relevant documents:")
        for i, r in enumerate(results[:3], 1):
            print(f"\n{i}. {r['content'][:300]}...")

        return "LLM call failed, please check API configuration."

def main():
    parser = argparse.ArgumentParser(description="RAG-based Q&A using knowledge base")
    parser.add_argument("--db-path", default="./knowledge.db", help="Database path")
    parser.add_argument("--question", required=True, help="Question")
    parser.add_argument("--collection", default="default", help="Collection name")
    parser.add_argument("--top-k", type=int, default=5, help="Retrieval count")
    parser.add_argument("--model", default="gpt-4", help="LLM model")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature parameter")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Max tokens")

    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable not set, LLM calls will fail")

    rag_query(
        args.db_path,
        args.question,
        args.collection,
        args.top_k,
        args.model,
        args.temperature,
        args.max_tokens
    )

if __name__ == "__main__":
    main()
