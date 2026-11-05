---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8f0bb6dfa77246fa186c2bc15b122329
    PropagateID: 8f0bb6dfa77246fa186c2bc15b122329
    ReservedCode1: 3045022100c778cac3bfb67371878d605a94629b3711431e0d095a418907b52f43e061aa1d022029122ff9e3cfed069497f4f67038521641170e802df6eeb0cf7bc4ee36237611
    ReservedCode2: 3046022100da21e493a601fa0c720c225b5aee9e8fef224060c0f0f25d3ab9bb08f829048d022100c420d766d02cbca3eabac6367fa825fdbe4e585a2e6ff8960c9f1d22cb0b358e
---

# TH B Mobile UI Skill

## Overview
Generate mobile interfaces that feel structured, practical, and product-ready rather than generic or overly decorative. This skill serves as a mobile UI rules layer for creating mobile UI mockups, wireframes, Figma prompts, or frontend code.

---

## Workflow
Follow this sequence:
1. Identify the mobile page type
2. Infer the dominant content pattern
3. Apply mobile layout, spacing, and interaction rules
4. Generate the prototype in the requested format
5. Briefly self-check that the result still feels like a usable mobile product page

If requirements are incomplete, infer the most likely mobile pattern:
- **Mobile list page**: top nav, filters or tabs, list content, bottom actions if needed
- **Detail page**: summary header, cards or grouped sections, action area
- **Form page**: mobile fields, grouped inputs, sticky bottom actions
- **Result or state page**: icon or illustration, status message, follow-up actions
- **Dashboard page**: compact cards, segmented tabs, action shortcuts, data modules

---

## Naming Semantics

### Component Categories
| Category | Description |
|----------|-------------|
| `Base*` | Foundational mobile UI patterns: nav bars, form controls, cards, lists, tabs, drawers, popups |
| `Business*` | Domain-aware controls: entity selectors, date ranges, category selectors, structured filters |
| `Standard*` | Reusable mobile sections: search areas, action bars, card lists, state blocks, fixed bottom actions |

### Mental Model
- Use `Base*` for core page containers and primitive interactions
- Use `Business*` for domain-aware inputs and workflows
- Use `Standard*` for repeatable mobile page sections

### Common Mobile-Feeling Examples
- Top navigation bar
- Segmented tabs
- Card list
- Grouped form cells
- Bottom fixed primary action
- Popup or bottom sheet
- Status tag or badge
- Icon-based empty state
- Business-aware selector

---

## Layout Rules

Prefer vertical flow, clear rhythm, and stable content blocks.

### Key Principles
- Mobile pages should read top to bottom with minimal ambiguity
- Use cards, grouped cells, list items, and section titles to organize content
- Keep the viewport focused on the current task
- Avoid overcrowding a single screen with too many parallel controls
- Use fixed bottom actions for form-heavy or completion-driven workflows

### Common Mobile Page Structures

**List page:**
1. Top nav
2. Search, tabs, or filter strip
3. List or card content
4. Load-more or pagination pattern if required

**Detail page:**
1. Top nav
2. Summary card
3. Grouped information blocks
4. Related content
5. Action area

**Form page:**
1. Top nav
2. Grouped field sections
3. Helper or validation text where needed
4. Bottom fixed action area

---

## Visual Rules

Use calm, product-oriented mobile styling.

### Do:
- Favor light backgrounds and white or near-white content surfaces
- Use one main accent color for key actions and active states
- Prefer small to medium radius
- Keep shadows subtle and use borders or spacing to define structure
- Maintain readable contrast without looking heavy
- Keep icon use purposeful

### Avoid:
- Decorative gradients as main surfaces
- Oversized promotional banners
- Visually noisy cards
- Excessive color variety
- Flashy mobile landing-page aesthetics

---

## Color Rules

Use a restrained mobile palette.

### Color Assignments
| Usage | Color |
|-------|-------|
| Page background | Light neutral |
| Card background | White or near-white |
| Primary text | Dark neutral |
| Secondary text | Medium neutral |
| Helper text | Muted neutral |
| Border and divider | Subtle neutral |
| Primary action | One clear accent color |
| Success | Calm green |
| Warning | Restrained amber |
| Error | Restrained red |

