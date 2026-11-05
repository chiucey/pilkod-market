---
name: academic-gpt
description: Academic paper writing assistant for research writing, paper review, literature polishing, translation, and academic tasks. Use when users ask for paper polishing, grammar checking, translation, peer review, literature analysis, abstract writing, PDF Q&A and other academic tasks.
---

# Academic-GPT 学术论文辅助系统

## 技能概述

Academic-GPT 是一个专业的学术论文辅助工具，整合了来自 GPT-Academic 项目和论文专用 Prompt 集合的最佳实践。该技能专注于帮助研究人员和学生完成以下核心任务：

- **论文润色**：英文/中文学术写作的语言优化
- **语法纠错**：拼写和语法错误的精准检测与修正
- **论文审稿**：专业的同行评审意见生成
- **文献翻译**：高质量的中英文学术翻译
- **结构优化**：段落逻辑与论文架构优化
- **摘要撰写**：中英文摘要的专业生成

---

## 核心功能模块

### 1. 英文论文润色

#### 基础英文润色
```
Below is a paragraph from an academic paper. Polish the writing to meet the academic style, improve the spelling, grammar, clarity, concision and overall readability. When necessary, rewrite the whole sentence. Furthermore, list all modification and explain the reasons to do so in markdown table.
```

#### 高级英文润色（中科院风格）
```
I want you to act as an expert in scientific writing, I will provide you with some paragraphs in English and your task is to improve the spelling, grammar, clarity, conciseness and overall readability of the text provided, while breaking down long sentences, reducing repetition, and providing improvement suggestions. You should use artificial intelligence tools, such as natural language processing and rhetorical knowledge and your expertise in effective scientific writing techniques to reply. Provide the output as a markdown table with the head in Chinese. The first column is the original sentence, and the second column is the sentence after editing and the third column provides explanation in Chinese, Make sure all text in third column in Chinese. Please edit the following text in a scientific tone:
```

#### SCI论文润色
```
I am preparing my SCI paper for submission and require assistance in polishing each paragraph. Could you please refine my writing for academic rigor? I need you to correct any grammatical errors, improve sentence structure for academic suitability, and make the text more formal where necessary. For each paragraph we need to improve, you need to put all modified sentences in a Markdown table, each column contains the following: Full original sentence; Highlight the revised part of the sentence; Explain why made these changes. Finally, Rewrite the full, corrected paragraph.
```

---

### 2. 中文论文润色

#### 基础中文润色
```
作为一名中文学术论文写作改进助理，你的任务是改进所提供文本的拼写、语法、清晰、简洁和整体可读性，同时分解长句，减少重复，并提供改进建议。请只提供文本的更正版本，避免包括解释。请编辑以下文本：
```

#### 带解释的中文润色
```
As a Chinese academic paper writing improvement assistant, your task is to improve the spelling, grammar, clarity, conciseness and overall readability of the text provided, while breaking down long sentences, reducing repetition, and providing improvement suggestions. Please provide only the corrected version of the text, with explanations. Provide the output as a markdown table, with each sentence in a separate row. The first column is the original sentence, and the second column is the sentence after editing, and the third column provides explanation in Chinese.
```

---

### 3. 语法拼写纠错

#### 英文纠错（仅纠错，不润色）
```
Can you help me ensure that the grammar and the spelling is correct? Do not try to polish the text, if no mistake is found, tell me that this paragraph is good. If you find grammar or spelling mistakes, please list mistakes you find in a two-column markdown table, put the original text the first column, put the corrected text in the second column and highlight the key words you fixed.

Example:
Paragraph: How is you? Do you knows what is it?

| Original sentence | Corrected sentence |
| :--- | :--- |
| How is you? | How are you? |
| Do you knows what is it? | Do you know what it is? |

Below is a paragraph from an academic paper. You need to report all grammar and spelling mistakes as the example before.
```

#### 详细中文解释纠错
```
Can you help me ensure that the grammar and spelling are correct? Do not try to improve the text, if no mistake is found, tell me that this paragraph is good. If you find grammar or spelling mistakes, please list the mistakes you find in a three-column markdown table, put the original text in the first column, put the corrected text in the second column, and highlight the key words you fixed, and give the explanation in bold for correction in Chinese.
```

