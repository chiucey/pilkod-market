---
name: slack-gif-creator
description: Toolkit for creating animated GIFs optimized for Slack, with validators for size constraints and composable animation primitives. Use when users ask to create, generate, or make Slack GIFs, animated images for Slack, or GIF stickers.
---

# Slack GIF Creator

A toolkit providing utilities and knowledge for creating animated GIFs optimized for Slack.

## Slack Requirements

**Dimensions:**
- Emoji GIFs: 128x128 (recommended)
- Message GIFs: 480x480

**Parameters:**
- FPS: 10-30 (lower is smaller file size)
- Colors: 48-128 (fewer = smaller file size)
- Duration: Keep under 3 seconds for emoji GIFs

## Core Workflow

```python
from core.gif_builder import GIFBuilder
from PIL import Image, ImageDraw

# 1. Create builder
builder = GIFBuilder(width=128, height=128, fps=10)

# 2. Generate frames
for i in range(12):
    frame = Image.new('RGB', (128, 128), (240, 248, 255))
    draw = ImageDraw.Draw(frame)
    # Draw your animation using PIL primitives
    builder.add_frame(frame)

# 3. Save with optimization
builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
```

## Drawing Graphics

### Drawing from Scratch

When drawing graphics from scratch, use PIL ImageDraw primitives:

```python
from PIL import ImageDraw
draw = ImageDraw.Draw(frame)

# Circles/ovals
draw.ellipse([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)

# Stars, triangles, any polygon
points = [(x1, y1), (x2, y2), (x3, y3), ...]
draw.polygon(points, fill=(r, g, b), outline=(r, g, b), width=3)

# Lines
draw.line([(x1, y1), (x2, y2)], fill=(r, g, b), width=5)

# Rectangles
draw.rectangle([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)
```

## Animation Concepts

### Shake/Vibrate
Offset object position with oscillation using `math.sin()` or `math.cos()`.

### Pulse/Heartbeat
Scale object size rhythmically using sine wave.

### Bounce
Object falls and bounces using easing functions.

### Spin/Rotate
Rotate object around center using PIL's rotate function.

### Fade In/Out
Gradually appear or disappear using alpha channel.

### Slide
Move object from off-screen to position using easing.

## Dependencies

```bash
pip install pillow imageio numpy
```

## Optimization Strategies

When asked to make the file size smaller:
1. Fewer frames - Lower FPS
2. Fewer colors - `num_colors=48`
3. Smaller dimensions - 128x128
4. Remove duplicates
5. Emoji mode optimization
