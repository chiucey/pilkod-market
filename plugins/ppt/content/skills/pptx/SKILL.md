---
name: pptx
description: >-
  Read, create, and edit PowerPoint PPTX/PPT presentations.
  Covers: parsing, summarizing, extracting content, inspecting themes/layouts, creating new decks with PptxGenJS, and editing existing PPTX while preserving formatting.
descriptions:
  zh-Hans: "读取、创建和编辑 PowerPoint PPTX/PPT，支持解析、总结、抽取内容、检查主题布局和保留格式编辑。"
---

## Scope

Use this skill for PowerPoint `.pptx` work.

- Read slide text, tables, speaker notes, or comments
- Search existing deck content
- Extract embedded images
- Render slide screenshots
- Audit theme, layout, font, color, hyperlink, embedded object, and security metadata
- Create a new deck from scratch with PptxGenJS
- Imitate an existing deck's visual style with new content
- Edit an existing PPTX or template while preserving layout
- Add speaker notes through a validated final-order notes sidecar

Replace `<skill_dir>` with the actual skill path shown by the loader.

## Router

| Need | Workflow |
| --- | --- |
| Existing PPTX inspection, extraction, search, preview, or audit | Use the inspection commands below |
| Existing PPTX provided and layout/style must be preserved | Follow `references/editing.md` |
| Reference PPTX provided for style imitation, but content is new | Run the Template-Preserving Imitation Workflow |
| No source deck, or a fresh deck is acceptable | Run the From-Scratch Workflow |

If the request says "edit" but no source deck is available, assume from-scratch generation and state that assumption.

## Inspection Commands

Default to `uv run --with python-pptx` for all Python workflows except comments, which has no extra dependency.

```bash
# Text, tables, notes, search
uv run --with python-pptx <skill_dir>/scripts/extract_pptx.py file.pptx

# Embedded images
uv run --with python-pptx <skill_dir>/scripts/extract_images.py file.pptx

# Review comments
uv run <skill_dir>/scripts/extract_comments.py file.pptx

# Format / metadata audit
uv run --with python-pptx <skill_dir>/scripts/audit_pptx.py file.pptx

# Screenshots (macOS only)
bash <skill_dir>/scripts/pptx-screenshot.sh file.pptx
```

High-value inspection flags:

- Slide subset: `--slides 1,3,5` or `--range 2-4`
- Text filtering: `--search "term"`, `--regex`, `--ignore-case`
- Speaker notes: `extract_pptx.py --notes`
- Image dry run: `extract_images.py --list-only`
- Comment output: `extract_comments.py --format json`
- Audit scope: `audit_pptx.py --sections metadata,themes,...`
- Screenshot subset: `pptx-screenshot.sh --pages "1,3,5" --outdir ./previews`

`audit_pptx.py` supports these sections:

- `metadata`: document properties
- `masters`: slide masters, layouts, usage counts
- `themes`: theme colors and font schemes
- `shapes`: per-slide shape inventory with position and text preview
- `hyperlinks`: URLs, actions, tooltips
- `embedded`: embedded files and OLE objects
- `security`: MSIP labels and custom XML parts

Use `--format text` only for human inspection. Prefer JSON when downstream processing is likely.

## Generation Defaults

Use these defaults unless the user specifies otherwise **and no template PPTX is provided for imitation**:

- audience: business / professional
- tone: clear, restrained, presentation-ready
- layout: `LAYOUT_16x9`
- Chinese font: `Microsoft YaHei`
- English font: `Arial` unless a better option is justified
- palette and typography: choose from `references/design-system.md`
- page numbers: required on all non-cover slides

When a template PPTX is provided for imitation, the template's actual colors and fonts override these defaults.

## Editable Sidecar Metadata

When Pilkod creates a new PPTX, it must also write a sidecar element map:

```text
slides/output/<descriptive-name>.mavis-ppt-map.json
```

