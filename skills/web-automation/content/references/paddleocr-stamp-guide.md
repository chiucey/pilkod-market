# PaddleOCR 3.x 印章识别指南

## 概览

PaddleOCR 3.x 新增了强大的印章识别能力，支持印章检测、文字识别、类型分类和真伪判断。

## 核心能力

### 1. 印章检测

**功能**：检测图像中的所有印章

**支持的印章类型**：
- 圆形印章
- 方形印章
- 椭圆印章
- 不规则印章

**使用方式**：
```python
from scripts.stamp_recognition_service import StampRecognitionService

service = StampRecognitionService()
stamps = service.detect_stamps("document.png")

for stamp in stamps:
    print(f"印章类型: {stamp['type']}")
    print(f"置信度: {stamp['confidence']}")
    print(f"位置: {stamp['bbox']}")
```

### 2. 印章文字识别

**功能**：识别印章中的文字内容

**特性**：
- 支持中英文混合识别
- 支持多行文字识别
- 自动检测印章方向
- 高精度识别（PaddleOCR 3.x）

**使用方式**：
```python
from scripts.stamp_recognition_service import StampRecognitionService

service = StampRecognitionService()

# 识别整个图像中的印章文字
result = service.recognize_stamp_text("document.png")
print(f"文字: {result['text']}")
print(f"置信度: {result['confidence']}")
print(f"方向: {result['direction']}")

# 识别指定位置的印章
bbox = [[100, 100], [300, 100], [300, 300], [100, 300]]
result = service.recognize_stamp_text("document.png", bbox)
print(f"文字: {result['text']}")
```

### 3. 印章类型分类

**功能**：根据印章文字和特征分类印章类型

**支持的类型**：
- **official**: 公章（企业名称、公司章）
- **finance**: 财务章（财务专用章、发票章）
- **contract**: 合同章（合同、协议章）
- **invoice**: 发票章（开票章、税务章）
- **other**: 其他类型

**使用方式**：
```python
from scripts.stamp_recognition_service import StampRecognitionService

service = StampRecognitionService()
result = service.classify_stamp_type("document.png")

print(f"印章类型: {result['type']}")
print(f"置信度: {result['confidence']}")
```

### 4. 印章真伪验证

**功能**：验证印章的真伪

**验证依据**：
- 印章文字是否匹配预期内容
- 印章形状是否规范
- 印章识别置信度

**使用方式**：
```python
from scripts.stamp_recognition_service import StampRecognitionService

service = StampRecognitionService()
result = service.verify_stamp(
    "document.png",
    expected_text="某某有限公司"
)

print(f"验证结果: {result['valid']}")
print(f"置信度: {result['confidence']}")
print(f"原因: {result['reason']}")
```

### 5. 一键检测和识别

**功能**：一次性完成印章检测、文字识别和类型分类

**使用方式**：
```python
from scripts.stamp_recognition_service import StampRecognitionService

service = StampRecognitionService()
stamps = service.detect_and_recognize("document.png")

for stamp in stamps:
    print(f"印章类型: {stamp['type']}")
    print(f"文字: {stamp['text']}")
    print(f"置信度: {stamp['confidence']}")
    print("-" * 50)
```

## 命令行使用

### 检测印章

```bash
python scripts/stamp_recognition_service.py document.png --detect
```

### 识别印章文字

```bash
python scripts/stamp_recognition_service.py document.png --recognize
```

### 验证印章真伪

```bash
python scripts/stamp_recognition_service.py document.png --verify \
    --expected-text "某某有限公司"
```

### 使用 GPU 加速

```bash
python scripts/stamp_recognition_service.py document.png --recognize --gpu
```

### 输出到文件

```bash
python scripts/stamp_recognition_service.py document.png --recognize \
    --output result.json
```

## 完整工作流示例

### 文档中的印章检测与识别

