#!/usr/bin/env python3
"""
Browser-Use AI Agent 封装

这是一个基于 browser-use 的 AI Agent 实现，用于执行复杂的网页自动化任务。
支持多种 LLM 集成（OpenAI、Anthropic、Google 等）。

使用场景：
- 需要理解和执行复杂任务的 AI Agent
- 需要与 LLM 集成
- 自然语言驱动的自动化
- 智能决策场景

依赖：
- browser-use>=0.12.0
- langchain>=0.1.0
- Playwright（已安装）

参考：https://github.com/browser-use/browser-use
"""

import asyncio
import sys
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

# 检查 browser-use 是否可用
try:
    from browser_use import Agent, BrowserProfile
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.language_models.chat_models import BaseChatModel
    BROWSER_USE_AVAILABLE = True
except ImportError as e:
    BROWSER_USE_AVAILABLE = False
    IMPORT_ERROR = str(e)


class BrowserUseAgentError(Exception):
    """Browser-Use Agent 错误"""
    pass


class BrowserUseAgent:
    """
    Browser-Use AI Agent 封装类
    
    提供：
    1. 自动化浏览器控制
    2. LLM 驱动的任务执行
    3. 多步任务规划
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        model_name: str = "gpt-4o",
        headless: bool = False,
        timeout: int = 30000,
        max_failures: int = 5,
    ):
        """
        初始化 Browser-Use Agent
        
        参数：
            llm: 自定义 LLM 模型，如果为 None 则使用 ChatOpenAI
            model_name: 模型名称（默认 gpt-4o）
            headless: 是否无头模式
            timeout: 超时时间（毫秒）
            max_failures: 最大失败次数
        """
        if not BROWSER_USE_AVAILABLE:
            raise BrowserUseAgentError(
                f"browser-use 依赖未安装或导入失败: {IMPORT_ERROR}\n"
                "请运行: pip install browser-use>=0.12.0"
            )
        
        self.model_name = model_name
        self.headless = headless
        self.timeout = timeout
        self.max_failures = max_failures
        
        # 初始化 LLM
        self.llm = llm or self._create_default_llm()
        
        # Agent 实例
        self.agent: Optional[Agent] = None
        
        # 历史记录
        self.history: List[Dict[str, Any]] = []

    def _create_default_llm(self) -> BaseChatModel:
        """创建默认 LLM（ChatOpenAI）"""
        return ChatOpenAI(
            model=self.model_name,
            temperature=0.0,
            max_tokens=4096,
        )

    async def run_task(
        self,
        task: str,
        url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        执行任务
        
        参数：
            task: 自然语言任务描述
            url: 起始 URL（可选）
        
        返回：
            执行结果字典
        """
        try:
            # 创建 BrowserProfile
            browser_profile = BrowserProfile(
                headless=self.headless,
            )
            
            # 如果有起始 URL，添加到任务描述
            if url:
                task = f"首先访问 {url}，然后：{task}"
            
            # 创建 Agent
            self.agent = Agent(
                task=task,
                llm=self.llm,
                browser_profile=browser_profile,
                max_failures=self.max_failures,
            )
            
            # 执行任务
            result = await self.agent.run()
            
            # 记录历史
            history_entry = {
                "task": task,
                "url": url,
                "result": str(result),
                "success": True,
            }
            self.history.append(history_entry)
            
            return {
                "success": True,
                "result": str(result),
                "history": self.history,
            }
            
        except Exception as e:
            history_entry = {
                "task": task,
                "url": url,
                "error": str(e),
                "success": False,
            }
            self.history.append(history_entry)
            
            return {
                "success": False,
                "error": str(e),
                "history": self.history,
            }

    async def search_and_collect(
        self,
        query: str,
        search_engine: str = "google",
        max_results: int = 10,
    ) -> Dict[str, Any]:
        """
        搜索并收集信息
        
        参数：
            query: 搜索查询
            search_engine: 搜索引擎
            max_results: 最大结果数
        
        返回：
            搜索结果
        """
        task = f"使用 {search_engine} 搜索 '{query}'，提取前 {max_results} 个结果的标题和链接"
        
        search_urls = {
            "google": "https://www.google.com",
            "bing": "https://www.bing.com",
            "duckduckgo": "https://duckduckgo.com",
        }
        
        url = search_urls.get(search_engine.lower(), "https://www.google.com")
        return await self.run_task(task, url=url)

    async def close(self) -> None:
        """关闭 Agent"""
        if self.agent:
            try:
                await self.agent.close()
            except Exception:
                pass
            self.agent = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

    def get_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.history


