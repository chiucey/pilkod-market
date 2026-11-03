# PDF 处理模块

## 目录
- [工作场景](#工作场景)
- [工作流程](#工作流程)
- [工作边界](#工作边界)
- [工作结果](#工作结果)
- [调用规范](#调用规范)

---

## 工作场景

需要处理 PDF 文档的场景：
- 解析 PDF 文档内容
- 提取 PDF 中的表格
- 分析 PDF 布局
- 转换 PDF 为其他格式
- 批量处理 PDF

---

## 工作流程

```
1. 读取 PDF 文件
   ↓
2. 使用 MinerU 引擎解析
   ↓
3. 执行提取（文本/表格/布局）
   ↓
4. 返回结构化数据
```

---

## 工作边界

### 能做
- 解析扫描版 PDF（需要 OCR）
- 提取高质量表格
- 分析文档布局
- 转换为 Markdown/JSON/HTML
- 批量处理 PDF
- 提取文档元数据

### 不能做
- 不能处理加密 PDF
- 不能处理损坏的 PDF 文件
- 不能提取图片中的文字（需要配合 OCR）
- 不能处理超大 PDF（内存限制）

---

## 工作结果

| 操作 | 成功结果 | 失败结果 |
|------|---------|---------|
| 解析 PDF | 返回 Markdown/JSON/HTML 格式 | PDF 文件不存在或解析失败 |
| 提取表格 | 返回结构化表格数据 | PDF 文件不存在或无表格 |

---

## 调用规范

### 1. 解析 PDF

#### 调用方法
```bash
python scripts/mineru_service.py parse-pdf
```

#### 触发条件
- 需要解析 PDF 文档
- 需要提取 PDF 内容
- 需要转换 PDF 格式

#### 调用格式
```
--pdf-path: [str] PDF 文件路径，必需
--output-format: [str] 输出格式，可选（markdown|json|html），默认 markdown
--ocr-enabled: [bool] 是否启用 OCR，默认 True
--extract-images: [bool] 是否提取图片，默认 False
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--pdf-path` | str | 是 | - | PDF 文件路径 |
| `--output-format` | str | 否 | markdown | 输出格式：markdown、json、html |
| `--ocr-enabled` | bool | 否 | True | 是否启用 OCR（扫描版 PDF） |
| `--extract-images` | bool | 否 | False | 是否提取图片 |

#### 结果说明

**成功**：返回解析后的内容

**失败**：PDF 文件不存在或解析失败，可能的原因：
- PDF 文件不存在
- PDF 文件损坏
- 内存不足
- PDF 加密

#### 结果格式

```json
{
  "status": "success|error",
  "message": "解析成功|错误信息",
  "content": "解析后的内容（Markdown/JSON/HTML）",
  "output_path": "输出文件路径",
  "metadata": {
    "page_count": 10,
    "title": "PDF 标题",
    "author": "作者",
    "creation_date": "2024-01-01"
  },
  "processing_time": 5.5
}
```

#### 数据流

```
PDF 文件 → MinerU 引擎 → 解析 → 返回结果
```

#### 示例

```bash
# 解析为 Markdown
python scripts/mineru_service.py parse-pdf \
  --pdf-path=./document.pdf \
  --output-format=markdown

# 解析为 JSON（禁用 OCR）
python scripts/mineru_service.py parse-pdf \
  --pdf-path=./document.pdf \
  --output-format=json \
  --ocr-enabled=False

# 解析并提取图片
python scripts/mineru_service.py parse-pdf \
  --pdf-path=./document.pdf \
  --output-format=html \
  --extract-images=True
```

---

### 2. 提取表格

#### 调用方法
```bash
python scripts/mineru_service.py extract-tables
```

#### 触发条件
- 需要从 PDF 提取表格
- 需要高质量表格数据

#### 调用格式
```
--pdf-path: [str] PDF 文件路径，必需
--output-format: [str] 输出格式，可选（markdown|json|csv），默认 markdown
```

#### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--pdf-path` | str | 是 | - | PDF 文件路径 |
| `--output-format` | str | 否 | markdown | 输出格式：markdown、json、csv |

#### 结果说明

**成功**：返回表格数据

**失败**：PDF 文件不存在或无表格，可能的原因：
- PDF 文件不存在
- PDF 中无表格
- 表格过于复杂

#### 结果格式

```json
{
  "status": "success|error",
  "message": "提取成功|错误信息",
  "tables": [
    {
      "page": 1,
      "caption": "表格标题",
      "headers": ["列1", "列2"],
      "rows": [
        ["数据1", "数据2"],
        ["数据3", "数据4"]
      ],
      "bbox": [x1, y1, x2, y2]
    }
  ],
  "table_count": 2,
  "processing_time": 3.2
}
```

#### 数据流

```
PDF 文件 → MinerU 引擎 → 表格检测 → 返回结果
```

#### 示例

```bash
# 提取为 Markdown
python scripts/mineru_service.py extract-tables \
  --pdf-path=./document.pdf \
  --output-format=markdown

# 提取为 JSON
python scripts/mineru_service.py extract-tables \
  --pdf-path=./document.pdf \
  --output-format=json
```

---

## 完整工作流示例

### 场景：下载并解析 PDF

```bash
# 1. 创建浏览器
python scripts/playwright_manager.py create

# 2. 导航到 PDF 页面
python scripts/browser_wrapper.py navigate \
  --url=https://example.com/document.pdf

# 3. 下载 PDF
python scripts/playwright_manager.py screenshot \
  --output-path=./document.pdf

# 4. 解析 PDF
python scripts/mineru_service.py parse-pdf \
  --pdf-path=./document.pdf \
  --output-format=markdown

# 5. 提取表格
python scripts/mineru_service.py extract-tables \
  --pdf-path=./document.pdf \
  --output-format=json

# 6. 关闭浏览器
python scripts/playwright_manager.py close
```

### 场景：批量处理 PDF

```bash
# 1. 解析多个 PDF
for pdf in ./documents/*.pdf; do
  python scripts/mineru_service.py parse-pdf \
    --pdf-path="$pdf" \
    --output-format=markdown
done

# 2. 提取所有表格
for pdf in ./documents/*.pdf; do
  python scripts/mineru_service.py extract-tables \
    --pdf-path="$pdf" \
    --output-format=json
done
```

---

## 注意事项

1. **内存管理**：处理大 PDF 时注意内存使用，避免同时处理多个文件
2. **OCR 性能**：启用 OCR 会显著增加处理时间
3. **表格质量**：复杂表格可能需要手动调整
4. **输出格式**：根据后续处理需求选择合适的输出格式
5. **加密 PDF**：不支持加密 PDF，需要先解密
