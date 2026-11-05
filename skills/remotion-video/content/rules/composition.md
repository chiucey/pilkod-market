---
name: composition
description: Remotion Composition definition, nesting, props passing, hooks.
tags: composition, component, props, sequence, hook, useCurrentFrame
---

# Composition - Video Units

## Basic Structure

```typescript
import { useCurrentFrame, useVideoConfig, interpolate, spring, Sequence } from "remotion";

export const MyVideo: React.FC<{ title: string; data: number[] }> = ({ title, data }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Linear interpolation
  const opacity = interpolate(frame, [0, 30], [0, 1]);

  // Spring animation (physics feel)
  const bounce = spring({ frame, fps, config: { damping: 10, stiffness: 100 } });

  // Slide-in
  const slideX = interpolate(frame, [0, 60], [-1920, 0]);

  return (
    <div style={{ opacity }}>
      <Sequence from={0} durationInFrames={90}>
        <Intro />
      </Sequence>
      <Sequence from={90} durationInFrames={180}>
        <MainContent data={data} />
      </Sequence>
      <Sequence from={270} durationInFrames={30}>
        <Outro />
      </Sequence>
    </div>
  );
};
```

## Core Hooks

| Hook | Returns | Use |
|---|---|---|
| `useCurrentFrame()` | number | Current frame (0,1,2...) |
| `useVideoConfig()` | {fps, durationInFrames, width, height} | Video metadata |
| `interpolate(input, [i,o], [i,o], opts)` | number | Map frame to value |
| `spring(opts)` | number | Physics spring animation |

## interpolate() Examples

```typescript
// Fade in (0-30 frames)
interpolate(frame, [0, 30], [0, 1])

// Scale up (0-60 frames, 0.8 -> 1.2)
interpolate(frame, [0, 60], [0.8, 1.2])

// Slide in from left
interpolate(frame, [0, 90], [-1920, 0])

// Color transition
interpolate(frame, [0, 60], [0, 255], { extrapolateLeft: "clamp" })
```

## Sequence - Timeline Control

```typescript
<Sequence from={0} durationInFrames={90}>
  <Intro />          // 0-90 frames (0-3s @ 30fps)
</Sequence>

<Sequence from={90} durationInFrames={180}>
  <MainContent />    // 90-270 frames (3-9s)
</Sequence>

<Sequence from={270} durationInFrames={30}>
  <Outro />         // 270-300 frames (9-10s)
</Sequence>
```

## Still (Static Image)

```bash
npx remotion still out/MyComposition thumbnail.png --frame=0
```
