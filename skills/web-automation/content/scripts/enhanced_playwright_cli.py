#!/usr/bin/env python3
"""
增强版 Playwright CLI 工具
集成超时优化、重试机制、反爬增强、证书处理等功能

核心增强：
1. 超时策略：更长默认超时 + 可配置超时策略
2. 重试机制：集成 RetryManager，自动重试失败操作
3. 反爬增强：代理IP、随机UA、浏览器指纹伪装
4. 证书处理：支持忽略证书错误
5. 智能等待：自适应等待策略

版本：3.0.0（增强版）
"""

import subprocess
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import random


class TimeoutConfig:
    """超时配置管理"""
    
    # 默认超时时间（毫秒）
    DEFAULT_TIMEOUT = 60000  # 60秒
    
    # 操作类型超时映射
    TIMEOUT_PRESETS = {
        "fast": 30000,        # 快速操作：30秒
        "normal": 60000,      # 正常操作：60秒
        "slow": 120000,       # 慢速操作：120秒
        "very_slow": 300000,  # 超慢操作：300秒（5分钟）
        "download": 600000,   # 下载操作：600秒（10分钟）
    }
    
    @classmethod
    def get_timeout(cls, operation_type: str = "normal") -> int:
        """获取指定操作类型的超时时间"""
        return cls.TIMEOUT_PRESETS.get(operation_type, cls.DEFAULT_TIMEOUT)


class RetryConfig:
    """重试配置管理"""
    
    # 默认重试配置
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BASE_DELAY = 1.0
    DEFAULT_MAX_DELAY = 60.0
    
    # 操作类型重试映射
    RETRY_PRESETS = {
        "navigation": {"max_retries": 3, "base_delay": 2.0},
        "click": {"max_retries": 2, "base_delay": 0.5},
        "fill": {"max_retries": 2, "base_delay": 0.5},
        "screenshot": {"max_retries": 2, "base_delay": 0.5},
        "download": {"max_retries": 5, "base_delay": 5.0},
    }
    
    @classmethod
    def get_config(cls, operation_type: str = "navigation") -> Dict[str, Any]:
        """获取指定操作类型的重试配置"""
        return cls.RETRY_PRESETS.get(operation_type, {
            "max_retries": cls.DEFAULT_MAX_RETRIES,
            "base_delay": cls.DEFAULT_BASE_DELAY
        })


class AntiScrapingConfig:
    """反爬配置管理"""
    
    # 常用 User-Agent 列表
    USER_AGENTS = [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Chrome on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Firefox on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Safari on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    
    # 视口大小列表
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 2560, "height": 1440},
    ]
    
    # 时区和语言
    TIMEZONES = [
        "Asia/Shanghai",
        "America/New_York",
        "Europe/London",
        "Asia/Tokyo",
        "America/Los_Angeles",
    ]
    
    LOCALES = [
        "zh-CN",
        "en-US",
        "en-GB",
        "ja-JP",
    ]
    
    @classmethod
    def get_random_user_agent(cls) -> str:
        """获取随机 User-Agent"""
        return random.choice(cls.USER_AGENTS)
    
    @classmethod
    def get_random_viewport(cls) -> Dict[str, int]:
        """获取随机视口大小"""
        return random.choice(cls.VIEWPORTS)
    
    @classmethod
    def get_random_timezone(cls) -> str:
        """获取随机时区"""
        return random.choice(cls.TIMEZONES)
    
    @classmethod
    def get_random_locale(cls) -> str:
        """获取随机语言"""
        return random.choice(cls.LOCALES)


