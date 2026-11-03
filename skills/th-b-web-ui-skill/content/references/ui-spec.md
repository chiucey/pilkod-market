# UI Spec

Use this reference when the task needs a more explicit interface specification rather than only structural page guidance.

## Color

Prefer a restrained enterprise palette.

| Element | Style |
|---------|-------|
| background | very light neutral |
| panel | white or near-white |
| primary text | dark neutral |
| secondary text | medium neutral |
| muted text | lower-contrast neutral |
| border | light neutral |
| divider | subtle neutral |
| primary action | one accent color |
| success | calm green |
| warning | restrained amber |
| error | restrained red |
| info | muted blue |

**Rules:**
- Keep most surfaces neutral
- Use accent color mainly for interaction focus and primary actions
- Use semantic colors for status, not decoration

## Buttons

**Button hierarchy:**
- primary
- secondary
- tertiary or text
- danger

**Rules:**
- default to one primary action in each area
- keep button text short
- preserve width during loading
- disabled state must be visibly inactive

## Forms

**Rules:**
- group fields by topic
- align labels consistently
- use compact spacing
- show validation near the field
- avoid over-explaining helper text

**Preferred control mapping:**
- text input: names, keywords, identifiers
- select: controlled options
- date range: reporting and filtering ranges
- business selector: structured domain entities

## Tables

**Rules:**
- use clear column labels
- keep action columns compact
- use tags or indicators for status
- preserve table space during loading
- include empty and error states

## Spacing

Use a repeatable compact-to-medium rhythm.

| Level | Spacing |
|-------|---------|
| controls | tight |
| rows | compact |
| sections | medium |
| cards | medium |
| page blocks | medium to large |

## Shapes

- use small to medium radius
- keep containers rectangular
- avoid decorative pill treatments unless functionally required

## Interaction

| Pattern | Use Case |
|---------|----------|
| drawer | quick side tasks |
| modal | confirmation or short workflows |
| tabs | peer content sections |
| pagination | predictable and persistent |
| feedback | short, explicit, useful |

## Prompt Add-On

```
Apply restrained enterprise UI rules: neutral surfaces, one accent color, clear button hierarchy, compact forms, stable data tables, explicit loading and empty states, and predictable admin interactions.
```
