# 复杂页面与反爬对抗指南

## 概览

本指南介绍如何使用 PaddleOCR 3.x 的能力（OCR、版面识别、表格识别、印章识别、VL 能力）来应对复杂页面和反爬虫场景。

## 适用场景

### 复杂页面场景

| 场景 | 特点 | 解决方案 |
|------|------|----------|
| **Canvas 渲染页面** | 内容在 Canvas 中绘制，无法直接提取 DOM | 截图 + OCR 提取 |
| **SVG 图片页面** | 内容以 SVG 形式呈现 | SVG 解析 + OCR 识别 |
| **动态加载内容** | 懒加载、滚动加载 | 滚动触发 + 智能等待 |
| **混淆的 DOM 结构** | DOM 结构复杂，难以定位元素 | 版面分析 + 结构化提取 |
| **图片形式的文本** | 文本以图片形式呈现 | 直接 OCR 识别 |
| **复杂表格布局** | 无线表格、合并单元格、嵌套表格 | PP-StructureV3 表格识别 |
| **验证码** | 图形验证码、滑块验证码 | 验证码识别服务 |

### 反爬虫场景

| 场景 | 特点 | 解决方案 |
|------|------|----------|
| **文本以图片形式呈现** | 绕过文本提取，强制人眼看 | OCR 识别 + 文本提取 |
| **混淆的 DOM 结构** | 故意混淆 DOM，增加提取难度 | 版面分析 + 智能定位 |
| **验证码** | 阻止自动化访问 | 验证码识别服务 |
| **动态内容** | 内容通过 JS 动态加载 | 滚动触发 + 等待加载 |
| **Canvas 反爬** | 内容在 Canvas 中渲染 | Canvas 截图 + OCR 提取 |
| **印章验证** | 文档需要印章验证 | 印章识别 + 真伪判断 |

## 核心工具

### 1. 验证码识别服务

**功能**：
- 图形验证码识别（数字、字母、混合）
- 验证码预处理（去噪、二值化、增强）
- 干扰线和干扰点处理
- 带重试的识别（多种参数组合）

**使用方式**：
```python
from scripts.captcha_recognition_service import CaptchaRecognitionService

# 初始化服务
service = CaptchaRecognitionService(use_gpu=True)

# 识别验证码
result = service.recognize_with_retry(
    "captcha.png",
    max_retries=3,
    pattern=r'^[A-Z0-9]{4}$'  # 4位字母数字
)

if result['success']:
    captcha_text = result['text']
    print(f"验证码: {captcha_text}")
```

**命令行使用**：
```bash
python scripts/captcha_recognition_service.py captcha.png --retry 3 --pattern "^[A-Z0-9]{4}$"
```

### 2. 复杂页面处理器

**功能**：
- Canvas 内容提取
- SVG 图片解析
- 复杂页面布局分析
- 智能降级（DOM 提取失败 → OCR 提取）
- 动态内容加载处理

**使用方式**：
```python
import asyncio
from scripts.complex_page_processor import ComplexPageProcessor
from scripts.playwright_cli import AsyncPlaywrightBrowser

async def process_complex_page():
    # 初始化浏览器
    browser = AsyncPlaywrightBrowser(headless=True)
    await browser.start()

    # 初始化处理器
    processor = ComplexPageProcessor(browser, use_gpu=True)

    # 智能提取（DOM 失败则降级到 OCR）
    result = await processor.smart_extraction(
        "https://example.com/complex-page",
        fallback_to_ocr=True
    )

    print(f"提取方法: {result['method']}")
    print(f"内容: {result['text']}")

    await browser.close()

asyncio.run(process_complex_page())
```

### 3. Canvas 内容提取

**场景**：页面内容在 Canvas 中渲染，无法通过 DOM 提取

**解决方案**：
```python
async def extract_canvas_content():
    processor = ComplexPageProcessor(browser, use_gpu=True)

    # 从 Canvas 提取内容
    result = await processor.extract_from_canvas(
        selector='#canvas-element',
        scroll_to_load=True
    )

    if result['success']:
        print(f"文本内容: {result['text']}")
        print(f"版面结构: {result['layout']}")
        print(f"表格数据: {result['tables']}")
```

