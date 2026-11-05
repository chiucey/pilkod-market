# Browser-Use 使用指南

## 目录
- [概览](#概览)
- [集成方式](#集成方式)
- [智能交互](#智能交互)
- [错误恢复](#错误恢复)
- [最佳实践](#最佳实践)

## 概览
Browser-use 是一个 LLM 原生的浏览器自动化工具，提供智能化的网页交互能力。它基于 Playwright 构建，强调"思考-行动"循环。

**核心特性**：
- LLM 驱动的智能决策
- 自动错误恢复
- 多步骤任务规划
- 自然语言交互接口

**适用场景**：
- 复杂的网页操作流程
- 需要智能判断的交互
- 动态网页的自动化

## 集成方式

### 基本集成
```python
from browser_use import Agent

agent = Agent(
    task="在亚马逊上搜索并购买一本书",
    browser_context=context  # Playwright 上下文
)

result = await agent.run()
```

### 与 Playwright Manager 集成
```python
from playwright_manager import BrowserManager
from browser_wrapper import BrowserAgent

# 创建浏览器
manager = BrowserManager()
await manager.create_browser()

# 创建智能代理
agent = BrowserAgent(manager)

# 执行智能交互
result = await agent.navigate(url="https://example.com")
```

### 自定义配置
```python
agent = BrowserAgent(
    manager=manager,
    use_browser_use=True,
    max_retries=3,
    timeout=30
)
```

## 智能交互

### 1. 智能导航
```python
result = await agent.navigate(
    url="https://example.com",
    wait_for_selector=".content",
    human_simulation=True,  # 模拟人类行为
    random_delay=True       # 随机延迟
)
```

**智能特性**：
- 自动处理弹窗和重定向
- 智能等待加载完成
- 模拟人类浏览行为

### 2. 智能点击
```python
result = await agent.click(
    selector="button:has-text('确认')",
    timeout=10000,
    human_simulation=True
)
```

**智能特性**：
- 自动滚动到元素可见位置
- 处理遮挡元素
- 重试失败的点击

### 3. 智能填充
```python
result = await agent.fill(
    selector="input[name='username']",
    text="user123",
    human_simulation=True  # 逐字输入
)
```

**智能特性**：
- 自动清空已有内容
- 模拟真实输入速度
- 处理输入框遮挡

### 4. 智能提取
```python
result = await agent.extract(
    selector=".article-content",
    extract_type="text",
    multiple=True
)
```

**智能特性**：
- 自动处理动态加载内容
- 提取结构化数据
- 支持多种数据类型

## 错误恢复

### 自动重试机制
```python
agent = BrowserAgent(manager)

# 内置重试逻辑
result = await agent.click(selector, max_retries=3)
```

### 智能错误处理
```python
try:
    result = await agent.navigate(url)
except Exception as e:
    # 自动分析错误原因
    if "timeout" in str(e):
        # 重试或调整策略
        await agent.navigate(url, timeout=60000)
    elif "not found" in str(e):
        # 尝试替代选择器
        await agent.navigate(url, wait_for_selector=".alternative")
```

### 状态恢复
```python
# 保存当前状态
state = await agent.page.evaluate("() => ({url: location.href, title: document.title})")

# 恢复状态
await agent.navigate(state["url"])
```

## 最佳实践

### 1. 任务分解
将复杂任务分解为多个子任务：
```python
# ✅ 正确：分解任务
await agent.navigate(url)
await agent.click(selector)
await agent.extract(data_selector)

# ❌ 错误：一次性完成所有操作
result = await agent.complex_operation(url, selector, data_selector)
```

### 2. 使用人类行为模拟
```python
# ✅ 正确：模拟人类行为
await agent.click(selector, human_simulation=True)

# ❌ 错误：机械式操作
await agent.page.click(selector)
```

### 3. 合理设置超时
```python
# ✅ 正确：根据页面复杂度设置超时
await agent.navigate(url, timeout=30000)  # 首页
await agent.navigate(detail_url, timeout=10000)  # 详情页

# ❌ 错误：统一超时
await agent.navigate(url, timeout=10000)  # 可能超时
```

### 4. 错误处理与日志
```python
try:
    result = await agent.navigate(url)
    log_result(result)
except Exception as e:
    log_error(e)
    # 尝试恢复或退出
```

## 使用边界

### 性能限制
- **思考延迟**: 每次决策需要 1-5 秒的思考时间
- **API 调用**: 频繁的 API 调用可能产生成本
- **并发限制**: 不建议同时运行多个智能代理

### 功能限制
- **复杂表单**: 某些复杂的表单可能需要手动调整
- **验证码**: 无法自动处理复杂验证码
- **第三方集成**: 与第三方服务的集成需要额外配置

### 适用场景
- ✅ 适合：需要智能判断的复杂交互
- ✅ 适合：动态网页的自动化
- ✅ 适合：多步骤任务流程
- ❌ 不适合：简单重复性任务（使用 Playwright）
- ❌ 不适合：高性能批量操作（使用 Playwright 并发）
- ❌ 不适合：需要精确控制的场景（使用 Playwright）

## 高级功能

### 自定义决策逻辑
```python
class CustomAgent(BrowserAgent):
    async def should_retry(self, error: Exception) -> bool:
        # 自定义重试逻辑
        if "timeout" in str(error):
            return True
        return False
```

### 任务规划
```python
tasks = [
    {"action": "navigate", "url": "https://example.com"},
    {"action": "click", "selector": "button"},
    {"action": "extract", "selector": ".content"}
]

for task in tasks:
    result = await self.execute_task(task)
    if not result["success"]:
        break
```

### 多模态交互
```python
# 结合 OCR
ocr_result = await agent.screenshot_and_ocr()
if "验证码" in ocr_result["text"]:
    await agent.handle_captcha(ocr_result)
```
