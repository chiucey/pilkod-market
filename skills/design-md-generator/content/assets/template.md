# [Project Name] Design Specification

> Generated using design-md-generator skill based on [Brand] design system

## Overview

[Describe the holistic design vision: mood, density, philosophy, target audience]

## Colors

| Token | Hex | Role |
|-------|-----|------|
| **Primary** | #[hex] | [CTAs, active states, key interactive elements] |
| **Secondary** | #[hex] | [Supporting actions, chips, toggle states] |
| **Tertiary** | #[hex] | [Accent highlights, badges, decorative elements] |
| **Neutral** | #[hex] | [Backgrounds, surfaces, non-chromatic UI] |
| **Text Primary** | #[hex] | [Main content text] |
| **Text Secondary** | #[hex] | [Muted, supporting text] |
| **Surface** | #[hex] | [Card backgrounds, elevated surfaces] |
| **Outline** | #[hex] | [Borders, dividers] |
| **Error** | #[hex] | [Error states, destructive actions] |
| **Success** | #[hex] | [Success states, positive feedback] |

### Generated Named Colors

These semantic tokens are derived from the base palette:
- `on-primary`: Text on primary color (auto-calculated for contrast)
- `surface-variant`: Alternative surface color
- `surface-bright`: Highest contrast surface

## Typography

### Font Families
- **Headline Font**: [Font Name]
- **Body Font**: [Font Name]
- **Label Font**: [Font Name]
- **Mono Font**: [Font Name] (for code blocks)

### Type Scale

| Level | Size | Weight | Line Height | Use Case |
|-------|------|--------|-------------|----------|
| Display | [N]px | [weight] | 1.2 | Hero sections, major headlines |
| Headline | [N]px | [weight] | 1.3 | Section titles |
| Title | [N]px | [weight] | 1.4 | Card headers, prominent text |
| Body | [N]px | [weight] | 1.5 | Paragraph content |
| Label | [N]px | [weight] | 1.4 | Buttons, tags, captions |
| Caption | [N]px | [weight] | 1.4 | Fine print, metadata |

### Font Usage Rules
- [Rule 1, e.g., "Headlines use semibold weight"]
- [Rule 2, e.g., "Body text uses regular weight at 14-16px"]
- [Rule 3, e.g., "Labels use medium weight at 12px with uppercase for section headers"]

## Elevation

### Shadow System

[Describe elevation approach: shadows OR border contrast + surface variation]

| Level | Shadow | Usage |
|-------|--------|-------|
| None | - | Flat elements, cards |
| Subtle | [shadow values] | Hover states, tooltips |
| Medium | [shadow values] | Dropdowns, modals |
| Strong | [shadow values] | Dialogs, overlays |

### Surface Hierarchy

| Surface Level | Color | Purpose |
|---------------|-------|---------|
| Background | [hex] | Page background |
| Surface | [hex] | Default card surfaces |
| Surface Elevated | [hex] | Elevated cards, modals |
| Surface Bright | [hex] | Maximum contrast surfaces |

## Components

### Buttons

| Variant | Background | Text | Border | Radius | Padding |
|---------|------------|------|--------|--------|---------|
| Primary | [hex] | [hex] | none | [N]px | [N]px [N]px |
| Secondary | transparent | [hex] | 1px [hex] | [N]px | [N]px [N]px |
| Ghost | transparent | [hex] | none | [N]px | [N]px [N]px |
| Destructive | [hex] | [hex] | none | [N]px | [N]px [N]px |

**States:**
- **Default**: As specified above
- **Hover**: [Background lightens/darkens by X%, cursor pointer]
- **Active**: [Background shifts to X%, scale 0.98]
- **Disabled**: [Opacity 0.5, cursor not-allowed]
- **Loading**: [Spinner icon, text "Loading...", disabled interaction]

### Inputs

| Type | Background | Border | Radius | Padding | Height |
|------|------------|--------|--------|---------|--------|
| Text | [hex] | 1px [hex] | [N]px | [N]px | [N]px |
| Search | [hex] | 1px [hex] | [N]px | [N]px | [N]px |
| Textarea | [hex] | 1px [hex] | [N]px | [N]px | auto |

