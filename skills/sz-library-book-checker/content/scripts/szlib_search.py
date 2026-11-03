#!/usr/bin/env python3
"""
深圳图书馆OPAC图书搜索脚本
查询图书馆藏情况：馆藏地、索书号、可借状态
"""

import json
import sys
import re
import argparse
from typing import Optional, Dict, List, Any
from urllib.parse import quote

# 尝试导入requests，如果不可用则使用curl
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class SZLibrarySearcher:
    """深圳图书馆OPAC搜索器"""

    BASE_URL = "https://opac.szlib.org.cn"
    SEARCH_URL = f"{BASE_URL}/search/search.action"
    DETAIL_URL = f"{BASE_URL}/search/detail.service"

    # 馆藏地映射
    LOCATION_MAP = {
        "SZUL-主馆-基藏": "深圳图书馆主馆五楼基藏库",
        "SZUL-主馆-开架": "深圳图书馆主馆三楼开架书库",
        "SZUL-主馆-少儿": "深圳图书馆主馆二楼少儿服务区",
        "SZUL-南山分馆": "南山图书馆分馆",
        "SZUL-福田分馆": "福田图书馆分馆",
        "SZUL-罗湖分馆": "罗湖图书馆分馆",
        "SZUL-宝安分馆": "宝安图书馆分馆",
    }

    def __init__(self):
        self.session = None
        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/html',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            })

    def search(self, keyword: str, search_type: str = "title") -> List[Dict[str, Any]]:
        """
        搜索图书

        Args:
            keyword: 搜索关键词（书名/ISBN/作者）
            search_type: 搜索类型 (title/isbn/author)

        Returns:
            图书列表
        """
        if not keyword:
            return []

        # 根据搜索类型设置查询参数
        if search_type == "isbn":
            query_field = "ISBN"
        elif search_type == "author":
            query_field = "author"
        else:
            query_field = "title"

        params = {
            'query': keyword,
            'field': query_field,
            'sort': ' relevance ',
            'curPage': 1,
            'matchType': ' exact ',
            'mediaType': 'BK',
        }

        result = self._http_get(self.SEARCH_URL, params)
        return self._parse_search_results(result)

    def get_book_detail(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        获取图书详情

        Args:
            record_id: 记录ID

        Returns:
            图书详情信息
        """
        params = {'id': record_id}
        result = self._http_get(self.DETAIL_URL, params)
        return self._parse_detail(result)

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
            # 使用curl作为备选
            import subprocess
            query_parts = [f"{k}={quote(str(v))}" for k, v in params.items()]
            query_str = "&".join(query_parts)
            cmd = f"curl -s -H 'User-Agent: Mozilla/5.0' '{url}?{query_str}'"
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                return result.stdout
            except Exception as e:
                print(f"CURL失败: {e}", file=sys.stderr)
                return None

    def _parse_search_results(self, html: Optional[str]) -> List[Dict[str, Any]]:
        """解析搜索结果页面"""
        if not html:
            return []

        books = []
        # 简单解析HTML中的图书信息
        # 实际项目中需要根据深圳图书馆OPAC的实际HTML结构进行调整
        try:
            # 提取记录ID
            id_pattern = r'record_(\d+)'
            ids = re.findall(id_pattern, html)

            # 提取标题
            title_pattern = r'class="title"[^>]*>([^<]+)'
            titles = re.findall(title_pattern, html)

            # 提取作者
            author_pattern = r'class="author"[^>]*>([^<]+)'
            authors = re.findall(author_pattern, html)

            for i, bid in enumerate(ids):
                book = {
                    'record_id': bid,
                    'title': titles[i] if i < len(titles) else '未知',
                    'author': authors[i] if i < len(authors) else '未知',
                }
                books.append(book)
        except Exception as e:
            print(f"解析失败: {e}", file=sys.stderr)

        return books

    def _parse_detail(self, html: Optional[str]) -> Optional[Dict[str, Any]]:
        """解析图书详情页面"""
        if not html:
            return None

        detail = {}
        try:
            # 提取索书号
            call_pattern = r'索书号[:：]\s*([A-Z0-9/\-]+)'
            match = re.search(call_pattern, html)
            if match:
                detail['call_number'] = match.group(1)

            # 提取ISBN
            isbn_pattern = r'ISBN[:：]\s*([0-9\-X]+)'
            match = re.search(isbn_pattern, html)
            if match:
                detail['isbn'] = match.group(1)

            # 提取馆藏信息
            loc_pattern = r'馆藏地[:：]\s*([^<\n]+)'
            locs = re.findall(loc_pattern, html)
            detail['locations'] = [self._map_location(loc.strip()) for loc in locs]

            # 提取可借状态
            avail_pattern = r'可借[:：]\s*(\d+)'
            avail_matches = re.findall(avail_pattern, html)
            detail['available'] = sum(int(x) for x in avail_matches) if avail_matches else 0

        except Exception as e:
            print(f"详情解析失败: {e}", file=sys.stderr)

        return detail if detail else None

    def _map_location(self, code: str) -> str:
        """映射馆藏地代码为中文名称"""
        return self.LOCATION_MAP.get(code, code)

    def format_result(self, books: List[Dict], detail: Optional[Dict] = None) -> str:
        """格式化输出结果"""
        if not books:
            return "❌ 未找到相关图书"

        output = []
        for i, book in enumerate(books[:5], 1):
            output.append(f"{i}. 《{book.get('title', '未知')}》")
            output.append(f"   作者：{book.get('author', '未知')}")
            if detail and detail.get('call_number'):
                output.append(f"   索书号：{detail.get('call_number')}")
            if detail and detail.get('locations'):
                locs = "、".join(detail.get('locations', []))
                output.append(f"   馆藏地：{locs}")
            if detail and detail.get('available') is not None:
                avail = detail.get('available', 0)
                status = "✅ 可借" if avail > 0 else "❌ 已借出"
                output.append(f"   可借数量：{avail} {status}")
            output.append("")

        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='深圳图书馆OPAC图书搜索')
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--type', '-t', choices=['title', 'isbn', 'author'],
                      default='title', help='搜索类型')
    parser.add_argument('--detail', '-d', help='图书ID，获取详情')
    parser.add_argument('--json', '-j', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    searcher = SZLibrarySearcher()

    if args.detail:
        # 获取详情
        detail = searcher.get_book_detail(args.detail)
        if args.json:
            print(json.dumps(detail, ensure_ascii=False, indent=2))
        else:
            if detail:
                print(f"索书号：{detail.get('call_number', '未知')}")
                print(f"ISBN：{detail.get('isbn', '未知')}")
                print(f"馆藏地：{', '.join(detail.get('locations', []))}")
                print(f"可借数量：{detail.get('available', 0)}")
            else:
                print("获取详情失败")
    else:
        # 搜索
        books = searcher.search(args.keyword, args.type)
        if args.json:
            print(json.dumps(books, ensure_ascii=False, indent=2))
        else:
            print(searcher.format_result(books))


if __name__ == '__main__':
    main()
