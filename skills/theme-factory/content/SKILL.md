---
name: theme-factory
description: Design and generate UI themes, color schemes, typography systems, and visual style templates. Use when creating UI themes, color palettes, typography systems, dark/light mode designs, CSS themes, or visual style guides for applications and websites.
---

# Theme Factory Skill

Design and generate comprehensive UI themes, color schemes, and visual style templates.

## Theme Components

### Color Systems

**Base Palette:**
- Primary: Main brand color
- Secondary: Supporting accent
- Neutral: Text, backgrounds
- Semantic: Success, warning, error

**Color Scales:**
- Create 50-900 scale for each color
- Ensure consistent contrast ratios
- Test accessibility compliance

### Typography Systems

**Font Stack:**
```css
--font-heading: 'Inter', system-ui, sans-serif;
--font-body: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;
```

**Type Scale:**
- Display: 48-72px
- H1: 32-36px
- H2: 24-28px
- H3: 18-20px
- Body: 14-16px
- Small: 12px

### Spacing & Layout

**Spacing Scale:**
```css
--space-1: 4px;
--space-2: 8px;
--space-4: 16px;
--space-6: 24px;
--space-8: 32px;
--space-12: 48px;
```

### Component Styles

**Buttons:**
- Primary, secondary, ghost variants
- Size scale (sm, md, lg)
- States (hover, active, disabled)

**Forms:**
- Input styles
- Focus states
- Error/success indicators

**Cards:**
- Elevation levels
- Border treatments
- Padding scales

## Theme Variants

### Dark Mode
- Invert color values
- Reduce contrast slightly
- Use muted colors
- Test readability

### Light Mode
- High contrast
- White backgrounds
- Clear hierarchy

### High Contrast
- WCAG AAA compliance
- Maximum contrast ratios
- Clear boundaries

## Implementation

### CSS Variables
```css
:root {
  --color-primary: #3b82f6;
  --color-secondary: #8b5cf6;
  /* ... */
}
```

### Tailwind Config
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
      }
    }
  }
}
```

## Design Process

1. **Analyze Requirements**: Brand, use case, audience
2. **Define Colors**: Base palette and scales
3. **Build Typography**: Font selection and scale
4. **Create Components**: Button, input, card styles
5. **Generate Tokens**: CSS variables or design tokens
6. **Document**: Usage guidelines and examples
7. **Export**: Multiple format options
