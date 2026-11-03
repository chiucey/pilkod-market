---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 17e967feac32fcc110dfd3ad78fdc7c7
    PropagateID: 17e967feac32fcc110dfd3ad78fdc7c7
    ReservedCode1: 3045022100e2088b2fc2080cc5564981148f31879572b20f9a345eaabd067439e50c0795590220156caf42b2c93d657236725e722886592b55a2ead6460b781ef4f4e51c23d566
    ReservedCode2: 3046022100ce07df0876e406b84a53f3ec0b930f130cd2f3f6f83610d7c9f6b451d392b53a0221008afaa288e633960acc29203dcebe67ec4a2ad8c6d55ab8a7a613a5db1b83a3ff
---

# Content to Infographic Skill

## Overview

This skill automatically transforms user-provided text content into infographic cards (PNG format), using a minimalist, tech-forward, business-appropriate design style.

**Supported Aspect Ratios**: 9:16 (vertical/mobile) and 16:9 (horizontal/desktop). Default is 9:16.

---

## Input Parameters

When using this skill, you can specify the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `aspect_ratio` | string | `9:16` | Canvas ratio: `9:16` (vertical) or `16:9` (horizontal) |
| `content` | string | required | The text content to convert into infographics |
| `card_count` | number | auto | Number of cards to generate (default: auto based on content structure) |

**Examples**:
- "生成信息图，16:9横向布局" → uses 16:9 horizontal layout
- "制作9:16竖版信息卡片" → uses 9:16 vertical layout (default)
- "16:9比例，三张卡片" → 16:9 horizontal with 3 cards

---

## Design Specifications

### Unified Visual Guidelines

- **Canvas Ratio**: `{ASPECT_RATIO}` (default: 9:16 vertical, or 16:9 horizontal based on user input)
- **Background**: Light background (cream white + light gray gradient)
- **Primary Colors**:
  - Background: `#FAFBFC` to `#F0F2F5` gradient
  - Primary text: `#1A1A2E` (deep blue-black)
  - Secondary text: `#6B7280` (medium gray)
  - Accent: `#3B82F6` (tech blue) or `#10B981` (success green)
- **Font**: Sans-serif (e.g., Inter, PingFang SC)
- **White Space**: Ample margins, 20% top, 15% bottom
- **Borders**: Fine-line geometric style, 1-2px lines
- **Effects**: Subtle glow, soft shadows

---

## Card Template Library

### Card 1: Cover (Person + Core Insight)

**Purpose**: Infographic cover, showcase core theme

**Prompt Template**:
```
{ASPECT_RATIO} info card, light background (cream white + light gray gradient), minimalist premium style, large white space at top for title, abstract figure silhouette in center (tech entrepreneur standing at a fork in the path), path extending upward from "Tech → Product → Organization → CEO" layer by layer, fine-line geometric structure style, subtle glow effect, symbolizing cognitive upgrade

Title (large text, top):
{MAIN_TITLE}

Subtitle (center):
{SUBTITLE}

Bottom text:
{BOTTOM_TEXT}
```

**Use Cases**: Article opening, core insight emphasis

---

### Card 2: Story Core (Quote Card)

**Purpose**: Showcase key quote or insight

**Prompt Template**:
```
{ASPECT_RATIO} vertical card, light background with subtle paper texture, centered text layout, minimalist typography style, keywords bolded, subtle line icons as accents (gear → product box → organization chart → crown)

Main copy:
{MAIN_QUOTE}

Supporting copy:
{SUPPORTING_TEXT}

{HASHTAGS}
```

**Use Cases**: Core insight emphasis, cognitive reversal

---

### Card 3: Comparison Analysis Card

**Purpose**: Side-by-side comparison of two perspectives or solutions

**Prompt Template**:
```
{ASPECT_RATIO} card, left-right comparison layout, left side shows "{LEFT_TITLE}" ({LEFT_ICON}), right side shows "{RIGHT_TITLE}" ({RIGHT_ICON}), clear dividing line in the center

Title:
{TOPIC_TITLE}

Content sections:

Left side ({LEFT_TITLE}):
{LEFT_ITEMS}

Right side ({RIGHT_TITLE}):
{RIGHT_ITEMS}

Bottom emphasis:
{BOTTOM_EMPHASIS}
```

**Use Cases**: Tech vs needs, solution comparison, pros/cons analysis

