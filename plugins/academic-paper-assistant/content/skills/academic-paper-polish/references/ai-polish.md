# AI-Assisted Polishing Prompts

Ready-to-use prompts for polishing academic writing with ChatGPT or Claude.

## Contents

- [Core Strategy](#core-strategy)
- [Basic Polishing Prompts](#basic-polishing-prompts)
- [Advanced Prompts](#advanced-prompts)
- [Clarity-first template](#clarity-first-template)
- [Dimension-Specific Polishing](#dimension-specific-polishing)
- [Reusable instruction preset](#reusable-instruction-preset)
- [Quick Shortcut](#quick-shortcut)
- [Tool boundary](#tool-boundary)

---

## Core Strategy

1. Polish **section by section** first, then unify the overall style
2. Use **iterative refinement** when the first revision does not preserve the intended meaning
3. Use **different prompts** for different dimensions (see below)
4. Use the most capable available writing model when quality is critical

---

## Basic Polishing Prompts

Paste one of these before your paragraph:

```
Rewrite this paragraph in an academic language: [PARAGRAPH]

Paraphrase the text using more academic and scientific language. Use a neutral tone and avoid repetitions of words and phrases. [PARAGRAPH]

Improve the style of my writing? [PARAGRAPHS]

Improve the clarity and coherence of my writing [PARAGRAPHS]

Improve the organization and structure of my paper [PARAGRAPHS]

Can you improve this paragraph to make it more cohesive? [PARAGRAPH]

Give three variations of this sentence: [SENTENCE]
```

---

## Advanced Prompts

```
Analyze the text below for style, voice, and tone. Using NLP, create a prompt to write a new article in the same style, voice, and tone: [PARAGRAPHS]

Write a transition sentence to connect the following two paragraphs: [PARAGRAPH1] [PARAGRAPH2]

Provide effective transitions between paragraphs [PARAGRAPH1] [PARAGRAPH2]

Provide me a list of synonyms for [WORD/PHRASE] and evaluate them in the context of [PARAGRAPH]

Act as a language expert, proofread my paper on [TOPIC SENTENCE] while putting a focus on grammar and punctuation.

Proofread the following text for spelling and grammatical errors and rewrite it with corrections. [PARAGRAPHS]
```

---

## Clarity-first template

The source collection attributes the following pattern to 2024 guidance on AI-assisted writing. Treat it as a reusable prompt pattern, not as a verified quotation:

```
I'm writing a paper on [topic] for a leading [discipline] academic journal. What I tried to say in the following section is [specific point].
Please rephrase it for clarity, coherence and conciseness, ensuring each paragraph flows into the next. Remove jargon. Use a professional tone.
```

If the first output is unsatisfactory:
```
This isn't quite what I meant. Let's adjust this part.
```

---

## Dimension-Specific Polishing

Request targeted improvements by specifying which dimension to improve:

| Dimension | Instruction |
|---|---|
| **Precision** | 选择更精确的词汇，例如使用"generate"代替"produce"或"analyze"代替"look at" |
| **Conciseness** | 消除不必要的词语和短语，使句子更加清晰、直接 |
| **Objectivity** | 删除主观性语言，以中立的方式呈现信息 |
| **Specificity** | 提供更具体的细节，以支持论点或想法 |
| **Coherence** | 确保句子组织良好，逻辑流畅 |
| **Consistency** | 确保语言和风格与论文其余部分一致 |
| **Academic tone** | 使用学术写作中常用的术语，例如"furthermore"和"thus" |
| **Formal grammar** | 使用正确的语法和句法，避免句子碎片 |
| **Nuance** | 使用词语传达更复杂或微妙的含义 |

English version for direct use:
```
Please revise this paragraph to be:
- More precise: replace vague verbs with specific ones
- More concise: eliminate unnecessary words
- More objective: remove subjective language
- More academic in tone
[PARAGRAPH]
```

---

## Reusable instruction preset

Use this as a persistent instruction when the runtime supports one:

```
When tasked with rewriting or polishing content, preserve the original claim and provide alternative versions only when they express materially different academic nuances. The academic field is computer science.
```

---

## Quick Shortcut

In a new conversation, simply type:

```
polish: <your contents>
```

---

## Tool boundary

These prompts are model-agnostic. Do not upload confidential manuscripts to a third-party service or
use a retrieval tool without the user's permission. Any citation discovered externally must be opened,
verified against its primary source, and clearly distinguished from text supplied by the user.
