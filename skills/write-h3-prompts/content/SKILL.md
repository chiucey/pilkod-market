---
name: write-h3-prompts
description: Use when a user wants to expand a rough video idea, creative brief, frame-transition intent, or reference-media plan into a polished MiniMax-H3 prompt for T2VA, I2VA, FL2VA, L2VA, or full-reference generation.
---

# Write MiniMax-H3 prompts

Turn a user's brief into prompt text that follows MiniMax-H3's official prompt-writing guides. This skill writes prompts only. It does not create JSON payloads, select endpoints or regions, validate media URLs, handle credentials, call an API, run a local model, or download a video.

Load [h3-prompting.md](references/h3-prompting.md) before drafting. Use only the official MiniMax-H3 guides linked there as the domain authority.

## 1. Understand the intended video

Extract what the user supplied:

- generation mode or reference role;
- duration, if known;
- story or communication goal;
- subject identity, setting, visual style, composition, camera behavior, action path, and ending;
- dialogue, lyrics, and visible on-screen text;
- desired ambience, physical sounds, diegetic audio, and audience-only music.

Preserve the user's intent. Add concrete, observable detail and continuity, but do not invent a new plot, extra characters, dialogue, lyrics, brand claims, or unsupported details from media that cannot be inspected. When a required piece of visible copy is missing, use a bracketed placeholder inside English double quotes—for example, "[PRODUCT TITLE]"—and disclose it in `Assumptions:` instead of inventing a product or brand name. If another non-critical detail is missing, make a restrained assumption and disclose it briefly instead of blocking. Ask a question only when the generation mode or the role/order of keyframes cannot be inferred safely.

## 2. Choose the official format

Use the base format for T2VA, I2VA, FL2VA, and L2VA:

- T2VA starts directly with the three core fields.
- I2VA starts with the exact first-frame instruction.
- FL2VA starts with the exact first-and-last-frame instruction and uses the actual final duration.
- L2VA starts with the exact last-frame instruction and names the actual final shot.

In every base-mode prompt, the first field starts in this exact shape:

```text
integrated_multimodal_description: [Shot 1] <style, initial composition, and opening action> ...
```

`[Shot 1]` is the first token of the field value. Put the visual style and initial composition after that tag. Encode duration through cut timing, action density, and the ending; encode aspect ratio through framing and composition. The base prompt body contains no global duration statement or aspect-ratio label. Only frame-alignment instructions use the final duration, and later shot tags use cut times.

