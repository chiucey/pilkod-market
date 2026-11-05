---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d55649c0e22582df37be5ea7669234f5
    PropagateID: d55649c0e22582df37be5ea7669234f5
    ReservedCode1: 30440220096170a802773a2f1e2a9670f32a8d5015586c3150be4f106d8bf7a4f3453aba02203ab32e85d550cfea3f4583b2f2f8c660322040cd6ea25c87ba21f3be98066555
    ReservedCode2: 3045022006ccf83e8813efa43127389cfeb405748aae62e38c002f220bffbdcb9b1f9e05022100d51a6133ebeeb84eefac451c8338c114a01fb72b399d55e73e6b3aa7f7f4bf90
---

# Writing Pack Guidance

Use this reference when the proposal will be drafted by another skill or by multiple collaborators.

## Principle

A chapter brief alone is usually not enough for stable drafting.

For major chapters, output a `writing pack` made of:

- chapter brief
- section blueprint

The chapter brief controls chapter intent.

The section blueprint controls subsection construction.

## When A Thin Brief Is Not Acceptable

Do not output only a short brief when the chapter involves:

- a real service delivery chain
- a product or platform capability stack
- a phased implementation path
- an attack and defense workflow
- a migration or cutover path
- a risk and emergency mechanism
- a training, acceptance, or reporting system

In these cases, the section blueprint is mandatory.

## Recommended Writing Pack Shape

### Part 1: Chapter Brief

Include:

- chapter title
- chapter purpose
- chapter role in the proposal
- tender concerns covered
- requirement themes absorbed
- scoring and evidence opportunities
- pre-sales reason for keeping this chapter
- relationship to previous and next chapters
- reader takeaway
- recommended writing logic
- what to keep out

### Part 2: Section Blueprint

Include:

- suggested second-level headings
- suggested third-level headings when needed
- section-by-section writing notes
- capability or technology stack mapping
- deliverable or evidence mapping
- scoring or compliance notes

## Good Blueprint Behavior

Good blueprints do not merely rename headings.

They explain:

- what each section is for
- why the section exists
- how the section connects to the real service or product stack
- which actions, mechanisms, or outputs should appear in the writing

## Example Pattern For Service Chapters

For a service-heavy chapter, the blueprint often follows a real delivery chain:

- demand understanding
- scope confirmation
- preparation
- implementation
- monitoring or control
- reporting
- remediation or optimization
- acceptance or handover

## Example Pattern For Product Chapters

For a product-heavy chapter, the blueprint often follows a real capability chain:

- positioning and objectives
- overall architecture
- core modules
- key mechanisms
- compatibility and integration
- security and reliability
- deployment and verification

## Use This File To Prevent Empty Writing

If the proposed brief could be reused unchanged across many unrelated projects, it is probably too thin.

Rewrite it with more structure until a downstream writer could realistically draft from it.
