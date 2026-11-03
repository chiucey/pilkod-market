---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: c53c589a5ef5aa118b02d50a6262197a
    PropagateID: c53c589a5ef5aa118b02d50a6262197a
    ReservedCode1: 304502207cbb30d3d959c4154ff2abeb3f71a912863e4a4a389143187089102f94a73184022100adebbc90d2e90a6ea0f4c11068c20d239659b33b35b3c2ccada675a7e279229a
    ReservedCode2: 304402201dbea48d2f5726bd1451570e03a57db1ef88ff3a08736d6dbf50d066156dd75f0220311da659c3b8980b1b5c53912bed7789158fdee1281d24239a847286a32bed01
---

# Output Format

Always produce four coordinated artifacts.

## 1. bid-outline.md

This is the human-facing full outline.

Recommended structure:

### A. Formal Response Layer

Include items required by the tender or by the team template, for example:

- technical deviation table
- `★/#/△` response tables
- service description table
- technical document index
- annex index
- tender-required miscellaneous files

### B. Main Proposal Layer

This is the readable technical proposal body.

Recommend a numbered outline with at least:

- first-level chapters
- second-level sections
- third-level sections when needed for drafting stability

Prefer a strong main body that can usually be split into:

- technical service solution or product technical solution
- assurance solution

### C. Scoring And Evidence Layer

When the tender has strong scoring logic or the team template requires it, create an explicit section or group for scored responses and proof-heavy materials.

Typical subsections may include:

- technical response status
- detailed design
- team capability evaluation
- service requirement response
- cloud platform response
- security service response
- operation and maintenance response
- risk and emergency response
- supporting evidence and customer practice

## 2. scoring-response-map.md

This is the bridge between the tender scoring logic and the proposal structure.

For each major scoring item or proof-heavy requirement, include:

- Scoring item or requirement
- Related tender clause
- Main proposal chapter home
- Scoring-response chapter home
- Required evidence
- Notes on duplication or cross-reference

## 3. chapter-briefs.md

This is the AI-facing drafting brief set.

For each major chapter or section group, include:

- Chapter title
- Purpose
- Chapter role in the whole proposal
- Tender concerns covered
- Requirement themes absorbed
- Related scoring opportunities
- Why this chapter exists from a pre-sales writing perspective
- Relationship to the previous and next major chapters
- Reader takeaway after this chapter
- Recommended writing logic
- Keep out of this chapter

For scoring-response chapters, also include:

- Main role: scoring, compliance, or evidence packaging
- Suggested proof package
- Whether to summarize, cross-reference, or restate the main proposal

Do not reduce this file to short summaries. Each entry should read like a chapter-level writing instruction sheet.

## 4. section-blueprints.md

This is the section-level writing blueprint set.

Use it for major narrative chapters that require real drafting depth.

For each selected chapter, include:

- Chapter title
- Suggested section tree
- Section-by-section writing notes
- Capability or technology stack mapping
- Deliverable or evidence mapping
- Scoring or compliance notes

### Suggested section tree

List the likely second-level headings and, when useful, third-level headings.

### Section-by-section writing notes

For each heading, explain:

- what this section should say
- what problem it is solving
- how it connects to the previous and next sections
- what should not be over-expanded here
- what professional method, service action, or technical mechanism is carrying the section

### Capability or technology stack mapping

Explain what real service modules, product capabilities, methodology steps, or technical mechanisms support the section.

### Deliverable or evidence mapping

Connect the section to concrete outputs such as:

- reports
- confirmation sheets
- screenshots
- certificates
- logs
- diagrams
- daily reports
- acceptance files
- remediation lists

## Quality Rules

- The outline and briefs must match one another exactly in chapter naming.
- The scoring-response map must point to real chapters, not abstract ideas.
- Do not produce a generic summary in place of a chapter brief.
- The brief should be instructional, not decorative, and not just a short summary.
- The section blueprint should be detailed enough that a writer can start drafting subsection by subsection.
- If a chapter only exists because of a tender template, say so in the brief.
- If a topic belongs in a deviation table instead of prose, say so explicitly.
- If two sections overlap, state which one is primary and which one acts as scoring support or evidence support.
