# -*- coding: utf-8 -*-
"""
本地RAG快速启动脚本

使用方法：
python quick_start.py --documents /path/to/docs --query "你的问题"
"""

import argparse
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_engine import RAGEngine


def main():
    parser = argparse.ArgumentParser(description="本地RAG快速启动")
    parser.add_argument("--documents", "-d", nargs="+", required=True,
                        help="文档路径或目录")
    parser.add_argument("--query", "-q", type=str, required=True,
                        help="查询问题")
    parser.add_argument("--embed-model", "-e", type=str,
                        default="BAAI/bge-large-zh",
                        help="嵌入模型名称")
    parser.add_argument("--llm", "-l", type=str,
                        default="mock",
                        choices=["mock", "ollama", "openai", "anthropic"],
                        help="LLM提供者")
    parser.add_argument("--vector-store", "-v", type=str,
                        default="faiss",
                        choices=["faiss", "chroma"],
                        help="向量存储后端")
    parser.add_argument("--top-k", "-k", type=int,
                        default=5,
                        help="检索数量")
    parser.add_argument("--chunk-size", "-c", type=int,
                        default=500,
                        help="分块大小")
    parser.add_argument("--save-index", "-s", type=str,
                        default=None,
                        help="保存索引路径")

    args = parser.parse_args()

    print("=" * 60)
    print("本地RAG检索增强生成系统")
    print("=" * 60)

    # 初始化引擎
    print(f"\n[1/4] 初始化RAG引擎...")
    print(f"  - 嵌入模型: {args.embed_model}")
    print(f"  - LLM提供者: {args.llm}")
    print(f"  - 向量存储: {args.vector_store}")

    rag = RAGEngine(
        embed_model=args.embed_model,
        llm_provider=args.llm,
        vector_store=args.vector_store,
        chunk_size=args.chunk_size,
        top_k=args.top_k
    )

    # 索引文档
    print(f"\n[2/4] 索引文档...")
    print(f"  - 文档路径: {args.documents}")

    stats = rag.index_documents(args.documents)
    print(f"  - 索引完成: {stats['total_chunks']} 个文档块")

    # 保存索引
    if args.save_index:
        print(f"\n[3/4] 保存索引到: {args.save_index}")
        rag.save_index(args.save_index)

    # 查询
    print(f"\n[4/4] 处理查询...")
    print(f"  - 问题: {args.query}")

    result = rag.query(args.query)

    print("\n" + "=" * 60)
    print("检索结果")
    print("=" * 60)
    print(f"\n答案:\n{result['answer']}")

    if result.get('sources'):
        print(f"\n参考来源 ({result['num_sources']} 个):")
        for i, source in enumerate(result['sources'], 1):
            print(f"\n  [{i}] {source['source']}")
            print(f"      相似度: {source['score']:.4f}")
            print(f"      内容: {source['content'][:150]}...")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
