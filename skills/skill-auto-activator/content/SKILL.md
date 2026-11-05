---
name: skill-auto-activator
description: Automatically identify and activate relevant skills based on user input context. Use when you need to determine which skills to use, match user requests to available skills, or automatically route tasks to appropriate specialized capabilities.
---

# Skill Auto-Activator

Automatically identify and activate relevant skills based on user input context and task requirements.

## Core Functionality

### Skill Matching Logic

**Keyword Analysis:**
- Extract key terms from user input
- Match against skill descriptions
- Score relevance by match strength

**Context Assessment:**
- Identify task type (code, design, writing, etc.)
- Assess complexity level
- Determine required capabilities

**Skill Selection:**
- Select highest-scoring matches
- Consider skill combinations
- Avoid overloading context

## Matching Criteria

### High Priority Triggers
- Exact skill name mentions
- Direct domain keywords
- Clear intent signals

### Medium Priority Triggers
- Related terminology
- Implicit requirements
- Contextual hints

### Low Priority Triggers
- General topics
- Adjacent skills
- Supplementary capabilities

## Skill Categories

### Development
- code-generation, debugging, testing
- api-design, database, devops
- frontend, backend, mobile

### Content
- writing, editing, translation
- documentation, reports
- creative, marketing

### Analysis
- data-analysis, visualization
- research, summaries
- planning, strategy

### Communication
- internal-comms, emails
- presentations, proposals
- feedback, reviews

## Activation Process

```
1. Receive user input
2. Analyze context and intent
3. Match against skill metadata
4. Score and rank matches
5. Select appropriate skills
6. Load skill resources
7. Execute with skill context
```

## Conflict Resolution

When multiple skills might apply:
- Prioritize direct matches
- Consider user intent
- Avoid redundant activation
- Respect skill boundaries

## Best Practices

1. **Be Selective**: Don't over-activate skills
2. **Stay Relevant**: Match genuinely applicable skills
3. **Provide Transparency**: Explain why skills were activated
4. **Allow Override**: User can disable auto-activation
5. **Learn Patterns**: Track successful activations
