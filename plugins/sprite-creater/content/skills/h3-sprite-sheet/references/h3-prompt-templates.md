# H3 prompts for reusable image sequences

Read this file whenever a still image or text request needs H3 to create new
motion. Existing video, GIF, sprite sheets, and numbered frames do not use
these prompts; process those sources directly.

The generation model is always `MiniMax-H3`. These templates do not authorize
H2.5 or any default-model fallback. If the submitting tool cannot explicitly
select and confirm `MiniMax-H3`, do not submit the video generation request.

The prompt must be written in English and must follow the official MiniMax H3
field names and order. Use one shot, one primary motion, and one action per
clip unless the user explicitly requests a multi-shot sequence. The sequence
source is silent: explicitly request complete silence so both audio fields can
be `N/A`.

Official format references:

- <https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing>
- <https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md>

## Choose the mode

| Need | H3 mode | Reference use |
|---|---|---|
| Loop from an approved still | FL2VA | Use the same approved image as Picture 1 and Picture 2. |
| One-shot from an approved still | I2VA | Use the approved image as Picture 1. |
| Text-only concept | T2VA | Create and approve a master still first when identity or exact composition matters. |
| Several identity/style/action references must remain separate | Ref2VA | Use the official six-section reference format; do not flatten conflicting references silently. |
| Existing motion video/GIF | No H3 | Extract and pack directly. |

When the official `h3-prompt-writing` capability is available, use it and pass
the action contract below as the brief. Otherwise fill the templates in this
file exactly. Do not invent alternate field names or reorder fields.

## Shared constraints

Briefly anchor the subject, visual style, proportions, framing, composition,
facing, and background established by the reference. Do not redesign the
appearance or add unrequested clothing, props, text, characters, scenery, or
effects. “Only describe motion” is insufficient: H3's I2VA format requires the
opening image anchors to be established before the motion path.

Every prompt must state observable positive behavior:

- the full subject remains inside the frame at one screen position and scale
  when the source contains a foreground subject;
- the camera holds a completely static shot;
- facing and view remain unchanged unless the requested action is a turn;
- transparent output uses the confirmed flat key colour by name and hex;
- keep-background output preserves the scene layout and limits motion to the
  requested layers;
- one primary motion follows the confirmed action boundary;
- the clip contains complete silence, with no dialogue or music.

Do not ask H3 to recolour the subject to avoid the key colour. Select a key
colour that is absent from the subject before generation.

## FL2VA loop template

Replace `{duration}` with exactly two decimals and use the same approved image
for both pictures. Keep `Shot 1` because this is a single continuous shot.

```text
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot 1) aligns with the {duration}-second mark of the target video.

integrated_multimodal_description: [Shot 1] {style}, a {view} static shot preserves {reference_anchors} and {background} established by Picture 1. {loop_motion} The overall framing and scale remain unchanged throughout. The camera holds a completely static shot. The motion progressively returns to the same action phase, pose, layer positions, and exact composition established by Picture 2 at the end of the shot. The clip is completely silent.

overall_soundscape: N/A

non_diegetic_music: N/A
```

Use one of these action bodies or adapt it without changing the boundary:

- `idle`: one restrained base breathing/sway cycle repeats at a steady cadence;
  feet or root stay planted. Blink, wave, twitch, and flourish are separate
  actions by default.
- `walk`/`run`: the subject repeats an in-place treadmill gait at a constant
  cadence, completes only whole left-right gait cycles, keeps the same facing,
  and finishes on the same foot-contact phase as the opening frame.
- looping expression/sticker: the face or gesture moves from the neutral
  expression through one readable expression and returns to the identical
  neutral expression; unrelated body parts remain stable.
- dynamic wallpaper: only the named layers move gently and continuously, such
  as cloud drift, mist, light, water, hair, or foliage; the camera, horizon,
  scene geometry, and all unlisted layers remain fixed; every moving layer
  returns to its opening phase without reversing time.
- product spin: the object rotates in one direction around the confirmed axis
  at constant angular speed, completes one or more whole 360-degree turns, and
  returns to the opening orientation; scale and centre stay fixed.

Do not write “exactly one gait cycle across the whole clip” for walk/run. A
six-second clip may stretch that one cycle unnaturally. The requirement is a
steady cadence, whole cycles only, and a matching boundary phase.

## I2VA one-shot template

```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] {style}, a {view} static shot preserves {reference_anchors} and {background} established by <Picture 1>. {oneshot_motion} The overall framing and scale remain unchanged throughout. The camera holds a completely static shot. {end_behavior} The clip is completely silent.

overall_soundscape: N/A

non_diegetic_music: N/A
```

Use a complete chronological action path:

- `attack`/`cast`/`interact`: idle-compatible opening, anticipation, readable
  contact/action, follow-through, then recovery to the same idle-compatible
  pose. Keep projectile, hit effect, and weapon trail separate unless included
  by the user.
- `jump`: idle-compatible takeoff, rise, apex, fall, landing, and recovery to
  the same idle-compatible pose. Split takeoff/air/land when the target state
  machine requires separate clips.
- `hurt`: idle-compatible opening, readable impact and recoil, then recovery
  to the requested idle, stun, or knockdown state.
- `death`: idle-compatible opening, complete collapse, then a stable final
  hold. The end behavior states that the final pose remains still through the
  last frame and does not recover.
- expression/sticker oneshot: neutral opening, one readable expression or
  gesture, then either return to neutral or hold the peak expression according
  to the specification card.
- object/UI/VFX oneshot: describe the initial state, observable transition,
  final state, and whether it holds, disappears, returns, or hands off.

For return-home actions, `{end_behavior}` says the final frames settle into the
same idle-compatible pose and composition as the opening frame. For hold
actions, it says the final state remains stable through the last frame.

## Ref2VA fallback

Use Ref2VA only when multiple references must retain distinct roles. Follow the
official six sections in this exact order:

```text
subject_definitions: ...

summary: ...

retention_analysis: ...

detailed_description: ...

overall_soundscape: N/A

non_diegetic_music: N/A
```

Assign stable `<Subject N>`, `<Picture N>`, and `<Video N>` labels. State which
reference provides identity, costume, style, pose, background, or motion. If
two references conflict on identity, costume, view, or facing, stop and resolve
the conflict in the specification card instead of asking the model to guess.

## Prompt audit before submission

Reject or repair the prompt if any item is missing:

- correct H3 mode and exact alignment instruction;
- exact core field names in their required order;
- `[Shot 1]`, requested duration, and a single continuous shot;
- reference anchors for subject/style/composition/background;
- static camera, fixed position/scale, facing, and full-subject framing;
- action-specific start, motion path, end state, and playback semantics;
- named key colour plus hex, or explicit keep-background behavior;
- complete-silence statement and both audio fields set to `N/A`;
- no incidental blink, gesture, turn, camera move, extra subject, or effect;
- no claim that “perfect loop” alone proves loop quality.

The generated clip still has to pass source-video QA and final playback QA.
Prompt compliance is not acceptance proof.
