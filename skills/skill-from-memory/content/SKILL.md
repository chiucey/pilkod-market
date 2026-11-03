---
name: skill-from-memory
description: Convert memory, conversation history, or completed tasks into publishable OpenClaw skills. Use when (1) A task or workflow should be reusable, (2) Extracting patterns from past conversations, (3) Creating automated workflows from solutions.
version: 1.0.0
trigger: skill-from-memory
---

# Skill From Memory

Transform your work into reusable skills. Extract workflows, solutions, and patterns from conversation history or memory files, package them as skills, and publish to GitHub and ClawHub.

## Overview

This skill automates the complete workflow:
- **Extract** - Parse conversation history or memory for reusable patterns
- **Design** - Structure as a proper skill with SKILL.md and resources
- **Create** - Generate skill files and scripts
- **Publish** - Push to GitHub and publish to ClawHub

## Quick Start

### Create Skill from Recent Conversation

```bash
# Analyze last conversation and create skill draft
./scripts/extract-from-history.sh /path/to/session.jsonl ./my-new-skill

# Or specify a time range
./scripts/extract-from-history.sh /path/to/session.jsonl ./my-new-skill --since "2026-02-03" --pattern "backup"
```

### Create Skill from Memory File

```bash
# Extract from memory markdown
./scripts/extract-from-memory.sh /path/to/memory/2026-02-04.md ./my-new-skill
```

### Full Auto-Create and Publish

```bash
# One command: extract, create, and publish
./scripts/create-and-publish.sh \
  --source /path/to/session.jsonl \
  --skill-name "my-automation" \
  --github-repo "user/my-skills" \
  --clawhub-slug "my-automation"
```

## Workflow Steps

### Step 1: Extract

Identify from conversation/memory:
- **Task Pattern**: What workflow was solved?
- **Inputs/Outputs**: What goes in, what comes out?
- **Scripts/Tools**: What code was written?
- **Key Decisions**: What choices were made?

### Step 2: Design Skill Structure

Decide resource types:
- `scripts/` - For reusable code
- `references/` - For documentation
- `assets/` - For templates/files

### Step 3: Create Skill Files

Generate:
- SKILL.md with frontmatter and instructions
- Scripts in scripts/
- Any reference files

### Step 4: Publish

Push to GitHub and publish to ClawHub

## Scripts Reference

### `extract-from-history.sh`

Parse conversation JSONL for skill content.

```bash
./scripts/extract-from-history.sh <session.jsonl> <output-dir> [options]
```

Options:
- `--since DATE` Only extract from DATE onwards
- `--pattern REGEX` Filter messages matching pattern
- `--tools-only` Only extract tool usage patterns

### `extract-from-memory.sh`

Parse memory markdown files.

```bash
./scripts/extract-from-memory.sh <memory.md> <output-dir>
```

### `create-skill.sh`

Generate skill structure from extracted content.

```bash
./scripts/create-skill.sh <extracted-content-dir> <skill-name> [options]
```

Options:
- `--description "..."` Skill description
- `--type workflow` Skill type (workflow|tool|reference)

### `publish.sh`

Complete publish workflow.

```bash
./scripts/publish.sh <skill-path> [options]
```

Options:
- `--github REPO` GitHub repo (owner/repo)
- `--clawhub-slug ClawHub slug`
- `--version VER` Version tag
- `--skip-github` Skip GitHub push
- `--skip-clawhub` Skip ClawHub publish

## Converting a Task to Skill

**Original Task (from conversation)**:
User: "帮我设置每天自动备份OpenClaw配置" → Agent creates backup scripts + cron setup

**Skill Creation Process**:
1. Extract: `./scripts/extract-from-history.sh ~/.openclaw/agents/main/sessions/latest.jsonl ./extracted-backup`
2. Design:
   - Type: Workflow skill
   - Scripts: backup.sh, setup-cron.sh, cleanup.sh
3. Create: `./scripts/create-skill.sh ./extracted-backup cron-backup --description "Automated backup scheduling with cron" --type workflow`
4. Publish: `./scripts/publish.sh ./cron-backup --github "zfanmy/openclaw-skills" --clawhub-slug "cron-backup" --version "1.0.0"`

## Best Practices

### What Makes a Good Skill

✅ **Do**:
- Single, well-defined purpose
- Reusable across contexts
- Includes working scripts
- Clear usage examples
- Progressive disclosure design

❌ **Don't**:
- Too broad or vague
- Hardcoded personal paths
- Missing error handling
- Undocumented assumptions

### Extracting from Memory

Look for these patterns:
- "帮我写一个脚本..."
- "设置定时任务..."
- "以后每次都要..."
- "这个流程可以复用..."

## Related Skills

- skill-creator - Low-level skill creation utilities
- cron-backup - Example output skill (backup automation)
