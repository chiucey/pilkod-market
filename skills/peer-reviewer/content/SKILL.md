---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a77c8a5ad7587f7a2809a5fd8d1ce919
    PropagateID: a77c8a5ad7587f7a2809a5fd8d1ce919
    ReservedCode1: 3046022100f20313aeb5cb9464cfce912fddd3cfe6ed78b8eb789219026d23d73ece2b284c022100aff82c4bb0aa5ddd50ee3abed911d63c99bd80cee1e014627e00a4f60bd0431c
    ReservedCode2: 30450220368b14aea2e2ef84978261b71cbbd0be22f5d11f910fcc0ee0814c6cb9902075022100b7f5f8db2ccf4dd701b9efd42b5aa381e4ec93571c52f7d2c2d7276c9a45cf9c
description: Professional academic peer reviewer skill. Use when users upload a PDF paper and select a review decision (Major/Minor Revision, Accept, Reject) to generate English peer review comments. Supports bilingual interaction, automatically extracts paper core information, and generates academically compliant professional feedback.
name: peer-reviewer
---

# Peer Reviewer Skill

## Overview

This skill generates professional English peer review comments for academic papers based on the provided review decision. The reviewer acts as an expert in the field, providing constructive, encouraging, or critical feedback depending on the decision.

## Workflow

### Step 1: Extract Paper Information

When a PDF is provided, use the `extract_pdfs_key_info` tool to extract:
- Full title
- Authors and affiliations
- Abstract and keywords
- Main sections (Introduction, Methods, Results, Discussion, Conclusion)
- Key findings and contributions

**Prompt template for extraction:**
```
Extract the full title, authors, abstract, keywords, and main sections including Introduction, Methods, Results, Discussion, and Conclusion. Also note the journal name if visible.
```

### Step 2: Confirm Review Decision

After extraction, present the user with a summary and ask for their review decision:

| Decision | Description | Tone |
|----------|-------------|------|
| Major Revision | Significant improvements required | Constructive |
| Minor Revision | Minor details to polish | Encouraging |
| Accept | Ready for publication | Highly positive |
| Reject | Fatal flaws present | Objective/Serious |

### Step 3: Generate Review Comments

Based on the decision, generate 5 numbered review comments following the format below:

**Opening Paragraph:** Summarize the paper's main contribution in 2-3 sentences.

**Review Comments 1-5:** Each comment should:
- Be specific and actionable
- Address methodology, clarity, completeness, or significance
- Match the tone appropriate to the decision

## Review Templates by Decision

### For "Minor Revision"

```
This paper presents [summary of contribution]. The authors [method/approach] and demonstrate [key findings]. The study addresses an important topic in [field] and provides valuable insights for [practical/theoretical application].

1. [Detail improvement on clarity/completeness]
2. [Specific suggestion for methodology refinement]
3. [Request for additional validation or sensitivity analysis]
4. [Clarification on assumptions or boundary conditions]
5. [Minor issues: notation consistency, grammar, formatting]
```

**Tone:** Encouraging, positive, emphasize near-publication quality

### For "Major Revision"

```
This paper investigates [topic] through [methodology]. While the research addresses a relevant problem in [field], there are significant concerns that must be addressed before publication.

1. [Major concern: fundamental methodological issue]
2. [Major concern: missing validation or insufficient data]
3. [Critical: unclear theoretical framework or assumptions]
4. [Critical: incomplete literature review or comparison]
5. [Important: insufficient discussion of limitations]
```

**Tone:** Constructive but serious, acknowledge value while pointing out needed improvements

### For "Accept"

```
This paper makes a significant contribution to [field] by [key innovation]. The methodology is sound, the results are compelling, and the implications for [area] are substantial. The authors have successfully addressed [research question/gap].

1. [Optional minor suggestion for further enhancement]
2. [Optional clarification on presentation]
3. [Optional note on broader impact]
```

**Tone:** Highly positive, summarize contributions, no required changes

### For "Reject"

```
This paper proposes [approach] for [problem]. However, after careful review, the manuscript has critical flaws that prevent it from meeting the standards for publication in this journal.

1. [Fatal flaw: fundamental methodological error]
2. [Fatal flaw: lack of novelty or insufficient contribution]
3. [Fatal flaw: incomplete validation or unsupported conclusions]
4. [Fatal flaw: significant gaps in literature or theory]
5. [Fatal flaw: data integrity or reproducibility concerns]
```

**Tone:** Objective, serious, clear about fatal defects

## Quality Standards

- All review comments must be in **English**
- Opening paragraph should be 2-3 sentences summarizing the paper
- Exactly **5 numbered comments** without sub-headings
- Comments should be specific, actionable, and constructive
- Avoid vague statements; provide concrete suggestions
- Match the appropriate tone for each decision type
- Use academic language and terminology

## Output Format

The final output should be a complete peer review document with:
1. Opening paragraph (2-3 sentences)
2. Five numbered review comments
3. Closing paragraph appropriate to the decision (optional)

## Edge Cases

- If no PDF is provided, ask the user to upload the paper
- If the paper content cannot be extracted, request clarification or ask for specific sections
- If the review decision is unclear, confirm with the user before proceeding