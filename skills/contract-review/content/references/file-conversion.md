# 文件读取与转换

> 合同审查 skill 必须先把用户上传的文件转成可分析的纯文本 + 原文片段定位，再走审查流程。这份参考说明各类格式的处理方式。

## 支持的输入格式

| 格式 | 扩展名 | 处理方式 |
|---|---|---|
| **DOCX** | `.docx` | 直接用 `python3 <docx_skill>/scripts/extract_docx_text.py` |
| **DOC**（老 Word 二进制） | `.doc` | 先用 `libreoffice --headless --convert-to docx` 转成 .docx，再走 DOCX 路径 |
| **PDF**（文字型） | `.pdf` | 用 `read` 工具带 `pages` 参数分页读取 |
| **PDF**（扫描件） | `.pdf` | 用 `pdf` skill 的 OCR 能力，OCR 后当文字处理 |
| **纯文本** | `.txt` / 粘贴文本 | 直接读 |
| **图片型** | `.png` / `.jpg` / `.jpeg` | 走多模态识别（图片理解能力），不要假设有 OCR |
| **HTML** | `.html` / `.htm` | 用 `pandoc -t markdown` 转纯文本 |

## 不支持的格式

| 格式 | 处理方式 |
|---|---|
| WPS 专用格式 `.wps` | 用 `libreoffice --headless --convert-to docx` 转 |
| Pages `.pages`（macOS） | `libreoffice --headless --convert-to docx`（部分版本可） |
| 加密 PDF | 让用户解密或提供 docx 版 |
| 损坏文件 | 让用户重新提供 |

## 标准流程

### 1. 探测文件类型

```bash
file <contract_file>
```

判断真实格式（不依赖扩展名，避免 .doc 实际是 .docx 之类）。

### 2. 按格式分流

**DOC / DOCX**（OOXML 容器）：
```bash
# .doc 先转 .docx
libreoffice --headless --convert-to docx \
    "/path/to/contract.doc" \
    --outdir /workspace/.tmp/ 2>&1 | tail -3

# 抽文字
python3 <docx_skill>/scripts/extract_docx_text.py /workspace/.tmp/contract.docx
```

**PDF**：
- 文字型：`read` 工具带 `pages`，例如 `pages: "1-5"`
- 扫描件：先 OCR（用 pdf skill 的 OCR 能力）
- 加密：让用户提供无加密版本

**纯文本 / 粘贴文本**：
- 直接使用。

**图片 / WPS / Pages**：
```bash
libreoffice --headless --convert-to docx <file> --outdir /workspace/.tmp/
# 然后走 DOCX 路径
```

### 3. 文本预处理

拿到纯文本后，做这些处理让后续审查更准：

- **保留原文段落结构**：不要把段落合并成单行，否则条款边界会糊掉。
- **标记表格**：表格内容按"行 / 列"维度保留，不要扁平化。
- **记录页码 / 章节位置**：DOCX 的章节标题（heading 1/2）要保留，PDF 的页码要标注。
- **修复 OCR 错字**：明显的 OCR 错误（如"亿" → "乙"、"甲" → "由"）在原文引用里修正，但不要改合同条款本身。

### 4. 缓存与复用

为避免重复转换，建议：

```bash
mkdir -p /workspace/.tmp
cp <user_upload> /workspace/.tmp/contract.<原扩展名>
# 转换产物也放这里
```

后续审查产生的报告写到 `/workspace/contract-review-<合同简称或日期>.md`。

## 失败处理

### `.doc` 转 `.docx` 失败

- `libreoffice` 不在 PATH：用绝对路径 `/usr/bin/libreoffice` 或 `/usr/bin/soffice`
- 报错"X11 display required"：加 `--headless`
- 报错"java not found"：warning 级别，可忽略
- 仍然失败：用 `pandoc <file.doc> -o contract.txt` 作为降级方案（pandoc 对 .doc 支持有限）

### `.docx` 读不出（损坏 / 加密）

- 提示用户重新提供无加密版
- 降级方案：用 `pandoc <file.docx> -t plain` 或 `unzip -p <file.docx> word/document.xml` 后正则提取文本

### PDF 文字层缺失（扫描件）

- 用 pdf skill 的 OCR 能力
- OCR 质量差时：让用户上传 docx 版
- OCR 仍读不出：列出已知可见内容，请求用户粘贴文本

### 文件超大（> 50 MB）

- 多页 PDF：分批读取（每次 ≤ 20 页）
- DOCX：直接用 extract_docx_text.py 不受限
- 卡顿：告知用户、给出预估时间

## 技巧：保留"原文片段定位"

审查报告里的每条引用都要让用户能"回查原文"。建议：

- DOCX：保留章节编号（如"4.1.3"）+ 段落前几个字
- PDF：保留页码 + 段落前几个字
- 表格：保留"行 / 列标识"

例如报告里写：
> **条款摘录**（4.1.3，第二段）：
> > 测试费用 200,000.00 元…首期支付 100,000.00…

让用户一眼能跳回原文核对。

## 工具版本基线

- `libreoffice` ≥ 7.0（处理 .doc / .docx / .wps / 部分 .pages）
- `pandoc` ≥ 2.10（DOCX / Markdown / HTML 互转）
- `python3-docx` 或 `python3 + zipfile + xml.etree`（DOCX 解析）
- 不要依赖 Microsoft Office 或 WPS Office（GUI 版，无法 --headless）

## 总结：审查者决策
1. 拿到文件 → 用 `file` 探测真实格式
2. 按格式分流：DOCX 直接读 / DOC 先转 / PDF 分页读
3. 抽文本 + 保留结构 + 标注位置
4. 缓存到 `.tmp/`，避免重复转换
5. 出错时按失败处理路径降级，不阻塞审查