#!/usr/bin/env python3
"""
ask_book.py - 根据书籍内容回答问题（增强版）
用法: python3 ask_book.py <书名> <问题>

流程：
1. 读取 index.json 摘要索引
2. 根据问题语义匹配最相关的2-3章
3. 精读相关章节原文
4. 整理答案返回给用户
"""

import sys
import os
import json
import argparse
from pathlib import Path

def load_index(book_name: str) -> dict:
    """加载书籍索引"""
    index_path = Path(f"/workspace/library/{book_name}/index.json")
    if not index_path.exists():
        print(f"ERROR: 书籍不存在或未生成索引: {book_name}")
        print(f"请先运行 import_book.py 导入书籍")
        sys.exit(1)
    return json.loads(index_path.read_text(encoding="utf-8"))

def find_relevant_chapters(index: dict, question: str, top_n: int = 3) -> list:
    """根据问题找到最相关的章节"""
    keywords = question.lower().split()
    
    scored = []
    for ch in index["chapters"]:
        score = 0
        title = ch["title"].lower()
        summary = ch["summary"].lower()
        
        for kw in keywords:
            if kw in title:
                score += 3  # 标题命中权重更高
            if kw in summary:
                score += 1
        
        # 包含问答的章节优先
        if "q" in question or "如何" in question or "为什么" in question:
            if "方法" in summary or "原因" in summary or "步骤" in summary:
                score += 2
        
        if score > 0:
            scored.append((score, ch))
    
    # 按分数排序，取前N个
    scored.sort(reverse=True)
    return [ch for _, ch in scored[:top_n]]

def read_chapter(book_name: str, chapter_file: str) -> str:
    """读取章节完整内容"""
    chapter_path = Path(f"/workspace/library/{book_name}/{chapter_file}")
    if chapter_path.exists():
        return chapter_path.read_text(encoding="utf-8", errors="ignore")
    return ""

def answer_from_chapters(book_name: str, chapters: list, question: str) -> str:
    """基于相关章节生成答案"""
    # 读取章节内容
    contents = []
    for ch in chapters:
        content = read_chapter(book_name, ch["file"])
        if content:
            # 截取关键段落（避免太长）
            lines = content.split('\n')
            key_lines = [l for l in lines if len(l.strip()) > 10][:50]
            contents.append({
                "title": ch["title"],
                "content": '\n'.join(key_lines)
            })
    
    # 构造 prompt 让 LLM 回答
    try:
        import openai
        client = openai.OpenAI(
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.minimaxi.chat/v1"),
            api_key=os.environ.get("OPENAI_API_KEY", "")
        )
        
        context = "\n\n".join([
            f"=== {c['title']} ===\n{c['content'][:1500]}"
            for c in contents
        ])
        
        prompt = f"""你是一个阅读了本书的助手。请根据以下书籍内容回答用户的问题。

用户问题：{question}

书籍相关章节内容：
{context}

要求：
- 基于书中内容给出准确答案
- 如果书籍内容不足以完全回答，说明哪些方面有涉及
- 可以引用书中的具体观点
- 回答条理清晰"""

        response = client.chat.completions.create(
            model="abab6.5s-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERROR: LLM调用失败: {e}")
        # 降级：直接返回章节内容
        return "【内容摘要】\n\n" + "\n\n".join([
            f"📖 {c['title']}\n{c['content'][:500]}..."
            for c in contents
        ])

def main():
    parser = argparse.ArgumentParser(description="根据书籍内容回答问题（增强版）")
    parser.add_argument("book_name", help="书籍名称")
    parser.add_argument("question", help="问题（可用引号包裹）")
    args = parser.parse_args()

    book_name = args.book_name
    question = args.question

    # 加载索引
    index = load_index(book_name)
    print(f"📚 《{book_name}》已加载，共 {len(index['chapters'])} 章")

    # 找相关章节
    relevant = find_relevant_chapters(index, question)
    if not relevant:
        print(f"❓ 未找到与「{question}」直接相关的内容")
        print(f"   尝试用其他关键词搜索，或检查索引是否完整")
        return

    print(f"🔍 找到 {len(relevant)} 个相关章节:")
    for ch in relevant:
        print(f"   - {ch['title']}")

    # 生成答案
    print(f"\n💡 正在分析...")
    answer = answer_from_chapters(book_name, relevant, question)
    print(f"\n{'='*50}")
    print(f"📖 回答：")
    print(answer)
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
