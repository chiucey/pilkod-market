#!/usr/bin/env python3
"""
Browser-use 高级交互封装脚本
基于 Playwright 提供 LLM 友好的智能交互能力

核心功能：
- 智能导航
- 元素交互（点击、输入、滚动）
- 数据提取
- 异常处理与恢复
- 人类行为模拟
"""

import asyncio
import argparse
import sys
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

# 尝试导入 browser-use，如果不存在则提供基本实现
try:
    from browser_use import Agent
    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright_manager import get_manager, BrowserManager


class BrowserAgent:
    """浏览器智能代理"""
    
    def __init__(self, manager: Optional[BrowserManager] = None):
        """
        初始化代理
        
        参数：
            manager: BrowserManager 实例，如果为 None 则创建新实例
        """
        self.manager = manager or get_manager()
        self.use_browser_use = BROWSER_USE_AVAILABLE
    
    async def navigate(
        self,
        url: str,
        wait_for_selector: Optional[str] = None,
        wait_for_load_state: str = "networkidle",
        timeout: int = 30000,
        human_simulation: bool = False,
        random_delay: bool = False
    ) -> Dict[str, Any]:
        """
        导航到指定 URL
        
        参数：
            url: 目标 URL
            wait_for_selector: 等待特定选择器出现
            wait_for_load_state: 等待加载状态 (load/domcontentloaded/networkidle)
            timeout: 超时时间（毫秒）
            human_simulation: 是否模拟人类行为
            random_delay: 是否添加随机延迟
        
        返回：
            包含导航结果的字典
        """
        if not self.manager.page:
            return {
                "success": False,
                "error": "浏览器未初始化，请先调用 playwright_manager.py create"
            }
        
        try:
            # 人类行为模拟：随机延迟
            if human_simulation and random_delay:
                import random
                delay = random.uniform(0.5, 2.0)
                await asyncio.sleep(delay)
            
            # 导航到 URL
            await self.manager.page.goto(
                url,
                wait_until=wait_for_load_state,
                timeout=timeout
            )
            
            # 等待特定元素
            if wait_for_selector:
                await self.manager.page.wait_for_selector(
                    wait_for_selector,
                    timeout=timeout
                )
            
            return {
                "success": True,
                "url": self.manager.page.url,
                "title": await self.manager.page.title()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"导航失败: {str(e)}"
            }
    
    async def click(
        self,
        selector: str,
        timeout: int = 10000,
        force: bool = False,
        human_simulation: bool = False
    ) -> Dict[str, Any]:
        """
        点击元素
        
        参数：
            selector: CSS 选择器
            timeout: 超时时间（毫秒）
            force: 是否强制点击
            human_simulation: 是否模拟人类行为
        
        返回：
            操作结果
        """
        if not self.manager.page:
            return {
                "success": False,
                "error": "浏览器未初始化"
            }
        
        try:
            # 人类行为模拟：随机移动延迟
            if human_simulation:
                import random
                await asyncio.sleep(random.uniform(0.3, 1.0))
            
            # 等待元素可点击
            await self.manager.page.wait_for_selector(
                selector,
                state="visible",
                timeout=timeout
            )
            
            # 点击元素
            await self.manager.page.click(
                selector,
                timeout=timeout,
                force=force
            )
            
            return {
                "success": True,
                "selector": selector,
                "message": "点击成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"点击失败: {str(e)}"
            }
    
    async def fill(
        self,
        selector: str,
        text: str,
        timeout: int = 10000,
        clear_first: bool = True,
        human_simulation: bool = False
    ) -> Dict[str, Any]:
        """
        填充文本输入框
        
        参数：
            selector: CSS 选择器
            text: 要填充的文本
            timeout: 超时时间（毫秒）
            clear_first: 是否先清空
            human_simulation: 是否模拟人类输入
        
        返回：
            操作结果
        """
        if not self.manager.page:
            return {
                "success": False,
                "error": "浏览器未初始化"
            }
        
        try:
            # 人类行为模拟：模拟逐字输入
            if human_simulation:
                await self.manager.page.wait_for_selector(selector, timeout=timeout)
                if clear_first:
                    await self.manager.page.fill(selector, "")
                for char in text:
                    await self.manager.page.type(selector, char, delay=random.randint(50, 150))
            else:
                if clear_first:
                    await self.manager.page.fill(selector, "")
                await self.manager.page.fill(selector, text)
            
            return {
                "success": True,
                "selector": selector,
                "text": text,
                "message": "填充成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"填充失败: {str(e)}"
            }
    
    async def scroll(
        self,
        direction: str = "down",
        distance: int = 500,
        selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        滚动页面
        
        参数：
            direction: 滚动方向 (up/down/left/right)
            distance: 滚动距离（像素）
            selector: 滚动特定元素
        
        返回：
            操作结果
        """
        if not self.manager.page:
            return {
                "success": False,
                "error": "浏览器未初始化"
            }
        
        try:
            if selector:
                element = await self.manager.page.wait_for_selector(selector)
                await element.scroll_into_view_if_needed()
            else:
                # 页面滚动
                scroll_amount = distance if direction == "down" else -distance
                await self.manager.page.evaluate(
                    f"window.scrollBy(0, {scroll_amount})"
                )
            
            return {
                "success": True,
                "direction": direction,
                "distance": distance
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"滚动失败: {str(e)}"
            }
    
    async def extract(
        self,
        selector: str,
        extract_type: str = "text",
        attribute: Optional[str] = None,
        multiple: bool = False
    ) -> Dict[str, Any]:
        """
        提取元素数据
        
        参数：
            selector: CSS 选择器
            extract_type: 提取类型 (text/html/attr)
            attribute: 当 type=attr 时，指定属性名
            multiple: 是否提取多个元素
        
        返回：
            提取的数据
        """
        if not self.manager.page:
            return {
                "success": False,
                "error": "浏览器未初始化"
            }
        
        try:
            if multiple:
                elements = await self.manager.page.query_selector_all(selector)
                results = []
                
                for element in elements:
                    if extract_type == "text":
                        results.append(await element.inner_text())
                    elif extract_type == "html":
                        results.append(await element.inner_html())
                    elif extract_type == "attr" and attribute:
                        results.append(await element.get_attribute(attribute))
                
                return {
                    "success": True,
                    "data": results,
                    "count": len(results)
                }
            else:
                element = await self.manager.page.wait_for_selector(selector)
                
                if extract_type == "text":
                    data = await element.inner_text()
                elif extract_type == "html":
                    data = await element.inner_html()
                elif extract_type == "attr" and attribute:
                    data = await element.get_attribute(attribute)
                else:
                    data = None
                
                return {
                    "success": True,
                    "data": data
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"提取失败: {str(e)}"
            }
    
    async def evaluate_script(
        self,
        script: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行 JavaScript 脚本
        
        参数：
            script: JavaScript 代码
            **kwargs: 传递给脚本的变量
        
        返回：
            脚本执行结果
        """
        if not self.manager.page:
            return {
                "success": False,
                "error": "浏览器未初始化"
            }
        
        try:
            result = await self.manager.page.evaluate(script, **kwargs)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"脚本执行失败: {str(e)}"
            }


