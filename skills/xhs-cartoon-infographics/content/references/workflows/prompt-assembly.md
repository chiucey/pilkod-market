# Prompt Assembly Guide

## Prompt Structure

### Base Template

```
[Scene/Context] + [Style Description] + [Color Palette] + [Layout Instructions] + [Typography] + [Decorative Elements] + [Technical Specs]
```

### Style-Enhanced Prompt

```markdown
# Cartoon illustration for Xiaohongshu infographic

## Scene
[Brief description of the main visual concept]

## Style
[Full style description from references/styles/*.md]

## Colors
[Primary colors with hex codes]
[Secondary colors]
[Accent colors]

## Layout
[Layout description from references/layouts/*.md]

## Typography
[Text direction, positioning, style]

## Decorations
[List of decorative elements]

## Technical
- Aspect ratio: 3:4 (XHS optimal)
- Format: PNG with transparent/solid background
- Resolution: High quality for mobile display
```

## Style-Specific Prompts

### Cute Style

```markdown
Cartoon illustration in kawaii cute style for Xiaohongshu post.
Soft pastel colors: pink #FFB6C1, lavender #E6E6FA, mint #98FB98.
Rounded shapes, heart and star decorations, fluffy clouds, bow ribbons.
Warm and sweet atmosphere with gentle lighting.
Chinese text in cute bubble style.
Layout: [balanced/ sparse/ etc]
Background: soft gradient with pastel tones.
Decorations: scattered stars, hearts, small flowers at corners.
```

### Notion Style

```markdown
Minimalist hand-drawn illustration for Xiaohongshu infographic.
Clean white background with thin black line art (#333333).
Simple line icons, hand-drawn arrows, minimal decorations.
Intellectual aesthetic with clean typography.
Layout: [dense/ list/ mindmap/ etc]
Chinese text in clean sans-serif style.
Decorations: subtle dotted lines, simple brackets.
```

### Bold Style

```markdown
High-impact cartoon illustration for Xiaohongshu post.
Bold contrast: black #000000, bright red #FF0000, electric blue #00BFFF.
Thick black outlines (4-6px), geometric shapes, explosive effects.
Dynamic composition with strong visual hierarchy.
Layout: [sparse/ comparison/ list]
Chinese text with thick black outline and bright color fill.
Decorations: explosion effects, bold arrows, emphasis marks.
```

## Layout-Specific Prompts

### Sparse Layout

```
Minimal composition, one focal point.
Large hero image or product shot.
Generous white space (60-70% of canvas).
Short impactful headline text.
Decorative elements positioned at corners only.
Clean, breathable design.
```

### Dense Layout

```
High-density information layout.
Multiple compact content blocks (5-8 items).
Small icons or bullet points for each element.
Organized grid structure.
Clear typography hierarchy (title > subtitle > body).
Efficient use of available space.
```

### Flow Layout

```
Step-by-step process layout.
Connected stages with arrows or lines.
Numbered process blocks.
Clear directional flow (left-to-right or top-to-bottom).
Timeline or progression indicators.
```

## Reference Image Usage

### For Style Consistency

```
# First image (establish style)
Generate WITHOUT reference image

# Subsequent images (maintain consistency)
Use first image as reference:
- Same character design
- Same color rendering
- Same line quality
- Same decoration style
```

### Reference Image Prompt Addition

```
Style reference: [previous_image.png]
Maintain consistent: character style, color palette, line quality, decorative elements.
Adapt to: [current page's specific content and layout]
```

## Chinese Text Handling

### Best Practices

1. **Position**: Place Chinese text in clear zones
2. **Size**: Ensure readability on mobile (min 24pt equivalent)
3. **Contrast**: Use high contrast for text areas
4. **Direction**: Left-to-right for modern design
5. **Emphasis**: Use boxes/bubbles for key phrases

### Text Zone Examples

```
┌─────────────────────────┐
│                         │
│  [主视觉区域]            │
│                         │
├─────────────────────────┤
│  [文字区域]              │
│  主要标题文字            │
│  副标题/说明文字          │
└─────────────────────────┘
```

## Technical Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Aspect Ratio | 3:4 | XHS optimal |
| Resolution | High | Mobile display |
| Format | PNG | Transparency support |
| Color Mode | RGB | Screen display |
| Max File Size | <5MB | Upload limit |

## Prompt Optimization Tips

1. **Be Specific**: Include exact colors, styles
2. **Reference Previous**: Use reference images for series
3. **Balance Info**: Don't overcrowd prompts
4. **Style Keywords**: Include style names as triggers
5. **Chinese Context**: Add Chinese context when needed
6. **Layout Clear**: Specify layout structure
7. **Decoration Budget**: List but don't over-list decorations
