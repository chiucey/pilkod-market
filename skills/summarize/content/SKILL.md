---
name: summarize
description: 多格式内容总结技能，支持URL、本地文件（PDF/图片/音频）、YouTube链接的核心内容总结。当用户要求"内容总结"、"URL总结"、"PDF总结"、"音频总结"、"YouTube总结"、"提取核心内容"、"自定义总结长度"、"JSON输出总结"时触发。支持适配主流AI模型（OpenAI/Anthropic/XAI/Google），支持总结长度自定义（短/中/长/自定义字符数）、仅提取内容、JSON结构化输出，适配信息提炼、快速阅读、数据化处理等场景。
---

# 多格式内容总结技能

## 技能职责

快速提取和总结多种格式的内容来源，输出适配不同模型和格式要求的总结结果。

## 支持的内容来源

| 来源类型 | 触发关键词 | 解析方式 |
|---------|-----------|---------|
| URL 网页 | "URL总结"、"总结这个网页" | 网页内容抓取 |
| PDF 文件 | "PDF总结"、"总结PDF" | PDF 文本提取 |
| 图片 | "图片总结"、"识别图片内容" | 图像理解 |
| 音频 | "音频总结"、"转录音频" | 音频转文字 |
| YouTube | "YouTube总结"、"视频总结" | 字幕/片段提取 |

## 执行流程

### 步骤 1：解析用户指令

解析输入，提取以下参数：
- **内容来源**：URL/文件路径/YouTube链接
- **总结长度**：`短`（100-200字）/ `中`（300-500字）/ `长`（800-1500字）/ `自定义`（指定字符数）
- **输出格式**：`普通文本`（默认）/ `JSON结构化`
- **模型选择**：OpenAI / Anthropic / XAI / Google Gemini（默认）

### 步骤 2：内容提取

根据来源类型选择提取方式：

```
URL → mcp__matrix__extract_content_from_websites
PDF → mcp__matrix__extract_pdfs_full_content
图片 → mcp__matrix__images_understand
音频 → mcp__matrix__audios_understand
YouTube → mcp__matrix__extract_content_from_websites (字幕页) 或 视频理解
```

### 步骤 3：内容总结

使用 AI 模型进行总结：

```javascript
// 总结提示词模板
const SUMMARY_PROMPT = {
  short: `请用100-200字简洁总结以下内容的核心要点：\n\n{content}`,
  medium: `请用300-500字总结以下内容的主要信息：\n\n{content}`,
  long: `请用800-1500字详细总结以下内容的完整内容：\n\n{content}`,
  custom: `请用约{char_count}字总结以下内容：\n\n{content}`
};
```

### 步骤 4：输出适配

根据用户选择的格式输出：

**普通文本输出**：
```
## 内容总结

[总结内容]

---
来源：{source}
长度：{length_type}
模型：{model}
```

**JSON 结构化输出**：
```json
{
  "summary": "总结内容",
  "source": "来源URL/文件路径",
  "source_type": "url|pdf|image|audio|youtube",
  "length_type": "short|medium|long|custom",
  "character_count": 500,
  "model": "google_gemini",
  "extracted_content": "仅提取模式时返回原始内容"
}
```

## 配置参数

| 参数 | 可选值 | 默认值 | 说明 |
|-----|-------|-------|------|
| length | short/medium/long/custom | medium | 总结长度 |
| format | text/json | text | 输出格式 |
| model | openai/anthropic/xai/google | google | AI 模型 |
| extract_only | true/false | false | 仅提取不总结 |

## 质量校验

- 确保总结覆盖原文核心信息
- 剔除冗余和重复内容
- 保持语义完整性
- 字符数误差控制在 ±10%

## 安全规则

- 文件解析限制：最大 200MB
- 敏感内容过滤：启用
- 仅执行总结操作：不执行内容修改或外部调用
