# Acceptance Checks

Read every generated image and run these checks. Regenerate on any failure — do not
ship an image that fails, and do not rationalise it in the delivery note.

## Universal fails (any route)

| Symptom | Cause | Fix |
|---|---|---|
| Reads as a photo with painterly texture | "NOT a photograph" clause too weak | Strengthen it; stress physical brush + ink bleed into paper fibre |
| Colour dots are perfect circles with hard edges | Model defaulted to vector shapes | Apply the brush-mark clause verbatim: irregular oval / teardrop / comma, feathered edges, varying size |
| Individual roof tiles drawn | "Do NOT draw individual tiles" dropped | Restore the clause; each roof is ONE gesture |
| Cast shadows or light-source modelling present | Flat-plane clause dropped | Restore "no cast shadows, no light source modelling" |
| Walls have gradient shading | Blank-paper clause too weak | Restore "no shading, no texture, no tone" |
| Text, seal, or signature appears | Trailing negative clause dropped | Restore "No text, no seal, no signature, no border, no frame" |
| Subject unrecognisable | Pushed past 风筝不断线 | Reduce abstraction; the source must stay readable |

## Route A — Jiangnan

- [ ] Blank paper ≥ ~45% of canvas.
- [ ] Each roof is one decisive black sweep, not a tiled surface.
- [ ] Walls are pure blank paper.
- [ ] Foliage is clusters of dots/commas, not rendered leaves.
- [ ] Colour is clearly a minority; ink and paper carry the image.
- [ ] Any human is a small pure red mark with no facial or clothing detail.

## Route B — Shizilin

- [ ] Blank + pale grey planes dominate; grey planes are substantial, not wispy.
- [ ] Black ink dots visibly outnumber colour dots (target ~4:1).
- [ ] Wandering contour lines have visibly uneven width and enclose lobed shapes.
- [ ] Dark openings are narrow solid-black bars, not grey rectangles.
- [ ] Image has weight. Weightless and decorative = fail; raise grey planes and dot density.

## Route C — Shuangyan

- [ ] Roof ridge band is slender — roughly one twelfth of canvas height. A thick heavy
      bar is the signature failure of this route.
- [ ] Empty sky above the ridge is clearly larger than the ridge itself.
- [ ] Walls are absolutely blank; almost no middle tone anywhere.
- [ ] Reflections are soft vertical grey smudges, not mirrored detail.
- [ ] Colour is near-absent apart from small green dabs and a single red dot.

## Plate check

After running `scripts/make_plate.py`, read the output and confirm:

- [ ] All panels are the same height and evenly spaced.
- [ ] Labels are centred under their own panel and not clipped.
- [ ] CJK glyphs render as text, not as tofu boxes (wrong font path).
