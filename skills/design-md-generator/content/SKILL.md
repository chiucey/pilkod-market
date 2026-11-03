---
name: design-md-generator
description: Generate design specs based on DESIGN.md templates from VoltAgent's awesome-design-md collection. Use when users ask to create design specifications in the style of specific brands like Linear, Figma, Vercel, Claude, or any of the 50+ supported websites. Triggers with /design --brand or /design --style commands.
---

# Design MD Generator

Generate high-quality DESIGN.md specifications inspired by real-world design systems.

## Workflow

### Step 1: Parse User Intent

When user triggers `/design --[brand/style] [description]`:

1. **Extract the brand/style** from the command
2. **Identify the design goal** from remaining text
3. **Match to a template** from the collection

### Step 2: Available Brand Templates

| Category | Brands |
|----------|--------|
| **AI & ML** | claude, cohere, elevenlabs, minimax, mistral, ollama, replicate, runway, togetherai, voltagent, xai |
| **Dev Tools** | cursor, expo, linear, lovable, mintlify, posthog, raycast, resend, sentry, supabase, superhuman, vercel, warp, zapier |
| **Infrastructure** | clickhouse, composio, hashicorp, mongodb, sanity, stripe |
| **Design & Productivity** | airtable, calcom, clay, figma, framer, intercom, miro, notion, pinterest, webflow |
| **Fintech** | coinbase, kraken, revolut, wise |
| **Enterprise** | airbnb, apple, ibm, nvidia, spacex, spotify, uber |
| **Automotive** | bmw, ferrari, lamborghini, renault, tesla |

### Step 3: Generate DESIGN.md

Combine the selected brand template with user's specific requirements:

```markdown
## Overview
[Brand]-inspired design spec for [user's goal].

## Colors
[Brand color palette with hex values]

## Typography
[Brand typography rules]

## Elevation
[Brand shadow/elevation system]

## Components
[Brand component styles]

## Do's and Don'ts
[Brand design principles]
```

## Design System Sections

Every DESIGN.md follows the Stitch format:

| Section | Purpose |
|---------|---------|
| **Overview** | Mood, density, philosophy |
| **Colors** | Semantic names + hex + roles |
| **Typography** | Font hierarchy table |
| **Elevation** | Shadows, surface hierarchy |
| **Components** | Buttons, cards, inputs with states |
| **Do's and Don'ts** | Guardrails and anti-patterns |

## Brand Template Examples

### Linear Style
- Ultra-minimal, precise
- Purple accent (#5E6AD2)
- SF Pro typography
- No shadows, border contrast

### Figma Style
- Vibrant multi-color
- Playful yet professional
- Distinctive brand identity
- Bold design choices

### Vercel Style
- Black/white precision
- Geist font
- Minimalist approach
- Clean gradients

## Output Format

Generate a complete DESIGN.md that:

1. **Starts with Overview** describing the design personality
2. **Includes exact color values** (hex codes)
3. **Specifies typography** with font weights and sizes
4. **Documents component states** (hover, active, disabled)
5. **Provides actionable do's and don'ts**

## Quick Reference

For instant templates, use these common brand profiles:

- `/design --linear` → Ultra-minimal dev tool aesthetic
- `/design --figma` → Creative design tool energy
- `/design --vercel` → Clean deployment platform feel
- `/design --claude` → Warm editorial AI assistant style
- `/design --supabase` → Dark emerald code-first look
- `/design --airbnb` → Warm coral photography-driven UI

## Edge Cases

- **Unknown brand**: Fall back to clean minimal style with blue accent
- **No brand specified**: Ask user which brand/style they prefer
- **Custom requirements**: Merge user specs with selected brand template
