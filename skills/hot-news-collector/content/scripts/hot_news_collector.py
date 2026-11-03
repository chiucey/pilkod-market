#!/usr/bin/env python3
"""
热点新闻收集器 - 获取多平台实时热搜数据

支持平台:
- 今日头条
- 新浪微博
- 百度贴吧
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import urllib.request
import ssl


class HotNewsCollector:
    """热点新闻收集器类"""

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.news_list: List[Dict] = []
        # 创建 SSL 上下文
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def _make_request(self, url: str, headers: Optional[Dict] = None) -> Optional[str]:
        """发送 HTTP 请求获取数据"""
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/html, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=10) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"请求失败: {url}, 错误: {e}")
            return None

    def get_toutiao_hot(self) -> List[Dict]:
        """获取今日头条热榜"""
        print("正在获取今日头条热榜...")
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=hot_board&pd=wenda&tab=0"

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.toutiao.com/',
            }
            response = self._make_request(url, headers)

            if response:
                result = json.loads(response)
                if 'data' in result:
                    for i, item in enumerate(result['data'][:50], 1):
                        self.news_list.append({
                            "序号": i,
                            "标题": item.get('Title', item.get('word', '')),
                            "来源": "今日头条",
                            "分类": item.get('Category', '热榜'),
                            "链接": item.get('Url', item.get('url', ''))
                        })
        except Exception as e:
            print(f"获取今日头条热榜失败: {e}")

    def get_weibo_hot(self) -> List[Dict]:
        """获取新浪微博热搜榜"""
        print("正在获取新浪微博热搜...")
        url = "https://weibo.com/ajax/side/hotSearch"

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://weibo.com/',
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'XMLHttpRequest',
            }
            response = self._make_request(url, headers)

            if response:
                result = json.loads(response)
                if result.get('ok') == 1 and 'data' in result:
                    hot_list = result['data'].get('realtime', [])
                    for i, item in enumerate(hot_list[:50], 1):
                        self.news_list.append({
                            "序号": i,
                            "标题": item.get('word', item.get('note', '')),
                            "来源": "新浪微博",
                            "分类": item.get('category', '热搜'),
                            "链接": f"https://s.weibo.com/weibo?q={item.get('word', '')}"
                        })
        except Exception as e:
            print(f"获取微博热搜失败: {e}")

    def get_tieba_hot(self) -> List[Dict]:
        """获取百度贴吧热搜"""
        print("正在获取百度贴吧热搜...")
        url = "https://tieba.baidu.com/hottopic/browse/topicList"

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://tieba.baidu.com/',
                'Accept': 'application/json, */*',
            }
            response = self._make_request(url, headers)

            if response:
                result = json.loads(response)
                if 'data' in result and 'bang_topic' in result['data']:
                    topics = result['data']['bang_topic']['topic_list']
                    for i, item in enumerate(topics[:50], 1):
                        self.news_list.append({
                            "序号": i,
                            "标题": item.get('topic_name', item.get('title', '')),
                            "来源": "百度贴吧",
                            "分类": item.get('category', '热帖'),
                            "链接": f"https://tieba.baidu.com/topic/hottopic?id={item.get('topic_id', '')}"
                        })
        except Exception as e:
            print(f"获取百度贴吧热搜失败: {e}")

    def get_all_platforms(self) -> List[Dict]:
        """获取所有平台热搜"""
        self.news_list = []
        print(f"开始获取热搜数据 - {self.timestamp}")
        print("-" * 50)

        self.get_toutiao_hot()
        time.sleep(0.3)

        self.get_weibo_hot()
        time.sleep(0.3)

        self.get_tieba_hot()

        print("-" * 50)
        print(f"获取完成! 共 {len(self.news_list)} 条热搜")

        return self.news_list

    def get_platform(self, platform: str) -> List[Dict]:
        """获取指定平台热搜"""
        platform = platform.lower()
        self.news_list = []

        if platform == "toutiao" or platform == "今日头条":
            self.get_toutiao_hot()
        elif platform == "weibo" or platform == "微博":
            self.get_weibo_hot()
        elif platform == "tieba" or platform == "百度贴吧":
            self.get_tieba_hot()
        else:
            print(f"不支持的平台: {platform}")
            return []

        return self.news_list

    def format_table(self) -> str:
        """格式化输出为表格"""
        if not self.news_list:
            return "暂无数据"

        # 计算每列的最大宽度
        headers = ["序号", "标题", "来源", "分类", "链接"]
        col_widths = {
            "序号": 4,
            "标题": 30,
            "来源": 10,
            "分类": 8,
            "链接": 40
        }

        # 构建表格
        lines = []

        # 表头
        header_line = "|" + "|".join([
            headers[i].center(col_widths[headers[i]]) for i in range(5)
        ]) + "|"
        separator = "+" + "+".join(["-" * (col_widths[headers[i]] + 2) for i in range(5)]) + "+"

        lines.append(separator)
        lines.append(header_line)
        lines.append(separator)

        # 数据行
        for item in self.news_list[:50]:
            title = item['标题'][:28] + ".." if len(item['标题']) > 30 else item['标题']
            url = item['链接'][:38] + ".." if len(item['链接']) > 40 else item['链接']

            row = "|{0}|{1}|{2}|{3}|{4}|".format(
                str(item['序号']).center(col_widths["序号"]),
                title.center(col_widths["标题"]),
                item['来源'].center(col_widths["来源"]),
                item['分类'].center(col_widths["分类"]),
                url.center(col_widths["链接"])
            )
            lines.append(row)

        lines.append(separator)

        return "\n".join(lines)

    def format_list(self) -> str:
        """格式化输出为列表"""
        if not self.news_list:
            return "暂无数据"

        lines = []
        lines.append("")
        lines.append("=" * 70)
        lines.append(f"  热点热搜数据  |  更新时间: {self.timestamp}  |  共 {len(self.news_list)} 条")
        lines.append("=" * 70)
        lines.append("")

        for item in self.news_list[:50]:
            lines.append(f"{item['序号']:2d}. {item['标题']}")
            lines.append(f"    来源: {item['来源']}  |  分类: {item['分类']}")
            lines.append(f"    链接: {item['链接']}")
            lines.append("")

        return "\n".join(lines)

    def get_data(self) -> List[Dict]:
        """获取数据列表"""
        return self.news_list


def main():
    """主函数"""
    collector = HotNewsCollector()
    collector.get_all_platforms()

    # 输出表格形式
    print(collector.format_table())


if __name__ == "__main__":
    main()
