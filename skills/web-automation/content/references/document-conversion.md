# 文档转换模块

## 目录
- [工作场景](#工作场景)
- [工作流程](#工作流程)
- [工作边界](#工作边界)
- [工作结果](#工作结果)
- [调用规范](#调用规范)

---

## 工作场景

需要转换文档格式的场景：
- 将 Word 转换为 PDF
- 将 PPT 转换为 PDF
- 将 Excel 转换为 PDF
- 批量转换文档
- 检查转换环境

---

## 工作流程

```
1. 检查 LibreOffice 环境
   ↓
2. 调用 LibreOffice Headless 模式
   ↓
3. 执行格式转换
   ↓
4. 返回转换后的文件
```

---

## 工作边界

### 能做
- Word → PDF
- PPT → PDF
- Excel → PDF
- 其他 LibreOffice 支持格式 → PDF
- 批量转换
- 跨平台自动安装 LibreOffice

### 不能做
- 不能转换为其他格式（仅支持 PDF）
- 不能处理损坏的源文件
- 不能处理加密文件
- 不能保留宏（会被移除）

---

## 工作结果

| 操作 | 成功结果 | 失败结果 |
|------|---------|---------|
| 转换文档 | 返回 PDF 文件路径 | 源文件不存在或转换失败 |
| 环境检测 | 返回系统信息和 LibreOffice 状态 | - |
| 自动安装 | LibreOffice 安装成功 | 安装失败 |

---

## 调用规范

### 1. 环境检测

#### 调用方法
```bash
python scripts/document_converter.py check-env
```

#### 触发条件
- 需要检查 LibreOffice 是否安装
- 需要诊断转换环境
- 转换失败时排查问题

#### 调用格式
```
无参数
```

#### 结果说明

返回系统信息和 LibreOffice 状态

#### 结果格式

```json
{
  "system": {
    "os": "Linux",
    "arch": "x86_64",
    "platform": "Linux-5.15.0"
  },
  "libreoffice": {
    "installed": true,
    "version": "7.6.0",
    "executable_path": "/usr/bin/libreoffice",
    "headless_mode": true
  },
  "status": "ready|not_ready",
  "message": "环境就绪|LibreOffice 未安装"
}
```

#### 数据流

```
系统 → 环境检测 → 返回状态
```

#### 示例

```bash
# 检查环境
python scripts/document_converter.py check-env
```

---

### 2. 自动安装 LibreOffice

#### 调用方法
```bash
python scripts/document_converter.py install-libreoffice
```

#### 触发条件
- LibreOffice 未安装
- 需要重新安装 LibreOffice

#### 调用格式
```
--force: [bool] 强制重新安装，默认 False
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--force` | bool | 否 | False | 是否强制重新安装 |

#### 结果说明

**成功**：LibreOffice 安装成功

**失败**：安装失败，可能的原因：
- 网络问题
- 权限不足
- 平台不支持

#### 结果格式

```json
{
  "status": "success|error",
  "message": "安装成功|错误信息",
  "version": "7.6.0",
  "install_path": "/usr/bin/libreoffice"
}
```

#### 数据流

```
系统 → 下载 → 安装 → 返回结果
```

#### 示例

```bash
# 自动安装
python scripts/document_converter.py install-libreoffice

# 强制重新安装
python scripts/document_converter.py install-libreoffice --force
```

---

### 3. 转换单个文档

#### 调用方法
```bash
python scripts/document_converter.py convert
```

#### 触发条件
- 需要转换文档格式
- 需要生成 PDF

#### 调用格式
```
--input-file: [str] 输入文件路径，必需
--output-dir: [str] 输出目录，可选（默认 .web-automation/converted）
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--input-file` | str | 是 | - | 输入文件路径（Word/PPT/Excel 等） |
| `--output-dir` | str | 否 | .web-automation/converted | 输出目录 |

#### 结果说明

**成功**：返回 PDF 文件路径

**失败**：源文件不存在或转换失败，可能的原因：
- 源文件不存在
- 文件格式不支持
- LibreOffice 未安装
- 文件损坏

#### 结果格式

```json
{
  "status": "success|error",
  "message": "转换成功|错误信息",
  "input_file": "输入文件路径",
  "output_file": "输出 PDF 文件路径",
  "file_size": 12345,
  "conversion_time": 2.5
}
```

#### 数据流

```
源文件 → LibreOffice → 格式转换 → PDF 文件
```

#### 示例

```bash
# 转换文档
python scripts/document_converter.py convert \
  --input-file=./document.docx

# 指定输出目录
python scripts/document_converter.py convert \
  --input-file=./presentation.pptx \
  --output-dir=./output
```

---

### 4. 批量转换

#### 调用方法
```bash
python scripts/document_converter.py batch
```

#### 触发条件
- 需要转换多个文档
- 需要批量处理

#### 调用格式
```
--input-files: [str] 输入文件列表，必需
--output-dir: [str] 输出目录，可选（默认 .web-automation/converted）
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--input-files` | str | 是 | - | 输入文件列表（空格分隔） |
| `--output-dir` | str | 否 | .web-automation/converted | 输出目录 |

#### 结果说明

**成功**：返回所有转换结果

**失败**：部分或全部转换失败

#### 结果格式

```json
{
  "status": "success|error",
  "message": "批量转换完成|错误信息",
  "total": 5,
  "success": 4,
  "failed": 1,
  "results": [
    {
      "input_file": "file1.docx",
      "output_file": "file1.pdf",
      "status": "success",
      "conversion_time": 2.1
    }
  ],
  "failures": [
    {
      "input_file": "file2.pptx",
      "error": "文件损坏"
    }
  ],
  "total_time": 10.5
}
```

#### 数据流

```
多个文件 → LibreOffice → 批量转换 → 多个 PDF
```

#### 示例

```bash
# 批量转换
python scripts/document_converter.py batch \
  --input-files=./doc1.docx ./doc2.pptx ./doc3.xlsx

# 指定输出目录
python scripts/document_converter.py batch \
  --input-files=./doc1.docx ./doc2.pptx \
  --output-dir=./output
```

---

## 完整工作流示例

### 场景：文档转换后解析

```bash
# 1. 检查环境
python scripts/document_converter.py check-env

# 2. 转换文档
python scripts/document_converter.py convert \
  --input-file=./document.docx

# 3. 解析转换后的 PDF
python scripts/mineru_service.py parse-pdf \
  --pdf-path=./web-automation/converted/document.pdf \
  --output-format=markdown

# 4. 提取表格
python scripts/mineru_service.py extract-tables \
  --pdf-path=./web-automation/converted/document.pdf \
  --output-format=json
```

### 场景：批量转换

```bash
# 1. 批量转换所有文档
python scripts/document_converter.py batch \
  --input-files=./documents/*.docx ./documents/*.pptx

# 2. 批量处理所有 PDF
for pdf in ./web-automation/converted/*.pdf; do
  python scripts/mineru_service.py parse-pdf \
    --pdf-path="$pdf" \
    --output-format=markdown
done
```

---

## 支持的格式

### 输入格式
- Word: .doc, .docx, .rtf
- PowerPoint: .ppt, .pptx
- Excel: .xls, .xlsx
- 其他: .odt, .ods, .odp (LibreOffice 格式)

### 输出格式
- PDF: .pdf

---

## 注意事项

1. **权限要求**：Linux/macOS 需要 sudo 权限安装 LibreOffice
2. **路径权限**：确保输出目录有写入权限
3. **文件大小**：大文件转换可能需要较长时间
4. **兼容性**：某些复杂格式可能转换效果不佳
5. **宏处理**：宏会在转换过程中被移除
6. **字体支持**：确保系统有必要的字体
