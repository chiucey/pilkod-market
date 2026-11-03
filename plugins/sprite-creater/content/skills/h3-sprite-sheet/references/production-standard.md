# Standard sprite and image-sequence delivery contract

Read this reference whenever the requested result is meant to be reused in a
game, website, animation tool, or another program. A visually attractive GIF
is not enough; the files and playback semantics below are the acceptance
contract.

## Minimise conversation rounds without hiding decisions

Do not ask one parameter at a time. Inspect all inputs first, then present one
specification card containing every unresolved item with a recommended choice.
The card must visibly include:

- asset kind: character, object, VFX, UI/image sequence, or scene/wallpaper;
- source route: direct video/GIF processing, existing-sheet repack, or H3
  generation from still reference;
- the primary subject and role of every reference image;
- background: transparent or keep;
- each action ID, loop/oneshot type, boundary behaviour, frame count, and FPS;
- view/facing, direction count, and whether mirroring is allowed;
- cell size, pivot, maximum texture size, style/filtering, and target engine;
- whether ground shadow, weapon trail, projectile, or hit effect belongs in
  the character frames or should be a separate sequence;
- the paid generation task count and retry ceiling.

Do not continue if background, action playback type, cell size, pivot, or paid
scope is absent. After the consolidated card, additional questions are allowed
only for a genuine ambiguity, candidate selection, or a scope/cost change.

## Route arbitrary inputs before calling H3

| Input | Route |
|---|---|
| Existing MP4/MOV/WebM or animated GIF with the wanted motion | Skip H3; validate, extract, align, and pack directly. |
| Existing sprite sheet or numbered PNG sequence | Skip H3; split/reorder/repack and run final QA. Never regenerate it merely because the user said “sprite”. |
| Transparent full-body still | Composite onto the chosen flat key background for H3; final background choice still must be explicit. |
| Full-body single subject on a complex background | Keep only if the user chose keep; otherwise replace only the background with a flat key colour before H3. |
| Half body, cropped limbs, severe occlusion, or tiny/blurred subject | Explain the defect and ask for a better image or explicit permission to outpaint/reconstruct. Mark inferred anatomy/clothing as inference. |
| Multiple subjects | Ask which subject is animated, or split into independent character tracks. Never let H3 silently animate all of them. |
| Multiple reference images | Label each as identity, costume, style, view, or pose reference. Resolve identity/costume conflicts before generation. |
| Non-neutral pose | Use it as pose/style reference or explicitly create a neutral master reference; do not treat it as an idle boundary silently. |
| Character with asymmetrical weapon, logo, text, hair, scar, or clothing | Do not obtain the opposite facing by mirroring unless the user accepts the reversed asymmetry. Generate that direction separately when correctness matters. |
| Object/product | Use centre pivot unless the user specifies a hinge/contact point; define actions such as open/spin/break. |
| VFX | Use centre pivot, transparent background, no character reference unless compositing is intentional; prefer a separate atlas. |
| Scene/dynamic wallpaper | Use centre pivot, keep background by default, lock camera and scene geometry, and animate only the named layers in a forward loop. |

One atlas represents one subject, one visual scale, and one view/facing profile.
Multiple characters or incompatible views become separate atlases.

## Action boundary contracts

Every action must have a written boundary contract before generation. “Make it
walk” is incomplete.

- `idle` loop: one stable base cycle. Keep feet/root planted. Export blink,
  twitch, flourish, or other rare events as separate oneshots unless the user
  explicitly wants them in every idle cycle.
- `walk`/`run` loop: in-place treadmill motion, fixed facing, one complete
  left-right gait cycle, chronological forward time, final boundary matching
  the initial contact phase. No turn, moonwalk, backward phase, or ping-pong.
- `attack`/`cast`/`interact` oneshot: start from an idle-compatible pose,
  include anticipation, readable action/contact, and recovery to an
  idle-compatible pose. Projectiles and hit effects are separate by default.
- `jump` oneshot: idle-compatible takeoff, airborne apex, landing, then an
  idle-compatible recovery pose. If the game separates takeoff/air/land,
  export three actions instead.
- `hurt` oneshot: idle-compatible start, readable impact/recoil, recover to an
  idle-compatible pose unless the gameplay requires stun/knockdown.
- `death` oneshot: idle-compatible start, full collapse, stable final hold;
  do not return to idle.
- object/VFX/UI sequences: explicitly state whether the last frame holds,
  returns to the initial frame, disappears, or hands off to another state.

H3 prompts must lock camera, scale, screen position, facing, full-body framing,
background, and a single main motion. For loops use the same reference as first
and last frame when FL2VA is available. A prompt claiming “perfect loop” is not
proof; the exported sequence still must pass seam QA.

## Engine-safe image contract

- Require `--cell-size`; recommended starting points are 128, 256, or 512.
  Non-square cells are allowed when the project requires them.
- Character pivot defaults to bottom-centre. Object/VFX pivot defaults to
  centre. The selected pivot is written to every frame and the manifest.
- Preserve one source canvas and one scale across all actions in an atlas.
  Do not independently auto-centre or fit each action.
- Default padding is 4 px and RGB extrusion is 2 px. Extrusion changes RGB
  under transparent alpha, not alpha coverage.
- Output is PNG RGBA, sRGB, straight alpha, no rotated packing. Pixel assets
  use nearest filtering and a shared palette; non-pixel art uses linear
  filtering in the target engine.
- A single atlas must not exceed the confirmed engine texture limit. Use 4096
  when the target is unknown. Reduce cell/frame count or split the asset rather
  than silently emitting an oversized texture.
- Action IDs are portable ASCII slugs. Human-facing labels may be localised
  outside the file ID.
- Each frame records rect, duration, source frame index, source size, visible
  bounds, pivot, playback type, and independent PNG path.

## Two-layer acceptance gate

The source-video gate and exported-cell gate are both mandatory.

Source video hard failures:

- identity/costume/facing changes, body duplication or broken limbs;
- camera movement, zoom, crop, subject leaving frame, or background collapse;
- incomplete action, wrong action direction, extra subjects, or unintended
  scene/VFX content;
- a loop without one complete chronological action cycle.

Exported sequence hard failures:

- missing/duplicate frame budget, non-chronological source indices, reverse
  phase, freeze-jump rhythm, or loop seam spike;
- any sprite entering the reserved cell padding, empty frame, inconsistent
  canvas, oversized atlas, or missing playback classification;
- key-colour fringe, background residue, incorrect alpha mode, scale jump
  across actions, or pivot/foot drift visible at target cell size;
- oneshot missing the specified start/end state; death returning to idle;
- M3 cannot identify the intended action when watching the final GIF at the
  declared FPS.

M3 must review both the source clip and the final selected-frame playback.
Programmatic metrics decide geometry, order, alpha, budget, and texture limits;
M3 decides identity, anatomy, semantic action phase, facing, and game
readability. Do not average a hard failure into a passing score.

Try at most three zero-cost sampling/FPS variants of the same source. If none
passes, the source motion is unsuitable. Request permission before another
paid H3 generation and retry only the failed action.

## Required delivery

```text
output/
  manifest.json
  atlas.png
  atlas.json
  report.json
  preview.html
  frames/<action>/<action>_000.png ...
  <action>.gif
```

Open `preview.html` before delivery. Check every action on checkerboard, dark,
and light backgrounds; pause and step through every frame; show the pivot;
test the exact declared FPS; keep ping-pong off; and test the oneshot return or
hold behaviour. Deliver only when `meta.qc` is PASS, or when a WARN has been
shown and explicitly accepted. Never deliver FAIL as a finished asset.
