---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5c90d65b4e853fbef75024417a20d8d3
    PropagateID: 5c90d65b4e853fbef75024417a20d8d3
    ReservedCode1: 3046022100fc783f2f0d1c023fe3adc0864b5b2008838c9a7bd3d260a4284f955e17e5f0ce022100cea95113ae6ed40c343d48b9f7f80a394f75558f8f92c102849c0bf884ad3911
    ReservedCode2: 30450220562e94ecc4ed953567ca93fb06b75f7b5b617d74b655838e40cae1cf21fdf3710221009ff8f2e0a72b37258c344cdf41b4ff991a69becafa7ddc3e055cb98f059f96ad
description: 'Generate simulated peer review comments (评审意见) for Chinese National Natural Science Foundation (NSFC / 国家自然科学基金) grant proposals. Produces structured review comments from 7 simulated reviewers across 5 standardized evaluation dimensions, formatted as plain-text DOCX matching the official NSFC review output style. Use when: (1) User uploads or describes an NSFC grant proposal and asks for review comments or evaluation, (2) User wants potential 评审意见 or peer review feedback for a 国家自然科学基金申请, (3) User asks to evaluate, critique, or review a Chinese scientific grant application from a reviewer''s perspective, (4) User wants simulated expert reviews for grant proposal preparation, (5) User requests review opinion compilation (评审意见汇总) for an NSFC proposal.'
name: nsfc-grant-review
---

# NSFC Grant Proposal Review Skill

## Overview

Simulate the NSFC peer review process by generating structured review comments from
7 expert reviewers. The output is a plain-text DOCX document with no special formatting,
matching the official NSFC review comment compilation style.

## Reference Files

- **SOTA analysis**: `references/sota_analysis.md` — Style and structure contract
  extracted from the reference document.
- **Review framework**: `references/review_framework.md` — 5 review dimensions,
  tone guidelines, sentence patterns, and reviewer profile guidance.

Read `references/sota_analysis.md` first for output format requirements.
Read `references/review_framework.md` for review content generation guidance.

## Reference Source and Output Policy

- **Reference source type**: Uploaded artifact (DOCX)
- **Reference artifact type**: DOCX
- **Reference File Type**: DOCX
- **Supported outputs**: DOCX (default), PDF
- **Default output**: DOCX when user requests a document artifact
- **Language**: Chinese (formal academic), English for technical terms

## Style Contract (CRITICAL — Must Follow Exactly)

The reference document is a **plain-text document with absolutely no formatting**.
The output MUST adhere to these constraints:

1. **No bold text** anywhere in the document
2. **No headers or footers** — no page numbers, no document title banners
3. **No centered title block** — title is inline plain text
4. **No horizontal separators or lines**
5. **No custom styles** — use Normal style throughout
6. **No tables, charts, or graphics**
7. **Font**: SimSun (宋体) or similar CJK serif font for Chinese text; Liberation Serif
   or similar serif for Latin text. Standard body size (10.5-12pt).
8. **Line spacing**: ~1.5x
9. **Color**: Black text on white background only

### Document Layout

```
[Title line in plain text]: 项目名称  申请人  依托单位  项目类别  "<1>具体评价意见：

一、请评述申请项目研究选题的创新性。请详细阐述判断理由。
[1-3 sentences of review]

二、请评述申请项目所提出研究问题的科学价值以及是否可推动某些学科领域或者科学前沿取得突破。
[1-3 sentences of review]

三、请评述申请项目研究方案的可行性；如有可能，请对完善研究方案提出建议。
[1-3 sentences of review]

四、请评述研究队伍构成、研究条件和与本项目相关的前期工作基础。
[1-3 sentences of review]

五、其他建议
[1-3 sentences, or "无" if none]

<2>具体评价意见：
[same 5 dimensions for reviewer 2]
...
<7>具体评价意见：
[same 5 dimensions for reviewer 7]
```

**Note**: The title line contains project metadata as plain text separated by spaces/tabs,
immediately followed by `"<1>具体评价意见：` with no line break before the first reviewer.

## Structure Contract

