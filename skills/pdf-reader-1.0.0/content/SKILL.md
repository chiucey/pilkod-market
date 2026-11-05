# PDF 内容读取与分析技能

## 技能信息
- **名称**: pdf-reader
- **版本**: 1.0.0
- **激活条件**: 用户提到"读取PDF"、"提取PDF内容"、"分析PDF"、"总结PDF"、"从PDF提取"、"PDF内容"

## 功能描述
读取、提取和分析 PDF 文件的内容，返回结构化的文字信息。

## 使用方法

### 方式一：PDF 文件（推荐截图法）

**本环境无法直接解析矢量PDF**，请按以下步骤操作：

1. 用 `images_understand` 工具读取 PDF 截图
2. prompt 模板：
   ```
   请详细提取这张图片中的所有文字内容，包括：
   1. 所有标题和正文文字（请逐段OCR）
   2. 表格内容（行列结构还原）
   3. 所有数字、参数、规格值
   4. 关键结论和数据
   ```

3. 若 PDF 过大或为多页，分段处理：
   - 先问用户"PDF 有几页？"
   - 每 3~5 页截一张图，分批分析

### 方式二：内嵌图片型 PDF
部分 PDF 是图片扫描件（含文字图片），直接用 `images_understand` 读取：
```
images_understand(image_info=[{"file": "/path/to/file.pdf.png", "prompt": "OCR提取"}) 
```

### 方式三：已提取文字的 PDF（文字型）
用 Node.js 提取 PDF 文本流中的可读字符串（适用于未加密的文字型 PDF）：
```javascript
const fs = require('fs');
const buf = fs.readFileSync('/path/to/file.pdf');
const str = buf.toString('binary');
// 查找可读文本块（PDF文本流）
const readable = str.replace(/[^\x20-\x7E\n]/g, ' ').replace(/\s+/g, ' ');
console.log(readable.substring(0, 3000));
```

## 注意事项
- **矢量型 PDF**：CAD/Visio图纸、矢量字体 PDF 无法直接读取，必须截图
- **多页 PDF**：逐页截图处理，每批 3~5 页
- **加密 PDF**：无法处理
- **扫描图片型 PDF**：直接用 `images_understand` OCR

## 输出格式
读取完成后，按以下结构返回：
- 文件基本信息（页数、大小、格式）
- 内容摘要（3~5句话）
- 详细章节内容（按原文档结构）
- 关键数据/参数表
- 表格内容（Markdown 格式）

## 限制与已知问题
| PDF 类型 | 本环境支持 | 解决方案 |
|:---|:---|:---|
| 矢量型（CAD图纸） | ❌ | 用户截图后用图片理解 |
| 图片扫描型 | ✅ | 直接 OCR |
| 文字型（未加密） | ✅ | Node.js 提取字符串或截图 |
| 加密型 | ❌ | 无法处理 |
| 表格式 PDF | ✅ | 截图后表格还原 |
| 含中文字型 | ⚠️ 部分 | 截图 OCR 最可靠 |

## 触发词
- "读取PDF"
- "提取PDF内容"
- "分析PDF"
- "总结PDF"
- "从PDF提取"
- "PDF内容"
- "帮我看看这个PDF"
- "PDF里说了什么"