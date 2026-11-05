#!/usr/bin/env python3
"""
豆瓣图书搜索脚本
查询书籍评分、评论数量和热门短评
"""

import json
import sys
import re
import argparse
from typing import Optional, Dict, List, Any
from urllib.parse import quote

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class DoubanBookSearcher:
    """豆瓣读书搜索器"""

    BASE_URL = "https://book.douban.com"
    SEARCH_URL = f"{BASE_URL}/j/search_subjects"
    SUBJECT_URL = f"{BASE_URL}/subject"

    def __init__(self):
        self.session = None
        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/html',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://book.douban.com/',
            })

    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索图书

        Args:
            keyword: 搜索关键词（书名/ISBN）

        Returns:
            图书列表
        """
        if not keyword:
            return []

        params = {
            'type': 'book',
            'query': keyword,
            'page_size': 10,
            'page': 1,
        }

        result = self._http_get(self.SEARCH_URL, params)
        return self._parse_search_results(result)

    def get_book_detail(self, book_id: str) -> Optional[Dict[str, Any]]:
        """
        获取图书详情

        Args:
            book_id: 豆瓣图书ID

        Returns:
            图书详情信息
        """
        url = f"{self.SUBJECT_URL}/{book_id}/"
        html = self._http_get(url, {})

        if not html:
            return None

        return self._parse_detail(html, book_id)

    def _http_get(self, url: str, params: Dict) -> Optional[str]:
        """发送HTTP请求"""
        if HAS_REQUESTS:
            try:
                resp = self.session.get(url, params=params, timeout=15)
                resp.encoding = 'utf-8'
                return resp.text
            except Exception as e:
                print(f"请求失败: {e}", file=sys.stderr)
                return None
        else:
            import subprocess
            query_parts = [f"{k}={quote(str(v))}" for k, v in params.items()]
            query_str = "&".join(query_parts)
            cmd = f"curl -s -H 'User-Agent: Mozilla/5.0' -H 'Referer: https://book.douban.com/' '{url}?{query_str}'"
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                return result.stdout
            except Exception as e:
                print(f"CURL失败: {e}", file=sys.stderr)
                return None

    def _parse_search_results(self, text: Optional[str]) -> List[Dict[str, Any]]:
        """解析搜索结果"""
        if not text:
            return []

        books = []
        try:
            # 豆瓣API返回的是JSON格式
            data = json.loads(text)
            subjects = data.get('subjects', [])

            for item in subjects:
                book = {
                    'douban_id': str(item.get('id', '')),
                    'title': item.get('title', '未知'),
                    'url': item.get('url', ''),
                    'cover_url': item.get('cover_url', ''),
                    'rating': item.get('rating', {}).get('rate', 0),
                    'rating_count': item.get('rating', {}).get('numRaters', 0),
                }
                books.append(book)
        except json.JSONDecodeError:
            # 尝试解析HTML
            books = self._parse_html_results(text)
        except Exception as e:
            print(f"解析失败: {e}", file=sys.stderr)

        return books

    def _parse_html_results(self, html: Optional[str]) -> List[Dict[str, Any]]:
        """从HTML中解析搜索结果"""
        if not html:
            return []

        books = []
        try:
            # 提取图书ID
            id_pattern = r'/subject/(\d+)/'
            ids = re.findall(id_pattern, html)

            # 提取标题
            title_pattern = r'"title":"([^"]+)"'
            titles = re.findall(title_pattern, html)

            # 提取评分
            rating_pattern = r'"rating":\s*\{"min":\d+,\s*"max":\d+,\s*"rating":([\d.]+)'
            ratings = re.findall(rating_pattern, html)

            for i, bid in enumerate(ids):
                if len(set(ids[:i+1])) == len(ids[:i+1]):  # 去重
                    book = {
                        'douban_id': bid,
                        'title': titles[i] if i < len(titles) else '未知',
                        'rating': float(ratings[i]) if i < len(ratings) else 0,
                    }
                    books.append(book)
        except Exception as e:
            print(f"HTML解析失败: {e}", file=sys.stderr)

        return books

    def _parse_detail(self, html: Optional[str], book_id: str) -> Optional[Dict[str, Any]]:
        """解析图书详情页面"""
        if not html:
            return None

        detail = {}
        try:
            # 提取评分
            rating_pattern = r'"rating":\s*"([\d.]+)"'
            match = re.search(rating_pattern, html)
            if match:
                detail['rating'] = float(match.group(1))

            # 提取评价人数
            count_pattern = r'"ratingCount":\s*(\d+)'
            match = re.search(count_pattern, html)
            if match:
                detail['rating_count'] = int(match.group(1))

            # 提取评价人数（备选）
            if 'rating_count' not in detail:
                count_pattern = r'(\d+)\s*人评价'
                match = re.search(count_pattern, html)
                if match:
                    detail['rating_count'] = int(match.group(1))

            # 提取简介
            summary_pattern = r'"description":\s*"([^"]+)"'
            match = re.search(summary_pattern, html)
            if match:
                detail['summary'] = match.group(1)

            # 提取作者
            author_pattern = r'"author":\s*\[([^\]]+)\]'
            match = re.search(author_pattern, html)
            if match:
                authors = re.findall(r'"([^"]+)"', match.group(1))
                detail['author'] = '、'.join(authors)

            # 提取出版社
            publisher_pattern = r'"publisher":\s*"([^"]+)"'
            match = re.search(publisher_pattern, html)
            if match:
                detail['publisher'] = match.group(1)

            # 提取ISBN
            isbn_pattern = r'"isbn":\s*"([^"]+)"'
            match = re.search(isbn_pattern, html)
            if match:
                detail['isbn'] = match.group(1)

            # 提取热门短评
            comments = self._extract_hot_comments(html)
            if comments:
                detail['hot_comments'] = comments

            detail['douban_id'] = book_id

        except Exception as e:
            print(f"详情解析失败: {e}", file=sys.stderr)

        return detail if detail else None

    def _extract_hot_comments(self, html: Optional[str]) -> List[str]:
        """提取热门短评"""
        if not html:
            return []

        comments = []
        try:
            # 提取短评
            comment_pattern = r'"content":\s*"([^"]{10,200})"'
            matches = re.findall(comment_pattern, html)
            comments = [c.replace('\\"', '"') for c in matches[:5]]  # 取前5条
        except Exception as e:
            print(f"短评提取失败: {e}", file=sys.stderr)

        return comments

    def get_rating_advice(self, rating: float) -> str:
        """根据评分给出推荐建议"""
        if rating >= 9.0:
            return "🌟 强烈推荐"
        elif rating >= 8.0:
            return "👍 推荐"
        elif rating >= 7.0:
            return "📖 可参考"
        elif rating >= 6.0:
            return "🤔 谨慎选择"
        else:
            return "⚠️ 不推荐"

    def format_result(self, books: List[Dict], detail: Optional[Dict] = None) -> str:
        """格式化输出结果"""
        if not books:
            return "❌ 未找到相关图书"

        output = []
        for i, book in enumerate(books[:5], 1):
            rating = book.get('rating', 0)
            advice = self.get_rating_advice(rating)

            output.append(f"{i}. 《{book.get('title', '未知')}》")
            output.append(f"   豆瓣评分：{rating}/10 {advice}")
            output.append(f"   评价人数：{book.get('rating_count', 0)}人")

            if detail and detail.get('author'):
                output.append(f"   作者：{detail.get('author')}")
            if detail and detail.get('publisher'):
                output.append(f"   出版社：{detail.get('publisher')}")
            if detail and detail.get('isbn'):
                output.append(f"   ISBN：{detail.get('isbn')}")

            # 添加热门评论
            if detail and detail.get('hot_comments'):
                output.append("   热门短评：")
                for j, comment in enumerate(detail.get('hot_comments', [])[:3], 1):
                    # 截断过长的评论
                    if len(comment) > 80:
                        comment = comment[:77] + "..."
                    output.append(f"     {j}. {comment}")

            output.append("")

        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='豆瓣图书搜索')
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--id', '-i', help='豆瓣图书ID，获取详情')
    parser.add_argument('--json', '-j', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    searcher = DoubanBookSearcher()

    if args.id:
        # 获取详情
        detail = searcher.get_book_detail(args.id)
        if args.json:
            print(json.dumps(detail, ensure_ascii=False, indent=2))
        else:
            if detail:
                print(f"评分：{detail.get('rating', 0)}/10")
                print(f"评价人数：{detail.get('rating_count', 0)}人")
                if detail.get('author'):
                    print(f"作者：{detail.get('author')}")
                if detail.get('publisher'):
                    print(f"出版社：{detail.get('publisher')}")
                if detail.get('isbn'):
                    print(f"ISBN：{detail.get('isbn')}")
                if detail.get('hot_comments'):
                    print("\n热门短评：")
                    for i, c in enumerate(detail.get('hot_comments', [])[:5], 1):
                        print(f"  {i}. {c}")
            else:
                print("获取详情失败")
    else:
        # 搜索
        books = searcher.search(args.keyword)
        if args.json:
            print(json.dumps(books, ensure_ascii=False, indent=2))
        else:
            print(searcher.format_result(books))


if __name__ == '__main__':
    main()
