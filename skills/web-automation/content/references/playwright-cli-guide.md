# Playwright CLI 使用指南

## 概览

本 Skill 现在支持 Playwright CLI 最佳实践，提供更标准、更可靠的浏览器自动化功能。

## 核心改进

### 1. Playwright CLI 工具

**命令行工具功能：**
- 代码生成（codegen）：录制操作并生成测试脚本
- 测试运行：运行标准 Playwright 测试
- 浏览器安装：自动安装所需的浏览器
- 追踪查看：查看测试执行追踪

### 2. 异步 Playwright 浏览器

**改进的浏览器操作：**
- 异步操作，性能更优
- 智能等待策略
- 更好的错误处理
- 支持完整的页面交互

## 使用方式

### 方式 1：使用 Playwright CLI 工具

```bash
# 1. 代码生成（录制操作）
python scripts/playwright_cli.py codegen https://example.com

# 2. 安装浏览器
python scripts/playwright_cli.py install chromium

# 3. 运行测试
python scripts/playwright_cli.py run generated_test.py

# 4. 查看追踪
python scripts/playwright_cli.py show-trace trace.zip
```

### 方式 2：使用异步 Playwright 浏览器

```python
import asyncio
from scripts.playwright_cli import AsyncPlaywrightBrowser

async def scrape_website(url):
    # 创建浏览器
    browser = AsyncPlaywrightBrowser(
        headless=True,
        browser_type="chromium",
        timeout=30000
    )

    # 启动浏览器
    await browser.start()

    # 导航到网页
    await browser.goto(url, wait_until="networkidle")

    # 等待页面加载
    await browser.wait_for_load_state("domcontentloaded")

    # 滚动页面
    await browser.scroll_down(500)

    # 截图
    await browser.screenshot("screenshot.png", full_page=True)

    # 关闭浏览器
    await browser.close()

# 运行异步函数
asyncio.run(scrape_website("https://example.com"))
```

### 方式 3：使用工作流引擎

```bash
# 使用改进后的网页抓取工作流
python scripts/workflow_engine.py web-scraping https://example.com --type text
```

## 改进点

### 1. 更智能的等待策略

**等待策略选项：**
- `load`: 页面完全加载
- `domcontentloaded`: DOM 内容加载完成
- `networkidle`: 网络空闲（推荐用于动态页面）
- `commit`: 页面提交

**使用示例：**
```python
await browser.goto(url, wait_until="networkidle")
await browser.wait_for_selector("#content", state="visible")
```

### 2. 更好的错误处理

**错误处理改进：**
- 详细的错误信息
- 超时控制
- 自动重试机制
- 资源清理保证

### 3. 支持更多页面交互

**支持的操作：**
- 点击（click）
- 填写（fill）
- 滚动（scroll）
- 等待（wait）
- 获取文本（get_text）

### 4. 性能优化

**性能优化：**
- 异步操作
- 并行处理
- 资源复用
- 智能缓存

## 最佳实践

### 1. 使用代码生成

对于复杂的页面操作，建议使用代码生成：

```bash
# 录制操作
python scripts/playwright_cli.py codegen https://example.com

# 这将打开一个浏览器窗口，您可以手动操作
# 操作结束后，代码将保存到 generated_test.py
```

### 2. 设置合理的超时

```python
browser = AsyncPlaywrightBrowser(
    timeout=30000,  # 30 秒超时
    slow_mo=100     # 慢动作模式，便于调试
)
```

### 3. 使用智能等待

```python
# 等待特定元素出现
await browser.wait_for_selector("#button", state="visible")

# 等待页面加载完成
await browser.wait_for_load_state("networkidle")
```

### 4. 处理动态内容

```python
# 滚动以触发懒加载
for _ in range(3):
    await browser.scroll_down(500)
    await asyncio.sleep(1)  # 等待内容加载
```

### 5. 错误处理

```python
try:
    await browser.goto(url)
    await browser.wait_for_selector("#content")
    text = await browser.get_text("#content")
except Exception as e:
    print(f"操作失败: {e}")
finally:
    await browser.close()  # 确保关闭浏览器
```

## 迁移指南

### 从旧版本迁移

如果您之前使用的是旧版本的 Playwright 实现，以下是迁移步骤：

**旧代码：**
```python
from playwright_manager import PlaywrightManager
from browser_wrapper import BrowserWrapper

pm = PlaywrightManager()
browser = pm.create_browser()
bw = BrowserWrapper(browser)
bw.navigate(url)
```

**新代码：**
```python
import asyncio
from playwright_cli import AsyncPlaywrightBrowser

async def scrape():
    browser = AsyncPlaywrightBrowser()
    await browser.start()
    await browser.goto(url)
    await browser.close()

asyncio.run(scrape())
```

## 常见问题

### Q: 如何处理需要登录的页面？
A: 使用 Cookie 或手动登录后保存状态：

```python
# 使用 Cookie
context = await browser.context
await context.add_cookies(cookies)
```

### Q: 如何处理验证码？
A: 使用 OCR 识别或人工介入：

```python
# 截图验证码
await browser.screenshot("captcha.png")

# OCR 识别
from ocr_service import OCRService
ocr = OCRService()
result = ocr.recognize_image("captcha.png")
captcha_text = result["text"]

# 填写验证码
await browser.fill("#captcha", captcha_text)
```

### Q: 如何提高抓取速度？
A: 使用无头模式和并行处理：

```python
browser = AsyncPlaywrightBrowser(
    headless=True,
    slow_mo=0
)
```

### Q: 如何调试？
A: 使用非无头模式和慢动作模式：

```python
browser = AsyncPlaywrightBrowser(
    headless=False,  # 显示浏览器
    slow_mo=1000     # 慢动作模式
)
```

## 相关资源

- [Playwright 官方文档](https://playwright.dev/)
- [Playwright CLI 文档](https://playwright.dev/docs/cli)
- [工作流引擎指南](workflow-guide.md)
- [反爬虫指南](anti-scraping-advanced.md)
