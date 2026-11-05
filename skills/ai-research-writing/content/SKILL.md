---
name: ai-research-writing
description: AI学术论文写作助手。当用户需要翻译润色学术论文、论文结构优化、实验图表生成、逻辑检查、去AI味、审稿视角分析、或需要中英文论文写作辅助时使用。支持NeurIPS/ICML/ICLR/ACL等顶会论文格式。
---

# AI Research Writing

Comprehensive AI-powered academic paper writing assistant for top-tier conferences.

## Core Workflow

### 1. Identify Writing Task Type

**Translation Tasks:**
- Chinese to English: Academic paper translation
- English to Chinese: Technical translation
- Chinese polishing: Word-based Chinese papers

**Polishing Tasks:**
- English paper polishing (NeurIPS/ICLR/ICML)
- Chinese paper polishing (核心期刊)
- Remove AI flavor for natural writing

**Structural Tasks:**
- Paper architecture diagrams
- Experiment visualization recommendations
- Figure/Table caption generation

**Analysis Tasks:**
- Experiment analysis paragraphs
- Logic consistency check
- Reviewer perspective simulation

### 2. Select Prompt Template

Based on task type, select appropriate template from references:
- `translation-prompts.md`: All translation scenarios
- `polishing-prompts.md`: Expression refinement
- `structural-prompts.md`: Diagrams and captions
- `analysis-prompts.md`: Logic and review

### 3. Execute with Context

Provide to AI:
1. Original text/paper content
2. Target conference/jourmal format
3. Any specific requirements

### 4. Review and Refine

Apply logic check before finalizing. Iterate if needed.

## Usage Examples

**Translate Chinese to English:**
```
Task: Translate abstract section
Input: [Chinese draft]
Format: NeurIPS LaTeX
Output: Polished English with LaTeX commands preserved
```

**Polish English Paper:**
```
Task: Deep polish for ICLR submission
Input: [Draft sections]
Focus: Zero-error, formal academic tone
Constraint: Preserve all LaTeX commands
```

**Generate Figure Caption:**
```
Task: Create caption for experiment comparison
Input: [Figure description]
Format: Top conference standard
Output: Title Case title + descriptive body
```

## Model Selection Guide

| Task | Recommended Model |
|------|------------------|
| Creative writing | Gemini-3-pro/flash |
| Code/experiments | Claude-4.5, Cursor |
| Translation polish | Claude-4.5, GPT-4 |

## Prompt Categories

### Translation Prompts
- 中转英 (Chinese→English)
- 英转中 (English→Chinese)
- 中转中润色 (Chinese→Polished Chinese)

### Polishing Prompts
- 英文论文润色
- 中文论文润色
- 去AI味 (Remove AI flavor)

### Structural Prompts
- 论文架构图 (Architecture diagram)
- 实验绘图推荐 (Chart recommendations)
- 图表标题生成 (Caption generation)

### Analysis Prompts
- 实验分析 (Experiment analysis)
- 逻辑检查 (Logic check)
- 审稿视角 (Reviewer perspective)

## References

- `references/translation-prompts.md` - All translation templates
- `references/polishing-prompts.md` - Polishing templates
- `references/structural-prompts.md` - Diagrams & captions
- `references/analysis-prompts.md` - Analysis templates
