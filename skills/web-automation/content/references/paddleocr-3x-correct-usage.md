# PaddleOCR 3.x 正确使用指南（基于官方文档）

## 官方文档参考

- [快速开始](https://www.paddleocr.ai/latest/quick_start.html)
- [安装说明](https://www.paddleocr.ai/latest/version3.x/installation.html)
- [通用 OCR 使用教程](https://www.paddleocr.ai/latest/version3.x/pipeline_usage/OCR.html)
- [PP-StructureV3 使用教程](https://www.paddleocr.ai/latest/version3.x/pipeline_usage/PP-StructureV3.html)
- [PP-ChatOCRv4 使用教程](https://www.paddleocr.ai/latest/version3.x/pipeline_usage/PP-ChatOCRv4.html)
- [PaddleOCR-VL 使用教程](https://www.paddleocr.ai/latest/version3.x/pipeline_usage/PaddleOCR-VL.html)

## 安装方式

### 1. 安装 PaddlePaddle

**CPU 版本**：
```bash
python -m pip install paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
```

**GPU 版本**（以 CUDA 11.8 为例）：
```bash
python -m pip install paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
```

### 2. 安装 PaddleOCR

**基础功能（文字识别）**：
```bash
python -m pip install paddleocr
```

**完整功能（文档解析、信息抽取、文档翻译）**：
```bash
python -m pip install "paddleocr[all]"
```

**按需安装**：
```bash
# 文档解析（PP-StructureV3）
python -m pip install "paddleocr[doc-parser]"

# 信息抽取（PP-ChatOCRv4）
python -m pip install "paddleocr[ie]"

# 文档翻译
python -m pip install "paddleocr[trans]"
```

## 依赖组说明

| 依赖组 | 对应功能 | 包含内容 |
|--------|---------|---------|
| `doc-parser` | 文档解析 | PP-StructureV3（表格、公式、印章、图片等版面元素） |
| `ie` | 信息抽取 | PP-ChatOCRv4（姓名、日期、地址、金额等关键信息） |
| `trans` | 文档翻译 | PP-DocTranslation |
| `all` | 完整功能 | 包含所有上述功能 |

## 使用方式

### 1. 通用 OCR（文字识别）

```python
from paddleocr import PaddleOCR

# 初始化 OCR（使用默认的 PP-OCRv5_server 模型）
ocr = PaddleOCR()

# 识别图片
result = ocr.ocr("image_path.jpg")

# 输出结果
for line in result:
    print(line[1][0])  # 文本内容
```

### 2. PP-StructureV3（文档解析）

```python
from paddleocr import PPStructure

# 初始化 PP-StructureV3
structure = PPStructure(show_log=True)

# 解析文档（包含表格、公式、印章等）
result = structure("document_path.jpg")

# 输出结果
for region in result:
    print(f"类型: {region['type']}")
    print(f"内容: {region.get('res', {}).get('text', '')}")
```

### 3. PP-ChatOCRv4（信息抽取）

```python
from paddleocr import PPChatOCR

# 初始化 PP-ChatOCRv4
chat_ocr = PPChatOCR()

# 问答式信息抽取
answer = chat_ocr.ocr(
    image_path="invoice.jpg",
    question="发票金额是多少？"
)
print(answer)
```

### 4. PaddleOCR-VL（视觉语言模型）

```python
from paddleocr import PaddleOCR

# 初始化 PaddleOCR-VL
vl_ocr = PaddleOCR(use_vl=True)

# 图像问答
result = vl_ocr.ocr(
    image_path="document.jpg",
    question="这张图片展示的是什么内容？"
)
print(result)
```

## Skill 中的使用

### requirements.txt

```txt
# 基础功能
paddleocr
paddlepaddle>=2.6.0

# 可选：完整功能
# "paddleocr[all]"

# 可选：VL 能力
# transformers>=4.30.0
# torch>=2.0.0
```

### 安装脚本

**install.sh**:
```bash
# 安装 PaddlePaddle
python3 -m pip install paddlepaddle>=2.6.0

# 安装 PaddleOCR（完整功能）
python3 -m pip install "paddleocr[all]"
```

### 脚本中的使用

**OCR 服务**（`scripts/ocr_service.py`）:
```python
from paddleocr import PaddleOCR

# 初始化 OCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr(image_path)
```

**版面分析**（`scripts/page_parser.py`）:
```python
from paddleocr import PPStructure

# 初始化 PP-StructureV3
structure = PPStructure(show_log=False)
result = structure(image_path)
```

**复杂页面处理**（`scripts/complex_page_processor.py`）:
```python
from paddleocr import PaddleOCR, PPStructure

# 初始化 OCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 初始化 PP-StructureV3
structure = PPStructure(show_log=False)
```

## 参数说明

### PaddleOCR 主要参数

```python
PaddleOCR(
    lang='ch',              # 语言：ch（中文）、en（英文）、korean（韩语）等
    use_angle_cls=True,     # 是否使用方向分类器
    use_gpu=False,          # 是否使用 GPU
    ocr_version='PP-OCRv5', # OCR 版本：PP-OCRv3/v4/v5
    show_log=True,          # 是否显示日志
    det=True,               # 是否进行文本检测
    rec=True                # 是否进行文本识别
)
```

### PPStructure 主要参数

```python
PPStructure(
    table=True,             # 是否识别表格
    ocr=True,               # 是否进行 OCR
    layout=True,            # 是否进行版面分析
    show_log=False,         # 是否显示日志
    structure_version='PP-StructureV3',  # 版面分析版本
    image_orientation=True  # 是否进行图像方向检测
)
```

## 常见问题

### Q: 如何选择安装方式？

A: 
- 只需要文字识别：`pip install paddleocr`
- 需要文档解析：`pip install "paddleocr[doc-parser]"`
- 需要信息抽取：`pip install "paddleocr[ie]"`
- 需要所有功能：`pip install "paddleocr[all]"`

### Q: 如何启用 GPU 加速？

A: 
1. 安装 GPU 版本的 PaddlePaddle：
   ```bash
   pip install paddlepaddle-gpu>=2.6.0
   ```
2. 初始化时指定 GPU：
   ```python
   ocr = PaddleOCR(use_gpu=True)
   ```

### Q: PP-StructureV3 和 PaddleOCR 的区别？

A: 
- `PaddleOCR`：主要用于文字识别（OCR）
- `PPStructure`：用于文档解析，包含表格、公式、印章等版面元素识别

### Q: 如何使用 PaddleOCR-VL？

A: 
1. 安装完整功能：`pip install "paddleocr[all]"`
2. 初始化时启用 VL：
   ```python
   ocr = PaddleOCR(use_vl=True)
   ```

### Q: 如何处理多种文档类型？

A: 使用 `PPStructure` 进行版面分析：
```python
structure = PPStructure()
result = structure("document.jpg")

# 结果包含不同类型的区域
for region in result:
    if region['type'] == 'table':
        print("表格:", region)
    elif region['type'] == 'text':
        print("文本:", region)
```

## 版本兼容性

- Python: 3.8 ~ 3.12
- PaddlePaddle: >= 2.6.0
- PaddleOCR: >= 3.0.0

## 参考资料

- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR 官网](https://www.paddleocr.ai)
- [PaddleX 文档](https://paddlex.readthedocs.io/)
