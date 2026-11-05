#!/usr/bin/env python3
"""
Stock News Search - 使用 DuckDuckGo 搜索股票相关新闻
"""

import sys
import argparse
import requests
from datetime import datetime


def search_stock_news(query, max_results=8):
    """
    使用 DuckDuckGo HTML 接口搜索股票新闻

    Args:
        query: 搜索关键词
        max_results: 最大结果数
    """
    try:
        # 使用 DuckDuckGo HTML 搜索
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 解析搜索结果
        results = []
        lines = response.text.split('\n')

        # 简单解析 DuckDuckGo HTML 结果
        for i, line in enumerate(lines):
            if 'result__a' in line or 'result__title' in line:
                # 提取标题和链接
                start = line.find('href="') + 6
                end = line.find('"', start)
                link = line[start:end] if start > 5 else ""

                # 查找下一个包含标题的标签
                if i + 1 < len(lines):
                    title_line = lines[i + 1] if '<a' in lines[i + 1] else lines[i]
                    title_start = title_line.find('>') + 1
                    title_end = title_line.find('<', title_start)
                    title = title_line[title_start:title_end].strip() if title_end > title_start else ""

                    if title and link and link.startswith('http'):
                        results.append({
                            'title': title,
                            'url': link,
                            'source': extract_domain(link)
                        })
                        if len(results) >= max_results:
                            break

        # 输出结果
        print(f"=== {query} Related News ===")
        print(f"Found {len(results)} news articles\n")

        for i, result in enumerate(results, 1):
            print(f"[{i}] {result['title']}")
            print(f"    Source: {result['source']}")
            print(f"    URL: {result['url']}")
            print()

        return results

    except requests.RequestException as e:
        print(f"Network error: {e}")
        return []
    except Exception as e:
        print(f"Search failed: {e}")
        return []


def extract_domain(url):
    """提取域名"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except:
        return "Unknown"


def main():
    parser = argparse.ArgumentParser(description="Stock news search")
    parser.add_argument("query", help="Search query (stock ticker or company name)")
    parser.add_argument("--max", type=int, default=8, help="Maximum number of results")

    args = parser.parse_args()
    search_stock_news(args.query, args.max)


if __name__ == "__main__":
    main()
