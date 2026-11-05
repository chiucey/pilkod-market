# Playwright 使用指南

## 目录
- [概览](#概览)
- [API 参考](#api-参考)
- [异步模式](#异步模式)
- [浏览器配置](#浏览器配置)
- [反爬策略](#反爬策略)
- [异常处理](#异常处理)
- [性能优化](#性能优化)

## 概览
Playwright 是微软开发的现代化浏览器自动化框架，支持多浏览器（Chromium、Firefox、WebKit）、异步操作、网络拦截等强大功能。

**适用场景**：
- 网页自动化测试
- 数据抓取与采集
- UI 自动化操作
- 网页性能监控

## API 参考

### 核心类
- `BrowserManager`: 浏览器生命周期管理
- `Page`: 页面操作核心类
- `Locator`: 元素定位器

### 主要方法

#### 浏览器管理
```python
# 创建浏览器
await manager.create_browser(
    headless=False,           # 是否无头模式
    proxy="socks5://127.0.0.1:1080",  # 代理
    user_agent="自定义 UA",   # User-Agent
    timeout=30000,            # 超时时间
    viewport={"width": 1920, "height": 1080}  # 视口大小
)

# 关闭浏览器
await manager.close_browser()
```

#### 页面操作
```python
# 导航
await page.goto(url, wait_until="networkidle", timeout=30000)

# 等待元素
await page.wait_for_selector(selector, state="visible", timeout=10000)

# 点击元素
await page.click(selector, timeout=10000, force=False)

# 填充输入框
await page.fill(selector, text)

# 截图
await page.screenshot(path="screenshot.png", full_page=True)

# 执行 JavaScript
result = await page.evaluate("document.title")
```

#### 元素定位
```python
# CSS 选择器
await page.locator(".class").click()

# 文本选择器
await page.locator("text=确认").click()

# XPath
await page.locator("//div[@class='content']").click()

# 组合选择器
await page.locator("button >> text=提交").click()
```

## 异步模式

### 基本语法
```python
import asyncio

async def main():
    # 创建浏览器
    manager = BrowserManager()
    await manager.create_browser()
    
    # 异步操作
    await manager.page.goto("https://example.com")
    await manager.page.click("button")
    
    # 关闭浏览器
    await manager.close_browser()

asyncio.run(main())
```

### 并发操作
```python
# 同时打开多个页面
tasks = []
for url in urls:
    task = asyncio.create_task(process_url(url))
    tasks.append(task)

results = await asyncio.gather(*tasks)
```

### 超时控制
```python
# 设置默认超时
manager.context.set_default_timeout(30000)

# 单次操作超时
await page.click(selector, timeout=10000)
```

## 浏览器配置

### 反自动化检测
```python
launch_options = {
    "headless": False,
    "args": [
        "--disable-blink-features=AutomationControlled",  # 绕过自动化检测
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled"
    ]
}
```

### 代理设置
```python
# SOCKS5 代理
launch_options["proxy"] = {"server": "socks5://127.0.0.1:1080"}

# HTTP 代理
launch_options["proxy"] = {"server": "http://proxy.com:8080"}
```

### 用户代理
```python
context_options = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

### 语言和时区
```python
context_options = {
    "locale": "zh-CN",
    "timezone_id": "Asia/Shanghai"
}
```

## 反爬策略

### 1. 浏览器指纹伪装
```python
# 使用真实浏览器配置
context_options = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "真实的 UA",
    "locale": "zh-CN",
    "timezone_id": "Asia/Shanghai"
}
```

### 2. 随机延迟
```python
import random
import asyncio

await asyncio.sleep(random.uniform(0.5, 2.0))
```

### 3. 模拟人类行为
```python
# 模拟鼠标移动
await page.mouse.move(x, y)

# 模拟逐字输入
for char in text:
    await page.type(selector, char, delay=100)
```

### 4. Cookie 管理
```python
# 保存 Cookie
cookies = await context.cookies()

# 加载 Cookie
await context.add_cookies(cookies)
```

### 5. 网络拦截
```python
# 拦截请求
async def handle_route(route):
    # 修改请求头
    headers = route.request.headers
    headers["X-Custom-Header"] = "value"
    await route.continue_(headers=headers)

await page.route("**/*", handle_route)
```

## 异常处理

### 常见异常
- `TimeoutError`: 操作超时
- `Error`: 元素未找到
- `TargetClosedError`: 页面已关闭

### 异常捕获
```python
try:
    await page.click(selector, timeout=10000)
except TimeoutError:
    print("元素未找到或超时")
except Exception as e:
    print(f"操作失败: {e}")
```

### 重试机制
```python
async def retry_operation(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 指数退避
```

## 性能优化

### 1. 禁用不必要的功能
```python
context_options = {
    "java_script_enabled": True,  # 禁用 JS 可提升性能
    "ignore_https_errors": True
}
```

### 2. 资源拦截
```python
# 拦截图片、字体等资源
await page.route("**/*.{png,jpg,jpeg,svg,woff,woff2}", lambda route: route.abort())
```

### 3. 缓存管理
```python
# 启用缓存
await page.goto(url, wait_until="domcontentloaded")
```

### 4. 页面复用
```python
# 复用同一个浏览器上下文
context = await browser.new_context()
page1 = await context.new_page()
page2 = await context.new_page()
```

## 使用边界

### 性能限制
- **内存占用**: 每个浏览器实例约占用 200-500MB
- **并发限制**: 单机建议不超过 10 个并发实例
- **超时建议**: 页面加载超时建议 30s，元素等待建议 10s

### 功能限制
- 不支持移动端原生 App 自动化
- 某些复杂的 WebGL 场景可能不稳定
- 需要手动处理的验证码无法自动识别

### 最佳实践
- 优先使用 CSS 选择器而非 XPath
- 合理设置超时时间，避免无限等待
- 操作完成后及时关闭浏览器，释放资源
- 使用上下文隔离不同任务