---

### 4. 论文结构与逻辑优化

#### 段落逻辑连贯性分析
```
Please analyze the logic and coherence among sentences within each paragraph in the following text. Identify any areas where the flow or connections between sentences could be improved, and provide specific suggestions to enhance the overall quality and readability to the content.

Please only provide the text after improving and then give a list of the improvements in Chinese.
```

#### Nature期刊风格结构优化
```
I am a researcher studying [your field] and now trying to revise my manuscript which will be submitted to the journal of Nature. I want you to analyze the logic and coherence among sentences within each paragraph in the following text. Identify any areas where the flow or connections between sentences could be improved, and provide specific suggestions to enhance the overall quality and readability to the content. Please only provide the text after improving (the added or revised words or sentences should be highlighted in bold) and then give a list of the improvements in Chinese and do highlight the key words or sentences you fixed in bold. Please note that only highlight the words or sentences that was actually added or revised.
```

#### 中文论文结构优化
```
你是一名中文学术论文的结构优化专家。请根据下面提供的段落内容，优化论文的结构布局，确保每个部分都有清晰的主题句，并且关键点得到突出。同时，调整句子之间的逻辑关系，使得段落内的观点更加连贯。请注意使用专业术语，并在段落末尾提供一个简短的总结，概括本段落的核心观点。以下是待优化的段落：（插入段落内容）请在保持原意的基础上，提供一个结构更加清晰、逻辑更加严密的修订版本，并简要说明所做的主要修改。
```

---

### 5. 论文审稿

#### 通用审稿模板
```
Your task is to draft a high-quality review outline for a top-tier [field] journal for a submission titled "[paper title]", including sections like Abstract, Figures/Tables Captions, and Introduction. Compose a peer review starting with "Review outline:", covering "1. Significance and novelty", "2. Potential reasons for acceptance", "3. Potential reasons for rejection", and "4. Suggestions for improvement". For each section, list key reasons and provide at least two sub-bullet points to detail and support your arguments. Be specific, detailed, thoughtful, and constructive. Only outlines are required.
```

#### ML会议审稿（详细版）
```
Your task now is to draft a high-quality review outline for a top-tier Machine Learning (ML) conference for a submission titled "[paper title]":

Abstract: [abstract content]
Figures/Tables Captions: [captions]
Introduction: [intro content]

Your task:
Compose a high-quality peer review of an ML paper submitted to a top-tier ML conference on OpenReview.

Start by "Review outline:".
And then:
"1. Significance and novelty"
"2. Potential reasons for acceptance"
"3. Potential reasons for rejection",
List multiple key reasons. For each key reason, use **>=2 sub bullet points** to further clarify and support your arguments in painstaking details. Be as specific and detailed as possible.
"4. Suggestions for improvement",
List multiple key suggestions. Be as specific and detailed as possible. Be thoughtful and constructive. Write Outlines only.
```

---

### 6. 中英文学术翻译

#### 学术中译英
```
I want you to act as a scientific English-Chinese translator, I will provide you with some paragraphs in one language and your task is to accurately and academically translate the paragraphs only into the other language. Be conversational & empathetic. Ensure heterogeneous paragraphs. Ensure heterogeneous sentence lengths. And stick to primarily short, straightforward sentences. Also try to give the output with English writing logic. I want you to give your output in a markdown table where the first column is the original language and the second is the sentence after translating, and give each row only one sentence. Give the improvements as bullet points in Chinese in the end:
```

#### 中科院中译英风格
```
I want you to act as a scientific English-Chinese translator, I will provide you with some paragraphs in one language and your task is to accurately and academically translate the paragraphs only into the other language. I want you to give the output in a markdown table where the first column is the original language and the second is the first version of translation and third column is the second version of the translation, and give each row only one sentence.
```

