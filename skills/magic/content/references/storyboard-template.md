# Storyboard Template

This template defines the structure for creating comic storyboards.

## Structure

Each storyboard is a Markdown file with YAML front matter followed by cover and page definitions.

## Front Matter

```yaml
---
title: "Comic Title"
narrative_approach: [chronological | thematic | character-focused]
style: [style-name]
layout: [layout-name]
aspect_ratio: ["3:4" | "4:3" | "16:9"]
estimated_pages: [number]
language: [zh | en | ja | etc.]
---
```

## Cover Definition

```markdown
## Cover

**Title**: [Compelling title]

**Visual Concept**: [Overall composition idea]

**Panel Layout**:
- [Single-panel or multi-panel description]
- [Focus on central imagery/characters]

**Elements**:
- [Key visual element 1]
- [Key visual element 2]
- [Text placement if any]

**Color/Mood**: [Palette suggestions, lighting]

**Image Prompt**: [Detailed description for image generation]
```

## Page Definition

Each page follows this structure:

```markdown
## Page N: [Page Title]

**Narrative Purpose**: [What this page accomplishes in story]

**Panel Layout**: [Description of panel arrangement]

**Panel Breakdown**:

### Panel 1
**Content**: [What happens in this panel]
**Visual**: [Composition, camera angle, lighting]
**Characters**: [Who appears, expressions, actions]
**Background**: [Setting details]
**Dialogue/Caption**: [Text if needed]

### Panel 2
[Continue for each panel...]

**Visual Flow**: [How eye moves across page]

**Page Notes**: [Special instructions, continuity, mood]
```

## Example: Complete Storyboard

```yaml
---
title: "Alan Turing: The Father of Computing"
narrative_approach: chronological
style: sepia
layout: cinematic
aspect_ratio: "3:4"
estimated_pages: 12
language: zh
---

## Cover

**Title**: 图灵与计算机：天才的悲剧与荣耀

**Visual Concept**: Young Alan Turing framed against backdrop of modern computers, ghost of Enigma machine in background

**Panel Layout**: Single dramatic full-bleed illustration

**Elements**:
- Central: Turing in profile, deep in thought
- Background: Faint outlines of Enigma machine and modern computers
- Lighting: Spotlight on Turing, shadows around edges
- Atmosphere: Nostalgic, contemplative, timeless

**Color/Mood**: Sepia tones, warm browns, high contrast between light and shadow

**Image Prompt**: Profile portrait of young Alan Turing (1940s), sepia photograph style, intense thoughtful expression, messy dark hair, rumpled tweed jacket, looking toward horizon. Background shows ghostly transparent outlines: Enigma machine on one side, modern computer chip on the other. Cinematic lighting with warm spotlight on Turing's face, edges fade to shadow. Vintage photograph aesthetic with film grain. Aspect ratio 3:4.

## Page 1: 天才的起点

**Narrative Purpose**: Establish Turing's early genius and social isolation

**Panel Layout**: Cinematic 4-panel - establish wide shot → medium → close-up → close-up

**Panel Breakdown**:

### Panel 1
**Content**: Young Turing alone at school, other boys playing in distance
**Visual**: Wide shot, Turing small in foreground reading, distant blurred figures playing
**Characters**: Turing (age 16), alone, book open, completely absorbed
**Background**: School courtyard, isolated bench under tree
**Dialogue/Caption**: CAPTION: 舍洛克郡，1928年。一个男孩格格不入。

### Panel 2
**Content**: Turing meets Christopher Morcom
**Visual**: Medium two-shot, both looking at science experiment
**Characters**: Turing and Morcom, both excited, Morcom pointing at something
**Background**: Chemistry lab, warm lighting
**Dialogue/Caption**:
MORCOM: 你看，这个化学反应...
TURING: 就像在解一道数学题！

### Panel 3
**Content**: Shared passion montage
**Visual**: Close-up of hands working together, two heads bent over problem
**Characters**: Both in profile, expressions of pure joy
**Background**: Warm golden light, focus on connection
**Dialogue/Caption**: CAPTION: 他找到了懂他的人。

### Panel 4
**Content**: Morcom's sudden death foreshadowed
**Visual**: Turing smiling, Morcom's face slightly faded/translucent
**Characters**: Turing unaware, Morcom ghostly overlay
**Background**: Darkening edges, sense of impending loss
**Dialogue/Caption**: TURING: 我们还有一辈子的时间去探索，克里斯。

**Visual Flow**: Left to right, top to bottom, ending on dark note

**Page Notes**: Establish emotional core - Turing's genius + isolation + rare connection

## Page 2: 悲剧与觉醒

**Narrative Purpose**: Morcom's death transforms Turing's life purpose

**Panel Layout**: Splash page with 3 panels integrated

**Panel Breakdown**:

### Panel 1
**Content**: Turing receives news of Morcom's death
**Visual**: Close-up on Turing's face, shock, world crumbling around him
**Characters**: Turing, devastated, holding telegram
**Background**: Shattered glass effect, everything destabilizing
**Dialogue/Caption**: TELEGRAM: ...suddenly taken ill... passed away...

### Panel 2
**Content**: Turing at funeral, rain, alone in crowd
**Visual**: Wide shot, grave site, Turing separated from mourners
**Characters**: Turing in black, soaked, staring at coffin
**Background**: Rain-heavy scene, muted colors, gray sepia
**Dialogue/Caption**: CAPTION: 他失去了一切。但决心找到了方向。

### Panel 3
**Content**: Turing writes furiously about mind, death, machine intelligence
**Visual**: Extreme close-up on paper, Turing's hands writing, pages flying
**Characters**: Just hands, pen, papers covered in equations
**Background**: Candlelight,深夜 study atmosphere
**Dialogue/Caption**: TURING (internal): If the mind continues after death... can a machine think?

**Visual Flow**: Devastation → Grief → Determination

**Page Notes**: This is the turning point - from grief to life's work

[Continue for remaining pages...]
```

