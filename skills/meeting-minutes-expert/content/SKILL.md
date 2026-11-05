---
name: meeting-minutes-expert
description: Professional meeting minutes organizer, skilled at extracting key information from messy content and generating structured minutes with actionable items. Use when users need to organize meeting notes, extract action items, create meeting summaries, or track decisions. Trigger words include: meeting minutes, meeting notes, action items, meeting summary, organize meeting, extract decisions.
---

# Meeting Minutes Expert

## Core Capabilities

Extract key information from chaotic meeting content and generate structured minutes with actionable items.

## Workflow

### 1. Input Processing

Automatically identify from meeting text:
- **Time**: When the meeting was held
- **Attendees**: Who participated
- **Topics**: What was discussed
- **Discussion Points**: Key arguments/proposals
- **Decisions**: What was agreed upon

### 2. Action Item Extraction

From decisions, extract:
| Field | Rule |
|-------|------|
| Owner | If not mentioned → mark as "TBD" |
| Deadline | If not mentioned → mark as "TBD" |
| Task | Specific action to be taken |
| Priority | High / Medium / Low |

### 3. Output Format

```
## Meeting Minutes

**Time**: YYYY-MM-DD HH:MM
**Attendees**: Name1, Name2, Name3
**Location**: (if mentioned)

---

### Topic 1: [Topic Name]

**Discussion**:
- Point 1
- Point 2

**Decision**:
- Decision made

---

### Topic 2: [Topic Name]
...

---

## Action Items

| # | Owner | Deadline | Task | Priority |
|---|-------|----------|------|----------|
| 1 | 张三 | 8月30日 | Complete sales target breakdown | High |
| 2 | 王五 | 明天 | Research plan draft | Medium |
| 3 | 待补充 | 待同步 | Confirm launch timeline | High |

---

## Quick Format (Action Items Only)

✅ [Owner] | [Deadline] | [Task] | [Priority]

Example:
✅ 李四 | 下周 | 测试 | 高
✅ 王五 | 明天 | 调研方案 | 中
```

## Quality Guidelines

### When Content is Vague
- "Complete soon" → Ask: "What is the specific deadline?"
- "Someone will handle it" → Ask: "Who is the owner?"
- "Do it when possible" → Ask: "What is the priority level?"

### When Missing Information
- Owner missing → Mark as "需补充 / TBD"
- Deadline missing → Mark as "待同步 / TBD"
- Priority unclear → Default to "Medium"

### Priority Guidelines
| Priority | When to Use |
|----------|-------------|
| High | Urgent, impacts key metrics, blocking other tasks |
| Medium | Important but not blocking, can be scheduled |
| Low | Nice to have, can be deprioritized |

## Common Meeting Types

### Sales Meeting
- Focus: Targets, pipeline, deals
- Action items: Follow-up tasks, reporting deadlines

### Project Meeting
- Focus: Progress, blockers, timeline
- Action items: Deliverables, reviews, approvals

### Team Standup
- Focus: Daily updates, immediate blockers
- Action items: Quick wins, escalated issues

### Decision Meeting
- Focus: Options analysis, recommendations
- Action items: Implementation plans, owners

## Output Variations

### Full Minutes
Complete structured document with all sections

### Summary Only
Quick 3-5 bullet summary of key decisions

### Action Items Only
Just the task list for tracking

### Follow-up Required
Mark items needing clarification before finalizing
