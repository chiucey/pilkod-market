---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 40c6058b36a40dcfdf35b06db900e651
    PropagateID: 40c6058b36a40dcfdf35b06db900e651
    ReservedCode1: 30460221008f118d128331cff7583cb495406d8a74b99db41c03b2d14000afbef982fe7f6e0221009dc0b98c91c9e6d6b016368aaa82a743164211273102378f25574695d805d72f
    ReservedCode2: 3046022100abe735d9558868a39c252de3e148a6b8c6de1d075b296173928c90a2ca9474dc022100d4d25cddeb5c170dcab59bc00dfb4bc5b51f9f87323c25918e4e7a33684f5dd0
---

# OpenClaw Skill Template

Use this template when creating new OpenClaw skills.

## Basic Skill Template

```yaml
---
name: my-custom-skill
description: A clear description of what this skill does. Include trigger phrases like "Use when users ask to..."
---

# My Custom Skill

## Overview
Brief description of the skill's purpose.

## Usage
How to use this skill.

## Examples
Real-world usage examples.
```

## Advanced Skill Template with Gating

```yaml
---
name: advanced-skill
description: An advanced skill with gating requirements. Use when...
homepage: https://example.com/docs
user-invocable: true
disable-model-invocation: false
metadata:
{
  "openclaw": {
    "emoji": "🔧",
    "os": ["darwin", "linux"],
    "requires": {
      "bins": ["required-binary"],
      "env": ["REQUIRED_ENV_VAR"],
      "config": ["feature.enabled"]
    },
    "install": [
      {
        "id": "brew",
        "kind": "brew",
        "formula": "required-package",
        "bins": ["required-binary"]
      }
    ]
  }
}
---

# Advanced Skill

## Requirements
- Binary: required-binary
- Environment: REQUIRED_ENV_VAR
- Config: feature.enabled = true

## Installation
Install via: `clawhub install advanced-skill`

## Usage
Describe usage instructions...
```

## Tool Dispatch Skill Template

```yaml
---
name: tool-dispatch-skill
description: A skill that directly dispatches to a tool. Use when users want to...
command-dispatch: tool
command-tool: my-tool-name
command-arg-mode: raw
---

# Tool Dispatch Skill

## Tool
This skill dispatches directly to `my-tool-name`.

## Arguments
Raw arguments are passed directly to the tool.
```

## Multi-Agent Skill Template

```yaml
---
name: multiagent-skill
description: A skill for multi-agent setups. Use when...
metadata:
{
  "openclaw": {
    "always": true,
    "skillKey": "custom-config-key"
  }
}
---

# Multi-Agent Skill

This skill is available to all agents and has custom configuration.
```
