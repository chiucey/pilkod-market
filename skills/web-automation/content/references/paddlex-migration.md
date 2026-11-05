# PaddleX 迁移说明

## 概述

本 Skill 已将所有 OCR 相关功能统一迁移到 **PaddleX 框架**，以获得更好的性能、统一的 API 和更强的能力。

---

## 迁移内容

### 迁移前（使用 PaddleOCR）

```
依赖：
- PaddleOCR >= 3.0.0
- PaddlePaddle >= 3.0.0

脚本：
- scripts/ocr_service.py (基于 PaddleOCR 3.x API)
- scripts/page_parser.py (基于 PaddleX)
```

### 迁移后（统一使用 PaddleX）

```
依赖：
- PaddleX >= 3.4.0

脚本：
- scripts/ocr_service.py (基于 PaddleX API)
- scripts/page_parser.py (基于 PaddleX API)
```

---

## PaddleX 的优势

### 1. 统一的 API

**之前**：多个框架，不同的 API
```python
# PaddleOCR
ocr = PaddleOCR(lang='ch')
result = ocr.ocr(image_path)

# PaddleX
pipeline = pdx.create_pipeline('OCR')
result = pipeline.predict(image_path)
```

**现在**：统一使用 PaddleX
```python
from paddlex import pipelines

pipeline = pipelines.create_pipeline('OCR')
result = pipeline.predict(image_path)
```

### 2. 更强的能力

| 功能 | PaddleOCR | PaddleX |
|------|-----------|---------|
| **文字识别** | ✅ | ✅ |
| **表格识别** | ✅ | ✅ (更强) |
| **元素检测** | ⚠️ 基础 | ✅ 完善 |
| **版面分析** | ❌ | ✅ 支持 |
| **文档理解** | ⚠️ 有限 | ✅ 强大 |
| **目标检测** | ❌ | ✅ 支持 |
| **图像分割** | ❌ | ✅ 支持 |

### 3. 简化依赖

**之前**：
```
pip install paddleocr>=3.0.0 paddlepaddle>=3.0.0
```

**现在**：
```
pip install paddlex>=3.4.0
```

PaddleX 自动管理所有底层依赖。

### 4. 更好的性能

- ✅ 流水线优化
- ✅ GPU 加速支持
- ✅ 混合精度推理
- ✅ 批处理优化

---

## API 变化

### OCR 服务

#### 初始化

**之前（PaddleOCR）**：
```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang='ch',
    use_angle_cls=True,
    use_gpu=False,
    show_log=False
)
```

**现在（PaddleX）**：
```python
from paddlex import pipelines

ocr = pipelines.create_pipeline(
    pipeline='OCR',
    device='cpu'
)
```

#### 调用

**之前**：
```python
result = ocr.ocr(image_path, cls=True)
texts = [[{'bbox': [...], 'text': '...', 'confidence': 0.99}], ...]
```

**现在**：
```python
result = ocr.predict(image_path)
# PaddleX 统一的返回格式
```

**兼容封装**：
```python
from ocr_service import OCRService

# 使用兼容的 API（内部使用 PaddleX）
ocr = OCRService(device='cpu')
result = ocr.recognize_image(image_path)

# 返回格式保持不变
if result['success']:
    print(result['full_text'])
    for line in result['text_lines']:
        print(f"{line['text']} ({line['confidence']})")
```

### 页面解析

**之前**：
```python
# 需要单独的版面分析工具
```

**现在**：
```python
from page_parser import PageParser

parser = PageParser(device='cpu')

# 版面分析
layout = parser.parse_page_layout(image_path)

# 元素检测
elements = parser.detect_interactive_elements(image_path)

# 结构化提取
data = parser.extract_structured_data(image_path)

# 操作计划
plan = parser.generate_operation_plan(image_path)
```

---

## 使用示例

### 1. 文字识别

