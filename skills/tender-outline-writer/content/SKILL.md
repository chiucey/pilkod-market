---
name: tender-outline-writer
description: Turn parsed tender requirements into a complete bid outline, scoring-response structure, and AI-facing chapter briefs. Use when Codex needs to design the structure of a technical bid, decide chapter naming, separate parameter response tables from the main body, map scoring items into chapters or evidence sections, or generate a full outline for government procurement, engineering, services, or software integration tenders after requirement parsing.
---

# Tender Outline Writer

## Overview

Turn parsed tender requirements into a complete, usable bid outline for downstream drafting.

Do not behave like a generic table-of-contents generator. Build an outline that matches pre-sales writing logic, project type, tender structure, parameter-response strategy, and scoring-response strategy.

A strong outline must help the team do three things at once:

- write a readable main technical proposal
- place formal response tables and mandatory files correctly
- give every meaningful scoring item a clear landing place

## Required Input

Prefer to start from the output of `tender-requirement-parser`.

Especially look for these parsed sections:

- technical bid structure judgment
- parameter response strategy
- solution theme map
- recommended technical-body architecture
- evaluation and scoring matrix
- mandatory technical or service response points
- commercial and contractual constraints
- writing handoff for downstream skills

If those inputs are missing, reconstruct them from the tender before outlining.

## Core Goal

Produce four linked outputs:

- A complete human-facing outline
- A scoring-response and evidence structure
- AI-facing chapter briefs for downstream drafting
- Section blueprints for section-level writing

The outline is for people to review and approve.

The scoring-response structure is for the team to ensure scoring items, mandatory forms, and proof-heavy materials are not lost.

The chapter briefs are not normal summaries. They are writing instructions for `tender-technical-writer`, so each brief must tell the next skill what the chapter is supposed to accomplish, cover, emphasize, prove, and avoid.

The section blueprints go one level deeper. They must explain how major narrative chapters should be broken into smaller headings, what each heading should contain, which technical or service stack it reflects, and which outputs or proof packages it should connect to.

Treat the chapter brief and section blueprint together as a writing pack. Do not expect a thin brief by itself to be sufficient for full drafting.

## Workflow

1. Read the parsed tender interpretation, not only the original requirement list.
2. Decide whether technical parameters belong in deviation tables, the main body, or both.
3. Decide the naming logic for the technical body based on tender type.
4. Design the main proposal structure.
5. Design the scoring-response and evidence structure.
6. Attach an expanded chapter brief to every meaningful chapter or section group.
7. Build section blueprints for major narrative chapters.
8. Check that scoring items, mandatory requirements, assurance topics, proof materials, and service-capability logic all have a home.

## Build The Outline In Three Layers

Always think in three layers.

### Layer 1: Formal Response Layer

This layer holds items required by the tender format or by mandatory compliance logic, for example:

- technical deviation tables
- service description tables
- required response forms
- mandatory annex indexes
- tender-required miscellaneous files

### Layer 2: Main Proposal Layer

This layer is the readable technical proposal body.

It should be organized by professional solution logic, not by row-by-row parameter order.

### Layer 3: Scoring And Evidence Layer

This layer maps scoring items and proof-heavy sections into explicit chapter homes, for example:

- team capability evaluation response
- project service requirement response
- cloud platform construction response
- security service response
- operation and maintenance response
- risk and emergency response
- supporting evidence and case studies

If the team template or tender already mixes Layer 2 and Layer 3, keep the structure usable but still recognize the distinction internally.

## Separate Table Responses From The Main Body

Do not confuse parameter response tables with the technical solution body.

### When A Deviation Table Exists

If the tender provides a technical deviation table, technical response table, or `★/#/△` response template:

- keep row-by-row parameter response in that table structure
- do not turn parameter rows into the main body outline by default
- only absorb architecture-defining, high-risk, or strongly thematic parameters into the body text

When this happens, the outline should normally include a separate section such as:

- technical deviation table
- key parameter response
- annexed parameter compliance response

But the main technical chapters should still be organized by professional solution themes.

### When No Deviation Table Exists

If the tender does not require point-by-point parameter response, absorb technical requirements into themed solution chapters.

