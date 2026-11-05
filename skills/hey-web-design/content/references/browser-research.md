# Browser-first reference research

## Separate the two reference purposes

During `requirements`, same-industry or existing sites may inform only content
coverage, navigation hierarchy, Page Families, and Listing/Detail
relationships.

During `reference`, user-approved examples may inform layout, visual
presentation, navigation states, responsive behavior, and motion.

A site may serve both purposes only after the user explicitly selects it for
both. Never copy a competitor's Site Map or design wholesale.

## Capability order

For every selected URL:

1. Detect a real controllable Browser.
2. Open the live rendered site and exercise it.
3. If login is required, keep the session open, ask the user to log in there,
   and wait. Never request or type their password.
4. Only when Browser support is unavailable or an actual rendered attempt
   fails, try Fetch.
5. If Browser and Fetch both fail, stop in `reference` and request another
   accessible source.

Do not treat HTML, DOM, linked CSS, source text, search snippets, or a single
static screenshot as equivalent to rendered Browser research.

## Required coverage

Inspect when present:

- homepage;
- one representative Information page;
- one representative Listing page;
- one representative Detail page.

Capture or record:

- full-page Desktop and Mobile views;
- URL, viewport, inspection time, and operations;
- a full scroll through each representative page;
- Hover, Focus, Click, Tabs, Accordion, Filter, Carousel, Slider, and other
  meaningful states;
- scroll-linked Header or Section behavior;
- animation trigger, start/end state, timing, sequence, range, and fallback
  when motion is important.

Use DOM/CSS measurements only to support visible findings, such as Container
width, spacing, type size, Grid columns, Sticky offsets, media ratios, and
Breakpoints.

## Navigation research is mandatory

Inspect and record:

- first-level labels, order, spacing, logo placement, utility actions, and main
  action;
- second-level hierarchy, grouping, columns, descriptions, imagery, and links;
- Dropdown, Mega Menu, Drawer, Accordion, or another presentation form;
- default, scrolled, Sticky, hidden/revealed, active, Hover, Focus, open, and
  close states;
- trigger, delay, duration, easing, backdrop, pointer path, and Focus behavior;
- Mobile menu button, panel origin, overlay, nesting, back action, scroll lock,
  outside click, Escape, and close button;
- differences between Desktop and Mobile information priority;
- accessible/usability strengths and risks.

Do not infer second-level navigation from URLs. Open it.

## Evidence labels

Label every important finding:

- `Observed`: directly seen and exercised in the rendered Browser;
- `Fetched`: obtained from non-rendered content;
- `Inferred`: reasoned from incomplete evidence.

Record page, location, viewport, state, behavior, evidence path, confidence,
limitation, and whether it is a layout principle, interaction principle, or
proprietary asset. Never report Fetched or Inferred interaction as Observed.

## What to extract

Extract reusable principles:

- Section order, composition, height rhythm, and Section-local widths;
- Open, List, Grid, editorial, split, full-bleed, Card, or Bento use;
- information density and media rhythm;
- typography character and Chinese suitability;
- color, surface, border, radius, shadow, and scrollbar behavior;
- Hero copy/background relationship and focal point;
- media ratios, loading, transitions, and responsive crop;
- motion intensity, triggers, and reduced-motion clues;
- responsive structural change rather than simple shrinking.

Explicitly record whether the reference contains:

- Card surfaces;
- Bento layout;
- page, Section, button, or decorative gradients;
- Glow, Gradient Orb, Blur Blob, or abstract-gradient Hero;
- decorative 3×2 Grids;
- repetitive Landing Page composition.

Missing evidence does not grant permission. The user must approve retained
principles.

## Asset and copying boundary

Never transfer from the reference into the new website:

- Logo, brand name, auxiliary graphics, or trust marks;
- copy, claims, data, testimonials, or page text;
- images, videos, illustrations, textures, 3D models, or custom icons;
- proprietary source code;
- a complete visual composition.

Keep screenshots and recordings under `docs/evidence/reference/` only as
research evidence. Use user-supplied or verified permitted project assets in
the website.

## Fetch downgrade

When Fetch is used, record the Browser failure, URL, time, accessible pages,
supporting text/DOM evidence, and everything left unverified: rendered layout,
responsive behavior, JavaScript, motion, Hover, and real interaction.

Do not continue when the decision depends on facts Fetch cannot establish.

## Browser-visible review

Summarize research on `review/index.html` in the conversation language:

- selected references and why;
- screenshots or recordings;
- menu and mobile-menu states;
- useful principles;
- principles to reject;
- access limitations;
- links to the neutral website changes supported by the evidence.

The actual website must also receive an honest stage-appropriate update, such
as its own navigation hierarchy, menu behavior, responsive ordering, or broad
Section rhythm. Never paste a reference screenshot into the site as design.