## Panel Layout Types

### Standard Layout
- 4-6 panels per page
- Grid-based (2x2, 2x3, or 3x2)
- Balanced distribution
- Good for: Balanced narratives, dialogue-heavy scenes

### Cinematic Layout
- 2-4 panels per page
- Variable panel sizes
- Wide panels for establishing shots
- Good for: Drama, emotional beats, atmosphere

### Dense Layout
- 6-9 small panels per page
- Information-dense
- Quick visual flow
- Good for: Educational content, tutorials, explanations

### Splash Layout
- 1-2 dominant panels
- Full or half-page impact images
- Good for: Climactic moments, dramatic reveals

### Mixed Layout
- Combination throughout page
- Some pages splash, others dense
- Good for: Long-form stories, variety

### Webtoon Layout
- Vertical scrolling format
- Panel height varies, width consistent
- Good for: Digital reading, tutorials

## Panel Composition Guidelines

### Camera Angles

| Angle | Effect | Usage |
|-------|--------|-------|
| Eye level | Neutral, objective | Standard scenes |
| High angle | Vulnerability, weakness | Character defeat |
| Low angle | Power, dominance | Authority, triumph |
| Dutch angle | Unease, tension | Conflict, disturbance |
| Extreme close-up | Intensity, emotion | Critical moments |
| Wide shot | Context, isolation | Establishing shots |

### Visual Flow Patterns

- **Z-pattern**: Western reading flow, natural progression
- **Reverse Z**: Flashback, looking back
- **Vertical flow**: Webtoon, temporal progression
- **Circular flow**: Cyclical themes, loops

### Panel Transitions

- **Moment-to-moment**: Same scene, time passes slightly
- **Action-to-action**: Same subject, continuous action
- **Subject-to-subject**: Same scene, different focus
- **Scene-to-scene**: Different time/location, requires reader inference
- **Aspect-to-aspect**: Different aspects of same idea/place
- **Non-sequitur**: No logical connection (rare, special effect)

## Page Writing Tips

### Narrative Pacing

- **Fast**: Many small panels, quick actions, minimal dialogue
- **Medium**: Mix of panel sizes, balanced dialogue
- **Slow**: Few large panels, atmospheric, time to absorb

### Dialogue Balance

- **Wordy pages**: 3-4 panels, room for text
- **Action pages**: 6+ panels, minimal text
- **Rule of thumb**: If panels feel crowded, reduce dialogue OR reduce panels

### Visual Variety

- **Don't**: All medium shots, same distance, same angle
- **Do**: Mix close-ups, medium shots, wide shots, Dutch angles

### Continuity

- **Character positions**: Maintain spatial relationships
- **Props**: If a character has something in Panel 1, keep it (or show it gone intentionally)
- **Lighting**: Match mood across panels unless intentional change

## Storyboard Quality Checklist

After creating storyboard, verify:

- ✓ Cover establishes title and mood
- ✓ Each page has clear narrative purpose
- ✓ Panel layout fits content density
- ✓ Visual prompts are detailed and specific
- ✓ Character actions are clear (not just "standing there")
- ✓ Background settings are specified
- ✓ Lighting/color suggestions support mood
- ✓ Flow guides reader through story
- ✓ Pacing varies (not all fast or all slow)
- ✓ Emotional arc builds across pages
- ✓ Ending resolves or thoughtfully concludes

## Generating from Storyboard

When generating images:

1. **For each panel**: Use the panel's "Image Prompt" if available
2. **If no separate prompt**: Combine Visual + Characters + Background + Color/Mood into detailed description
3. **Maintain consistency**: Use same session ID across all pages
4. **Character reference**: Pass `characters.png` if supported by image skill
5. **Aspect ratio**: Use specified aspect_ratio for all images