**States:**
- **Default**: As specified
- **Focus**: Border 2px [primary hex], outline none
- **Error**: Border [error hex], helper text in red
- **Disabled**: Background [surface-variant], text [muted]

### Cards

| Type | Background | Border | Radius | Shadow |
|------|------------|--------|--------|--------|
| Default | [hex] | 1px [outline] | [N]px | none |
| Elevated | [hex] | none | [N]px | subtle |
| Interactive | [hex] | 1px [outline] | [N]px | none |

**Interactive Card States:**
- **Hover**: Shadow [subtle], border-color [primary]
- **Active**: Transform translateY(1px)

### Navigation

| Element | Style |
|---------|-------|
| Navbar Height | [N]px |
| Navbar Background | [hex] |
| Navbar Border | 1px [outline] |
| Nav Item Padding | [N]px [N]px |
| Nav Item Radius | [N]px |
| Active Indicator | [underline/color block] |

### Chips/Tags

| Variant | Background | Text | Border | Radius |
|---------|------------|------|--------|--------|
| Default | [hex] | [hex] | none | [N]px |
| Outline | transparent | [hex] | 1px [hex] | [N]px |
| Selected | [primary-light] | [primary] | none | [N]px |

## Layout

### Spacing Scale

Base unit: [N]px

| Token | Value | Usage |
|-------|-------|-------|
| space-1 | [N]px | Tight spacing, icon gaps |
| space-2 | [N]px | Compact elements |
| space-3 | [N]px | Default component padding |
| space-4 | [N]px | Card padding |
| space-5 | [N]px | Section gaps |
| space-6 | [N]px | Large gaps |
| space-8 | [N]px | Section separation |
| space-10 | [N]px | Page margins |
| space-12 | [N]px | Maximum spacing |

### Grid System

- **Container Max Width**: [N]px
- **Grid Columns**: [N]
- **Gutter**: [N]px
- **Breakpoints**: [specify each]

| Breakpoint | Width | Columns |
|------------|-------|---------|
| Mobile | < [N]px | [N] |
| Tablet | [N]-[M]px | [N] |
| Desktop | > [M]px | [N] |

### Whitespace Philosophy

[Describe spacing philosophy: generous vs compact, breathing room, visual rhythm]

## Do's and Don'ts

### Do
- ✅ [Design principle 1]
- ✅ [Design principle 2]
- ✅ [Design principle 3]
- ✅ [Design principle 4]

### Don't
- ❌ [Anti-pattern to avoid 1]
- ❌ [Anti-pattern to avoid 2]
- ❌ [Anti-pattern to avoid 3]
- ❌ [Anti-pattern to avoid 4]

### Accessibility
- Maintain WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
- Minimum touch target size: 44x44px
- Focus indicators visible for keyboard navigation
- Alt text for all images

## Responsive Behavior

### Breakpoints

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 640px | Single column, stacked navigation |
| Tablet | 640-1024px | Two columns where appropriate |
| Desktop | > 1024px | Full layout, side navigation |
| Wide | > 1440px | Maximum content width |

### Collapsing Strategy
- Navigation: [Hamburger menu / tabs / etc.]
- Cards: [Stack / grid reduction]
- Typography: [Scale reduction percentage]

### Touch Targets
- Minimum: 44x44px
- Recommended: 48x48px for primary actions

## Agent Prompt Quick Reference

### Color Quick Reference
```
Primary: #[hex]
Secondary: #[hex]
Background: #[hex]
Surface: #[hex]
Text: #[hex]
Accent: #[hex]
```

### Component Quick Prompts
- **Button**: "[style] button with [color] background"
- **Card**: "card with [radius]px radius, [shadow/border] style"
- **Input**: "input field with [padding]px padding, [border style]"
- **Typography**: "[size]px [weight] [font] for [use case]"

---

*This DESIGN.md was generated based on [Brand] design system template.*
*Generated: [Date]*
