# Structure, content, visual, Hero, and motion rules

## Rule levels

- **Forbidden**: do not create it unless the stated exception is explicitly
  approved.
- **Required**: implement and inspect when its condition applies.
- **Recommended**: prefer it, but choose a simpler, safer, more accessible, or
  more performant result when justified.

Record exceptions in the owning source document and `project-state.yaml`.
“Modern,” “award-caliber,” current fashion, or a library demo is not evidence.

## Anti-AI foundation

Use this text verbatim in the global design prompt:

```text
Never create a website that feels AI-generated.

Avoid repetitive layouts, generic SaaS aesthetics, default component
libraries, common gradients, excessive rounded corners, overused
glassmorphism, repetitive card grids, placeholder illustrations, and
predictable landing page structures.

Every section should have its own purpose, composition, rhythm, and visual
identity.
```

Operationally:

- reject interchangeable SaaS templates and library-default appearance;
- do not force Hero → Logo Wall → Features → Testimonials → Pricing → FAQ →
  CTA;
- use project-specific people, product, process, place, material, culture,
  language, or evidence;
- give each Section one purpose and a distinct composition while preserving a
  coherent typography, color, spacing, and interaction system;
- keep labeled development Placeholders, but never present generic placeholder
  illustrations as final art.

## Structure and responsive composition

### Independent templates

Count independent templates by distinct information goal, Section order,
field/media relationship, navigation path, or presentation interaction, not by
the number of repeated URLs.

Use:

| Scope | Templates |
|---|---:|
| Focused | 1–5 |
| Standard | 6–12 |
| Full-site | 13–20 |
| Custom | 20+ with explicit batches and priorities |

Each content collection needs one Listing Template and at least one
representative Detail Template.

Test:

- 2560×1440;
- 1920×1080;
- 1180×820;
- 820×1180;
- 390×844.

These are representatives, not hard supported widths. Resize around them.

### Section-local Containers

Every Section owns an inner Container. Never wrap every page Section in one
page-level Container.

```html
<section class="section section--intro">
  <div class="container container--md">...</div>
</section>
```

Define project-specific `xs`, `md`, `xl`, and `full` roles with `width: 100%`,
`max-width`, `margin-inline: auto`, and fluid horizontal padding. Let Section
background colors, images, or video span full width outside the Container.
Keep Mobile gutters even on `full`; remove them only for a specifically
approved full-bleed element.

Vary Container widths intentionally to create horizontal rhythm. Do not vary
them randomly.

### Section rhythm and action count

Unless an approved full-page-scroll or split-screen concept requires it, let
content determine Section height. Do not give consecutive Sections identical
fixed height or `min-height`.

Use at most one dedicated CTA Section per page. It may contain multiple clearly
prioritized buttons. Hero, Header, Footer, text links, and content-specific
actions are not dedicated CTA Sections.

### Forbidden 3×2 and nested Cards

Do not default six equal items into a decorative three-column-by-two-row Grid.
Keep repeated Section items to one Desktop row by default. Multiple rows are
allowed for a real Listing or an approved need to show many Features. Consider
a list, Slider, pagination, “view more,” or Detail page first. Never invent or
duplicate content to fill the arrangement.

When Cards are approved, never put another rounded, bordered, shadowed, or
surfaced Card inside one. Use media, typography, spacing, dividers, lists, and
status text for internal hierarchy.

## Card, Bento, Gradient, and decoration gates

### Cards

When neither the reference nor the user approves Cards, do not create repeated
rounded, bordered, shadowed, floating, or surfaced content blocks. One reduced
style property does not bypass this rule when the composition still reads as a
Card system.

Prefer open layouts, Lists, indexes, columns, dividers, alternating media/text,
large media, whitespace, and typography.

### Bento

Do not create Bento unless:

1. the selected reference visibly uses it and the user retains it;
2. the user explicitly requests it; or
3. one product/service has several concentrated Features, the Agent recommends
   Bento, and the user approves.

### Gradients and abstract Hero art

Without approved reference evidence or explicit user approval, do not create
page, Section, button, decorative, Glow, Gradient Orb, Blur Blob, gradient mesh,
or abstract-gradient Hero treatments.

One narrow exception is a clearly labeled gradient Placeholder inside a
missing image/video region. Never promote it into final Hero art.

Search CSS/assets for `linear-gradient`, `radial-gradient`, and
`conic-gradient` during QA and match every occurrence to an approval or
Placeholder.

### Emoji and icons

Do not use Emoji in navigation, headings, buttons, Feature lists, decoration,
or functional controls unless the approved brand language requires them.

Use Lucide as the default placeholder/general interface icon system. Do not add
an icon to every heading or use icons as filler.

## Content and media

### Writing approach

