---
name: remotion-video
description: >
  React video generation expert. Uses Remotion framework to create videos programmatically
  with TypeScript/React code, supporting dynamic data charts, AE-level effects,
  AI voiceover, and automated rendering.
  Keywords: React video, dynamic chart, programmatic video, Remotion,
  data visualization video, auto-generate video, AE effects.
---

# remotion-video - React Video Generation Expert

## Platform Positioning

| Skill | Positioning | Core Tools |
|---|---|---|
| `jianyin-jianji` | Jianying-style editing (template) | FFmpeg + Jianying project |
| **`remotion-video`** | **React code generation (programmatic)** | **Remotion + FFmpeg** |

> Ideal for: dynamic data, complex effects, programmatic generation, data reports, product demos.

---

## Core Capabilities

- Dynamic data charts (bar/line/pie) with time-based animations
- React component-based video structure
- Lambda batch cloud rendering
- AI voiceover + subtitle sync
- Text animations: typewriter, scale, gradient, glitch

---

## Tool Chain

| Tool | Purpose |
|---|---|
| `batch_text_to_audio` / `synthesize_speech` | AI voiceover |
| `batch_text_to_music` | AI BGM |
| `videos_understand` | Video analysis |
| `exec` (FFmpeg) | Audio/video merge, format conversion |
| Remotion CLI | Local/Cloud rendering |

---

## Routing Index

| Task | Rule |
|---|---|
| Create Remotion project | `rules/setup.md` |
| Composition structure | `rules/composition.md` |
| FFmpeg rendering | `rules/rendering.md` |
| Subtitles & timeline | `rules/captions.md` |
| AI voiceover | `rules/voiceover.md` |
| Chart animation | `rules/charts.md` |
| Text animation | `rules/text-animations.md` |
| Batch generation | `rules/batch-render.md` |
| Lambda deployment | `rules/lambda.md` |

---

## Quick Start Flow

```
1. Clarify requirements -> video type (data report / product demo / social content)
2. Create project -> npx create-video@latest or manual setup
3. Write components -> React + Remotion code per rules
4. Render output -> FFmpeg or Remotion CLI
5. Post-produce -> voiceover + BGM + subtitles -> final MP4
```

---

## Acceptance Checklist

- [ ] Video dimensions correct (width/height/Duration)
- [ ] Frame rate correct (30fps / 60fps)
- [ ] Fonts loaded (Google Fonts or local)
- [ ] Voiceover duration matches video
- [ ] Subtitle timeline aligned
- [ ] Final output: MP4 H.264