This sidecar is required internal editing metadata for Mavis-generated decks, including static
decks. It must not replace the standard `.pptx` output, change visible slide layout, or change the
`createSlide(pres, theme)` slide-module contract. Use
`references/element-map.md` and `scripts/mavis-ppt-map.cjs` to record stable `elementId`, role,
text, style, and `rectIn` / `normalizedRect` coordinates for meaningful editable elements.

When speaker notes are requested, write
`slides/output/<descriptive-name>.mavis-ppt-notes.json` only after final slide order is known.
Follow `references/speaker-notes.md` and apply it with `scripts/pptx_notes_apply.py`. Notes are
never written by slide modules and do not require an external Office runtime.

For a newly generated Pilkod deck, a complete element map is a delivery gate: fix map coverage
errors before delivery. A third-party or previously existing PPTX may still have no map; that edit
flow remains best-effort and can fall back to preview text, screenshots, and coordinates.

## Hard Constraints

These are mandatory unless the user explicitly overrides them:

1. Use `LAYOUT_16x9` for from-scratch decks. For template-preserving imitation, detect the template's actual slide size and use the matching PptxGenJS layout.
2. **Canvas boundary rule**: coordinates must match the active layout. `LAYOUT_16x9` is **10" wide x 5.625" tall**; `LAYOUT_WIDE` is **13.333" wide x 7.5" tall**. Every element must satisfy `x + w <= slideWidth` and `y + h <= slideHeight`.
3. Create one file per slide: `slides/slide-01.js`, `slides/slide-02.js`, ...
4. Each slide file must export synchronous `createSlide(pres, theme)`.
5. Never use `async` / `await` in `createSlide()`.
6. Theme keys must be exactly `primary`, `secondary`, `accent`, `light`, `bg`.
7. Colors must be 6-character hex strings without `#`.
8. Do not encode opacity into hex strings.
9. All non-cover slides must include a page number badge. For from-scratch `LAYOUT_16x9`, place it near x `9.3`, y `5.1`; for template-preserving imitation, place it in the template profile's footer/source/body region.
10. Chinese text should use `Microsoft YaHei`.
11. Speaker notes must use `mavis.ppt_notes.v1`, final one-based slide numbers, atomic write, and
    exact semantic readback as defined in `references/speaker-notes.md`.
12. Do not reuse mutable PptxGenJS option objects across calls.
13. Output filename must be descriptive; never use `presentation.pptx`.
14. Run QA before returning the deck — this is a **blocking gate**, not optional. Do NOT return the deck to the user until QA is complete. See `references/pitfalls.md` for the QA process.
15. When imitating a template, use the template's actual fonts. Only fall back to `references/design-system.md` font pairings when no template is provided.

## From-Scratch Workflow

Use this when no source PPTX must be preserved.

1. Derive a concise outline from topic, audience, purpose, and expected depth.
2. Pick one palette, font pairing, and style recipe from `references/design-system.md`.
3. Assign each slide one page type from `references/slide-types.md`.
4. Create `slides/slide-XX.js` modules and keep layout variety where the outline calls for it. Use
   mapped helpers for every meaningful editable object so `elementId` is also the PPT object name.
   Create one map slide entry for every PPT slide.
5. Run the pre-compile lint in `references/pitfalls.md#pre-compile-lint` before compiling.
6. Create `slides/compile.js`, load slide modules in final order, and write
   `slides/output/<descriptive-name>-static.pptx` when speaker notes are requested, otherwise the final name.
7. Write the complete content element map and assert its slide coverage.
8. Run `sanitize_pptx.py` on the compiled output.
9. If speaker notes are requested, write `mavis.ppt_notes.v1` using final slide numbers and run
   `pptx_notes_apply.py` to produce `slides/output/<descriptive-name>.pptx`.
10. Run the QA process in `references/pitfalls.md#qa-process`, fix issues, and re-verify.

Minimal compile shape:

