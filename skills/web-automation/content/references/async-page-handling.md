# 异步动态页面处理指南

## 概览

现代网页大量使用异步加载技术（AJAX、SPA、懒加载），传统的 DOMContentLoaded 事件可能无法获取完整内容。本指南介绍如何处理异步动态页面。

## 问题分析

### 常见异步加载场景

1. **单页应用（SPA）**：React、Vue、Angular 等框架构建的应用
2. **懒加载内容**：滚动时才加载的图片、列表、评论
3. **数据延迟加载**：通过 AJAX 请求获取数据
4. **动态渲染**：JavaScript 动态生成的内容

### 传统方法的局限

```python
# ❌ 传统方法可能失效
await page.goto(url, wait_until="domcontentloaded")
# 此时内容可能还未完全加载
```

## 解决方案

### 策略 1：多阶段等待

```python
import asyncio
from playwright.async_api import async_playwright

async def load_page_with_strategies(page, url):
    """使用多种策略加载页面"""

    # 1. 等待 DOMContentLoaded
    response = await page.goto(url, wait_until="domcontentloaded")
    print("✅ DOMContentLoaded 完成")

    # 2. 等待网络空闲
    try:
        await page.wait_for_load_state('networkidle', timeout=15000)
        print("✅ 网络已空闲")
    except:
        print("⚠️ 网络未完全空闲，继续处理")

    # 3. 滚动页面触发懒加载
    await scroll_to_load_content(page)

    # 4. 等待动态内容稳定
    await wait_for_dynamic_content(page)

    return response
```

### 策略 2：滚动触发懒加载

```python
async def scroll_to_load_content(page):
    """滚动页面触发懒加载"""

    # 获取页面高度
    height = await page.evaluate('() => document.body.scrollHeight')
    viewport_height = await page.evaluate('() => window.innerHeight')

    # 分段滚动
    scroll_steps = 5
    for i in range(scroll_steps):
        scroll_position = (height * (i + 1)) // scroll_steps
        await page.evaluate(f'window.scrollTo(0, {scroll_position})')
        await asyncio.sleep(1)

    # 滚动回顶部
    await page.evaluate('window.scrollTo(0, 0)')
    await asyncio.sleep(0.5)

    print("✅ 滚动完成")
```

### 策略 3：动态内容稳定检测

```python
async def wait_for_dynamic_content(page, max_wait=10):
    """等待动态内容加载完成"""

    print("⏳ 检测动态内容...")

    # 记录初始文本长度
    initial_length = await page.evaluate('() => document.body.innerText.length')

    # 多次检查文本长度是否稳定
    stable_count = 0
    for i in range(max_wait):
        await asyncio.sleep(1)
        current_length = await page.evaluate('() => document.body.innerText.length')

        if current_length == initial_length:
            stable_count += 1
        else:
            stable_count = 0
            initial_length = current_length

        # 如果连续3次长度不变，认为内容稳定
        if stable_count >= 3:
            print(f"✅ 内容已稳定 (等待 {i+1} 秒)")
            return True

    print("⚠️ 等待超时，继续处理")
    return False
```

### 策略 4：等待特定元素

```python
async def wait_for_specific_element(page, selector, timeout=30000):
    """等待特定元素出现"""

    try:
        await page.wait_for_selector(selector, timeout=timeout)
        print(f"✅ 元素已出现: {selector}")
        return True
    except:
        print(f"⚠️ 元素未出现: {selector}")
        return False

# 使用示例
await wait_for_specific_element(page, '.content-loaded')
await wait_for_specific_element(page, '.data-loaded[data-ready="true"]')
```

### 策略 5：等待网络请求完成

```python
async def wait_for_api_response(page, url_pattern, timeout=30000):
    """等待特定的 API 请求完成"""

    async with page.expect_response(url_pattern, timeout=timeout) as response_info:
        print(f"⏳ 等待 API 请求: {url_pattern}")
        response = await response_info.value
        print(f"✅ API 请求完成: {response.status}")
        return response

# 使用示例
await wait_for_api_response(page, '**/api/data')
await wait_for_api_response(page, '**/graphql')
```

## 完整示例

### 异步页面爬取脚本

