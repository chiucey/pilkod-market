# ANSI Color Codes Reference

## Overview

The ASCII Chart Generator supports ANSI 256-color mode for enhanced visual differentiation in terminal environments.

---

## Basic Color Codes (16-color)

### Foreground Colors
| Color Name | Normal Code | Bright Code | Example |
|------------|-------------|-------------|---------|
| Black | `\033[30m` | `\033[90m` | ▓▓▓▓ |
| Red | `\033[31m` | `\033[91m` | ▓▓▓▓ |
| Green | `\033[32m` | `\033[92m` | ▓▓▓▓ |
| Yellow | `\033[33m` | `\033[93m` | ▓▓▓▓ |
| Blue | `\033[34m` | `\033[94m` | ▓▓▓▓ |
| Magenta | `\033[35m` | `\033[95m` | ▓▓▓▓ |
| Cyan | `\033[36m` | `\033[96m` | ▓▓▓▓ |
| White | `\033[37m` | `\033[97m` | ▓▓▓▓ |

### Background Colors
| Color Name | Normal Code | Bright Code |
|------------|-------------|-------------|
| Black | `\033[40m` | `\033[100m` |
| Red | `\033[41m` | `\033[101m` |
| Green | `\033[42m` | `\033[102m` |
| Yellow | `\033[43m` | `\033[103m` |
| Blue | `\033[44m` | `\033[104m` |
| Magenta | `\033[45m` | `\033[105m` |
| Cyan | `\033[46m` | `\033[106m` |
| White | `\033[47m` | `\033[107m` |

### Control Codes
| Code | Name | Usage |
|------|------|-------|
| `\033[0m` | Reset | Reset all attributes |
| `\033[1m` | Bold | Bold/bright text |
| `\033[3m` | Italic | Italic text |
| `\033[4m` | Underline | Underlined text |
| `\033[9m` | Strikethrough | Strikethrough text |

---

## 256-Color Mode

For more precise color control, use 256-color codes:

### Format
```
\033[38;5;Nm    # Foreground
\033[48;5;Nm    # Background
```
Where `N` is the color number (0-255)

### Color Palette Ranges

| Range | Numbers | Description |
|-------|---------|-------------|
| Grayscale | 0-15 | Basic + bright |
| Standard | 16-231 | 6×6×6 color cube |
| Extended | 232-255 | Grayscale ramp |

### 6×6×6 Color Cube

The standard 216-color cube uses this formula:
```
Color = 16 + 36×R + 6×G + B
Where R, G, B ∈ {0, 1, 2, 3, 4, 5}
```

### Useful 256-Color Codes

| Color | 256-Code | Common Use |
|-------|----------|------------|
| Dark Gray | `\033[38;5;240m` | Secondary text |
| Light Gray | `\033[38;5;250m` | Muted elements |
| Dark Red | `\033[38;5;124m` | Error/negative |
| Orange | `\033[38;5;208m` | Warning |
| Light Green | `\033[38;5;82m` | Success/positive |
| Purple | `\033[38;5;135m` | Special/highlight |
| Sky Blue | `\033[38;5;75m` | Info/links |
| Pink | `\033[38;5;205m` | Accent |

---

## Chart Color Mapping

### Default Palette

| Series | Color Name | ANSI Code |
|--------|------------|-----------|
| Series 1 | Red | `\033[91m` |
| Series 2 | Green | `\033[92m` |
| Series 3 | Yellow | `\033[93m` |
| Series 4 | Blue | `\033[94m` |
| Series 5 | Magenta | `\033[95m` |
| Series 6 | Cyan | `\033[96m` |

### Extended Palette (for 6+ series)

```python
EXTENDED_COLORS = [
    '\033[38;5;196m',  # Red
    '\033[38;5;082m',  # Green
    '\033[38;5;226m',  # Yellow
    '\033[38;5;021m',  # Blue
    '\033[38;5;201m',  # Magenta
    '\033[38;5;051m',  # Cyan
    '\033[38;5;208m',  # Orange
    '\033[38;5;165m',  # Purple
    '\033[38;5;045m',  # Teal
    '\033[38;5;210m',  # Pink
    '\033[38;5;129m',  # Violet
    '\033[38;5;118m',  # Lime
]
```

---

## Style Classes

### Semantic Colors

```python
SEMANTIC_COLORS = {
    'success': '\033[92m',      # Green
    'warning': '\033[93m',     # Yellow
    'error': '\033[91m',       # Red
    'info': '\033[94m',        # Blue
    'neutral': '\033[90m',     # Gray
    'highlight': '\033[95m',   # Magenta
}
```

### Usage Example

```python
from generate_chart import ASCIIChartGenerator

# Create with colors enabled
gen = ASCIIChartGenerator(use_colors=True)

# Custom color mapping
gen.COLOR_SEQUENCE = [
    'red', 'green', 'yellow', 'blue',
    'magenta', 'cyan', 'orange', 'purple'
]

# Generate colored chart
print(gen.bar([30, 60, 90], ['Low', 'Medium', 'High']))
```

---

## Terminal Compatibility

### Full Support (256 colors)
- Modern terminals (iTerm2, Konsole, Terminator)
- tmux/screen with 256-color support
- VS Code integrated terminal
- Git Bash / WSL

### Limited Support (16 colors)
- Legacy terminals
- Basic SSH clients
- Some mobile terminals

### No Color Support
- Pure text mode
- File redirection (use `script` command)
- Very old terminals

### Detection

```python
import os
import sys

def supports_colors():
    """Check if terminal supports colors"""
    # Check if redirected
    if not sys.stdout.isatty():
        return False

    # Check TERM variable
    term = os.getenv('TERM', '')
    color_terms = {'xterm', 'xterm-256color', 'screen-256color', 'linux'}
    return any(t in term for t in color_terms)

# Usage
if supports_colors():
    gen = ASCIIChartGenerator(use_colors=True)
else:
    gen = ASCIIChartGenerator(use_colors=False)
```

---

## Best Practices

1. **Use bright variants** for better contrast on dark backgrounds
2. **Maintain accessibility** - don't rely solely on color
3. **Reset after use** - always end with `\033[0m`
4. **Test in multiple terminals** - colors vary between apps
5. **Consider colorblind users** - add patterns or labels

---

## Reset Sequence

Always end colored output with reset:

```python
# Correct
print(f"\033[91m{text}\033[0m")

# Wrong - may affect subsequent output
print(f"\033[91m{text}")
```
