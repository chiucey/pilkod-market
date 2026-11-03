#!/usr/bin/env python3
"""
Cookie 持久化管理器
支持 Cookie 保存、加载、过期检测和多域名管理
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse


class CookieManager:
    """Cookie 持久化管理器"""

    def __init__(self, storage_path: str = "./cookies"):
        """
        初始化 Cookie 管理器

        Args:
            storage_path: Cookie 存储目录
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.cookies = {}  # {domain: [cookie_dict]}

    def _get_cookie_file(self, domain: str) -> Path:
        """
        获取 Cookie 文件路径

        Args:
            domain: 域名

        Returns:
            Cookie 文件路径
        """
        # 规范化域名
        domain = domain.replace("http://", "").replace("https://", "").replace("/", "")
        return self.storage_path / f"{domain}.json"

    def _is_expired(self, cookie: Dict[str, Any]) -> bool:
        """
        检查 Cookie 是否过期

        Args:
            cookie: Cookie 字典

        Returns:
            是否过期
        """
        expires = cookie.get("expires")
        if expires is None:
            return False

        # expires 可能是时间戳或字符串
        try:
            if isinstance(expires, str):
                expires = datetime.fromisoformat(expires.replace("Z", "+00:00"))

            # 如果是浮点数时间戳
            if isinstance(expires, (int, float)):
                expires = datetime.fromtimestamp(expires)

            return datetime.now() >= expires
        except:
            return False

    def save_cookies(self, domain: str, cookies: List[Dict[str, Any]]) -> bool:
        """
        保存 Cookie

        Args:
            domain: 域名
            cookies: Cookie 列表

        Returns:
            是否保存成功
        """
        try:
            cookie_file = self._get_cookie_file(domain)

            # 保存时添加保存时间
            data = {
                "domain": domain,
                "saved_at": datetime.now().isoformat(),
                "cookies": cookies
            }

            with open(cookie_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.cookies[domain] = cookies
            print(f"✅ 已保存 {len(cookies)} 个 Cookie (域名: {domain})")
            return True
        except Exception as e:
            print(f"❌ 保存 Cookie 失败: {e}")
            return False

    def load_cookies(self, domain: str) -> Optional[List[Dict[str, Any]]]:
        """
        加载 Cookie

        Args:
            domain: 域名

        Returns:
            Cookie 列表
        """
        try:
            cookie_file = self._get_cookie_file(domain)

            if not cookie_file.exists():
                return None

            with open(cookie_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            cookies = data.get("cookies", [])

            # 过滤过期的 Cookie
            valid_cookies = []
            for cookie in cookies:
                if not self._is_expired(cookie):
                    valid_cookies.append(cookie)

            if len(valid_cookies) < len(cookies):
                print(f"⚠️ 过滤了 {len(cookies) - len(valid_cookies)} 个过期 Cookie")

            self.cookies[domain] = valid_cookies
            print(f"✅ 已加载 {len(valid_cookies)} 个 Cookie (域名: {domain})")

            return valid_cookies

        except Exception as e:
            print(f"❌ 加载 Cookie 失败: {e}")
            return None

    def get_cookies(self, domain: str) -> List[Dict[str, Any]]:
        """
        获取 Cookie（从内存或文件）

        Args:
            domain: 域名

        Returns:
            Cookie 列表
        """
        # 先从内存获取
        if domain in self.cookies:
            return self.cookies[domain]

        # 从文件加载
        return self.load_cookies(domain) or []

    def add_cookie(self, domain: str, cookie: Dict[str, Any]) -> bool:
        """
        添加单个 Cookie

        Args:
            domain: 域名
            cookie: Cookie 字典

        Returns:
            是否添加成功
        """
        if domain not in self.cookies:
            self.cookies[domain] = []

        # 检查是否已存在同名 Cookie
        name = cookie.get("name")
        if name:
            # 更新或添加
            self.cookies[domain] = [
                c for c in self.cookies[domain] if c.get("name") != name
            ] + [cookie]

        return self.save_cookies(domain, self.cookies[domain])

    def update_cookie(self, domain: str, name: str, updates: Dict[str, Any]) -> bool:
        """
        更新 Cookie

        Args:
            domain: 域名
            name: Cookie 名称
            updates: 更新内容

        Returns:
            是否更新成功
        """
        cookies = self.get_cookies(domain)

        updated = False
        for cookie in cookies:
            if cookie.get("name") == name:
                cookie.update(updates)
                updated = True

        if updated:
            return self.save_cookies(domain, cookies)

        return False

    def delete_cookie(self, domain: str, name: str) -> bool:
        """
        删除 Cookie

        Args:
            domain: 域名
            name: Cookie 名称

        Returns:
            是否删除成功
        """
        cookies = self.get_cookies(domain)

        original_count = len(cookies)
        self.cookies[domain] = [c for c in cookies if c.get("name") != name]

        if len(self.cookies[domain]) < original_count:
            return self.save_cookies(domain, self.cookies[domain])

        return False

    def clear_cookies(self, domain: Optional[str] = None) -> bool:
        """
        清除 Cookie

        Args:
            domain: 域名，None 表示清除所有

        Returns:
            是否清除成功
        """
        try:
            if domain:
                cookie_file = self._get_cookie_file(domain)
                if cookie_file.exists():
                    cookie_file.unlink()
                if domain in self.cookies:
                    del self.cookies[domain]
                print(f"✅ 已清除 Cookie (域名: {domain})")
            else:
                # 清除所有
                for cookie_file in self.storage_path.glob("*.json"):
                    cookie_file.unlink()
                self.cookies.clear()
                print(f"✅ 已清除所有 Cookie")

            return True
        except Exception as e:
            print(f"❌ 清除 Cookie 失败: {e}")
            return False

    def cleanup_expired_cookies(self) -> int:
        """
        清理过期的 Cookie

        Returns:
            清理的 Cookie 数量
        """
        cleaned_count = 0

        for domain, cookies in list(self.cookies.items()):
            original_count = len(cookies)
            valid_cookies = [c for c in cookies if not self._is_expired(c)]

            if len(valid_cookies) < original_count:
                self.cookies[domain] = valid_cookies
                self.save_cookies(domain, valid_cookies)
                cleaned_count += (original_count - len(valid_cookies))

        if cleaned_count > 0:
            print(f"🧹 清理了 {cleaned_count} 个过期 Cookie")

        return cleaned_count

    def get_stats(self) -> Dict[str, Any]:
        """
        获取 Cookie 统计信息

        Returns:
            统计信息
        """
        total_cookies = sum(len(cookies) for cookies in self.cookies.values())
        domains = list(self.cookies.keys())

        return {
            "total_cookies": total_cookies,
            "domains": len(domains),
            "domain_list": domains,
            "storage_path": str(self.storage_path)
        }

    def export_cookies(self, domain: str, format: str = "json") -> Optional[str]:
        """
        导出 Cookie

        Args:
            domain: 域名
            format: 格式（json、netscape）

        Returns:
            导出的字符串
        """
        cookies = self.get_cookies(domain)

        if format == "json":
            return json.dumps(cookies, ensure_ascii=False, indent=2)
        elif format == "netscape":
            # Netscape Cookie 格式（浏览器导入）
            lines = ["# Netscape HTTP Cookie File"]
            for cookie in cookies:
                line = f"{domain}\t{'TRUE' if cookie.get('hostOnly', False) else 'FALSE'}\t{cookie.get('path', '/')}\t{'TRUE' if cookie.get('secure', False) else 'FALSE'}\t{int(cookie.get('expires', 0))}\t{cookie.get('name')}\t{cookie.get('value')}"
                lines.append(line)
            return "\n".join(lines)

        return None


def main():
    """主函数 - 测试 Cookie 管理器"""
    import argparse

    parser = argparse.ArgumentParser(description="Cookie 持久化管理器")
    parser.add_argument("--domain", help="域名")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--clear", action="store_true", help="清除 Cookie")
    parser.add_argument("--cleanup", action="store_true", help="清理过期 Cookie")

    args = parser.parse_args()

    manager = CookieManager()

    if args.stats:
        stats = manager.get_stats()
        print("\nCookie 统计:")
        print(f"  总 Cookie 数: {stats['total_cookies']}")
        print(f"  域名数: {stats['domains']}")
        print(f"  存储路径: {stats['storage_path']}")
        print(f"  域名列表: {', '.join(stats['domain_list'])}")

    if args.clear:
        if args.domain:
            manager.clear_cookies(args.domain)
        else:
            manager.clear_cookies()

    if args.cleanup:
        manager.cleanup_expired_cookies()


if __name__ == "__main__":
    main()
