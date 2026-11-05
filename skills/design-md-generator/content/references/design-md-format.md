# DESIGN.md Reference Guide

Based on Google Stitch's DESIGN.md format specification.

## Overview

The Overview section describes the holistic look and feel:
- **Mood**: Is it playful or professional?
- **Density**: Dense data dashboard or spacious landing page?
- **Philosophy**: Design principles that guide decisions

```markdown
## Overview
A calm, professional interface for a healthcare scheduling platform.
Accessibility-first design with high contrast and generous touch targets.
```

## Colors

Color section format with semantic naming:

```markdown
## Colors
- **Primary** (#2665fd): CTAs, active states, key interactive elements
- **Secondary** (#6074b9): Supporting actions, chips, toggle states
- **Tertiary** (#bd3800): Accent highlights, badges, decorative elements
- **Neutral** (#757681): Backgrounds, surfaces, non-chromatic UI
```

### Color Role Generation

Agents generate named colors from base values:
- `surface` - Background surfaces
- `on-primary` - Text on primary color
- `error` - Error states
- `outline` - Borders and dividers

## Typography

Typography rules with font hierarchy:

```markdown
## Typography
- **Headline Font**: Inter
- **Body Font**: Inter
- **Label Font**: Inter

Headlines use semi-bold weight. Body text uses regular weight at 14–16px.
Labels use medium weight at 12px with uppercase for section headers.
```

### Type Hierarchy Levels
1. **Display**: Hero sections, major headlines
2. **Headline**: Section titles
3. **Title**: Card headers, prominent text
4. **Body**: Paragraph content
5. **Label**: Buttons, tags, captions

## Elevation

How depth is conveyed (shadows or flat):

```markdown
## Elevation
This design uses no shadows. Depth is conveyed through border contrast
and surface color variation (surface, surface-container, surface-bright).
```

### Shadow Properties (if used)
- Spread: Shadow radius
- Blur: Softness level
- Color: Shadow tint
- Offset: Vertical positioning

## Components

Component styling guidance:

| Component | What to specify |
|-----------|----------------|
| **Buttons** | Variants, sizing, padding, radius, states |
| **Chips** | Selection, filter, action variants |
| **Lists** | Item styling, dividers, leading/trailing |
| **Inputs** | Text fields, labels, helper text, errors |
| **Checkboxes** | Checked, unchecked, indeterminate |
| **Radio buttons** | Selected, unselected states |
| **Tooltips** | Positioning, colors, timing |

```markdown
## Components
- **Buttons**: Rounded (8px), primary uses brand blue fill, secondary uses outline
- **Inputs**: 1px border, surface-variant background, 12px padding
- **Cards**: No elevation, 1px outline border, 12px corner radius
```

## Do's and Don'ts

Practical guardrails:

```markdown
## Do's and Don'ts
- Do use the primary color only for the single most important action per screen
- Don't mix rounded and sharp corners in the same view
- Do maintain WCAG AA contrast ratios (4.5:1 for normal text)
- Don't use more than two font weights on a single screen
```

## Section Order

1. Overview
2. Colors
3. Typography
4. Elevation
5. Components
6. Do's and Don'ts

**Note**: Sections can be omitted if not relevant, but preserve order.
