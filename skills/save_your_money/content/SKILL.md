---
name: save_your_money
description: Token optimization skill that reduces API costs by caching skill results, batching operations, and reusing computation. Use when the user wants to save tokens on repetitive tasks, similar queries, or multi-step workflows.
---

# Save Your Money

Token optimization through caching, batching, and result reuse.

## Core Strategies

### 1. Cache-First Pattern

Before invoking any skill or subagent:

1. **Check cache** - Has this exact query been processed?
2. **If hit** - Return cached result, skip the skill call
3. **If miss** - Execute, then cache the result

Cache key: Use semantic hash (not exact match) to catch near-duplicates.

### 2. Batching Pattern

Instead of multiple sequential skill calls:

1. **Collect all operations** - What needs to be done?
2. **Batch similar tasks** - Group by target skill
3. **Single invocation** - Pass all tasks to one skill call
4. **Split results** - Distribute outputs

### 3. Self-Execution Pattern

Before delegating to a skill, ask:

- "Can I do this directly without loading the skill?"
- If yes → Execute with general knowledge
- If no → Then invoke the skill

Loading a skill costs ~500-2000 tokens. Only load when truly needed.

### 4. Context Trimming

After skill completes:

1. Summarize key outputs (keep essence)
2. Discard full context from invoked skills
3. Keep only what future tasks need

## Integration Workflow

When user requests involve skills:

```
Request → Check Cache → [Hit: Return] → [Miss: Execute + Cache]
         → Analyze → Batching? → [Yes: Batch] → [No: Self-Exec or Delegate]
         → Execute → Trim Context → Store in Cache
```

## Cache Storage

Location: `C:\Users\Jinpeng Wang\Desktop\.sisyphus\cache\`

Format per request:
- `cache/<skill_name>/<hash>.json` - Result + timestamp
- Keys: query, result_summary, full_result_path, timestamp

See [references/cache-system.md](references/cache-system.md) for details.

## Implementation

See [references/implementation-patterns.md](references/implementation-patterns.md) for code patterns.

## Anti-Patterns to Avoid

- **Shotgun delegation**: Calling 5 skills when 1 would suffice
- **Full context preservation**: Keeping all skill context indefinitely
- **No caching**: Treating every request as brand new
- **Always delegate**: Not considering direct execution