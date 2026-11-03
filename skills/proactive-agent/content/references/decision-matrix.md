# Decision Matrix and Action Threshold Configuration

## Decision Framework

### Two-Dimensional Decision Matrix

| | **Low Risk** | **High Risk** |
|---|---|---|
| **High Value** | A: Execute immediately | B: Analyze deeply then propose |
| **Low Value** | C: Batch or ignore | D: Don't execute |

### Value Assessment

```
Value Score = Time Saved × Quality Improvement × Frequency × Urgency

- Time Saved: 1-5 points (how much time saved)
- Quality Improvement: 1-5 points (how much quality improved)
- Frequency: 1-5 points (how often it occurs)
- Urgency: 1-5 points (how urgent)
```

### Risk Assessment

```
Risk Score = Impact × Reversibility × Complexity

- Impact: 1-5 points (how large the impact)
- Reversibility: 1-5 points (how easy to recover) [5=fully reversible]
- Complexity: 1-5 points (how complex) [5=very simple]
```

### Comprehensive Assessment

```
Action Score = (Value Score / 25) × 0.6 + (Feasibility / 25) × 0.4

Decision Thresholds:
- >= 0.8: Execute autonomously
- >= 0.6: Execute after proposing
- >= 0.4: Record but don't act proactively
- < 0.4: Ignore
```

## Action Threshold Configuration

### User-Configurable Thresholds

```yaml
proactive_settings:
  # Action thresholds (0.0 - 1.0)
  auto_execute_threshold: 0.8
  suggest_threshold: 0.5

  # Cooldown period (seconds)
  action_cooldown: 300

  # Max consecutive proactive actions
  max_consecutive_actions: 3

  # Proactive mode scope
  scope:
    - code_quality
    - documentation
    - testing
    - # Auto-execute low-risk tasks

  exclude:
    - production_deployments  # Require confirmation for critical ops
    - data_deletion
    - security_changes
```

### Scenario-Based Thresholds

| Scenario | Auto Threshold | Suggest Threshold | Cooldown |
|----------|---------------|-------------------|----------|
| Normal Work | 0.8 | 0.5 | 300s |
| Debug Mode | 0.9 | 0.7 | 60s |
| Demo Mode | 0.6 | 0.4 | 600s |
| Conservative Mode | 0.95 | 0.8 | 900s |

## Decision Checklist

### Pre-Execution Check

```
□ Is the action within allowed scope?
□ Is the action reversible?
□ Is user in a state that allows interruption?
□ Is confidence high enough?
□ Does it conflict with previous actions?
□ Is there enough context?
```

### Post-Execution Check

```
□ Did the action succeed?
□ Did the result match expectations?
□ Does user need to be notified?
□ Does memory need updating?
□ Do thresholds need adjustment?
```

## Decision Log Format

```markdown
## [Timestamp] Decision Log

### Situation
- Trigger: [what triggered this decision]
- Context: [relevant context]

### Analysis
- Value Assessment: [score and rationale]
- Risk Assessment: [score and rationale]
- Alternatives: [other possible actions]

### Decision
- Choice: [final choice]
- Action Type: [notify/suggest/execute]
- Confidence: [0-100%]

### Result
- Execution Status: [success/failed/partially successful]
- User Feedback: [if any]
- Lessons Learned: [if any]
```

## Threshold Tuning Guide

### How to Determine Initial Thresholds

1. **Conservative Start**: Begin at 0.8/0.5
2. **Observe for Two Weeks**: Log all actions and results
3. **Analyze Patterns**: Identify false positives and missed opportunities
4. **Adjust Gradually**: Change by 0.05 each time
5. **Scenario Configure**: Use different thresholds for different scenarios

### Signals Threshold is Too High

```
- Rare proactive actions
- User complains "you're too passive"
- Many obvious opportunities missed
→ Lower threshold by 0.1
```

### Signals Threshold is Too Low

```
- Frequent interruptions to user
- Many actions rejected by user
- User complains "you're too annoying"
→ Raise threshold by 0.1
```

## Best Practices

1. **Be Conservative First**: Mistaken proaction is more annoying than mistaken passivity
2. **Prioritize Reversibility**: High reversibility allows lower thresholds
3. **Weight by Frequency**: Be more conservative on high-frequency actions
4. **User Feedback**: Dynamically adjust based actual feedback
5. **Log Decisions**: Enable future analysis and improvement
