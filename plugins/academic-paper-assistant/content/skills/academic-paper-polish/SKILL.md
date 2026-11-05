---
name: academic-paper-polish
description: Polish and improve English wording for academic or research papers, especially in CS and ML. Use for language revision, section-specific phrasing, vocabulary, transitions, rebuttal wording, and requests to make supplied research prose clearer or more academic. Do not use this Skill as the primary workflow for medical bilingual abstract compression, peer review, or LaTeX typesetting.
---

# Academic Paper Polish

## Attribution

Original author: yzy (`yzy1996` on GitHub). Source:
https://github.com/yzy1996/English-Writing. The upstream repository did not declare a license when
this package was prepared; see the package-level `ATTRIBUTION.md` for provenance and changes.

Help the user write and polish English for academic research papers, with a focus on CS/ML fields. This Skill includes curated vocabulary, phrase banks, and section templates collected from published-paper usage.

## Scope and integrity

- Preserve the author's technical meaning, numbers, equations, citations, uncertainty, and claim strength.
- Never invent experimental results, references, methods, limitations, or evidence to make prose sound stronger.
- If wording is ambiguous, state the ambiguity or ask for the intended meaning before making a substantive change.
- Use `academic-abstract-refiner` for medical Chinese/English unstructured abstracts, `academic-paper-review` for evidence-based critique, and `academic-writing-latex` for templates or compilation.
- Treat the phrase banks as options, not claims. Strong terms such as “unprecedented” or “state of the art” require evidence in the supplied text.

## Workflow

When the user provides text to polish or asks for writing help:

1. **Identify the section** — determine which part of the paper (Abstract, Introduction, Related Work, Method, Experiment, Conclusion, Rebuttal) or ask if unclear
2. **Diagnose the issues** — look for: vague vocabulary, weak transitions, informal tone, lack of precision, repetitive sentence starters, missing evidence claims
3. **Apply improvements** using vocabulary and phrase banks in the reference files without changing the underlying claim
4. **Return the revision and a concise change note**; provide 2–3 alternatives only when the wording choice materially changes emphasis or nuance

## Section-Specific Guidance

Read `references/section-phrases.md` for ready-to-use sentence templates organized by paper section.

### Abstract (3-part structure)
- **Opening**: describe the problem/gap existing methods face — "Existing approaches face a dilemma...", "Despite the rapid advancement of..."
- **Middle**: describe your method and key innovations — "In this work, we present...", "A key part of our approach is..."
- **Closing**: show results — "Extensive experiments demonstrate that our framework significantly outperforms SOTA methods on..."

### Introduction (4-paragraph structure)
1. Background & motivation — "An explosively growing line of research...", "has enjoyed tremendous growth..."
2. Limitations of existing work — "The main drawback...", "prior attempts hamper...", "an inevitable problem..."
3. Your solution — "To address this, we propose...", "Motivated by this, we introduce..."
4. Contributions — "In summary, our contributions are:" followed by bullet points

### Related Work
- Group by sub-category, not chronologically
- "The most related works can be divided into... The first focuses on... The second..."
- Handle concurrent work: "The concurrently developed X. The central distinction between these and ours is that..."
- "Our method builds upon this line of research"

### Method
- Introduce the full framework first, then individual components
- "Our system consists of three major components: (1)... (2)... (3)..."
- For math notation: "where X denotes...", "we formulate this as..."
- "Specifically, our model first adapts... Then, we... Finally,..."

### Experiment
- Standard structure: Dataset → Baselines → Metrics → Quantitative Results → Qualitative Results → Ablations
- Use `w/` and `w/o` for ablation notation (with / without)
- Figure captions: bold the key phrase, e.g. "**Qualitative comparison** of our method against baselines."
- "We conduct extensive experiments to evaluate our model."

### Conclusion
- Sentence 1: "We present [method] for [task]."
- Sentence 2: "The key idea underpinning the proposed method is to..."
- Sentence 3: "Extensive experiments demonstrate that our method achieves state-of-the-art performance."
- Sentence 4: Future impact — "We hope this work brings us one step closer to..."

## Vocabulary & Phrases

Read `references/vocabulary.md` for curated vocabulary organized by use case:
- **Positive evaluation** (abstract/good concepts): unprecedented, phenomenal, intriguing, seminal, indispensable...
- **Positive evaluation** (concrete methods): ameliorate, synergistic, complementary, maturity...
- **Negative evaluation** (critiquing baselines): hamper, hinder, deficiency, deteriorate, inferior, vulnerable...
- **Difficulty vocabulary**: elusive, tackle, address, a remedy to...
- **Transitional connectors**: notably, in contrast, as a remedy, in tandem, meanwhile...
- **Quantity expressions**: a myriad of, plethora of, a wide range of...
- **Useful phrases**: off-the-shelf, on par with, in stark contrast to, take an orthogonal direction...
- **Domain-specific terms**: leverage, streamline, harness, empirically, agnostic, hallucinate (amodal)...

## Abbreviations & Latin Terms

| Abbreviation | Meaning |
|---|---|
| e.g. | for example |
| i.e. | that is / in other words |
| w.r.t. | with regard to |
| a.k.a. | also known as |
| etc. | and so forth |

Latin terms (*italicize*): *per se*, *de facto*, *vice versa*, *post hoc*, *ad-hoc*

## AI-Assisted Polishing

Read `references/ai-polish.md` for ready-to-paste prompts for ChatGPT/Claude polishing, including:
- A **clarity-first** prompt pattern attributed by the source collection to 2024 guidance
- System presets for consistent academic style
- Dimension-specific polishing: precision, conciseness, coherence, academic tone, formality

## Key Writing Principles

- **Academic tone**: prefer "generate" over "produce", "analyze" over "look at", "demonstrate" over "show"
- **Precision**: avoid vague claims; retain supplied specifics or request them when needed (for example, a measured PSNR change or training-time reduction)
- **Variety**: avoid repeating the same sentence opener; rotate transitions (notably / in contrast / more specifically / furthermore)
- **Evidence-backed claims**: support assertions with "experiments demonstrate...", "as shown in Fig. X..."
- **No fabricated support**: do not insert a metric, figure/table reference, citation, or comparison unless it exists in the supplied material
- **Active vs. passive**: use active voice for your contributions ("We propose..."), passive for results ("The model is trained on...")
- **Avoid these weak phrases**: "it can be seen that", "in order to", "due to the fact that" → replace with direct alternatives
