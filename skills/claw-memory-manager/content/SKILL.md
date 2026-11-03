---
name: claw-memory-manager
description: "Universal memory management system for OpenClaw/MaxClaw agents. Use when: (1) Creating memory files for sessions, tasks, or projects, (2) Archiving old memories by date, (3) Generating searchable memory indices, (4) Searching memory content by keywords, (5) Organizing knowledge bases, (6) Managing context recovery files, (7) Maintaining project documentation. Designed for general-purpose use cases: research, work, projects, learning, or any domain."
---

# Claw Memory Manager - 通用记忆管理系统

A flexible memory management system designed for OpenClaw/MaxClaw agents to organize, search, and retrieve information across sessions. Works for any domain: research, development, business, education, personal knowledge management, etc.

## Core Concepts

### Memory Storage Location
- **Primary Path**: `/memories/` - OpenClaw's persistent memory directory
- **Session Memory**: `/memories/sessions/` - Per-session context
- **Project Memory**: `/memories/projects/` - Project-specific knowledge
- **Knowledge Base**: `/memories/knowledge/` - Structured information

### Directory Structure

```
/memories/
├── sessions/                 # Session-specific memories
│   ├── YYYY-MM-DD-session.md
│   └── context-recovery.md
├── projects/                  # Project memories
│   ├── project-name/
│   │   ├── overview.md
│   │   ├── decisions.md
│   │   └── progress.md
├── knowledge/                 # Knowledge base
│   ├── topics/
│   │   └── topic-name.md
│   └── references/
├── archive/                   # Archived memories (by month)
│   └── YYYY-MM/
└── index.md                   # Auto-generated index
```

## Document Naming Conventions

| Type | Format | Example | Location |
|------|--------|---------|----------|
| Session Record | `YYYY-MM-DD-session.md` | `2026-03-26-session.md` | `sessions/` |
| Project Overview | `project-name/` folder | `my-project/` | `projects/` |
| Topic Note | `{topic}.md` | `api-design.md` | `knowledge/topics/` |
| Context Recovery | `context-recovery.md` | - | `sessions/` |
| Archived | `YYYY-MM-DD.md` | same as source | `archive/YYYY-MM/` |

## Memory Types

### 1. Session Memory
Quick session context and notes for the current conversation.

```markdown
# Session: 2026-03-26

## Session Summary
Brief description of this session's purpose and context.

## Key Decisions
- Decision 1
- Decision 2

## Next Steps
- [ ] Task 1
- [ ] Task 2

## Important Findings
Notable discoveries or information gathered.
```

### 2. Project Memory
Long-term project context and documentation.

```markdown
# Project: {Project Name}

## Overview
What this project is about.

## Current Status
Current state and recent developments.

## Architecture/Structure
Technical or organizational structure.

## Progress Log
### YYYY-MM-DD
- Entry 1
- Entry 2

## Decisions & Rationale
Key decisions and why they were made.
```

### 3. Knowledge Note
Structured information on any topic.

```markdown
# Topic: {Subject}

## Summary
One-paragraph overview.

## Key Concepts
- Concept 1: explanation
- Concept 2: explanation

## Resources
- [Resource 1](url)
- [Resource 2](url)

## Related Topics
- Related Topic 1
- Related Topic 2
```

## Scripts

### 1. Create Memory File

```bash
# Create session memory for today
python scripts/create_memory.py --type session

# Create project memory
python scripts/create_memory.py --type project --name "my-project"

# Create knowledge note
python scripts/create_memory.py --type knowledge --name "api-design"

# Create for specific date
python scripts/create_memory.py --type session --date 2026-03-25
```

### 2. Generate Index

```bash
# Generate/refresh index.md
python scripts/generate_index.py

# Output to custom location
python scripts/generate_index.py -o /path/to/index.md
```

### 3. Search Memories

```bash
# Basic search
python scripts/search_memories.py "keyword"

# Search specific file type
python scripts/search_memories.py "API" --type md

# Adjust context lines
python scripts/search_memories.py "decision" --context 3
```

### 4. Archive Old Memories

```bash
# Preview what would be archived
python scripts/archive_memories.py --dry-run

# Archive memories older than 30 days
python scripts/archive_memories.py --days 30

# Execute archiving
python scripts/archive_memories.py --days 30
```

## Workflows

### Daily Session Memory

1. Start new session → Create session memory
2. During session → Update session memory with key info
3. End session → Add summary and next steps
4. Next session → Check session memory for context

### Project Memory

1. New project → Create project folder and overview
2. During work → Update progress log and decisions
3. Milestone → Document architecture and key decisions
4. Project end → Add final summary and lessons learned

### Knowledge Management

1. Learn something new → Create knowledge note
2. Find connections → Link related topics
3. Update regularly → Keep notes current
4. Search when needed → Find information quickly

## Integration

### With OpenClaw Cron

```bash
# Daily index refresh
cron add --schedule "0 23 * * *" --command "python /path/to/scripts/generate_index.py"

# Weekly archive old memories
cron add --schedule "0 0 * * 0" --command "python /path/to/scripts/archive_memories.py --days 30"
```

### Context Recovery

Use session memory for context recovery on restart:

1. Session ends → Save summary to `/memories/sessions/YYYY-MM-DD-session.md`
2. Restart occurs → Read session memory
3. Continue → Context restored

### Multi-Agent Context Sharing

```markdown
# Share context between agents
/memories/projects/shared-context/
├── agent-a-notes.md
├── agent-b-notes.md
└── shared-decisions.md
```

## Best Practices

- **Naming**: Use descriptive, consistent names with dates when applicable
- **Structure**: Keep related content together; use folders for projects
- **Updates**: Update memory files during work, not just at the end
- **Search**: Build index regularly for fast retrieval
- **Archive**: Archive old content to keep recent memory fast
- **Link**: Reference related documents for context

## Script Paths

| Script | Purpose |
|--------|---------|
| `scripts/create_memory.py` | Create new memory files (session/project/knowledge) |
| `scripts/generate_index.py` | Generate searchable index of all memories |
| `scripts/search_memories.py` | Search memories by keyword |
| `scripts/archive_memories.py` | Archive old memories by date |
