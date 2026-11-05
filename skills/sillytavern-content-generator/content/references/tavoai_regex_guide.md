---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f0e5360981f417386d1c7fd549a541a9
    PropagateID: f0e5360981f417386d1c7fd549a541a9
    ReservedCode1: 3045022100ddfc1aedf703e02565cbac96c9de2318ef226031b93ea88e1b6c41e9463505c502205aa8eed8dea5b0619488ccd2b0f83a81512798d83f6670b67f305e4ca4bdb9c5
    ReservedCode2: 304502202e3924934bdebaa6d5e15a591d89b5e3d576c7dcda0ad0365497cdc87bd668fd022100a08f46a4def5bceac338f18aee376948d6d3c1f8fe12e16d76e46e4e5dd04beb
---

# TavoAI Regex Configuration Guide

Complete guide for TavoAI's regex replacement system. Regex rules allow dynamic text transformation during message processing.

## Overview

Regex rules in TavoAI intercept messages and apply find/replace transformations. They can operate on:
- User messages
- Character messages
- Thinking content
- World book entries

## Rule Structure

```json
{
  "name": "Rule Display Name",
  "findRegex": "pattern to match",
  "replaceString": "replacement text",
  "Trim Out": "text to remove before replacement",
  "placements": ["userMessage", "characterMessage"],
  "timing": "onDisplay",
  "substitution": "original",
  "enabled": true,
  "isRegex": true,
  "ignoreCase": false,
  "useReplacement": true,
  "filterByRoles": []
}
```

## Field Reference

### Basic Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name for the rule |
| `findRegex` | string | Yes | Regex pattern to match |
| `replaceString` | string | No | Replacement text |
| `Trim Out` | string | No | Text to remove before replacement |
| `enabled` | boolean | No | Whether rule is active (default: true) |

### Matching Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `isRegex` | boolean | true | Enable regex matching |
| `ignoreCase` | boolean | false | Case-insensitive matching |

### Replacement Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `useReplacement` | boolean | true | Use replaceString |
| `substitution` | string | "original" | Substitution mode |

### Placement and Timing

| Field | Type | Description |
|-------|------|-------------|
| `placements` | array | Where to apply the rule |
| `timing` | string | When to process the rule |
| `filterByRoles` | array | Limit to specific roles |

## Placements

Define where the regex rule applies.

### Available Placements

| Value | Description |
|-------|-------------|
| `userMessage` | User's messages |
| `characterMessage` | Character's responses |
| `thinking` | Internal thinking/thought blocks |
| `worldbook` | Lorebook/world book entries |

### Examples

```json
// Apply to user messages only
"placements": ["userMessage"]

// Apply to both user and character
"placements": ["userMessage", "characterMessage"]

// Apply everywhere
"placements": ["userMessage", "characterMessage", "thinking", "worldbook"]
```

## Timing Options

Control when the regex transformation occurs.

### Available Timing Values

| Value | Description |
|-------|-------------|
| `onDisplay` | When message is displayed |
| `onSend` | When user sends a message |
| `onSendDisplay` | On both send and display |
| `onReceive` | When character message is received |
| `onReceiveEdit` | When received message is edited |

### Timing Flow

```
User types message
    ↓
onSend / onSendDisplay ← User message processed here
    ↓
AI generates response
    ↓
onReceive / onReceiveEdit ← Character message processed here
    ↓
onDisplay ← Final display processing
```

### Common Use Cases by Timing

| Timing | Use Case |
|--------|----------|
| `onSend` | Sanitize user input, add formatting |
| `onReceive` | Transform character output |
| `onDisplay` | Final display cleanup |

## Substitution Modes

| Value | Description |
|-------|-------------|
| `original` | Keep original text if no match |
| `escaped` | Escape special characters |
| `none` | No substitution |

## Replacement String Features

### Capture Groups

Use `$1`, `$2`, etc. for capture groups:

```json
{
  "findRegex": "(\\w+) said",
  "replaceString": "[$1] whispered"
}
```

### Special Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{{match}}` | Full matched text |
| `{{match:0}}` | Full matched text (alternative) |
| `{{match:1}}` | First capture group |
| `{{match:N}}` | Nth capture group |

### Examples

```json
// Replace with captured name
{
  "findRegex": "([A-Z]\\w+) attacked",
  "replaceString": "{{char}} defended against $1"
}

// Use full match in replacement
{
  "findRegex": "\\*\\*(.+?)\\*\\*",
  "replaceString": "{{match}}"
}
```

## Complete Examples

### Example 1: Character Name Normalization

```json
{
  "name": "Normalize Character Name",
  "findRegex": "银发公主|冰霜公主",
  "replaceString": "{{char}}",
  "Trim Out": "",
  "placements": ["userMessage", "characterMessage"],
  "timing": "onDisplay",
  "substitution": "original",
  "enabled": true,
  "isRegex": false,
  "ignoreCase": true,
  "useReplacement": true,
  "filterByRoles": []
}
```

