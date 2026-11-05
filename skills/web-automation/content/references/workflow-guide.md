# 工作流引擎使用指南

## 目录
- [概览](#概览)
- [核心功能](#核心功能)
- [支持的工作流](#支持的工作流)
- [安装配置](#安装配置)
- [API 使用](#api-使用)
- [命令行使用](#命令行使用)
- [自定义工作流](#自定义工作流)
- [最佳实践](#最佳实践)

## 概览

工作流引擎（Workflow Engine）是一个强大的自动化工具，支持多步骤的文档和网页理解任务。

**核心特性：**
- 多步骤自动化流程
- 自动服务发现和初始化
- GPU 自动检测和回退
- 统一的错误处理
- 结果聚合和报告生成

**适用场景：**
- 复杂文档分析
- 批量文档处理
- 网页内容抓取
- 表格数据提取
- 多模态分析

## 核心功能

### 1. 服务管理
- 自动检测可用服务
- 统一的服务接口
- GPU 自动配置

### 2. 工作流执行
- 自动执行多步骤流程
- 步骤依赖管理
- 错误处理和回退

### 3. 结果聚合
- 统一的结果格式
- 步骤状态跟踪
- 执行时间统计

## 支持的工作流

### 1. 文档理解工作流 (Document Understanding)

**流程：**
1. OCR 识别
2. 文档分类
3. 表格识别（如果有）
4. 文档问答（可选）
5. 摘要生成

**适用场景：**
- 发票处理
- 合同分析
- 证件识别
- 文档归档

### 2. 表格提取工作流 (Table Extraction)

**流程：**
1. 表格检测
2. 表格识别
3. 数据提取
4. 格式转换
5. 结果导出

**适用场景：**
- 发票表格提取
- 财务报表处理
- 数据整理
- 数据导入

### 3. 网页抓取工作流 (Web Scraping)

**流程：**
1. 浏览器导航
2. 页面截图
3. OCR 识别
4. 内容提取
5. 数据分析

**适用场景：**
- 网页数据抓取
- 验证码处理
- 动态内容提取
- 网页分析

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

### 初始化工作流引擎
```python
from scripts.workflow_engine import WorkflowEngine

# 初始化引擎（自动检测 GPU）
engine = WorkflowEngine()

# 初始化引擎（手动指定）
engine = WorkflowEngine(use_gpu=True)
```

### 文档理解工作流
```python
# 基本文档理解
result = engine.run_document_understanding_workflow(
    image_path="document.png"
)

# 带问答的文档理解
result = engine.run_document_understanding_workflow(
    image_path="invoice.png",
    questions=["发票金额是多少？", "开票日期？"]
)

# 查看结果
if result["success"]:
    print(f"文档类型: {result['steps']['classify']['document_type']}")
    print(f"摘要: {result['steps']['summary']['summary']}")
    if 'qa' in result['steps']:
        for qa in result['steps']['qa']['results']:
            print(f"Q: {qa['question']}")
            print(f"A: {qa['answer']}")
```

### 表格提取工作流
```python
# 提取表格并输出为 HTML
result = engine.run_table_extraction_workflow(
    image_path="table.png",
    output_format="html"
)

if result["success"]:
    html_output = result["output"]
    print(html_output)

# 提取表格并输出为 JSON
result = engine.run_table_extraction_workflow(
    image_path="table.png",
    output_format="json"
)

if result["success"]:
    json_output = result["output"]
    print(json_output)
```

## 命令行使用

### 文档理解工作流
```bash
# 基本文档理解
python workflow_engine.py document-understanding document.png

# 带问答的文档理解
python workflow_engine.py document-understanding invoice.png \
  --questions "发票金额是多少？" "开票日期？" "纳税人识别号？"

# 使用 GPU
python workflow_engine.py document-understanding document.png --gpu

# JSON 输出
python workflow_engine.py document-understanding document.png --json
```

### 表格提取工作流
```bash
# 提取表格为 HTML
python workflow_engine.py table-extraction table.png --format html

# 提取表格为 JSON
python workflow_engine.py table-extraction table.png --format json

# 提取表格为 CSV
python workflow_engine.py table-extraction table.png --format csv

# JSON 输出
python workflow_engine.py table-extraction table.png --format json --json
```

### 网页抓取工作流
```bash
# 提取文本内容
python workflow_engine.py web-scraping https://example.com --type text

# 提取表格内容
python workflow_engine.py web-scraping https://example.com --type table

# 提取图片内容
python workflow_engine.py web-scraping https://example.com --type image
```

## 自定义工作流

### 创建自定义工作流
```python
from scripts.workflow_engine import WorkflowEngine

engine = WorkflowEngine()

def custom_workflow(image_path: str) -> dict:
    """自定义工作流"""
    result = {
        "workflow": "custom",
        "image_path": image_path,
        "steps": {},
        "success": False
    }

    # 步骤 1：OCR 识别
    if "ocr" in engine.services:
        ocr_result = engine.services["ocr"].recognize_image(image_path)
        result["steps"]["ocr"] = ocr_result

    # 步骤 2：版面分析
    if "page_parser" in engine.services:
        layout_result = engine.services["page_parser"].analyze_layout(image_path)
        result["steps"]["layout"] = layout_result

    # 步骤 3：场景分析
    if "vision_language" in engine.services:
        scene_result = engine.services["vision_language"].analyze_scene(image_path)
        result["steps"]["scene"] = scene_result

    result["success"] = True
    return result

# 执行自定义工作流
result = custom_workflow("document.png")
print(result)
```

### 批量处理
```python
import glob

engine = WorkflowEngine()

# 批量文档理解
for image_path in glob.glob("documents/*.png"):
    result = engine.run_document_understanding_workflow(image_path)
    if result["success"]:
        print(f"{image_path}: {result['steps']['classify']['document_type']}")

# 批量表格提取
for image_path in glob.glob("tables/*.png"):
    result = engine.run_table_extraction_workflow(image_path, output_format="json")
    if result["success"]:
        print(f"{image_path}: {len(result['output'])} 个表格")
```

## 最佳实践

### 1. GPU 使用
- 默认会自动检测 GPU，无需手动指定
- 如果 GPU 不可用，自动回退到 CPU
- 批量处理时建议使用 GPU

### 2. 错误处理
- 始终检查 `result["success"]`
- 检查每个步骤的结果
- 根据错误类型选择恢复策略

### 3. 性能优化
- 批量处理时复用引擎实例
- 使用 GPU 加速
- 合理设置工作流参数

### 4. 结果验证
- 验证识别结果的准确性
- 对于重要数据进行人工审核
- 建立质量反馈机制

### 5. 工作流设计
- 合理分解任务为多个步骤
- 考虑步骤之间的依赖关系
- 提供足够的错误处理

## 常见问题

### Q: 如何检查哪些服务可用？
A:
```python
engine = WorkflowEngine()
print(engine.services.keys())
```

### Q: 工作流执行失败怎么办？
A: 检查 `result["error"]` 字段，根据错误信息定位问题。常见问题：
- 图像文件不存在
- 服务未正确初始化
- GPU 内存不足

### Q: 如何处理大批量文档？
A:
1. 使用批量处理功能
2. 复用引擎实例
3. 使用 GPU 加速
4. 实现并行处理（需要多线程/多进程）

### Q: 可以自定义工作流吗？
A: 可以，参考"自定义工作流"章节，基于 WorkflowEngine 创建自定义工作流。

### Q: 如何集成浏览器管理功能？
A: 需要集成 playwright_manager.py 和 browser_wrapper.py，然后在工作流中调用相应的方法。

## 相关资源

- [OCR 服务指南](ocr-service.md)
- [PaddleStructure 指南](paddlestructure-guide.md)
- [PP-ChatOCRv4 指南](pp-chatocrv4-guide.md)
- [PaddleOCR-VL 指南](paddleocr-vl-guide.md)
- [文档分类指南](document-classifier-guide.md)
