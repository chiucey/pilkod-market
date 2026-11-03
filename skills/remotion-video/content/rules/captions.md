---
name: captions
description: Subtitles and timeline sync, TTS alignment, typewriter effect.
tags: caption, subtitle, timeline, sync, typewriter
---

# Subtitle Rules

## Subtitle Component

```typescript
import { useCurrentFrame, interpolate } from "remotion";

export const Subtitle: React.FC<{
  text: string;
  startFrame: number;
  endFrame: number;
}> = ({ text, startFrame, endFrame }) => {
  const frame = useCurrentFrame();
  const visible = frame >= startFrame && frame <= endFrame;
  if (!visible) return null;

  // Typewriter effect
  const progress = interpolate(
    frame, [startFrame, startFrame + 30], [0, text.length]
  );
  const displayText = text.slice(0, Math.floor(progress));

  return (
    <div style={{
      position: "absolute",
      bottom: 120,
      left: "50%",
      transform: "translateX(-50%)",
      fontSize: 48,
      fontFamily: "Microsoft YaHei",
      color: "white",
      textShadow: "0 2px 8px rgba(0,0,0,0.8)",
      opacity: interpolate(frame, [startFrame, startFrame + 10], [0, 1]),
    }}>
      {displayText}
    </div>
  );
};
```

## TTS Timeline Sync

```typescript
// Step 1: Whisper analysis
// audios_understand(audio=voice.mp3, prompt="return JSON: {segments:[{start,end,text}]}")

// Step 2: Convert to frames
const fps = 30;
const subtitleSegments = whisperResult.segments.map(s => ({
  startFrame: Math.floor(s.start * fps),
  endFrame:   Math.floor(s.end * fps),
  text:       s.text,
}));

// Step 3: Render subtitles in Remotion
subtitleSegments.map(seg => (
  <Subtitle key={seg.startFrame} text={seg.text}
    startFrame={seg.startFrame} endFrame={seg.endFrame} />
));
```

## Subtitle Styles

| Effect | Implementation | Scene |
|---|---|---|
| Typewriter | Slice text by frame | AI voice sync |
| Fade | opacity interpolate | Cinematic |
| Slide | translateY interpolate | Variety show |
| Scale bounce | scale spring | Action title |
| Stroke+shadow | CSS text-shadow | High contrast |
