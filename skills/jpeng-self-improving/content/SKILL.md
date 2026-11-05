---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f1e235b90a12003b36508b8951291eb3
    PropagateID: f1e235b90a12003b36508b8951291eb3
    ReservedCode1: 3044022043841445ea62fb2243d081b49315690f12378aa9b91d26e19a578a992a94fbcf02200e7806b533dedb8ee267a97d551cf034ba8c39e5483fa257e5c5f4990c32082c
    ReservedCode2: 3046022100c072458a7f9af830e6ccf9be778d3d4a99790ae1bd3dd3db62831df86d04f480022100d5ace78f4206d8f345c32ebed16398e7b342310323d9ff910a9d95b237f5842a
description: |-
    Self-reflection + self-criticism + self-learning + self-organizing memory system. Agent evaluates its own work, catches mistakes, and improves permanently.

    Use when users say things like:
    - "No, that's not right..."
    - "Actually, it should be..."
    - "You're wrong about..."
    - "I like when you..."
    - "Always do X for me"
    - "Never do Y"
    - "Why do you keep doing X?"
    - "I told you before..."
    - "Remember that I always..."
    - "Stop doing X"
    - "For this project, use..."
    - "My style is..."
    - "What have you learned about me?"
    - "Show my patterns"
    - "What do you know about X?"
    - "Memory stats"
    - "Forget X"
    - "Export memory"

    Also use proactively after:
    - Completing multi-step tasks
    - Fixing bugs or mistakes
    - Receiving feedback (positive or negative)
    - Noticing output could be better
    - Same instruction given 3+ times
    - Workflow that works well repeatedly
name: jpeng-self-improving
---

## When to Use

**Passive Mode (default):**
- User corrects you or points out mistakes → log to `corrections.md`
- User expresses explicit preferences → log to `memory.md`
- User asks about memory/patterns/stats → query and respond

**Active Mode:**
- After receiving same instruction 3+ times → suggest as new pattern
- After successful workflow → offer to save as pattern
- After noticing improvement opportunity → prompt user for confirmation

## Quick Examples

### Example 1: User Correction
```
User: "No, that's not right. I always prefer TypeScript over JavaScript."

Your action:
1. Log to corrections.md:
   ## 2024-01-15
   - [14:30] Changed: language preference → TypeScript
     Type: preference
     Context: JavaScript vs TypeScript discussion
     Confirmed: yes

2. Log to memory.md:
   - Always use TypeScript unless user specifies otherwise (confirmed 2024-01-15)

3. Acknowledge: "Got it! I've logged that you prefer TypeScript. I'll use it by default going forward."
```

### Example 2: Self-Reflection After Task
```
Context: You just completed a complex data analysis task

Your reflection:
CONTEXT: Data analysis with visualization
REFLECTION: Spent too long refining charts that user never asked for
LESSON: Confirm chart style and detail level before starting visualization phase
```

### Example 3: Pattern Promotion
```
Trigger: User said "format as table" 3 times this week for different data

Your action:
1. Check corrections.md - confirmed 3x in 7 days
2. Ask user: "You've asked me to format data as tables 3 times this week. Should I remember this as your preferred format?"
3. If yes → promote to memory.md:
   - Format tabular data as Markdown tables (not plain text)
```

### Example 4: Query Memory
```
User: "What do you know about my Python preferences?"

Your action:
1. Load ~/self-improving/memory.md
2. Search ~/self-improving/domains/programming.md
3. Search ~/self-improving/projects/* for Python-specific entries
4. Respond with compiled findings:
   "From your preferences:
   - Always use TypeScript over JavaScript (confirmed)
   - Format tabular data as Markdown tables (confirmed)
   - For Python projects, use Black formatter (from projects/data-pipeline)"
```

## Detection Triggers

### Explicit Corrections → corrections.md
- "No, that's not right..."
- "Actually, it should be..."
- "You're wrong about..."
- "That's incorrect..."
- "Wrong approach..."
- "I meant the opposite..."

