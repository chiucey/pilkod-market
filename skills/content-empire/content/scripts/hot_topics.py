#!/usr/bin/env python3
"""
微信公众号选题热榜获取脚本
支持获取多个平台的热榜信息，帮助快速选题

使用方法：
    python3 hot_topics.py                    # 获取所有平台热榜
    python3 hot_topics.py weibo,zhihu       # 获取指定平台
    python3 hot_topics.py --list            # 列出所有支持的平台
"""

import json
import sys
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("请先安装 requests 库：pip install requests")
    sys.exit(1)


class HotTopicsAggregator:
    """热榜聚合器"""

    # DailyHotApi 公共接口（备用）
    DEFAULT_API_URL = "https://api.pearktrue.cn/api/hot/"

    # 支持的平台配置
    PLATFORMS = {
        "weibo": {"name": "微博热搜", "endpoint": "weibo"},
        "zhihu": {"name": "知乎热榜", "endpoint": "zhihu"},
        "bilibili": {"name": "B站热门", "endpoint": "bilibili"},
        "douyin": {"name": "抖音热点", "endpoint": "douyin"},
        "baidu": {"name": "百度热搜", "endpoint": "baidu"},
        "csdn": {"name": "CSDN热榜", "endpoint": "csdn"},
        "juejin": {"name": "掘金热榜", "endpoint": "juejin"},
    }

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or self.DEFAULT_API_URL

    def fetch_hot_topics(self, platform: str, limit: int = 10) -> List[Dict]:
        """获取单个平台的热榜"""
        try:
            url = f"{self.api_url}{self.PLATFORMS[platform]['endpoint']}/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # 解析返回数据（根据不同API格式调整）
            if "data" in data:
                items = data["data"]
            elif "result" in data:
                items = data["result"]
            else:
                items = data.get("list", [])

            # 返回指定数量的条目
            return items[:limit] if isinstance(items, list) else []

        except requests.RequestException as e:
            print(f"获取 {platform} 热榜失败: {e}")
            return []
        except (KeyError, json.JSONDecodeError) as e:
            print(f"解析 {platform} 数据失败: {e}")
            return []

    def fetch_all(self, platforms: Optional[List[str]] = None, limit: int = 10) -> Dict[str, List]:
        """获取所有或指定平台的热榜"""
        if platforms is None:
            platforms = list(self.PLATFORMS.keys())

        results = {}
        for platform in platforms:
            if platform in self.PLATFORMS:
                results[platform] = self.fetch_hot_topics(platform, limit)

        return results

    def format_output(self, results: Dict[str, List]) -> str:
        """格式化输出"""
        output = []
        platform_names = {k: v["name"] for k, v in self.PLATFORMS.items()}

        for platform, items in results.items():
            if not items:
                continue

            output.append(f"\n{'='*50}")
            output.append(f"📊 {platform_names.get(platform, platform)}")
            output.append(f"{'='*50}")

            for i, item in enumerate(items, 1):
                # 尝试获取标题
                if isinstance(item, dict):
                    title = item.get("title") or item.get("word") or item.get("name", "未知")
                    hot_value = item.get("hot", item.get("value", ""))
                elif isinstance(item, str):
                    title = item
                    hot_value = ""
                else:
                    title = str(item)
                    hot_value = ""

                if hot_value:
                    output.append(f"{i:2}. {title} [{hot_value}]")
                else:
                    output.append(f"{i:2}. {title}")

        return "\n".join(output)

    def list_platforms(self) -> None:
        """列出所有支持的平台"""
        print("\n支持的平台列表：")
        print("-" * 40)
        for key, info in self.PLATFORMS.items():
            print(f"  • {info['name']:12} ({key})")


def main():
    """主函数"""
    aggregator = HotTopicsAggregator()

    # 解析命令行参数
    if "--list" in sys.argv:
        aggregator.list_platforms()
        return

    # 获取指定平台
    platforms = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--") and arg:
            platforms = arg.split(",")

    # 获取热榜
    results = aggregator.fetch_all(platforms, limit=10)

    # 输出结果
    if results:
        print(aggregator.format_output(results))
        print("\n" + "="*50)
        print("💡 提示：选择感兴趣的话题，结合账号定位进行创作")
        print("="*50)
    else:
        print("\n获取热榜失败，请检查网络连接或稍后重试。")
        print("\n备用方案：手动访问以下链接查看热榜")
        print("-" * 40)
        aggregator.list_platforms()


if __name__ == "__main__":
    main()
