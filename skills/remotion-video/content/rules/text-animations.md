---
name: text-animations
description: Text animations: typewriter, fade, slide, scale, gradient, glitch.
tags: text, animation, typewriter, fade, slide, scale, gradient, glitch
---

# Text Animations

## Common Text Style

```typescript
const textStyle = {
  fontFamily: "Microsoft YaHei, sans-serif",
  fontSize: 72,
  color: "white",
  textAlign: "center",
  textShadow: "0 4px 16px rgba(0,0,0,0.6)",
  letterSpacing: 4,
};
```

## Typewriter Effect

```typescript
const TypewriterText: React.FC<{ text: string; start: number }> = ({ text, start }) => {
  const frame = useCurrentFrame();
  const chars = interpolate(frame, [start, start + text.length * 3], [0, text.length]);
  return <span>{text.slice(0, Math.floor(chars))}</span>;
};
```

## Scale Bounce In

```typescript
const AnimatedTitle: React.FC<{ text: string; start: number }> = ({ text, start }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [start, start + 45], [0, 1], {
    easing: Easing.bezier(0.34, 1.56, 0.64, 1), // bounce
  });
  return (
    <div style={{
      opacity: interpolate(progress, [0, 0.5], [0, 1]),
      transform: `scale(${interpolate(progress, [0, 1], [0.5, 1])})`,
      ...textStyle, fontSize: 96,
    }}>
      {text}
    </div>
  );
};
```

## Gradient Text

```typescript
<div style={{
  fontSize: 96, fontWeight: "bold",
  background: "linear-gradient(135deg, #FFD700, #FF6B6B, #4facfe)",
  WebkitBackgroundClip: "text",
  WebkitTextFillColor: "transparent",
}}>{text}</div>
```

## Glitch Effect

```typescript
const GlitchText: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const glitch = Math.sin(frame * 0.5) > 0.8;
  return (
    <div style={{ position: "relative" }}>
      <div style={{ color: glitch ? "#00ffff" : "transparent",
        textShadow: glitch ? "2px 0 #ff0080" : "none", ...textStyle }}>
        {text}
      </div>
      <div style={{ ...textStyle, position: "absolute", top: 0, left: 0 }}>{text}</div>
    </div>
  );
};
```
