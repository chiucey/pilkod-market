# Beautiful-Mermaid Theme Reference

Beautiful-Mermaid provides 15 beautifully designed built-in themes covering light and dark color schemes. Each theme is based on two core colors (background `bg` and foreground `fg`), with optional enriched colors for customization.

## Quick Selection Guide

### Light Themes
| Theme | Background | Foreground | Use Case |
|-------|------------|------------|----------|
| `zinc-light` | #FFFFFF | auto-derive | General purpose light theme |
| `tokyo-night-light` | #d5d6db | #34548a | Soft light |
| `catppuccin-latte` | #eff1f5 | #8839ef | Fresh light |
| `nord-light` | #eceff4 | #5e81ac | Ice blue light |
| `github-light` | #ffffff | #0969da | GitHub light style |
| `solarized-light` | #fdf6e3 | #268bd2 | Solarized light |

### Dark Themes
| Theme | Background | Foreground | Use Case |
|-------|------------|------------|----------|
| `zinc-dark` | #18181B | auto-derive | General purpose dark theme |
| `tokyo-night` | #1a1b26 | #a9b1d6 | Modern Japanese style |
| `tokyo-night-storm` | #24283b | #a9b1d6 | Tokyo Night variant |
| `catppuccin-mocha` | #1e1e2e | #cba6f7 | Warm dark |
| `nord` | #2e3440 | auto-derive | Nordic ice blue style |
| `dracula` | #282a36 | #f8f8f2 | Classic dark theme |
| `github-dark` | #0d1117 | #4493f8 | GitHub dark style |
| `solarized-dark` | #002b36 | #268bd2 | Solarized dark |
| `one-dark` | #282c34 | auto-derive | Atom One Dark style |

---

## Theme Detailed Descriptions

### `zinc-light` (Light)
**Features:** Clean, general-purpose light theme suitable for printing and high-contrast scenarios.

**Configuration:**
```javascript
{
  bg: '#FFFFFF',
  fg: '#27272A'
}
```

**Best Uses:**
- Formal documents and reports
- Print output
- Presentation slides

---

### `zinc-dark` (Dark)
**Features:** Pure dark theme with auto-derived foreground color. Minimalist style.

**Configuration:**
```javascript
{
  bg: '#18181B',
  fg: 'auto-derive'
}
```

**Best Uses:**
- Terminal applications
- Dark mode UI integration
- Code editors

---

### `tokyo-night` (Dark) ⭐ Recommended
**Features:** Modern Japanese style with soft blue tones, designed for developers.

**Configuration:**
```javascript
{
  bg: '#1a1b26',
  fg: '#a9b1d6',
  accent: '#7aa2f7'
}
```

**Best Uses:**
- Modern development documentation
- AI-assisted programming
- Code examples and tutorials