### Color Usage Rules
- Keep large surfaces neutral
- Use accent color mainly for primary buttons, active tabs, links, selected states, and focus points
- Use semantic colors for state, not decoration
- Keep badges and tags concise and readable

---

## Typography Rules

Use compact and readable mobile typography.

| Element | Guideline |
|---------|-----------|
| Page title | Concise and prominent |
| Section title | Clearly secondary to the page title |
| Body text | Readable and compact |
| Helper text | Smaller and lower contrast |
| Action text | Short and strong |

### Avoid:
- Oversized headlines
- Too many font weights
- Loose spacing between text lines in dense screens

---

## Spacing And Shape Rules

### Spacing
| Element | Spacing |
|---------|---------|
| Cell and control spacing | Tight |
| Card padding | Medium |
| Section spacing | Medium |
| Page edge padding | Medium |
| Bottom action area padding | Medium |

### Shape Rules
- Buttons and inputs: small to medium radius
- Cards: stable and lightly rounded
- Avoid overly pill-like shapes unless the control requires it

---

## Button Rules

### Button Hierarchy
1. **Primary button**: Main task completion action
2. **Secondary button**: Supporting action
3. **Text button**: Lightweight action
4. **Danger button**: Destructive action only when clearly necessary

### Button Usage
- Default to one primary button in the main action area
- Use fixed bottom primary actions for important form or completion flows
- Keep button labels short
- Do not overload the screen with too many high-emphasis buttons

### Button States
- Default
- Hover or pressed where applicable
- Active
- Disabled
- Loading

---

## Form Rules

Forms should feel natural on mobile.

### Guidelines
- Group fields into clear sections
- Keep labels and values easy to scan
- Prefer selectors and pickers over free text when the domain is structured
- Use date ranges, pickers, and selectors for mobile-friendly input
- Keep required markers visible but light
- Place validation close to the field

### Preferences
- Single-column form flow
- Grouped card or cell sections
- Sticky bottom action area when the page goal is submission

---

## List And Card Rules

Lists and cards are primary mobile patterns.

### Guidelines
- Keep each item focused on one information goal
- Use title, supporting text, status, and actions in a stable hierarchy
- Do not overload a card with too many equal-priority elements
- Use tags, badges, or short labels for state
- Prefer infinite scroll or load-more patterns only when appropriate

---

## Interaction Rules

Mobile interactions should feel explicit and efficient.

### Guidelines
- Use bottom sheets or popups for short selection tasks
- Use full pages for complex forms and deeper workflows
- Use segmented tabs for peer content categories
- Keep gesture expectations conservative unless explicitly requested
- Preserve context after save, submit, cancel, and back actions

### Feedback
- **Success feedback**: Brief
- **Error feedback**: Explain the problem clearly
- **Loading feedback**: Appear close to the task context

---

## State Rules

Every meaningful mobile page should account for state:
- Default
- Loading
- Empty
- Error
- Disabled where relevant
- Success or completion state where relevant

Empty states should be useful and not overly decorative.

---

## Output Rules

### For Prototype or Design Brief
- Describe the screen structure, primary action, states, and interaction flow
- Mention the mobile pattern used in each section

### For Frontend Code
- Keep the layout mobile-first
- Preserve state handling and bottom action behavior
- Keep card, list, and form hierarchy explicit

### For Figma Prompts
- Mention mobile viewport assumptions
- Mention compact spacing, neutral surfaces, and clear action hierarchy
- Mention cards, grouped cells, fixed bottom actions, or tab patterns when relevant

---

## Safety Boundary

Do not imply technical dependency on unpublished implementation details. Focus on reproducing visible mobile design language, interaction conventions, and structural rules through generic components and clear interface guidance.

---

## Reusable Prompt Pattern

```
Generate a mobile enterprise-style prototype with compact spacing, neutral surfaces, clear action hierarchy, grouped content sections, explicit loading and empty states, and practical app-like interactions.
```

---

## References

- [mobile-page-patterns.md](references/mobile-page-patterns.md) - Concrete mobile page archetypes and prompt snippets
- [mobile-ui-spec.md](references/mobile-ui-spec.md) - Explicit color, button, form, card, and interaction rules