After the content outline and before full copy, derive three or four
project-specific writing approaches from the industry, audience, relationship,
brand position, conversion goal, known evidence, language, and existing copy.

For each, hold facts and approximate information amount constant and show:

- a plain-language name;
- formality, warmth, energy, information density, and terminology behavior;
- why it fits and what could go wrong;
- the same homepage headline, introduction, and main-button text.

Recommend one. Let the user select one, combine at most two, define a custom
approach, or retain an existing brand style. Do not show a fixed “professional,
friendly, creative” menu for every industry and do not use unexplained
`copy voice`.

Never invent testimonials, clients, awards, metrics, certifications, pricing,
product capability, or other evidence.

### Density and media rhythm

Give each Section one main point. Separate Listing preview information from
Detail information. Do not shrink type, compress spacing, or add columns merely
to fit all facts.

Prefer when appropriate:

- media or Placeholder + title + short introduction + necessary metadata for
  Listings;
- alternating media/text Feature rows;
- short centered copy over purposeful background media with sufficient
  contrast and fallback;
- headings, readable line length, Table of Contents, anchors, lists, spacing,
  and dividers for long-form pages.

Do not turn these into Card or Bento surfaces without approval. Add media only
when it contributes information, proof, atmosphere, or browsing rhythm.

Use `<strong>` sparingly for phrases that help scanning. Do not bold whole
paragraphs. Keep copy specific and concise.

### Source assets and media generation

Tell the user they may place approved copy, documents, spreadsheets, PDFs,
images, video, and Logo files in one folder. Inspect recursively and record
filename, type, dimensions/duration, language, likely subject, rights note,
duplicate candidates, and proposed page/Section.

Do not delete, rename, move, overwrite, or silently transform originals.
Presence does not prove usage rights. Do not expose private sources publicly.

For every media gap, let the user choose:

1. existing approved media;
2. generated media;
3. verified permitted Pexels/Unsplash media;
4. clearly marked Placeholder;
5. later upload;
6. no media.

Before Image Generation, confirm a named small batch: purpose, subject,
composition, count, aspect ratio, minimum dimensions, focal point, Desktop/
Mobile crop, style, exclusions, output location, and factual/conceptual status.
Generate only after explicit approval. Show candidates and wait for selection.
Only selected candidates enter HTML.

Ask about Logo separately. Confirm exact real brand text, language, symbol/
wordmark/combined form, style, backgrounds, lockups, colors, and PNG sizes.
Explain that a generated PNG is a raster concept, not a vector master,
trademark clearance, or proof of uniqueness. Reject malformed or misspelled
lettering.

Never present generated media as a real client, project, product, team member,
location, result, testimonial, award, certification, or news event. Keep
headlines, buttons, claims, and data as real HTML.

For stock media, verify current permission and restrictions at use time.
Record source URL, author, date, attribution, Alt, crop, and focal point. Do not
use search thumbnails or generic handshake/meeting-room filler.

### Media loading

For important images/video:

- reserve geometry with width/height or `aspect-ratio`;
- provide Placeholder/Poster/loading state and failure fallback;
- choose eager/preload/lazy behavior by location;
- transition after load without hiding content indefinitely;
- simplify under reduced motion;
- keep no-JavaScript content usable.

## Typography

Build deliberate Display/Heading, secondary label, and Body roles. Use a
purposeful Heading/Body difference by default; a single-family system needs
concept evidence.

For Chinese UI/body without another approved direction, prefer:

```css
--font-family-zh-sans:
  "SF Pro SC",
  "SF Pro Display",
  "PingFang SC",
  "Helvetica Neue",
  Helvetica,
  Arial,
  sans-serif;
```

Use another Chinese sans, Song/serif, calligraphic, or expressive Display face
only when it fits and has valid licensing. Record source, loading, fallback,
and failure.

For Chinese and multilingual pages containing Chinese:

- keep default H1 at or below 64px, with a smaller Mobile value;
- test real long headings for wrap, line height, and overflow;
- use bold for primary H1/H2/H3 visual roles;
- use normal weight for a paired secondary-heading role unless approved
  otherwise;
- preserve semantic H1–H6 order and express visual roles with classes;
- keep Chinese `letter-spacing: normal` or `0`, including buttons and
  navigation.

## Components and interaction

- Do not enlarge Button, Icon, Logo, navigation, label, or ordinary interface
  surface on Hover/Focus using `scale()`, font size, width, or height.
- Use color, background, border, underline, restrained translation, mask,
  shadow intensity, and visible Focus.
- A restrained image/video-cover scale is allowed inside a stable
  overflow-hidden media container without layout shift.
- Design a supported native Desktop scrollbar from approved tokens. Keep native
  fallback; never build a JavaScript fake scrollbar.
- Keep semantic landmarks, headings, lists, links, buttons, forms, figures,
  keyboard order, visible Focus, Skip Link, labels, and accessible menu
  behavior.