**Visual Features:**
- Deep blue background (#1a1b26)
- Soft purple text (#a9b1d6)
- Bright blue accent (#7aa2f7)

---

### `tokyo-night-storm` (Dark)
**Features:** Deeper variant of Tokyo Night with darker background.

**Configuration:**
```javascript
{
  bg: '#24283b',
  fg: '#a9b1d6',
  accent: '#7aa2f7'
}
```

**Best Uses:**
- Ultra-low light environments
- OLED screen optimization
- Long reading sessions

---

### `tokyo-night-light` (Light)
**Features:** Light version of Tokyo Night, maintaining the same color philosophy.

**Configuration:**
```javascript
{
  bg: '#d5d6db',
  fg: '#34548a'
}
```

**Best Uses:**
- Daytime use
- High contrast needs
- Print-friendly

---

### `catppuccin-mocha` (Dark)
**Features:** Warm, comfortable dark theme with red-purple accents.

**Configuration:**
```javascript
{
  bg: '#1e1e2e',
  fg: '#cba6f7'
}
```

**Best Uses:**
- Long reading sessions (eye-friendly)
- Creative projects
- Design documentation

---

### `catppuccin-latte` (Light)
**Features:** Light variant of Catppuccin, warm and soft.

**Configuration:**
```javascript
{
  bg: '#eff1f5',
  fg: '#8839ef'
}
```

**Best Uses:**
- Daytime light environments
- Purple enthusiasts
- Design-oriented documentation

---

### `nord` (Dark)
**Features:** Nordic-inspired ice blue tones, professional and calm.

**Configuration:**
```javascript
{
  bg: '#2e3440',
  fg: 'auto-derive'
}
```

**Best Uses:**
- Enterprise documentation
- Technical specifications
- System architecture diagrams

---

### `nord-light` (Light)
**Features:** Light version of Nord.

**Configuration:**
```javascript
{
  bg: '#eceff4',
  fg: '#5e81ac'
}
```

**Best Uses:**
- Daytime light use
- Print materials
- Nordic-style projects

---

### `dracula` (Dark) ⭐ Recommended
**Features:** Classic dark theme with high contrast.

**Configuration:**
```javascript
{
  bg: '#282a36',
  fg: '#f8f8f2'
}
```

**Best Uses:**
- Code editor integration
- Developer documentation
- Command-line tools

---

### `github-light` (Light)
**Features:** GitHub light theme, web-friendly.

**Configuration:**
```javascript
{
  bg: '#ffffff',
  fg: '#0969da'
}
```

**Best Uses:**
- GitHub README
- Web documentation
- Online tutorials

---

### `github-dark` (Dark)
**Features:** GitHub dark theme, familiar to GitHub users.

**Configuration:**
```javascript
{
  bg: '#0d1117',
  fg: '#4493f8'
}
```

**Best Uses:**
- GitHub documentation
- GitHub Issues and Discussions
- Open source projects

---

### `solarized-light` (Light)
**Features:** Classic light theme designed by Ethan Schoonover.

**Configuration:**
```javascript
{
  bg: '#fdf6e3',
  fg: '#268bd2'
}
```

**Best Uses:**
- Research papers
- Academic documents
- Precise color work

---

### `solarized-dark` (Dark)
**Features:** Dark version of Solarized with carefully tuned contrast.

**Configuration:**
```javascript
{
  bg: '#002b36',
  fg: '#268bd2'
}
```

**Best Uses:**
- Long-form document reading
- Scientific papers
- Programming textbooks

---

### `one-dark` (Dark)
**Features:** Classic One Dark theme from Atom editor.

**Configuration:**
```javascript
{
  bg: '#282c34',
  fg: 'auto-derive'
}
```

**Best Uses:**
- Atom users
- JavaScript projects
- Web development documentation

---

## Custom Themes

### Basic Customization (Mono Mode)

Only two colors are needed to create a beautiful theme:

```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output output.svg \
  --bg '#0f0f0f' \
  --fg '#e0e0e0'
```

The system automatically derives all other colors.

### Advanced Customization (Enriched Mode)

For richer color schemes, provide optional accent colors:

```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output output.svg \
  --bg '#0f0f0f' \
  --fg '#e0e0e0' \
  --accent '#ff6b6b' \
  --muted '#666666' \
  --line '#4a90e2' \
  --surface '#1a1a1a' \
  --border '#2a2a2a'
```

### Color Parameter Guide

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `--bg` | Background color (required) | `#1a1a1a` |
| `--fg` | Text color (required) | `#e0e0e0` |
| `--accent` | Arrow heads and accents | `#7aa2f7` |
| `--muted` | Secondary text and labels | `#666666` |
| `--line` | Edge/connector lines | `#3d59a1` |
| `--surface` | Node fill | `#292e42` |
| `--border` | Node stroke | `#3d59a1` |

---

## Theme Selection Decision Tree

```
What style of theme do you want?
├── Light
│   ├── Minimal/Clean? → zinc-light
│   ├── GitHub style? → github-light
│   ├── Solarized? → solarized-light
│   ├── Ice blue? → nord-light
│   ├── Purple? → catppuccin-latte
│   └── Soft Japanese? → tokyo-night-light
│
└── Dark
    ├── Recommended general? → tokyo-night ⭐
    ├── Classic dark? → dracula ⭐
    ├── Minimal/Pure? → zinc-dark
    ├── Nordic style? → nord
    ├── Warm & cozy? → catppuccin-mocha
    ├── GitHub style? → github-dark
    ├── Ultra dark background? → tokyo-night-storm
    ├── Academic/Precise? → solarized-dark
    └── Atom style? → one-dark
```

---

## Practical Examples

### Example 1: Using Tokyo Night for Technical Documentation

```bash
node scripts/render.mjs \
  --input architecture.mmd \
  --output architecture.svg \
  --theme tokyo-night
```

### Example 2: Creating Print-Friendly Diagrams

```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output diagram.svg \
  --theme zinc-light
```

### Example 3: Batch Applying Themes

```bash
node scripts/batch.mjs \
  --input-dir ./diagrams \
  --output-dir ./output \
  --format svg \
  --theme dracula
```

### Example 4: Custom Enterprise Theme

```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output output.svg \
  --bg '#1a1a1a' \
  --fg '#ffffff' \
  --accent '#0066cc' \
  --border '#333333'
```

---

## Color Value Quick Reference

### Common Hex Colors
| Color Name | Hex Code | Use Case |
|------------|----------|----------|
| Pure White | #FFFFFF | Light backgrounds |
| Pure Black | #000000 | Dark backgrounds |
| Dark Gray | #1a1a1a | Friendly dark |
| Light Gray | #f0f0f0 | Friendly light |
| Blue | #0066cc | Accent color |
| Green | #00cc00 | Success color |
| Red | #cc0000 | Warning/Error |
| Purple | #9966cc | Creative projects |

---

## FAQ

**Q: Which theme should I use?**
A: If unsure, recommended `tokyo-night` (dark) or `zinc-light` (light).

**Q: How to choose a theme for GitHub README?**
A: Use `github-light` or `github-dark` to match GitHub's theme.

**Q: Can I mix colors from multiple themes?**
A: Yes, use Enriched Mode to customize any color combination.

**Q: Do themes support transparent backgrounds?**
A: Yes, add the `--transparent` flag.

**Q: How to recommend themes to users in AI chat?**
A: Based on project type: development projects → Tokyo Night, enterprise → Nord, printing → Zinc Light.