## Default Technical Body Architecture

Unless the tender imposes another mandatory chapter system, use a two-part technical body:

- Technical service solution or product technical solution
- Assurance solution

This default reflects common pre-sales writing logic and should be preferred over flat requirement-order outlines.

### Technical Service Solution Or Product Technical Solution

Use this part for:

- project understanding and goals
- solution positioning
- overall technical route
- product or platform architecture
- functional and technical realization
- implementation, deployment, migration, or integration methods
- key technical response themes that belong in prose

### Assurance Solution

Use this part for:

- project organization and staffing
- implementation planning and schedule control
- quality assurance
- security assurance
- risk control and emergency plans
- training
- acceptance and delivery
- after-sales or continuous service mechanisms

If the project type suggests a different naming style, recommend that naming explicitly.

## Add A Scoring-Response Structure When Scoring Is Strong

If the tender has a detailed evaluation matrix, do not rely on the main proposal body alone.

Create an explicit scoring-response structure that ensures each scored topic has a home.

Typical patterns include:

- procurement requirement or scoring-required files
- detailed design or response status
- team capability evaluation
- project service requirement response
- cloud platform construction response
- security service response
- unified operation and maintenance response
- risk control and emergency response
- supporting evidence, customer practice, and core advantages

Use this layer when it helps the team submit a proposal that is easier to score, even if parts of the content overlap with the main proposal body.

## Use A Four-Part Writing Package For High-Value Sections

When a section is heavily scored, strongly evidence-based, or central to the project, prefer a four-part package:

- response status or solution positioning
- core scheme or core advantages
- landing feasibility or assurance mechanism
- supporting evidence or reference material

Use this pattern especially for:

- cloud platform construction
- security service
- operation and maintenance service
- project service requirement response
- risk and emergency response

## Add Section Blueprints For Major Narrative Chapters

Do not stop at chapter-level guidance when the proposal will require real writing depth.

For major narrative chapters, especially service-heavy or technically layered chapters, produce a section blueprint that answers:

- what second-level headings should appear
- what third-level headings are needed for writing stability
- what each heading should write about
- what technical stack, service capability, or method framework sits behind that heading
- what output, report, table, or proof package is related to that heading

This is mandatory for chapters that would otherwise become vague, such as:

- implementation schemes
- service delivery schemes
- security service schemes
- operation and maintenance schemes
- attack-and-defense drill schemes
- migration schemes
- risk and emergency schemes
- training, acceptance, and delivery schemes

## Derive The Section Tree From The Real Service Or Product Stack

Do not invent headings from generic proposal language alone.

Infer the likely section tree from the actual service or product stack behind the procurement target.

Examples:

- Attack-and-defense drill service may naturally decompose into demand analysis, scope confirmation, asset inventory, authorization or filing preparation, drill scheme design, execution, guidance and consulting, scanning and verification, risk measurement, remediation retest, reporting, on-site support, and platform support.
- Unified operation and maintenance service may naturally decompose into service organization, service process, inspection, monitoring, fault handling, change management, resource management, security operations, training, reporting, and service assurance.
- Cloud platform construction may naturally decompose into overall architecture, compute, storage, network, system resources, compatibility, security, delivery path, and verification.

When building the section blueprint, prefer the real implementation or service chain over generic headings such as `项目背景`, `建设内容`, `保障措施`.

## Choose Chapter Names By Tender Type

Do not force every project into the same labels.

Use the tender type to choose the most natural naming system.

- Government procurement service project: often prefer `技术服务方案` and `保障方案`.
- Software integration project: often prefer `产品技术方案` or `技术方案`, plus `实施与保障方案`.
- Engineering project: often prefer `施工组织设计`, `实施方案`, or `质量安全保障方案`.
- Hybrid build-and-operate project: often prefer `技术方案` plus `运维与保障方案`.

If the tender itself already implies a naming style, follow it.

## What The Outline Must Achieve

A good outline must ensure that all of the following are placed somewhere explicit:

- mandatory response points
- scoring opportunities
- technical themes
- implementation or service logic
- assurance content
- proof-heavy or annex-heavy items
- high-risk commitments and boundaries

