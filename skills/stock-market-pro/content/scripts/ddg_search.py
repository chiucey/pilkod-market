#!/usr/bin/env python3
"""
DuckDuckGo Search Module - 用于股票相关信息搜索
"""

import sys
import argparse
import requests


def ddg_search(query, max_results=10):
    """
    使用 DuckDuckGo HTML 搜索

    Args:
        query: 搜索关键词
        max_results: 最大结果数

    Returns:
        list: 搜索结果列表
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        results = []
        lines = response.text.split('\n')

        for i, line in enumerate(lines):
            if 'result__a' in line:
                start = line.find('href="') + 6
                end = line.find('"', start)
                link = line[start:end] if start > 5 else ""

                if i + 1 < len(lines):
                    title_line = lines[i + 1]
                    title_start = title_line.find('>') + 1
                    title_end = title_line.find('<', title_start)
                    title = title_line[title_start:title_end].strip() if title_end > title_start else ""

                    if title and link and link.startswith('http'):
                        results.append({'title': title, 'url': link})
                        if len(results) >= max_results:
                            break

        return results

    except Exception as e:
        print(f"Search failed: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="DuckDuckGo Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max", type=int, default=10, help="Max results")

    args = parser.parse_args()
    results = ddg_search(args.query, args.max)

    print(f"Search results for: {args.query}")
    print("=" * 50)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")


if __name__ == "__main__":
    main()