```javascript
const pptxgen = require('pptxgenjs');
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';

const theme = {
  primary: '22223b',
  secondary: '4a4e69',
  accent: '9a8c98',
  light: 'c9ada7',
  bg: 'f2e9e4'
};

require('./slide-01.js').createSlide(pres, theme);
pres.writeFile({ fileName: './output/my-deck-name.pptx' });
```

## Template-Preserving Imitation Workflow

Use this when the user provides a reference PPTX for visual style, but all content is new.

Default to **template-preserving imitation** whenever a template PPTX is provided. A flattened
visual copy (full-slide screenshots/backgrounds plus newly drawn text) is a degraded mode and is
allowed only when the user explicitly says exact template formatting/editability is not required.

### Non-Negotiable Ownership Rules

Keep these rules in the active context before planning slides:

1. **Structural pages are template-owned.** Cover, TOC, section-divider, ending, and disclaimer
   slides must be cloned from the template and filled with `structural_fill.py`. Never recreate
   those pages with PptxGenJS in template-preserving mode.
2. **Content pages are generation-owned.** Ordinary analysis/data/content pages may be generated
   with PptxGenJS, but fixed logo/ribbon/footer/header chrome must come from the original template
   chrome asset/profile. If a clean chrome asset is not available, extract it from a rendered
   template content slide by removing/masking non-chrome content; do not redraw the chrome.
3. **Flattened background + `addText()` is not template-preserving.** Using assets such as
   `cover-full-bg.png` or `content-bg.png` as a full-slide background and then drawing structural
   page text with PptxGenJS is a visual-only shortcut. Label it as flattened visual imitation
   unless the user explicitly approved that mode.
4. **Hand-drawn chrome is not original chrome.** Do not use Pillow, SVG, or PptxGenJS primitives
   to approximate template logos, ribbons, waves, city silhouettes, taglines, or footer text. A
   script that draws a red circle plus "Changjiang Securities" text is a degraded visual copy, not
   preserved template chrome.
5. **Do not downgrade QA.** Visual review is useful, but it cannot replace structural fill,
   chrome profile creation, reserved-zone lint, crop diff, merge, or final audit checks required
   by this workflow.

### Step 1: Analyze Template Visual Identity

1. Take screenshots of 3-5 representative slides: cover, a content-heavy slide, and a data slide.
2. Run `audit_pptx.py --sections themes,masters,shapes` to extract theme colors, fonts, and layout usage.
3. Determine dark-mode vs light-mode:
   - Check the most-used slide layouts. If their backgrounds use `dk1`/`dk2` colors with dark values such as `1A1A1A` or `0D0D0D`, the template is dark-mode.
   - Look at screenshots: dark backgrounds with light text indicate dark-mode.
4. Record the template's visual identity:
   - Slide background color
   - Primary text color
   - Accent color(s)
   - Card/panel background color
   - Font families for title and body

### Step 2: Build Content Chrome Profile

For template-preserving imitation, content slides must preserve the template's fixed visual chrome
(logo, ribbon, footer, page-number decorations) without relying on structural slide masters during
merge. Use a full-slide **opaque** chrome image for content pages, plus structured reserved zones.

1. Choose the most representative **ordinary content** slide or blank content layout screenshot. Do not use cover, TOC, section-divider, ending, or disclaimer chrome for ordinary content pages.
2. Build the chrome asset from the template, using this order:
   - Best: render a blank/ordinary content layout where the template already shows only fixed chrome.
   - If no blank content page exists: clone/render an ordinary content slide, then remove or mask
     only the non-chrome content area. Keep the original rendered logo/ribbon/footer/header pixels.
   - If masking is needed, clear old title/body/card/chart regions to the template background color,
     but do not redraw any logo, ribbon, wave, skyline, tagline, or footer text.
   - If original chrome pixels cannot be extracted, stop and label the output as flattened visual
     imitation unless the user explicitly accepts that degraded mode.