Do not leave these floating in notes. Give them a chapter home.

## What The Chapter Brief Must Contain

For every major chapter or section group, write a brief that includes:

- chapter purpose
- chapter role in the whole proposal
- tender concerns this chapter addresses
- requirement themes this chapter must absorb
- scoring or evidence opportunities linked to the chapter
- why this chapter exists from a pre-sales writing perspective
- relationship to the previous and next major chapters
- what the reader should understand after finishing the chapter
- recommended writing logic
- what should stay out of this chapter

If the chapter belongs to the scoring-response layer, also include:

- whether it is mainly for scoring, compliance, or evidence packaging
- what proof materials should be attached
- whether the chapter should restate or only point to the main proposal body

The brief should help `tender-technical-writer` write a professional section rather than restate requirements mechanically.

Do not let the brief collapse into a short summary. It should be a chapter-level writing instruction sheet.

## What The Section Blueprint Must Contain

For every major narrative chapter, include:

- Chapter title
- Suggested section tree
- Section-by-section writing notes
- Capability or technology stack mapping
- Deliverable or evidence mapping
- Scoring or compliance notes when relevant

The section tree should usually include proposed second-level headings and optional third-level headings.

The writing notes should explain what to write under each heading, not just restate the heading name.

The capability mapping should explain what product capabilities, service modules, methodology steps, or technical mechanisms support the section.

The deliverable mapping should mention items such as:

- reports
- forms
- confirmation sheets
- screenshots
- certificates
- logs
- diagrams
- daily reports
- acceptance documents
- remediation lists

Use this to prevent AI from writing elegant but empty prose.

## Use The Writing Pack To Drive Drafting

When downstream drafting starts, the chapter brief should answer `why write this chapter this way`, and the section blueprint should answer `how to actually write it subsection by subsection`.

For service-heavy projects, the section blueprint is often more important than the chapter brief.

For product-heavy projects, use the chapter brief to keep strategic structure stable and the section blueprint to prevent shallow feature-stacking.

## Outline Design Rules

- Prefer professional solution logic over tender line order unless the tender mandates a fixed structure.
- Do not create directory trees that merely rename procurement clauses.
- Do not let parameter rows dictate second- and third-level titles when the body should express a system, method, or framework.
- Distinguish clearly between technical solution content and assurance content.
- Distinguish clearly between the main proposal layer and the scoring-response layer.
- If a chapter exists only to satisfy a template requirement, keep it concise and avoid letting it distort the whole outline.
- If the tender has strong scoring categories, ensure the outline gives each category a natural landing place.
- If the tender has mandatory forms, keep them separate from narrative chapters.
- If the team already uses a strong internal template, align with it instead of forcing an abstract ideal structure.
- Avoid uncontrolled duplication; when two sections overlap, decide which one is the main narrative and which one is the response or evidence package.
- Do not output a thin chapter brief when the chapter clearly requires a section blueprint to be writable.
- Prefer richer writing packs over shorter summaries when the project involves a real implementation chain, service chain, or product stack.

## Output Requirements

Always produce all four outputs:

- `bid-outline.md`: the complete outline
- `scoring-response-map.md`: the scoring-response and evidence structure
- `chapter-briefs.md`: the AI-facing chapter briefs
- `section-blueprints.md`: the section-level writing blueprints

Use the output pattern in `references/output-format.md`.

## Handoff To Other Tender Skills

- For `tender-technical-writer`: every chapter brief should be usable as a direct drafting brief.
- For `tender-compliance-reviewer`: preserve the mapping between chapters and mandatory/scoring requirements.
- For `tender-polish-editor`: preserve the chosen naming system and terminology across all chapter titles.

## Read Additional References When Needed

- Read `references/output-format.md` when generating the final outline, scoring-response structure, chapter briefs, and section blueprints.
- Read `references/naming-guidance.md` when the tender type is ambiguous and you need help choosing chapter names or deciding whether to use `技术方案`, `服务方案`, `产品技术方案`, or `保障方案`.
- Read `references/writing-pack-guidance.md` when the project is complex enough that downstream drafting needs a true chapter writing pack instead of a thin brief.
