# 高级反爬策略

## 目录
- [概述](#概述)
- [浏览器指纹伪装](#浏览器指纹伪装)
- [人类行为模拟](#人类行为模拟)
- [User-Agent 管理](#user-agent-管理)
- [综合策略](#综合策略)

---

## 概述

本指南介绍高级反爬策略，用于绕过复杂的网站反爬机制。这些策略包括浏览器指纹伪装、人类行为模拟和智能 User-Agent 管理。

### 适用场景

- 需要访问带强反爬保护的网站（如新闻网站、电商网站）
- 需要长期稳定爬取数据
- 需要模拟真实用户行为

### 前置条件

- 了解 JavaScript 基础
- 了解 HTTP 协议
- 了解浏览器工作原理

---

## 浏览器指纹伪装

### 工作原理

浏览器指纹是网站用于识别用户的技术手段，包括：
- Canvas 指纹：通过 Canvas API 生成的图像特征
- WebGL 指标：通过 WebGL 获取的显卡信息
- AudioContext 指纹：通过 Audio API 生成的音频特征
- Navigator 对象：浏览器属性信息

### 调用规范

#### 调用方法
```bash
python scripts/browser_fingerprint.py --type=<type> --output=<path>
```

#### 触发条件
- 需要访问带指纹检测的网站
- 需要绕过浏览器指纹识别

#### 调用格式
```
--type: [str] 指纹类型，可选（canvas|webgl|audio|navigator|all），默认 all
--output: [str] 输出文件路径，默认 fingerprint.js
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--type` | str | 否 | all | 指纹类型：canvas（Canvas）、webgl（WebGL）、audio（音频）、navigator（导航器）、all（全部） |
| `--output` | str | 否 | fingerprint.js | 输出 JavaScript 文件路径 |

#### 结果说明

**成功**：生成指纹伪装 JavaScript 文件

#### 结果格式

```json
{
  "status": "success",
  "message": "指纹伪装脚本已生成",
  "output_path": "fingerprint.js",
  "type": "all"
}
```

#### 数据流

```
参数 → 指纹生成脚本 → JavaScript 文件 → 注入浏览器
```

#### 示例

```bash
# 生成所有指纹伪装脚本
python scripts/browser_fingerprint.py --type=all --output=./fingerprint.js

# 仅生成 Canvas 指纹伪装
python scripts/browser_fingerprint.py --type=canvas --output=./canvas.js
```

### 在 Playwright 中使用

```python
from playwright.async_api import async_playwright
import asyncio

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # 读取指纹伪装脚本
        with open('./fingerprint.js', 'r', encoding='utf-8') as f:
            fingerprint_script = f.read()

        # 注入指纹伪装脚本
        page = await context.new_page()
        await page.add_init_script(fingerprint_script)

        # 访问网站
        await page.goto('https://example.com')

        await browser.close()

asyncio.run(main())
```

---

## 人类行为模拟

### 工作原理

人类行为模拟包括：
- **鼠标移动**：使用贝塞尔曲线模拟平滑移动
- **滚动**：分段滚动，模拟人类阅读
- **打字**：逐字输入，模拟真实打字速度
- **延迟**：随机延迟，模拟人类反应时间

### 调用规范

#### 调用方法
```bash
python scripts/human_simulation.py --action=<action> [参数...]
```

#### 触发条件
- 需要模拟真实用户行为
- 需要绕过行为检测

#### 调用格式

**鼠标移动**：
```
--action=move --start=x,y --end=x,y --output=<path>
```

**滚动**：
```
--action=scroll --distance=<pixels> --output=<path>
```

**打字**：
```
--action=type --text=<text> --selector=<selector> --output=<path>
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--action` | str | 是 | - | 动作类型：move（移动）、scroll（滚动）、type（打字） |
| `--start` | str | move 必需 | - | 起始点坐标，格式：x,y |
| `--end` | str | move 必需 | - | 终点坐标，格式：x,y |
| `--distance` | int | 否 | 300 | 滚动距离（像素） |
| `--text` | str | type 必需 | - | 要输入的文本 |
| `--selector` | str | 否 | - | 元素选择器 |
| `--output` | str | 否 | behavior.js | 输出文件路径 |

#### 结果说明

**成功**：生成行为模拟 JavaScript 文件

#### 结果格式

```json
{
  "status": "success",
  "message": "行为模拟脚本已生成",
  "output_path": "behavior.js",
  "action": "move"
}
```

#### 示例

```bash
# 生成鼠标移动脚本
python scripts/human_simulation.py \
  --action=move \
  --start=100,100 \
  --end=500,500 \
  --output=./mouse-move.js

# 生成滚动脚本
python scripts/human_simulation.py \
  --action=scroll \
  --distance=500 \
  --output=./scroll.js

# 生成打字脚本
python scripts/human_simulation.py \
  --action=type \
  --text="Hello World" \
  --selector="#input" \
  --output=./type.js
```

### 在 Playwright 中使用

```python
from playwright.async_api import async_playwright
import asyncio

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto('https://example.com')

        # 读取并执行行为模拟脚本
        with open('./mouse-move.js', 'r', encoding='utf-8') as f:
            move_script = f.read()
        await page.evaluate(move_script)

        await browser.close()

asyncio.run(main())
```

---

## User-Agent 管理

### 工作原理

User-Agent 管理包括：
- **多平台支持**：Windows、macOS、Linux、Mobile
- **随机选择**：从池中随机选择 User-Agent
- **轮换机制**：避免重复使用同一 UA

### 调用规范

#### 调用方法
```bash
python scripts/user_agent_manager.py --action=<action> [参数...]
```

#### 触发条件
- 需要随机化 User-Agent
- 需要轮换 User-Agent

#### 调用格式

**获取随机 UA**：
```
--action=get --platform=<platform>
```

**列出所有 UA**：
```
--action=list --platform=<platform>
```

**添加自定义 UA**：
```
--action=add --platform=<platform> --user-agent=<ua>
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--action` | str | 是 | - | 操作类型：get（获取）、list（列出）、add（添加）、config（配置） |
| `--platform` | str | 否 | windows | 平台类型：windows、macos、linux、mobile |
| `--user-agent` | str | add 必需 | - | User-Agent 字符串 |

#### 结果说明

**成功**：返回 User-Agent 或配置信息

#### 结果格式

```json
{
  "status": "success",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
}
```

#### 示例

```bash
# 获取随机 User-Agent
python scripts/user_agent_manager.py --action=get --platform=windows

# 列出所有 Windows User-Agent
python scripts/user_agent_manager.py --action=list --platform=windows

# 添加自定义 User-Agent
python scripts/user_agent_manager.py \
  --action=add \
  --platform=windows \
  --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."

# 查看配置
python scripts/user_agent_manager.py --action=config
```

### 在 Playwright 中使用

```python
from scripts.user_agent_manager import UserAgentManager
from playwright.async_api import async_playwright
import asyncio

async def main():
    # 创建 User-Agent 管理器
    ua_manager = UserAgentManager()

    # 获取随机 User-Agent
    user_agent = ua_manager.get_random_user_agent(platform="windows")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=user_agent
        )
        page = await context.new_page()

        await page.goto('https://example.com')

        await browser.close()

asyncio.run(main())
```

---

## 综合策略

### 完整的反爬防护方案

```python
from scripts.user_agent_manager import UserAgentManager
from scripts.browser_fingerprint import BrowserFingerprint
from scripts.human_simulation import HumanSimulation
from playwright.async_api import async_playwright
import asyncio
import random

async def browse_with_anti_scraping(url: str):
    """带反爬防护的浏览"""

    # 初始化工具
    ua_manager = UserAgentManager()
    fingerprint = BrowserFingerprint()
    simulation = HumanSimulation()

    # 获取随机 User-Agent
    user_agent = ua_manager.get_random_user_agent(platform="windows")

    # 生成指纹伪装脚本
    fingerprint_script = fingerprint.get_all_injection_scripts()

    # 生成行为模拟脚本
    behavior_script = simulation.get_scroll_script(scroll_distance=500, steps=5)

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )

        # 创建上下文
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
        )

        # 隐藏自动化特征
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
        """)

        page = await context.new_page()

        # 注入指纹伪装脚本
        await page.add_init_script(fingerprint_script)

        # 访问网站
        await page.goto(url, wait_until='networkidle')

        # 执行人类行为模拟
        await page.evaluate(behavior_script)

        # 随机延迟
        await asyncio.sleep(random.uniform(1, 3))

        # 继续操作...

        await browser.close()

# 使用示例
asyncio.run(browse_with_anti_scraping('https://news.163.com'))
```

### 策略组合

| 网站类型 | 推荐策略 | 成功率 |
|---------|---------|--------|
| 一般网站 | User-Agent 随机化 | 90%+ |
| 新闻网站 | User-Agent + 指纹伪装 + 行为模拟 | 70-80% |
| 电商网站 | 完整策略 + 代理 | 50-70% |
| 金融网站 | 完整策略 + 代理 + 验证码处理 | 30-50% |

### 注意事项

1. **延迟控制**：避免频繁请求，添加随机延迟
2. **IP 轮换**：配合代理服务器使用
3. **Cookie 管理**：维护 Cookie 状态
4. **异常处理**：遇到 403 时切换策略
5. **频率限制**：控制请求频率，避免触发风控

---

## 故障排查

### 问题 1：仍然返回 403

**可能原因**：
- IP 被封禁
- 需要登录
- 需要验证码

**解决方案**：
- 使用代理服务器
- 添加登录流程
- 集成 OCR 识别验证码

### 问题 2：指纹伪装不生效

**可能原因**：
- 脚本注入时机不对
- 指纹特征被覆盖

**解决方案**：
- 使用 `add_init_script` 在页面加载前注入
- 检查脚本执行顺序

### 问题 3：行为模拟被检测

**可能原因**：
- 行为过于规律
- 延迟时间不自然

**解决方案**：
- 增加随机性
- 模拟更复杂的行为模式