## Visual-direction process

1. Read approved `spec.md` and current layout.
2. Identify project-specific narrative material.
3. Propose two or three genuinely different concepts, not color variations.
4. For each, define business relevance, typography, composition, density,
   color/material, media, Hero focal moment, motion character, Mobile
   adaptation, risks, and deliberate exclusions.
5. Ask the user how they want to compare the concepts:
   - generated still mockups;
   - live HTML concept previews;
   - a purposeful combination.
6. Recommend the comparison medium based on the decision:
   - use generated stills for atmosphere, art direction, Hero imagery,
     photography/illustration language, unusual materials, or high-concept
     visual worlds;
   - use HTML for palette, typography, Chinese wrapping, spacing, contrast,
     components, interaction states, responsive behavior, and realistic page
     rhythm;
   - use both only when neither alone can answer the important questions.
7. For generated stills, create two or three project-specific full-page
   keyframes, representative Section/Hero mockups, or style/palette boards.
   Keep the same approved content goal across options and show them on the
   review page.
8. For HTML concepts, preserve approved content and layout while varying only
   the design direction. Use isolated styles or a comparison route under
   `review/visual-options/`; do not overwrite the actual website with every
   unselected option.
9. An HTML design-system comparison may show:
   - named color Tokens and swatches on light/dark or approved backgrounds;
   - real heading, secondary heading, paragraph, emphasis, and Chinese/Latin
     mixed samples;
   - buttons, links, navigation, forms, icons, dividers, media, loading/error,
     Focus, Hover, Active, Disabled, and reduced-motion examples;
   - Section-local Container widths and representative Desktop/Mobile
     compositions.
10. Recommend one concept and wait for selection.
11. Apply only the selected concept to the actual homepage.
12. Inspect Desktop/Mobile and obtain rendered approval.
13. Extract Tokens/components, then apply to every template family.
14. Review visual drift, anti-AI rules, accessibility, and performance.

Generated mockups and style cards are decision aids, not website assets unless
separately approved. They cannot prove responsive behavior, real text wrapping,
contrast, accessibility, interaction states, or implementation feasibility.
Even when the user selects from generated stills, the visual stage is complete
only after the direction is implemented and approved in the actual HTML.

## Hero

Keep semantic title, introduction, and actions in the DOM. A Hero may use an
approved image, video, pure-color field, product media, SVG, Canvas, WebGL, 3D,
or another purposeful scene, but the effect must support the message.

Accept screenshot, URL, recording, source, sketch, or behavior description from
the user, or propose two or three project-specific visible directions. Do not
invent missing behavior or copy proprietary assets/code/composition.

Show left, centered, right, and custom copy placement only when each is viable
against the actual focal point, copy length, CTA count, contrast, and crop.
Recommend one. Desktop and Mobile may differ intentionally.

Ask before adding Logo rail, trust marks, statistics, product media, scroll cue,
or secondary action. Use only permitted logos and assets.

Use a separate iframe only for a useful WebGL/Canvas/3D lifecycle boundary,
dependency conflict, independently runnable user source, or materially safer
failure isolation. Keep semantic content in the parent, provide a Poster/static
fallback, preserve keyboard behavior, and validate `postMessage` origins.

Use plain HTML/CSS for a static horizontal row. Add Swiper.js only for genuine
Touch/Drag/Loop/Navigation/Pagination/responsive-slide needs. Preserve source
order, keyboard, Focus, pause, reduced motion, resize, and no-JavaScript
fallback.

## Motion

Offer:

1. no decorative motion;
2. Agent-recommended motion;
3. page/element-specific requests.

When motion is not skipped, consider two separate passes:

- **GSAP pass** for approved coordinated timelines, ScrollTrigger, Pin, Scrub,
  Hero sequences, or synchronized media/copy;
- **scroll-experience pass** for native scrollbar styling and only purposeful
  Header, progress, reveal, or Section choreography.

Keep simple Hover, Focus, menu, and short transitions in CSS. Centralize GSAP
initialization, cleanup, resize/Breakpoint behavior, and reduced-motion
branching. Do not mix primary animation libraries without a reason.

Do not enable smooth scrolling by default. Use it only when the concept
requires it and Keyboard, mouse wheel, trackpad, Touch, anchors, history,
scroll restoration, Sticky, Focus, reduced motion, performance, and iframe
compatibility all remain correct.

Never leave core content hidden or off-screen when JavaScript fails. Under
reduced motion, keep necessary feedback while removing strong parallax, large
travel, continual motion, unnecessary autoplay, and intense scale.

Record every motion item with page/hook, trigger, start/end, duration, easing,
Desktop/Mobile behavior, reduced motion, fallback, dependency, and status:
implemented, not applicable, or skipped by user.
