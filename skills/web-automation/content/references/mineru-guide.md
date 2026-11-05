# MinerU 使用指南

## 目录
- [概览](#概览)
- [安装配置](#安装配置)
- [API 参考](#api-参考)
- [使用边界](#使用边界)
- [性能限制](#性能限制)
- [使用示例](#使用示例)

## 概览
MinerU 是由 OpenBMB 团队开发的文档智能处理工具，专注于 PDF 和文档的结构化解析。

**核心能力**：
- PDF 文档解析和结构化
- 高质量表格提取
- 文档版面分析
- 扫描版 OCR 处理
- 多格式输出（Markdown/JSON/HTML）

**适用场景**：
- 网页 PDF 文档下载和解析
- 学术论文内容提取
- 技术文档结构化
- 表格数据高质量提取

## 安装配置

### 1. 安装依赖
```bash
# 基础安装
pip install magic-pdf[full]

# 或单独安装
pip install magic-pdf
pip install pillow pypdf
```

### 2. 下载模型文件
```bash
# 下载必需的模型文件
magic-pdf download

# 模型文件会下载到 ~/.magic-pdf/ 目录
```

### 3. 验证安装
```bash
# 测试安装
python -c "from magic_pdf.pipe.UNIPipe import UNIPipe; print('安装成功')"
```

### 4. 依赖列表
```
magic-pdf>=0.7.0
pillow>=9.0.0
pypdf>=3.0.0
numpy>=1.21.0
```

## API 参考

### 初始化服务
```python
from mineru_service import MinerUService

service = MinerUService(output_dir=".web-automation/mineru-output")
```

### 1. 解析 PDF 文档
```python
result = service.parse_pdf(
    pdf_path="document.pdf",
    output_format="markdown",  # markdown/json/html
    ocr_enabled=True,          # 启用 OCR（扫描版 PDF）
    extract_images=False       # 是否提取图片
)

# 返回结果
{
    "success": True,
    "data": "# 文档标题\n\n文档内容...",
    "metadata": {
        "file_name": "document.pdf",
        "file_size": 1048576,
        "file_size_mb": 1.0
    },
    "output_format": "markdown",
    "output_dir": ".web-automation/mineru-output/document"
}
```

### 2. 提取表格数据
```python
result = service.extract_tables(
    image_path="table.png",
    output_format="markdown"  # markdown/json/csv
)

# 返回结果
{
    "success": True,
    "data": "| 列1 | 列2 |\n|---|---|\n| 数据1 | 数据2 |",
    "output_format": "markdown",
    "output_dir": ".web-automation/mineru-output/tables/table"
}
```

### 3. 分析文档布局
```python
result = service.analyze_layout(image_path="page.png")

# 返回结果
{
    "success": True,
    "message": "布局分析完成",
    "data": {...},
    "note": "布局信息包含在解析数据中"
}
```

### 4. 解析 PDF 为 JSON
```python
result = service.parse_pdf_to_json(pdf_path="document.pdf")

# 返回结构化 JSON 数据
{
    "success": True,
    "data": {
        "pages": [
            {
                "page_num": 1,
                "content": [...],
                "tables": [...],
                "images": [...]
            }
        ]
    },
    ...
}
```

### 5. 批量解析 PDF
```python
result = service.batch_parse_pdfs(
    pdf_paths=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    output_format="markdown"
)

# 返回结果
{
    "success": True,
    "total": 3,
    "success_count": 2,
    "failed_count": 1,
    "results": [...],
    "failed": [...]
}
```

## 使用边界

### 支持的文件格式

| 格式 | 支持 | 说明 |
|------|------|------|
| PDF | ✅ | 文本版和扫描版 |
| PNG | ✅ | 表格提取和布局分析 |
| JPG/JPEG | ✅ | 表格提取和布局分析 |
| BMP | ✅ | 表格提取和布局分析 |
| Word | ❌ | 需先转换为 PDF |
| PPT | ❌ | 需先转换为 PDF |

### 语言支持
- ✅ **中文**：准确率 85-95%
- ✅ **英文**：准确率 90-98%
- ⚠️ **其他语言**：准确率较低（<70%）

### 文档类型
| 类型 | 准确率 | 说明 |
|------|--------|------|
| 文本 PDF | 90-98% | 直接提取文本 |
| 扫描版 PDF | 70-85% | 需要 OCR |
| 复杂表格 | 80-90% | 多列表格准确率降低 |
| 简单表格 | 90-95% | 规则表格准确率高 |
| 混合布局 | 75-85% | 图文混排准确率中等 |
| 双栏布局 | 70-80% | 布局识别难度较高 |

### 功能限制

#### ❌ 不支持
1. 加密 PDF（需要先解密）
2. 超大文档（>500页或>100MB）
3. 复杂的数学公式
4. 手写内容识别
5. 多列复杂布局
6. 实时视频流处理

#### ⚠️ 部分支持
1. 扫描版 PDF（准确率 70-85%）
2. 复杂表格（准确率 80-90%）
3. 图文混排（准确率 75-85%）
4. 双栏布局（准确率 70-80%）

## 性能限制

### 处理速度

| 配置 | 文本 PDF | 扫描 PDF | 表格提取 |
|------|---------|---------|---------|
| CPU | 10-50 页/分钟 | 5-20 页/分钟 | 2-10 张/分钟 |
| GPU | 50-200 页/分钟 | 20-80 页/分钟 | 10-50 张/分钟 |

### 内存占用

| 文档复杂度 | 内存占用 |
|-----------|---------|
| 简单文档（<10页） | 500MB - 1GB |
| 中等文档（10-50页） | 1GB - 2GB |
| 复杂文档（50-200页） | 2GB - 4GB |
| 超大文档（>200页） | 4GB - 5GB |

### 文档限制
- **单文档大小**：建议不超过 100MB
- **单文档页数**：建议不超过 500 页
- **图像分辨率**：建议不超过 4096x4096

### 并发限制
- CPU 模式：建议并发不超过 2
- GPU 模式：建议并发不超过 4

## 使用示例

### 示例 1：网页 PDF 下载和解析
```bash
# 1. 使用 Playwright 下载 PDF
python scripts/playwright_manager.py create
python scripts/browser_wrapper.py navigate --url=https://example.com/document.pdf
python scripts/playwright_manager.py screenshot --output-path=./document.pdf

# 2. 使用 MinerU 解析 PDF
python scripts/mineru_service.py parse-pdf \
  --pdf-path=./document.pdf \
  --output-format=markdown \
  --ocr-enabled
```

### 示例 2：网页表格提取
```bash
# 1. 截图表格区域
python scripts/playwright_manager.py screenshot \
  --output-path=./table.png \
  --selector=".data-table"

# 2. 使用 MinerU 提取表格
python scripts/mineru_service.py extract-tables \
  --image-path=./table.png \
  --output-format=markdown
```

### 示例 3：学术论文解析
```bash
# 解析学术论文 PDF
python scripts/mineru_service.py parse-pdf-to-json \
  --pdf-path=./paper.pdf

# 提取结构化内容
# 结果包含：标题、摘要、章节、表格、图片等
```

### 示例 4：批量处理 PDF
```bash
# 批量解析目录下的所有 PDF
python scripts/mineru_service.py batch-parse \
  --pdf-dir=./pdfs \
  --output-format=markdown
```

## 最佳实践

### 1. 文档预处理
```bash
# 对于超大文档，先分拆
# 使用其他工具将 PDF 分拆为多个小文件
```

### 2. OCR 优化
```python
# 扫描版 PDF 启用 OCR
result = service.parse_pdf(
    pdf_path="scanned.pdf",
    ocr_enabled=True  # 必须
)
```

### 3. 输出格式选择
```python
# 文本提取：使用 markdown
result = service.parse_pdf(pdf_path, output_format="markdown")

# 结构化数据：使用 json
result = service.parse_pdf(pdf_path, output_format="json")

# 网页展示：使用 html
result = service.parse_pdf(pdf_path, output_format="html")
```

### 4. 错误处理
```python
result = service.parse_pdf(pdf_path)

if not result["success"]:
    if "过大" in result["error"]:
        # 分拆文档
        print("文档过大，建议分拆处理")
    elif "加密" in result["error"]:
        # 解密文档
        print("文档已加密，需要先解密")
```

### 5. 资源管理
```python
# 及时清理临时文件
import shutil
shutil.rmtree(".web-automation/mineru-output")
```

## 与其他工具的集成

### 与 Playwright 集成
```python
# 1. Playwright 下载 PDF
await page.goto("https://example.com/document.pdf")
await page.download_file("document.pdf")

# 2. MinerU 解析
result = service.parse_pdf("document.pdf")
```

### 与 PaddleOCR 对比

| 特性 | PaddleOCR | MinerU |
|------|-----------|--------|
| 文字识别 | ✅ 优秀 | ✅ 优秀 |
| 表格提取 | ⚠️ 一般 | ✅ 优秀 |
| 布局分析 | ❌ 不支持 | ✅ 支持 |
| 文档理解 | ❌ 不支持 | ✅ 支持 |
| PDF 解析 | ❌ 不支持 | ✅ 支持 |

**建议**：
- 简单文字识别：使用 PaddleOCR
- 复杂文档解析：使用 MinerU
- 两者结合：使用 PaddleOCR 识别验证码，MinerU 解析文档

## 注意事项

### 1. 首次运行
首次运行需要下载模型文件（约 500MB），建议提前下载：
```bash
magic-pdf download
```

### 2. GPU 加速
使用 GPU 可以显著提升速度：
```bash
# 安装 GPU 版本
pip install magic-pdf[full,cuda]

# 或设置环境变量
export USE_CUDA=True
```

### 3. 编码问题
中文文档输出建议使用 UTF-8 编码：
```python
result = service.parse_pdf(pdf_path)
text = result["data"].encode("utf-8")
```

### 4. 内存不足
如果遇到内存不足：
- 减小文档大小（分拆处理）
- 减少并发数
- 降低图像分辨率

## 常见问题

### Q1: 为什么扫描版 PDF 识别率低？
A: 扫描版 PDF 依赖 OCR，准确率受图像质量影响。建议：
- 使用高分辨率扫描（300 DPI 以上）
- 确保图像清晰、对比度高
- 避免扭曲和倾斜

### Q2: 如何处理加密 PDF？
A: MinerU 不支持加密 PDF。需要先使用其他工具解密：
```bash
# 使用 qpdf 解密
qpdf --decrypt --password="" encrypted.pdf decrypted.pdf
```

### Q3: 能否识别手写内容？
A: MinerU 不支持手写内容识别。建议使用专门的 OCR 工具。

### Q4: 如何提升表格提取准确率？
A: 建议：
- 确保表格线清晰
- 避免合并单元格过多
- 使用高分辨率截图
- 优先选择 markdown 格式输出

## 性能优化建议

1. **文档分拆**：超大文档分拆为多个小文件
2. **批量处理**：使用 batch_parse_pdfs 批量处理
3. **并发控制**：合理控制并发数（CPU: 2, GPU: 4）
4. **格式选择**：根据需求选择合适的输出格式
5. **资源清理**：及时清理临时文件和缓存