async def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="浏览器智能交互工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # navigate 命令
    navigate_parser = subparsers.add_parser("navigate", help="导航到 URL")
    navigate_parser.add_argument("--url", type=str, required=True, help="目标 URL")
    navigate_parser.add_argument("--wait-for-selector", type=str, help="等待选择器")
    navigate_parser.add_argument("--wait-for-load-state", type=str, default="networkidle", help="等待加载状态")
    navigate_parser.add_argument("--timeout", type=int, default=30000, help="超时时间")
    navigate_parser.add_argument("--human-simulation", action="store_true", help="模拟人类行为")
    navigate_parser.add_argument("--random-delay", action="store_true", help="随机延迟")
    
    # click 命令
    click_parser = subparsers.add_parser("click", help="点击元素")
    click_parser.add_argument("--selector", type=str, required=True, help="CSS 选择器")
    click_parser.add_argument("--timeout", type=int, default=10000, help="超时时间")
    click_parser.add_argument("--force", action="store_true", help="强制点击")
    click_parser.add_argument("--human-simulation", action="store_true", help="模拟人类行为")
    
    # fill 命令
    fill_parser = subparsers.add_parser("fill", help="填充输入框")
    fill_parser.add_argument("--selector", type=str, required=True, help="CSS 选择器")
    fill_parser.add_argument("--text", type=str, required=True, help="填充文本")
    fill_parser.add_argument("--clear-first", action="store_true", default=True, help="先清空")
    fill_parser.add_argument("--human-simulation", action="store_true", help="模拟人类输入")
    
    # scroll 命令
    scroll_parser = subparsers.add_parser("scroll", help="滚动页面")
    scroll_parser.add_argument("--direction", type=str, default="down", help="滚动方向")
    scroll_parser.add_argument("--distance", type=int, default=500, help="滚动距离")
    scroll_parser.add_argument("--selector", type=str, help="滚动特定元素")
    
    # extract 命令
    extract_parser = subparsers.add_parser("extract", help="提取数据")
    extract_parser.add_argument("--selector", type=str, required=True, help="CSS 选择器")
    extract_parser.add_argument("--type", type=str, default="text", choices=["text", "html", "attr"], help="提取类型")
    extract_parser.add_argument("--attribute", type=str, help="属性名")
    extract_parser.add_argument("--multiple", action="store_true", help="提取多个")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    agent = BrowserAgent()
    
    if args.command == "navigate":
        result = await agent.navigate(
            url=args.url,
            wait_for_selector=args.wait_for_selector,
            wait_for_load_state=args.wait_for_load_state,
            timeout=args.timeout,
            human_simulation=args.human_simulation,
            random_delay=args.random_delay
        )
        print_result(result)
    
    elif args.command == "click":
        result = await agent.click(
            selector=args.selector,
            timeout=args.timeout,
            force=args.force,
            human_simulation=args.human_simulation
        )
        print_result(result)
    
    elif args.command == "fill":
        result = await agent.fill(
            selector=args.selector,
            text=args.text,
            clear_first=args.clear_first,
            human_simulation=args.human_simulation
        )
        print_result(result)
    
    elif args.command == "scroll":
        result = await agent.scroll(
            direction=args.direction,
            distance=args.distance,
            selector=args.selector
        )
        print_result(result)
    
    elif args.command == "extract":
        result = await agent.extract(
            selector=args.selector,
            extract_type=args.type,
            attribute=args.attribute,
            multiple=args.multiple
        )
        print_result(result)


def print_result(result: Dict[str, Any]):
    """打印结果"""
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
