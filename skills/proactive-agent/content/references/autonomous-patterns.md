# Anti-Patterns and Defense Strategies for Autonomous Actions

## Common Anti-Patterns

### 1. Blind Execution

**Symptoms**:
- Executes without checking preconditions
- Doesn't verify execution results
- Ignores context

**Causes**:
- Over-reliance on instructions
- Lack of perception capability
- No verification mechanism

**Defense Strategy**:
```python
async def safe_execute(action):
    # Precondition check
    if not await check_preconditions(action):
        return Result(status="skipped", reason="preconditions_failed")

    # Execute
    result = await execute(action)

    # Verify
    if not await verify_result(result, action):
        await rollback(action)
        return Result(status="failed", reason="verification_failed")

    return Result(status="success", result=result)
```

### 2. Spiral Effect

**Symptoms**:
- One action triggers another
- Infinite loop, cannot stop
- Forgets original goal

**Causes**:
- Lacks termination conditions
- Each action generates new requirements
- No global view

**Defense Strategy**:
```markdown
## Action Boundaries

### Allowed Scope
- [explicitly listed action types]

### Forbidden Scope
- [explicitly forbidden action types]

### Max Depth
- Single action chain: Max 3 actions
- Force stop and report to user if exceeded
```

### 3. Groupthink

**Symptoms**:
- Always agrees with user suggestions
- Doesn't voice objections
- Avoids conflict

**Causes**:
- Over-pleasing users
- Lacks independent judgment
- Afraid to correct users

**Defense Strategy**:
```
When user requests risky operation:
1. Identify potential risks
2. Clearly express concerns
3. Provide alternatives
4. Ultimately respect user decision
5. Log decision for future reference
```

### 4. Analysis Paralysis

**Symptoms**:
- Always analyzing, never acting
- Over-optimizing
- Missing timing

**Causes**:
- Perfectionism
- Fear of mistakes
- Threshold set too high

**Defense Strategy**:
```markdown
## Action Time Limits

- Small actions (< 5 min): Execute immediately
- Medium actions (5-30 min): Execute after 2 min analysis
- Large actions (> 30 min): Execute after user confirmation

## Minimum Completion Standards
- Execute when reaching 80% quality
- Continuously iterate and improve
```

### 5. Memory Loss

**Symptoms**:
- Repeats same mistakes
- Forgets user preferences
- Doesn't leverage historical experience

**Causes**:
- Doesn't log decisions
- Doesn't update memory
- Doesn't review history

**Defense Strategy**:
```markdown
## Must-Record Moments

1. After each decision
2. After receiving user feedback
3. After discovering patterns
4. After encountering new situations
5. At session end

## Memory Review
- Daily: Quick review
- Weekly: Deep analysis
- Monthly: Cleanup and optimization
```

### 6. Over-Commitment

**Symptoms**:
- Handles too many tasks simultaneously
- Promises actions it cannot complete
- Quality and speed decline

**Causes**:
- Doesn't know capability boundaries
- Difficulty refusing users
- Lacks task management

**Defense Strategy**:
```markdown
## Capacity Management

### Max Parallel Tasks
- Simple tasks: 5
- Medium tasks: 3
- Complex tasks: 1

### Refusal Strategy
When exceeding capacity:
1. Honestly state current load
2. Suggest priorities
3. Provide alternatives
4. Never promise what cannot be delivered
```

### 7. Blind Optimism

**Symptoms**:
- Underestimates task difficulty
- Ignores potential risks
- Promises unrealistic timelines

**Causes**:
- Lack of experience
- Doesn't want to disappoint users
- Cognitive bias

**Defense Strategy**:
```python
def realistic_estimate(task):
    # Initial estimate
    base_estimate = estimate(task)

    # Add buffer
    buffer = base_estimate * uncertainty_factor(task)

    # Add risk premium
    if has_dependencies(task):
        buffer *= 1.5

    # Final estimate
    return base_estimate + buffer

def estimate_confidence(task):
    # Adjust based on historical accuracy
    historical_accuracy = get_accuracy_history()

    # Consider task complexity
    complexity_factor = assess_complexity(task)

    return historical_accuracy * complexity_factor
```

## Comprehensive Defense Framework

### Three-Layer Defense

```
┌─────────────────────────────────────┐
│  Layer 1: Prevention                │
│  - Set action boundaries            │
│  - Enforce precondition checks      │
│  - Capacity limits                  │
├─────────────────────────────────────┤
│  Layer 2: Detection                  │
│  - Monitor abnormal patterns        │
│  - Verify execution results         │
│  - Check action chains              │
├─────────────────────────────────────┤
│  Layer 3: Recovery                  │
│  - Fast rollback mechanism          │
│  - Error notification               │
│  - Learning updates                 │
└─────────────────────────────────────┘
```

### Self-Check Mechanism

```markdown
## Pre-Action Self-Check

- [ ] Is this action reversible?
- [ ] Is it within my permissions?
- [ ] Is there enough context?
- [ ] Will it trigger a spiral effect?
- [ ] Will it repeat previous mistakes?
- [ ] Do I have enough time and resources?

## Post-Action Self-Check

- [ ] Did the result match expectations?
- [ ] Does user need to be notified?
- [ ] Does experience need recording?
- [ ] Do thresholds need updating?
```

## Anti-Pattern Self-Check List

Monthly check:

```
□ Are there excessive complaints about "forgetting user preferences"?
□ Are there frequent "missing best timing" reports?
□ Are there excessive "action failures" in logs?
□ Do users feel the agent is "too annoying" or "too passive"?
□ Are there excessively long "analysis times"?
□ Are there tasks that "cannot be completed" or "severely overtime"?

If any problems persist, strategy adjustment is needed.
```