3. Create `slides/template-chrome-profile.json` before planning content page layouts.
4. The profile must include:
   - `chrome.asset`: a full-slide opaque image that preserves logo/ribbon exactly.
   - `chrome.source`: the template slide/screenshot used to derive the asset, and whether content
     regions were masked.
   - `reservedZones`: fixed logo/ribbon/footer/header zones that content must not overlap.
   - `contentRegions`: named layout regions such as `title`, `body`, and `source`.
   - `safeArea`: a coarse fallback rectangle only. Do not use one global `safeArea` as the primary layout plan when logo/ribbon chrome is non-uniform.

Example profile creation:

```bash
uv run --with pillow <skill_dir>/scripts/template_chrome_profile.py \
  --template template.pptx \
  --chrome-image slides/previews/content-chrome.png \
  --chrome-source-slide "slide 6 ordinary content page" \
  --chrome-source-method masked-template-render \
  --reserved-zone topRibbon,0,0,13.33,0.35 \
  --reserved-zone logo,10.4,0.55,2.0,0.65 \
  --reserved-zone footerRibbon,0.7,6.9,12.1,0.35 \
  --safe-area 0.75,0.55,11.85,6.10 \
  --content-region "title,0.75,0.55,9.35,0.65,title" \
  --content-region "body,0.75,1.25,11.85,5.15" \
  --content-region "source,0.75,6.20,9.80,0.25,source|footnote" \
  --out slides/template-chrome-profile.json
```

If manual zones are not obvious, use `--auto-red-zones` to get a first pass from the rendered
chrome screenshot, then inspect and correct the profile before generating slides:

```bash
uv run --with pillow <skill_dir>/scripts/template_chrome_profile.py \
  --template template.pptx \
  --chrome-image slides/previews/content-chrome.png \
  --chrome-source-slide "slide 6 ordinary content page" \
  --chrome-source-method masked-template-render \
  --auto-red-zones \
  --out slides/template-chrome-profile.json
```

The chrome asset is part of generation, not a style hint. The agent may look at screenshots to
understand style, but it must not redraw or approximate the logo/ribbon. It must place the original
chrome asset and use `contentRegions` for layout. A top-right logo should constrain the title band,
not force the entire body to be narrow; a footer ribbon should constrain the footer band, not the
main body. Use `safeArea` only as a backward-compatible fallback.

Chrome asset acceptance checklist:

- The `chrome.asset` image is derived from a rendered template slide/layout, not generated from
  scratch.
- `chrome.source.method` describes the extraction method, such as `rendered-template-image` or
  `masked-template-render`.
- Any masking only removes old content. It does not redraw or approximate logo/ribbon/footer
  artwork.
- Handcrafted helper scripts such as `make_chrome.py` that draw logo/ribbon with Pillow primitives
  are allowed only in explicitly approved flattened visual imitation mode.

### Step 3: Classify Slides — Structural vs Content

Based on Step 1's screenshots and audit output, classify every template slide as either **structural** (preserve original, fill text only) or **content example** (reference for PptxGenJS style generation).

Write `slides/template-classification.json`:

```json
{
  "structural": [
    {"idx": 0, "slideId": "cover", "type": "cover", "fillSlots": [{"shapeName": "文本框 2", "elementId": "cover.title", "role": "title"}, {"shapeName": "文本框 13", "elementId": "cover.subtitle", "role": "subtitle"}]},
    {"idx": 2, "slideId": "toc", "type": "toc", "fillSlots": [{"shapeName": "文本框 6", "elementId": "toc.item-01", "role": "item1"}]},
    {"idx": 3, "slideId": "section-01", "type": "section-divider", "fillSlots": [{"shapeName": "文本框 3", "elementId": "section-01.number", "role": "number"}, {"shapeName": "文本框 5", "elementId": "section-01.title", "role": "title"}, {"shapeName": "文本框 6", "elementId": "section-01.desc", "role": "desc"}]},
    {"idx": 22, "slideId": "ending", "type": "ending", "fillSlots": []}
  ],
  "contentExamples": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
}
```

Classification guidelines (model judges, no hard-coded logic):