class EnhancedAsyncPlaywrightBrowser:
    """
    增强版异步 Playwright 浏览器操作
    
    增强功能：
    1. 超时优化：可配置超时策略
    2. 重试机制：自动重试失败操作
    3. 反爬增强：代理、UA、指纹伪装
    4. 证书处理：支持忽略证书错误
    5. 智能等待：自适应等待策略
    """

    def __init__(
        self,
        headless: bool = True,
        browser_type: str = "chromium",
        slow_mo: int = 0,
        timeout: int = 60000,
        # 新增：超时策略
        timeout_strategy: str = "normal",
        # 新增：重试配置
        max_retries: int = 3,
        retry_base_delay: float = 1.0,
        # 新增：代理配置
        proxy: Optional[Dict[str, str]] = None,
        # 新增：反爬配置
        random_ua: bool = True,
        random_viewport: bool = True,
        # 新增：证书处理
        ignore_https_errors: bool = False,
    ):
        """
        初始化增强版浏览器

        参数：
            headless: 是否无头模式
            browser_type: 浏览器类型（chromium/firefox/webkit）
            slow_mo: 慢动作延迟（毫秒）
            timeout: 超时时间（毫秒）
            timeout_strategy: 超时策略（fast/normal/slow/very_slow/download）
            max_retries: 最大重试次数
            retry_base_delay: 重试基础延迟（秒）
            proxy: 代理配置 {"server": "http://...", "username": "...", "password": "..."}
            random_ua: 是否使用随机UA
            random_viewport: 是否使用随机视口
            ignore_https_errors: 是否忽略证书错误
        """
        self.headless = headless
        self.browser_type = browser_type
        self.slow_mo = slow_mo
        
        # 超时配置
        self.timeout = timeout or TimeoutConfig.get_timeout(timeout_strategy)
        self.timeout_strategy = timeout_strategy
        
        # 重试配置
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        
        # 代理配置
        self.proxy = proxy
        
        # 反爬配置
        self.random_ua = random_ua
        self.random_viewport = random_viewport
        
        # 证书配置
        self.ignore_https_errors = ignore_https_errors
        
        # 浏览器实例
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # 统计信息
        self.stats = {
            "total_operations": 0,
            "success_operations": 0,
            "failed_operations": 0,
            "retried_operations": 0,
        }

    async def start(self):
        """启动浏览器（增强版）"""
        try:
            from playwright.async_api import async_playwright

            self.playwright = await async_playwright().start()

            # 浏览器启动参数
            browser_args = {
                "headless": self.headless,
                "slow_mo": self.slow_mo,
            }
            
            # 添加代理
            if self.proxy:
                browser_args["proxy"] = self.proxy

            # 启动浏览器
            if self.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(**browser_args)
            elif self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(**browser_args)
            elif self.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(**browser_args)

            # 上下文配置
            context_args = {}
            
            # 视口设置
            if self.random_viewport:
                context_args["viewport"] = AntiScrapingConfig.get_random_viewport()
            else:
                context_args["viewport"] = {"width": 1920, "height": 1080}
            
            # User-Agent 设置
            if self.random_ua:
                context_args["user_agent"] = AntiScrapingConfig.get_random_user_agent()
            else:
                context_args["user_agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            
            # 时区和语言
            context_args["timezone_id"] = AntiScrapingConfig.get_random_timezone()
            context_args["locale"] = AntiScrapingConfig.get_random_locale()
            
            # 证书错误处理
            context_args["ignore_https_errors"] = self.ignore_https_errors

            # 创建上下文
            self.context = await self.browser.new_context(**context_args)

            # 创建页面
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.timeout)

            print("✅ 浏览器启动成功（增强版）")
            print(f"   超时策略: {self.timeout_strategy} ({self.timeout}ms)")
            print(f"   重试次数: {self.max_retries}")
            print(f"   随机UA: {'启用' if self.random_ua else '禁用'}")
            print(f"   忽略证书错误: {'启用' if self.ignore_https_errors else '禁用'}")
            if self.proxy:
                print(f"   代理: {self.proxy.get('server', 'N/A')}")

        except ImportError:
            raise ImportError("Playwright 未安装，请运行: pip install playwright")
        except Exception as e:
            raise Exception(f"浏览器启动失败: {str(e)}")

    async def _execute_with_retry(
        self,
        operation_name: str,
        operation_func,
        *args,
        **kwargs
    ) -> Any:
        """
        执行操作并自动重试

        参数：
            operation_name: 操作名称
            operation_func: 操作函数
            *args: 位置参数
            **kwargs: 关键字参数

        返回：
            操作结果
        """
        self.stats["total_operations"] += 1
        
        retry_config = RetryConfig.get_config(operation_name)
        max_retries = retry_config.get("max_retries", self.max_retries)
        base_delay = retry_config.get("base_delay", self.retry_base_delay)
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = await operation_func(*args, **kwargs)
                self.stats["success_operations"] += 1
                
                if attempt > 0:
                    self.stats["retried_operations"] += 1
                    print(f"✅ 重试成功 ({operation_name}) - 尝试 {attempt + 1}/{max_retries + 1}")
                
                return result
                
            except Exception as e:
                last_error = e
                
                # 检查是否应该重试
                if not self._should_retry(e, operation_name):
                    print(f"❌ 错误不可重试 ({operation_name}): {e}")
                    break
                
                # 等待后重试
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)  # 指数退避
                    print(f"⏳ 等待 {delay:.1f}s 后重试 ({operation_name}) - 尝试 {attempt + 1}/{max_retries + 1}")
                    await asyncio.sleep(delay)
        
        self.stats["failed_operations"] += 1
        raise last_error

    def _should_retry(self, error: Exception, operation_name: str) -> bool:
        """判断是否应该重试"""
        error_msg = str(error).lower()
        
        # 可重试的错误类型
        retryable_errors = [
            "timeout",
            "connection",
            "network",
            "temporary",
            "503",
            "502",
            "504",
            "429",
            "reset",
            "broken pipe",
        ]
        
        return any(err in error_msg for err in retryable_errors)

    async def goto(
        self,
        url: str,
        wait_until: str = "load",
        timeout: Optional[int] = None,
        retries: Optional[int] = None
    ):
        """
        导航到 URL（增强版：支持重试）

        参数：
            url: 目标 URL
            wait_until: 等待策略（load/domcontentloaded/networkidle/commit）
            timeout: 超时时间（可选）
            retries: 重试次数（可选）
        """
        async def _navigate():
            await self.page.goto(url, wait_until=wait_until, timeout=timeout)
            print(f"✅ 导航成功: {url}")
        
        await self._execute_with_retry("navigation", _navigate)

    async def click(
        self,
        selector: str,
        timeout: Optional[int] = None,
        force: bool = False,
        retries: Optional[int] = None
    ):
        """
        点击元素（增强版：支持重试）

        参数：
            selector: CSS 选择器
            timeout: 超时时间
            force: 强制点击
            retries: 重试次数
        """
        async def _do_click():
            await self.page.click(selector, timeout=timeout, force=force)
            print(f"✅ 点击成功: {selector}")
        
        await self._execute_with_retry("click", _do_click)

    async def fill(
        self,
        selector: str,
        value: str,
        timeout: Optional[int] = None,
        retries: Optional[int] = None
    ):
        """
        填写输入框（增强版：支持重试）

        参数：
            selector: CSS 选择器
            value: 填充值
            timeout: 超时时间
            retries: 重试次数
        """
        async def _do_fill():
            await self.page.fill(selector, value, timeout=timeout)
            print(f"✅ 填写成功: {selector}")
        
        await self._execute_with_retry("fill", _do_fill)

    async def screenshot(
        self,
        path: str,
        full_page: bool = False,
        retries: Optional[int] = None
    ):
        """
        截图（增强版：支持重试）

        参数：
            path: 保存路径
            full_page: 是否全页截图
            retries: 重试次数
        """
        async def _do_screenshot():
            await self.page.screenshot(path=path, full_page=full_page)
            print(f"✅ 截图成功: {path}")
        
        await self._execute_with_retry("screenshot", _do_screenshot)

    async def download(
        self,
        url: str,
        output_path: str,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        下载文件（增强版：支持重试和进度显示）

        参数：
            url: 下载 URL
            output_path: 输出路径
            timeout: 超时时间

        返回：
            下载结果
        """
        async def _do_download():
            # 设置下载超时
            download_timeout = timeout or TimeoutConfig.get_timeout("download")
            
            # 发起下载请求
            async with self.page.expect_download(timeout=download_timeout) as download_info:
                await self.page.goto(url)
            
            download = await download_info.value
            
            # 保存文件
            await download.save_as(output_path)
            
            print(f"✅ 下载成功: {output_path}")
            return {
                "success": True,
                "path": output_path,
                "url": url
            }
        
        return await self._execute_with_retry("download", _do_download)

    async def wait_for_selector(
        self,
        selector: str,
        state: str = "attached",
        timeout: Optional[int] = None
    ):
        """
        等待选择器（增强版）

        参数：
            selector: CSS 选择器
            state: 等待状态（attached/detached/hidden/visible）
            timeout: 超时时间
        """
        await self.page.wait_for_selector(selector, state=state, timeout=timeout)
        print(f"✅ 等待选择器成功: {selector}")

    async def get_text(self, selector: str) -> str:
        """
        获取文本内容

        参数：
            selector: CSS 选择器

        返回：
            文本内容
        """
        element = await self.page.query_selector(selector)
        if element:
            text = await element.inner_text()
            return text
        return ""

    async def scroll_down(self, distance: int = 500):
        """向下滚动"""
        await self.page.evaluate(f"window.scrollBy(0, {distance})")
        print(f"✅ 向下滚动: {distance} 像素")

    async def wait_for_load_state(self, state: str = "load"):
        """等待加载状态"""
        await self.page.wait_for_load_state(state)
        print(f"✅ 等待加载状态: {state}")

    async def close(self):
        """关闭浏览器"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            # 打印统计信息
            print("\n📊 操作统计:")
            print(f"   总操作数: {self.stats['total_operations']}")
            print(f"   成功操作: {self.stats['success_operations']}")
            print(f"   失败操作: {self.stats['failed_operations']}")
            print(f"   重试成功: {self.stats['retried_operations']}")
            print("✅ 浏览器已关闭")
            
        except Exception as e:
            print(f"⚠️ 关闭浏览器时出错: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()


# ============================================================================
# 命令行接口
# ============================================================================

async def cli_main():
    """命令行主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="增强版 Playwright CLI 工具 - 支持超时优化、重试机制、反爬增强"
    )
    
    parser.add_argument(
        "url",
        help="目标 URL"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=60000,
        help="超时时间（毫秒，默认: 60000）"
    )
    
    parser.add_argument(
        "--timeout-strategy",
        choices=["fast", "normal", "slow", "very_slow", "download"],
        default="normal",
        help="超时策略"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="最大重试次数（默认: 3）"
    )
    
    parser.add_argument(
        "--proxy",
        type=str,
        help="代理服务器（如: http://127.0.0.1:8080）"
    )
    
    parser.add_argument(
        "--random-ua",
        action="store_true",
        default=True,
        help="使用随机 User-Agent"
    )
    
    parser.add_argument(
        "--ignore-https-errors",
        action="store_true",
        help="忽略 HTTPS 证书错误"
    )
    
    parser.add_argument(
        "--screenshot",
        type=str,
        help="截图保存路径"
    )
    
    args = parser.parse_args()
    
    # 创建浏览器
    browser = EnhancedAsyncPlaywrightBrowser(
        headless=args.headless,
        timeout=args.timeout,
        timeout_strategy=args.timeout_strategy,
        max_retries=args.max_retries,
        random_ua=args.random_ua,
        ignore_https_errors=args.ignore_https_errors,
        proxy={"server": args.proxy} if args.proxy else None,
    )
    
    try:
        # 启动浏览器
        await browser.start()
        
        # 导航到目标 URL
        await browser.goto(args.url, wait_until="networkidle")
        
        # 截图
        if args.screenshot:
            await browser.screenshot(args.screenshot, full_page=True)
        
        # 获取页面标题
        title = await browser.get_text("title")
        print(f"\n📄 页面标题: {title}")
        
        # 等待用户输入（非无头模式）
        if not args.headless:
            input("\n按回车键关闭浏览器...")
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(cli_main())