```python
import asyncio
from playwright.async_api import async_playwright

async def crawl_async_page(url):
    """爬取异步动态页面"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        page = await context.new_page()

        try:
            # 加载页面（多策略）
            response = await load_page_with_strategies(page, url)

            if response and response.status == 200:
                # 提取内容
                title = await page.title()
                body_text = await page.evaluate('() => document.body.innerText')

                print(f"✅ 页面加载成功")
                print(f"   标题: {title}")
                print(f"   文本长度: {len(body_text):,} 字符")

                return {
                    "title": title,
                    "url": page.url,
                    "text": body_text
                }
            else:
                print(f"❌ 页面加载失败: {response.status}")
                return None

        finally:
            await browser.close()


async def load_page_with_strategies(page, url):
    """使用多种策略加载页面"""

    # 1. 等待 DOMContentLoaded
    response = await page.goto(url, wait_until="domcontentloaded")

    # 2. 等待网络空闲（带超时）
    try:
        await page.wait_for_load_state('networkidle', timeout=15000)
        print("✅ 网络已空闲")
    except:
        print("⚠️ 网络未完全空闲")

    # 3. 滚动触发懒加载
    await scroll_to_load_content(page)

    # 4. 等待动态内容稳定
    await wait_for_dynamic_content(page)

    return response


async def scroll_to_load_content(page):
    """滚动页面触发懒加载"""

    height = await page.evaluate('() => document.body.scrollHeight')

    # 分段滚动
    for i in range(5):
        scroll_position = (height * (i + 1)) // 5
        await page.evaluate(f'window.scrollTo(0, {scroll_position})')
        await asyncio.sleep(1)

    await page.evaluate('window.scrollTo(0, 0)')
    await asyncio.sleep(0.5)


async def wait_for_dynamic_content(page, max_wait=10):
    """等待动态内容稳定"""

    initial_length = await page.evaluate('() => document.body.innerText.length')
    stable_count = 0

    for i in range(max_wait):
        await asyncio.sleep(1)
        current_length = await page.evaluate('() => document.body.innerText.length')

        if current_length == initial_length:
            stable_count += 1
        else:
            stable_count = 0
            initial_length = current_length

        if stable_count >= 3:
            print(f"✅ 内容已稳定")
            return True

    print("⚠️ 等待超时")
    return False


# 使用示例
async def main():
    url = "https://example.com"
    result = await crawl_async_page(url)
    if result:
        print(result)

asyncio.run(main())
```

## 超时控制

### 分级超时策略

```python
import asyncio

async def load_with_timeout_control(page, url):
    """带超时控制的页面加载"""

    try:
        # 总体超时控制
        async with asyncio.timeout(120):  # 最多等待120秒

            # 页面加载超时
            response = await asyncio.wait_for(
                page.goto(url, wait_until="domcontentloaded"),
                timeout=30000
            )

            # 网络空闲超时
            try:
                await asyncio.wait_for(
                    page.wait_for_load_state('networkidle'),
                    timeout=15000
                )
            except asyncio.TimeoutError:
                print("⚠️ 网络空闲超时")

            # 滚动超时
            try:
                await asyncio.wait_for(
                    scroll_to_load_content(page),
                    timeout=15000
                )
            except asyncio.TimeoutError:
                print("⚠️ 滚动超时")

            # 动态内容检测超时
            try:
                await asyncio.wait_for(
                    wait_for_dynamic_content(page),
                    timeout=15000
                )
            except asyncio.TimeoutError:
                print("⚠️ 动态内容检测超时")

        return response

    except asyncio.TimeoutError:
        print("❌ 总体超时")
        return None
```

## 最佳实践

### 1. 组合策略

不要依赖单一策略，组合多种策略：

```python
# ✅ 推荐：组合策略
1. DOMContentLoaded（基础）
2. 网络空闲（中级）
3. 滚动触发（高级）
4. 内容稳定检测（高级）
```

### 2. 超时控制

设置合理的超时时间，避免无限等待：

```python
# 超时时间建议
- 页面加载: 30秒
- 网络空闲: 15秒
- 滚动: 15秒
- 动态检测: 10秒
- 总体: 120秒
```

### 3. 错误容错

即使某个策略失败，也要继续处理：

```python
# ✅ 推荐：错误容错
try:
    await page.wait_for_load_state('networkidle')
except:
    print("⚠️ 网络未完全空闲，继续处理")
    # 继续下一步
```

### 4. 日志记录

详细记录每个步骤的执行情况：

```python
# ✅ 推荐：详细日志
print("✅ DOMContentLoaded 完成")
print("⚠️ 网络未完全空闲")
print("⏳ 检测动态内容...")
print("✅ 内容已稳定 (等待 4 秒)")
```

## 常见问题

### Q1: 如何判断页面是否需要特殊处理？

**A**: 观察页面特征：
- 内容在滚动后出现 → 需要滚动策略
- 初始加载内容很少 → 可能是 SPA
- 网络请求持续活跃 → 需要等待网络空闲
- F12 查看网络请求 → 有 AJAX 请求

### Q2: 超时时间应该设置多少？

**A**: 根据页面复杂度调整：
- 简单页面: 30秒
- 中等页面: 60秒
- 复杂页面: 120秒

### Q3: 如何处理无限加载？

**A**: 设置最大滚动次数和最大等待时间：
```python
max_scrolls = 5
max_wait = 10
```

### Q4: 如何提取动态加载的内容？

**A**: 确保在所有策略执行完成后再提取：
```python
# 确保所有策略执行完成
await load_page_with_strategies(page, url)

# 然后再提取内容
content = await page.evaluate('() => document.body.innerText')
```

## 测试验证

使用提供的测试脚本验证异步动态页面处理能力：

```bash
# 运行完整测试
python3 /workspace/full-test/full_test_async.py

# 测试覆盖：
# - 网易新闻（3级爬取）
# - 中国政府网（3级爬取）
# - CSDN（3级爬取）
# - vLLM 文档（3级爬取）
```

## 总结

异步动态页面处理需要组合多种策略：

1. **基础策略**: DOMContentLoaded
2. **中级策略**: 网络空闲、特定元素
3. **高级策略**: 滚动触发、内容稳定检测
4. **防护措施**: 超时控制、错误容错

通过合理组合这些策略，可以应对大多数异步动态页面。
