---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 2edf59480de7dbf54985f845127a9315
    PropagateID: 2edf59480de7dbf54985f845127a9315
    ReservedCode1: 3045022100865dc0657380c8b2a8a152b8845eb7343ce9b2d048d3810cbae3c3c4bd014f000220351887187bcadc6d75c394daa64b08a5811f3d14862519b1b6a79527d80ffab2
    ReservedCode2: 3045022100c8c7a247136a3bc2c543f3c86d57dc73f415930efa1d2d17e588960c3d692867022060036e75aeaf26695a2f13078776f79524b9de611e925e680c842bc9bb6d6fe1
description: 读取和解析 Office 文档（DOCX、XLSX）和 PDF 文件，提取纯文本内容。触发条件：用户上传、发送、读取、查看 .docx/.xlsx/.pdf 文件，或要求分析文档内容、提取文件信息、整理文档内容。当用户说"帮我读一下这个文件"、"看看这个文档里有什么"、"提取 PDF 内容"时使用此技能。
name: doc-reader
---

# doc-reader

读取 DOCX、XLSX、PDF 文件，提取结构化文本内容。

## 支持格式

| 格式 | 适用场景 | 依赖 |
|------|---------|------|
| .docx | Word 文档 | 标准库（zipfile + xml）|
| .xlsx | Excel 电子表格 | 标准库 |
| .pdf | PDF 文件 | pdfminer.six（系统已装则直接用）|

## 使用方法

### 快速读取

直接运行脚本，自动识别格式：

```bash
python3 /workspace/skills/doc-reader/scripts/read_doc.py <文件路径>
```

脚本会自动：
- 识别文件类型（按扩展名）
- DOCX：从 word/document.xml 提取所有段落文本
- XLSX：读取所有 Sheet，按 Tab 分隔输出（含表头）
- PDF：调用 pdfminer.six 提取文字图层（扫描件无文本则提示

### 返回格式说明

**DOCX**：纯文本，每段一行，空行分隔，保留原始段落结构。
**XLSX**：每个 Sheet 输出 `=== Sheet: 表名 ===` 头部，行内单元格用 Tab 分隔。
**PDF**：连续文本流，页眉页脚需后续清理。

### PDF 注意事项

- **可搜索 PDF** → 直接提取文本，效果好
- **扫描件（图片转PDF）** → 无文字图层，提取失败，提示用户
- 如需处理扫描件，使用 `images_understand` 工具截图识别

## 限制与已知问题

- XLSX 仅读取可见单元格内容，公式计算结果以缓存值返回
- DOCX 中的表格、图片、页眉页脚暂不包含
- PDF 依赖 pdfminer.six；如未安装可联系管理员安装：
  `pip3 install pdfminer.six`
