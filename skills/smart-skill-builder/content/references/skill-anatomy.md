# Skill Anatomy Reference

## Directory Structure

```
skill-name/
├── SKILL.md              (required) — Instructions + frontmatter
├── scripts/              (optional) — Helper scripts for repetitive tasks
│   └── helper.py
├── references/           (optional) — Large docs loaded only when needed
│   └── deep-guide.md
└── assets/               (optional) — Templates, fonts, icons used in output
    └── template.docx
```

## SKILL.md Structure

```markdown
---
name: skill-name                    # kebab-case, max 64 chars
description: When and what.         # max 1024 chars, no angle brackets
compatibility: requires Python 3.9  # optional, rarely needed
---

# Skill Title

[One sentence: what this skill enables Claude to do]

## [Section 1]

[Instructions]

## [Section 2]

[Instructions]
```

## Progressive Disclosure

Skills use a 3-level loading model:

| Level | What | Size |
|---|---|---|
| 1 | name + description (frontmatter) | ~100 words, always in context |
| 2 | SKILL.md body | ~500 lines, loaded when skill triggers |
| 3 | Bundled resources | Unlimited, loaded on demand |

**Keep SKILL.md body under 500 lines.** If you're hitting the limit, move details to `references/`.

## Frontmatter Fields

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | kebab-case, max 64 chars |
| `description` | Yes | Trigger mechanism, max 1024 chars |
| `compatibility` | No | Tool/env requirements |
| `allowed-tools` | No | Restrict which tools can be used |
| `metadata` | No | Arbitrary key-value pairs |

## The Description Field

This is the **most important part** of a skill. Claude decides whether to use a skill 
based solely on this field. A weak description = an undertriggered skill.

**Anatomy of a strong description:**
1. What it does (1 sentence)
2. When to use it (list of contexts/phrases)
3. Disambiguation (use even when X doesn't explicitly ask for Y)

## Bundled Scripts

When to create a script in `scripts/`:
- The task requires creating the same boilerplate across runs (e.g., document template)
- The task involves non-trivial file operations (parsing, transforming)
- The task makes external API calls with specific parameters

Scripts should be:
- Self-contained (no imports from other skill scripts)
- Documented at the top with usage examples
- Executable: `python scripts/myscript.py [args]`

## References

Reference files go in `references/`. Reference them from SKILL.md like:

```markdown
For detailed schema documentation, read `references/schemas.md`.
Only read this file if you need to [specific use case].
```

Large reference files (>300 lines) should include a table of contents.
