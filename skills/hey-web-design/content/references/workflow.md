# Workflow, state, and approval commands

## Core contract

Use `project-state.yaml` as the only machine-readable workflow authority. Only
the main Agent may write it. Internal Markdown preserves reasoning; rendered
HTML is what the user reviews.

Every numbered stage has three synchronized layers:

```text
editable source Markdown
        ↓ compile
spec.md or design.md
        ↓ present and implement
review/index.html + actual website HTML/CSS/JavaScript
```

No layer replaces another. A change recorded only in chat, only in Markdown, or
only on the review page is incomplete.

## Setup

Before `requirements`:

1. Confirm a new standalone project or an existing repository target.
2. Inspect the target, conventions, current files, Git state, and overlapping
   user changes.
3. Detect Browser, Fetch, Image Generation, Subagent, and Git capabilities as
   `available`, `unavailable`, or `failed`.
4. Record conversation language separately from website language.
5. Use the website root for final static files; do not create a nested
   `prototype/`.
6. Create:

   ```text
   index.html
   pages/
   assets/
   css/
   js/
   review/
   docs/source/
   project-state.yaml
   ```

7. Copy the Skill's `assets/review-template/` into `review/`, translate it to
   the conversation language, and connect its links to the current project.
8. Create all eight source Markdown files as labeled stubs so both compiled
   master files can exist from the beginning.
9. Run the Skill's `scripts/assemble_docs.py <project-root> all`.
10. Enter `requirements` automatically. Setup has no approval command.

Adapt an existing repository rather than rearranging it. Keep `review/` clearly
separate and exclude it from public delivery.

## Stable stages and commands

Keep these internal IDs stable:

```text
setup
requirements
reference
sitemap
content
layout
visual
animation
review
handoff
complete
```

| Stage | Source documents changed | Required website change | Allowed command |
|---|---|---|---|
| `requirements` | `requirements.md` | Neutral homepage and currently known page/Section skeleton | `next:reference` |
| `reference` | `reference.md` | Neutral navigation/menu behavior and structural principles supported by research | `next:sitemap` |
| `sitemap` | `sitemap.md` | Every approved route/template exists and is navigable | `next:content` |
| `content` | `content.md`, rebuilt `spec.md` | Approved copy, links, CTA, source media, selected generated media, and Placeholders | `next:layout` |
| `layout` | `layout.md` | Responsive composition for every approved template | `next:visual` |
| `visual` | `design-token.md`, `components.md` | Selected visual direction applied first to homepage, then all templates | `next:animation` |
| `animation` | `animation.md`, rebuilt `design.md` | Hero, navigation, media, scroll, and interaction motion, or approved restrained no-motion state | `next:review` |
| `review` | QA state and review page | Objective fixes to the complete running website | `approve:complete` or `next:handoff` |
| `handoff` | `development-handoff.md` | No website redesign or framework migration | `approve:complete` |

Reject a command that skips a stage, targets another destination, arrives before
required rendered work exists, or has unresolved objective defects.

## What each stage must do

### `requirements`

- Interview in small rounds until the business, site purpose, background,
  audience, primary outcome, real brand name or `未确定`, content, trust
  evidence, language, existing assets, static/dynamic boundary, and desired
  completeness are understood.
- Ask for current, competitor, or same-industry URLs only to understand content
  coverage and navigation hierarchy.
- Describe the website as a directory tree with ordered Sections under every
  page, plus Listing/Detail relationships.
- Classify independent templates as Focused 1–5, Standard 6–12, Full-site
  13–20, or explicitly scoped Custom 20+.
- Update `requirements.md`.
- Render a neutral, clearly provisional homepage and known Section/page
  skeleton. Do not apply a guessed final brand style.

Before `next:reference`, confirm the user can see and approves the purpose,
audience, language, directory tree, ordered Sections, static scope, template
range, known facts, assumptions, and missing inputs.

### `reference`

- Separate structural/industry examples from design references.
- Let the user provide URLs, screenshots, recordings, or source, or ask the
  Agent to recommend two or three current industry-relevant sites.
- Follow [browser-research.md](browser-research.md).
- Record evidence, limitations, useful principles, and rejected patterns in
  `reference.md`.
