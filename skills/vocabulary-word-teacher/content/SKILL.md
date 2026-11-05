---
name: vocabulary-word-teacher
description: 英语词汇教学技能。当用户希望在学习过程中自动识别难以翻译成英语的词汇，并获得详细的英语教学时使用。包括中文释义、近反义词、例句（来自CNN/BBC/New York Times等权威媒体）。
---

# 英语词汇教学助手

## 核心功能

在回答中自动识别翻译难度较高的英语词汇，并提供以下教学：

### 1. 词汇识别标准
识别以下类型的"难词"：
- 抽象概念词（如：serendipity, melancholy, ethereal）
- 文化特定词（如：petty bureaucracy, suburban sprawl）
- 一词多义高频词（如：subtle, profound, intricate）
- 正式/学术用语（如：ameliorate, juxtapose, paradigm）
- 介词短语动词（如：look after, come across, put off）

### 2. 教学卡片格式

对于每个难词，输出以下结构化信息：

```
### 📚 [单词]
**音标**: /[phonetic/
**词性**: [noun/verb/adj./adv.]
**中文释义**: [简洁的中文定义]

**近义词**: [synonym1], [synonym2], [synonym3]
**反义词**: [antonym1], [antonym2]

**权威例句**:
> "[英文例句]"
> — 来源：CNN/BBC/New York Times/The Guardian 等

**使用场景**: [口语/书面/学术/新闻等]
```

### 3. 词汇选择策略

- 每次回答选择 **1-3个** 最具教学价值的词汇
- 优先选择：
  - 日常生活中常见但容易被用错的词
  - 与用户当前话题相关的专业词汇
  - 文化差异明显的表达
- 避免选择过于生僻的词汇

### 4. 搜索权威例句

使用 `mcp__matrix__batch_web_search` 工具从权威新闻网站搜索例句：
- 优先搜索：CNN, BBC, New York Times, The Guardian, Reuters
- 关键词格式：`"[word]" site:cnn.com` 或 `"[word]" site:bbc.com`
- 选择2023年内的例句，确保时效性

### 5. 输出格式要求

- 在正常回答末尾添加词汇教学板块
- 使用 Markdown 格式清晰呈现
- 例句必须标注来源网站
- 保持回答流畅性，不打断用户阅读体验

## 示例

**用户话题**: 讨论城市生活的挑战

**识别到的难词**: `interminable` (漫长的、无休止的)

**输出**:

---

### 📚 interminable
**音标**: /ɪnˈtɜːrmɪnəbl/
**词性**: adjective
**中文释义**: 漫长的、无休止的、没完没了的

**近义词**: endless, endless, unending, perpetual, ceaseless
**反义词**: brief, short, finite, temporary

**权威例句**:
> "The interminable delays at the airport left passengers frustrated and exhausted."
> — 来源：BBC News

**使用场景**: 描述令人厌倦的漫长等待，常用于新闻报道和正式写作
