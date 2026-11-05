#!/usr/bin/env python3
"""
代理池管理器
支持多种代理类型（HTTP/HTTPS/SOCKS5），自动切换故障代理
"""

import json
import asyncio
import aiohttp
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import random


class ProxyManager:
    """代理池管理器"""

    def __init__(self, proxy_list: Optional[List[str]] = None, config_file: Optional[str] = None):
        """
        初始化代理池管理器

        Args:
            proxy_list: 代理列表，格式 ["http://user:pass@host:port", "socks5://host:port"]
            config_file: 代理配置文件路径
        """
        self.proxies = []
        self.failed_proxies = {}  # {proxy: {"failed_count": int, "last_failed": datetime}}
        self.current_proxy_index = 0
        self.health_check_timeout = 10
        self.max_failed_count = 3

        # 从配置文件加载代理
        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)

        # 添加代理列表
        if proxy_list:
            self.proxies.extend(proxy_list)

    def load_from_file(self, file_path: str) -> bool:
        """
        从配置文件加载代理

        Args:
            file_path: 配置文件路径

        Returns:
            是否加载成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.proxies = config.get('proxies', [])
            return True
        except Exception as e:
            print(f"加载代理配置文件失败: {e}")
            return False

    def save_to_file(self, file_path: str) -> bool:
        """
        保存代理配置到文件

        Args:
            file_path: 配置文件路径

        Returns:
            是否保存成功
        """
        try:
            config = {
                "proxies": self.proxies,
                "failed_proxies": {
                    proxy: {
                        "failed_count": info["failed_count"],
                        "last_failed": info["last_failed"].isoformat()
                    }
                    for proxy, info in self.failed_proxies.items()
                }
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存代理配置文件失败: {e}")
            return False

    def add_proxy(self, proxy: str) -> bool:
        """
        添加代理

        Args:
            proxy: 代理地址

        Returns:
            是否添加成功
        """
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            return True
        return False

    def remove_proxy(self, proxy: str) -> bool:
        """
        移除代理

        Args:
            proxy: 代理地址

        Returns:
            是否移除成功
        """
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            if proxy in self.failed_proxies:
                del self.failed_proxies[proxy]
            return True
        return False

    def get_proxy(self, strategy: str = "round_robin") -> Optional[str]:
        """
        获取代理

        Args:
            strategy: 代理选择策略
                - round_robin: 轮询
                - random: 随机
                - least_failed: 失败次数最少

        Returns:
            代理地址
        """
        if not self.proxies:
            return None

        # 过滤掉失败次数过多的代理
        available_proxies = []
        for proxy in self.proxies:
            failed_info = self.failed_proxies.get(proxy, {"failed_count": 0})
            if failed_info["failed_count"] < self.max_failed_count:
                available_proxies.append(proxy)

        if not available_proxies:
            # 所有代理都失败了，重置失败计数
            print("⚠️ 所有代理都已失败，重置失败计数")
            self.failed_proxies.clear()
            available_proxies = self.proxies.copy()

        # 根据策略选择代理
        if strategy == "random":
            return random.choice(available_proxies)
        elif strategy == "least_failed":
            return min(available_proxies, key=lambda p: self.failed_proxies.get(p, {}).get("failed_count", 0))
        else:  # round_robin
            proxy = available_proxies[self.current_proxy_index % len(available_proxies)]
            self.current_proxy_index += 1
            return proxy

    def mark_failed(self, proxy: str) -> None:
        """
        标记代理失败

        Args:
            proxy: 代理地址
        """
        if proxy not in self.failed_proxies:
            self.failed_proxies[proxy] = {"failed_count": 0, "last_failed": None}

        self.failed_proxies[proxy]["failed_count"] += 1
        self.failed_proxies[proxy]["last_failed"] = datetime.now()

        print(f"⚠️ 代理失败: {proxy} (失败次数: {self.failed_proxies[proxy]['failed_count']})")

    def mark_success(self, proxy: str) -> None:
        """
        标记代理成功

        Args:
            proxy: 代理地址
        """
        if proxy in self.failed_proxies:
            self.failed_proxies[proxy]["failed_count"] = 0

    async def check_proxy_health(self, proxy: str, test_url: str = "http://httpbin.org/ip") -> bool:
        """
        检查代理健康状态

        Args:
            proxy: 代理地址
            test_url: 测试 URL

        Returns:
            代理是否健康
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)) as session:
                async with session.get(test_url, proxy=proxy) as response:
                    if response.status == 200:
                        self.mark_success(proxy)
                        print(f"✅ 代理健康: {proxy}")
                        return True
                    else:
                        self.mark_failed(proxy)
                        return False
        except Exception as e:
            self.mark_failed(proxy)
            print(f"❌ 代理检查失败: {proxy} - {e}")
            return False

    async def check_all_proxies(self, test_url: str = "http://httpbin.org/ip") -> Dict[str, bool]:
        """
        检查所有代理健康状态

        Args:
            test_url: 测试 URL

        Returns:
            代理健康状态 {proxy: is_healthy}
        """
        if not self.proxies:
            return {}

        print(f"🔍 开始检查 {len(self.proxies)} 个代理...")

        tasks = [self.check_proxy_health(proxy, test_url) for proxy in self.proxies]
        results = await asyncio.gather(*tasks)

        health_status = dict(zip(self.proxies, results))

        healthy_count = sum(1 for status in health_status.values() if status)
        print(f"✅ 健康检查完成: {healthy_count}/{len(self.proxies)} 个代理可用")

        return health_status

    def cleanup_old_failed_proxies(self, hours: int = 24) -> int:
        """
        清理旧的失败记录

        Args:
            hours: 保留最近多少小时的失败记录

        Returns:
            清理的代理数量
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        removed_count = 0

        for proxy, info in list(self.failed_proxies.items()):
            if info["last_failed"] and info["last_failed"] < cutoff_time:
                del self.failed_proxies[proxy]
                removed_count += 1

        if removed_count > 0:
            print(f"🧹 清理了 {removed_count} 个旧失败记录")

        return removed_count

    def get_stats(self) -> Dict:
        """
        获取代理池统计信息

        Returns:
            统计信息
        """
        return {
            "total_proxies": len(self.proxies),
            "available_proxies": len([p for p in self.proxies if self.failed_proxies.get(p, {}).get("failed_count", 0) < self.max_failed_count]),
            "failed_proxies": len(self.failed_proxies),
            "current_proxy_index": self.current_proxy_index
        }


def main():
    """主函数 - 测试代理管理器"""
    import argparse

    parser = argparse.ArgumentParser(description="代理池管理器")
    parser.add_argument("--config", help="代理配置文件路径")
    parser.add_argument("--check", action="store_true", help="检查所有代理健康状态")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")

    args = parser.parse_args()

    # 创建代理管理器
    manager = ProxyManager(config_file=args.config)

    if args.check:
        asyncio.run(manager.check_all_proxies())

    if args.stats:
        stats = manager.get_stats()
        print("\n代理池统计:")
        print(f"  总代理数: {stats['total_proxies']}")
        print(f"  可用代理数: {stats['available_proxies']}")
        print(f"  失败代理数: {stats['failed_proxies']}")
        print(f"  当前索引: {stats['current_proxy_index']}")


if __name__ == "__main__":
    main()