```python
from ocr_service import OCRService

# 初始化
ocr = OCRService(device='cpu')

# 识别图像
result = ocr.recognize_image('captcha.png')

if result['success']:
    print(f"识别结果: {result['full_text']}")

    # 验证码识别
    captcha_text = result['text_lines'][0]['text']
    await page.fill('#captcha-input', captcha_text)
```

### 2. 页面解析

```python
from page_parser import PageParser

# 初始化
parser = PageParser(device='cpu')

# 解析页面布局
layout = parser.parse_page_layout('page.png')
for region in layout['regions']:
    print(f"[{region['type']}] {region['bbox']}")

# 检测交互元素
elements = parser.detect_interactive_elements('page.png')
for elem in elements['elements']:
    print(f"[{elem['type']}] {elem['text']}")

# 生成操作计划
plan = parser.generate_operation_plan('page.png')
for step in plan:
    print(f"{step['action']}: {step['text']}")
```

### 3. 表格提取

```python
from ocr_service import OCRService

ocr = OCRService(device='cpu')
result = ocr.extract_table('table.png')

if result['success']:
    for row in result['table_data']:
        print(' | '.join(row))
```

---

## 性能优化

### 1. 使用 GPU

```python
# CPU 模式
ocr = OCRService(device='cpu')

# GPU 模式
ocr = OCRService(device='gpu')
```

### 2. 批处理

```python
images = ['img1.png', 'img2.png', 'img3.png']
ocr = OCRService(device='cpu')

for img_path in images:
    result = ocr.recognize_image(img_path)
    # 处理结果
```

### 3. 流水线复用

```python
# 复用流水线，避免重复初始化
class OCRSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = OCRService(device='cpu')
        return cls._instance

ocr = OCRSingleton.get_instance()
```

---

## 兼容性说明

### 向后兼容

所有现有代码保持兼容，无需修改：

```python
from ocr_service import OCRService

# API 保持不变
ocr = OCRService(lang='ch')  # lang 参数保留
result = ocr.recognize_image(image_path)
```

### 迁移指南

如果您在迁移前有自定义代码，请参考以下步骤：

1. **检查导入**
   ```python
   # 之前
   from paddleocr import PaddleOCR

   # 现在
   from paddlex import pipelines
   # 或
   from ocr_service import OCRService  # 推荐
   ```

2. **更新初始化**
   ```python
   # 之前
   ocr = PaddleOCR(lang='ch', use_gpu=False)

   # 现在
   ocr = OCRService(device='cpu')
   ```

3. **检查返回格式**
   ```python
   # 返回格式保持兼容
   result = ocr.recognize_image(image_path)
   text = result['text_lines'][0]['text']
   ```

---

## 故障排除

### 问题 1：PaddleX 导入失败

**错误**：
```
ModuleNotFoundError: No module named 'paddlex'
```

**解决**：
```bash
pip install paddlex>=3.4.0
```

### 问题 2：模型下载失败

**错误**：
```
Connectivity check to the model hoster
```

**解决**：
```bash
export PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True
```

### 问题 3：GPU 不可用

**错误**：
```
GPU not available
```

**解决**：
```python
# 使用 CPU
ocr = OCRService(device='cpu')
```

---

## 版本信息

- **PaddleX**: 3.4.2
- **PaddlePaddle**: 3.3.0（PaddleX 自动管理）
- **支持的模型**:
  - PP-OCRv5 (文字识别)
  - PP-LCNet (布局检测)
  - PP-YOLO (目标检测)

---

## 参考资料

- [PaddleX 官方文档](https://paddlex.readthedocs.io/)
- [PaddleX GitHub](https://github.com/PaddlePaddle/PaddleX)
- [PaddleX 模型库](https://paddlepaddle.github.io/PaddleX/model_zoo.html)

---

## 迁移日志

- **2025-03-13**: 统一迁移到 PaddleX
- **2025-03-13**: 重写 ocr_service.py
- **2025-03-13**: 创建 page_parser.py
- **2025-03-13**: 更新依赖和安装脚本
- **2025-03-13**: 保持向后兼容
