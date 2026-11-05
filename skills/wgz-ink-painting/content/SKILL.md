---
name: wgz-ink-painting
description: |
  Translate a real photograph into an authentic Wu Guanzhong (吴冠中) style Chinese
  ink-and-color painting, and optionally build a side-by-side comparison plate.
  Use when the user asks to turn a photo into Wu Guanzhong style, 吴冠中风格/水墨画转译,
  or asks for a Jiangnan water-town / Shizilin / Shuangyan ink rendering of their photo.
  Works best on Chinese garden, water-town, architecture, and landscape photos.
  Do not use for photo-faithful editorial layouts where the original pixels must be
  preserved (use photo-abstract-editorial), for generic "make it artistic" filters,
  or for other painters' styles.
descriptions:
  zh-Hans: "把实拍照片转译成吴冠中风格水墨画，可选三种语言路线并生成对照拼版。"
displayNames:
  zh-Hans: "吴冠中水墨转译"
---

# Wu Guanzhong Ink Translate

Full repaint of a photograph into a Wu Guanzhong brush-and-ink work. This is
intentionally NOT pixel-preserving: repainting is the goal.

## Core principle

The photo is the **compositional source**, not content to be preserved. Feed it to
`image_synthesize` as a reference image and repaint it wholesale. Do not attempt the
"generate panel + locally composite original" approach — that is for faithful-original
skills and does not apply here.

## Procedure

1. **Prep the source.** Read the photo. If it carries a platform watermark band
   (Xiaohongshu = bottom account-number strip + a logo above it), crop the bottom
   8.5–9.5% — 6% only removes the number and leaves the logo. Verify by viewing the
   cropped result.

2. **Pick the style route** (see `references/style-routes.md` for the full prompt of
   each). If the user has no preference, default to **Jiangnan** — most legible and the
   strongest popular read of "Wu Guanzhong".

3. **Generate.** Call `image_synthesize` with `input_file_paths: [cropped photo]` and
   the chosen route's prompt verbatim. Aspect ratio should follow the source
   orientation. Batch multiple photos in one call — the tool accepts up to 10 requests.

4. **Inspect every output.** Read each generated image and check it against
   `references/acceptance.md`. Regenerate any image that fails a check.

5. **Build the comparison plate** if the user asked for one. Use
   `scripts/make_plate.py`.

## Non-negotiable style rules

These separate a real Wu Guanzhong read from generic "Chinese ink filter" output:

- **Black is narrow and intense, not broad.** Roof ridges are slender dense bands;
  dark doorways/windows are tall narrow solid-black bars. A thick heavy black mass
  reads as muddy, not as Wu Guanzhong.
- **White walls are absolutely blank paper.** No shading, no texture, no tone.
  Bounded only by a thin ink line and the black above.
- **Colour is a minority accent.** Ink black / grey / paper white carry the image.
  Clean unmixed vermilion, sap green, yellow — as flat dots and short dashes.
- **Colour dots must read as brush marks.** Irregular oval / teardrop / comma shapes
  with feathered edges and varying size. Perfect circles with hard edges read as
  plastic stickers and instantly kill the illusion.
- **Emptiness is a load-bearing element.** 45%+ blank paper for Jiangnan, 60%+ for
  the abstract routes.
- **Flat picture plane.** No photographic perspective depth, no cast shadows, no
  light-source modelling.
- **风筝不断线.** Abstraction is arrived at by subtraction. The subject must stay
  readable — if the source is unrecognisable, the route has been pushed too far.

## Output contract

- One repainted image per photo per requested route, each visually inspected.
- The comparison plate when requested, with per-panel labels.
- Deliver every image with `<media />` tags — verify each file on disk first.

## Failure handling

- `image_synthesize` returns 0 saved: retry once. If it fails again, simplify the
  prompt (drop markdown structure, write as flowing prose) — heavily formatted prompts
  sometimes fail.
- Output looks like a photo with a painterly overlay: the prompt's "NOT a photograph,
  NOT a filter" clause was too weak. Strengthen it and stress physical brush/paper.
- Colour dots read as stickers: apply the brush-mark clause from
  `references/style-routes.md` verbatim.
- Abstract route feels weightless: add back large pale grey planes and raise the
  ink-dot density — black dots must outnumber colour dots roughly 4:1.

## Windows (win32) platform notes

`scripts/make_plate.py` is cross-platform Python 3 (requires Pillow). On Windows use
`python` instead of `python3`. The CJK font path must be overridden with `--font`,
for example `C:\Windows\Fonts\simsun.ttc`.

## Additional resources

- `references/style-routes.md` - the three verified route prompts
- `references/acceptance.md` - per-route visual acceptance checks
- `scripts/make_plate.py` - build the labelled comparison plate
