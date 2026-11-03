# MiniMax-H3 prompt-writing reference

This operational reference is distilled only from MiniMax-H3's official prompt-writing docs:

- [Docs directory](https://huggingface.co/MiniMaxAI/MiniMax-H3/tree/main/docs)
- [Base guide: T2VA, I2VA, FL2VA, and L2VA](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md)
- [Full-reference mode guide](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md)
- [H3-Context-IR API](https://platform.minimaxi.com/docs/api-reference/video-generation-v2-h3-context-ir), used only to calibrate prompt-output shape and detail level

Consult the linked source when an edge case is not covered below.

## Base prompt format

T2VA has no frame-alignment instruction. I2VA, FL2VA, and L2VA begin with the applicable line below, followed by one blank line.

```text
I2VA:
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

FL2VA:
How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.

L2VA:
How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
```

Replace `N` with the actual final shot and `S.SS` with the effective duration formatted to exactly two decimal places. Then use exactly these three fields:

```text
integrated_multimodal_description: [Shot 1] ...

overall_soundscape: ...

non_diegetic_music: ...
```

The first line is structural: `[Shot 1]` must be the first token after `integrated_multimodal_description: `. Put style, initial composition, and opening action after the shot tag. Express duration through cut times, action density, and the final state; express aspect ratio through framing. Do not restate either value as prompt prose such as `a 15-second film`, `through 15.00 seconds`, or `in 16:9`. This immediate-shot-tag rule applies to the base modes; full-reference `detailed_description` intentionally uses one or two style sentences before `[Shot 1]`.

### H3-Context-IR calibration target

Use official H3-Context-IR output as a behavioral benchmark, not as an API workflow. Its base-mode output follows these tendencies:

- begin the field exactly with `integrated_multimodal_description: [Shot 1]`;
- establish style, shot scale or composition, and camera behavior inside the opening shot rather than in a global synopsis;
- make each later shot begin with a cut time and a concrete composition, camera action, and observable state change;
- omit global duration and ratio labels from the prompt body while using them to plan pacing and framing;
- keep synchronized physical or interface sounds in the audiovisual description when relevant, summarize the overall effects layer in `overall_soundscape`, and isolate audience-only score in `non_diegetic_music`.

### Keyframe paths

- **I2VA:** establish the referenced style, composition, subject identity, clothing, colors, props, and fixed environment geometry, then follow `first-frame anchor → action onset → continuous development → result or reaction`. Treat position, pose, and manipulated prop state as changing states when the requested action changes them; do not describe those states as simultaneously unchanged.
- **FL2VA:** describe observable intermediate changes in pose, object state, camera, composition, and lighting. Prefer a single shot unless the user explicitly asks for cuts, and land on the last image at the end.
- **L2VA:** infer a compatible earlier state, give an explicit transition path, and gradually converge on the supplied final image. For physically driven changes, use `cause → contact → material-specific response → settling`; keep motion consistent with visible forces and use material-credible behavior such as brittle fracture, flexible folding, or fluid flow.

## Timeline and camera

- `[Shot 1]` has no timestamp. Later shots use sequential numbers and strictly increasing cut times inside the video duration, for example `[Shot 2] At 00:03.500, the camera cuts to ...`.
- Keep prose counts aligned with the explicit timeline: a linear sequence of `N` shots has `N - 1` cuts. Do not call all shot segments cuts.
- A cut should add new subject, spatial, state, viewpoint, or time information. Use camera movement for small reframing changes.
- Give each shot one dominant visible action and one primary camera movement. Supporting movement should complete the same beat rather than compete with it.
- Preserve a visible causal anchor across shots when the sequence is a transformation. For abstract computational imagery, choose two or three recurring motifs—such as a light point, signal path, and translucent plane—and reuse them instead of stacking many unrelated code, chart, icon, waveform, and UI motifs.
- Camera vocabulary includes `Zoom In/Out`, `Push In/Pull Out`, `Pan Left/Right`, `Truck Left/Right`, `Tilt Up/Down`, `Pedestal Up/Down`, `Arc Shot`, `Tracking Shot`, `Static Shot`, `Shake Slightly/Strongly`, `POV`, and `Roll Clockwise/Counterclockwise`.
- Add `with small/large amplitude` or `at slow/fast speed` only when meaningful. Write motion naturally inside the shot rather than as detached tags.

## Speakers, dialogue, visible text, and sound

- Assign `(S1)`, `(S2)`, and subsequent IDs in order of actual vocal events and reuse them across shots. Non-vocal characters receive no speaker ID; simultaneous speakers may use `(S1,S2)`.
- Establish a speaker's stable visual/audio identity at first appearance. Keep the speaker ID and delivery outside `<d>`; put only the language tag and exact spoken content inside: `<d>[English] Exact words.</d>`.
- Preserve user-provided dialogue and lyrics verbatim, including punctuation. Never translate or paraphrase them.
- For voiceover, use this order: `<Subject or speaker> (S1) says in an off-screen voiceover: <d>[Language] Exact words.</d>`; immediately after the complete `<d>` block, state that the corresponding on-screen character's lips remain completely closed.
- When one line crosses a cut, use `<scenetrans>` at both connection points and state that audio continues across the cut. Use `<cutoff>` when speech is truncated by the end.
- Put visible signs, labels, subtitles, and UI text in English double quotation marks while preserving their text and punctuation. If required copy is absent, use a bracketed placeholder inside the quotes, such as "[PRODUCT TITLE]", and disclose it in `Assumptions:`. The final prompt includes the double quotes and square brackets but no Markdown backticks. Do not substitute a guessed product, model, brand, slogan, or claim.
- `overall_soundscape` is one paragraph of 1–4 English sentences for ambience, physical actions, and non-verbal human sounds. Keep motion qualifiers consistent with the timeline: describe the audible roll, impact, or settling without adding acceleration, deceleration, or another cause not shown there. Do not repeat dialogue, singing, or diegetic music. Use `N/A` only for explicitly requested complete silence.
- `non_diegetic_music` is 1–3 English sentences for audience-only instrumentation, tempo, rhythm, and dynamics. Use qualitative tempo unless the user supplied an exact BPM. Do not describe mood or narrative function. Use `N/A` when no audience-only score is requested.

## Full-reference prompt format

Write all six sections in English, except original dialogue, lyrics, and visible text, and keep this order:

1. `subject_definitions`
2. `summary`
3. `retention_analysis`
4. `detailed_description`
5. `overall_soundscape`
6. `non_diegetic_music`

### Labels

- `<Subject N>` is reusable visible content such as a person, object, scene, style, action, or effect. A subject may draw from several assets, and one asset may define several subjects.
- `<Picture N>` is a concrete first frame, keyframe, last frame, edited frame, composition anchor, or storyboard reference. If an image only defines a subject, cite it within that subject instead of making a standalone picture entry.
- For an attribute-only source image, write plain `Picture N` inside the `<Subject N>` definition; do not wrap it in angle brackets, define it separately, or give it a `retention_analysis` line. Angle brackets make it a tracked label.
- A tracked `<Picture N>` requires an actual supplied reference-image asset. Do not extract or invent a picture label from a frame contained only in `<Video N>`; describe a continuation's opening as the exact ending frame and motion state of `<Video N>` instead.
- `<Video N>` identifies a whole-video edit, continuation source, or temporal/camera/cut structure. Visible content reused from it still gets `<Subject N>` labels.
- `<Audio N>` identifies copied or referenced audio. Its numbering is independent from video numbering. An ordinary reference video does not automatically create an audio label.

Keep source evidence within its modality. Build each visible subject's noun inventory only from the brief and inspectable picture/video content. A sound in `<Audio N>` does not by itself establish that its apparent source is visible: `spatula sound`, for example, remains an audio event unless the visual source also shows a spatula. For a concrete `<Picture N>` that must match exactly, preserve its existing lighting, palette, texture, and depth source-relatively when those attributes are not supplied in the brief.

When `<Audio N>` explicitly corresponds to a target speaker, reuse that speaker's global ID inside the definition. For a defined visible speaker, use `<Audio N>: ... for <Subject N> (Sx).`; for another independent vocal source, use a stable voice description followed by `(Sx)`. The ID follows target-video vocal order and is not assigned independently or attached to the `<Audio N>` label.

Assign each label one stable meaning across all sections. Define each tracked item on its own line with its source, role, and relevant traits.

### Summary and retention

Begin the first paragraph after `summary:` with an accurate task-type prefix enclosed in one pair of square brackets, for example `[reference generation]` or `[video continuation + keyframe completion]`. Compose it only from `keyframe completion`, `reference generation`, `video editing`, `video continuation`, `audio reuse`, and `audio reference`. Combine applicable types with ` + ` inside the brackets, do not repeat a type, and do not infer a type merely because an asset is present.

For a `video editing` task, put this exact sentence immediately after the task-type prefix: `The target video is an edited version of <Video N>.` Replace `N` with the source-video label.

Use only these fixed retention markers:

- visible labels: `fully_preserved`, `partially_preserved`, `attribute_transfer`, `weak_reference`;
- audio labels: `fully_copy`, `partially_copy`, `reference`, `weak_reference`.

Give every tracked label one retention line and explain the relationship within the role already defined for it.

Use `attribute_transfer` only when the referenced characteristics are applied to a different identifiable target subject. Preserving the identity and attributes of the same referenced subject uses `fully_preserved` or `partially_preserved`.

### Detailed description and referenced audio

Open `detailed_description` with one or two English style sentences before `[Shot 1]`. Then follow the base shot, camera, speaker, dialogue, visible-text, and sound rules while inserting labels where their roles take effect. Generation descriptions are normally 350–500 English words; dialogue density and source-video complexity take priority over a mechanical word target.

When a referenced subject speaks, combine its label and speaker ID, such as `<Subject 2> (S1)`. If verbal content is merely part of a directly reused soundtrack and no independent vocal source produces it, use `<Audio N>` without inventing a speaker ID.

When dialogue, narration, or lyrics are directly reused from reference audio, or explicitly reperformed, preserve the exact words and language. Use `[unclear]` instead of guessing. Normalize punctuation to ordinary `,`, `.`, `?`, and `!`; remove emoji, bullets, repeated tildes, and decorative or repeated punctuation. Put the complete verbal content only inside `<d>` in `detailed_description`; in every other section, describe only its language, timing, source, copy/reference role, or delivery. Do not carry source words into the target when only timbre, rhythm, emotion, or delivery is referenced.

State copied or referenced ambience and effects in `overall_soundscape`, and audience-only score relationships in `non_diegetic_music`. Keep complete dialogue and lyrics only inside `<d>` in `detailed_description`.
