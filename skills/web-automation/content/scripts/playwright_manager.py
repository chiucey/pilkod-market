#!/usr/bin/env python3
"""
Playwright 浏览器管理脚本
提供浏览器生命周期管理、截图、异步操作支持

核心功能：
- 创建和关闭浏览器实例
- 页面管理（获取、创建、关闭）
- 截图功能
- 异步操作支持
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright


class BrowserManager:
    """Playwright 浏览器管理器"""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._lock = asyncio.Lock()
    
    async def create_browser(
        self,
        headless: bool = False,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout: int = 30000,
        viewport: Optional[Dict[str, int]] = None,
        locale: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        创建浏览器实例
        
        参数：
            headless: 是否无头模式
            proxy: 代理地址，格式为 "socks5://127.0.0.1:1080" 或 "http://proxy.com:8080"
            user_agent: 自定义 User-Agent
            timeout: 默认超时时间（毫秒）
            viewport: 视口大小，格式为 {"width": 1920, "height": 1080}
            locale: 浏览器语言设置
        
        返回：
            包含浏览器状态和页面信息的字典
        """
        async with self._lock:
            if self.browser is not None:
                return {
                    "success": False,
                    "error": "浏览器实例已存在，请先关闭现有实例"
                }
            
            try:
                self.playwright = await async_playwright().start()
                
                # 配置浏览器启动参数
                launch_options = {
                    "headless": headless,
                    "args": [
                        "--disable-blink-features=AutomationControlled",  # 绕过自动化检测
                        "--disable-dev-shm-usage",
                        "--no-sandbox"
                    ]
                }
                
                # 代理配置
                if proxy:
                    if proxy.startswith("socks5"):
                        launch_options["proxy"] = {"server": proxy}
                    elif proxy.startswith("http"):
                        launch_options["proxy"] = {"server": proxy}
                
                # 启动浏览器
                self.browser = await self.playwright.chromium.launch(**launch_options)
                
                # 创建上下文
                context_options = {
                    "locale": locale,
                    "timezone_id": "Asia/Shanghai",
                    "viewport": viewport or {"width": 1920, "height": 1080},
                    "java_script_enabled": True,
                    "ignore_https_errors": True
                }
                
                if user_agent:
                    context_options["user_agent"] = user_agent
                
                self.context = await self.browser.new_context(**context_options)
                
                # 设置默认超时
                self.context.set_default_timeout(timeout)
                
                # 创建新页面
                self.page = await self.context.new_page()
                
                return {
                    "success": True,
                    "browser_id": id(self.browser),
                    "page_id": id(self.page),
                    "message": "浏览器创建成功"
                }
                
            except Exception as e:
                await self._cleanup()
                return {
                    "success": False,
                    "error": f"浏览器创建失败: {str(e)}"
                }
    
    async def get_page(self) -> Dict[str, Any]:
        """获取当前页面实例"""
        if self.page is None:
            return {
                "success": False,
                "error": "浏览器未初始化，请先调用 create_browser"
            }
        
        return {
            "success": True,
            "page_id": id(self.page),
            "url": self.page.url,
            "title": await self.page.title()
        }
    
    async def new_page(self) -> Dict[str, Any]:
        """创建新页面"""
        if self.context is None:
            return {
                "success": False,
                "error": "浏览器上下文未初始化"
            }
        
        try:
            self.page = await self.context.new_page()
            return {
                "success": True,
                "page_id": id(self.page),
                "message": "新页面创建成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"创建新页面失败: {str(e)}"
            }
    
    async def close_page(self) -> Dict[str, Any]:
        """关闭当前页面"""
        if self.page is None:
            return {
                "success": False,
                "error": "当前没有活跃页面"
            }
        
        try:
            await self.page.close()
            self.page = None
            return {
                "success": True,
                "message": "页面已关闭"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"关闭页面失败: {str(e)}"
            }
    
    async def screenshot(
        self,
        output_path: str,
        full_page: bool = False,
        selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        截图
        
        参数：
            output_path: 输出路径
            full_page: 是否全页截图
            selector: 仅截图指定元素
        
        返回：
            包含截图路径和信息的字典
        """
        if self.page is None:
            return {
                "success": False,
                "error": "浏览器未初始化"
            }
        
        try:
            # 确保输出目录存在
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if selector:
                # 截图指定元素
                element = await self.page.wait_for_selector(selector, timeout=10000)
                await element.screenshot(path=str(output_file))
            else:
                # 全页或视口截图
                await self.page.screenshot(
                    path=str(output_file),
                    full_page=full_page
                )
            
            return {
                "success": True,
                "path": str(output_file),
                "size": output_file.stat().st_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"截图失败: {str(e)}"
            }
    
    async def close_browser(self) -> Dict[str, Any]:
        """关闭浏览器"""
        await self._cleanup()
        return {
            "success": True,
            "message": "浏览器已关闭"
        }
    
    async def _cleanup(self):
        """清理资源"""
        if self.page:
            try:
                await self.page.close()
            except:
                pass
            self.page = None
        
        if self.context:
            try:
                await self.context.close()
            except:
                pass
            self.context = None
        
        if self.browser:
            try:
                await self.browser.close()
            except:
                pass
            self.browser = None
        
        if self.playwright:
            try:
                await self.playwright.stop()
            except:
                pass
            self.playwright = None


# 全局管理器实例
_manager_instance: Optional[BrowserManager] = None


def get_manager() -> BrowserManager:
    """获取全局管理器实例"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = BrowserManager()
    return _manager_instance


async def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="Playwright 浏览器管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # create 命令
    create_parser = subparsers.add_parser("create", help="创建浏览器")
    create_parser.add_argument("--headless", action="store_true", help="无头模式")
    create_parser.add_argument("--proxy", type=str, help="代理地址")
    create_parser.add_argument("--user-agent", type=str, help="自定义 User-Agent")
    create_parser.add_argument("--timeout", type=int, default=30000, help="超时时间（毫秒）")
    create_parser.add_argument("--viewport-width", type=int, default=1920, help="视口宽度")
    create_parser.add_argument("--viewport-height", type=int, default=1080, help="视口高度")
    
    # get_page 命令
    subparsers.add_parser("get-page", help="获取当前页面信息")
    
    # screenshot 命令
    screenshot_parser = subparsers.add_parser("screenshot", help="截图")
    screenshot_parser.add_argument("--output-path", type=str, required=True, help="输出路径")
    screenshot_parser.add_argument("--full-page", action="store_true", help="全页截图")
    screenshot_parser.add_argument("--selector", type=str, help="截图指定元素")
    
    # close 命令
    subparsers.add_parser("close", help="关闭浏览器")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = get_manager()
    
    if args.command == "create":
        result = await manager.create_browser(
            headless=args.headless,
            proxy=args.proxy,
            user_agent=args.user_agent,
            timeout=args.timeout,
            viewport={"width": args.viewport_width, "height": args.viewport_height}
        )
        print_result(result)
    
    elif args.command == "get-page":
        result = await manager.get_page()
        print_result(result)
    
    elif args.command == "screenshot":
        result = await manager.screenshot(
            output_path=args.output_path,
            full_page=args.full_page,
            selector=args.selector
        )
        print_result(result)
    
    elif args.command == "close":
        result = await manager.close_browser()
        print_result(result)


def print_result(result: Dict[str, Any]):
    """打印结果"""
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
