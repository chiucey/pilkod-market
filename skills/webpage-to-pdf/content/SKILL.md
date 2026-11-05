---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 492e2a99030ffb7f13f0f102919b9beb
    PropagateID: 492e2a99030ffb7f13f0f102919b9beb
    ReservedCode1: 3045022100b47d26e2bfc8e212a59ecefce02166ce5885837d7f54fe9dc8e2e974f3da1d1b022066c74b42e13775ba7543170765a45d666ba692e4b7f02cb7c8d1bc1c75337d12
    ReservedCode2: 304402200d2d17e5fc453fc483b12fc1a2c7c58d18fcdf43c17090f3934069cd564d3d6b0220324f68e2a0bbffd74f76d9c8aac6a19b43dc53079d1952619fdaa31084ad89f9
description: 将网页及其子页面逐级转换成PDF文件，支持将多个页面合并为单个PDF文档。当用户要求将网站页面、URL列表或网页层级结构转换为PDF文档时使用。支持指定遍历深度、CSS选择器、输出目录和PDF合并选项。
name: webpage-to-pdf
---

# 网页转PDF技能

将指定URL的网页及其子页面逐级转换为PDF文件，支持多页面PDF合并。

## 工作流程

### 步骤1：收集用户需求

使用交互式表单收集以下信息：

1. **起始URL**：要转换的网页地址（必填）
2. **最大深度**：遍历层级数（1-5，默认1）
3. **链接选择器**：CSS选择器，指定要跟踪的链接（如 `a[href^="/docs"]`）
4. **输出目录**：PDF保存路径（默认 `/downloads`）
5. **文件名模式**：`{title}`、`{url}`、或 `{index}`（默认 `{title}`）
6. **合并PDF**：是否将所有页面合并为单个PDF（是/否，默认否）

### 步骤2：获取并处理网页

对于每个URL：

1. 使用 `extract_content_from_websites` 获取页面内容
2. 提取页面标题用于文件名
3. 使用 `html_to_pdf` 将页面转换为PDF
4. 将生成的PDF路径添加到列表中

### 步骤3：递归处理子页面（如深度>1）

如果指定了深度>1：

1. 解析HTML中的链接
2. 根据选择器过滤相关链接
3. 对每个子链接递归执行步骤2
4. 维护已访问URL集合避免重复
5. 按发现顺序记录每个页面的PDF路径

### 步骤4：PDF合并（如启用）

如果用户选择合并PDF：

1. 使用Python的PyPDF2或pypdf库合并所有PDF
2. 按页面层级顺序（先父页面，后子页面）合并
3. 生成合并后的PDF文件，命名格式：`{起始URL标题}_merged.pdf`
4. 保存到指定输出目录

### 步骤5：保存并汇总

1. 将所有PDF保存到指定输出目录
2. 生成转换报告，包含：
   - 成功转换的页面数量
   - 失败的页面及原因
   - 单独PDF文件路径列表（如果未合并）
   - 合并后的PDF路径（如果启用合并）

## 输出格式

**未启用合并时**：
```
## 转换完成

**成功**: X 个页面
**失败**: Y 个页面

### PDF文件列表
- [页面标题1] → /path/to/file1.pdf
- [页面标题2] → /path/to/file2.pdf
...
```

**启用合并时**：
```
## 转换完成

**成功**: X 个页面已合并为单个PDF
**失败**: Y 个页面

### 合并PDF
- [合并文件名] → /path/to/merged_output.pdf

### 原始PDF文件（保留）
- [页面标题1] → /path/to/file1.pdf
- [页面标题2] → /path/to/file2.pdf
...
```

## PDF合并实现方式

使用Python脚本执行合并：

```python
from PyPDF2 import PdfMerger

merger = PdfMerger()
for pdf_path in pdf_list:
    merger.append(pdf_path)
merger.write(output_path)
merger.close()
```

## 错误处理

- **网络错误**：跳过该页面，记录到失败列表
- **无效URL**：跳过并提示用户
- **深度限制**：达到指定深度后停止递归
- **重复URL**：使用Set去重，避免循环访问
- **合并失败**：保留单独PDF，仅报告合并错误
- **空PDF列表**：跳过合并步骤，直接输出单独文件

## 限制说明

- 最大递归深度：5层
- 单次任务最大页面数：50个
- 支持的URL协议：http, https
- PDF使用A4纸张，默认边距
- 合并PDF最大页面数：500页
- 单独PDF文件默认保留，可选清理