---

### Card 4: Structure Card (Pyramid/Hierarchy)

**Purpose**: Display hierarchical structure or logical relationships

**Prompt Template**:
```
{ASPECT_RATIO} card, "pyramid structure diagram" in the center, {LEVEL_COUNT} layers from bottom to top, each layer with fine-line frame + subtle shadow, tech infographic style

Title:
{STRUCTURE_TITLE}

{LEVEL_CONTENT}

Bottom note:
{BOTTOM_NOTE}
```

**Use Cases**: Principle explanation, hierarchy analysis, priority display

---

### Card 5: Three-Point Summary Card

**Purpose**: Parallel display of three points or cases

**Prompt Template**:
```
{ASPECT_RATIO} card, three-section structure, one icon per section ({ICONS}), infographic style

Title:
{CARD_TITLE}

Three sections:

{POINT_1}

{POINT_2}

{POINT_3}

Bottom summary:
{SUMMARY}
```

**Use Cases**: Case summary, point aggregation, methodology

---

### Card 6: Checklist/Method Card

**Purpose**: Step-by-step or checklist display

**Prompt Template**:
```
{ASPECT_RATIO} card, checklist structure, minimalist UI style, subtle icons ({ICONS})

Title:
{LIST_TITLE}

Content:
{LIST_ITEMS}

Bottom emphasis (bold):
{BOTTOM_EMPHASIS}
```

**Use Cases**: Action guide, operation steps, to-do items

---

## Content Analysis Process

### Step 1: Content Recognition

Analyze input content to identify:
- **Core Theme**: Central idea of the article/content
- **Key Points**: 3-5 core arguments
- **Structure Type**: Comparison / Causation / Parallel / Process
- **Emotional Tone**: Inspirational / Warning / Analytical / Summary

### Step 2: Card Planning

Select appropriate card template based on content:

| Content Type | Recommended Template |
|-------------|---------------------|
| Core insight emphasis | Card 1 (Cover) / Card 2 (Quote) |
| Two-solution comparison | Card 3 (Comparison) |
| Hierarchical logic analysis | Card 4 (Structure) |
| Multi-point summary | Card 5 (Three-point) |
| Action recommendations | Card 6 (Checklist) |

### Step 3: Content Extraction

Extract from original text:
- Main title (one-sentence summary)
- Subtitle/core quote
- Supporting arguments (3-5 points)
- Bottom summary/call to action

### Step 4: Prompt Generation

Based on selected template, fill in content to generate complete prompt

---

## Quality Standards

### Visual Quality
- Ample white space, not crowded
- Clear information hierarchy, distinct layers
- Fine-line geometric style, consistent visual language
- Subtle glow/shadow effects for depth

### Content Quality
- Concise and powerful titles
- Prominent core insights
- Clear logical hierarchy
- Moderate information density

### Technical Requirements
- Output format: PNG
- Resolution: 1080x1920 (9:16) or 1920x1080 (16:9)
- Aspect ratio: User-specified (`9:16` or `16:9`)

---

## Usage Examples

### Input Example

User input:
```
Technology is not the answer, demand is the starting point of entrepreneurship. The cognitive leap from engineer to CEO.

Tech people often fall into a thinking trap: believing technology is the core competitiveness. But reality is, technology is just a means, demand is the end.

Successful entrepreneurs and CEOs all have demand insight ability. They can break out of tech thinking and think from the user's perspective.

The pyramid principle tells us: demand = core value. Product boundaries, tech priorities, and commercial value should all be defined around demand.

Excellent product cases tell us: tool integration is more important than tech innovation, experience priority is more important than tech superiority, scene penetration is more important than feature quantity.

Tech person transformation advice: ask about demand first, then do tech; use MVP to validate; proactively get close to users. Doing the right direction is more important than doing tech well.
```

### Output Process

1. **Identify Content Structure**:
   - Core insight: Tech vs demand
   - Key quote: "Technology is not the answer, demand is the answer"
   - Comparison: Tech means vs demand purpose
   - Structure: Pyramid logic
   - Cases: Three elements of successful products
   - Action: Tech person transformation guide

2. **Plan Cards**:
   - Card 1: Cover - "Technology is Not the Answer"
   - Card 2: Quote - "Not insufficient tech, but the problem changed"
   - Card 3: Comparison - Tech vs Demand
   - Card 4: Pyramid - Demand hierarchy
   - Card 5: Cases - Common traits of successful products
   - Card 6: Action - Tech person transformation guide

