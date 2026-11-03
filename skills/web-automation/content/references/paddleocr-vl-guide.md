# PaddleOCR-VL 使用指南

## 目录
- [概览](#概览)
- [核心功能](#核心功能)
- [安装配置](#安装配置)
- [API 使用](#api-使用)
- [命令行使用](#命令行使用)
- [高级功能](#高级功能)
- [最佳实践](#最佳实践)

## 概览

PaddleOCR-VL 是视觉语言模型服务，支持图像问答、图像理解、多模态交互等功能。

**核心特性：**
- 强大的视觉语言理解能力
- 支持图像问答和交互
- 场景分析和内容描述
- 多模态智能处理

**适用场景：**
- 图像内容理解
- 视觉问答系统
- 场景识别和分析
- 图像内容检索
- 多模态智能应用

## 核心功能

### 1. 图像问答 (Image QA)
基于图像内容回答用户问题，支持自然语言交互。

**特点：**
- 准确理解图像内容
- 支持复杂问题
- 返回答案和依据

### 2. 图像描述 (Image Description)
生成图像的自然语言描述。

**特点：**
- 简单描述：快速概述
- 详细描述：完整信息
- 可控详细程度

### 3. 场景分析 (Scene Analysis)
分析图像的场景类型和关键元素。

**特点：**
- 识别场景类型（发票、合同、文档等）
- 提取关键元素
- 结构化返回结果

### 4. 文字提取 (Text Extraction)
提取图像中的文字内容，支持带版面信息的提取。

**特点：**
- 高精度文字识别
- 可选版面信息
- 支持批量处理

## 安装配置

### 环境要求
- Python >= 3.8
- PaddlePaddle >= 2.6.0
- PaddleOCR >= 3.0.0
- Transformers >= 4.30.0
- PyTorch >= 2.0.0

### 安装依赖
```bash
pip install paddleocr>=3.0.0 transformers torch
```

### GPU 支持（可选）
```bash
pip install paddlepaddle-gpu>=2.6.0
```

## API 使用

### 初始化服务
```python
from vision_language_service import VisionLanguageService

# 初始化服务（CPU）
service = VisionLanguageService(use_gpu=False)

# 初始化服务（GPU）
service = VisionLanguageService(use_gpu=True)
```

### 图像问答
```python
result = service.image_qa(
    image_path="image.png",
    question="图像中有什么内容？"
)

if result["success"]:
    print("答案:", result["answer"])
    print("图像内容:", result["image_content"])
else:
    print("错误:", result["error"])
```

### 描述图像
```python
# 简单描述
result = service.describe_image(
    image_path="image.png",
    detail_level="simple"
)

if result["success"]:
    print("描述:", result["description"])

# 详细描述
result = service.describe_image(
    image_path="image.png",
    detail_level="detailed"
)

if result["success"]:
    print("详细描述:", result["description"])
```

### 分析场景
```python
result = service.analyze_scene(image_path="image.png")

if result["success"]:
    print("场景类型:", result["scene_type"])
    print("关键元素:", result["key_elements"])
    print("图像内容:", result["image_content"])
```

### 提取文字
```python
# 提取文字（不含版面信息）
result = service.extract_text(image_path="image.png")

if result["success"]:
    print("完整文本:", result["text"])
    print("文本列表:", result["texts"])

# 提取文字（包含版面信息）
result = service.extract_text(
    image_path="image.png",
    with_layout=True
)

if result["success"]:
    print("完整文本:", result["text"])
    print("版面信息:", result["layout"])
    for item in result["layout"]:
        print(f"  文字: {item['text']}")
        print(f"  位置: {item['bbox']}")
```

## 命令行使用

### 图像问答
```bash
# 基本问答
python vision_language_service.py qa image.png "图像中有什么内容？"

# 复杂问题
python vision_language_service.py qa image.png "发票的金额和开票日期分别是多少？"
```

### 描述图像
```bash
# 简单描述
python vision_language_service.py describe image.png --detail-level simple

# 详细描述
python vision_language_service.py describe image.png --detail-level detailed
```

### 分析场景
```bash
python vision_language_service.py analyze image.png
```

### 提取文字
```bash
# 提取文字（不含版面信息）
python vision_language_service.py extract image.png

# 提取文字（包含版面信息）
python vision_language_service.py extract image.png --with-layout
```

### 使用 GPU 加速
```bash
python vision_language_service.py qa image.png "问题是什么？" --gpu
```

## 高级功能

### 批量图像问答
```python
import glob

service = VisionLanguageService(use_gpu=False)

# 批量问答
for image_path in glob.glob("images/*.png"):
    result = service.image_qa(image_path, "图像中有什么？")
    if result["success"]:
        print(f"{image_path}: {result['answer']}")
```

### 批量场景分析
```python
import glob

service = VisionLanguageService(use_gpu=False)

# 批量场景分析
for image_path in glob.glob("documents/*.png"):
    result = service.analyze_scene(image_path)
    if result["success"]:
        print(f"{image_path}: 场景={result['scene_type']}, 关键元素={result['key_elements']}")
```

### 自定义场景分类
可以通过修改 `_analyze_scene_content` 方法实现自定义场景分类。

```python
def _analyze_scene_content(self, image_content: List[str]) -> Dict[str, Any]:
    full_text = "\n".join(image_content).lower()

    # 自定义场景分类逻辑
    if "特定关键词" in full_text:
        scene_type = "custom_scene"
        key_elements = ["元素1", "元素2"]
    else:
        scene_type = "general"
        key_elements = image_content[:5]

    return {
        "scene_type": scene_type,
        "key_elements": key_elements
    }
```

### 错误处理
```python
result = service.image_qa(image_path, question)

if not result["success"]:
    # 处理错误
    error_type = result.get("error")
    if "不存在" in error_type:
        print("文件路径错误")
    elif "未返回有效结果" in error_type:
        print("图像内容无法识别")
    else:
        print(f"其他错误: {error_type}")
```

## 最佳实践

### 1. 图像质量
- 使用清晰的图像
- 分辨率建议 >= 300 DPI
- 避免模糊、倾斜、光照不均

### 2. 问题设计
- 问题要明确具体
- 避免歧义
- 优先提取关键信息

### 3. 性能优化
- 批量处理时使用 GPU
- 合理选择描述详细程度
- 避免重复加载模型

### 4. 场景识别
- 根据业务需求定制场景类型
- 提取关键元素要准确
- 建立场景标签体系

### 5. 结果验证
- 验证问答的准确性
- 对于重要数据进行人工审核
- 建立质量反馈机制

## 常见问题

### Q: 如何提高识别准确率？
A:
1. 使用高质量的输入图像
2. 确保图像清晰、光照均匀
3. 避免图像倾斜和模糊
4. 使用 GPU 加速可以提高速度

### Q: 支持哪些类型的图像？
A: 支持各种类型的图像，包括文档、发票、合同、身份证、菜单等。

### Q: 可以处理复杂场景吗？
A: 可以，PaddleOCR-VL 具有强大的场景理解能力，可以处理复杂场景。

### Q: 如何定制场景分类？
A: 通过修改 `_analyze_scene_content` 方法实现自定义场景分类逻辑。

### Q: GPU 加速需要什么环境？
A: 需要安装 CUDA 和 cuDNN，并安装 `paddlepaddle-gpu`。

## 相关资源

- 官方文档: https://www.paddleocr.ai/
- PaddleOCR-VL 文档: https://www.paddleocr.ai/latest/version3.x/pipeline_usage/PaddleOCR-VL.html
- GitHub 仓库: https://github.com/PaddlePaddle/PaddleOCR
