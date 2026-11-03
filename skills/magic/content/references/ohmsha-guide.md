# Ohmsha Style Guide

Educational manga style inspired by Japanese technical comics. Optimized for making complex concepts accessible through visual metaphor and character-driven explanations.

## Core Philosophy

Ohmsha style = Visual learning + Character-driven narrative + Real-world applications

**Key principle**: Show, don't just tell. Every concept should be visualized as an action, gadget, or situation.

## Default Characters: Doraemon Cast

Unless custom characters are explicitly requested (`--characters` option), always use Doraemon characters directly:

### Character Roles

| Doraemon Character | Role | Function |
|-------------------|------|----------|
| 大雄 (Nobita) | Student/Learner | Asks questions, makes mistakes, learns |
| 哆啦A梦 (Doraemon) | Mentor/Teacher | Explains concepts, provides gadgets |
| 胖虎 (Gian) | Antagonist/Challenge | Represents obstacles, misconceptions |
| 静香 (Shizuka) | Support/Clarification | Asks clarifying questions, summarizes |

### Character Usage Patterns

```markdown
**大雄** (Student)
- Initial state: Confused, has misconception
- Action: Struggles with problem
- Learning: Has "aha!" moment when concept clicks
- Comic relief: Relatable struggles

**哆啦A梦** (Mentor)
- Introduces concept: "Today's topic is..."
- Uses gadget: Visual metaphor as physical object
- Explains: Simple language, step-by-step
- Encourages: Guides 大雄 to insight

**胖虎** (Challenge)
- Presents problem: "This is impossible!"
- Has misconception: Common misunderstanding
- Gets proven wrong: Learning moment for readers
- Sometimes: Learns alongside 大雄

**静香** (Clarifier)
- Asks: "Wait, why does that work?"
- Summarizes: "So basically..."
- Validates: Checks understanding
- Example: Provides concrete use case
```

## Visual Metaphor Requirements

### CRITICAL: No Talking Heads

**❌ AVOID**:
- Characters standing around talking
- Static explanation panels
- Dialogue-heavy scenes without action

**✓ DO**:
- Every concept becomes a gadget/prop
- Explanations happen during action
- Visual metaphors drive understanding

### Gadget System

```markdown
Concept → Gadget → Action → Understanding

Example:
Concept: Binary data
Gadget: "Any-Door" that transports to 0-world or 1-world
Action: 大雄 keeps stepping through door, lands in different worlds
Understanding: Binary is just many yes/no choices
```

### Common Metaphor Patterns

| Concept Type | Visual Metaphor | Example |
|-------------|----------------|---------|
| Transformation | Machine that processes input→output | Compiler as "translation machine" |
| Selection | Door/river branch | If/else as "magic door" with two rooms |
| Storage | Box/cabinet/container | Variables as "labeled boxes" |
| Algorithm | Recipe/map/instruction | Algorithm as "treasure map" |
| Network | Web/connections | Internet as "town of messengers" |
| Encryption | Lock/key/scramble | Encryption as "word scrambler gadget" |

## Panel Structure for Ohmsha Style

### Page-Level Pattern

```markdown
**3-act structure per page**:

Act 1: Problem/Question
- 1-2 panels establishing what we're learning
- 大雄 struggles with misconception
- Reader relates: "I've wondered this too"

Act 2: Visual Explanation
- 3-4 panels: Doraemon brings gadget
- Action-based explanation
- Step-by-step visual breakdown

Act 3: Realization/Application
- 1-2 panels: 大雄 understands
- Real-world example/application
- Setup for next topic
```

### Panel Types

1. **Question Panel** (1-2 panels)
   - 大雄: "I don't get X!"
   - Establish confusion/misconception
   - Hook reader's curiosity

2. **Gadget Introduction** (1 panel)
   - Doraemon: "Use this gadget!"
   - Visual of the gadget
   - Clear, iconic design

3. **Demonstration** (3-4 panels)
   - Action sequence showing concept
   - Each panel = one step
   - Visual change shows transformation

4. **Understanding** (1-2 panels)
   - 大雄: "Oh, I get it now!"
   - Lightning bolt effect or similar
   - Happy expression, relief

5. **Application** (1 panel)
   - Real-world example
   - How this is used in practice
   - Bridge to next topic

## Page Title Guidelines

**❌ AVOID**:
- "Page 1: Introduction to Variables"
- "Chapter 2: What is an Algorithm?"
- Academic language

**✓ DO**:
- Narrative titles that tell mini-story
- Examples:
  - "Why does this code crash? 大雄's mystery"
  - "The magic door that chooses paths"
  - "大雄 learns to sort his toys"