### Must Include Exactly 7 Reviewers

The output MUST contain exactly 7 reviewers, labeled `<1>` through `<7>`.
This is non-negotiable. Each reviewer covers all 5 dimensions.

### Five Standard Dimensions (Fixed Order)

1. **一、请评述申请项目研究选题的创新性。请详细阐述判断理由。**
2. **二、请评述申请项目所提出研究问题的科学价值以及是否可推动某些学科领域或者科学前沿取得突破。**
3. **三、请评述申请项目研究方案的可行性；如有可能，请对完善研究方案提出建议。**
4. **四、请评述研究队伍构成、研究条件和与本项目相关的前期工作基础。**
5. **五、其他建议**

### Comment Length

Each dimension comment must be **1-3 sentences** only. Be concise. Do not expand
or embellish. Typical length: 30-120 Chinese characters per dimension.

## Workflow

### Step 1: Extract Proposal Information

Read and analyze the user's grant proposal to extract:

1. **Project title** (项目名称)
2. **Applicant** (申请人) and institution (依托单位)
3. **Project type** (项目类别): e.g., 重点项目, 面上项目, 青年基金
4. **Research background** and scientific problem
5. **Core hypothesis** and novel claims
6. **Technical approaches**, cell lines, animal models, methods
7. **Preliminary data** and prior publications mentioned
8. **Team composition** and applicant qualifications
9. **Key genes, proteins, diseases, pathways** involved

### Step 2: Generate 7 Reviewer Comments

Generate reviews from **exactly 7** simulated reviewers with varied perspectives:

| Reviewer | Profile | Typical Stance |
|----------|---------|---------------|
| <1> | Supportive generalist | Generally positive, minor concerns |
| <2> | Critical methodologist | Balanced, focuses on experimental issues |
| <3> | Rigorous cell biologist | Detailed technical critiques |
| <4> | Field expert | Evaluates novelty vs published work |
| <5> | Moderate evaluator | Balanced, fair assessment |
| <6> | Harsh skeptic | Highly critical, emphasizes weaknesses |
| <7> | Constructive expert | Supportive but with specific suggestions |

### Step 3: Content Fidelity Rules (CRITICAL)

Every review comment MUST:
- Reference **specific elements from the proposal** (genes, proteins, cell lines,
  methods, diseases, publications) — never invent or substitute
- If the proposal mentions "293T cells", the review must say "293T cells", not
  invent other cell lines
- If the proposal cites "Signal Transduction And Targeted Therapy", use that
  exact journal name, not a different one
- If the proposal studies "albumosome/albumin body", reference that structure
- Do NOT fabricate: specific gene names, experimental methods, paper citations,
  or technical details not present in the proposal
- Do NOT use generic filler text — every sentence must be specific to the
  proposal under review
- Balance positive and negative aspects realistically per reviewer's profile

### Step 4: Format the Output Document

Create a DOCX document with:
- **Only Normal style** applied throughout
- **No bold**, no italics, no underline, no color changes
- **No headers, footers, page numbers**
- Title line as plain text at the very beginning
- 7 reviewer sections in sequence
- Each dimension header as plain text (not bold)
- Comments in plain text, 1-3 sentences each

## Reviewer Stance Distribution

Across 7 reviewers, maintain this approximate distribution:
- 2 reviewers: Generally supportive (more positives)
- 3 reviewers: Balanced (mixed positives and negatives)
- 2 reviewers: Critical (more negatives, including one highly critical)

This simulates a realistic peer review panel with diverse expert opinions.

## Content Quality Checklist

Before finalizing, verify:
- [ ] Exactly 7 reviewers (<1> through <7>)
- [ ] All 5 dimensions present for each reviewer
- [ ] Each comment is 1-3 sentences
- [ ] Comments reference actual proposal content (genes, methods, models)
- [ ] No fabricated technical details
- [ ] No formatting (bold, headers, footers, separators)
- [ ] Title line uses plain text format
- [ ] "五、其他建议" is "无" when reviewer has no additional suggestions
- [ ] Language is formal academic Chinese with English for technical terms
