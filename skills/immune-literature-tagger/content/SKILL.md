---
name: immune-literature-tagger
description: "tag and split immunology-related medical literature into source-traceable knowledge cards, then output a structured excel workbook. use when the user uploads pdf papers, abstracts, guidelines, reviews, meta-analyses, clinical studies, or regulatory documents and asks to classify, label, card-split, summarize, extract evidence, or map content into disease background, market demand, promotion strategy, product evidence chain, competitor analysis, and law/regulation modules."
---

# Immune Literature Tagger

## Purpose

Convert uploaded immunology-related literature PDFs into reusable, source-traceable knowledge cards with standardized tags, risk flags, and Excel output. Prioritize cards that can support physician PPTs, medical DA, patient education, internal training, competitive intelligence, and evidence-chain summaries.

## Required Output

Always produce an `.xlsx` workbook unless the user explicitly asks for another format in addition to Excel. Each workbook must include at least these sheets:

1. `Knowledge_Cards` — one row per knowledge card.
2. `Tag_Summary` — counts by level-1 and level-2 tags, review flags, and card type.
3. `Source_Map` — PDF/page/section/table/figure traceability.
4. `Review_Checklist` — medical, compliance, traceability, and patient-facing adaptation checks.
5. `Instructions` — short note explaining how to read and filter the workbook.

Use the schema in `references/excel-schema.md`. Use the tag framework in `references/tag-taxonomy.md`. Use the extraction and QA rules in `references/extraction-rules.md`.

## Workflow

### 1. Ingest the PDF

Read the uploaded PDF. Extract title, journal/source, year, DOI/PMID if available, article type, abstract, methods, results, discussion, figures, tables, supplements, and references when accessible.

If the PDF text is incomplete, inspect pages visually where needed. Do not use OCR unless there is no other viable option.

### 2. Classify the article

Assign one primary article type:

- Basic research: animal, in vitro, organoid, mechanism, target validation.
- Clinical research: RCT, cohort, case-control, cross-sectional, real-world, diagnostic, prognostic.
- Evidence synthesis: systematic review, meta-analysis, network meta-analysis, umbrella review.
- Review: narrative review, expert review, state-of-the-art review.
- Guideline/consensus/policy: guideline, recommendation, position statement, regulatory/policy update.
- Translational/methodology: biomarker, assay, multi-omics, AI/ML model, vaccine platform, drug delivery, platform technology.

For mixed studies, set a primary type by the central claim and add secondary evidence labels.

### 3. Split into knowledge cards

Create one card per core medical conclusion. A valid card must contain only one core conclusion and must be traceable to the PDF.

Do not create broad generic summaries. Prefer reusable content assets:

- Mechanism statements with target/pathway/cell type.
- Clinical efficacy/safety data.
- epidemiology or disease burden facts.
- patient journey, unmet need, or treatment-choice insights.
- product positioning, core message, or medical story material.
- competitor/product comparison facts.
- guideline, policy, or compliance-relevant recommendations.

### 4. Assign labels

For every card, assign:

- level-1 tag: one of the six modules in `tag-taxonomy.md`.
- level-2 tag: one of the approved submodules.
- content-use tag: physician PPT, medical DA, patient education, internal training, competitive intelligence, guideline update, evidence chain, compliance review.
- evidence object: human, animal, cell, organoid, tissue, public database, literature set, regulatory document, expert opinion.
- article type and evidence level.
- review flags: needs medical review, needs compliance review, needs source tracing, needs patient-friendly rewrite.

### 5. Apply review and compliance rules

Use conservative medical language. Do not overclaim.

Mandatory flags:

- If a card mentions product names, competitors, advantages, superiority, positioning, patient management, prescribing habit, promotional strategy, or clinical-data comparison, set `Needs_Compliance_Review = Yes`.
- If a card comes from a Review and references clinical research data, product comparison, key efficacy/safety numbers, or immunology mechanism data, set `Needs_Source_Tracing = Yes` unless the original primary source is also cited with location.
- If a card will be patient-facing, set `Needs_Patient_Rewrite = Yes` and convert technical language into patient-friendly language in the patient-facing column only.
- If a card supports medical claims, set `Needs_Medical_Review = Yes` unless it is purely bibliographic or administrative.

### 6. Build the Excel workbook

Create the workbook with clean formatting, filters, frozen header rows, wrapped text, dropdown-like controlled values where feasible, and summary counts. The workbook must be easy to filter by level-1 tag, level-2 tag, article type, evidence level, review status, and source page.

Use a stable filename pattern:

`immune_literature_tagged_cards_[short-title-or-date].xlsx`

## Card Writing Rules

- One card = one conclusion.
- Every card needs source traceability: page, section, figure/table if available, and short source excerpt or paraphrase.
- Preserve English drug names, gene/protein names, pathway names, cytokines, biomarkers, endpoints, and standard abbreviations.
- For first-use abbreviations, expand in Chinese plus English abbreviation when available.
- Use clinician-standard Chinese phrasing.
- Separate source fact, interpretation, and content-use suggestion.
- Mark all inference as inference.
- Never state causal, mechanistic, or clinical conclusions beyond the article design.

## Minimum Viable Output If PDF Is Limited

If the full PDF cannot be read, still create an Excel workbook using available metadata/abstract, but add `Insufficient_Full_Text = Yes` and clearly mark missing pages/sections in `Source_Map` and `Review_Checklist`.

## Related Skills

For PDF extraction and workbook creation, use the environment's PDF and spreadsheet tools according to their instructions. For deep medical appraisal, use medical literature reading conventions when needed, but keep this skill's Excel card output as the final deliverable.
