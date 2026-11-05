# OCR 在反爬中的应用指南

## 概览
本文档说明如何使用 Web Automation Skill 中的 OCR 服务处理验证码和反爬场景。

## OCR 服务位置
- 脚本：`scripts/ocr_service.py`
- 指南：`references/ocr-guide.md`
- 集成：`scripts/crawler.py`

## 支持的验证码类型

### 1. 文本验证码
- ✅ 4-6 位字符
- ✅ 中文/英文/混合
- ✅ 简单干扰线

**使用方法**：
```python
from ocr_service import OCRService

# 初始化 OCR
ocr = OCRService(lang='ch')

# 识别验证码
result = ocr.recognize_image(captcha_img_path)
if result['success']:
    captcha_text = ''.join([line['text'] for line in result['text_lines']])
    print(f"验证码: {captcha_text}")
```

### 2. 滑块验证码
- ⚠️ 需要 Playwright 行为模拟
- ⚠️ OCR 识别滑块位置

**使用方法**：
```python
# 1. 使用 OCR 识别滑块目标位置
result = ocr.detect_elements(slider_img)
target_pos = result['elements'][0]['bbox']

# 2. 使用人类行为模拟拖动
from human_simulation import HumanSimulation
human = HumanSimulation()
await human.drag_slide(page, start_pos, target_pos)
```

### 3. 点选验证码
- ⚠️ OCR 识别文字
- ⚠️ 映射点击坐标

**使用方法**：
```python
# 1. OCR 识别点击顺序
result = ocr.recognize_image(captcha_img)
order = extract_click_order(result['text_lines'])

# 2. 点击对应位置
for idx, text in enumerate(order):
    pos = find_position_by_text(text)
    await page.click_at(pos)
```

## 完整流程示例

### 51CTO 验证码处理
```python
import asyncio
from playwright.async_api import async_playwright
from ocr_service import OCRService

async def handle_51cto_captcha():
    # 初始化 OCR
    ocr = OCRService(lang='ch')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # 访问网站
        await page.goto('https://blog.51cto.com/')

        # 检测验证码
        captcha = await page.query_selector('#captcha img')
        if captcha:
            # 截取验证码
            captcha_img = await captcha.screenshot(path='captcha.png')

            # OCR 识别
            result = ocr.recognize_image('captcha.png')
            if result['success']:
                captcha_text = ''.join([line['text'] for line in result['text_lines']])

                # 填写验证码
                await page.fill('#captcha-input', captcha_text)
                await page.click('#submit')

        await browser.close()
```

## 性能优化

### 1. 图像预处理
```python
from PIL import Image, ImageEnhance

def preprocess_image(img_path):
    img = Image.open(img_path)
    # 去噪
    img = img.filter(ImageFilter.MedianFilter())
    # 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    # 二值化
    img = img.convert('L').point(lambda x: 0 if x < 128 else 255, '1')
    return img
```

### 2. 多次重试
```python
def recognize_with_retry(ocr, img_path, max_retries=3):
    for i in range(max_retries):
        result = ocr.recognize_image(img_path)
        if result['success']:
            text = ''.join([line['text'] for line in result['text_lines']])
            if validate_captcha(text):  # 验证格式
                return text
    return None
```

## 注意事项

1. **环境依赖**：确保已安装 `paddleocr` 和 `paddlepaddle`
2. **初始化冲突**：避免在同一进程多次初始化 OCR
3. **识别率**：简单验证码识别率约 80-90%，复杂验证码需要人工干预
4. **合规性**：仅用于合法的数据采集，遵守网站 robots.txt 和服务条款

## 故障排除

### 问题：OCR 初始化失败
```
PDX has already been initialized. Reinitialization is not supported.
```
**解决方案**：使用单例模式管理 OCR 实例

### 问题：依赖缺失
```
ModuleNotFoundError: No module named 'langchain.docstore'
```
**解决方案**：`pip install langchain`

### 问题：识别率为 0
**检查**：
- 验证码图片是否清晰
- 图像格式是否支持（PNG/JPG）
- 语言设置是否正确（'ch' 或 'en'）

## 相关资源
- [OCR 使用指南](./ocr-guide.md)
- [人类行为模拟](../scripts/human_simulation.py)
- [爬虫脚本](../scripts/crawler.py)
