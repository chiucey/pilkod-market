#!/usr/bin/env python3
"""
B站数据抓取核心模块
支持视频信息、UP主信息、排行榜、搜索结果等多种数据抓取
"""

import json
import re
import time
import random
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode
from dataclasses import dataclass, asdict

try:
    import requests
except ImportError:
    print("请先安装 requests: pip install requests")
    raise

@dataclass
class VideoInfo:
    """视频信息数据结构"""
    bvid: str
    title: str
    author: str
    mid: int  # UP主ID
    publish_time: str
    description: str
    duration: int  # 秒
    view: int  # 播放量
    like: int  # 点赞
    coin: int  # 投币
    favorite: int  # 收藏
    share: int  # 分享
    danmaku: int  # 弹幕
    reply: int  # 评论
    pid: int = 0  # 分区ID

    def to_dict(self) -> Dict:
        return asdict(self)


class BilibiliScraper:
    """B站数据抓取器"""

    def __init__(self, timeout: int = 30, retry: int = 3):
        self.timeout = timeout
        self.retry = retry
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com',
            'Accept': 'application/json, text/plain, */*',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """发送请求并处理响应"""
        for attempt in range(self.retry):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                if data.get('code') == 0:
                    return data.get('data', {})
                else:
                    print(f"API返回错误: {data.get('message', '未知错误')}")
                    return None
            except requests.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/{self.retry}): {e}")
                time.sleep(random.uniform(1, 3))
        return None

    def get_video_info(self, bvid: str) -> Optional[VideoInfo]:
        """获取视频详细信息"""
        url = "https://api.bilibili.com/x/web-interface/view"
        params = {'bvid': bvid}

        data = self._request(url, params)
        if not data:
            return None

        stat = data.get('stat', {})

        video_info = VideoInfo(
            bvid=data.get('bvid', ''),
            title=data.get('title', ''),
            author=data.get('owner', {}).get('name', ''),
            mid=data.get('owner', {}).get('mid', 0),
            publish_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data.get('pubdate', 0))),
            description=data.get('desc', ''),
            duration=data.get('duration', 0),
            view=stat.get('view', 0),
            like=stat.get('like', 0),
            coin=stat.get('coin', 0),
            favorite=stat.get('favorite', 0),
            share=stat.get('share', 0),
            danmaku=stat.get('danmaku', 0),
            reply=stat.get('reply', 0),
            pid=data.get('tids', {}).get(data.get('tid', 0), {}).get('pid', 0) if isinstance(data.get('tids'), dict) else 0
        )

        return video_info

    def get_rank_list(self, rid: int = 0, type_: str = 'all', day: int = 3) -> List[Dict]:
        """
        获取排行榜数据
        :param rid: 分区ID，0表示全站
        :param type_: 排行榜类型 (all, monthly, weekly)
        :param day: 统计周期 (1, 3, 7, 30)
        """
        url = "https://api.bilibili.com/x/web-interface/ranking/v2"
        params = {'rid': rid, 'type': type_}

        data = self._request(url, params)
        if not data:
            return []

        return data.get('list', [])

    def search(self, keyword: str, page: int = 1, page_size: int = 20,
               search_type: str = 'video', order: str = 'totalrank') -> List[Dict]:
        """
        搜索B站内容
        :param keyword: 搜索关键词
        :param page: 页码
        :param page_size: 每页数量
        :param search_type: 搜索类型 (video, bili_user, article)
        :param order: 排序方式 (totalrank, click, pubdate, stow)
        """
        url = "https://api.bilibili.com/x/web-interface/search/type"
        params = {
            'search_type': search_type,
            'keyword': keyword,
            'page': page,
            'pagesize': page_size,
            'order': order,
        }

        data = self._request(url, params)
        if not data:
            return []

        return data.get('result', [])

    def get_up_info(self, mid: int) -> Optional[Dict]:
        """获取UP主信息"""
        url = "https://api.bilibili.com/x/web-interface/card"
        params = {'mid': mid}

        data = self._request(url, params)
        if not data:
            return None

        card = data.get('card', {})
        return {
            'mid': mid,
            'name': card.get('name', ''),
            'sex': card.get('sex', ''),
            'face': card.get('face', ''),
            'sign': card.get('sign', ''),
            'fans': card.get('fans', 0),
            'friend': card.get('friend', 0),
            'attention': card.get('attention', 0),
            'level': card.get('level_info', {}).get('current_level', 0),
            'vip_status': card.get('vip', {}).get('status', 0),
            'archive_count': data.get('archive_count', 0),
            'like_num': data.get('like_num', 0),
        }

    def get_comments(self, oid: str, page: int = 1, mode: int = 3,
                     type_: int = 1, ps: int = 20) -> Dict:
        """
        获取视频评论
        :param oid: 视频BV号或评论资源ID
        :param page: 页码
        :param mode: 排序模式 (1:最新, 2:最热, 3:按回复)
        :param type_: 资源类型 (1:视频, 11:专栏)
        """
        url = "https://api.bilibili.com/x/v2/reply"
        params = {
            'oid': oid,
            'pn': page,
            'type': type_,
            'ps': ps,
            'mode': mode,
        }

        data = self._request(url, params)
        if not data:
            return {'replies': [], 'count': 0}

        return {
            'replies': data.get('replies', []) or [],
            'count': data.get('cursor', {}).get('all_count', 0),
            'page': page,
            'mode': mode,
        }

    def get_video_list_by_tag(self, tag_name: str, page: int = 1, page_size: int = 30) -> Dict:
        """获取标签下的视频列表"""
        # 先获取标签ID
        tag_url = "https://api.bilibili.com/x/tag/info"
        tag_params = {'tag_name': tag_name}
        tag_data = self._request(tag_url, tag_params)

        if not tag_data:
            return {'videos': [], 'count': 0}

        tag_id = tag_data.get('tag_id', 0)

        # 获取标签下视频
        url = "https://api.bilibili.com/x/tag/archive/tags"
        params = {
            'tag_id': tag_id,
            'pn': page,
            'ps': page_size,
        }

        data = self._request(url, params)
        if not data:
            return {'videos': [], 'count': 0}

        return {
            'videos': data.get('archives', []),
            'count': data.get('count', 0),
            'tag_name': tag_name,
            'tag_id': tag_id,
        }


