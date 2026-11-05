# PaddleOCR-VL 使用指南

## 目录
- [概览](#概览)
- [功能边界](#功能边界)
- [API 参考](#api-参考)
- [性能限制](#性能限制)
- [使用示例](#使用示例)
- [最佳实践](#最佳实践)

## 概览
PaddleOCR-VL 是百度开源的 OCR 引擎，支持中英文识别、表格提取、版面分析等功能。

**核心能力**：
- 通用文字识别（中英文混合）
- 表格识别与提取
- 版面分析与结构化
- 多语言支持（80+ 语言）

**适用场景**：
- 网页截图识别
- 验证码识别
- 表格数据提取
- 文档数字化

## 功能边界

### 支持的图像格式
- ✅ PNG、JPG、JPEG、BMP
- ✅ 单张图像最大分辨率：4096x4096
- ✅ 支持灰度和彩色图像
- ❌ 不支持 PDF 直接识别（需先转换为图像）

### 识别语言
- ✅ 中文（简体/繁体）
- ✅ 英文
- ✅ 中英文混合
- ✅ 其他 80+ 语言（需下载对应模型）

### 识别精度
| 场景 | 准确率 |
|------|--------|
| 清晰文字 | 95%+ |
| 模糊文字 | 70-85% |
| 手写文字 | 60-80% |
| 验证码 | 40-70% |

### 功能限制
- ❌ 不支持实时视频流识别
- ❌ 不支持三维文本识别
- ❌ 复杂背景下的文字识别精度下降
- ❌ 手写文字识别需要特定模型

## API 参考

### 初始化服务
```python
from paddleocr import PaddleOCR

# 初始化
ocr = PaddleOCR(
    use_angle_cls=True,   # 使用方向分类器
    lang="ch",            # 语言类型
    use_gpu=False,        # 是否使用 GPU
    show_log=False        # 是否显示日志
)
```

### 1. 通用文字识别
```python
# 识别单张图像
result = ocr.ocr("image.png")

# 结果格式
[
    [
        [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],  # 文本框坐标
        ("识别的文字", 0.95)  # 文字内容和置信度
    ],
    ...
]
```

### 2. 区域识别
```python
from PIL import Image

img = Image.open("image.png")
cropped = img.crop((x1, y1, x2, y2))  # 裁剪区域
cropped.save("region.png")

result = ocr.ocr("region.png")
```

### 3. 批量识别
```python
images = ["img1.png", "img2.png", "img3.png"]

results = []
for img_path in images:
    result = ocr.ocr(img_path)
    results.append(result)
```

### 4. 表格识别
```python
# 基础表格识别（仅文字提取）
result = ocr.ocr("table.png")

# 完整表格结构识别（需要 PaddleStructure）
from paddleocr import PPStructure

structure = PPStructure(show_log=False)
result = structure("table.png")
```

## 性能限制

### 处理速度
| 配置 | 速度（张/秒） |
|------|--------------|
| CPU | 0.5-2 |
| GPU | 5-20 |

### 内存占用
| 配置 | 内存占用 |
|------|----------|
| CPU | 500MB - 1GB |
| GPU | 1GB - 2GB |

### 并发限制
- CPU 模式：建议并发不超过 4
- GPU 模式：建议并发不超过 8

## 使用示例

### 示例 1：网页截图识别
```python
from ocr_service import OCRService

# 初始化服务
service = OCRService(lang="ch")

# 识别网页截图
result = service.recognize_image("screenshot.png")

if result["success"]:
    print(f"识别到 {result['line_count']} 行文字")
    print(f"平均置信度: {result['avg_confidence']:.2f}")
    print(f"完整文本:\n{result['full_text']}")
```

### 示例 2：验证码识别
```python
result = service.recognize_region(
    "page.png",
    region=(100, 100, 200, 150)  # 验证码区域
)

if result["success"]:
    captcha_code = result["full_text"].strip()
    print(f"验证码: {captcha_code}")
```

### 示例 3：表格数据提取
```python
result = service.extract_table("table.png")

if result["success"]:
    for i, text in enumerate(result["text_lines"]):
        print(f"行 {i+1}: {text}")
```

### 示例 4：元素检测
```python
result = service.detect_elements(
    "page.png",
    element_type="button"  # 仅检测按钮
)

if result["success"]:
    for elem in result["elements"]:
        print(f"按钮: {elem['text']} (置信度: {elem['confidence']:.2f})")
```

## 最佳实践

### 1. 图像预处理
```python
from PIL import Image, ImageEnhance

img = Image.open("image.png")

# 调整对比度
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.0)

# 调整亮度
enhancer = ImageEnhance.Brightness(img)
img = enhancer.enhance(1.2)

# 保存预处理后的图像
img.save("processed.png")
```

### 2. 识别结果过滤
```python
result = service.recognize_image("image.png")

# 过滤低置信度结果
filtered_lines = [
    text for text, conf in zip(result["text_list"], result["confidence_list"])
    if conf > 0.8
]
```

### 3. 批量处理优化
```python
import asyncio

async def batch_recognize(images):
    service = OCRService()
    tasks = []
    
    for img_path in images:
        # 使用线程池并发处理
        task = asyncio.to_thread(service.recognize_image, img_path)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### 4. 结果缓存
```python
import hashlib
import json

def get_image_hash(image_path):
    with open(image_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# 检查缓存
cache_key = get_image_hash("image.png")
cache_file = f".cache/{cache_key}.json"

if Path(cache_file).exists():
    with open(cache_file) as f:
        result = json.load(f)
else:
    result = service.recognize_image("image.png")
    with open(cache_file, "w") as f:
        json.dump(result, f)
```

## 注意事项

### 1. 模型下载
首次运行时，PaddleOCR 会自动下载模型文件（约 200MB）：
- 检测模型：~100MB
- 识别模型：~80MB
- 方向分类器：~10MB

### 2. GPU 加速
使用 GPU 需要：
```bash
pip install paddlepaddle-gpu
```

### 3. 网络依赖
首次运行需要联网下载模型，建议提前下载并缓存。

### 4. 编码问题
中文识别结果建议使用 UTF-8 编码：
```python
result = ocr.ocr("image.png", cls=True)
text = result[0][0][1][0]  # UTF-8 编码的中文
```

## 性能优化建议

1. **图像压缩**: 将大图像压缩到合适尺寸（建议 1024x1024 以下）
2. **批量处理**: 使用多线程或异步处理批量图像
3. **结果缓存**: 对重复识别的图像进行缓存
4. **区域识别**: 仅识别需要的区域，减少计算量
5. **GPU 加速**: 批量处理时使用 GPU 显著提升速度
