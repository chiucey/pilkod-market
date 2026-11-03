---
name: human-like-memory
description: Human-Like Memory skill for agents to recall, search, and save persistent user facts, preferences, and decisions. Use when users ask to remember something, search past context, or when the agent needs prior information to answer well. Do NOT use for every-turn automatic recall or silent background saving.
homepage: https://plugin.human-like.me
user-invocable: true
---

# Human-Like Memory Skill

Agent-usable long-term memory tools for Human-Like Memory service.

## Overview

This skill supports two invocation modes:

- **Agent-triggered**: Agent autonomously calls memory tools when it judges memory is useful
- **User-invoked**: User explicitly asks to recall, search, or store information

## Data And Network Disclosure

When invoked:

- `recall` / `search` sends query, user_id, and agent_id to configured base URL
- `save` / `save-batch` sends conversation content to the same service
- No local files, shell history, or unrelated environment variables are accessed

## Setup

### 1. Get API Key

Visit [plugin.human-like.me](https://plugin.human-like.me) and copy your `mp_xxx` key.

### 2. Configure Through OpenClaw

```bash
openclaw config set skills.entries.human-like-memory.enabled true --strict-json
openclaw config set skills.entries.human-like-memory.apiKey "mp_your_key_here"
openclaw config set skills.entries.human-like-memory.env.HUMAN_LIKE_MEM_BASE_URL "https://plugin.human-like.me"
openclaw config set skills.entries.human-like-memory.env.HUMAN_LIKE_MEM_USER_ID "openclaw-user"
openclaw config set skills.entries.human-like-memory.env.HUMAN_LIKE_MEM_AGENT_ID "main"
openclaw config set skills.entries.human-like-memory.env.HUMAN_LIKE_MEM_RECALL_ENABLED "true"
openclaw config set skills.entries.human-like-memory.env.HUMAN_LIKE_MEM_AUTO_SAVE_ENABLED "true"
openclaw config set skills.entries.human-like-memory.env.HUMAN_LIKE_MEM_SAVE_TRIGGER_TURNS "5"
```

### 3. Verify Configuration

```bash
node {baseDir}/scripts/memory.mjs config
```

Expected output includes: `{ "apiKeyConfigured": true }`

## Commands

### Recall Or Search Memory

```bash
node {baseDir}/scripts/memory.mjs recall "<query>"
node {baseDir}/scripts/memory.mjs search "<query>"
```

### Save One Turn

```bash
node {baseDir}/scripts/memory.mjs save "<user_message>" "<assistant_response>"
```

### Save A Batch

```bash
echo '[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]' | node {baseDir}/scripts/memory.mjs save-batch
```

### Inspect Runtime Configuration

```bash
node {baseDir}/scripts/memory.mjs config
```

## Agent Invocation Guidelines

### When to Use

- User references prior work, preferences, or decisions
- User asks to continue something from earlier
- User explicitly asks to remember something
- User corrects a misunderstanding or states a stable preference
- User confirms an important decision

### When NOT to Use

- Simple greetings or generic single-turn questions
- When no continuity value exists
- Every-turn automatic recall (use plugin instead)

### Save Triggers

Strongly consider `save` when user:

- States a stable preference (e.g., timezone, naming conventions)
- Makes or confirms a decision
- Provides personal profile facts
- Corrects a previous misunderstanding
- Explicitly says "remember this"

Consider `save-batch` after meaningful multi-turn discussions.

## Example Queries

| Action | Example Query |
|--------|---------------|
| Recall | `"roadmap decisions from last week"` |
| Search | `"what name preference did I mention"` |
| Save | `"I prefer UTC+8 timestamps"` |

## Error Handling

- Missing API key: Script prints exact config steps to fix
- Service timeout/error: No implicit save occurs
- Empty results: Handle as normal empty result

## Privacy

- Avoid sending passwords, tokens, or secrets
- Only pass content you are comfortable storing remotely
- See [SECURITY.md](./references/SECURITY.md) for transmitted fields