### Example 2: Bold to Italic Conversion

```json
{
  "name": "Convert Bold to Italic",
  "findRegex": "\\*\\*(.+?)\\*\\*",
  "replaceString": "_$1_",
  "Trim Out": "",
  "placements": ["userMessage", "characterMessage"],
  "timing": "onDisplay",
  "substitution": "original",
  "enabled": true,
  "isRegex": true,
  "ignoreCase": false,
  "useReplacement": true,
  "filterByRoles": []
}
```

### Example 3: Remove Spoiler Tags

```json
{
  "name": "Remove Spoilers",
  "findRegex": "\\|\\|(.+?)\\|\\|",
  "replaceString": "[SPOILER]",
  "Trim Out": "",
  "placements": ["characterMessage"],
  "timing": "onReceive",
  "substitution": "original",
  "enabled": true,
  "isRegex": true,
  "ignoreCase": false,
  "useReplacement": true,
  "filterByRoles": []
}
```

### Example 4: Time Stamp Injection

```json
{
  "name": "Add Timestamp",
  "findRegex": ".*",
  "replaceString": "[{{time}}] {{match}}",
  "Trim Out": "",
  "placements": ["userMessage"],
  "timing": "onSend",
  "substitution": "original",
  "enabled": true,
  "isRegex": true,
  "ignoreCase": false,
  "useReplacement": true,
  "filterByRoles": []
}
```

### Example 5: Role-Play Action Formatting

```json
{
  "name": "Format Actions",
  "findRegex": "\\*\\*(.+?)\\*\\*",
  "replaceString": "<action>$1</action>",
  "Trim Out": "",
  "placements": ["userMessage", "characterMessage"],
  "timing": "onDisplay",
  "substitution": "original",
  "enabled": true,
  "isRegex": true,
  "ignoreCase": false,
  "useReplacement": true,
  "filterByRoles": []
}
```

### Example 6: Variable Trigger

```json
{
  "name": "Trigger Variable Set",
  "findRegex": "trust me|believe me",
  "replaceString": "{{setvar:trust={{addvar:trust=5}}}}",
  "Trim Out": "",
  "placements": ["userMessage"],
  "timing": "onSend",
  "substitution": "original",
  "enabled": true,
  "isRegex": false,
  "ignoreCase": true,
  "useReplacement": false,
  "filterByRoles": []
}
```

## Common Regex Patterns

### Basic Patterns

| Pattern | Matches |
|---------|---------|
| `hello` | Literal "hello" |
| `hello\|hi` | "hello" or "hi" |
| `^hello` | "hello" at start |
| `hello$` | "hello" at end |
| `.` | Any single character |
| `.*` | Any characters (greedy) |
| `.+` | One or more characters |

### Character Classes

| Pattern | Matches |
|---------|---------|
| `[abc]` | a, b, or c |
| `[^abc]` | Not a, b, or c |
| `[a-z]` | Any lowercase letter |
| `[A-Z]` | Any uppercase letter |
| `[0-9]` | Any digit |

### Quantifiers

| Pattern | Matches |
|---------|---------|
| `a*` | Zero or more a |
| `a+` | One or more a |
| `a?` | Zero or one a |
| `a{3}` | Exactly 3 a |
| `a{2,5}` | Between 2 and 5 a |

### Groups and Capturing

| Pattern | Description |
|---------|-------------|
| `(abc)` | Capture group |
| `(?:abc)` | Non-capturing group |
| `(?<name>abc)` | Named capture |
| `\1` | Backreference to group 1 |

## Best Practices

1. **Be specific**: More precise patterns avoid false matches
2. **Test patterns**: Use regex tester tools before implementing
3. **Consider timing**: Choose appropriate timing for your use case
4. **Order rules**: Process order matters for multiple rules
5. **Keep it simple**: Complex regex can be hard to debug
6. **Use non-greedy**: Prefer `.+?` over `.*` when possible
7. **Escape properly**: Escape special regex characters with `\`

## Troubleshooting

### Pattern Not Matching

- Check if `isRegex` is set correctly
- Verify case sensitivity with `ignoreCase`
- Test pattern in external regex tool

### Unexpected Replacements

- Check `Trim Out` field
- Review substitution mode
- Verify placement includes target

### Performance Issues

- Avoid overly complex patterns
- Don't use `.*` when more specific patterns work
- Limit rules to necessary placements only

## Export/Import

Regex rules can be exported and imported as JSON:

```json
[
  {
    "name": "Rule 1",
    "findRegex": "...",
    ...
  },
  {
    "name": "Rule 2",
    "findRegex": "...",
    ...
  }
]
```

Save as `.json` file and import through TavoAI settings.
