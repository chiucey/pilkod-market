#!/usr/bin/env python3
"""
ASRANK检索技能测试脚本
"""

import sys
import json
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from asrank_retrieval import ASRANKRetriever, RetrievalConfig


def test_basic_retrieval():
    """测试基础检索功能"""
    print("=" * 60)
    print("测试1: 基础检索功能")
    print("=" * 60)

    retriever = ASRANKRetriever()

    # 测试文档
    documents = [
        {
            "path": "ai_intro.txt",
            "content": """
            人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，
            致力于开发能够执行通常需要人类智能的任务的系统。
            AI的应用领域包括机器学习、自然语言处理、计算机视觉等。
            """
        },
        {
            "path": "ml_intro.txt",
            "content": """
            机器学习是人工智能的一个子集，它使用统计技术使计算机系统
            能够从数据中学习和改进，而无需进行明确的编程。
            常见的机器学习算法包括监督学习、无监督学习和强化学习。
            """
        },
        {
            "path": "dl_intro.txt",
            "content": """
            深度学习是机器学习的一个分支，使用多层神经网络来分析各种因素的数据。
            近年来，深度学习在图像识别、语音识别和自然语言处理等领域
            取得了突破性进展。
            """
        }
    ]

    # 索引文档
    for doc in documents:
        count = retriever.index_document(doc["path"], doc["content"])
        print(f"索引 {doc['path']}: {count} 个chunk")

    # 执行检索
    test_queries = [
        "什么是机器学习？",
        "深度学习有哪些应用？",
        "人工智能和机器学习有什么区别？"
    ]

    for query in test_queries:
        print(f"\n查询: {query}")
        results = retriever.retrieve(query, recall_top_k=10, rerank_top_k=5)

        print(f"状态: {results['status']}")
        print(f"召回数量: {results['stage1_recall_count']}")
        print(f"精选数量: {results['stage2_rerank_count']}")

        if results['results']:
            top_result = results['results'][0]
            print(f"最相关结果: {top_result['chunk'][:100]}...")
            print(f"相关性分数: {top_result['relevance_score']:.2f}")


def test_config_options():
    """测试配置选项"""
    print("\n" + "=" * 60)
    print("测试2: 配置选项")
    print("=" * 60)

    # 自定义配置
    config = RetrievalConfig(
        chunk_size=500,
        chunk_overlap=100,
        recall_top_k=50,
        rerank_top_k=5
    )

    retriever = ASRANKRetriever(config)

    doc = """
    这是一个测试文档，用于验证分块配置是否正确工作。
    文档包含多个段落，每个段落都应该被正确地分块处理。
    分块大小和重叠参数会影响检索的效果。
    """

    count = retriever.index_document("test.txt", doc)
    print(f"使用chunk_size={config.chunk_size}索引了 {count} 个chunk")

    results = retriever.retrieve("测试")
    print(f"检索完成，返回 {len(results['results'])} 个结果")


def test_context_building():
    """测试上下文构建"""
    print("\n" + "=" * 60)
    print("测试3: 上下文构建")
    print("=" * 60)

    retriever = ASRANKRetriever()

    doc = """
    OpenAI是一个人工智能研究公司，致力于开发友好的AI技术。
    他们的产品包括ChatGPT、DALL-E和GPT-4等。
    GPT-4是一个大型多模态模型，能够接受图像和文本输入。
    """

    retriever.index_document("openai.txt", doc)
    results = retriever.retrieve("OpenAI有哪些产品？")

    if results['results']:
        context = results['context_for_agent']
        print("生成的上下文:")
        print("-" * 40)
        print(context)
        print("-" * 40)


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试4: 错误处理")
    print("=" * 60)

    retriever = ASRANKRetriever()

    # 测试空文档库检索
    results = retriever.retrieve("测试查询")
    print(f"空文档库检索: {results['status']}")

    # 测试空查询
    if retriever.chunks:
        results = retriever.retrieve("")
        print(f"空查询: {results['status']}")


def main():
    print("ASRANK向量检索技能测试")
    print("=" * 60)

    try:
        test_basic_retrieval()
        test_config_options()
        test_context_building()
        test_error_handling()

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