| Type | Characteristics |
| --- | --- |
| `cover` | First page, large title + brand decoration, minimal text slots |
| `toc` | Section number list ("01", "02" ...) + short titles, "目录" / "CONTENTS" |
| `section-divider` | Full-page background image or large number + short title, separates chapters |
| `ending` | "THANKS" / "Thank You" / farewell-only |
| `disclaimer` | Legal / compliance boilerplate |
| content example | Everything else — data, analysis, charts, multi-column layouts |

`fillSlots[].shapeName` comes from `audit_pptx.py` shape name field. `fillSlots[].elementId`
is the stable logical identity used by the element map; template shape names are not renamed.
`fillSlots[].role` is one of: `title`, `subtitle`, `number`, `desc`, `item1`-`itemN`. Shapes not
listed in `fillSlots` are preserved untouched (decorative, images, logos).

Structural fill guardrails:

- Structural slides must be filled with `scripts/structural_fill.py`; do not hand-write a per-slide `set_text()` helper for cover, TOC, section-divider, ending, or disclaimer slides.
- Do not use full-slide template screenshots/background images plus PptxGenJS `addText()` for structural pages. That is flattened visual imitation, not template-preserving imitation.
- Do not call `text_frame.clear()` and then create a fresh run for structural slide placeholders. That discards the original run properties and can change theme colors such as `bg1` into hard-coded RGB colors.
- Do not set `run.font.color`, `run.font.name`, `run.font.size`, or other run styling on structural slide placeholders unless the user explicitly asks to restyle the template. Replace only the text while preserving the source run's formatting.
- If a structural placeholder needs multiple lines, clone the source paragraph/run properties before adding lines; never use default PowerPoint/PptxGenJS styling for those text runs.

### Step 4: Map to Theme Keys + Detect Slide Size

Map the template's actual colors to the 5-key theme, respecting the template's color roles:

```text
bg        = actual slide background color (may be dark)
primary   = actual body text color (may be light)
accent    = primary accent/highlight color
secondary = secondary/muted text color
light     = card/panel background color
```

Do not pick from `references/design-system.md` palettes. Use the template's actual colors.

Do not assume `bg` is light and `primary` is dark. Dark-mode templates flip this.

**Slide size detection**: Read the template's slide dimensions from `audit_pptx.py` output or `presentation.xml`'s `<p:sldSz>`. Use the matching PptxGenJS layout in compile.js:
- 13.33" × 7.5" → `LAYOUT_WIDE`
- 10" × 5.625" → `LAYOUT_16x9`
- Other → `pres.defineLayout({ name: 'CUSTOM', width: W, height: H })`

This ensures content pages match structural page dimensions after merge.

### Step 5: Use Template Fonts

Use the font families from the template audit, not `references/design-system.md` recommendations. Only fall back to recommended pairings if the template fonts are unavailable on the target system.

### Step 6: Plan Content + Structural Fill

1. Derive a concise outline from topic, audience, purpose, and expected depth.
2. Assign each **content** slide one page type from `references/slide-types.md`.
3. Write `slides/structural-fill-content.json` for structural pages:

```json
{
  "cover": {"title": "报告标题", "subtitle": "研究所名称"},
  "toc": {"items": ["章节一标题", "章节二标题", "章节三标题"]},
  "sectionDividers": [
    {"slideId": "section-01", "number": "01", "title": "章节一标题", "desc": "简述内容"},
    {"slideId": "section-02", "number": "02", "title": "章节二标题", "desc": "简述内容"}
  ]
}
```

4. Write `slides/merge-order.json` specifying final slide sequence:

```json
[
  {"source": "structural", "slideIdx": 0, "slideId": "cover"},
  {"source": "structural", "slideIdx": 1, "slideId": "toc"},
  {"source": "content", "slideIdx": 0, "slideId": "market-overview"},
  {"source": "content", "slideIdx": 1, "slideId": "growth"},
  {"source": "structural", "slideIdx": 2, "slideId": "section-01"},
  {"source": "content", "slideIdx": 2, "slideId": "outlook"}
]
```