- Update the actual website only with neutral, evidence-backed navigation,
  menu-state, responsive-hierarchy, and broad rhythm principles. Do not
  prematurely imitate the reference's color, font, assets, or final styling.

Before `next:sitemap`, confirm research coverage, menu behavior, mobile
behavior, layout/motion principles, forbidden-pattern evidence, and the
copying boundary.

### `sitemap`

- Turn approved requirements into routes and independent Page Families.
- Include Global Shell, homepage, Information, Listing, Detail, Contact,
  Utility, and other approved families.
- For each collection, pair one Listing Template with a representative Detail
  Template.
- Record route, purpose, Section order, shared template, short/long/empty/
  missing-media states, and priority in `sitemap.md`.
- Build semantic, navigable neutral HTML for every approved independent
  template. Full-site work may be implemented in batches of three to five, but
  all batches remain in this stage.

Before `next:content`, every approved route and template must open in a real
Browser on Desktop and Mobile.

### `content`

- Inventory an approved source-material folder recursively without deleting,
  renaming, moving, overwriting, or exposing originals.
- Separate facts, permitted rewriting, assumptions, missing information, and
  rights status.
- Present three or four project-specific ways the website text could feel,
  using the same factual sample; recommend one in plain language.
- Write concise, specific copy. Move detail out of Listing previews instead of
  compressing every fact into one page.
- Ask separately about existing Logo, generated Logo PNG concept, text Logo,
  later upload, or no Logo decision.
- Ask by media group whether to use approved source assets, generate, search a
  permitted stock source, keep a clear Placeholder, provide later, or omit.
- Obtain explicit approval before each generation batch; show candidates and
  let the user select before inserting any result.
- Record content, sources, media purpose, factual/conceptual status, Alt, crop,
  rights, loading, and approval in `content.md`.
- Apply approved copy and selected media to the actual pages and rebuild
  `spec.md`.

Before `next:layout`, inspect real wrapping, density, media rhythm, links, menu,
CTA, long/short text, and missing states in the Browser.

### `layout`

- Treat approved content as real layout input, not replaceable lorem ipsum.
- For every Section, record purpose, content order, semantic structure,
  Section-local Container, background boundary, media geometry, CTA, and
  responsive transformation in `layout.md`.
- Implement responsive wireframes/composition for every template.
- Use the structure, density, Container, Card, Bento, Grid, CTA, and responsive
  rules in [design-rules.md](design-rules.md).
- Review every Section, not only the homepage.

Before `next:visual`, show all templates at Desktop and Mobile and resolve
structural drift, overflow, repeated layouts, density problems, and broken
states.

### `visual`

- Derive two or three genuinely different project-specific visual concepts
  from the approved `spec.md` and layout.
- Before producing concepts, let the user choose one understandable preview
  route:
  1. generated still mockups or style/palette images;
  2. live HTML concept previews;
  3. a deliberate combination of generated art direction and HTML design
     system previews.
- Recommend a route from the project:
  - use generated stills to explore high-concept atmosphere, art direction,
    Hero scenes, photography/illustration character, or a broad visual world;
  - use HTML to compare real Chinese/Latin typography, color Tokens, contrast,
    responsive wrapping, components, Hover/Focus, and loading states;
  - combine them only when both kinds of evidence materially improve the
    decision.
- If the user asks the Agent to decide, prefer HTML for color-system or
  component decisions and add generated stills only for visual territory that
  HTML cannot communicate efficiently.
- For the HTML route, keep approved layout and copy constant and create a
  Browser-visible comparison under the review area, such as
  `review/visual-options/`. It may show complete homepage treatments and/or a
  design-system page with palette, type, buttons, links, forms, navigation,
  media, loading, Focus, Hover, and responsive states.
- For the generated route, show two or three project-specific still mockups or
  style/palette boards on the review page. Treat them as decision evidence, not
  final website assets or proof of responsive behavior.
- Do not ask the user to select from text descriptions alone.
- After selection, apply the direction to the real homepage, review it, then
  extract `design-token.md` and `components.md` and apply the system to all
  templates.
- Record typography, color, spacing, Section-local width, surfaces, media,
  icons, states, Logo use, responsive behavior, and exceptions.

