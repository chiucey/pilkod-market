# Analysis Framework for Comic Adaptation

This framework guides the deep analysis process for transforming source content into engaging comic narratives.

## Structure

Every `analysis.md` should follow this YAML + Markdown structure:

```yaml
---
title: "Compelling Title"
topic: [Biography | Concept | Historical Event | Tutorial | Story]
time_span: [relevant time period]
source_language: [detected source language]
user_language: [user's preferred language]
aspect_ratio: ["3:4" | "4:3" | "16:9"]
recommended_page_count: [number]
---
```

## Core Analysis Components

### 1. Target Audience Identification

Identify three tiers of readers:

```markdown
## Target Audience

- **Primary**: [Who is this primarily for? What's their background/knowledge level?]
- **Secondary**: [Who else might benefit?]
- **Tertiary**: [Broader audience who might find it interesting]
```

**Questions to ask**:
- What's the reader's prior knowledge on this topic?
- Why would they seek out this content?
- What's their reading context (casual vs. study)?

### 2. Value Proposition

What transformation does the reader experience?

```markdown
## Value Proposition

What readers will gain:
1. [Specific knowledge/insight]
2. [Emotional experience/shift]
3. [Practical application/perspective]
```

**Examples**:
- Biography: Understanding the human side of historical achievements
- Technical: Making complex concepts intuitive through visual metaphor
- Tutorial: Step-by-step confidence building through visual guidance

### 3. Core Themes Analysis

Identify themes with high narrative and visual potential:

```markdown
## Core Themes

| Theme | Narrative Potential | Visual Opportunity |
|-------|--------------------|--------------------|
| [Theme 1] | [Conflict/emotion/arc potential] | [Panel/scene/color/lighting ideas] |
| [Theme 2] | [How it drives story] | [Visual motifs, symbols] |
```

**Theme categories**:
- Intellectual: Discovery, problem-solving, innovation
- Emotional: Triumph, tragedy, conflict, redemption
- Relational: Mentorship, friendship, rivalry, love
- Social: Individual vs. society, cultural change, progress

### 4. Key Figures & Story Arcs

Map characters and their emotional journeys:

```markdown
## Key Figures & Story Arcs

### [Character Name] (Role)
- **Arc**: [Starting state → transformation → ending state]
- **Visual identity**: [Appearance traits, clothing, expressions, props]
- **Key moments**: [2-3 defining scenes for this character]
```

**Character types**:
- Protagonist: Central figure driving the narrative
- Catalyst: Triggers change/action
- Antagonist: Creates conflict/obstacles
- Mentor: Guides protagonist
- Witness: Observes/commentator

### 5. Content Signal Detection

Analyze content to auto-recommend style/layout:

```markdown
## Content Signals

- "[signal 1]" → [style] + [layout]
- "[signal 2]" → [style] + [layout]
```

**Signal mapping**:

| Content Type | Signals | Style | Layout |
|-------------|---------|-------|--------|
| Tutorial | "how-to", "guide", "beginner" | ohmsha | webtoon |
| Technical | "computing", "AI", "programming", "math" | ohmsha | dense |
| Period | "pre-1950", "ancient", "classical", "Victorian" | sepia | cinematic |
| Personal | "memoir", "mentor", "teacher" | warm | standard |
| Conflict | "war", "breakthrough", "revolution", "battle" | dramatic | splash |
| Professional | "business", "wine", "lifestyle" | realistic | cinematic |
| Wuxia | "martial arts", "jianghu", "xianxia" | wuxia | splash |
| Romance | "love", "friendship", "emotional" | shoujo | standard |
| Balanced | "biography", "documentary" | classic | mixed |

### 6. Page Count Estimation

Based on complexity and depth:

| Story Type | Page Range | Criteria |
|------------|-----------|----------|
| Short | 5-8 pages | Single concept, simple narrative, focused scope |
| Medium | 9-15 pages | Multiple concepts, moderate complexity |
| Full | 16-25 pages | Comprehensive biography, multi-chapter narrative |

## Example: Complete Analysis

```yaml
---
title: "Alan Turing: The Father of Computing"
topic: Biography
time_span: 1912-1954
source_language: en
user_language: zh
aspect_ratio: "3:4"
recommended_page_count: 12
---

## Target Audience

- **Primary**: Tech enthusiasts curious about computing history, ages 16-35
- **Secondary**: Students learning about foundational figures in computer science
- **Tertiary**: General readers interested in biographical stories of genius

## Value Proposition

What readers will gain:
1. Understanding of how modern computing was born from one mind's vision
2. Emotional connection to a brilliant but tragic figure who changed the world
3. Appreciation for the human cost of innovation and persecution

## Core Themes

| Theme | Narrative Potential | Visual Opportunity |
|-------|--------------------|--------------------|
| Genius vs. Society | High conflict - misunderstood genius persecuted by the society he saved | Contrast: Turing's chaotic brilliance vs. sterile institutional spaces |
| Code-breaking | Mystery, tension, race against time | Technical diagrams as art, Enigma machine close-ups |
| Personal Tragedy | Deep emotional resonance, injustice | Intimate panels, somber lighting, isolation motifs |

## Key Figures & Story Arcs

### Alan Turing (Protagonist)
- **Arc**: Misunderstood schoolboy → Cambridge prodigy → War hero → Persecuted genius → Tragic end
- **Visual identity**: Disheveled academic, intense eyes, running clothes, contemplative expression
- **Key moments**: School friendship with Morcom, Enigma breakthrough, arrest, Apple with cyanide

### Christopher Morcom (Catalyst)
- **Role**: Early friend whose death shaped Turing's life's work on life, death, and machine intelligence
- **Visual identity**: Youthful, bright, contrast with Turing's intensity
- **Key moments**: School friendship bonding over science, sudden death devastating Turing

### Commander Denniston (Antagonist)
- **Role**: Initially dismissive of Turing, becomes obstacle, later grudging respect
- **Visual identity**: Military stiffness, authority, conflict with Turing's nonconformity

## Content Signals

- "biography" → classic + mixed
- "computing history" → ohmsha + dense
- "personal tragedy" → dramatic + splash
- "war hero" → sepia + cinematic

## Recommended Approaches

1. **Chronological** - follow life timeline from childhood to death (recommended for biography)
   - Advantages: Clear narrative arc, emotional buildup, shows evolution
   - Challenges: May feel episodic if transitions weak

2. **Thematic** - organize by contributions (computing, code-breaking, AI theory)
   - Advantages: Educational clarity, concept-focused
   - Challenges: May lose emotional thread

3. **Character-focused** - relationships (Morcom, Joan Clarke, Hut 8 team) drive narrative
   - Advantages: High emotional impact, humanizes technical work
   - Challenges: May skip technical achievements

**Recommended**: Chronological with thematic threads woven in
```

## Analysis Tips

### Reading the Source

1. **First pass - Main idea**: What's this about in one sentence?
2. **Second pass - Emotional core**: What's the feeling/mood?
3. **Third pass - Key moments**: Which scenes MUST be visualized?
4. **Fourth pass - Signals**: Which style/layout combinations fit?

### Common Pitfalls

- ❌ Too academic - lose narrative drive
- ❌ Too many characters - focus on 2-3 key figures
- ❌ All summary, no scenes - find specific moments to show
- ❌ Missing visual opportunities - every theme should suggest imagery

### Quality Checks

After analysis, ask:
- ✓ Do I know EXACTLY who this is for?
- ✓ Can I articulate the reader's emotional journey?
- ✓ Are themes specific enough to visualize?
- ✓ Does page count match content complexity?
- ✓ Do style/layout recommendations follow from content signals?