### 4. 图片文本提取

**场景**：页面中的文本以图片形式呈现（反爬策略）

**解决方案**：
```python
async def extract_from_images():
    processor = ComplexPageProcessor(browser, use_gpu=True)

    # 从多个图片提取文本
    image_selectors = [
        '#text-image-1',
        '#text-image-2',
        '.content-image'
    ]

    results = await processor.extract_from_images(
        image_selectors,
        pattern=r'\d+\.\d+'  # 只提取数字
    )

    for result in results:
        print(f"图片: {result['selector']}")
        print(f"文本: {result['text']}")
```

### 5. 复杂页面布局分析

**场景**：DOM 结构混淆，难以定位元素

**解决方案**：
```python
async def analyze_complex_layout():
    processor = ComplexPageProcessor(browser, use_gpu=True)

    # 分析页面布局
    result = await processor.analyze_complex_layout(
        "https://example.com/obfuscated-page",
        full_page=True
    )

    if result['success']:
        # 提取各区域内容
        titles = result['text_regions']['title']
        paragraphs = result['text_regions']['text']
        tables = result['tables']

        print(f"标题: {titles}")
        print(f"段落: {paragraphs}")
        print(f"表格: {len(tables)} 个")
```

## 完整工作流示例

### 工作流 1：带验证码的网页抓取

```python
import asyncio
from scripts.playwright_cli import AsyncPlaywrightBrowser
from scripts.captcha_recognition_service import CaptchaRecognitionService

async def scrape_with_captcha(url, captcha_selector, submit_selector):
    """
    带验证码的网页抓取流程

    步骤：
    1. 访问页面
    2. 识别验证码
    3. 填写验证码
    4. 提交表单
    5. 提取结果
    """
    # 初始化
    browser = AsyncPlaywrightBrowser(headless=True)
    await browser.start()

    captcha_service = CaptchaRecognitionService(use_gpu=True)

    try:
        # 1. 访问页面
        await browser.goto(url, wait_until='networkidle')

        # 2. 截取验证码
        captcha_path = "temp_captcha.png"
        await browser.screenshot_element(captcha_selector, captcha_path)

        # 3. 识别验证码
        captcha_result = captcha_service.recognize_with_retry(
            captcha_path,
            max_retries=3,
            pattern=r'^[A-Z0-9]{4}$'
        )

        if not captcha_result['success']:
            raise Exception("验证码识别失败")

        captcha_text = captcha_result['text']
        print(f"识别到的验证码: {captcha_text}")

        # 4. 填写验证码
        await browser.fill(captcha_selector, captcha_text)

        # 5. 提交表单
        await browser.click(submit_selector)
        await browser.wait_for_load_state('networkidle')

        # 6. 提取结果
        result_text = await browser.page.evaluate('document.body.innerText')

        print(f"抓取结果: {result_text}")

        return {
            'success': True,
            'captcha': captcha_text,
            'content': result_text
        }

    finally:
        # 清理
        await browser.close()

# 使用
result = asyncio.run(scrape_with_captcha(
    "https://example.com/login",
    "#captcha-image",
    "#submit-button"
))
```

### 工作流 2：Canvas 页面内容提取

```python
import asyncio
from scripts.playwright_cli import AsyncPlaywrightBrowser
from scripts.complex_page_processor import ComplexPageProcessor

async def extract_canvas_page(url, canvas_selector):
    """
    Canvas 页面内容提取流程

    步骤：
    1. 访问页面
    2. 滚动加载完整内容
    3. 截图 Canvas
    4. OCR 提取文本
    5. 版面分析结构
    6. 提取表格数据
    """
    browser = AsyncPlaywrightBrowser(headless=True)
    await browser.start()

    processor = ComplexPageProcessor(browser, use_gpu=True)

    try:
        await browser.goto(url, wait_until='networkidle')

        # 提取 Canvas 内容
        result = await processor.extract_from_canvas(
            selector=canvas_selector,
            scroll_to_load=True
        )

        if result['success']:
            # 提取文本
            text = result['text']
            print(f"文本内容:\n{text}")

            # 提取版面结构
            layout = result['layout']
            print(f"版面结构: {len(layout)} 个区域")

            # 提取表格
            tables = result['tables']
            print(f"表格数据: {len(tables)} 个表格")

            return {
                'success': True,
                'text': text,
                'layout': layout,
                'tables': tables
            }
        else:
            raise Exception(f"提取失败: {result['error']}")

    finally:
        await browser.close()

# 使用
result = asyncio.run(extract_canvas_page(
    "https://example.com/canvas-page",
    "#content-canvas"
))
```

