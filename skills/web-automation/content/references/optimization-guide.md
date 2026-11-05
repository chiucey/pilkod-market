# Web Automation Skill 优化指南

## 目录
- [概览](#概览)
- [超时策略优化](#超时策略优化)
- [重试机制集成](#重试机制集成)
- [反爬增强](#反爬增强)
- [证书处理](#证书处理)
- [PDF处理优化](#pdf处理优化)
- [最佳实践](#最佳实践)

## 概览

本文档介绍 Web Automation Skill 的四个核心优化：

1. **超时策略调整**：增加超时时间，支持可配置超时策略
2. **重试机制集成**：自动重试失败操作，提高成功率
3. **反爬增强**：代理IP、随机UA、浏览器指纹伪装
4. **证书处理**：支持忽略证书错误，处理自签名证书
5. **PDF处理优化**：URL直接下载、进度显示、断点续传

所有优化已集成到增强版脚本中，可以直接使用。

## 超时策略优化

### 问题
- 默认超时时间（30秒）可能不足以加载复杂页面
- 不同操作类型需要不同的超时时间
- 网络波动导致频繁超时

### 解决方案

#### 1. 预设超时策略

```python
from scripts.enhanced_playwright_cli import TimeoutConfig

# 获取预设超时时间
timeout = TimeoutConfig.get_timeout("normal")  # 60000ms
timeout = TimeoutConfig.get_timeout("slow")    # 120000ms
timeout = TimeoutConfig.get_timeout("download")  # 600000ms
```

**预设类型**：
- `fast`: 30秒 - 快速操作（如点击、输入）
- `normal`: 60秒 - 正常操作（默认）
- `slow`: 120秒 - 慢速操作（如复杂页面加载）
- `very_slow`: 300秒 - 超慢操作（如大数据加载）
- `download`: 600秒 - 下载操作

#### 2. 使用增强版浏览器

```python
import asyncio
from scripts.enhanced_playwright_cli import EnhancedAsyncPlaywrightBrowser

async def main():
    browser = EnhancedAsyncPlaywrightBrowser(
        headless=True,
        timeout_strategy="slow",  # 使用慢速策略
        timeout=120000,  # 或自定义超时时间
    )
    
    await browser.start()
    await browser.goto("https://example.com")
    await browser.close()

asyncio.run(main())
```

#### 3. 命令行使用

```bash
# 使用预设策略
python scripts/enhanced_playwright_cli.py "https://example.com" \
  --timeout-strategy slow

# 自定义超时时间
python scripts/enhanced_playwright_cli.py "https://example.com" \
  --timeout 120000
```

## 重试机制集成

### 问题
- 网络波动导致操作失败
- 服务器临时不可用
- 需要手动重试

### 解决方案

#### 1. 自动重试

增强版浏览器已内置重试机制，会自动重试失败操作：

```python
import asyncio
from scripts.enhanced_playwright_cli import EnhancedAsyncPlaywrightBrowser

async def main():
    browser = EnhancedAsyncPlaywrightBrowser(
        max_retries=5,  # 最大重试5次
        retry_base_delay=2.0,  # 基础延迟2秒
    )
    
    await browser.start()
    
    # 导航操作会自动重试
    await browser.goto("https://example.com")
    
    # 点击操作也会自动重试
    await browser.click("#submit-btn")
    
    await browser.close()

asyncio.run(main())
```

#### 2. 操作类型重试配置

不同操作类型有不同的重试策略：

| 操作类型 | 最大重试次数 | 基础延迟 |
|---------|------------|---------|
| navigation | 3 | 2.0秒 |
| click | 2 | 0.5秒 |
| fill | 2 | 0.5秒 |
| screenshot | 2 | 0.5秒 |
| download | 5 | 5.0秒 |

#### 3. 指数退避策略

重试延迟采用指数退避：
- 第1次重试：等待 `base_delay` 秒
- 第2次重试：等待 `base_delay * 2` 秒
- 第3次重试：等待 `base_delay * 4` 秒
- 以此类推...

#### 4. 查看重试统计

```python
# 获取统计信息
stats = browser.get_stats()
print(f"总操作数: {stats['total_operations']}")
print(f"成功操作: {stats['success_operations']}")
print(f"重试成功: {stats['retried_operations']}")
print(f"失败操作: {stats['failed_operations']}")
```

## 反爬增强

### 问题
- IP 被封禁
- User-Agent 被识别
- 浏览器指纹被检测

### 解决方案

#### 1. 代理IP支持

```python
import asyncio
from scripts.enhanced_playwright_cli import EnhancedAsyncPlaywrightBrowser

async def main():
    # 配置代理
    proxy = {
        "server": "http://proxy.example.com:8080",
        "username": "user",  # 可选
        "password": "pass",  # 可选
    }
    
    browser = EnhancedAsyncPlaywrightBrowser(
        proxy=proxy,
    )
    
    await browser.start()
    await browser.goto("https://example.com")
    await browser.close()

asyncio.run(main())
```

**命令行使用**：
```bash
python scripts/enhanced_playwright_cli.py "https://example.com" \
  --proxy "http://proxy.example.com:8080"
```

#### 2. 随机User-Agent

```python
import asyncio
from scripts.enhanced_playwright_cli import EnhancedAsyncPlaywrightBrowser

async def main():
    browser = EnhancedAsyncPlaywrightBrowser(
        random_ua=True,  # 启用随机UA（默认启用）
    )
    
    await browser.start()
    # 每次启动都会使用不同的UA
    await browser.goto("https://example.com")
    await browser.close()

asyncio.run(main())
```

**命令行使用**：
```bash
python scripts/enhanced_playwright_cli.py "https://example.com" \
  --random-ua  # 默认启用
```

#### 3. 随机视口和时区

增强版浏览器会自动随机化：
- 视口大小
- 时区
- 语言

#### 4. 使用代理池管理器

```python
from scripts.proxy_manager import ProxyManager

# 初始化代理池
proxy_manager = ProxyManager()

# 添加代理
proxy_manager.add_proxy("http://proxy1.example.com:8080")
proxy_manager.add_proxy("http://proxy2.example.com:8080")

# 获取随机代理
proxy = proxy_manager.get_random_proxy()
print(proxy)
```

#### 5. 使用 User-Agent 管理器

```python
from scripts.user_agent_manager import UserAgentManager

# 初始化 UA 管理器
ua_manager = UserAgentManager()

# 获取随机 UA
ua = ua_manager.get_random_user_agent()
print(ua)

# 获取特定平台的 UA
ua = ua_manager.get_user_agent(platform="windows", browser="chrome")
```

## 证书处理

### 问题
- 自签名证书导致访问失败
- 内网 HTTPS 站点证书不受信任
- 测试环境证书问题

### 解决方案

#### 1. 忽略证书错误

```python
import asyncio
from scripts.enhanced_playwright_cli import EnhancedAsyncPlaywrightBrowser

async def main():
    browser = EnhancedAsyncPlaywrightBrowser(
        ignore_https_errors=True,  # 忽略证书错误
    )
    
    await browser.start()
    
    # 可以访问自签名证书的站点
    await browser.goto("https://self-signed.example.com")
    
    await browser.close()

asyncio.run(main())
```

**命令行使用**：
```bash
python scripts/enhanced_playwright_cli.py "https://self-signed.example.com" \
  --ignore-https-errors
```

#### 2. 注意事项

⚠️ **安全警告**：
- 仅在测试环境或可信网络中使用
- 生产环境应使用有效证书
- 忽略证书错误可能导致中间人攻击

## PDF处理优化

### 问题
- 需要先手动下载 PDF 再解析
- 大文件下载慢，无进度显示
- 下载失败需要重新开始

### 解决方案

#### 1. 从 URL 直接下载 PDF

```python
import asyncio
from scripts.enhanced_mineru_service import EnhancedMinerUService

async def main():
    service = EnhancedMinerUService()
    
    # 从 URL 下载 PDF
    result = await service.download_pdf_from_url(
        url="https://example.com/document.pdf",
        output_path="./downloads/document.pdf",
        timeout=600,  # 10分钟超时
        max_retries=3,
    )
    
    if result["success"]:
        print(f"下载成功: {result['path']}")
        print(f"文件大小: {result['size'] / (1024*1024):.2f} MB")
        print(f"耗时: {result['elapsed_time']:.1f}秒")
    else:
        print(f"下载失败: {result['error']}")

asyncio.run(main())
```

#### 2. 下载并解析 PDF

```python
import asyncio
from scripts.enhanced_mineru_service import EnhancedMinerUService

async def main():
    service = EnhancedMinerUService()
    
    # 一步完成：下载 + 解析
    result = await service.download_and_parse_pdf(
        url="https://example.com/document.pdf",
        output_format="markdown",
        timeout=600,
    )
    
    if result["success"]:
        print(f"解析成功，输出目录: {result['output_dir']}")
        # 处理解析结果
        data = result["data"]
    else:
        print(f"处理失败: {result['error']}")

asyncio.run(main())
```

#### 3. 进度显示

下载过程会实时显示进度：

```
📥 开始下载: https://example.com/document.pdf
   文件大小: 25.50 MB
   进度: 45.2% | 速度: 2.35 MB/s | 剩余: 6s
✅ 下载完成: ./downloads/document.pdf
   耗时: 10.8秒
```

#### 4. 断点续传

如果下载中断，下次会自动从断点继续：

```
📦 检测到未完成的下载，从 15728640 字节处继续
📥 开始下载: https://example.com/document.pdf
   ...
```

#### 5. 批量处理

```python
import asyncio
from scripts.enhanced_mineru_service import EnhancedMinerUService

async def main():
    service = EnhancedMinerUService()
    
    urls = [
        "https://example.com/doc1.pdf",
        "https://example.com/doc2.pdf",
        "https://example.com/doc3.pdf",
    ]
    
    result = await service.batch_download_and_parse(
        urls=urls,
        output_format="markdown",
        max_concurrent=3,  # 同时处理3个
    )
    
    print(f"总数: {result['total']}")
    print(f"成功: {result['success_count']}")
    print(f"失败: {result['failed_count']}")

asyncio.run(main())
```

#### 6. 命令行使用

```bash
# 下载 PDF
python scripts/enhanced_mineru_service.py download-pdf \
  --url "https://example.com/document.pdf" \
  --output "./downloads/document.pdf"

# 下载并解析
python scripts/enhanced_mineru_service.py download-and-parse \
  --url "https://example.com/document.pdf" \
  --output-format markdown

# 批量处理
python scripts/enhanced_mineru_service.py batch-process \
  --urls "https://example.com/doc1.pdf" "https://example.com/doc2.pdf" \
  --max-concurrent 3
```

## 最佳实践

### 1. 根据场景选择超时策略

```python
# 快速测试
browser = EnhancedAsyncPlaywrightBrowser(timeout_strategy="fast")

# 常规使用
browser = EnhancedAsyncPlaywrightBrowser(timeout_strategy="normal")

# 复杂页面
browser = EnhancedAsyncPlaywrightBrowser(timeout_strategy="slow")

# 大文件下载
browser = EnhancedAsyncPlaywrightBrowser(timeout_strategy="download")
```

### 2. 合理配置重试

```python
# 高可靠场景（多次重试）
browser = EnhancedAsyncPlaywrightBrowser(
    max_retries=5,
    retry_base_delay=2.0,
)

# 快速场景（少重试）
browser = EnhancedAsyncPlaywrightBrowser(
    max_retries=2,
    retry_base_delay=0.5,
)
```

### 3. 反爬策略组合

```python
browser = EnhancedAsyncPlaywrightBrowser(
    # 使用代理
    proxy={"server": "http://proxy.example.com:8080"},
    
    # 随机UA和视口
    random_ua=True,
    random_viewport=True,
    
    # 适当的超时和重试
    timeout_strategy="normal",
    max_retries=3,
)
```

### 4. 完整示例

```python
import asyncio
from scripts.enhanced_playwright_cli import EnhancedAsyncPlaywrightBrowser
from scripts.enhanced_mineru_service import EnhancedMinerUService

async def main():
    # 1. 创建增强版浏览器
    browser = EnhancedAsyncPlaywrightBrowser(
        headless=True,
        timeout_strategy="slow",
        max_retries=3,
        proxy={"server": "http://proxy.example.com:8080"},
        random_ua=True,
        ignore_https_errors=False,
    )
    
    try:
        # 2. 启动浏览器
        await browser.start()
        
        # 3. 导航到目标页面
        await browser.goto("https://example.com/login")
        
        # 4. 执行操作（自动重试）
        await browser.fill("#username", "user@example.com")
        await browser.fill("#password", "password123")
        await browser.click("#login-btn")
        
        # 5. 等待页面加载
        await browser.wait_for_load_state("networkidle")
        
        # 6. 截图
        await browser.screenshot("screenshot.png")
        
        # 7. 下载 PDF
        mineru = EnhancedMinerUService()
        result = await mineru.download_and_parse_pdf(
            url="https://example.com/report.pdf",
            output_format="markdown",
        )
        
        if result["success"]:
            print(f"PDF 解析成功: {result['output_dir']}")
        
    finally:
        # 8. 关闭浏览器并查看统计
        stats = browser.get_stats()
        print(f"\n操作统计: {stats}")
        await browser.close()

asyncio.run(main())
```

### 5. 错误处理

```python
import asyncio
from scripts.enhanced_playwright_cli import EnhancedAsyncPlaywrightBrowser

async def main():
    browser = EnhancedAsyncPlaywrightBrowser()
    
    try:
        await browser.start()
        await browser.goto("https://example.com")
        
    except Exception as e:
        print(f"操作失败: {e}")
        
        # 查看统计信息，了解失败原因
        stats = browser.get_stats()
        print(f"统计信息: {stats}")
        
    finally:
        await browser.close()

asyncio.run(main())
```

## 注意事项

### 超时设置
- 超时时间不宜过长，避免资源浪费
- 根据实际网络情况调整
- 下载大文件时使用 `download` 策略

### 重试机制
- 重试次数过多会增加总耗时
- 对于业务逻辑错误（如登录失败），不应重试
- 查看统计信息判断是否需要调整配置

### 反爬策略
- 遵守目标网站的 robots.txt
- 不要过于频繁访问
- 使用代理时确保代理可用

### 证书处理
- 仅在可信环境使用忽略证书错误
- 生产环境应使用有效证书
- 定期检查证书有效性

### PDF 处理
- 大文件解析需要较多内存
- 批量处理时控制并发数
- 及时清理临时文件

## 参考资源

- [Playwright 官方文档](https://playwright.dev/python/)
- [MinerU 官方文档](https://github.com/opendatalab/MinerU)
- [反爬虫策略指南](anti-scraping-advanced.md)
- [浏览器管理规范](browser-management.md)
