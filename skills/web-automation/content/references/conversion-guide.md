# 文档格式转换指南

## 目录
- [概览](#概览)
- [安装配置](#安装配置)
- [支持格式](#支持格式)
- [使用边界](#使用边界)
- [性能限制](#性能限制)
- [使用示例](#使用示例)

## 概览
文档格式转换服务基于 LibreOffice Headless 模式，支持将各种 Office 文档格式转换为 PDF，以便后续使用 MinerU 进行解析。

**核心能力**：
- Word 文档转换为 PDF
- PowerPoint 演示文稿转换为 PDF
- Excel 表格转换为 PDF
- OpenDocument 格式转换
- RTF 和其他格式转换

**适用场景**：
- 网页下载的 Word/PPT/Excel 文件处理
- 文档统一格式化
- 为 MinerU 提供标准输入

## 安装配置

### 1. 自动安装（推荐）

使用脚本自动检测环境并安装 LibreOffice：

```bash
# 检查系统环境
python scripts/document_converter.py check-env

# 自动安装 LibreOffice
python scripts/document_converter.py install-libreoffice

# 强制重新安装
python scripts/document_converter.py install-libreoffice --force
```

**自动安装功能**：
- ✅ 自动检测操作系统（Windows/macOS/Linux）
- ✅ 自动检测系统架构（x86_64/arm64/mips 等）
- ✅ 检查是否已安装 LibreOffice
- ✅ 下载适合当前系统的安装包
- ✅ 自动执行安装
- ✅ 验证安装结果

### 2. 手动安装

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install libreoffice --no-install-recommends
```

#### macOS
```bash
brew install --cask libreoffice
```

#### Windows
下载并安装：https://www.libreoffice.org/download/

### 3. 验证安装
```bash
# 检查 LibreOffice 是否安装
python scripts/document_converter.py check-env

# 或使用命令行
soffice --version

# 或
libreoffice --version
```

### 4. 无需额外依赖
- 使用 LibreOffice 系统级安装
- Python 脚本通过 subprocess 调用
- 自动安装功能需要 `requests` 库（可选）

### 5. 系统要求

**支持的操作系统**：
- ✅ Windows (x86/x86_64)
- ✅ macOS (x86_64/arm64)
- ✅ Linux (x86_64/arm64/aarch64/mips)

**支持的架构**：
- ✅ x86 (32位)
- ✅ x86_64 (64位)
- ✅ arm64 (Apple Silicon / ARM64)
- ✅ aarch64 (ARM64)
- ⚠️ mips/mips64（需要手动安装）

## 支持格式

### 输入格式（转换为 PDF）

| 格式 | 扩展名 | 说明 | 转换质量 |
|------|--------|------|----------|
| Word | `.doc`, `.docx` | Microsoft Word 文档 | 优秀 |
| PowerPoint | `.ppt`, `.pptx` | Microsoft PowerPoint 演示文稿 | 优秀 |
| Excel | `.xls`, `.xlsx` | Microsoft Excel 表格 | 良好 |
| OpenDocument Text | `.odt` | LibreOffice 文本文档 | 优秀 |
| OpenDocument Spreadsheet | `.ods` | LibreOffice 表格 | 良好 |
| OpenDocument Presentation | `.odp` | LibreOffice 演示文稿 | 优秀 |
| Rich Text Format | `.rtf` | 富文本格式 | 良好 |
| Plain Text | `.txt` | 纯文本 | 良好 |
| HTML | `.html`, `.htm` | HTML 文档 | 良好 |

### 输出格式
- **PDF**：唯一输出格式，兼容 MinerU

## 使用边界

### 文件大小限制
- **推荐**：< 50MB
- **最大支持**：< 100MB（可能很慢）
- **超大文档**：建议分拆处理

### 文档复杂度

| 复杂度 | 描述 | 转换效果 |
|--------|------|----------|
| 简单 | 纯文本、基本格式 | 优秀 |
| 中等 | 图片、表格、基本样式 | 良好 |
| 复杂 | 复杂样式、宏、嵌入对象 | 中等 |
| 超复杂 | 复杂布局、特殊字体、VBA | 一般 |

### 功能限制

#### ❌ 不支持
1. 加密文档（需要先解密）
2. 受密码保护的文档
3. 包含宏的文档（宏会被移除）
4. 超大文档（>100MB）
5. 某些特殊字体（可能被替换）

#### ⚠️ 部分支持
1. 复杂表格布局（可能调整）
2. 嵌入对象（可能丢失）
3. 特殊效果（阴影、渐变等）
4. 自定义字体（可能被替换）

### 平台兼容性
- ✅ **Linux**：完美支持
- ✅ **macOS**：完美支持
- ✅ **Windows**：完美支持

## 性能限制

### 转换速度

| 文档类型 | 大小 | 转换时间 |
|---------|------|----------|
| Word 文档 | 1-5MB | 1-3 秒 |
| Word 文档 | 5-20MB | 3-10 秒 |
| PPT 演示文稿 | 1-10MB | 2-5 秒 |
| PPT 演示文稿 | 10-50MB | 5-15 秒 |
| Excel 表格 | 1-5MB | 1-3 秒 |
| Excel 表格 | 5-20MB | 3-8 秒 |

### 资源占用
- **CPU**：单核，50-100%
- **内存**：100-500MB
- **磁盘**：临时文件约等于源文件大小

### 并发限制
- **建议并发**：1-2 个
- **最大并发**：3 个（可能很慢）

## 使用示例

### 示例 1：转换单个 Word 文档
```bash
python scripts/document_converter.py convert \
  --input-file=./document.docx \
  --output-dir=./converted
```

**输出**：
```json
{
  "success": true,
  "input_file": "./document.docx",
  "output_file": "./converted/document.pdf",
  "input_format": ".docx",
  "output_format": ".pdf",
  "input_size": 1048576,
  "output_size": 786432,
  "compression_ratio": 0.75
}
```

### 示例 2：批量转换
```bash
python scripts/document_converter.py batch \
  --input-files=./doc1.docx ./doc2.docx ./doc3.pptx \
  --output-dir=./converted
```

### 示例 3：转换整个目录
```bash
python scripts/document_converter.py convert-dir \
  --input-dir=./documents \
  --output-dir=./converted \
  --recursive
```

### 示例 4：检测文件格式
```bash
python scripts/document_converter.py detect \
  --file-path=./unknown.xyz
```

### 示例 5：列出所有支持的格式
```bash
python scripts/document_converter.py list-formats
```

## 完整工作流示例

### 场景：下载并解析 Word 文档

```bash
# 1. 使用 Playwright 下载 Word 文档
python scripts/playwright_manager.py create
python scripts/browser_wrapper.py navigate \
  --url=https://example.com/document.docx
# 假设已下载到 ./document.docx

# 2. 转换 Word 为 PDF
python scripts/document_converter.py convert \
  --input-file=./document.docx \
  --output-dir=./converted

# 3. 使用 MinerU 解析 PDF
python scripts/mineru_service.py parse-pdf \
  --pdf-path=./converted/document.pdf \
  --output-format=markdown

# 4. 清理临时文件
rm -rf ./converted
```

### 场景：批量处理 PPT 文件

```bash
# 1. 批量下载 PPT 文件（Playwright）
# ... 省略下载步骤

# 2. 批量转换为 PDF
python scripts/document_converter.py convert-dir \
  --input-dir=./downloads \
  --output-dir=./converted \
  --recursive

# 3. 批量解析 PDF
python scripts/mineru_service.py batch-parse \
  --pdf-dir=./converted \
  --output-format=json

# 4. 关闭浏览器
python scripts/playwright_manager.py close
```

## 最佳实践

### 1. 文件预处理
```bash
# 对于超大文档，先分拆
# 使用其他工具将文档分拆为多个小文件
```

### 2. 错误处理
```python
result = converter.convert_to_pdf("document.docx")

if not result["success"]:
    if "过大" in result["error"]:
        print("文档过大，建议分拆处理")
    elif "不支持" in result["error"]:
        print("格式不支持，请检查文件类型")
```

### 3. 批量处理优化
```bash
# 限制并发数，避免资源耗尽
# 脚本内部已经实现串行处理，无需额外控制
```

### 4. 资源管理
```bash
# 及时清理临时文件
rm -rf .web-automation/converted
```

### 5. 转换后验证
```python
result = converter.convert_to_pdf("document.docx")

if result["success"]:
    pdf_size = result["output_size"]
    if pdf_size == 0:
        print("警告：生成的 PDF 为空")
```

## 常见问题

### Q1: 为什么转换失败？
**A**: 可能原因：
- LibreOffice 未安装或版本过旧
- 文件已加密或受密码保护
- 文件格式损坏
- 文件过大（>100MB）

**解决方法**：
```bash
# 检查 LibreOffice 安装
soffice --version

# 尝试手动转换
soffice --headless --convert-to pdf input.docx
```

### Q2: 转换速度很慢怎么办？
**A**: 优化方法：
- 减小文档大小（分拆处理）
- 关闭其他占用 CPU 的程序
- 使用 SSD 存储
- 避免批量转换，改为单文件转换

### Q3: 转换后的 PDF 格式不正确？
**A**: 可能原因：
- 源文档使用了特殊字体
- 源文档包含嵌入对象
- 源文档布局过于复杂

**解决方法**：
- 在源文档中替换特殊字体
- 尝试另存为其他格式（如 .doc 而非 .docx）
- 简化文档布局

### Q4: 能否批量转换？
**A**: 可以，支持两种方式：
```bash
# 方式 1：指定文件列表
python scripts/document_converter.py batch \
  --input-files=./doc1.docx ./doc2.docx

# 方式 2：指定目录
python scripts/document_converter.py convert-dir \
  --input-dir=./documents
```

### Q5: 如何处理加密文档？
**A**: LibreOffice 不支持转换加密文档。需要先解密：
```bash
# 使用其他工具解密（如 qpdf）
qpdf --decrypt --password="" encrypted.docx decrypted.docx

# 然后转换
python scripts/document_converter.py convert \
  --input-file=./decrypted.docx
```

## 与其他工具的集成

### 与 MinerU 集成
```bash
# 标准工作流
文档 → document_converter → PDF → MinerU → 结构化数据
```

### 与 Playwright 集成
```python
# 下载文档
await page.goto("https://example.com/document.docx")
download = await page.wait_for_download()
await download.save_as("document.docx")

# 转换文档
# 调用 document_converter.py
```

### 与 Python 脚本集成
```python
import subprocess
import json

# 转换文档
result = subprocess.run([
    "python", "scripts/document_converter.py",
    "convert",
    "--input-file", "document.docx"
], capture_output=True, text=True)

data = json.loads(result.stdout)
pdf_path = data["output_file"]
```

## 性能优化建议

1. **文档分拆**：超大文档分拆为多个小文件
2. **批量处理**：使用 batch 或 convert-dir 命令
3. **资源清理**：及时清理临时文件和缓存
4. **SSD 存储**：使用 SSD 提升转换速度
5. **限制并发**：避免同时转换多个大文档

## 注意事项

### 1. 首次运行
首次运行需要 LibreOffice 已安装，否则会报错。

### 2. 字体问题
如果源文档使用了特殊字体，转换后可能丢失或被替换。建议：
- 使用常见字体（Arial、Times New Roman 等）
- 在系统中安装所需字体
- 转换前检查字体兼容性

### 3. 嵌入对象
某些嵌入对象（如 Excel 表格、视频）可能无法正确转换。

### 4. 宏和 VBA
文档中的宏和 VBA 代码会被移除。

### 5. 临时文件
转换过程会产生临时文件，建议定期清理：
```bash
rm -rf .web-automation/converted
```

## 故障排除

### 问题：命令未找到
```bash
# 错误信息
soffice: command not found

# 解决方法
# Ubuntu/Debian
sudo apt-get install libreoffice

# macOS
brew install --cask libreoffice
```

### 问题：转换超时
```bash
# 错误信息
转换超时（超过 5 分钟）

# 解决方法
# 1. 检查文档大小
ls -lh document.docx

# 2. 分拆文档
# 3. 增加超时时间（需要修改脚本）
```

### 问题：PDF 为空
```bash
# 可能原因
# 1. 源文档损坏
# 2. 源文档为空
# 3. 转换过程中出错

# 解决方法
# 1. 用 LibreOffice 打开源文档，检查是否正常
# 2. 尝试另存为其他格式
# 3. 检查 LibreOffice 日志
```
