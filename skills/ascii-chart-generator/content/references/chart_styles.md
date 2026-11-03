# ASCII Chart Style Reference

## Style Presets

The ASCII Chart Generator supports four distinct style presets, each with unique character sets for different use cases.

---

## 1. Simple Style

**Use case**: Email, plain text, maximum compatibility

### Character Set
| Element | Character | Unicode |
|---------|-----------|---------|
| Horizontal | `-` | U+002D |
| Vertical | `\|` | U+007C |
| Bar | `#` | U+0023 |
| Dot | `*` | U+002A |
| Top-Left | `+` | U+002B |
| Top-Right | `+` | U+002B |
| Bottom-Left | `+` | U+002B |
| Bottom-Right | `+` | U+002B |

### Example Output
```
  +------------------------+
  | *   *   *   *          |
  |   *   *   *   *        |
  | *   *   *   *          |
  +------------------------+
    Jan  Feb  Mar  Apr
```

---

## 2. Elegant Style

**Use case**: Documentation, presentations, professional output

### Character Set
| Element | Character | Unicode |
|---------|-----------|---------|
| Horizontal | `─` | U+2500 |
| Vertical | `│` | U+2502 |
| Bar | `█` | U+2588 |
| Dot | `●` | U+25CF |
| Top-Left | `┌` | U+250C |
| Top-Right | `┐` | U+2510 |
| Bottom-Left | `└` | U+2514 |
| Bottom-Right | `┘` | U+2518 |
| Left-T | `├` | U+251C |
| Right-T | `┤` | U+2524 |
| Top-T | `┬` | U+252C |
| Bottom-T | `┴` | U+2534 |
| Cross | `┼` | U+253C |

### Example Output
```
  ┌────────────────────────────────────────────┐
  │                                            │
  │    ●────●────●────●                       │
  │   ╱╲                                    │
  │  ●   ╲───●───●                          │
  │                                            │
  └────────────────────────────────────────────┘
    Jan    Feb    Mar    Apr    May
```

---

## 3. Compact Style

**Use case**: Dense data, narrow terminals, efficiency-focused

### Character Set
| Element | Character | Unicode |
|---------|-----------|---------|
| Horizontal | `━` | U+2501 |
| Vertical | `┃` | U+2503 |
| Bar | `▓` | U+2593 |
| Dot | `●` | U+25CF |
| Top-Left | `┏` | U+250F |
| Top-Right | `┓` | U+2513 |
| Bottom-Left | `┗` | U+2517 |
| Bottom-Right | `┛` | U+251B |
| Left-T | `┣` | U+2523 |
| Right-T | `┫` | U+252B |
| Top-T | `┳` | U+2533 |
| Bottom-T | `┻` | U+253B |
| Cross | `╋` | U+254B |

### Example Output
```
  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
  ┃▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓┃
  ┃▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓┃
  ┃▓▓▓▓▓▓▓▓▓▓▓▓▓┃
  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    Q1    Q2    Q3    Q4
```

---

## 4. Rounded Style

**Use case**: Modern terminals, friendly UI, soft aesthetic

### Character Set
| Element | Character | Unicode |
|---------|-----------|---------|
| Horizontal | `─` | U+2500 |
| Vertical | `│` | U+2502 |
| Bar | `█` | U+2588 |
| Dot | `●` | U+25CF |
| Top-Left | `╭` | U+252D |
| Top-Right | `╮` | U+252E |
| Bottom-Left | `╰` | U+2572 |
| Bottom-Right | `╯` | U+2573 |

### Example Output
```
  ╭────────────────────────────────────╮
  │                                    │
  │    ●────●────●────●               │
  │   ╭─╮                          │
  │  ● ╰────●───●                  │
  │                                    │
  ╰────────────────────────────────────╯
    Jan    Feb    Mar    Apr    May
```

---

## Customization Guide

### Bar Characters

| Density | Characters | Use Case |
|---------|-----------|----------|
| Light | `░` `▒` | Gradients, subtle fills |
| Medium | `▓` | Compact charts |
| Heavy | `█` | Bold, high contrast |
| Double | `�.double` | Alternate pattern |

### Chart Density Mapping

```
Full height:     100% = ████████████████
75% height:      75%  = ██████████████░░
50% height:      50%  = ██████████░░░░░░
25% height:      25%  = █████░░░░░░░░░░
```

---

## Style Selection Guidelines

| Scenario | Recommended Style |
|----------|------------------|
| Plain text email | `simple` |
| GitHub README | `simple` or `elegant` |
| Terminal dashboard | `compact` or `elegant` |
| Documentation | `elegant` |
| Data-heavy reports | `compact` |
| Friendly/fun context | `rounded` |

---

## Combining Styles

You can mix styles programmatically:

```python
from generate_chart import ASCIIChartGenerator

# Create generators with different styles
simple_gen = ASCIIChartGenerator(style='simple')
elegant_gen = ASCIIChartGenerator(style='elegant')
compact_gen = ASCIIChartGenerator(style='compact')

# Generate charts with specific styles
print(simple_gen.bar(data, labels))    # Simple output
print(elegant_gen.line(data, labels))  # Elegant output
```
