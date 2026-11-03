# PP-ChatOCRv4 使用指南

## 目录
- [概览](#概览)
- [核心功能](#核心功能)
- [安装配置](#安装配置)
- [API 使用](#api-使用)
- [命令行使用](#命令行使用)
- [高级功能](#高级功能)
- [最佳实践](#最佳实践)

## 概览

PP-ChatOCRv4 是基于大模型的文档理解系统，提供强大的文档问答、关键信息提取、语义理解等功能。

**核心特性：**
- 基于大模型的智能文档理解
- 支持复杂文档的问答和交互
- 结构化信息提取（发票、合同、身份证等）
- 文档摘要生成
- 深度语义理解

**适用场景：**
- 智能客服文档问答
- 发票/合同信息提取
- 文档智能审核
- 知识库构建
- 文档内容理解

## 核心功能

### 1. 文档问答 (Document QA)
基于文档内容回答用户问题，支持自然语言交互。

**特点：**
- 准确理解文档内容
- 支持复杂问题
- 返回答案和依据

### 2. 关键信息提取 (Key Information Extraction)
从文档中提取结构化信息。

**支持类型：**
- 发票信息：发票号码、金额、日期等
- 合同信息：合同编号、甲方、乙方等
- 身份证信息：姓名、身份证号、住址等
- 自定义提取：根据业务需求定制

### 3. 文档摘要 (Document Summary)
生成文档的精简摘要，快速了解文档要点。

**特点：**
- 保留关键信息
- 可控摘要长度
- 支持多语言

### 4. 语义理解 (Semantic Understanding)
理解文档的深层含义和逻辑关系。

**特点：**
- 识别文档类型
- 理解段落关系
- 提取主题信息

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
from chat_ocr_service import ChatOCRService

# 初始化服务（CPU）
service = ChatOCRService(use_gpu=False)

# 初始化服务（GPU）
service = ChatOCRService(use_gpu=True)
```

### 文档问答
```python
result = service.document_qa(
    image_path="document.png",
    question="发票金额是多少？"
)

if result["success"]:
    print("答案:", result["answer"])
    print("文档内容:", result["document_text"])
else:
    print("错误:", result["error"])
```

### 提取关键信息
```python
# 提取发票信息
result = service.extract_key_info(
    image_path="invoice.png",
    info_type="invoice"
)

if result["success"]:
    key_info = result["key_info"]
    print("发票号码:", key_info.get("发票号码"))
    print("金额:", key_info.get("金额"))
    print("日期:", key_info.get("开票日期"))

# 提取合同信息
result = service.extract_key_info(
    image_path="contract.png",
    info_type="contract"
)

# 提取身份证信息
result = service.extract_key_info(
    image_path="id_card.png",
    info_type="id_card"
)
```

### 生成文档摘要
```python
result = service.generate_summary(
    image_path="document.png",
    max_length=200
)

if result["success"]:
    print("摘要:", result["summary"])
    print("原文:", result["document_text"])
```

## 命令行使用

### 文档问答
```bash
python chat_ocr_service.py qa image.png "发票金额是多少？"
```

### 提取关键信息
```bash
# 提取发票信息
python chat_ocr_service.py extract invoice.png --info-type invoice

# 提取合同信息
python chat_ocr_service.py extract contract.png --info-type contract

# 提取身份证信息
python chat_ocr_service.py extract id_card.png --info-type id_card
```

### 生成文档摘要
```bash
# 生成 200 字摘要
python chat_ocr_service.py summary document.png --max-length 200

# 生成 500 字摘要
python chat_ocr_service.py summary document.png --max-length 500
```

### 使用 GPU 加速
```bash
python chat_ocr_service.py qa image.png "问题是什么？" --gpu
```

## 高级功能

### 自定义信息提取
可以通过修改 `_extract_by_type` 方法实现自定义提取逻辑。

```python
def _extract_by_type(self, text: str, info_type: str) -> Dict[str, str]:
    if info_type == "custom":
        # 自定义提取逻辑
        info = {}
        lines = text.split('\n')
        for line in lines:
            if "关键字段" in line:
                info["字段值"] = line.split("：")[-1].strip()
        return info
```

### 批量处理
```python
import glob

service = ChatOCRService(use_gpu=False)

# 批量提取发票信息
for image_path in glob.glob("invoices/*.png"):
    result = service.extract_key_info(image_path, info_type="invoice")
    if result["success"]:
        print(f"{image_path}: {result['key_info']}")
```

### 错误处理
```python
result = service.document_qa(image_path, question)

if not result["success"]:
    # 处理错误
    error_type = result.get("error")
    if "不存在" in error_type:
        print("文件路径错误")
    elif "未返回有效结果" in error_type:
        print("文档内容无法识别")
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
- 合理设置摘要长度
- 避免重复加载模型

### 4. 错误处理
- 始终检查 `success` 字段
- 处理文件不存在的情况
- 处理识别失败的情况

### 5. 结果验证
- 验证提取信息的准确性
- 对于重要数据进行人工审核
- 建立质量反馈机制

## 常见问题

### Q: 如何提高识别准确率？
A:
1. 使用高质量的输入图像
2. 确保图像清晰、光照均匀
3. 避免图像倾斜和模糊
4. 使用 GPU 加速可以提高速度

### Q: 支持哪些语言？
A: 支持中英文，PP-ChatOCRv4 主要针对中文文档优化。

### Q: 如何处理复杂版面？
A: PP-ChatOCRv4 内置版面分析能力，可以处理复杂版面的文档。

### Q: 可以自定义提取规则吗？
A: 可以，通过修改 `_extract_by_type` 方法实现自定义提取逻辑。

### Q: GPU 加速需要什么环境？
A: 需要安装 CUDA 和 cuDNN，并安装 `paddlepaddle-gpu`。

## 相关资源

- 官方文档: https://www.paddleocr.ai/
- PP-ChatOCRv4 文档: https://www.paddleocr.ai/latest/version3.x/pipeline_usage/PP-ChatOCRv4.html
- GitHub 仓库: https://github.com/PaddlePaddle/PaddleOCR
