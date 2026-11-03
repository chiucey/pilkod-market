# 文档分类器使用指南

## 目录
- [概览](#概览)
- [核心功能](#核心功能)
- [支持文档类型](#支持文档类型)
- [安装配置](#安装配置)
- [API 使用](#api-使用)
- [命令行使用](#命令行使用)
- [高级功能](#高级功能)
- [最佳实践](#最佳实践)

## 概览

文档分类器（Document Classifier）是一个自动识别文档类型的工具，基于 PaddleOCR 和 PaddleStructure 实现。

**核心特性：**
- 自动识别多种文档类型
- 基于规则和版面分析
- GPU 自动检测和回退
- 批量处理支持

**适用场景：**
- 文档归档
- 自动化处理
- 文档管理
- 数据预处理

## 核心功能

### 1. 文档类型识别
基于关键词和版面特征识别文档类型

### 2. 版面分析
使用 PaddleStructure 分析文档布局

### 3. 批量处理
批量识别多个文档类型

### 4. 置信度评估
评估分类结果的置信度

## 支持文档类型

| 文档类型 | 英文标识 | 特征关键词 |
|---------|---------|-----------|
| 发票 | invoice | 发票、纳税人识别号、开票日期 |
| 合同 | contract | 合同、甲方、乙方、违约责任 |
| 身份证 | id_card | 身份证、公民身份号码、住址 |
| 菜单 | menu | 菜单、菜名、价格 |
| 证书 | certificate | 证书、颁发、授予 |
| 表单 | form | 申请表、填报、审核 |
| 通用文档 | document | 无特定特征 |

## 安装配置

### 环境要求
- Python >= 3.8
- PaddlePaddle >= 2.6.0
- PaddleOCR >= 3.0.0
- PaddleStructure >= 1.0.0

### 安装依赖
```bash
pip install paddleocr>=3.0.0 paddlepaddle paddlestructure
```

### GPU 支持（可选）
```bash
pip install paddlepaddle-gpu>=2.6.0
```

## API 使用

### 初始化分类器
```python
from scripts.document_classifier import DocumentClassifier

# 初始化分类器（自动检测 GPU）
classifier = DocumentClassifier()

# 初始化分类器（手动指定）
classifier = DocumentClassifier(use_gpu=True)
```

### 识别单个文档
```python
result = classifier.classify_document("document.png")

if result["success"]:
    print(f"文档类型: {result['document_type']}")
    print(f"置信度: {result['confidence']:.2f}")
    print(f"文本预览: {result['text'][:100]}...")
    
    if result.get("layout"):
        print(f"版面分析: {result['layout']['region_counts']}")
else:
    print(f"错误: {result['error']}")
```

### 批量分类文档
```python
result = classifier.batch_classify("./documents")

if result["success"]:
    print(f"总文档数: {result['total_documents']}")
    print(f"类型统计:")
    for doc_type, count in result['type_counts'].items():
        print(f"  {doc_type}: {count}")
    
    # 查看每个文档的结果
    for doc_result in result["results"]:
        if doc_result["success"]:
            print(f"{doc_result['image_path']}: {doc_result['document_type']}")
```

## 命令行使用

### 识别单个文档
```bash
python document_classifier.py classify document.png
```

### 批量识别文档
```bash
python document_classifier.py batch ./documents
```

### 使用 GPU
```bash
python document_classifier.py classify document.png --gpu
```

### JSON 输出
```bash
python document_classifier.py classify document.png --json
```

### 批量识别并输出 JSON
```bash
python document_classifier.py batch ./documents --json
```

## 高级功能

### 自定义分类规则
可以修改 `_classify_by_rules` 方法添加自定义分类规则：

```python
def _classify_by_rules(self, text: str) -> Tuple[str, float]:
    """基于规则分类文档类型"""
    text_lower = text.lower()

    # 添加自定义规则
    if re.search(r"自定义关键词", text_lower):
        return ("custom_type", 0.9)

    # 其他规则...
    return ("document", 0.5)
```

### 结果过滤
```python
# 只获取高置信度的结果
result = classifier.classify_document("document.png")

if result["success"] and result["confidence"] > 0.8:
    print(f"高置信度文档: {result['document_type']}")
```

### 版面分析
```python
result = classifier.classify_document("document.png")

if result["success"] and result.get("layout"):
    region_counts = result["layout"]["region_counts"]
    print("文档区域分布:")
    for region_type, count in region_counts.items():
        print(f"  {region_type}: {count}")
```

## 最佳实践

### 1. 图像质量
- 使用清晰的图像
- 分辨率建议 >= 300 DPI
- 避免模糊、倾斜

### 2. 批量处理
- 复用分类器实例
- 使用 GPU 加速
- 实现并行处理

### 3. 结果验证
- 验证分类结果的准确性
- 对于低置信度结果进行人工审核
- 建立质量反馈机制

### 4. 规则优化
- 根据实际文档特点优化分类规则
- 定期更新关键词库
- 结合版面分析提高准确率

### 5. 性能优化
- 批量处理时使用 GPU
- 合理设置参数
- 避免重复加载模型

## 常见问题

### Q: 如何提高分类准确率？
A:
1. 使用高质量的输入图像
2. 优化分类规则和关键词
3. 结合版面分析
4. 使用 GPU 加速

### Q: 支持哪些文档类型？
A: 目前支持 7 种文档类型：发票、合同、身份证、菜单、证书、表单、通用文档。可以通过修改代码添加更多类型。

### Q: 如何添加自定义文档类型？
A: 修改 `_classify_by_rules` 方法，添加自定义规则和关键词。

### Q: 批量处理时性能如何？
A: 批量处理性能取决于图像数量和大小，使用 GPU 可以显著提高速度。

### Q: 分类结果不可信怎么办？
A: 检查置信度值，对于低置信度结果建议人工审核或使用其他方法验证。

## 相关资源

- [OCR 服务指南](ocr-service.md)
- [PaddleStructure 指南](paddlestructure-guide.md)
- [工作流引擎指南](workflow-guide.md)
- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
