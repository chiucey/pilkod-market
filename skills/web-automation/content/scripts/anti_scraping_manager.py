#!/usr/bin/env python3
"""
综合反爬虫管理器
整合代理、Cookie、重试、指纹伪装等反爬虫能力
"""

import json
from typing import Optional, Dict, List, Any
from pathlib import Path

from proxy_manager import ProxyManager
from cookie_manager import CookieManager
from retry_manager import RetryManager
from enhanced_fingerprint import EnhancedFingerprint


class AntiScrapingManager:
    """综合反爬虫管理器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化反爬虫管理器

        Args:
            config_path: 配置文件路径
        """
        self.config = {}
        if config_path and Path(config_path).exists():
            self.load_config(config_path)

        # 初始化各个模块
        self.proxy_manager = ProxyManager()
        self.cookie_manager = CookieManager()
        self.retry_manager = RetryManager()
        self.fingerprint = EnhancedFingerprint()

        # 应用配置
        self.apply_config()

    def load_config(self, config_path: str) -> bool:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            是否加载成功
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"✅ 已加载配置: {config_path}")
            return True
        except Exception as e:
            print(f"❌ 加载配置失败: {e}")
            return False

    def save_config(self, config_path: str) -> bool:
        """
        保存配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            是否保存成功
        """
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存配置: {config_path}")
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False

    def apply_config(self) -> None:
        """应用配置到各个模块"""
        # 代理配置
        proxy_config = self.config.get("proxy", {})
        if "list" in proxy_config:
            for proxy in proxy_config["list"]:
                self.proxy_manager.add_proxy(proxy)

        # 重试配置
        retry_config = self.config.get("retry", {})
        if retry_config:
            self.retry_manager = RetryManager(
                max_retries=retry_config.get("max_retries", 3),
                base_delay=retry_config.get("base_delay", 1.0),
                max_delay=retry_config.get("max_delay", 60.0)
            )

        # 指纹配置
        fingerprint_config = self.config.get("fingerprint", {})
        if fingerprint_config:
            for module, config in fingerprint_config.items():
                self.fingerprint.update_config(module, config)

    def generate_fingerprint_script(self, output_path: str = "fingerprint.js") -> bool:
        """
        生成指纹伪装脚本

        Args:
            output_path: 输出文件路径

        Returns:
            是否生成成功
        """
        modules = self.config.get("fingerprint_modules", ["all"])
        if modules == ["all"]:
            modules = None

        return self.fingerprint.save_script(output_path, modules)

    def get_proxy(self, strategy: str = "round_robin") -> Optional[str]:
        """
        获取代理

        Args:
            strategy: 代理选择策略

        Returns:
            代理地址
        """
        return self.proxy_manager.get_proxy(strategy)

    def load_cookies(self, domain: str) -> Optional[List[Dict[str, Any]]]:
        """
        加载 Cookie

        Args:
            domain: 域名

        Returns:
            Cookie 列表
        """
        return self.cookie_manager.load_cookies(domain)

    def save_cookies(self, domain: str, cookies: List[Dict[str, Any]]) -> bool:
        """
        保存 Cookie

        Args:
            domain: 域名
            cookies: Cookie 列表

        Returns:
            是否保存成功
        """
        return self.cookie_manager.save_cookies(domain, cookies)

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息
        """
        return {
            "proxy": self.proxy_manager.get_stats(),
            "cookie": self.cookie_manager.get_stats(),
            "retry": self.retry_manager.get_stats()
        }

    def print_stats(self) -> None:
        """打印统计信息"""
        print("\n" + "=" * 60)
        print("反爬虫管理器统计")
        print("=" * 60)

        print("\n代理统计:")
        proxy_stats = self.proxy_manager.get_stats()
        print(f"  总代理数: {proxy_stats['total_proxies']}")
        print(f"  可用代理数: {proxy_stats['available_proxies']}")
        print(f"  失败代理数: {proxy_stats['failed_proxies']}")

        print("\nCookie 统计:")
        cookie_stats = self.cookie_manager.get_stats()
        print(f"  总 Cookie 数: {cookie_stats['total_cookies']}")
        print(f"  域名数: {cookie_stats['domains']}")
        print(f"  存储路径: {cookie_stats['storage_path']}")

        print("\n重试统计:")
        self.retry_manager.print_stats()

        print("=" * 60)

    def cleanup(self) -> None:
        """清理资源"""
        self.proxy_manager.cleanup_old_failed_proxies()
        self.cookie_manager.cleanup_expired_cookies()
        print("✅ 资源清理完成")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="综合反爬虫管理器")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--generate-fingerprint", "-g", help="生成指纹脚本")
    parser.add_argument("--cleanup", action="store_true", help="清理资源")

    args = parser.parse_args()

    # 创建管理器
    manager = AntiScrapingManager(config_path=args.config)

    if args.stats:
        manager.print_stats()

    if args.generate_fingerprint:
        manager.generate_fingerprint_script(args.generate_fingerprint)

    if args.cleanup:
        manager.cleanup()


if __name__ == "__main__":
    main()
