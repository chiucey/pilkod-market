---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402207ed06fc677de3731c6f98beecf643d81e9eb48951c7a63ae2cebb29c9056a1ea02205b9121577bb23ae00291ec61948fd8456b248549952f52b9b60b91bb21158342
    ReservedCode2: 3046022100b279fb6a3a5d1fff69a60096376c8c891f1ba1102fb4486496fd06eaafc521740221008b67d47275232a92d1d6e72974969c8e7b24f8951eef55bbd1c65269179b162d
description: 从PPT单页中提取结构化信息。当用户提供PPT页面文本内容并要求提取标题、正文、公式、图表描述时使用。输出为标准化JSON格式，适合后续知识点拆解和分析。
name: ppt-page-extractor
---

# PPT单页信息提取器

## 任务描述

从PPT单页的原始文本中提取结构化信息，输出标准化JSON格式。专为minimax2.7模型优化，每次只处理一页PPT。

## 输入

用户提供PPT页面的文本内容（可以是OCR识别结果或直接复制的文本）。

## 输出格式

严格JSON格式，包含以下字段：

```json
{
  "page_index": 0,
  "title": "页面标题或空字符串",
  "sections": [
    {
      "type": "paragraph|formula|list_item|table",
      "content": "文本内容或公式内容",
      "level": 1
    }
  ],
  "formulas": [
    {
      "id": "formula_1",
      "content": "公式的完整LaTeX或文本表示",
      "inline": false,
      "referenced_in": ["paragraph_1"]
    }
  ],
  "images": [
    {
      "id": "image_1",
      "description": "图片的详细描述",
      "caption": "图片标题（如果有）",
      "referenced_in": ["paragraph_2"]
    }
  ],
  "tables": [
    {
      "id": "table_1",
      "headers": ["列1", "列2"],
      "rows": [["数据1", "数据2"]],
      "caption": "表格标题（如果有）"
    }
  ],
  "metadata": {
    "extraction_timestamp": "ISO8601时间戳",
    "has_title": true,
    "has_formulas": true,
    "has_images": true,
    "has_tables": true,
    "confidence_score": 0.95
  }
}
```

## 解析指令

### 1. 标题识别

- **优先级最高**：页面上最大的文本或第一行通常是标题
- **判断标准**：
  - 字体最大、加粗、居中的文本
  - 通常位于页面顶部
  - 长度通常<=50字符
- **命名规范**：使用`title`字段，若无标题则设为空字符串`""`

### 2. 正文分段

按内容类型分到不同section：

| type | 识别规则 | level说明 |
|------|---------|----------|
| paragraph | 普通段落文本 | 1=正文, 2=子段落 |
| formula | 数学公式、化学式 | 无level |
| list_item | 列表项（带符号或编号） | 1=一级, 2=二级, 3=三级 |
| table | 表格内容 | 无level |

### 3. 公式提取规则

**独立公式**（独占一行）：
- 提取到`formulas`数组
- `inline: false`
- 在原位置保留占位符引用

**行内公式**（嵌入段落中）：
- 提取到`formulas`数组
- `inline: true`
- 记录关联的paragraph id

**公式格式**：
- LaTeX格式优先
- 若无法确定，保留原文但添加`(raw)`标记
- 常见公式类型自动识别：
  - 分数：`\frac{a}{b}`
  - 上标：`x^{2}`
  - 下标：`x_{i}`
  - 根号：`\sqrt{x}`
  - 求和：`\sum_{i=1}^{n}`
  - 积分：`\int_{a}^{b}`

### 4. 图表描述生成

对于每个图片/图表：

1. **结构化描述**：
   - 类型（折线图、柱状图、流程图、照片等）
   - 主要元素（坐标轴、数据点、标签等）
   - 趋势或模式（如适用）
   - 颜色信息（仅当对理解重要时）

2. **描述模板**：
```
[类型]，[主要特征1]，[主要特征2]，[关键数据/趋势]。该图表用于说明[目的]。
```

3. **Caption识别**：
   - 图片下方或旁边的说明文字
   - 通常用"图X："或"Figure X:"开头

### 5. 表格处理

- 提取表头到`headers`
- 提取每行数据到`rows`
- 识别合并单元格并标注
- 提取表格标题（表格上方或"表X："开头的文字）

### 6. 元数据生成

- `has_*`字段：boolean，表示是否存在该类内容
- `confidence_score`：基于以下因素评估
  - 格式清晰度
  - 内容完整性
  - 公式识别准确度

## 约束条件

1. **严格JSON输出**：不得包含任何JSON之外的文本
2. **字段稳定性**：所有定义的字段必须存在，即使为空数组/对象
3. **UTF-8编码**：所有文本使用UTF-8
4. **无幻觉**：无法识别的内容标注`"confidence": "low"`或`"description": "无法解析的图片内容"`
5. **分页限制**：仅处理单页，若输入包含多页，提取第一页并标注`"page_index": 0`
6. **最小化输出**：不为空的内容省略字段值，仅保留空数组`[]`

## 错误处理

| 情况 | 处理方式 |
|------|---------|
| 无标题 | `"title": ""` |
| 无公式 | `"formulas": []` |
| 无图片 | `"images": []` |
| 无法解析图片 | `"description": "图片内容无法解析"` |
| 公式格式不确定 | `content`保留原文，添加`(raw)`后缀 |

## 示例

### 输入示例

```
机器学习基础

监督学习是从标记数据中学习预测模型的机器学习范式。

核心公式：
accuracy = \frac{TP + TN}{TP + TN + FP + FN}

分类器性能评估常用指标包括精确率、召回率和F1分数。

[图表：混淆矩阵示意图]
图1: 二分类混淆矩阵

| 预测正 | 预测负 |
| 真阳性 | 假阴性 |
```

### 输出示例

```json
{
  "page_index": 0,
  "title": "机器学习基础",
  "sections": [
    {
      "type": "paragraph",
      "content": "监督学习是从标记数据中学习预测模型的机器学习范式。",
      "level": 1
    },
    {
      "type": "paragraph",
      "content": "核心公式：[FORMULA_REFERENCE_1]",
      "level": 1
    },
    {
      "type": "paragraph",
      "content": "分类器性能评估常用指标包括精确率、召回率和F1分数。",
      "level": 1
    }
  ],
  "formulas": [
    {
      "id": "formula_1",
      "content": "accuracy = \\frac{TP + TN}{TP + TN + FP + FN}",
      "inline": false,
      "referenced_in": ["section_2"]
    }
  ],
  "images": [
    {
      "id": "image_1",
      "description": "2x2矩阵图，左上为真阳性(TP)，右上为假阳性(FP)，左下为假阴性(FN)，右下为真阴性(TN)。该图表用于说明二分类问题的预测结果分布。",
      "caption": "图1: 二分类混淆矩阵",
      "referenced_in": ["section_4"]
    }
  ],
  "tables": [],
  "metadata": {
    "extraction_timestamp": "2026-03-24T12:54:26Z",
    "has_title": true,
    "has_formulas": true,
    "has_images": true,
    "has_tables": false,
    "confidence_score": 0.92
  }
}
```

## 执行流程

1. 接收PPT页面文本
2. 识别并提取标题
3. 按行/段落分割内容
4. 识别公式并提取到独立数组
5. 识别图片引用并生成描述
6. 识别表格并结构化
7. 生成元数据
8. 输出完整JSON