Before `next:animation`, inspect the homepage and every template family in a
real Browser. Generated mockups, an isolated HTML comparison, or a token list
without the selected direction implemented in the actual website is incomplete.

### `animation`

- Treat Hero as a cross-document feature:
  - words and media facts come from `content.md`;
  - composition, alignment, responsive placement, and focal point come from
    `layout.md`;
  - visual appearance comes from `design-token.md` and `components.md`;
  - motion, loading, reduced-motion, and failure behavior belong in
    `animation.md`.
- Ask whether the user will supply a Hero screenshot, URL, recording, source,
  or direction, or wants Agent recommendations.
- Show viable left, center, right, or custom text composition against the
  actual background. Ask about optional Logo rail, trust marks, statistics,
  product image, scroll cue, and secondary action; add none automatically.
- Offer: restrained no decorative motion, recommended motion, or specific
  annotations.
- Implement approved Hero, menu, scrollbar, media-loading, scroll, and
  interaction behavior in the real website.
- Rebuild `design.md`.

Before `next:review`, test Desktop/Mobile, Keyboard/Touch, reduced motion, no
JavaScript, slow/failing media, and dependency fallbacks.

### `review`

- Follow [qa.md](qa.md).
- Test every independent template and representative content state in a real
  Browser.
- Fix objective defects that preserve approvals; ask before changing structure,
  meaning, visual direction, selected assets, motion intensity, dependencies,
  scope, or delivery.
- Keep `review/` out of the final static website package.

## Stage transition protocol

At every boundary:

1. Confirm source Markdown, compiled master, review page, and actual website are
   synchronized.
2. Confirm affected routes open and Browser evidence exists at Desktop and
   Mobile.
3. Resolve objective must-fix issues.
4. Update the review page with current step, visible changes, user decisions,
   affected routes, viewport status, and the exact allowed command.
5. Tell the user the same information in concise plain language.
6. Wait for the exact command.
7. Validate it against `workflow.current_phase`.
8. Create a scoped Git checkpoint when available.
9. Update approvals, locks, history, and current stage.
10. Begin only the next stage.

Use `revise:<topic>` for an in-stage revision. Explain downstream impact before
unlocking a prior decision.

## Project state

Keep state compact. Store long explanation in the eight sources.

```yaml
schema_version: 2
project:
  id: example-site
  website_language:
    primary: zh-CN
    multilingual: false
communication:
  conversation_language: zh-CN
  mode: plain-language
workspace:
  mode: standalone
  root: .
capabilities:
  browser: available
  fetch: available
  image_generation: unavailable
  subagent: available
  git: available
workflow:
  current_phase: layout
  status: in-review
  allowed_transition: next:visual
documents:
  spec:
    path: ./docs/spec.md
    source_hash: null
  design:
    path: ./docs/design.md
    source_hash: null
rendered:
  review:
    entrypoint: ./review/index.html
    preview_url: http://127.0.0.1:4173/review/
  website:
    entrypoint: ./index.html
    preview_url: http://127.0.0.1:4173/
    rendered_stage: layout
approved: []
locked: []
editable: []
pending_decisions: []
review:
  mode: self-second-pass
  status: pending
  must_fix: []
blockers: []
git_checkpoint:
  status: pending
transition_history: []
```

Useful statuses include:

```text
not-started
in-progress
in-review
approved
locked
skipped-by-user
waiting-for-user
waiting-for-user-login
waiting-for-user-git-decision
blocked-by-reference-access
unable-to-verify
unavailable
complete
```

If a `spec.md` source changes after design work begins, mark the affected
layout, visual, animation, and website HTML as needing revalidation.

## Git and resume behavior

- Preserve unrelated and overlapping user work.
- Stage only explicitly managed files; never broad-add a dirty repository.
- Never auto-Stash, Reset, Clean, Rebase, Checkout, or change global Git
  configuration.
- For a new standalone project, initialize Git when available. Do not initialize
  a nested repository inside an existing one.
- Create a checkpoint only after a valid transition and around major approved
  bulk application work.
- On resume, read state, both compiled masters, the current source, review page,
  and affected website files. Do not recreate completed stages.
- If reference login is required, remain in `waiting-for-user-login`.
- If Browser and Fetch both fail for a required reference, remain in
  `blocked-by-reference-access`.