3. **Generate Infographics**: Use `image_synthesize` tool to generate each card

---

## Special Card Examples (Pre-built)

### Pre-built Card 1: Cover (Tech vs Demand)

**Prompt**:
```
{ASPECT_RATIO} info card, light background (cream white + light gray gradient), minimalist premium style, large white space at top for title, abstract figure silhouette in center (tech entrepreneur standing at a fork in the path), path extending upward from "Tech → Product → Organization → CEO" layer by layer, fine-line geometric structure style, subtle glow effect, symbolizing cognitive upgrade

Title (large text, top):
Technology Is Not the Answer

Subtitle (center):
Demand is the Starting Point of Entrepreneurship

Bottom text:
The Cognitive Leap from Engineer to CEO
```

### Pre-built Card 2: Quote (Core Insight)

**Prompt**:
```
{ASPECT_RATIO} card, light background with subtle paper texture, centered text layout, minimalist typography style, keywords bolded, subtle line icons as accents (gear → product box → organization chart → crown)

Main copy:
"Not Insufficient Tech
But the Problem Changed"

Supporting copy:
Tech → Management → Product → CEO

Every transformation is essentially—
Seeing where the real demand lies

Bottom emphasis:
The Cognitive Leap from Engineer to CEO
```

### Pre-built Card 3: Tech vs Demand Comparison

**Prompt**:
```
{ASPECT_RATIO} card, left-right comparison layout, left side shows "Tech" (complex circuits, code flow), right side shows "Demand" (user silhouette, scenario icons), clear dividing line in the center

Title:
Tech Is the Means, Demand Is the End

Left section (Tech):
- Stronger Algorithms
- Higher Performance
- Better Architecture

Right section (Demand):
- Who Uses It?
- What Problem Does It Solve?
- Willing to Pay?

Bottom emphasis:
Tech divorced from demand almost certainly fails
```

### Pre-built Card 4: Pyramid Structure

**Prompt**:
```
{ASPECT_RATIO} card, "pyramid structure diagram" in the center, 3 layers from bottom to top, each layer with fine-line frame + subtle shadow, tech infographic style

Title:
Using Pyramid Principle to View Products

Top layer (largest text):
Demand = Core Value

Middle layer (three points):
• Define Product Boundaries
• Determine Tech Priorities
• Create Commercial Value

Bottom note:
Tech is just the implementation path, not the starting point
```

### Pre-built Card 5: Success Cases Summary

**Prompt**:
```
{ASPECT_RATIO} card, three-section structure, one icon per section (document/video/red packet), infographic style

Title:
Common Traits of Successful Products

Three sections:

1. Tool Integration
Not tech innovation
But better matching user work style

2. Experience Priority
Users want "adequate + easy to use"
Not "most technically advanced"

3. Scene Penetration
Capture one real urgent need
Outweighs 100 features

Bottom summary:
Victory comes not from tech leadership
But from deeper demand understanding
```

### Pre-built Card 6: Action Guide

**Prompt**:
```
{ASPECT_RATIO} card, checklist structure, minimalist UI style, subtle icons (magnifier/user/rocket)

Title:
How Can Tech People Shift to Demand-Driven?

Content:
① Ask about demand first, then do tech
② Validate with MVP, not perfect implementation
③ Proactively get close to users, don't develop in isolation

Bottom emphasis (bold):
Doing the right direction matters more than doing tech well
```

---

## Notes

1. **Content Compression**: Original content may be lengthy; distill core points
2. **Title Extraction**: Extract the most powerful statements as titles
3. **Clear Hierarchy**: Ensure moderate information density per card
4. **Unified Style**: Maintain consistent visual style across all cards
5. **Highlight Emphasis**: Use color, font size, and white space to emphasize key points

---

## Tool Usage

Use `image_synthesize` tool to generate infographics:

```json
{
  "display_text": "Generate infographic card",
  "requests": [{
    "aspect_ratio": "{ASPECT_RATIO}",
    "output_file": "output/card_{N}.png",
    "prompt": "{Generated Prompt}"
  }]
}
```

**Aspect Ratio Options**:
- `9:16` - Vertical/mobile format (default)
- `16:9` - Horizontal/desktop format
