#!/usr/bin/env python3
"""
综合图书查询脚本
整合深圳图书馆OPAC和豆瓣查询，生成完整的图书信息报告
"""

import json
import sys
import argparse
from typing import Optional, Dict, Any

# 导入子模块
from szlib_search import SZLibrarySearcher
from douban_search import DoubanBookSearcher


class BookChecker:
    """综合图书查询器"""

    def __init__(self):
        self.szlib = SZLibrarySearcher()
        self.douban = DoubanBookSearcher()

    def check_book(self, keyword: str, search_type: str = "title") -> Dict[str, Any]:
        """
        综合查询图书信息

        Args:
            keyword: 搜索关键词
            search_type: 搜索类型

        Returns:
            综合报告字典
        """
        report = {
            'keyword': keyword,
            'library': {},
            'douban': {},
            'suggestion': '',
        }

        # 1. 查询深圳图书馆
        print("🔍 正在查询深圳图书馆OPAC...")
        books = self.szlib.search(keyword, search_type)

        if books:
            report['library']['found'] = True
            report['library']['books'] = books

            # 获取第一本书的详情
            first_book = books[0]
            record_id = first_book.get('record_id')

            if record_id:
                detail = self.szlib.get_book_detail(record_id)
                if detail:
                    report['library']['detail'] = detail
        else:
            report['library']['found'] = False

        # 2. 查询豆瓣
        print("🔍 正在查询豆瓣读书...")
        douban_books = self.douban.search(keyword)

        if douban_books:
            report['douban']['found'] = True
            report['douban']['books'] = douban_books

            # 获取第一本书的详情（评分等）
            first_book = douban_books[0]
            douban_id = first_book.get('douban_id')

            if douban_id:
                detail = self.douban.get_book_detail(douban_id)
                if detail:
                    report['douban']['detail'] = detail
        else:
            report['douban']['found'] = False

        # 3. 生成建议
        report['suggestion'] = self._generate_suggestion(report)

        return report

    def _generate_suggestion(self, report: Dict) -> str:
        """根据查询结果生成借阅建议"""
        suggestions = []

        lib_found = report['library'].get('found', False)
        douban_found = report['douban'].get('found', False)

        if not lib_found and not douban_found:
            return "❌ 未找到该图书，建议检查书名是否正确。"

        if not lib_found:
            suggestions.append("⚠️ 该书不在深圳图书馆藏中")
            if douban_found:
                suggestions.append("但豆瓣有收录，可考虑网上阅读或购买")
            return "；".join(suggestions)

        # 检查馆藏情况
        detail = report['library'].get('detail', {})
        avail = detail.get('available', 0)

        if avail > 0:
            suggestions.append("✅ 深圳图书馆有藏书且可借")
            suggestions.append(f"   馆藏地：{', '.join(detail.get('locations', ['未知']))}")
        else:
            suggestions.append("❌ 深圳图书馆有藏书但已全部借出")
            suggestions.append("   可预约或选择其他分馆")

        # 添加豆瓣参考
        if douban_found:
            douban_detail = report['douban'].get('detail', {})
            rating = douban_detail.get('rating', 0)

            if rating >= 8.0:
                suggestions.append(f"⭐ 豆瓣评分 {rating}/10，评价较好，值得借阅")
            elif rating >= 6.0:
                suggestions.append(f"📖 豆瓣评分 {rating}/10，质量一般，视需求借阅")
            else:
                suggestions.append(f"⚠️ 豆瓣评分 {rating}/10，评价较低，谨慎选择")

        return "\n".join(suggestions)

    def format_report(self, report: Dict) -> str:
        """格式化综合报告"""
        output = []
        output.append("=" * 50)
        output.append("📚 图书信息综合报告")
        output.append("=" * 50)
        output.append(f"搜索关键词：{report['keyword']}")
        output.append("")

        # 图书馆信息
        output.append("【深圳图书馆馆藏情况】")
        lib = report['library']

        if not lib.get('found'):
            output.append("  未找到该图书")
        else:
            books = lib.get('books', [])
            if books:
                first = books[0]
                output.append(f"  书名：《{first.get('title', '未知')}》")
                output.append(f"  作者：{first.get('author', '未知')}")

            detail = lib.get('detail', {})
            if detail:
                output.append(f"  索书号：{detail.get('call_number', '未知')}")
                locs = detail.get('locations', [])
                if locs:
                    output.append(f"  馆藏地：{', '.join(locs)}")
                avail = detail.get('available', 0)
                status = "✅ 可借" if avail > 0 else "❌ 已借出"
                output.append(f"  可借数量：{avail} {status}")

        output.append("")

        # 豆瓣信息
        output.append("【豆瓣书评参考】")
        douban = report['douban']

        if not douban.get('found'):
            output.append("  豆瓣无记录")
        else:
            books = douban.get('books', [])
            if books:
                first = books[0]
                rating = first.get('rating', 0)
                advice = self.douban.get_rating_advice(rating)
                output.append(f"  书名：《{first.get('title', '未知')}》")
                output.append(f"  豆瓣评分：{rating}/10 {advice}")
                output.append(f"  评价人数：{first.get('rating_count', 0)}人")

            detail = douban.get('detail', {})
            if detail:
                if detail.get('author'):
                    output.append(f"  作者：{detail.get('author')}")
                if detail.get('publisher'):
                    output.append(f"  出版社：{detail.get('publisher')}")
                if detail.get('isbn'):
                    output.append(f"  ISBN：{detail.get('isbn')}")

                comments = detail.get('hot_comments', [])
                if comments:
                    output.append("  热门短评：")
                    for i, c in enumerate(comments[:3], 1):
                        c = c[:60] + "..." if len(c) > 60 else c
                        output.append(f"    {i}. {c}")

        output.append("")
        output.append("【综合建议】")
        output.append(report.get('suggestion', ''))
        output.append("")
        output.append("=" * 50)

        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='综合图书查询')
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--type', '-t', choices=['title', 'isbn', 'author'],
                      default='title', help='搜索类型')
    parser.add_argument('--json', '-j', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    checker = BookChecker()
    report = checker.check_book(args.keyword, args.type)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(checker.format_report(report))


if __name__ == '__main__':
    main()