```python
from scripts.stamp_recognition_service import StampRecognitionService

# 1. 初始化服务
service = StampRecognitionService(use_gpu=True)

# 2. 检测并识别所有印章
stamps = service.detect_and_recognize("document.png")

# 3. 分析结果
print(f"检测到 {len(stamps)} 个印章")
print("=" * 50)

for i, stamp in enumerate(stamps, 1):
    print(f"印章 #{i}")
    print(f"类型: {stamp['type']}")
    print(f"文字: {stamp['text']}")
    print(f"置信度: {stamp['confidence']:.2f}")
    print(f"方向: {stamp['direction']}°")
    print()

# 4. 分类每个印章的类型
for i, stamp in enumerate(stamps, 1):
    bbox = stamp['bbox']
    result = service.classify_stamp_type("document.png", bbox)
    print(f"印章 #{i} 类型分类: {result['type']} (置信度: {result['confidence']:.2f})")
```

### 契约文档印章验证

```python
from scripts.stamp_recognition_service import StampRecognitionService

# 1. 初始化服务
service = StampRecognitionService()

# 2. 验证印章
result = service.verify_stamp(
    "contract.png",
    expected_text="某某贸易有限公司"
)

# 3. 输出验证结果
if result['valid']:
    print("✓ 印章验证通过")
    print(f"置信度: {result['confidence']:.2f}")
    print(f"印章文字: {result['stamp']['text']}")
else:
    print("✗ 印章验证失败")
    print(f"原因: {result['reason']}")
```

## 性能优化建议

### 1. 使用 GPU 加速

```python
service = StampRecognitionService(use_gpu=True)
```

**注意**：需要先安装 CUDA 版本的 PaddlePaddle

### 2. 批量处理

```python
import os
from pathlib import Path

service = StampRecognitionService()

# 批量处理文件夹中的所有图像
image_dir = Path("documents")
for image_path in image_dir.glob("*.png"):
    stamps = service.detect_and_recognize(str(image_path))
    print(f"{image_path.name}: 检测到 {len(stamps)} 个印章")
```

### 3. 结果缓存

```python
import pickle
from pathlib import Path

def get_or_cache_stamps(image_path: str, cache_dir: str = "cache"):
    """获取或缓存印章识别结果"""
    cache_file = Path(cache_dir) / f"{Path(image_path).stem}.pkl"

    # 检查缓存
    if cache_file.exists():
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    # 识别印章
    service = StampRecognitionService()
    stamps = service.detect_and_recognize(image_path)

    # 保存缓存
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(stamps, f)

    return stamps
```

## 常见问题

### Q: 如何提高印章检测的准确率？

A:
1. 确保图像清晰度足够（分辨率至少 300 DPI）
2. 使用适当的图像预处理（去噪、对比度增强）
3. 使用 GPU 加速提高识别精度

### Q: 印章类型分类的准确率如何提高？

A:
1. 提供更多训练数据
2. 调整关键词匹配规则
3. 结合印章形状特征进行判断

### Q: 如何处理模糊的印章？

A:
1. 先对图像进行去模糊处理
2. 使用图像增强技术提高对比度
3. 考虑使用更高级的 OCR 模型

### Q: 支持哪些语言的印章？

A: PaddleOCR 3.x 支持 80+ 语言，包括：
- 中文（简体、繁体）
- 英文
- 日文
- 韩文
- 阿拉伯文
- 等

## API 参考

### StampRecognitionService

#### 初始化

```python
StampRecognitionService(
    det_model_dir: Optional[str] = None,
    rec_model_dir: Optional[str] = None,
    cls_model_dir: Optional[str] = None,
    use_gpu: bool = False
)
```

#### 主要方法

**detect_stamps(image_path: str) -> List[Dict[str, Any]]**
- 检测图像中的印章
- 返回印章列表，包含位置、类型、置信度

**recognize_stamp_text(image_path: str, bbox: Optional[List[List[int]]] = None) -> Dict[str, Any]**
- 识别印章文字
- 返回文字、置信度、方向

**classify_stamp_type(image_path: str, bbox: Optional[List[List[int]]] = None) -> Dict[str, Any]**
- 分类印章类型
- 返回类型和置信度

**verify_stamp(image_path: str, expected_text: Optional[str] = None) -> Dict[str, Any]**
- 验证印章真伪
- 返回验证结果

**detect_and_recognize(image_path: str) -> List[Dict[str, Any]]**
- 一键检测和识别
- 返回完整的印章信息

## 相关资源

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [OCR 服务指南](ocr-service.md)
- [版面识别指南](paddlestructure-guide.md)
- [VL 能力指南](paddleocr-vl-guide.md)