### Step 7: Generate (Two-Track)

**(a) Structural pages — python-pptx clone + fill:**

```bash
uv run --with python-pptx <skill_dir>/scripts/structural_fill.py \
  template.pptx \
  --classification slides/template-classification.json \
  --content slides/structural-fill-content.json \
  --out slides/output/structural-base.pptx \
  --element-map-out slides/output/structural-base.mavis-ppt-map.json
```

This clones structural slides from the template, fills text slots using run-level replacement
(preserving font/color/bold), clones section-dividers as needed, copies speaker notes into
independent notes parts, removes content example slides, and cleans orphan media.

**(b) Content pages — PptxGenJS generation:**

Create `slides/slide-XX.js` modules (content pages only) and `slides/compile.js` as usual. Use the detected slide size layout. Write output to `slides/output/content-only.pptx`.

Content pages must load `slides/template-chrome-profile.json`, place the full-slide chrome image
first, and lay out content from named `contentRegions`, especially `body` for ordinary content and
`title` for headings. Do not hard-code a 10" or 10.60" content width after detecting a `LAYOUT_WIDE`
template. Record meaningful content elements in the Pilkod element map sidecar so reserved-zone and
balance lint can run.

```javascript
const {
  loadTemplateChromeProfile,
  addTemplateChrome,
  getContentRegion,
  fitGrid,
  assertNoReservedZoneOverlap,
  assertRectInContentRegion,
} = require('<skill_dir>/scripts/template_chrome.cjs');
const { addMappedText } = require('<skill_dir>/scripts/mavis-ppt-map.cjs');

const chrome = loadTemplateChromeProfile('./template-chrome-profile.json');

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  const map = pres.__mavisElementMap;
  map?.startSlide({ slideNumber: 1, slideId: 'content-01', title: 'Content' });
  addTemplateChrome(slide, chrome);

  const title = getContentRegion(chrome, 'title');
  const body = getContentRegion(chrome, 'body');
  const titleRect = { x: title.x, y: title.y, w: title.w, h: Math.min(0.55, title.h) };
  assertRectInContentRegion(titleRect, chrome, 'title', 'content-01.title');
  assertNoReservedZoneOverlap(titleRect, chrome, 'content-01.title');
  addMappedText(slide, map, {
    elementId: 'content-01.title',
    kind: 'text',
    role: 'title',
    text: '标题',
    ...titleRect,
    options: { fontSize: 24, bold: true, color: theme.primary, margin: 0 },
  });

  const cards = fitGrid({ x: body.x, y: body.y, w: body.w, h: 1.2 }, { cols: 4, gapX: 0.15 });
  // Use cards[i] for KPI/card positions instead of hard-coded x/w constants.
}
```

When using the current merge flow, the chrome image should be a full-slide opaque background. This
masks any inherited structural master visuals and prevents duplicated ribbon/logo artifacts.

**(c) Merge:**

```bash
uv run --with python-pptx <skill_dir>/scripts/merge_decks.py \
  --structural slides/output/structural-base.pptx \
  --content slides/output/content-only.pptx \
  --order slides/merge-order.json \
  --out slides/output/<final-name>-static.pptx \
  --manifest-out slides/output/<final-name>.mavis-ppt-manifest.json
```

The merge drops imported content notes because their original `notesSlideN.xml` targets cannot be
reused safely across decks. When notes are requested, the final-order notes sidecar writes content
notes after merge. Template structural pages and their clones preserve their own notes. Every
merge-order entry must have a unique `slideId`.

Use the `-static.pptx` suffix only when a notes-enhanced output will be produced in the same
workflow. For a static delivery, write `<final-name>.pptx`.

**(c.1) Optional speaker notes:**

