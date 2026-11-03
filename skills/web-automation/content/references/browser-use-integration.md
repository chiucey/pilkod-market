# Browser-Use 集成指南

## 目录
- [概览](#概览)
- [Browser-Use 简介](#browser-use-简介)
- [与 Playwright 的区别](#与-playwright-的区别)
- [安装与配置](#安装与配置)
- [快速开始](#快速开始)
- [高级用法](#高级用法)
- [LLM 集成](#llm-集成)
- [常见场景](#常见场景)
- [最佳实践](#最佳实践)

## 概览

本文档说明如何在本 Skill 中集成和使用 browser-use，以及它与现有 Playwright 功能的区别和配合方式。

**核心定位**：
- **Playwright**：底层浏览器控制，适合精细操作和测试场景
- **browser-use**：AI Agent 层，适合复杂任务和智能决策场景

两者互补，不冲突，可以根据需求选择使用或组合使用。

## Browser-Use 简介

**Browser-Use** 是一个基于浏览器和 LLM 的 AI Agent 框架，可以：

1. **理解自然语言任务**：将自然语言描述转换为浏览器操作
2. **智能决策**：根据页面状态自动决定下一步操作
3. **多步规划**：自动拆分复杂任务为多个步骤
4. **DOM 智能分析**：理解页面结构和内容

**官方网站**：https://github.com/browser-use/browser-use

**核心组件**：
- `Agent`：AI Agent，负责任务规划和执行
- `BrowserProfile`：浏览器配置（替代旧版的 Browser、BrowserConfig）
- `Controller`：操作控制器

## 与 Playwright 的区别

| 特性 | Playwright | Browser-Use |
|------|-----------|-------------|
| **控制方式** | 精细 API 控制 | 自然语言描述 |
| **适用场景** | 测试、批量操作、精细控制 | AI Agent、复杂任务、智能决策 |
| **学习曲线** | 需要学习 API | 简单自然语言描述 |
| **LLM 集成** | 需要手动集成 | 原生支持 |
| **智能程度** | 低（需要详细指令） | 高（自动决策） |
| **性能** | 高（直接 API） | 中（需要 LLM 推理） |
| **成本** | 低（无 API 调用） | 中（需要 LLM API） |

**选择建议**：

**使用 Playwright，当：**
- 需要精确控制每个操作
- 批量执行相同任务
- 跨浏览器测试
- 性能要求高
- 不需要 LLM 推理

**使用 Browser-Use，当：**
- 需要理解和执行复杂任务
- 需要 LLM 集成
- 自然语言驱动
- 需要智能决策
- 任务步骤不确定

**组合使用，当：**
- Playwright 处理标准操作（登录、导航）
- Browser-Use 处理复杂任务（信息提取、表单填写）

## 安装与配置

### 1. 安装依赖

```bash
pip install browser-use>=0.12.0
```

### 2. 安装 LLM SDK

根据使用的 LLM 选择：

**OpenAI**:
```bash
pip install langchain-openai
```

**Anthropic**:
```bash
pip install langchain-anthropic
```

**Google**:
```bash
pip install langchain-google-genai
```

### 3. 配置环境变量

```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"

# Anthropic
export ANTHROPIC_API_KEY="your-api-key"

# Google
export GOOGLE_API_KEY="your-api-key"
```

### 4. 安装浏览器

browser-use 依赖 Playwright，需要安装浏览器驱动：

```bash
playwright install chromium
```

## 快速开始

### 基础使用

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent, BrowserUseAgentBuilder

async def main():
    # 方式 1：默认配置（使用 OpenAI）
    agent = BrowserUseAgent(
        model_name="gpt-4o",
        headless=False,
    )
    
    # 执行任务
    result = await agent.run_task(
        task="搜索 Python 教程并提取前 5 个链接",
        url="https://www.google.com",
    )
    
    print(result)
    await agent.close()

# 方式 2：使用构建器创建
async def main_with_builder():
    # 使用 Anthropic
    agent = BrowserUseAgentBuilder.create_with_anthropic(
        api_key="your-anthropic-key",
        model_name="claude-3-5-sonnet-20241022",
    )
    
    result = await agent.run_task(
        task="访问 https://github.com，搜索 'browser-use' 项目，获取项目描述和 Star 数"
    )
    
    print(result)
    await agent.close()

# 运行
asyncio.run(main())
```

### 命令行使用

```bash
# 基础用法
python scripts/browser_use_agent.py "搜索 Python 教程"

# 指定 URL
python scripts/browser_use_agent.py "提取页面标题和价格" --url "https://example.com"

# 指定模型
python scripts/browser_use_agent.py "搜索信息" --model "gpt-4o-mini"

# 无头模式
python scripts/browser_use_agent.py "搜索信息" --headless

# 指定提供商
python scripts/browser_use_agent.py "搜索信息" --provider anthropic --model "claude-3-5-sonnet-20241022"
```

## 高级用法

### 1. 提取结构化数据

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent

async def extract_data():
    agent = BrowserUseAgent(model_name="gpt-4o")
    
    result = await agent.run_task(
        task="""
        访问 https://example.com/products，
        提取产品信息，包含：
        - 标题 (title)
        - 价格 (price)
        - 评分 (rating)
        - 评论数 (reviews)
        
        以 JSON 格式返回结果
        """
    )
    
    print(result)
    await agent.close()

asyncio.run(extract_data())
```

### 2. 填写表单

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent

async def fill_form():
    agent = BrowserUseAgent(model_name="gpt-4o")
    
    task = """
    访问 https://example.com/contact，
    填写联系表单：
    - 姓名: John Doe
    - 邮箱: john@example.com
    - 消息: Hello, World!
    
    点击提交按钮
    """
    
    result = await agent.run_task(task)
    print(result)
    await agent.close()

asyncio.run(fill_form())
```

### 3. 搜索并收集信息

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent

async def search_collect():
    agent = BrowserUseAgent(model_name="gpt-4o")
    
    result = await agent.search_and_collect(
        query="Python web automation",
        search_engine="google",
        max_results=10,
    )
    
    print(result)
    await agent.close()

asyncio.run(search_collect())
```

### 4. 上下文管理器

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent

async def main():
    async with BrowserUseAgent(model_name="gpt-4o") as agent:
        # 自动初始化和清理
        result = await agent.run_task(
            task="搜索信息",
            url="https://www.google.com",
        )
        print(result)

asyncio.run(main())
```

### 5. 获取执行历史

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent

async def main():
    agent = BrowserUseAgent(model_name="gpt-4o")
    
    # 执行多个任务
    await agent.run_task("任务 1")
    await agent.run_task("任务 2")
    await agent.run_task("任务 3")
    
    # 获取历史
    history = agent.get_history()
    for entry in history:
        print(f"任务: {entry['task']}")
        print(f"结果: {entry['result']}")
    
    await agent.close()

asyncio.run(main())
```

## LLM 集成

### OpenAI

```python
from scripts.browser_use_agent import BrowserUseAgentBuilder

agent = BrowserUseAgentBuilder.create_with_openai(
    api_key="your-openai-key",
    model_name="gpt-4o",  # 或 gpt-4o-mini, gpt-4-turbo
)
```

### Anthropic

```python
from scripts.browser_use_agent import BrowserUseAgentBuilder

agent = BrowserUseAgentBuilder.create_with_anthropic(
    api_key="your-anthropic-key",
    model_name="claude-3-5-sonnet-20241022",
)
```

### Google

```python
from scripts.browser_use_agent import BrowserUseAgentBuilder

agent = BrowserUseAgentBuilder.create_with_google(
    api_key="your-google-key",
    model_name="gemini-1.5-pro",
)
```

### 自定义 LLM

```python
from scripts.browser_use_agent import BrowserUseAgent
from langchain_openai import ChatOpenAI

# 创建自定义 LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.0,
    max_tokens=4096,
    api_key="your-key",
)

# 使用自定义 LLM
agent = BrowserUseAgent(llm=llm, model_name="gpt-4o")
```

## 常见场景

### 场景 1：电商数据采集

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent

async def scrape_ecommerce():
    agent = BrowserUseAgent(model_name="gpt-4o")
    
    task = """
    访问 https://www.example-shop.com，
    搜索"笔记本电脑"，
    提取前 10 个产品的：
    - 名称
    - 价格
    - 评分
    - 链接
    
    以 JSON 格式返回
    """
    
    result = await agent.run_task(task)
    print(result)
    await agent.close()

asyncio.run(scrape_ecommerce())
```

### 场景 2：自动注册流程

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent

async def auto_register():
    agent = BrowserUseAgent(model_name="gpt-4o")
    
    task = """
    访问 https://www.example.com/register，
    填写注册表单：
    - 用户名: testuser
    - 邮箱: testuser@example.com
    - 密码: Test123!@#
    提交表单并验证是否成功
    """
    
    result = await agent.run_task(task)
    print(result)
    await agent.close()

asyncio.run(auto_register())
```

### 场景 3：内容监控

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent

async def monitor_content():
    agent = BrowserUseAgent(model_name="gpt-4o")
    
    task = """
    访问 https://news.example.com，
    检查是否有标题包含"AI"的新闻，
    如果有，提取标题和链接
    """
    
    result = await agent.run_task(task)
    print(result)
    await agent.close()

asyncio.run(monitor_content())
```

## 最佳实践

### 1. 任务描述

**好的任务描述**：
```
✅ 访问 https://example.com，找到"联系我们"按钮，点击它，
   提取所有联系信息（电话、邮箱、地址）
```

**不好的任务描述**：
```
❌ 获取联系信息
```

### 2. 模型选择

- **GPT-4o**：最适合复杂任务，性能好
- **GPT-4o-mini**：成本更低，适合简单任务
- **Claude 3.5 Sonnet**：长文本处理能力强
- **Gemini 1.5 Pro**：多语言支持好

### 3. 错误处理

```python
import asyncio
from scripts.browser_use_agent import BrowserUseAgent, BrowserUseAgentError

async def safe_run():
    try:
        agent = BrowserUseAgent(model_name="gpt-4o")
        result = await agent.run_task("任务描述")
        
        if result["success"]:
            print("成功:", result["result"])
        else:
            print("失败:", result["error"])
            
    except BrowserUseAgentError as e:
        print("Agent 错误:", e)
    except Exception as e:
        print("未知错误:", e)
    finally:
        if 'agent' in locals():
            await agent.close()

asyncio.run(safe_run())
```

### 4. 组合使用 Playwright 和 Browser-Use

```python
import asyncio
from scripts.playwright_cli import PlaywrightCLI
from scripts.browser_use_agent import BrowserUseAgent

async def combined_workflow():
    # 1. Playwright 处理登录（固定操作）
    pw_cli = PlaywrightCLI(headless=False)
    await pw_cli.start()
    
    await pw_cli.navigate("https://example.com/login")
    await pw_cli.fill("#username", "myuser")
    await pw_cli.fill("#password", "mypass")
    await pw_cli.click("#login-btn")
    await pw_cli.wait_for_navigation()
    
    # 2. Browser-Use 处理复杂任务
    bu_agent = BrowserUseAgent(model_name="gpt-4o")
    result = await bu_agent.run_task(
        task="导航到仪表板，提取最近 7 天的数据"
    )
    
    print(result)
    
    # 3. Playwright 处理登出
    await pw_cli.click("#logout-btn")
    
    # 清理
    await pw_cli.close()
    await bu_agent.close()

asyncio.run(combined_workflow())
```

### 5. 性能优化

- 使用缓存：避免重复导航
- 减少 LLM 调用：合并相似操作
- 并行执行：多个独立任务并行
- 合理设置超时：避免无限等待

### 6. 成本控制

- 使用 `gpt-4o-mini` 降低成本
- 限制最大步骤数
- 使用缓存减少重复调用
- 监控 LLM 调用次数

## 注意事项

1. **API 密钥安全**：不要在代码中硬编码 API 密钥
2. **速率限制**：注意 LLM API 的速率限制
3. **错误处理**：始终处理可能的异常
4. **资源清理**：使用 `await agent.close()` 或上下文管理器
5. **合规性**：遵守目标网站的 robots.txt 和使用条款

## API 版本说明

**browser-use 0.12.x 新 API**：

```python
# 新版本使用 BrowserProfile 替代 Browser 和 BrowserConfig
from browser_use import Agent, BrowserProfile

# 创建浏览器配置
browser_profile = BrowserProfile(
    headless=True,
    # 其他配置...
)

# 创建 Agent
agent = Agent(
    task="任务描述",
    llm=llm,
    browser_profile=browser_profile,
)

# 执行任务
result = await agent.run()
await agent.close()
```

**主要变化**：
- `Browser` 和 `BrowserConfig` 合并为 `BrowserProfile`
- Agent 构造函数直接接收 `browser_profile` 参数
- 更简化的 API 设计

## 参考资源

- Browser-Use 官方文档: https://github.com/browser-use/browser-use
- LangChain 文档: https://python.langchain.com/
- OpenAI API 文档: https://platform.openai.com/docs
- Anthropic API 文档: https://docs.anthropic.com/