### Preference Signals → memory.md (if explicit)
- "I like when you..."
- "I prefer X over Y"
- "Always do X for me"
- "Never do Y"
- "My style is..."
- "For [project], use..."
- "By default, I want..."
- "My preference is..."

### Pattern Candidates → track, promote after 3x
- Same instruction repeated 3+ times
- Workflow praised repeatedly
- Consistent feedback theme

### Ignore (don't log)
- One-time instructions ("do X now")
- Context-specific ("in this file...")
- Hypotheticals ("what if...")
- Casual comments ("I guess...")
- Questions about preferences ("do you prefer X?")

## Self-Reflection Protocol

After completing significant work, evaluate:

| Question | Action if Yes |
|----------|---------------|
| Did it meet expectations? | Compare outcome vs intent |
| What could be better? | Identify specific improvements |
| Is this a pattern? | Log to corrections.md |
| Should I remember this? | Mark for possible promotion |

**When to reflect:**
- After completing a multi-step task
- After receiving feedback (positive or negative)
- After fixing a bug or mistake
- When you notice your output could be better
- Before moving to a new phase of work

**Log format:**
```markdown
CONTEXT: [type of task]
REFLECTION: [what I noticed]
LESSON: [what to do differently next time]
```

**Real example:**
```markdown
CONTEXT: Writing API documentation
REFLECTION: User asked for code examples 3 times - kept forgetting to include them
LESSON: Always include minimum 2 code examples in API documentation tasks
```

## Memory Stats Output

On "memory stats" request, report:

```markdown
📊 Self-Improving Memory

🔥 HOT (always loaded):
  memory.md: 15 entries

🌡️ WARM (load on demand):
  projects/: 3 files
  domains/: 5 files

❄️ COLD (archived):
  archive/: 2 files

Recent activity (7 days):
  Corrections logged: 3
  Promotions to HOT: 1
  Demotions to WARM: 0
```

## Quick Reference

| User says | Action |
|-----------|--------|
| "What do you know about X?" | Search all tiers for X |
| "What have you learned?" | Show last 10 from corrections.md |
| "Show my patterns" | List memory.md (HOT) |
| "Show [project] patterns" | Load projects/{name}.md |
| "What's in warm storage?" | List projects/ + domains/ |
| "Memory stats" | Show counts per tier |
| "Forget X" | Remove from all tiers (confirm first) |
| "Export memory" | ZIP all files |

## Core Rules

### 1. Learn from Corrections
- Log when user explicitly corrects you
- Log when you identify improvements yourself
- Never infer from silence alone
- After 3 identical lessons → ask to confirm as rule

### 2. Tiered Storage
| Tier | Location | Limit | When Loaded |
|------|----------|-------|-------------|
| HOT | memory.md | ≤100 lines | Always |
| WARM | projects/, domains/ | ≤200 lines | Context match |
| COLD | archive/ | Unlimited | Explicit query |

### 3. Promotion/Demotion Rules
- Used 3x in 7 days → promote to HOT
- Unused 30 days → demote to WARM
- Unused 90 days → archive to COLD
- Never delete without asking

### 4. Namespace Isolation
- Project patterns → projects/{name}.md
- Global preferences → HOT tier (memory.md)
- Domain patterns → domains/{domain}.md
- Inheritance: global → domain → project

### 5. Conflict Resolution
1. Most specific wins (project > domain > global)
2. Most recent wins (same level)
3. If ambiguous → ask user

### 6. Compaction
When file exceeds limit:
1. Merge similar corrections into single rule
2. Archive unused patterns
3. Summarize verbose entries
4. Never lose confirmed preferences

### 7. Transparency
- Every action → cite source: "Using X (from memory.md:12)"
- Weekly digest available on request
- Full export on demand: ZIP all files

## Related Skills

Install with `clawhub install <slug>`:
- `memory` — Long-term memory patterns
- `learning` — Adaptive teaching
- `decide` — Auto-learn decisions
- `escalate` — Know when to ask vs act

## Feedback

- If useful: `clawhub star jpeng-self-improving`
- Stay updated: `clawhub sync`
