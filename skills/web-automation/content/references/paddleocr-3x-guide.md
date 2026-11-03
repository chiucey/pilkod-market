# PaddleOCR 3.x 适配说明

## 重要提示

**本 Skill 已适配 PaddleOCR 3.x API**，以获得 VL（Vision-Language）支持。

---

## 版本要求

### 必需版本
```
PaddleOCR >= 3.0.0
PaddlePaddle >= 3.0.0
```

### 当前推荐版本
```
PaddleOCR 3.4.0
PaddlePaddle 3.3.0
```

---

## API 变化（2.x vs 3.x）

### 初始化参数

**PaddleOCR 2.x**：
```python
ocr = PaddleOCR(
    use_angle_cls=True,
    lang='ch',
    use_gpu=False,
    show_log=False
)
```

**PaddleOCR 3.x**：
```python
ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True,
    return_word_box=True
)
```

### 调用方式

**PaddleOCR 2.x**：
```python
result = ocr.ocr(image_path, cls=True)
# 返回: [[{'bbox': [...], 'text': '...', 'confidence': 0.99}], ...]
```

**PaddleOCR 3.x**：
```python
result = ocr.predict(image_path)
# 返回: {'texts': [{'text': '...', 'score': 0.99}], 'boxes': [...]}
```

---

## 使用方式

### 方法 1：使用 OCR 服务（推荐）

```python
from ocr_service import OCRService

# 初始化 OCR 服务（已适配 3.x）
ocr = OCRService(lang='ch')

# 文字识别
result = ocr.recognize_image('captcha.png')
if result['success']:
    print(f"识别结果: {result['full_text']}")
    print(f"详细: {result['text_lines']}")

# 元素检测
result = ocr.detect_elements('page.png')
if result['success']:
    for elem in result['elements']:
        print(f"[{elem['type']}] {elem['text']}")

# 表格提取
result = ocr.extract_table('table.png')
if result['success']:
    for row in result['table_data']:
        print(' | '.join(row))
```

### 方法 2：直接使用 PaddleOCR 3.x

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang='ch',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=True
)

result = ocr.predict('image.png')
texts = result.get('texts', [])
for item in texts:
    print(f"{item['text']} (置信度: {item['score']})")
```

---

## 环境要求

### 必需环境
- Python 3.8+
- PaddlePaddle >= 3.0.0
- 稳定的网络连接（首次下载模型）

### 推荐环境
- Linux Ubuntu 20.04+
- Python 3.10+
- 8GB+ 内存
- 2GB+ 磁盘空间

### 不兼容环境
- ❌ Windows（部分模型可能不兼容）
- ❌ ARM 架构（需要重新编译）
- ❌ 旧版本 PaddlePaddle

---

## 故障排除

### 问题 1：oneDNN 错误

**错误信息**：
```
ConvertPirAttribute2RuntimeAttribute not support
at /paddle/paddle/fluid/framework/new_executor/instruction/onednn/onednn_instruction.cc:116
```

**原因**：PaddlePaddle 3.x 与当前环境的 oneDNN 版本不兼容

**解决方案**：
```bash
# 方案 1：设置环境变量（推荐）
export MKL_THREADING_LAYER=GNU

# 方案 2：降级到 PaddlePaddle 2.x（失去 VL 支持）
pip uninstall paddleocr paddlepaddle -y
pip install "paddleocr>=2.8.0,<3.0.0" "paddlepaddle>=2.6.0,<3.0.0"

# 方案 3：使用 Docker（最稳定）
docker run -it paddlepaddle/paddle:latest-gpu-cuda11.2-cudnn8
```

### 问题 2：模型下载失败

**错误信息**：
```
Connectivity check to the model hoster
```

**解决方案**：
```bash
# 跳过连接检查
export PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True

# 或手动下载模型
# 模型会被下载到 ~/.paddlex/official_models/
```

### 问题 3：内存不足

**错误信息**：
```
OutOfMemoryError
```

**解决方案**：
```python
# 使用更小的模型
ocr = PaddleOCR(
    lang='ch',
    text_det_limit_side_len=960,  # 减小检测尺寸
    text_rec_batch_size=1  # 减小批处理大小
)
```

### 问题 4：识别速度慢

**原因**：首次运行需要加载模型

**解决方案**：
```python
# 使用单例模式，避免重复初始化
class OCRSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PaddleOCR(lang='ch')
        return cls._instance
```

---

## VL（Vision-Language）功能

PaddleOCR 3.x 新增的 VL 功能：

### 1. 文档理解
```python
result = ocr.predict('document.png', task='document_understanding')
```

### 2. 表格识别
```python
result = ocr.predict('table.png', task='table_recognition')
```

### 3. 版面分析
```python
result = ocr.predict('layout.png', task='layout_analysis')
```

**注意**：VL 功能可能需要额外的模型下载和配置。

---

## 性能优化

### 1. 使用 GPU
```python
ocr = PaddleOCR(
    lang='ch',
    # 3.x 会自动检测 GPU
)
```

### 2. 批处理
```python
results = []
for img_path in image_paths:
    results.append(ocr.predict(img_path))
```

### 3. 缓存模型
- 模型自动缓存到 `~/.paddlex/official_models/`
- 首次运行较慢，后续运行快

---

## 与 2.x 的兼容性

如果 3.x 在您的环境中无法运行，可以降级到 2.x：

```bash
pip uninstall paddleocr paddlepaddle -y
pip install "paddleocr>=2.8.0,<3.0.0" "paddlepaddle>=2.6.0,<3.0.0"
```

**注意**：
- ✅ 2.x API 更稳定
- ✅ 兼容性更好
- ❌ 不支持 VL 功能
- ❌ 需要修改 ocr_service.py

---

## 参考资料

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddlePaddle 官方文档](https://www.paddlepaddle.org.cn/)
- [PaddleOCR 3.x 更新日志](https://github.com/PaddlePaddle/PaddleOCR/releases)

---

## 更新日志

- **2025-03-13**: 适配 PaddleOCR 3.x API
- **2025-03-13**: 重写 ocr_service.py
- **2025-03-13**: 添加 VL 功能支持
- **2025-03-13**: 更新安装脚本和文档