## Layout Guidelines

### Webtoon Format (Preferred)

- Vertical scrolling
- Variable panel height
- Room for explanatory text
- Easy reading on mobile

### Dense Format (Alternative)

- 6-9 small panels per page
- Quick information flow
- Good for complex multi-step concepts

### Mixed Format

- Some pages webtoon (explanations)
- Some pages splash (dramatic reveals)
- Variety maintains interest

## Dialogue Guidelines

### Language Level

- Target: Middle school comprehension
- Avoid jargon OR explain jargon with metaphor
- Short sentences
- Active voice

### Character Voices

```markdown
**大雄**: Casual, confused, relatable
- "I don't get it..."
- "Wait, what?"
- "But that doesn't make sense!"

**哆啦A梦**: Patient, clear, encouraging
- "Let me explain..."
- "Think of it this way..."
- "Exactly! You got it!"

**胖虎**: Boisterous, skeptical, then surprised
- "This is stupid!"
- "No way that works!"
- "Huh? It actually does?"

**静香**: Thoughtful, clarifying
- "But why..."
- "So that means..."
- "Can you give me an example?"
```

### Exposition Mechanics

```markdown
**Instead of**:
DORAEMON: "An algorithm is a step-by-step procedure for solving a problem." (talking head)

**Use**:
Panel 1: 大雄 tries to find treasure in messy room, fails
Panel 2: Doraemon hands him "Treasure Map Gadget"
Panel 3: Map shows step-by-step path
Panel 4: 大雄 follows steps, finds treasure
DORAEMON: "An algorithm is like this treasure map - steps that lead to solution!"
```

## Content-Specific Guidelines

### Tutorial / How-To

- Start with real-world problem 大雄 faces
- Gadget solves it
- Show each step visually
- End with success

### Technical Concepts

- Find everyday analogy
- Make it physical with gadget
- Break into sub-steps
- Check understanding frequently

### Historical / Biographical

- Use time-travel gadget
- Characters observe historical moment
- Ask "why" questions
- Historical figures explain their work

## Visual Style

### Color Palette

- Bright, approachable colors
- Clear contrast between elements
- Mood: Optimistic, curious

### Line Work

- Clean, readable
- Clear separation between elements
- Labels/glyphs for technical parts

### Effects

- Speed lines for action
- Light bulb for realization
- Question marks for confusion
- Gear icons for "processing"

## Common Mistakes to Avoid

### ❌ Don't

1. **Lecture mode**: Characters stand still explaining
2. **Wall of text**: Long paragraphs in panels
3. **No action**: All talk, no demonstration
4. **Abstract only**: Concepts never made concrete
5. **Too easy**: Skip steps, assume understanding

### ✓ Do

1. **Action-based**: Learning happens during doing
2. **Balanced text**: 1-2 short lines per panel max
3. **Visual-first**: Image explains, text reinforces
4. **Concrete metaphors**: Every concept = visual object/action
5. **Check understanding**: Characters verify they understand

## Example: Complete Page

```markdown
## Page: The Magic Key-Lock Gadget

**Panel 1** (Establish problem)
大雄 sits at computer, frustrated
BIG TEXT: "I keep forgetting my passwords!"

**Panel 2** (Doraemon arrives)
Doraemon pulls gadget from pocket
GADGET: Key-Lock Transformer (looks like futuristic padlock)
DORAEMON: "This gadget shows how passwords really work!"

**Panel 3** (Demonstration - Step 1)
Doraemon types "hello" into gadget
Gadget transforms "hello" into scrambled letters: "x7Km#"
VISUAL: Transformation animation effect

**Panel 4** (Demonstration - Step 2)
Gadget shows "x7Km#" on one side, lock opens
LABEL: "Hash function always creates same output"

**Panel 5** (Understanding)
大雄 has lightbulb moment
BIG IDEA: "So the site never stores my actual password!"

**Panel 6** (Application)
静香 enters with phone
SHIZUKA: "That's why they can't email me my password if I forget it!"
大雄: "Exactly! They don't HAVE it!"

CAPTION at bottom: Cryptographic hash - one-way transformation
```

## Quality Checklist

For each Ohmsha-style page, verify:

- ✓ Characters act, don't just talk
- ✓ Concept becomes visual metaphor/gadget
- ✓ Explanation happens during action
- ✓ 大雄 starts confused, ends understanding
- ✓ Real-world application included
- ✓ Title is narrative, not academic
- ✓ Panels flow logically (problem → solution → understanding)
- ✓ Text minimal, image dominant
- ✓ At least one "aha!" moment
- ✓ Reader learns by watching, not being told
