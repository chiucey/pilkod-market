#!/usr/bin/env python3
"""
Playwright CLI 工具
基于 Playwright CLI 最佳实践的浏览器操作工具

核心功能：
1. 使用 Playwright CLI 命令行工具
2. 代码生成（codegen）
3. 标准测试脚本
4. 智能等待策略
5. 改进的错误处理

版本：2.0.0（基于 Playwright CLI 最佳实践）
"""

import subprocess
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path


class PlaywrightCLI:
    """Playwright CLI 工具类"""

    def __init__(self):
        """初始化 Playwright CLI 工具"""
        self.check_playwright_installed()

    def check_playwright_installed(self) -> bool:
        """
        检查 Playwright 是否已安装

        返回：
            是否已安装
        """
        try:
            result = subprocess.run(
                ["playwright", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ Playwright 已安装: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            pass
        except subprocess.TimeoutExpired:
            pass

        print("❌ Playwright 未安装")
        return False

    def install_browser(self, browser: str = "chromium") -> bool:
        """
        安装浏览器

        参数：
            browser: 浏览器类型（chromium/firefox/webkit）

        返回：
            是否成功
        """
        print(f"📦 正在安装 {browser} 浏览器...")
        try:
            result = subprocess.run(
                ["playwright", "install", browser],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                print(f"✅ {browser} 浏览器安装成功")
                return True
            else:
                print(f"❌ {browser} 浏览器安装失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"❌ {browser} 浏览器安装超时")
            return False
        except Exception as e:
            print(f"❌ {browser} 浏览器安装失败: {str(e)}")
            return False

    def codegen(
        self,
        url: str,
        output_file: str = "generated_test.py",
        target: str = "chromium",
        device: Optional[str] = None
    ) -> bool:
        """
        代码生成（录制操作）

        参数：
            url: 目标 URL
            output_file: 输出文件
            target: 目标浏览器（chromium/firefox/webkit）
            device: 设备类型（Desktop Chrome/iPhone 12 等）

        返回：
            是否成功
        """
        print(f"🎬 开始录制操作: {url}")

        cmd = [
            "playwright", "codegen",
            "--output", output_file,
            "--target", target
        ]

        if device:
            cmd.extend(["--device", device])

        cmd.append(url)

        try:
            subprocess.run(cmd, check=True)
            print(f"✅ 录制完成，已保存到: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 录制失败: {e}")
            return False
        except FileNotFoundError:
            print("❌ Playwright 未安装")
            return False

    def run_test(
        self,
        test_file: str,
        headed: bool = False,
        browser: str = "chromium",
        slow_mo: int = 0
    ) -> bool:
        """
        运行测试脚本

        参数：
            test_file: 测试文件路径
            headed: 是否显示浏览器窗口
            browser: 浏览器类型
            slow_mo: 慢动作延迟（毫秒）

        返回：
            是否成功
        """
        print(f"🧪 运行测试: {test_file}")

        cmd = [
            "python", "-m", "playwright",
            test_file,
            "--browser", browser
        ]

        if headed:
            cmd.append("--headed")

        if slow_mo > 0:
            cmd.extend(["--slow-mo", str(slow_mo)])

        try:
            result = subprocess.run(cmd)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ 测试运行失败: {str(e)}")
            return False

    def show_trace(self, trace_file: str) -> bool:
        """
        显示测试追踪

        参数：
            trace_file: 追踪文件路径

        返回：
            是否成功
        """
        print(f"🔍 显示追踪: {trace_file}")

        try:
            result = subprocess.run(
                ["playwright", "show-trace", trace_file],
                check=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"❌ 显示追踪失败: {str(e)}")
            return False


class AsyncPlaywrightBrowser:
    """
    异步 Playwright 浏览器操作
    基于最新最佳实践的异步实现
    """

    def __init__(
        self,
        headless: bool = True,
        browser_type: str = "chromium",
        slow_mo: int = 0,
        timeout: int = 30000
    ):
        """
        初始化浏览器

        参数：
            headless: 是否无头模式
            browser_type: 浏览器类型（chromium/firefox/webkit）
            slow_mo: 慢动作延迟（毫秒）
            timeout: 超时时间（毫秒）
        """
        self.headless = headless
        self.browser_type = browser_type
        self.slow_mo = slow_mo
        self.timeout = timeout
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        """启动浏览器"""
        try:
            from playwright.async_api import async_playwright

            playwright = await async_playwright().start()

            # 启动浏览器
            browser_args = {
                "headless": self.headless,
                "slow_mo": self.slow_mo
            }

            if self.browser_type == "chromium":
                self.browser = await playwright.chromium.launch(**browser_args)
            elif self.browser_type == "firefox":
                self.browser = await playwright.firefox.launch(**browser_args)
            elif self.browser_type == "webkit":
                self.browser = await playwright.webkit.launch(**browser_args)

            # 创建上下文
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )

            # 创建页面
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.timeout)

            print("✅ 浏览器启动成功")

        except ImportError:
            raise ImportError("Playwright 未安装，请运行: pip install playwright")
        except Exception as e:
            raise Exception(f"浏览器启动失败: {str(e)}")

    async def goto(
        self,
        url: str,
        wait_until: str = "load",
        timeout: Optional[int] = None
    ):
        """
        导航到 URL

        参数：
            url: 目标 URL
            wait_until: 等待策略（load/domcontentloaded/networkidle/commit）
            timeout: 超时时间
        """
        try:
            await self.page.goto(url, wait_until=wait_until, timeout=timeout)
            print(f"✅ 导航到: {url}")
        except Exception as e:
            raise Exception(f"导航失败: {str(e)}")

    async def wait_for_selector(
        self,
        selector: str,
        state: str = "attached",
        timeout: Optional[int] = None
    ):
        """
        等待选择器

        参数：
            selector: CSS 选择器
            state: 等待状态（attached/detached/hidden/visible）
            timeout: 超时时间
        """
        try:
            await self.page.wait_for_selector(selector, state=state, timeout=timeout)
            print(f"✅ 等待选择器: {selector}")
        except Exception as e:
            raise Exception(f"等待选择器失败: {str(e)}")

    async def click(
        self,
        selector: str,
        timeout: Optional[int] = None,
        force: bool = False
    ):
        """
        点击元素

        参数：
            selector: CSS 选择器
            timeout: 超时时间
            force: 强制点击
        """
        try:
            await self.page.click(selector, timeout=timeout, force=force)
            print(f"✅ 点击: {selector}")
        except Exception as e:
            raise Exception(f"点击失败: {str(e)}")

    async def fill(
        self,
        selector: str,
        value: str,
        timeout: Optional[int] = None
    ):
        """
        填写输入框

        参数：
            selector: CSS 选择器
            value: 填充值
            timeout: 超时时间
        """
        try:
            await self.page.fill(selector, value, timeout=timeout)
            print(f"✅ 填写: {selector}")
        except Exception as e:
            raise Exception(f"填写失败: {str(e)}")

    async def screenshot(
        self,
        path: str,
        full_page: bool = False
    ):
        """
        截图

        参数：
            path: 保存路径
            full_page: 是否全页截图
        """
        try:
            await self.page.screenshot(path=path, full_page=full_page)
            print(f"✅ 截图已保存: {path}")
        except Exception as e:
            raise Exception(f"截图失败: {str(e)}")

    async def get_text(self, selector: str) -> str:
        """
        获取文本内容

        参数：
            selector: CSS 选择器

        返回：
            文本内容
        """
        try:
            element = await self.page.query_selector(selector)
            if element:
                text = await element.inner_text()
                return text
            return ""
        except Exception as e:
            raise Exception(f"获取文本失败: {str(e)}")

    async def scroll_down(self, distance: int = 500):
        """
        向下滚动

        参数：
            distance: 滚动距离（像素）
        """
        try:
            await self.page.evaluate(f"window.scrollBy(0, {distance})")
            print(f"✅ 向下滚动: {distance} 像素")
        except Exception as e:
            raise Exception(f"滚动失败: {str(e)}")

    async def wait_for_load_state(self, state: str = "load"):
        """
        等待加载状态

        参数：
            state: 加载状态（load/domcontentloaded/networkidle）
        """
        try:
            await self.page.wait_for_load_state(state)
            print(f"✅ 等待加载状态: {state}")
        except Exception as e:
            raise Exception(f"等待加载状态失败: {str(e)}")

    async def close(self):
        """关闭浏览器"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            print("✅ 浏览器已关闭")
        except Exception as e:
            print(f"⚠️ 关闭浏览器时出错: {str(e)}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Playwright CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

1. 代码生成（录制操作）：
  python playwright_cli.py codegen https://example.com

2. 安装浏览器：
  python playwright_cli.py install chromium

3. 运行测试：
  python playwright_cli.py run generated_test.py

4. 显示追踪：
  python playwright_cli.py show-trace trace.zip
        """
    )

    parser.add_argument(
        "command",
        choices=["install", "codegen", "run", "show-trace"],
        help="命令类型"
    )

    parser.add_argument(
        "target",
        nargs="?",
        help="目标（浏览器类型、URL 或文件路径）"
    )

    parser.add_argument(
        "--output",
        help="输出文件（仅用于 codegen 命令）"
    )

    parser.add_argument(
        "--device",
        help="设备类型（仅用于 codegen 命令）"
    )

    args = parser.parse_args()

    cli = PlaywrightCLI()

    if args.command == "install":
        if not args.target:
            print("错误: 需要指定浏览器类型（chromium/firefox/webkit）")
            sys.exit(1)
        cli.install_browser(args.target)

    elif args.command == "codegen":
        if not args.target:
            print("错误: 需要指定 URL")
            sys.exit(1)
        output_file = args.output or "generated_test.py"
        cli.codegen(args.target, output_file, device=args.device)

    elif args.command == "run":
        if not args.target:
            print("错误: 需要指定测试文件")
            sys.exit(1)
        cli.run_test(args.target)

    elif args.command == "show-trace":
        if not args.target:
            print("错误: 需要指定追踪文件")
            sys.exit(1)
        cli.show_trace(args.target)


if __name__ == "__main__":
    main()
