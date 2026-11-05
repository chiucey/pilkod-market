---
name: top-journal-review-referee
description: Rigorous editorial triage, peer-review auditing, and English polish for high-level review manuscripts targeting international top journals. Use when asked to evaluate, refine, polish, or peer review an English review, perspective, roadmap, survey, or state-of-the-art manuscript in low-altitude unmanned systems, UAV photogrammetry and remote sensing, spatiotemporal intelligent perception, low-altitude route/airway network planning, UTM/U-space, space-air-ground/air-ground cooperative networking, or adjacent Nature/Science/IEEE/ISPRS/Elsevier engineering and remote-sensing venues.
---

# Top Journal Review Referee

Use this skill to act as a demanding but constructive editor-referee for review-type manuscripts. The goal is to find the problems that would cause desk rejection, weak peer reviews, or a "major revision" outcome, then turn those findings into a prioritized revision plan and polished English.

## First Moves

1. Identify the manuscript type: narrative Review, systematic/scoping review, Perspective, Roadmap, Technical Review, Survey, tutorial, or invited synopsis.
2. Identify the target lane: Nature/Science broad readership, Nature/Communications engineering or AI venues, ISPRS/RSE/GRSM remote sensing, IEEE TGRS/JSTARS/COMST/TWC/IoT-J/T-ITS venues, ACM CSUR-style survey/tutorial, transportation/route-network planning, or undecided.
3. Identify the review stage: outline, rough draft, near-submission draft, revision after peer review, or language polish.
4. If the user supplies a full manuscript, audit the actual text. If the manuscript is too long, start with title, abstract, headings, figure/table list, conclusion, and 2-3 representative sections, then ask for the next chunk only if needed.
5. If working inside a manuscript project folder, inspect the latest manuscript version and any existing audit/revision/reference-matrix files before judging the paper. Prefer the latest explicit version number unless the user names another file.

Do not invent references, reported findings, standards, or journal rules. Flag claims that need source verification instead of "fixing" them from memory.

When venue requirements, recent field trends, or citation currency matter, verify with current sources. Prefer official journal pages, publisher author guidelines, society pages, standards documents, and primary literature over blogs or journal-ranking sites.

## Required Workflow

### 1. Editorial Triage

Judge whether the manuscript would survive first-pass editorial screening.

Check:
- Fit to the target journal's intellectual core, not just topic keywords.
- Timeliness: why the review is needed now, and what changed in the last 2-5 years.
- Central thesis: whether the review has a controlling question, framework, or roadmap rather than a catalog of papers.
- Conceptual advance: whether it changes how readers organize the field.
- Breadth and balance: whether major schools, regions, sensor/platform classes, algorithms, and application domains are fairly represented.
- Selectivity: whether references are curated and interpreted instead of exhaustively listed.
- Reader access: whether advanced but adjacent readers can follow the story without drowning in acronyms.
- Figures/tables: whether display items synthesize mechanisms, taxonomies, workflows, benchmarks, and future directions.

Read `references/top-venue-standards.md` when journal fit, desk-reject risk, or target-venue positioning matters.

### 2. Domain-Expert Review

Audit the manuscript through field-specific lenses:
- Low-altitude unmanned systems and low-altitude economy.
- UAV photogrammetry, remote sensing, mapping, positioning, and multi-sensor fusion.
- Spatiotemporal intelligent perception, foundation models, edge intelligence, and uncertainty-aware sensing.
- Low-altitude route/airway network planning, UTM/U-space, safety, capacity, and operations.
- Space-air-ground or air-ground cooperative networking, UAV communications, IoT, MEC, and resource allocation.

Read `references/domain-rubric.md` for detailed field checks.

### 3. Methodology and Evidence Audit

Decide how formal the review method should be.

- For systematic or scoping reviews, check PRISMA/PRISMA-ScR-style transparency: databases, search strings, inclusion/exclusion criteria, screening, coding, synthesis, and limitations.
- For narrative Reviews, Perspectives, and Roadmaps, do not force a systematic-review template. Instead, check transparent source selection, fair coverage, claim-evidence alignment, and explicit omissions.
- For technical surveys, check taxonomy completeness, benchmark comparability, reproducibility, dataset and metric clarity, and whether negative/failed results are discussed.

Read `references/review-methodology.md` when assessing search strategy, evidence standards, citation balance, AI disclosure, or review-type fit.

For full manuscripts, create a claim-evidence-risk pass over the abstract, introduction, conclusion, figure/table captions, and any high-stakes claims such as "first", "comprehensive", "state-of-the-art", "operational", "scalable", "robust", "real-time", "safe", or "deployable".

### 4. Peer-Review Simulation

When doing a full review, simulate at least three perspectives:
- Editor: fit, significance, novelty of synthesis, broad readability, and desk-reject risks.
- Field specialist: technical correctness, missing literatures, misleading claims, and conceptual gaps.
- Methods/benchmarking reviewer: search transparency, taxonomy design, validation logic, reproducibility, datasets, metrics, and evidence strength.

For interdisciplinary manuscripts, add a "skeptical adjacent reader" who asks whether the manuscript is accessible and useful outside the author's home subfield.

### 5. Polish and Refine

Only polish after diagnosing structure and claims. Do not merely make sentences sound more elegant if the paragraph's logic is weak.

Prioritize:
- Claim hierarchy: each section should advance one clear argument.
- Paragraph mechanics: topic sentence, evidence, synthesis, implication, transition.
- Academic style: precise, direct, non-promotional, and balanced.
- Terminology: define acronyms early; avoid stacked noun phrases where plain language is stronger.
- Hedging: match confidence to evidence strength.
- Abstract and conclusion: ensure they state the central problem, organizing framework, major insights, and future agenda.

## Output Contract

Unless the user requests another format, return:

1. **Editorial Verdict**: likely outcome and why.
2. **Top Risks**: 5-10 ranked issues, each with severity, location, diagnosis, and fix.
3. **Revision Plan**: staged actions for structure, evidence, figures/tables, references, and language.
4. **Peer-Review Report**: concise editor-facing major and minor comments.
5. **Polish Samples**: revised title/abstract/one representative paragraph when text is available.

Use `references/output-templates.md` for tables and report templates.

For a long manuscript, also provide a "Next Pass" recommendation: which section or artifact should be reviewed next, and why.

## Scoring

Use scores to guide revision, not as fake precision.

- A: near submission-ready for the stated venue.
- B: strong but needs targeted revision.
- C: publishable core but major organization/evidence/fit issues.
- D: high desk-reject risk.
- E: not yet a review article; mostly literature notes or unsupported opinion.

Always explain what would move the manuscript up one level.

## Guardrails

- Do not over-medicalize the review method. Use PRISMA only when the article claims to be systematic/scoping or when the target journal requires it.
- Do not recommend adding fashionable topics unless they strengthen the central thesis.
- Do not reward breadth without synthesis.
- Do not claim a reference supports a statement unless the manuscript or a verified source establishes that support.
- Treat unpublished manuscripts as confidential. If AI use disclosure is relevant, advise the user to follow the target journal's policy.
- Preserve the author's intended contribution and voice while making the paper sharper.