```bash
uv run --with python-pptx <skill_dir>/scripts/pptx_notes_apply.py \
  --input slides/output/<final-name>-static.pptx \
  --notes slides/output/<final-name>.mavis-ppt-notes.json \
  --out slides/output/<final-name>.pptx \
  --report slides/output/<final-name>.notes-report.json
```

The notes sidecar uses one-based final slide numbers. Omitted slides keep existing notes; an empty
`text` value clears the selected slide's notes. See `references/speaker-notes.md`.

**(c.2) Post-write structural integrity check:**

Run `sanitize_pptx.py` on the merged output before visual QA. This catches OOXML package issues
(dangling relationships, missing content types, duplicate rIds, orphan files) that would make the
deck fail to open. It auto-repairs what it can and reports what it cannot.

```bash
uv run <skill_dir>/scripts/sanitize_pptx.py \
  slides/output/<final-name>-static.pptx --verbose
```

If sanitize reports unrepairable errors, fix the upstream merge inputs and re-run from step (c).
For from-scratch decks (no merge step), run sanitize on the compiled output before QA. When notes
were written, also run sanitize against the final notes-enhanced output.

**(d) QA:**

Run the QA process in `references/pitfalls.md#qa-process`, fix issues, and re-verify. **Do NOT return the deck until QA passes.**

For Mavis-generated decks, keep the complete
`slides/output/<descriptive-name>.mavis-ppt-map.json` next to the PPTX.

## Delivery Messaging and Speaker Notes

After delivering a static Mavis-generated PPTX, tell the user that speaker notes remain available
as a follow-up. Use equivalent wording in the user's language:

> 已生成静态 PPT，并保留了可编辑元素映射。需要的话，我可以基于当前文件继续添加演讲者备注，无需重新制作版式。

The notes pass works on a copy after final assembly. It changes notes only and never replaces the
static source.

After notes delivery, say that speaker-note text was written and read back.

For template-preserving imitation content pages, run chrome-aware QA before delivery:

```bash
uv run --with python-pptx <skill_dir>/scripts/chrome_reserved_lint.py \
  --profile slides/template-chrome-profile.json \
  --element-map slides/output/<descriptive-name>.mavis-ppt-map.json

uv run --with pillow <skill_dir>/scripts/chrome_crop_diff.py \
  --profile slides/template-chrome-profile.json \
  --rendered 'slides/output/previews/content-*.png'

uv run --with python-pptx <skill_dir>/scripts/chrome_layout_balance_lint.py \
  --profile slides/template-chrome-profile.json \
  --element-map slides/output/<descriptive-name>.mavis-ppt-map.json
```

`chrome_reserved_lint.py` fails if generated elements overlap logo/ribbon/footer reserved zones or
leave the expected `contentRegions`/fallback `safeArea`. `chrome_crop_diff.py` fails if rendered
reserved-zone crops differ from the original chrome asset, catching accidental overlays on the
logo/ribbon.
`chrome_layout_balance_lint.py` fails if body content is packed to one side or underuses the
template profile's `contentRegions.body`.

Before delivery, classify the output honestly:

- If structural pages were recreated with PptxGenJS, or the final audit shows every slide using a
  single PptxGenJS default layout, the result is **flattened visual imitation**. Do not claim it
  preserved the template structure.
- If the user did not explicitly approve flattened visual imitation, go back to the two-track flow:
  `structural_fill.py` for structural pages, PptxGenJS for content pages, then `merge_decks.py`.
- Do not mark `Build chrome profile`, `Structural fill`, `Merge`, `chrome_reserved_lint`, or
  `chrome_crop_diff` complete unless the corresponding artifact/command exists in the workspace.
- Do not mark content layout QA complete unless generated content used `contentRegions` and passed
  `chrome_layout_balance_lint.py`, or the user explicitly requested an asymmetric layout.

Skip palette/font selection (step 2 of From-Scratch) because palette and fonts come from the template.

## Template Editing Workflow

Use this when the user provides a source PPTX and expects structure or layout to survive.