def parse_bvid(input_str: str) -> Optional[str]:
    """
    解析输入的B站链接或BV号
    支持格式:
    - BV1xx411c7XZ
    - https://www.bilibili.com/video/BV1xx411c7XZ/
    - https://b23.tv/xxx
    """
    if not input_str:
        return None

    # 直接是BV号
    if input_str.startswith('BV'):
        return input_str.strip()

    # 解析URL
    bvid_match = re.search(r'BV[a-zA-Z0-9]{10}', input_str)
    if bvid_match:
        return bvid_match.group(0)

    # 解析短链接 (需要重定向获取)
    if 'b23.tv' in input_str:
        try:
            response = requests.head(input_str, allow_redirects=True, timeout=10)
            bvid_match = re.search(r'BV[a-zA-Z0-9]{10}', response.url)
            if bvid_match:
                return bvid_match.group(0)
        except Exception as e:
            print(f"短链接解析失败: {e}")

    return None


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='B站数据抓取工具')
    parser.add_argument('--bvid', '-b', help='视频BV号或链接')
    parser.add_argument('--mid', '-m', type=int, help='UP主MID')
    parser.add_argument('--rank', '-r', action='store_true', help='获取排行榜')
    parser.add_argument('--search', '-s', help='搜索关键词')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['json', 'csv'], default='json', help='输出格式')

    args = parser.parse_args()
    scraper = BilibiliScraper()

    results = []

    if args.bvid:
        bvid = parse_bvid(args.bvid)
        if not bvid:
            print("无法解析BV号，请检查输入格式")
            return

        video = scraper.get_video_info(bvid)
        if video:
            print(f"视频: {video.title}")
            print(f"UP主: {video.author}")
            print(f"播放: {video.view:,} | 点赞: {video.like:,} | 投币: {video.coin:,} | 收藏: {video.favorite:,}")
            results.append(video.to_dict())

    elif args.mid:
        up_info = scraper.get_up_info(args.mid)
        if up_info:
            print(f"UP主: {up_info['name']}")
            print(f"粉丝: {up_info['fans']:,}")
            print(f"作品数: {up_info['archive_count']}")
            results.append(up_info)

    elif args.rank:
        rank_list = scraper.get_rank_list()
        for i, video in enumerate(rank_list[:10], 1):
            print(f"{i}. {video.get('title', '')} - {video.get('owner', {}).get('name', '')}")
            print(f"   播放: {video.get('stat', {}).get('view', 0):,} | 点赞: {video.get('stat', {}).get('like', 0):,}")
        results = rank_list

    elif args.search:
        search_results = scraper.search(args.search)
        for i, item in enumerate(search_results[:10], 1):
            print(f"{i}. {item.get('title', '').replace('<em class=\"search-highlight\">', '').replace('</em>', '')}")
        results = search_results

    # 保存结果
    if args.output and results:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.format == 'json':
                json.dump(results, f, ensure_ascii=False, indent=2)
            else:
                import csv
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
        print(f"结果已保存到: {args.output}")


if __name__ == '__main__':
    main()
