---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 6777c36c6bdac9514c2dd334a9ed8543
    PropagateID: 6777c36c6bdac9514c2dd334a9ed8543
    ReservedCode1: 3044022002596ae866e7f88a9978a981f7bf35a68e0bab68313fe606484fe212e4f410e902205773b2e57bcfd1fa7acedfc88bf55898cfa752e23e9be18f782fc5a1697c6e7e
    ReservedCode2: 3046022100d80112847510ddaf48859706d215db921f35035bde2159e8bc225af3dd18eab90221008ceafc94d93a2c1e0ad5642e4320291e60414a7cf7037b6676bd3503e5aff1de
---

# TavoAI Macro Reference

Complete reference for TavoAI macro system. These macros work in character cards, world book entries, and system prompts.

## Variable Macros

Variables store and retrieve dynamic values within a conversation.

### Local Variables (per-entry)

| Macro | Syntax | Description |
|-------|--------|-------------|
| Set | `{{setvar:key=value}}` | Set a variable to a value |
| Get | `{{getvar:key}}` | Retrieve a variable value |
| Add | `{{addvar:key=value}}` | Add value to existing variable |
| Increment | `{{incvar:key}}` | Increase variable by 1 |
| Decrement | `{{decvar:key}}` | Decrease variable by 1 |

### Global Variables (persistent across entries)

| Macro | Syntax | Description |
|-------|--------|-------------|
| Set Global | `{{setglobalvar:key=value}}` | Set a global variable |
| Get Global | `{{getglobalvar:key}}` | Retrieve a global variable |
| Add Global | `{{addglobalvar:key=value}}` | Add to global variable |

### Usage Examples

```
{{setvar:trust=0}}
{{setvar:affection=50}}
{{setvar:chapter=1}}

After the user helps {{char}}: {{addvar:trust=10}}
Current trust level: {{getvar:trust}}

{{setglobalvar:story_progress=2}}
We are in chapter {{getglobalvar:story_progress}}
```

### Use Cases

- Tracking relationship meters (trust, affection, loyalty)
- Progress through story chapters
- Counting interactions or events
- Storing conditional flags

## Date/Time Macros

Dynamic datetime injection based on current system time.

| Macro | Output Example | Description |
|-------|---------------|-------------|
| `{{time}}` | `14:30` | Current time (HH:mm) |
| `{{date}}` | `2024-01-15` | Current date |
| `{{weekday}}` | `Monday` | Day of week |
| `{{isotime}}` | `14:30:00` | ISO format time |
| `{{isodate}}` | `2024-01-15` | ISO format date |
| `{{idleDuration}}` | `5m` / `2h` | Time since last message |
| `{{time::UTC+9}}` | `23:30` | Time in specific timezone |

### Usage Examples

```
Current time: {{time}}
Today is {{weekday}}, {{date}}

You last messaged {{idleDuration}} ago.
```

### Use Cases

- Time-based character behavior
- Historical timeline references
- Event scheduling
- Time-sensitive dialogues

## Random Macros

### Basic Random Selection

| Macro | Syntax | Description |
|-------|--------|-------------|
| Random | `{{random:A,B,C}}` | Randomly pick one (comma-separated) |
| Pick | `{{pick:A,B,C}}` | Deterministic random (same prompt = same result) |
| Trigger Rate | `{{random::0.5}}` | Random boolean with probability |
| Multi-pick | `{{random::A::B::C}}` | Random pick with double-colon syntax |

### Dice Rolling

| Macro | Syntax | Description |
|-------|--------|-------------|
| Roll | `{{roll:6}}` or `{{roll:d6}}` | Roll a d6 die |
| Roll Multi | `{{roll:3d6}}` | Roll 3d6 |
| Dice | `{{dice:2d20}}` | Roll 2d20 |

### Usage Examples

```
{{random:你好,嗨,哟}}

{{random::0.5}} - Triggers 50% of the time

{{roll:d20}} - Roll a 20-sided die

{{dice:3d6}} - Roll three six-sided dice

{{pick:选项A,选项B,选项C}} - Deterministic pick
```

### Use Cases

- Varying dialogue options
- Random events
- Game mechanics (dice rolls)
- Non-repeating random content

## Format Macros

| Macro | Description |
|-------|-------------|
| `{{newline}}` | Insert a newline character |
| `{{space}}` | Insert a space |
| `{{trim}}` | Trim leading/trailing whitespace |
| `{{noop}}` | No operation (placeholder) |

### Comment Macros

| Macro | Syntax |
|-------|--------|
| Single-line | `{{//comment}}` or `{{/*comment*/}}` |
| Block | `{{/* multi-line comment */}}` |

Comments are not rendered in output.

### Escape Macros

| Syntax | Description |
|--------|-------------|
| `\{{}}` | Escape curly braces |
| `\{{text}}` | Escape specific text within braces |

### Usage Examples

```
Line 1{{newline}}Line 2

{{space}}{{space}}Indented text

{{trim}}  trimmed  {{/trim}}

{{// This is a comment and won't appear }}

\{{this will appear as literal}} = {this will appear as literal}
```

## Macro Assistant

Input box macro buttons for quick insertion.

### Syntax

```javascript
//# Button Label
//macro_key:macro_value
```

### Usage Examples

```
//# Greeting
//greet:你好！今天怎么样？

//# Action
//action:*深呼吸*

//# Roll Dice
//roll:/roll 3d6
```

This creates buttons in the input area that insert the configured text when clicked.

## Decorator Syntax

Control when and how world book entries are activated.

| Decorator | Syntax | Description |
|-----------|--------|-------------|
| Activate After | `@@activate_after N` | Activate after N messages |
| Depth | `@@depth N` | Insert at message depth N |
| Position | `@@position POS` | Set insertion position |
| Role | `@@role ROLE` | Specify message role |

### Position Values

| Value | Description |
|-------|-------------|
| `before_char` | Before character message |
| `after_char` | After character message |
| `system` | As system message |

### Role Values

| Value | Description |
|-------|-------------|
| `system` | System context |
| `assistant` | Character message |
| `user` | User message |

### Usage Examples

```
@@activate_after 3
@@depth 5
@@position before_char
@@role system
```

## Advanced Variable Operations

### Conditional Content

Variables can be combined with macros for conditional rendering:

```
{{#if {{getvar:trust}} > 50}}
She smiles warmly at you.
{{#else}}
She eyes you suspiciously.
{{/if}}
```

### Variable Math

```
Initial trust: {{setvar:trust=0}}
After event: {{addvar:trust=25}}
Final trust: {{getvar:trust}}
```

### String Variables

Variables can store text:

```
{{setvar:greeting=Hello}}
{{getvar:greeting}}, traveler!
```

## Best Practices

1. **Use descriptive names**: `trust_level` instead of `t1`
2. **Initialize variables**: Set initial values before use
3. **Consider scope**: Use local for per-entry, global for persistent
4. **Test randomness**: `{{pick}}` for reproducible testing
5. **Escape properly**: Use `\{{}}` when literal braces are needed
6. **Comment generously**: Use `{{//}}` for documentation
7. **Keep it simple**: Complex nested macros can be hard to debug
