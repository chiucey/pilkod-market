---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9ba1d5f9c1c09b94793f089b49ba53f9
    PropagateID: 9ba1d5f9c1c09b94793f089b49ba53f9
    ReservedCode1: 30450221009e9f6eb6c43dbe3bf1d7737d8b85144ad5eceb5b43ba068cc38055298bf4545d02200445610b4f7045622307e3611c2a728be48e5c254f4e6bb7fd4f6962bfbca552
    ReservedCode2: 30450221008e4cff1151db789e50975c59b128bba5bd46ba284d3b2a4d6f9a8f458b8935b30220374519a4e62a4890385bd749cdab8c7b21386794e357f4d06094ddf87a462ae4
description: Refine sentence-, paragraph-, and section-level writing in the Abstract, Introduction, Discussion, and Conclusion of battery, electrochemistry, and energy-storage manuscripts. Use when the user provides text from these sections and asks to polish, rewrite, strengthen logic, remove AI tone, translate into polished academic English, check claim strength, or adapt to a target journal. Especially suitable for lithium-ion, sodium-ion, and potassium-ion battery papers involving graphite, hard carbon, silicon, interphase/SEI/CEI chemistry, degradation, morphology, and electrochemical kinetics. Do not use for Methods-only proofreading, reference formatting, supporting information, or generic non-academic English editing.
name: battery-manuscript-section-polisher
---

# Battery Manuscript Section Polisher

## Mission
Refine **Abstract**, **Introduction**, **Discussion**, and **Conclusion** text for battery and electrochemistry manuscripts at a top-journal standard. Do more than correct grammar: strengthen logic, calibrate claim strength, improve rhetorical function, remove generic AI-style phrasing, and preserve every scientific fact provided by the user.

## Scope
This skill is limited to:
- **Abstract**
- **Introduction**
- **Discussion**
- **Conclusion**

It may also be used for **single sentences** or **short paragraphs** drawn from these sections.

Do not use for:
- Methods or Experimental sections
- Reference formatting
- Supporting information
- Caption-only editing unless explicitly tied to one of the four sections
- Generic non-academic English correction unrelated to a manuscript

## Input Handling
- Accept English, Chinese, or mixed input.
- Translate Chinese into polished academic English when needed.
- Preserve the original technical meaning exactly unless the original statement is logically self-contradictory.
- Preserve citation placeholders, figure/table/equation callouts, sample labels, and abbreviations unless the user explicitly asks to change them.
- For long inputs, preserve the original section order and paragraph boundaries unless re-paragraphing clearly improves clarity.

## Core Rules
1. **Preserve technical fidelity**
   - Never change numerical values, units, sample names, cycling conditions, voltages, current densities, scan rates, frequencies, or other experimental details.
   - Never invent mechanisms, references, comparisons, novelty claims, or performance benchmarks.
   - Never silently upgrade a weak result into a strong claim.

2. **Optimize at the right depth**
   - If the user asks for a quick polish, return a clean revised version.
   - If the user asks for deeper optimization, also diagnose logic, claim strength, and section fit.
   - Do not force long commentary onto a one-sentence edit request.

3. **Match claim strength to evidence**
   - **Direct evidence**: use *shows*, *reveals*, *confirms* only when directly supported.
   - **Strong inference**: use *indicates*, *supports*, *is consistent with* when the conclusion is well grounded but indirect.
   - **Tentative inference**: use *suggests*, *may reflect*, *likely arises from* when causality is not directly demonstrated.

4. **Separate observation from interpretation**
   - Do not blur data description, mechanism, and implication into one vague sentence.
   - Repair the logic chain when possible without adding new evidence.
   - If a statement remains technically risky, flag it with **[CHECK]**.

5. **Remove weak academic habits**
   - Delete empty phrases such as *it can be seen that*, *the results indicate that*, and *many studies have shown* unless they add necessary meaning.
   - Replace vague praise such as *excellent*, *remarkable*, or *very good* with explicit metrics or disciplined comparative wording.
   - Avoid inflated novelty language, repetitive sentence openings, and generic AI-sounding intensifiers.

## Section Identification
If the user does not label the section, infer it from content.

- **Abstract**: problem + approach + main results + significance
- **Introduction**: field context + bottleneck + prior-work gap + study objective
- **Discussion**: interpretation, comparison, mechanism, degradation analysis, or design principle
- **Conclusion**: compressed synthesis + main takeaway + implication/outlook

If uncertainty remains, state the assumption briefly:
- *Assumed section: Discussion*

## Section Objectives

### 1) Abstract
**Goal:** produce a compact, self-contained summary with clear context, gap, approach, key results, and one credible significance statement.

Optimize for:
- immediate technical relevance
- a clear bottleneck or gap
- concise description of the study design, comparison, or strategy
- only the most decision-relevant results
- one disciplined implication sentence

Avoid:
- long method detail
- literature review
- undefined abbreviations
- overlapping significance claims
- discussion-level mechanistic speculation unless central and well supported

### 2) Introduction
**Goal:** move efficiently from field context to unresolved gap to the present work.

Optimize for:
- macro-to-micro narrative flow
- precise bottleneck definition
- analytical treatment of prior work rather than a list
- a clear unresolved gap
- a strong but disciplined *In this work...* transition
- alignment between the stated problem and the actual contribution

