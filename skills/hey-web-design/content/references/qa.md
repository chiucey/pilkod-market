# Stage review, final QA, delivery, and handoff

## Rendered evidence is required

Use a real Browser. Source inspection cannot prove rendered layout, interaction,
responsive behavior, loading, or motion.

At every stage, verify:

- `review/index.html` reflects current state and links to the correct pages;
- the actual website contains a visible change appropriate to the stage;
- changed routes open at Desktop and Mobile;
- no new console error, missing resource, broken link, or horizontal overflow
  appeared;
- the source document and compiled master agree with the implementation;
- the user reviewed the rendered result before a transition command is
  requested.

## Reviewer model

Use one or two read-only Reviewers for Standard Review. Use three by default
only for requested Deep Review, complex homepage finalization, or full-site
final delivery; never more than four.

Possible perspectives:

| Checkpoint | Useful reviewer |
|---|---|
| requirements | website type and scope |
| reference | evidence fidelity |
| sitemap/layout | information architecture and anti-AI composition |
| content | specificity, factual integrity, and media provenance |
| visual | Awwwards/FWA craft and anti-AI patterns |
| animation | interaction, accessibility, and performance |
| final | browser route/template QA |
| handoff | completeness and boundary clarity |

Give Reviewers raw files, preview URLs, screenshots/evidence, approved/locked
decisions, applicable rules, and report format. Do not disclose an expected
verdict or another Reviewer's conclusion before their first pass.

Tell each:

```text
Act only as the assigned reviewer. Do not edit files, update project state,
approve decisions, expand scope, create stage commands, or advance workflow.
Base findings on observable evidence and mark anything you cannot verify.
```

Allow one initial pass and one targeted re-review. Replace a failed Reviewer
once, then run a labeled self-second-pass. The main Agent merges reports and
edits.

## Fix authority

The main Agent may fix without new approval:

- broken links/assets and console errors;
- responsive overflow and implementation breakage;
- keyboard, Focus, semantic, and obvious accessibility defects;
- missing loading/error/reduced-motion/no-JavaScript fallback;
- implementation drift from approved sources.

Ask the user before changing:

- navigation, route, Page Family, or Section structure;
- copy meaning, main-action priority, or writing approach;
- visual direction or selected asset;
- Hero concept or optional elements;
- motion intensity or interaction mechanism;
- dependency, template scope, or delivery method.

Rerun affected checks after every fix.

## Final template and viewport coverage

Test every independent template at:

| Target | Viewport |
|---|---:|
| 2K Desktop | 2560×1440 |
| 1080p Desktop | 1920×1080 |
| iPad Landscape | 1180×820 |
| iPad Portrait | 820×1180 |
| Mobile | 390×844 |

Sample repeated instances only after covering short content, long headings,
missing media, empty collection, zero/one/several/many items, boundary
metadata, loading, and failure.

For every collection, verify Listing and Detail together: navigation,
Breadcrumb, main action, related content, and return path.

## Final functional and content QA

Verify:

- every planned route exists and opens;
- page/Section coverage matches `spec.md`;
- first/second-level navigation and Mobile nested menu work;
- Header scroll behavior and menu animation match approved evidence;
- links/buttons have correct semantics and destinations;
- keyboard order, visible Focus, Skip Link, labels, landmarks, and headings are
  correct;
- approved copy, CTA, Alt, media, and writing approach appear in HTML;
- every user/generated/stock asset has approved provenance, rights status,
  purpose, crop, Alt, and loading;
- no rejected, malformed, unapproved, or deferred generated candidate is used;
- generated conceptual media is not presented as factual evidence;
- Chinese H1, wrapping, weight, punctuation, and letter spacing follow rules;
- multilingual pages rewrite naturally without losing brand character;
- core content works with JavaScript disabled;
- relative paths and documented preview instructions work;
- `review/` is not referenced by public pages and is excluded from delivery.

## Final visual and anti-AI QA

Inspect:

- unauthorized Cards, Bento, gradients, abstract Hero glows, or 3×2 Grids;
- nested Cards, default-library appearance, excessive radius/glassmorphism;
- repeated Card matrices or predictable Landing Page sequence;
- repetitive Section composition, widths, or equal heights;
- information density, Listing preview length, and media rhythm;
- Section-local Containers, full-width backgrounds, Mobile gutters, and
  full-bleed exceptions;
- more than one dedicated CTA Section per page;
- Chinese H1 over 64px without approval;
- Chinese letter spacing, heading roles, font license/loading/fallback;
- Paragraph rhythm and meaningful `<strong>`;
- non-media Hover/Focus scale;
- scrollbar contrast and native fallback;
- placeholder art incorrectly presented as final.

Distinct Sections must still belong to one coherent brand system.

## Hero, animation, media, and performance QA

Verify:

- Hero words remain semantic and readable;
- alignment, focal point, crop, contrast, Desktop/Mobile placement, and optional
  elements match approved sources;
- loading, Poster, error, no WebGL, no JavaScript, slow-network,
  low-performance, and reduced-motion states;
- iframe justification, parent semantics, Focus, and messaging safety;
- Swiper Touch, Drag, Keyboard, Focus, controls, pause, clones, resize, reduced
  motion, and fallback when used;
- GSAP purpose, initialization, lifecycle, cleanup, Breakpoint behavior, and
  fallback when used;
- GSAP and scroll-experience passes have an honest status;
- no scripted fake scrollbar;
- anchors, history, scroll restoration, Sticky, Focus, Keyboard, Wheel,
  trackpad, and Touch remain usable;
- image/video geometry prevents avoidable layout shift;
- above/below-fold loading strategy, crop, focal point, Alt, and error state;
- network, font, image, video, CPU, GPU, and memory cost are proportionate.

## Report

Record by route, template, viewport, state, evidence, severity, and verdict:

- `critical`: blocks access, navigation, or delivery;
- `major`: violates approval or breaks an important template/viewport;
- `minor`: localized craft or consistency defect;
- `optional`: subjective improvement outside approved scope.

Separate objective defects from optional ideas and mark anything
`unable-to-verify`.

## Static delivery

After all critical/major issues are resolved, provide:

- final website root and entry point;
- completed route/template list;
- local preview instructions and dependencies;
- reusable component/structure list;
- editing notes for copy and media;
- approved exceptions;
- remaining Placeholders and replacement guidance;
- asset sources, rights, and attribution;
- known limitations and future dynamic boundaries;
- final Browser QA status;
- Git checkpoint status.

The static HTML/CSS/JavaScript site is the final code delivery. Do not claim
that a visual account, filter, checkout, dashboard, CMS, or other mockup
implements product behavior. Do not deploy.

## Optional development handoff

Only after `next:handoff`, create one `docs/development-handoff.md` containing:

- purpose, scope, static delivery state, routes, and Page Families;
- summary/link to `spec.md` and `design.md`;
- component-boundary recommendations;
- content/media status and rights;
- Hero, Slider, motion, reduced-motion, loading, and fallbacks;
- approved anti-AI rules and exceptions as locked constraints;
- dynamic behavior not implemented;
- directional React, Vue, another ecosystem, or continued static HTML
  recommendation with reasons;
- risks and later acceptance criteria.

Do not specify exact current framework versions, database schema, deployment
provider, or generate production code unless another workflow authorizes it.

At `review`, accept `approve:complete` or `next:handoff`. At `handoff`, accept
only `approve:complete`.
