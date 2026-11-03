---
name: hermes-skills
description: Hermes Skills System - AI Self-Improving Memory and Skill Creation Framework. Use when creating skills, recording workflows, managing memories, building learning loops, or implementing the Hermes agent methodology. Triggers include: create a skill, remember this workflow, learn from experience, skill creation, memory management, extract lessons, build agent memory, persistent learning system.
---

# Hermes Skills Framework

The self-improving AI skill system inspired by Nous Research's Hermes Agent.

## Core Philosophy

**Closed Learning Loop**: Create → Use → Learn → Improve → Persist

## Memory Architecture

### Two Memory Stores

| Store | Purpose | Limit | File |
|-------|---------|-------|------|
| **MEMORY.md** | Agent's personal notes, environment facts, lessons learned | 2,200 chars | `~/.hermes/memories/` |
| **USER.md** | User profile, preferences, communication style | 1,375 chars | `~/.hermes/memories/` |

### Memory Actions

- **add** — Add new memory entry
- **replace** — Update existing entry (substring matching via `old_text`)
- **remove** — Remove outdated entry

### Entry Format

```
Section 1: content here
§
Section 2: content here
§
Section 3: multiline
content here
```

---

## Skills System

### SKILL.md Structure

```yaml
---
name: skill-name
description: Brief description of what this skill does
version: 1.0.0
platforms: [macos, linux]     # Optional
metadata:
  hermes:
    tags: [tag1, tag2]
    category: category-name
---
```

### Skill Content Sections

```markdown
# Skill Title

## When to Use
Trigger conditions for this skill.

## Procedure
1. Step one
2. Step two

## Pitfalls
- Known failure modes and fixes

## Verification
How to confirm it worked.
```

### Progressive Disclosure Levels

| Level | Function | Output | Use Case |
|-------|----------|--------|----------|
| Level 0 | `skills_list()` | `[{name, description, category}]` | Discovery |
| Level 1 | `skill_view(name)` | Full content + metadata | Usage |
| Level 2 | `skill_view(name, path)` | Specific reference file | Deep dive |

---

## Learning Loop Implementation

### 1. Automatic Capture Triggers

| Scenario | Action |
|----------|--------|
| User correction | Prompt: "Remember this correction?" |
| Successful workflow | Prompt: "Save this workflow?" |
| Task completion | Prompt: "Extract lessons?" |
| Pattern detected | Prompt: "Log this pattern?" |

### 2. Memory Entry Template

```markdown
## [Title]
**Date**: YYYY-MM-DD
**Source**: [user_input/auto_capture/correction]
**Context**: [situation description]

### What Happened
[description]

### Lesson Learned
[key takeaway]

### Next Time
[specific action to take]

### Tags
- [tag1]
- [tag2]
```

### 3. Skill Creation Workflow

```
Observation → Pattern Recognition → Hypothesis → Skill Draft → Testing → Refinement
```

---

## Best Practices

1. **Token Efficiency**: Use progressive disclosure, load full content only when needed
2. **Actionable Memories**: Every entry must have "next time" guidance
3. **Unique Entries**: No duplicate memories
4. **Security**: Scan for injection patterns before saving
5. **Capacity Management**: Consolidate when >80% full

---

## Integration with Workflow

```
┌─────────────────────────────────────────────────────────┐
│                    User Interaction                      │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   [Correction]  [Workflow]   [Question]
        │             │             │
        ▼             ▼             ▼
   Ask: Save?    Ask: Log?    Search Memory
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              [Memory Store]
                      │
                      ▼
              [System Prompt]
                      │
                      ▼
           [Improved Response]
```

---

*Inspired by Nous Research's Hermes Agent — Building AI that learns from every interaction.*