- Prefer preserving slide masters, theme relationships, and layout semantics.
- Complete structural edits first, then content edits.
- Follow `references/editing.md` for XML-level workflow and pitfalls.
- Only switch to from-scratch generation if it does not violate the user's intent.

## Delivery Checklist

- slides render without runtime errors
- layout is `LAYOUT_16x9` (from-scratch) or matches template size (template-preserving imitation)
- no `#` in colors
- all slide modules are synchronous
- all non-cover slides include page numbers
- no placeholder/demo text remains
- titles do not wrap awkwardly
- repeated elements align consistently
- final file is written successfully
- `sanitize_pptx.py` passes with no unrepairable errors (run on every final PPTX before delivery)
- every newly generated Pilkod deck includes a complete element-map sidecar without changing the `.pptx` output contract
- static delivery tells the user that speaker notes can be added later without rebuilding the layout
- requested notes have a passing notes report with exact semantic readback
- inspection/editing tasks preserve the source file unless explicitly replacing it
- template-preserving imitation background color matches the template's dark/light mode
- template-preserving imitation fonts match the template's font families
- template-preserving imitation structural pages are produced by `structural_fill.py`, not recreated with PptxGenJS
- template-preserving imitation content pages use `template-chrome-profile.json` when fixed logo/ribbon chrome should be preserved
- template-preserving imitation content elements pass `chrome_reserved_lint.py`
- template-preserving imitation rendered previews pass `chrome_crop_diff.py` for comparable reserved zones
- template-preserving imitation body content passes `chrome_layout_balance_lint.py` against `contentRegions.body`
- final audit is not an all-slides PptxGenJS default-layout deck unless the user explicitly approved flattened visual imitation

## Operational Notes

- Screenshots are macOS-only and require `soffice` plus `swiftc`.
- `extract_comments.py` supports classic comments only, not modern Office 365 collaborative comments.
- If targeted `python-pptx` editing is needed, read `references/python-pptx-recipes.md` on demand instead of keeping those patterns in main context.

## Windows (win32) platform notes

On Windows, invoke bash scripts and piped commands via **Git Bash**:

```powershell
# QA verification with markitdown
bash -c "python -m markitdown output.pptx | grep -iE 'xxxx|lorem|ipsum|placeholder'"

# Python inspection via uv
uv run --with python-pptx scripts/extract_pptx.py file.pptx
```

> **Note:** `scripts/pptx-screenshot.sh` is **macOS-only** (requires Swift compiler + soffice).
> On Windows, use LibreOffice GUI export or `python-pptx` + pillow for slide previews.

| Unix reference | Windows handling |
|---|---|
| `python3` / `python -m` | `python` — works in both PowerShell and Git Bash |
| `/tmp/` for temp writes | Git Bash maps `/tmp/` automatically |
| `soffice` | Must be on PATH — `winget install TheDocumentFoundation.LibreOffice` |

**If Git Bash or any required tool is missing**, read
`references/windows-tool-bootstrap.md` for detection and setup guidance.

## References

### Mandatory for Generation Tasks

Read these **before writing any slide code**. Do not skip them even if you think you already know the API:

- `references/pitfalls.md`: pre-compile lint, QA process, common PptxGenJS failures — **must run lint and QA**
- `references/pptxgenjs.md`: PptxGenJS API, layout dimensions, text/shape/table options — **must verify canvas dimensions**
- `references/slide-types.md`: page type classification and layout patterns — **must assign a type to each slide**
- `references/element-map.md`: required internal sidecar metadata for Mavis-generated decks — **must not replace the PPTX output contract**
- `references/speaker-notes.md`: direct OOXML speaker-note contract — **mandatory when speaker notes are requested**

### Load On Demand

- `references/design-system.md`: palette, typography, style recipes (skip when imitating a template)
- `references/editing.md`: template-preserving editing workflow
- `references/python-pptx-recipes.md`: targeted python-pptx inspection or editing patterns
- `references/windows-tool-bootstrap.md`: Windows dependency detection and setup guidance
