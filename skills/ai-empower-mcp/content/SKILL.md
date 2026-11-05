---
name: ai-empower-mcp
description: An intelligent co-pilot skill that observes AI agent workflows and provides real-time insights, quality checks, and optimization suggestions. Use when agents need to improve thinking quality, work efficiency, or delivery completeness.
---

# AI Empower MCP Skill

## Overview

An intelligent co-pilot skill that works as an "AI guardian" - observing AI agent workflows and providing continuous quality assurance, optimization insights, and enhancement suggestions throughout the entire task lifecycle.

**Core Value: Turn every AI output from "good enough" to "excellent"**

## Three Empowerment Modes

### 1. Think Empowerment (Thinking Enhancement)

**When to use**: When AI is analyzing, planning, or reasoning about a problem.

**What it does**:
- Analyzes logical coherence of thinking
- Detects blind spots and missing perspectives
- Suggests deeper analysis directions
- Identifies unsupported assumptions

**Example triggers**:
- "Let me analyze this problem..."
- "I think we should..."
- "The approach would be..."

### 2. Work Empowerment (Work Enhancement)

**When to use**: When AI is executing tasks, writing code, or building content.

**What it does**:
- Monitors work quality in real-time
- Detects potential issues and risks
- Suggests optimization opportunities
- Checks efficiency and completeness

**Example triggers**:
- "I'm working on the implementation..."
- "Currently coding the module..."
- "Building the component..."

### 3. Deliver Empowerment (Delivery Enhancement)

**When to use**: When AI is about to deliver results to users.

**What it does**:
- Verifies completeness against requirements
- Checks accuracy and quality standards
- Identifies missing elements
- Suggests final improvements

**Example triggers**:
- "Here's the result..."
- "The deliverable is ready..."
- "Task completed, summary:"

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mode | string | Yes | Empowerment mode: "think", "work", or "deliver" |
| thought_content | string | Cond* | Content for think mode |
| work_content | string | Cond* | Content for work mode |
| deliverable_content | string | Cond* | Content for deliver mode |
| requirements | string | No | Original requirements (for deliver mode) |
| task_description | string | No | Task context |
| context | object | No | Additional context info |
| current_step | int | No | Current step (for work mode) |
| total_steps | int | No | Total steps (for work mode) |

*Cond = Required based on mode

## Output Format

```json
{
  "success": true,
  "mode": "think|work|deliver",
  "summary": "Brief summary of analysis",
  "insights": [
    {
      "category": "Category name",
      "finding": "What was found",
      "severity": "critical|warning|info",
      "suggestion": "How to improve"
    }
  ],
  "improvements": ["List of improvement suggestions"],
  "warnings": ["List of warnings if any"]
}
```

## Capabilities Detail

### Thinking Analysis

| Check | Description |
|-------|-------------|
| Logical Coherence | Assesses if thinking flows logically |
| Blind Spot Detection | Finds missing perspectives |
| Evidence Check | Verifies claims have support |
| Assumption Tracking | Identifies underlying assumptions |

### Work Analysis

| Check | Description |
|-------|-------------|
| Quality Score | Rates work quality (0-100%) |
| Issue Detection | Finds potential problems |
| Completeness | Checks if all aspects covered |
| Efficiency Tips | Suggests optimization |

### Delivery Analysis

| Check | Description |
|-------|-------------|
| Completeness | Verifies all requirements met |
| Accuracy | Checks for errors |
| Quality Standards | Reviews format and style |
| Missing Items | Identifies gaps |

## Usage Examples

### Example 1: Enhance Thinking
```
Input:
{
  "mode": "think",
  "thought_content": "We should build a recommendation system to improve user engagement..."
}

Output:
{
  "success": true,
  "mode": "think",
  "summary": "Logic coherence: 85% | 2 warnings | 3 suggestions",
  "insights": [
    {
      "category": "Blind Spot Detection",
      "finding": "No consideration of alternative approaches",
      "severity": "warning",
      "suggestion": "Consider A/B testing or simpler alternatives first"
    }
  ],
  "improvements": ["Add supporting data or case studies", "Consider implementation complexity"]
}
```

### Example 2: Quality Work
```
Input:
{
  "mode": "work",
  "work_content": "Completed user authentication module with basic JWT validation...",
  "task_description": "Build authentication system",
  "current_step": 2,
  "total_steps": 5
}

Output:
{
  "success": true,
  "mode": "work",
  "summary": "Quality: Good (78%) | 1 issue | 2 optimizations",
  "insights": [
    {
      "category": "Issue Detection",
      "finding": "No error handling detected",
      "severity": "warning",
      "suggestion": "Add try-catch blocks and error responses"
    }
  ],
  "improvements": ["Add proper error handling", "Consider adding logging"]
}
```

### Example 3: Final Delivery Check
```
Input:
{
  "mode": "deliver",
  "deliverable_content": "Built user profile page with avatar, name, bio editing...",
  "requirements": "User profile with avatar, name, bio; editing capability; save changes"
}

Output:
{
  "success": true,
  "mode": "deliver",
  "summary": "Completeness: 75% | Accuracy: 95% | Ready with minor improvements",
  "insights": [
    {
      "category": "Completeness",
      "finding": "Save changes feature may need verification",
      "severity": "warning",
      "suggestion": "Add confirmation feedback after saving"
    }
  ],
  "improvements": ["Add save confirmation toast", "Consider adding auto-save option"]
}
```

## Integration Patterns

### Passive Monitoring
The skill can be called at key checkpoints without blocking the main workflow.

### Active Review
Call before major transitions (thinking → working → delivering).

### Final Audit
Always call before final delivery to ensure quality.

## Dependencies

- Python 3.8+
- No external dependencies required

## Notes

1. All analyses are deterministic - same input produces same output
2. Designed to enhance, not replace, AI judgment
3. Use insights as suggestions, not mandates
4. Multiple calls at different stages recommended for best results