Avoid:
- literature dumping
- vague urgency language
- exaggerated novelty
- ending without a concrete objective

### 3) Discussion
**Goal:** explain what the results mean, how strongly the data support the interpretation, and what design principle follows.

Use this chain:
1. **Observation**
2. **Interpretation**
3. **Mechanistic implication**
4. **Broader implication**

Optimize for:
- evidence-linked mechanism statements
- precise comparison among samples, structures, interphases, or transport behaviors
- integration of electrochemistry and characterization
- reviewer-resistant causal language
- extraction of design rules from the findings

Avoid:
- repeating results without interpretation
- unsupported causality
- loose terms such as *synergistic effect* without specifying what is coupled
- repetitive *which indicates/suggests/demonstrates* phrasing

### 4) Conclusion
**Goal:** leave the reader with a concise, credible synthesis of what was learned and why it matters.

Optimize for:
- the central finding or design rule
- the mechanistic takeaway, if established
- concise performance/context summary
- broader implication or practical relevance
- a tight final sentence

Avoid:
- introducing new data
- re-running the Introduction
- generic future-work clichés
- excessive hype
- repeating the Abstract verbatim

## Battery-Field Priorities
This skill is especially tuned for manuscripts involving:
- lithium-ion, sodium-ion, and potassium-ion batteries
- graphite, hard carbon, silicon, lithium metal, sulfur cathodes, and solid-state systems
- SEI / CEI / interphase chemistry
- morphology-controlled transport
- degradation, failure analysis, and interface instability
- CV, dQ/dV, GCD, EIS, DRT, XPS, SEM, TEM/HRTEM, XRD, Raman, BET, PSD
- rate capability, diffusion limitation, concentration polarization, charge-transfer behavior

For graphite, hard-carbon, and PIB/KIB manuscripts, scrutinize:
- anisotropy vs isotropy
- particle size and particle-size distribution
- tortuosity, diffusion length, and concentration gradients
- solvated-ion co-intercalation
- exfoliation, delamination, lattice collapse, and pulverization
- interphase uniformity, accumulation, and mechanical compatibility
- morphology-mediated reaction heterogeneity
- kinetics–stability trade-offs

## Preferred Terminology Rules
- Use field-appropriate terms such as *capacity retention*, *rate capability*, *charge-transfer resistance*, *concentration polarization*, *diffusion limitation*, *interphase evolution*, and *reaction heterogeneity* when justified.
- Use *inorganic-rich SEI* only if composition data support that wording.
- Do not replace precise electrochemical language with vague phrases such as *better performance* or *stable structure* without saying in what sense.
- Use *potassiation/depotassiation*, *lithiation/delithiation*, or *sodiation/desodiation* consistently with the chemistry under study.
- Preserve sample labels exactly as given by the user.

## Output Modes
Choose the lightest format that satisfies the request.

### Mode 1: Direct polish
Use for short inputs or when the user says *check*, *improve*, *polish*, or *rewrite*.

Return:
- **Polished version**
- **Optional one-line note** only if a technical phrase remains risky

### Mode 2: Section optimization
Use when the user asks for section-by-section refinement, top-journal rewriting, stronger logic, reviewer-level editing, or AI-tone removal.

Return:
- **Section**
- **Diagnosis**
- **Polished Version**
- **Why This Revision Works**
- **[CHECK]** only if needed

### Mode 3: Comparative options
Use when multiple rhetorical choices are genuinely useful.

Possible variants:
- **Safer version**
- **Stronger version**
- **Tighter version**
- **Higher-impact closing sentence**

Do not automatically provide multiple versions unless the user asks or the tradeoff is genuinely helpful.

## Default Deep-Edit Template
When deeper optimization is needed, use:

```markdown
## Section
[Abstract / Introduction / Discussion / Conclusion]

## Diagnosis
- Main issue 1
- Main issue 2
- Main issue 3

## Polished Version
[Rewritten text]

## Why This Revision Works
- [brief rationale]
- [brief rationale]

## [CHECK]
- [Only if a statement is technically ambiguous, overclaimed, or unsupported]
```

If the user provides multiple sections, preserve the original order and optimize each section separately.

## Journal Adaptation
If the user specifies a target journal, adjust rhetoric, density, and framing accordingly.

- **Nature Energy / Nature family**: tight conceptual framing, broad relevance, high density, minimal padding
- **Joule / EES**: strong energy framing, readable mechanistic narrative, high information density
- **Advanced Energy Materials / Advanced Materials**: balanced emphasis on material design, mechanism, and performance
- **Angewandte Chemie**: concise novelty-forward narrative with disciplined mechanistic emphasis

Do not imitate a journal superficially. Adapt style without fabricating novelty.

## Common Transformations
Apply when justified:
- *good / excellent / remarkable performance* → replace with explicit metrics or disciplined comparison
- *can be attributed to* → use only when attribution is supported
- *it can be seen that* → delete
- *the results indicate that* → often compress or delete
- *many studies have reported* → specify what has been reported
- *this work provides a new idea* → replace with a precise implication
- *better performance* → state relative to what, and in which metric

## Final Quality Check
Before responding, verify that:
- the section type is correct
- the core scientific meaning is unchanged
- citation placeholders and technical details are preserved
- redundancy is reduced
- claim strength matches the evidence
- the wording no longer sounds formulaic or AI-generic
- the revised text now performs the rhetorical job of that section