#### 达到发表水平的中译英
```
I am a researcher studying [your field] and now trying to revise my manuscript which will be submitted to the journal of [target journal]. I want you to act as a scientific English-Chinese translator, I will provide you with some paragraphs in one language and your task is to accurately and academically translate the paragraphs only into the other language. I want you to give the output in a markdown table where the first column is the original language and the second is the first version of translation and third column is the second version of the translation, and give each row only one sentence. If you understand the above task, please reply with yes, and then I will provide you with the paragraphs.
```

---

### 7. 论文摘要撰写

#### 中英文摘要生成
```
Based on the provided paper content, please generate both Chinese and English abstracts following academic standards:

For Chinese Abstract:
- 背景（Research Background）
- 方法（Research Methodology）
- 结果（Key Results）
- 结论（Main Conclusions）

For English Abstract:
- Same structure with concise academic language
- Use appropriate academic terminology
- Keep within typical abstract length (200-300 words)

Please provide the following sections:
1. Title (with Chinese translation)
2. Authors' names (English)
3. First author's affiliation
4. Keywords (English)
5. Chinese Abstract
6. English Abstract
```

---

### 8. 论文完整审阅流程

```
Your role as a comprehensive paper reviewer:

1. **Initial Assessment**
   - Evaluate the significance and novelty of the research
   - Assess the motivation and problem formulation

2. **Methodology Review**
   - Examine the research design and experimental setup
   - Evaluate data collection methods and dataset characteristics
   - Assess analytical techniques and evaluation metrics
   - Judge the methodological rigor and appropriateness

3. **Results Analysis**
   - Verify the presentation of key findings
   - Assess the sufficiency of evidence
   - Evaluate the interpretation of results

4. **Writing Quality**
   - Check for logical coherence and clarity
   - Evaluate paragraph structure and transitions
   - Assess grammar, spelling, and academic tone

5. **Final Recommendations**
   - List strengths of the paper
   - Identify weaknesses and areas for improvement
   - Provide specific, constructive suggestions
   - Make recommendation (Accept / Minor Revision / Major Revision / Reject)

Please structure your review as follows:
- Summary
- Major Concerns
- Minor Concerns
- Detailed Comments (by section)
- Recommendation
```

---

## 输出格式规范

### 润色输出格式
```markdown
| 原文 | 修改后 | 修改说明 |
| :--- | :--- | :--- |
| [原始句子] | [修改后句子] | [中文解释] |
```

### 审稿输出格式
```markdown
# Review Outline

## 1. Significance and Novelty
- [Key point 1]
  - [Supporting detail 1]
  - [Supporting detail 2]
- [Key point 2]
  - [Supporting detail 1]
  - [Supporting detail 2]

## 2. Potential Reasons for Acceptance
...

## 3. Potential Reasons for Rejection
...

## 4. Suggestions for Improvement
...
```

---

## 适用场景示例

| 场景 | 推荐使用的功能模块 |
| :--- | :--- |
| 准备投稿SCI论文 | 英文润色 + 语法纠错 + 结构优化 |
| 审阅同行论文 | 论文审稿（完整流程） |
| 中译英论文 | 学术翻译（发表级别） |
| 快速检查语法 | 语法拼写纠错 |
| 撰写摘要 | 摘要撰写 |
| 分析论文逻辑 | 段落逻辑优化 |
| 初稿润色 | 高级英文润色（中科院风格） |

---

## 使用注意事项

1. **上下文提供**：进行润色时，尽量提供完整的段落或章节，而非单个句子，以获得更准确的上下文理解

2. **学术领域说明**：如果涉及特定学科的专业术语，请在请求时说明研究领域

3. **目标期刊**：对于投稿级别的润色，建议说明目标期刊名称，以获得更匹配的学术风格

4. **迭代优化**：对于重要的论文，建议进行多轮润色：语法检查 → 基础润色 → 结构优化 → 最终审校

5. **中英混用**：在处理中英混用的论文时，请明确指出需要保持原文的专业术语

---

## 版本信息

- **技能版本**：1.0
- **数据来源**：GPT-Academic 项目 + 论文专用 Prompt 集合
- **最后更新**：2026-03-28
