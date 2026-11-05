# Internal document model

## Purpose

The documents are compact internal memory for the Agent and future development
work. They are not the user's primary review interface. Use the project review
page and actual website for approval.

## Canonical sources

Only these eight files are editable design/specification sources:

| Source | Owns |
|---|---|
| `docs/source/requirements.md` | background, goals, audience, real brand status, language, scope, facts, constraints, initial page/Section needs |
| `docs/source/reference.md` | structural and design-reference evidence, navigation behavior, reusable principles, rejected patterns, access limitations |
| `docs/source/sitemap.md` | routes, Page Families, ordered Sections, Listing/Detail pairs, template coverage, navigation relationships |
| `docs/source/content.md` | writing approach, approved copy, links/CTA, source mapping, Logo/media decisions, provenance, rights, Alt, crop, loading, placeholders |
| `docs/source/layout.md` | Section purpose/composition, semantic structure, Section-local Containers, background boundaries, media geometry, responsive transformations |
| `docs/source/design-token.md` | colors, typography, spacing, widths, edges, surfaces, states, motion primitives, scrollbar values, approved exceptions |
| `docs/source/components.md` | Global Shell, navigation, buttons, links, media, forms, Listings, Detail patterns, Hero visual anatomy, states, responsive behavior |
| `docs/source/animation.md` | Hero/menu/scroll/media/interaction motion, triggers, timing, GSAP/Swiper use, loading, failure, reduced motion, no-JavaScript behavior |

Do not create separate `hero-spec.md`, `motion.md`, `content-plan.md`,
`website-requirements.md`, `page-structures.md`, or `design-reference.md`.
Put each fact in its owning source.

Evidence files such as screenshots, recordings, or generated concept cards may
exist under `docs/evidence/`. They support a source document but do not become
new authorities.

## Compiled masters

Generate:

```text
docs/spec.md
  ← requirements.md
  ← reference.md
  ← sitemap.md
  ← content.md

docs/design.md
  ← layout.md
  ← design-token.md
  ← components.md
  ← animation.md
```

Never edit compiled masters directly. Their generated header and source digest
make stale or manual changes visible.

Run:

```bash
python3 /path/to/hey-web-design/scripts/assemble_docs.py /path/to/project all
```

Use `spec` or `design` instead of `all` when only one group changed.

Rebuild `spec.md` after any of its four sources changes. Rebuild `design.md`
after any of its four sources changes. If a `spec.md` source changes after
layout, mark design and rendered pages for revalidation rather than silently
preserving incompatible decisions.

## Source format

Each source should begin with:

```markdown
# Human-readable title

- Status: draft | in-review | approved | locked
- Updated in stage: requirements
- User approval: pending

## Decisions

## Evidence and sources

## Missing or unresolved

## Change log
```

Add domain-specific headings after this small header. Keep known facts,
preferences, assumptions, and missing information visibly separate.

Use stable page, Section, template, media, and rule IDs only when they improve
cross-reference. Do not turn the Markdown into a database or duplicate the
entire HTML.

## Relationship to HTML

- The review page summarizes current sources and state in the conversation
  language.
- The actual website implements the approved sources.
- The website's copy uses the website language.
- The review page does not need to match the website's visual direction.
- A decision becomes approved only through the required command, not because it
  appears in HTML.

When updating a source, immediately identify the corresponding visible change:

| Source | Minimum visible consequence |
|---|---|
| requirements | page/Section skeleton or labels |
| reference | menu/navigation behavior or structural principle |
| sitemap | route/template creation or navigation relationship |
| content | real copy/media/link state |
| layout | composition/container/responsive change |
| design-token | computed visual styling |
| components | rendered component/state change |
| animation | observable motion, loading, fallback, or explicit no-motion state |

If there is no honest visible consequence yet, leave the source decision
pending instead of claiming the stage is complete.

## Review-page content

Generate the review page from state and source summaries. It should show:

- project name and current step;
- what changed since the previous approval;
- what the user needs to decide now;
- page directory and affected routes;
- reference evidence, design comparisons, or media candidates when relevant;
- links to actual website pages;
- Desktop and Mobile inspection status;
- known limitations and placeholders;
- exact transition command.

Do not expose long internal documents, raw status enums, or technical review
reports by default. Do not store an approval only in review-page markup.

## Optional handoff

Create `docs/development-handoff.md` only after `next:handoff`. It may summarize
the two compiled masters, static delivery, dynamic work not implemented, and
directional React/Vue/other recommendations. It does not authorize production
code or add another specification authority.
