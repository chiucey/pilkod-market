---
name: voiceover
description: AI voiceover generation, ElevenLabs TTS, volume curves.
tags: voiceover, tts, audio, dubbing, volume
---

# AI Voiceover Rules

## Generate Voice (Platform Tools)

```typescript
// synthesize_speech or batch_text_to_audio
// voice_id: system voice or cloned voice
// speed: 0.5-2.0 (recommended 0.9-1.1)
```

## Use in Remotion

```typescript
import { Audio, Sequence } from "remotion";

<Sequence from={90} durationInFrames={300}>
  <Audio
    src="./voice/narration.mp3"
    startFrom={0}
    volume={(f) => interpolate(f, [0, 10, 290, 300], [0, 1, 1, 0])}
  />
  <Subtitle text="Welcome to the report" startFrame={90} endFrame={180} />
</Sequence>
```

## Volume Curve (Fade In/Out)

```typescript
const volume = interpolate(
  frame,
  [0, 15, durationInFrames - 30, durationInFrames],
  [0, 1, 1, 0]  // Fade in start, fade out end
);
```

## Voiceover + BGM Mix

```typescript
// BGM at 0.3-0.5 volume (voice priority)
<>
  <Audio src="./voice/narration.mp3" />
  <Audio src="./music/bgm.mp3" volume={0.4} startFrom={0} />
</>
```

## Checklist

- [ ] TTS text has no rare characters
- [ ] Voiceover duration >= video duration
- [ ] Voice BGM ratio <= 0.5
- [ ] Fade in/out at start/end
