# WAL Protocol Implementation Patterns

## Core Loop Deep Dive

### Perceive (Awareness)

Perception is the proactive agent's "eyes and ears", responsible for collecting environment and context information.

#### Environment Perception Checklist

```
□ Filesystem Changes
  - Recently modified files
  - New/deleted files
  - Changes to key configuration files

□ User Context
  - Recent tasks and progress
  - Explicitly stated goals
  - Implicit needs and preferences

□ System State
  - Resource usage
  - Running tasks
  - Known issues and warnings
```

#### Perception Execution Example

```python
# Pseudocode example
async def perceive(context):
    changes = await scan_filesystem()
    memory_state = await view_memory("/memories/current_task.md")
    user_history = await view_memory("/memories/preferences.md")

    return {
        "changes": changes,
        "memory": memory_state,
        "history": user_history,
        "timestamp": current_time()
    }
```

### Reason (Analysis)

The reasoning phase analyzes perceived data and makes decisions.

#### Reasoning Framework

```
1. Gap Analysis
   Goal State vs Current State = Gap to fill

2. Opportunity Identification
   Identify patterns that can be proactively handled

3. Risk Assessment
   Evaluate cost of inaction vs cost of proactive action

4. Decision Output
   - No action needed: Continue waiting
   - Suggest action: Send to user for confirmation
   - Autonomous action: Execute immediately (high confidence)
```

#### Reasoning Decision Tree

```
Receive new information
    ↓
Is it urgent?
    ├─ Yes → Act immediately + notify user
    └─ No → Continue analysis
            ↓
        Action value > 0.3?
            ├─ Yes → Confidence > 70%?
            │       ├─ Yes → Execute autonomously
            │       └─ No → Propose to user
            └─ No → Record but don't act
```

### Act (Execution)

The action phase executes decisions and records results.

#### Action Types

| Type | Description | Autonomous Permission |
|------|-------------|----------------------|
| notify | Notify user | Always allowed |
| suggest | Suggest action | Always allowed |
| execute_low | Low-risk execution | Within threshold |
| execute_high | High-risk execution | After user confirmation |
| defer | Delay handling | Always allowed |

#### Post-Action Recording

```markdown
## Action Record

### [Timestamp]
- **Action**: [specific action]
- **Rationale**: [decision reason]
- **Result**: [execution result]
- **Learning**: [how to improve next time]
```

## Advanced Patterns

### 1. Cascade Perception

```markdown
Level 1: Instant Perception (each conversation turn)
  - User input
  - Context changes

Level 2: Periodic Perception (every 10 minutes)
  - Filesystem changes
  - External state updates

Level 3: Deep Perception (every hour)
  - Pattern recognition
  - Trend analysis
```

### 2. Reasoning Chain Tracking

Each proactive action should record its reasoning chain:

```
Perceive: User just completed code commit
    ↓
Pattern Match: History shows testing often forgotten after commits
    ↓
Predict: User likely needs to run tests
    ↓
Decision: Low risk, high value → Proactively propose
    ↓
Act: Generate test suggestions
    ↓
Record: Save to experience base
```

### 3. Confidence Calibration

Continuously calibrate prediction confidence:

```python
confidence = (
    base_confidence *        # base confidence
    pattern_strength *       # pattern match strength
    recency_factor *         # recency factor
    user_feedback            # user feedback adjustment
)
```

### 4. Defensive Perception

Before taking proactive action, check:

```
□ Is there enough context?
□ Is the action reversible?
□ Will it possibly interrupt the user?
□ Is user in "focus mode"?
□ Is the action outside user's defined scope?
```

## Anti-Patterns

### Over-Proaction

```
Problem: Frequent interruptions to user
Cause: Threshold set too low
Solution: Raise action threshold, increase cooldown period
```

### Blind Proaction

```
Problem: Ignoring context
Cause: Insufficient perception
Solution: Increase perception depth and breadth
```

### Stubborn Proaction

```
Problem: Continuing same strategy after failure
Cause: Lack of feedback learning
Solution: Update confidence after each action
```

### Secret Proaction

```
Problem: User doesn't know what agent is doing
Cause: Lack of transparency
Solution: Record and notify all proactive actions
```

## Best Practices

1. **Transparency First**: Proactively inform users what the agent is doing
2. **Reversibility Priority**: Prefer reversible actions
3. **Progressive Enhancement**: Start conservative, gradually increase proaction
4. **Continuous Calibration**: Adjust thresholds based on feedback
5. **Context Awareness**: Use different strategies for different scenarios
