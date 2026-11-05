---
name: ascii-chart
description: Generate ASCII art charts with customizable styles and colors. Use when users ask to create bar charts, line charts, pie charts, or any data visualizations using ASCII/Unicode characters. Triggers: "ASCII chart", "ASCII graph", "bar chart in terminal", "text chart", "terminal chart", "命令行图表", "ASCII 图表", "生成图表"
---

# ASCII Art Chart Generator

Generate customizable ASCII/Unicode art charts for terminal display and documentation.

## Supported Chart Types

1. **Bar Chart** - Vertical/horizontal bars with optional labels
2. **Line Chart** - Multi-series line plots with markers
3. **Pie Chart** - Circular pie with percentage labels

## Color Support

- **ANSI 16-color**: Standard terminal colors (black, red, green, yellow, blue, magenta, cyan, white + bright variants)
- **256-color**: Extended palette (0-255)
- **Truecolor**: 24-bit RGB colors (requires terminal support)
- **No-color**: Plain text output for maximum compatibility

## Style Presets

| Preset | Border | Fills | Best For |
|--------|--------|-------|----------|
| `simple` | `+-` `|` | `#` | Markdown/docs |
| `classic` | `+-+` `| |` | `█` | Legacy terminals |
| `modern` | `┌─┐` `│ │` `└─┘` | `█` | Modern terminals |
| `double` | `╔═╗` `║ ║` `╚═╝` | `█` | Emphasized |
| `minimal` | none | `▓` | Ultra-compact |

## Execution Workflow

### 1. Parse User Input

Extract from user message:
- **Data**: Numeric values, labels, series names
- **Chart type**: bar, line, pie (default: bar)
- **Style**: border preset, colors, width/height
- **Options**: show values, show labels, title

### 2. Validate Data

- Numeric values must be non-negative
- Labels should be concise (< 20 chars)
- Maximum 20 data points per series
- Maximum 10 series per chart

### 3. Generate Chart

For each chart type, apply appropriate ASCII/Unicode characters:

**Bar Chart Algorithm:**
```
- Calculate max value for scaling
- Normalize values to chart height
- Select fill character based on style preset
- Draw bars with optional value labels
```

**Line Chart Algorithm:**
```
- Map data points to grid coordinates
- Draw grid lines based on style
- Plot points with markers (●, ○, ◆, ■)
- Connect with line characters (─, ━, ╱, ╲)
```

**Pie Chart Algorithm:**
```
- Calculate percentages from values
- Assign colors/patterns to segments
- Use block characters for segments: ▓ ▒ ░
- Label with percentage or value
```

### 4. Apply Styling

- Wrap in border characters (per preset)
- Add title at top (if specified)
- Add legend at bottom (for multi-series)
- Apply colors via ANSI escape codes

## Color Usage

**ANSI 16-color codes:**
```
Reset: \033[0m
Black: \033[30m (bg: \033[40m)
Red: \033[31m (bg: \033[41m)
Green: \033[32m (bg: \033[42m)
Yellow: \033[33m (bg: \033[43m)
Blue: \033[34m (bg: \033[44m)
Magenta: \033[35m (bg: \033[45m)
Cyan: \033[36m (bg: \033[36m)
White: \033[37m (bg: \033[47m)
Bright: Add 60 to code (e.g., \033[91m = bright red)
```

**Truecolor format:**
```
\033[38;2;R;G;Bm  (foreground)
\033[48;2;R;G;Bm  (background)
Example: \033[38;2;255;128;0m = orange
```

## Output Formats

### Terminal Output
Direct printing with ANSI codes for colored display.

### Markdown Compatible
Use `--no-color` flag or `simple` preset for plain text that renders in all Markdown viewers.

### File Export
Save to `.txt` or `.md` file with optional color codes preserved.

## Examples

**Simple bar chart:**
```
┌─────────────────────┐
│   Monthly Sales     │
├─────────────────────┤
│ Jan  ████████████   │
│ Feb  ██████████████ │
│ Mar  ██████████     │
└─────────────────────┘
```

**Multi-series line chart:**
```
    Series A  Series B
 10 │                ●──●
  8 │      ●────────╱
  6 │           ╲───╱
  4 │    ●─────╱
  2 │───╱
  0 └────────────────────
```

**Pie chart:**
```
      Sales Distribution
    ┌──────────────────┐
    │   ▓▓▓   Product A│
    │ ▓▓▓▓▓           │
    │▓▓▓▓ Product B   │
    │ ▓▓▓▓▓▓▓  Product C│
    └──────────────────┘
      A: 35%  B: 45%  C: 20%
```

## Usage Patterns

**When user provides raw data:**
```
User: "Q1: 100, Q2: 150, Q3: 120, Q4: 200"
→ Generate bar chart with quarters as labels
```

**When user specifies style:**
```
User: "bar chart with double border and green bars"
→ Apply double border + green color
```

**When user wants specific format:**
```
User: "show me a pie chart without colors"
→ Generate with no-color mode
```

## Edge Cases

- **Empty data**: Show placeholder message
- **Single value**: Center bar or full pie
- **Very large values**: Auto-scale with K/M suffix
- **Negative values**: Show as diverging bars below axis
- **Zero values**: Draw baseline only, no bar

## Performance Notes

- Chart generation is instantaneous
- No external dependencies required
- Pure Python string manipulation
- ANSI codes may not render in all environments
