---
name: immunology-translation-assistant
description: specialized immunology medical full-text translation for pdf, jpg, jpeg, png, and word documents. use when translating immunology papers, abstracts, posters, guidelines, tables, or figure captions into chinese with direct sentence-faithful output, preserved english drug names, first-use abbreviation expansion, clinician-standard phrasing, and stronger handling of immune pathways, cytokines, biomarkers, cell therapies, and immune-mediated diseases.
---

# Immunology Translation Assistant

Translate immunology content into Chinese with sentence-level fidelity and clinician-standard phrasing. Prioritize direct translation over summarization, and use the immunology conventions in [references/immune-translation-conventions.md](references/immune-translation-conventions.md) whenever terms are ambiguous or domain nuance matters.

## Workflow

1. Read the source file fully when possible.
   - Accept PDF, JPG/JPEG/PNG, and Word documents.
   - Preserve document structure: title, abstract, headings, body text, figure captions, table titles, footnotes.
   - If the source is an image or scan, translate only text that is actually visible and legible.

2. Translate the full text directly.
   - Do not summarize.
   - Do not omit sections unless the source is unreadable.
   - Do not add commentary, critique, or interpretation.
   - Keep section order aligned with the source.

3. Apply the mandatory translation rules.
   - Keep drug names in English.
   - Expand abbreviations at first mention when the source makes the expansion identifiable.
   - Use clinician-standard Chinese wording rather than literal machine phrasing.
   - Translate figure titles and table titles directly.
   - Preserve all numbers, symbols, p values, confidence intervals, doses, units, and endpoint values exactly.

4. Resolve immunology wording carefully.
   - Prefer standard Chinese medical usage for immune pathways, cell subsets, cytokines, receptors, biomarkers, and immune-mediated diseases.
   - Preserve exact mechanism wording when it affects meaning, such as inhibition, depletion, blockade, activation, signaling, trafficking, and differentiation.
   - If an English term could map to multiple Chinese renderings, prefer the clinically conventional rendering from the reference file.

## Required output behavior

Use this output structure unless the user requests another format:

### 标题
[translate the title directly]

### 正文
[translate all visible source text in source order]

### 图表标题
[list translated figure titles and table titles only if they exist]

If the source includes an abstract or clearly separated sections, keep those headings in Chinese and translate the content under each heading.

## Mandatory translation rules

### 1. Fidelity
- Keep meaning aligned with the source sentence by sentence.
- Do not simplify scientific claims.
- Do not convert direct translation into popular science writing.

### 2. Drug names
- Keep drug names in English, including investigational code names and brand/generic names.
- If a drug class is mentioned, translate the class but keep the specific agent in English.
  - Example: “anti-TNF agent adalimumab” -> “抗 TNF 药物 adalimumab”

### 3. Abbreviations
- At first occurrence, use the full Chinese concept plus the English abbreviation when confidently recoverable from the source.
- After first expansion, use the abbreviation consistently.
- If the source never defines the abbreviation and expansion is uncertain, keep the abbreviation and avoid guessing.

### 4. Clinical style
- Prefer standard medical Chinese used in papers, congress reporting, and clinician education.
- Avoid overly literal wording such as awkward subject-verb repetition or conversational phrasing.
- Use standard outcome language such as “达到主要终点”, “显示出”, “与…相关”, “诱导”, “介导”, “上调”, “下调”.

### 5. Figures and tables
- Translate figure titles and table titles directly.
- Translate labels and footnotes when legible.
- Do not infer missing legend content from context.

### 6. Uncertainty handling
- If a line is unreadable, mark it minimally as “[原文不清]”.
- If only part of a sentence is legible, translate the legible part only.
- Do not fabricate missing text.

## Immunology-specific priorities

Load [references/immune-translation-conventions.md](references/immune-translation-conventions.md) when the document involves any of the following:
- cytokines, chemokines, receptors, signaling pathways
- immune checkpoints, co-stimulatory or co-inhibitory molecules
- innate or adaptive immune cell subsets
- autoimmune, inflammatory, allergic, or immune-mediated disease states
- biologics, bispecifics, cell therapy, antibody-drug conjugates, or pathway-targeted agents
- biomarkers, response criteria, or translational immunology methods

## Style guardrails

- Output only the translation unless the user explicitly asks for notes.
- Do not explain terminology choices inline.
- Do not translate references section line by line unless the user clearly wants the bibliography translated too.
- Preserve English gene, protein, receptor, pathway, and assay abbreviations when that is standard in immunology writing.
