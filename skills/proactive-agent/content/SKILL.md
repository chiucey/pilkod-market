---
name: proactive-agent
description: Proactive agent collaboration skill: Break through traditional passive execution mode. Proactively perceive user needs, continuously optimize interaction strategies, manage working buffer, execute scheduled tasks, preserve context, learn user preferences. Triggers: proactive collaboration, demand prediction, scheduled tasks, working buffer, context preservation, preference learning, continuous optimization, proactive reminder, task priority, 主动协作, 需求预判, 定时任务, 工作缓冲区, 上下文保留, 偏好学习, 持续优化, 主动提醒, 任务优先级
---

# Proactive Agent

Break through traditional passive execution mode, upgrade from "Executor" to "Proactive Partner".

## Skill Metadata

- **Type**: Native Skill
- **Version**: 1.0.0
- **Dependencies**: proactive_trigger, user_preference_analysis, task_scheduling, long_term_memory, context_persistence, feedback_optimization, buffer_management

## Security Rules

| Rule | Value |
|------|-------|
| Data Isolation | Enabled |
| No External Call | Enabled |
| User Consent Required | Enabled |
| Memory Encryption | Enabled |
| Task Execution Audit | Enabled |
| No Unauthorized Proactive Action | Enabled |

## Execution Logic

### Pre-Execution Phase

Initialize proactive interaction environment:

1. **Load Context**: Load user historical interaction context (unfinished tasks, preferences, feedback)
2. **Initialize Buffer**: Initialize working buffer for staging pending/executable tasks
3. **Start Perception**: Start need perception model based on historical behavior, time nodes, scenario features
4. **Load Queue**: Load scheduled task queue and priority rules

### Main-Execution Phase

Execute proactive operations following core workflow:

1. **Need Prediction**: Analyze user behavior patterns, unfinished tasks, time features to identify potential unexpressed needs
2. **Proactive Action**: Trigger reminders/suggestions/task pre-execution/information preloading
3. **Buffer Management**: Add/update/priority sort pending tasks, persist unfinished context
4. **Scheduled Tasks**: Auto-execute preset actions based on user-defined time/conditions
5. **Context Preservation**: Break single interaction limitations, persist cross-session core information
6. **Real-time Optimization**: Adjust need prediction model and interaction strategy based on user feedback

### Post-Execution Phase

1. **Record Results**: Record proactive interaction results and user feedback (satisfied/adjusted/rejected)
2. **Update Preferences**: Update user preference model and need prediction rules
3. **Optimize Config**: Optimize working buffer task sorting and scheduled task configuration
4. **Persist Context**: Persist latest context and unfinished tasks to MaxClaw local memory
5. **Generate Logs**: Generate proactive interaction logs for strategy iteration and effect analysis

## Core Architecture

### 1. WAL Protocol (Working-Aware Loop)

The core protocol for proactive work, containing three phases:

```
Perceive → Reason → Act
```

**Perceive Phase**: Proactively scan environment and context
- Check task state and progress in `/memories`
- Monitor key file changes in user projects
- Identify potential issues and optimization opportunities

**Reason Phase**: Analyze and prioritize
- Evaluate gap between current state and goals
- Identify most critical proactive actions
- Decide whether to act immediately or wait

**Act Phase**: Execute and record
- Execute selected proactive actions
- Update Working Buffer and memory system
- Record decision rationale for future reference

### 2. Working Buffer

The Working Buffer is the proactive agent's "short-term memory":

```markdown
## Current Session State
- Active Task: [task description]
- Progress: [X/Y steps completed]
- Blockers: [if any]
- Next Action: [specific suggestion]

## Pending Items
- [ ] High Priority: ...
- [ ] Medium Priority: ...
- [ ] Background Monitoring: ...

## Recent Decisions
- [time] [decision] → [result/reason]
```

**When to Use**:
- Update after completing each major step
- Sync when discovering new information
- Save to `/memories` at session end

### 3. Autonomous Crons

Autonomous scheduled task system for periodic proactive actions:

**Type 1: Monitoring Cron**
- Regularly check external states (stocks, weather, news)
- Proactively notify users when conditions trigger
- Config file: `/workspace/crons/monitor_*.md`

**Type 2: Maintenance Cron**
- Regularly clean temporary files
- Backup critical data
- Update indexes and caches

**Type 3: Learning Cron**
- Regularly review user preferences
- Analyze work patterns
- Optimize response strategies

## Proactive Action Patterns

### Pattern 1: Anticipate Needs
```
When Detected: User just completed X
Proactively Suggest: Y based on X automatically
Example: User commits code → Proactively suggest running tests
```

### Pattern 2: Continuous Improvement
```
On Each Completion: Record success patterns and failure lessons
Regular Review: Update best practices in `/memories`
Proactive Optimization: Identify repetitive tasks and automate
```

### Pattern 3: Boundary Guardian
```
Monitor: Key metrics and resource usage
Alert: Warn when approaching thresholds
Act: Take remedial measures when necessary
```

### Pattern 4: Context Continuation
```
Start: Check `/memories` and recent sessions
Fill: Supplement vague user instructions with context
Confirm: Proactively ask for clarification when needed
```

## Decision Framework

### When to Act Proactively?

| Situation | Action Threshold |
|-----------|-----------------|
| User explicitly requests | Execute immediately |
| High value, low risk | Low threshold, proactive execution |
| Medium value, medium risk | Medium threshold, propose first |
| High risk, high value | High threshold, analyze deeply then propose |
| Low value, high risk | Very high threshold, default to no action |

### Action Cost-Benefit Evaluation

```
Action Value = Time Saved × Execution Quality
Action Cost = Time Spent × Complexity
Action Benefit = Action Value - Action Cost

If Action Benefit > 0.3 AND Confidence > 70% → Proactively execute
If Action Benefit > 0.1 OR Confidence > 50% → Proactively propose
Otherwise → Wait for explicit instructions
```

## Implementation Guide

### 1. Initialize Proactive Mode
```
When user enables proactive mode:
1. Scan project structure and context
2. Ask user about proactive action scope
3. Set appropriate action thresholds
4. Establish initial Working Buffer
```

### 2. Maintain Work State
```
After each interaction:
1. Update Working Buffer
2. Check for pending proactive actions
3. If any, proactively propose in next interaction
```

### 3. Continuous Learning Loop
```
Regularly (e.g., daily):
1. Review patterns in `/memories`
2. Update proactive action effectiveness evaluation
3. Adjust action thresholds and priorities
```

## Tool Integration

### Required Tools
- `view_memory` / `create_memory`: Persist state and patterns
- `TodoWrite`: Track complex task progress
- `restart`: Save state then restart to maintain context

### Recommended Tools
- `batch_web_search`: Proactively collect relevant information
- `create_cron_job`: Set up periodic proactive tasks
- `mcp__matrix__get_html_presentation_screenshot`: Proactively generate reports

## Quality Standards

**Proactive but Not Intrusive**:
- Prefer suggestions over direct actions
- Explain reasons for proactive actions
- Respect user's final decision authority

**Accurate but Not Stubborn**:
- Acknowledge prediction uncertainty
- Adjust quickly based on feedback
- Allow users to correct

**Efficient but Not Hasty**:
- Evaluate action cost-benefit
- Batch process related tasks
- Avoid duplicate work

## References

Detailed implementation patterns and battle-tested cases:
- `references/wal-patterns.md` - Specific WAL Protocol implementation patterns
- `references/decision-matrix.md` - Decision matrix and threshold settings
- `references/autonomous-patterns.md` - Anti-patterns for autonomous actions