### 工作流 3：混淆 DOM 页面智能提取

```python
import asyncio
from scripts.playwright_cli import AsyncPlaywrightBrowser
from scripts.complex_page_processor import ComplexPageProcessor

async def smart_extract_obfuscated(url):
    """
    混淆 DOM 页面智能提取流程

    步骤：
    1. 尝试 DOM 提取
    2. 失败则降级到 OCR 提取
    3. 版面分析识别结构
    4. 提取各区域内容
    5. 整合结果
    """
    browser = AsyncPlaywrightBrowser(headless=True)
    await browser.start()

    processor = ComplexPageProcessor(browser, use_gpu=True)

    try:
        # 智能提取（自动降级）
        result = await processor.smart_extraction(
            url,
            fallback_to_ocr=True
        )

        if result['success']:
            method = result.get('method', 'unknown')
            print(f"提取方法: {method}")

            if method == 'dom':
                # DOM 提取成功
                print(f"DOM 文本: {result['text']}")
            else:
                # OCR 提取
                print(f"区域内容:")
                for region_type, texts in result['text_regions'].items():
                    if texts:
                        print(f"  {region_type}: {len(texts)} 个")

                print(f"表格: {len(result['tables'])} 个")

            return result
        else:
            raise Exception(f"提取失败: {result['error']}")

    finally:
        await browser.close()

# 使用
result = asyncio.run(smart_extract_obfuscated(
    "https://example.com/obfuscated-content"
))
```

## 性能优化建议

### 1. GPU 加速

```python
# 启用 GPU 加速
service = CaptchaRecognitionService(use_gpu=True)
processor = ComplexPageProcessor(browser, use_gpu=True)
```

### 2. 批量处理

```python
# 批量识别验证码
image_paths = ["captcha1.png", "captcha2.png", "captcha3.png"]
results = service.batch_recognize(image_paths, pattern=r'^[A-Z0-9]{4}$')
```

### 3. 结果缓存

```python
import pickle
from pathlib import Path

def get_or_cache_captcha(image_path: str, cache_dir: str = "cache"):
    """获取或缓存验证码识别结果"""
    cache_file = Path(cache_dir) / f"{Path(image_path).stem}.pkl"

    if cache_file.exists():
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    result = service.recognize_with_retry(image_path)
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(result, f)

    return result
```

### 4. 并行处理

```python
import asyncio

async def parallel_extract(urls: List[str]):
    """并行提取多个页面"""
    tasks = []
    for url in urls:
        task = processor.analyze_complex_layout(url)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results

# 使用
urls = ["url1.com", "url2.com", "url3.com"]
results = asyncio.run(parallel_extract(urls))
```

## 常见问题

### Q: 如何处理动态加载的内容？

A: 使用滚动触发和智能等待：
```python
await processor._scroll_to_load_content()
await browser.wait_for_load_state('networkidle')
```

### Q: 如何提高验证码识别率？

A:
1. 使用带重试的识别：`recognize_with_retry()`
2. 启用 GPU 加速
3. 调整正则表达式模式
4. 手动调整图像预处理参数

### Q: 如何处理混淆的 DOM 结构？

A: 使用版面分析：
```python
result = await processor.analyze_complex_layout(url)
regions = result['text_regions']
```

### Q: Canvas 内容提取失败怎么办？

A:
1. 确保滚动加载了完整内容
2. 尝试不同的截图尺寸
3. 检查图像质量
4. 启用 GPU 加速

## 相关资源

- [验证码识别服务](captcha_recognition_service.py)
- [复杂页面处理器](complex_page_processor.py)
- [Playwright CLI 指南](playwright-cli-guide.md)
- [反爬虫增强指南](anti-scraping-advanced.md)
- [PaddleOCR 3.x 能力](paddleocr-stamp-guide.md)
