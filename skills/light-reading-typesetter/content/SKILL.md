---
name: light-reading-typesetter
description: Light reading style book typesetting skill. Use when users request book typesetting, adding illustrations or placeholders, or designing light reading style (minimalist aesthetic). Trigger keywords: book typesetting, light reading, minimalist style, image layout, add illustration, placeholder, image typesetting, Chinese style book design.
---

# Light Reading Book Typesetting Skill

## Skill Overview

This skill focuses on converting existing text content into a book layout format suitable for "light reading" and "minimalist aesthetic" (wabi-sabi style). Core features include:

- Generous white space to reduce reading burden
- Beautiful illustrations to enhance visual experience
- Clean typography to highlight content focus
- Flexible image placeholder mechanism

## Typography Style Guidelines

### Light Reading Style Characteristics

1. **Margins**: Top 2.5cm, Bottom 2cm, Left/Right 2.5cm
2. **Body Font**: Noto Serif, 14pt, line-height 1.8
3. **Heading Font**: Noto Sans, clear hierarchy
4. **Paragraph Spacing**: 0.5em before, 0.3em after
5. **First Line Indent**: 2 character widths

### Minimalist Aesthetic Characteristics

1. **Colors**: Soft, elegant, mainly ivory white or light gray
2. **Decorative Elements**: Simple lines, light dividers
3. **Illustration Style**: Ink wash, flat illustration, minimalist line art
4. **Overall Atmosphere**: Serene, elegant, easy to read

## Execution Workflow

### Step 1: Analyze Original Content

1. Read and understand the original text material:
   - Article structure (chapters, paragraphs)
   - Content theme and emotional tone
   - Nodes suitable for adding illustrations

2. Identify scenes that need visual elements:
   - Chapter opening
   - Important paragraph breaks
   - Key concept/quote locations
   - Emotional climax points

### Step 2: Plan Illustration Layout

Based on content analysis, plan image positions:

| Position | Purpose | Style Suggestion |
|----------|---------|------------------|
| Chapter Opening | Atmosphere | Full or half page illustration |
| Between Paragraphs | Content transition | Small decorative image |
| Quote Block | Visual emphasis | Border decoration |
| Ending | Lingering resonance | Small atmospheric image |

### Step 3: Generate or Add Images

#### Option A: Use AI to Generate Illustrations

Call image generation tools to create illustrations matching the minimalist style:

```
Prompt Template:
[Theme description], ink wash style, minimalist lines, soft colors,
abundant white space, book illustration style
```

#### Option B: Add Image Placeholders

When no suitable images are available, use elegant placeholders:

```
Placeholder Style:
┌─────────────────────────┐
│                         │
│   [Placeholder text]     │
│                         │
│   e.g.: "Decorative     │
│          illustration"  │
│                         │
└─────────────────────────┘
```

### Step 4: Apply Typography Format

Output processed content in the following formats:

1. **HTML Format**: Suitable for web/ereaders
2. **Markdown Format**: Suitable for note-taking software
3. **PDF Format**: Suitable for print publishing

## Output Format Examples

### Chapter Structure

```markdown
# Chapter 1 Title

![Chapter Atmosphere](chapter-image.jpg)

Body content with first line indent...

> Quote content with special styling

Continue body...

![Paragraph Decoration](decoration.png)

## Chapter Summary

- Key point 1
- Key point 2
```

### Placeholder Markup

```html
<!-- Image Placeholder -->
<figure class="image-placeholder">
  <div class="placeholder-content">
    <span class="placeholder-icon">✦</span>
    <span class="placeholder-text">[Decorative illustration]</span>
  </div>
</figure>
```

## Quality Checklist

After typesetting, confirm the following:

- [ ] Font hierarchy clear and distinguishable
- [ ] Paragraph spacing comfortable
- [ ] Illustration style unified
- [ ] Placeholder markers clear but unobtrusive
- [ ] Overall reading experience relaxed and pleasant
- [ ] Color scheme matches minimalist aesthetic

## Applicable Scenarios

| Scenario | Recommended Configuration |
|----------|--------------------------|
| Essay Collection | Generous white space, ink wash illustrations |
| Short Stories | Chapter images + quote decorations |
| Travel Essays | Scene atmosphere images |
| Life Reflections | Simple line decorations |

## Notes

1. **Copyright Compliance**: Ensure illustrations have proper copyright
2. **Style Consistency**: Maintain consistent illustration style throughout
3. **Moderate White Space**: Don't overuse illustrations, keep content dominant
4. **Responsive Design**: Consider different screen sizes for digital versions

---

*This skill focuses on transforming text content into an elegant book form suitable for light reading*