class BrowserUseAgentBuilder:
    """
    Browser-Use Agent 构建器
    
    提供便捷的方法创建不同配置的 Agent
    """

    @staticmethod
    def create_with_openai(
        api_key: Optional[str] = None,
        model_name: str = "gpt-4o",
        **kwargs
    ) -> BrowserUseAgent:
        """创建使用 OpenAI 的 Agent"""
        llm_kwargs = {
            "model": model_name,
            "temperature": 0.0,
            "max_tokens": 4096,
        }
        if api_key:
            llm_kwargs["api_key"] = api_key
        
        llm = ChatOpenAI(**llm_kwargs)
        return BrowserUseAgent(llm=llm, model_name=model_name, **kwargs)

    @staticmethod
    def create_with_anthropic(
        api_key: Optional[str] = None,
        model_name: str = "claude-3-5-sonnet-20241022",
        **kwargs
    ) -> BrowserUseAgent:
        """创建使用 Anthropic 的 Agent"""
        llm_kwargs = {
            "model": model_name,
            "temperature": 0.0,
            "max_tokens": 4096,
        }
        if api_key:
            llm_kwargs["api_key"] = api_key
        
        llm = ChatAnthropic(**llm_kwargs)
        return BrowserUseAgent(llm=llm, model_name=model_name, **kwargs)

    @staticmethod
    def create_with_google(
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-pro",
        **kwargs
    ) -> BrowserUseAgent:
        """创建使用 Google 的 Agent"""
        llm_kwargs = {
            "model": model_name,
            "temperature": 0.0,
        }
        if api_key:
            llm_kwargs["google_api_key"] = api_key
        
        llm = ChatGoogleGenerativeAI(**llm_kwargs)
        return BrowserUseAgent(llm=llm, model_name=model_name, **kwargs)


# ============================================================================
# 命令行接口
# ============================================================================

async def cli_main():
    """命令行主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Browser-Use AI Agent - 基于浏览器和 LLM 的智能自动化工具"
    )
    
    parser.add_argument(
        "task",
        help="自然语言任务描述"
    )
    
    parser.add_argument(
        "--url",
        help="起始 URL（可选）"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="LLM 模型名称（默认: gpt-4o）"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式（不显示浏览器窗口）"
    )
    
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "google"],
        default="openai",
        help="LLM 提供商（默认: openai）"
    )
    
    args = parser.parse_args()
    
    # 创建 Agent
    if args.provider == "openai":
        agent = BrowserUseAgentBuilder.create_with_openai(
            model_name=args.model,
            headless=args.headless,
        )
    elif args.provider == "anthropic":
        agent = BrowserUseAgentBuilder.create_with_anthropic(
            model_name=args.model,
            headless=args.headless,
        )
    else:
        agent = BrowserUseAgentBuilder.create_with_google(
            model_name=args.model,
            headless=args.headless,
        )
    
    try:
        # 执行任务
        result = await agent.run_task(
            task=args.task,
            url=args.url,
        )
        
        # 输出结果
        if result["success"]:
            print("✅ 任务执行成功")
            print(f"结果: {result['result']}")
        else:
            print("❌ 任务执行失败")
            print(f"错误: {result['error']}")
            
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        sys.exit(1)
    finally:
        await agent.close()


if __name__ == "__main__":
    if BROWSER_USE_AVAILABLE:
        asyncio.run(cli_main())
    else:
        print("❌ browser-use 依赖未安装")
        print("请运行: pip install browser-use>=0.12.0")
        sys.exit(1)
