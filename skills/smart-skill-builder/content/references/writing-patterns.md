# Skill Writing Patterns

Common patterns for well-structured skills. Use these as templates.

---

## Pattern 1: File Transformation Skill

For skills that take a file as input and produce a transformed file.

```markdown
---
name: file-transformer
description: Use when the user wants to [transform action] their [file type] files. 
  Trigger on: [list 5-8 specific trigger phrases]. Even if the user doesn't mention 
  [file type], trigger when they describe the transformation.
---

# [Skill Name]

[One sentence: what this does and why it's useful]

## Workflow

1. **Read** the input file from the uploads directory
2. **Process** [the core transformation, explain how]
3. **Write** the output to `/mnt/user-data/outputs/`
4. **Present** the file to the user

## Input Handling

- Accept: [list accepted formats]
- If format is unrecognized: [explain what to do]
- If file is missing: ask the user to upload it

## Output Format

[Exact description of the output with an example]

## Edge Cases

- [Edge case 1]: [how to handle]
- [Edge case 2]: [how to handle]
```

---

## Pattern 2: Research / Synthesis Skill

For skills that gather information and produce a report or summary.

```markdown
---
name: research-skill
description: Use when the user wants to research, analyze, or synthesize information 
  about [topic]. Trigger on phrases like [list phrases]. Use even when the user 
  describes the output type instead of the process ("give me a summary of...", 
  "what's the current state of...").
---

# [Skill Name]

[What it produces and why it's valuable]

## Research Process

1. **Search** for [what to search]
2. **Evaluate** sources by [criteria]
3. **Synthesize** into the output format below

## Output Structure

Use this exact template:

# [Topic]
## Summary (2-3 sentences)
## Key Findings
[bullet points]
## Sources
[citations]

## Quality Bar

Before presenting: verify that [quality check], ensure [completeness check].
```

---

## Pattern 3: Interactive / Multi-Step Skill

For skills with phases or decisions.

```markdown
---
name: interactive-skill
description: ...
---

# [Skill Name]

## Phase 1: Understand

Before doing anything, gather: [list what's needed]

Ask in a single message. If context already contains answers, skip to Phase 2.

## Phase 2: Plan

Based on what the user provided, create a brief plan and confirm with them:
> "Here's my plan: [X, Y, Z]. Does this look right?"

## Phase 3: Execute

[Detailed execution instructions]

## Phase 4: Present

[How to present results]
```

---

## Pattern 4: Code Generation Skill

```markdown
---
name: code-generator
description: Use when the user wants to generate, scaffold, or write [type] code.
  Trigger on: "write me a...", "create a script that...", "help me build...". 
  Use even for vague requests like "I need code that does X".
---

# [Code Generation Skill]

## Before Writing Code

Clarify if missing:
- Target language/framework (infer from context first)
- [Other key unknowns]

## Code Standards

- [Standard 1: explain why]
- [Standard 2: explain why]

## Output Format

Always output:
1. The complete code (no truncation)
2. Brief explanation of key choices
3. How to run it

## Error Handling

Include error handling for: [list common failure modes]
```

---

## Trigger Description Templates

Copy and adapt:

```
Use whenever the user wants to [verb] their [noun]. Trigger on phrases like "[phrase1]", 
"[phrase2]", "[phrase3]". Also trigger when the user describes the outcome they want 
("[outcome description]") even without mentioning [skill name] explicitly. 
Use even for casual requests like "[casual phrase]".
```

```
Trigger this skill for any task involving [domain]. This includes: [list 5+ subtasks]. 
Use even if the user only describes the problem, not the solution — phrases like 
"[problem description]" should trigger this skill.
```
