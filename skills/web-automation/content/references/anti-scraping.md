# 反爬与异常处理指南

## 目录
- [常见反爬机制](#常见反爬机制)
- [检测方法](#检测方法)
- [绕过策略](#绕过策略)
- [验证码处理](#验证码处理)
- [风控规避](#风控规避)

## 常见反爬机制

### 1. IP 限制
- **特征**: 频繁访问后返回 403 或连接超时
- **触发条件**: 单 IP 短时间内大量请求
- **检测方式**: 观察响应状态码和延迟

### 2. User-Agent 检测
- **特征**: 使用默认或可疑的 User-Agent 被拒绝
- **触发条件**: User-Agent 为空或包含自动化特征
- **检测方式**: 检查 HTTP 响应头

### 3. Cookie/Session 验证
- **特征**: 需要登录或携带特定 Cookie
- **触发条件**: 缺少必要的 Cookie 或 Session
- **检测方式**: 观察是否需要登录验证

### 4. JavaScript 挑战
- **特征**: 页面需要执行 JS 才能加载内容
- **触发条件**: 直接请求获取不到完整内容
- **检测方式**: 查看页面源码与渲染后的差异

### 5. 行为分析
- **特征**: 非人类访问模式被识别
- **触发条件**: 访问频率过高、路径异常
- **检测方式**: 分析访问日志

### 6. 浏览器指纹检测
- **特征**: 检测自动化工具特征
- **触发条件**: 使用无头浏览器或自动化工具
- **检测方式**: 检查 navigator 对象

### 7. 验证码
- **特征**: 访问一定次数后出现验证码
- **触发条件**: 频繁访问或异常行为
- **检测方式**: 页面出现验证码元素

## 检测方法

### 1. 响应状态码检测
```python
response = await page.goto(url)

if response.status == 403:
    print("可能被 IP 封禁")
elif response.status == 429:
    print("请求过于频繁")
```

### 2. 内容检测
```python
content = await page.content()

if "验证码" in content or "captcha" in content.lower():
    print("触发验证码")
elif "访问受限" in content or "access denied" in content.lower():
    print("访问被拒绝")
```

### 3. 行为检测
```python
import time

# 记录访问时间
start_time = time.time()

# 执行操作
await page.click(selector)

# 计算延迟
delay = time.time() - start_time

if delay > 5:
    print("可能被限速")
```

### 4. Cookie 检测
```python
cookies = await context.cookies()

if not cookies:
    print("可能需要登录或携带 Cookie")
```

## 绕过策略

### 1. IP 限制绕过
```python
# 使用代理
await manager.create_browser(
    proxy="socks5://127.0.0.1:1080"
)

# 轮换代理
proxies = [
    "socks5://proxy1:1080",
    "socks5://proxy2:1080",
    "socks5://proxy3:1080"
]

for proxy in proxies:
    await manager.create_browser(proxy=proxy)
    # 执行操作
    await manager.close_browser()
```

### 2. User-Agent 伪装
```python
# 使用真实浏览器的 User-Agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

await manager.create_browser(
    user_agent=user_agent
)

# 定期更换 User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)..."
]
```

### 3. Cookie/Session 管理
```python
# 保存 Cookie
cookies = await context.cookies()
with open("cookies.json", "w") as f:
    json.dump(cookies, f)

# 加载 Cookie
with open("cookies.json") as f:
    cookies = json.load(f)
await context.add_cookies(cookies)
```

### 4. JavaScript 挑战处理
```python
# 等待页面完全加载
await page.goto(url, wait_until="networkidle")

# 等待特定元素出现
await page.wait_for_selector(".content", timeout=30000)

# 执行必要的 JavaScript
await page.evaluate("""
    // 执行页面需要的 JS 代码
    window.scrollTo(0, document.body.scrollHeight);
""")
```

### 5. 人类行为模拟
```python
import random
import asyncio

# 随机延迟
await asyncio.sleep(random.uniform(1, 3))

# 模拟鼠标移动
await page.mouse.move(x, y)
await asyncio.sleep(random.uniform(0.1, 0.3))

# 逐字输入
for char in text:
    await page.type(selector, char, delay=random.randint(50, 150))

# 随机滚动
scroll_distance = random.randint(300, 800)
await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
```

### 6. 浏览器指纹伪装
```python
# 使用浏览器上下文隔离
context = await browser.new_context(
    viewport={"width": 1920, "height": 1080},
    user_agent=user_agent,
    locale="zh-CN",
    timezone_id="Asia/Shanghai"
)

# 注入脚本修改指纹
await page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

## 验证码处理

### 1. 识别验证码
```python
# 截图验证码区域
await page.screenshot(
    path="captcha.png",
    clip={"x": 100, "y": 100, "width": 200, "height": 50}
)

# 使用 OCR 识别
from ocr_service import OCRService

service = OCRService()
result = service.recognize_image("captcha.png")

if result["success"]:
    captcha_code = result["full_text"].strip()
    print(f"识别到验证码: {captcha_code}")
```

### 2. 输入验证码
```python
# 填充识别的验证码
await page.fill("#captcha-input", captcha_code)

# 点击提交
await page.click("#submit-button")
```

### 3. 手动处理
```python
# 提示用户手动输入
captcha_image = await page.screenshot()
print("请查看截图并输入验证码:")

# 等待用户输入
import sys
captcha_code = input("验证码: ")

# 填充验证码
await page.fill("#captcha-input", captcha_code)
```

### 4. 第三方验证码服务
```python
# 集成第三方验证码识别服务（如 2Captcha、超级鹰等）
# 需要购买服务并获取 API Key

async def solve_captcha(image_path):
    # 调用第三方 API
    # ...
    return captcha_code
```

## 风控规避

### 1. 访问频率控制
```python
import time
import random

# 控制访问频率
async def controlled_request(url):
    # 随机延迟
    delay = random.uniform(2, 5)
    await asyncio.sleep(delay)
    
    # 执行请求
    await page.goto(url)
```

### 2. 请求间隔控制
```python
# 使用指数退避策略
async def exponential_backoff(attempt, base_delay=2):
    delay = base_delay ** attempt
    await asyncio.sleep(delay)

for i in range(5):
    try:
        result = await perform_operation()
        break
    except Exception as e:
        await exponential_backoff(i)
```

### 3. 异常行为检测
```python
# 监控异常行为
async def safe_operation(operation):
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # 分析错误类型
            if "403" in str(e):
                print("可能被 IP 封禁，尝试更换代理")
            elif "captcha" in str(e):
                print("触发验证码，尝试处理")
            
            await asyncio.sleep(10)  # 冷却时间
```

### 4. 日志记录
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def logged_operation(operation):
    logging.info(f"开始执行操作: {operation.__name__}")
    
    try:
        result = await operation()
        logging.info(f"操作成功: {operation.__name__}")
        return result
    except Exception as e:
        logging.error(f"操作失败: {operation.__name__} - {str(e)}")
        raise
```

## 最佳实践

1. **渐进式访问**: 从低频访问开始，逐步增加频率
2. **多样化行为**: 模拟真实用户的浏览模式
3. **资源隔离**: 使用不同的浏览器上下文隔离不同任务
4. **监控日志**: 记录所有操作，便于问题排查
5. **优雅降级**: 遇到反爬时降低访问频率或暂停
6. **定期维护**: 定期更新代理、Cookie、User-Agent

## 法律合规

⚠️ **重要提示**：
- 遵守网站的 robots.txt 协议
- 尊重网站的服务条款
- 不要进行恶意爬取
- 避免对服务器造成过大压力
- 遵守相关法律法规