Use the full-reference format when several assets define reusable subjects, concrete frames, source-video structure, or audio relationships; or when the request involves video editing, continuation, audio reuse, or audio reference. Write all six sections in their fixed order: `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, and `non_diegetic_music`.

Do not combine the base three-field wrapper with the full-reference six-section wrapper.

## 3. Expand the prompt

Write the body in English, except that dialogue, lyrics, and visible text stay in their original language.

- Build a coherent playback timeline. In base mode, start the field value immediately with `[Shot 1]` and no timestamp; give later shots strictly increasing cut times inside the duration.
- Keep shot and cut counts consistent with the explicit timeline. In a linear `N`-shot sequence there are `N - 1` cuts; call the segments shots and count only the transitions as cuts.
- Give each shot one dominant visible action and one primary camera movement. Secondary motion may complete the same beat but should not introduce a competing camera instruction. Prefer continuous camera movement over unnecessary cuts, and describe it as natural prose with amplitude and speed only when useful.
- Separate source-frame invariants from states the requested action must change. Preserve identity, appearance, fixed environment geometry, and unaffected props while allowing the subject's position, pose, and manipulated prop state to follow the requested action.
- For collisions, breakage, unfolding, spilling, and other physically driven transitions, trace `cause → contact → material-specific response → settling`. Keep speed and momentum consistent unless a visible force changes them; use rigid, brittle, flexible, or fluid behavior appropriate to the material. Carry the same motion facts into `overall_soundscape`: sound descriptors may mirror visible speed and impact, but do not add acceleration, deceleration, or a new cause absent from the timeline.
- Carry a visible causal anchor across transitions when the story depends on transformation, such as `light point → traveling signal → typographic stroke`. For abstract computational imagery, select two or three recurring motifs and reuse them instead of introducing a new UI, chart, icon, or code layer for every idea.
- For I2VA, develop forward from the first image. For FL2VA, describe the observable path between the two frames and land on the last frame. For L2VA, infer a compatible earlier state and converge on the final image.
- Assign stable `(S1)`, `(S2)`, and subsequent IDs only to actual vocal sources. Put only the language tag and spoken words inside `<d>`. Preserve user-provided dialogue and punctuation verbatim. For voiceover, write `<Subject or speaker> (S1) says in an off-screen voiceover: <d>[Language] Exact words.</d>` first, then immediately state that the corresponding on-screen character's lips remain completely closed.
- For dialogue or lyrics directly reused or reperformed from reference audio, preserve the words and language, use `[unclear]` rather than guessing, and normalize decorative punctuation according to the full-reference guide.
- Put visible text in English double quotation marks without translating or rewriting it. If the user did not provide required copy, use the disclosed bracketed placeholder verbatim. The final prompt contains the double quotes and square brackets only; Markdown backticks are never part of visible text.
- Keep ambience, physical sounds, and non-verbal human sounds in `overall_soundscape`. Keep audience-only score in `non_diegetic_music`; diegetic music belongs in the timeline. Describe musical tempo qualitatively unless the user supplied an exact BPM.
- In full-reference mode, define every tracked label once, reuse it consistently, begin `summary` with the applicable task types inside one pair of square brackets (for example, `[reference generation + audio reference]`), and apply only the official retention markers. When the task type includes `video editing`, put the exact sentence `The target video is an edited version of <Video N>.` immediately after the task-type prefix.
- Keep evidence inside the modality that supplies it. Before defining a visible `<Subject N>`, make its visual inventory only from the brief and inspectable image/video evidence, then check every visible noun in the definition against that inventory. Audio-source words such as footsteps, utensil, bell, or engine remain audible-only until visual evidence confirms their source. When a concrete picture must be matched exactly but its lighting, palette, or depth is not described, refer to the picture's existing attributes instead of inventing them.
- When `<Audio N>` explicitly supplies the voice of a defined target speaker, use this definition shape: `<Audio N>: ... for <Subject N> (Sx).` Attach the global ID to the target speaker inside the definition, not to the `<Audio N>` label. Put complete dialogue or lyrics only inside `<d>` in `detailed_description`; describe their language, timing, or role without repeating the words in `subject_definitions`, `summary`, `retention_analysis`, `overall_soundscape`, or `non_diegetic_music`.
- When an image only supplies attributes for `<Subject N>`, cite it as plain `Picture N` inside that subject definition. Do not create a tracked `<Picture N>` label or a retention line for it. Reserve angle-bracketed `<Picture N>` for a concrete frame, composition anchor, edited frame, or separately analyzed visual reference.
- Create `<Picture N>` only for an actual reference-image asset supplied in that role. Do not synthesize a picture label from the first or last frame inside `<Video N>`; for video continuation, anchor the opening directly to the exact ending frame and motion state of `<Video N>` unless a separate image is supplied.
- Use `attribute_transfer` only when referenced traits are applied to a different identifiable target subject. When the target is the same referenced subject, use `fully_preserved` or `partially_preserved` according to its defined role.

Favor visible state, spatial relationships, action, camera behavior, synchronized sound, and a clear final state. Remove decorative adjectives that do not change what the model should render.

## 4. Self-review

Before returning the prompt, check:

- the selected mode and wrapper match the user's inputs;
- every base-mode `integrated_multimodal_description` starts exactly with `integrated_multimodal_description: [Shot 1]` and has no prose between the colon and shot tag;
- the base prompt body does not restate values such as `15-second`, `15.00 seconds`, or `16:9`; duration and ratio are expressed through timing and composition instead;
- any frame-alignment instruction is exact, first, and followed by one blank line;
- final durations use two decimal places and later cut times are valid and increasing;
- any stated shot or cut count matches the explicit timeline, with one fewer cut than shots in a linear sequence;
- the action can plausibly fit within the duration and reaches the requested ending;
- each shot has one dominant action and one primary camera move, with a visible causal anchor maintained across transformations;
- fixed source-frame invariants are preserved without freezing positions, poses, or prop states that the requested action must change;
- physically driven transitions follow a material-credible cause, response, and settling path without unexplained changes in speed or momentum;
- motion and material qualifiers in `overall_soundscape` match the timeline and introduce no new kinematics or causal event;
- every voiceover places the complete `<d>` block before the corresponding closed-lips statement;
- every visible word is either user-provided text or a disclosed bracketed placeholder, never invented brand or product copy;
- abstract computational prompts reuse two or three motifs rather than accumulating unrelated UI elements;
- speaker IDs, reference labels, the square-bracketed full-reference task prefix, and retention markers stay consistent;
- every `video editing` summary uses the fixed edited-version opening immediately after its task prefix;
- speaker-linked audio definitions use `<Audio N>: ... for <Subject N> (Sx).`, and complete verbal content appears only inside `<d>` in `detailed_description`;
- every noun in a visible subject definition appears in the explicit visual inventory rather than only in an audio cue, and exact picture attributes are source-relative when not described;
- an attribute-only source image is cited as plain `Picture N` inside its subject definition and never appears as a tracked `<Picture N>` or retention item;
- every tracked `<Picture N>` corresponds to an actual supplied image asset rather than a frame synthesized from `<Video N>`;
- `attribute_transfer` names a transfer to a different identifiable target, never preservation of the same subject;
- dialogue markup, visible text, and sound categories follow the guide;
- the prompt contains no contradictions, unsupported asset claims, API fields, or execution instructions.

## 5. Return copy-ready prompt text

Return:

1. one short `Mode:` line;
2. one short `Assumptions:` line only when assumptions materially affect the prompt;
3. the final prompt in a single fenced text block.

Do not append a JSON payload, request schema, endpoint, authentication advice, media-upload instructions, or local-runtime mapping. Those concerns are outside this skill's scope.

## Official sources

- [MiniMax-H3 prompt-writing docs](https://huggingface.co/MiniMaxAI/MiniMax-H3/tree/main/docs)
- [Base guide for T2VA, I2VA, FL2VA, and L2VA](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)
- [Full-reference guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)
- [H3-Context-IR](https://platform.minimaxi.com/docs/api-reference/video-generation-v2-h3-context-ir) is an output-calibration reference only; API execution remains outside this skill.
