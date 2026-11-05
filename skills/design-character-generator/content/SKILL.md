---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5b7731cf4acc6b59e36e8944f8c3827e
    PropagateID: 5b7731cf4acc6b59e36e8944f8c3827e
    ReservedCode1: 304602210096d6347d30ee44e028eba4788546dd2c18b15dcb7e8b0e5b4f7007e1992fd72a022100fb877db2897c48824a923004f71ccf52f79ecba5217c0f204e6ff61ed0226796
    ReservedCode2: 304402200a2949ce5a5dc5e5dcb874072397ce9ae11936f0e99d749b3b431533214fc57c02204452c15398c3c0466dda1a50735b1af7f74415ab0049dc290451e22a824dbcf2
description: 生成设计角色人物（用户画像、人物模型）用于用户体验设计、市场研究和创意项目。当用户要求创建角色、人物画像、用户画像 persona、设计人物时使用。
name: design-character-generator
---

# Design Character Generator

Generate comprehensive design character personas for UX design, market research, and creative projects.

## Input Requirements

Collect the following information before generating:

1. **Project Context**: What product/service is this character for?
2. **Target Domain**: Industry or field (e.g., fintech, healthcare, e-commerce)
3. **Character Purpose**: User research, persona documentation, creative writing
4. **Age Range**: Target demographic age
5. **Key Traits**: Specific personality traits or behaviors to emphasize

## Character Profile Structure

Generate characters with these sections:

### 1. Basic Information

```
- Name (culturally appropriate)
- Age, Gender, Location
- Occupation
- Education Level
- Income Range (if applicable)
- Family Status
```

### 2. Demographics & Background

```
- Cultural Background
- Life Stage
- Tech Proficiency Level
- Urban/Rural Setting
```

### 3. Psychographic Profile

```
- Core Values
- Personality Traits (Big Five: O/C/E/A/N)
- Interests & Hobbies
- Media Consumption Habits
- Communication Style
```

### 4. Goals & Motivations

```
- Primary Goals (what they want to achieve)
- Secondary Goals (nice-to-have)
- Deepest Motivation
- Values Driving Decisions
```

### 5. Pain Points & Frustrations

```
- Current Problems
- Barriers to Goals
- Workarounds Currently Used
- Emotional Triggers
```

### 6. Behaviors & Patterns

```
- Daily Routines Related to Domain
- Decision-Making Process
- Information Gathering Habits
- Channel Preferences (digital/physical)
- Purchase/Action Triggers
```

### 7. Tech & Digital Profile

```
- Device Usage
- Platform Preferences
- App Usage Patterns
- Privacy Concerns Level
```

### 8. Quote & Voice

```
- Characteristic Quote (in their voice)
- Speech Patterns
- Common Expressions
```

## Output Format

Present the character in a structured, visual-friendly format:

```markdown
# [Character Name]

## Quick Stats
| Attribute | Value |
|-----------|-------|
| Age | XX |
| Location | City, Country |
| Occupation | Job Title |
| Tech Savvy | [Low/Medium/High] |

## Story Summary
[2-3 sentences describing their life and context]

## Goals & Frustrations
[Detailed goals and pain points]

## Behavioral Patterns
[Key behaviors and decision patterns]

## Quote
> "[Characteristic quote in their voice]"
```

## Examples

### Example 1: E-commerce User Persona

**Input**: Young professional, frequent online shopper, values convenience

**Output**:
```
Name: Sarah Chen
Age: 28
Occupation: Marketing Manager
Location: Shanghai

Goals:
- Save time on routine purchases
- Find quality products within budget
- Stay updated on latest trends

Pain Points:
- Long delivery times
- Difficulty finding honest reviews
- Decision fatigue from too many options

Behaviors:
- Shops primarily via mobile
- Compares prices across 2-3 platforms
- Influenced by social media recommendations
- Makes impulse purchases when distracted

Quote: "If I can't find what I need in 5 minutes, I'll just go somewhere else."
```

### Example 2: Healthcare App User

**Input**: Senior citizen, moderate tech literacy, managing chronic condition

**Output**:
```
Name: Wei Zhang
Age: 67
Occupation: Retired Teacher
Location: Beijing

Goals:
- Manage diabetes effectively
- Communicate easily with family about health
- Maintain independence

Pain Points:
- Small text hard to read
- Complex navigation confusing
- Concerned about data privacy
- Prefers human interaction

Behaviors:
- Uses tablet primarily
- Gets help from adult children
- Checks app 2-3 times daily
- Takes screenshots to remember steps

Quote: "I want to stay healthy for my grandchildren, but these phones are so complicated."
```

## Best Practices

1. **Avoid Stereotypes**: Base characters on research, not assumptions
2. **Include Contradictions**: Real people are inconsistent
3. **Add Specific Details**: Concrete details make characters memorable
4. **Consider Context**: Same person behaves differently in different situations
5. **Use Direct Quotes**: Authentic voice brings characters to life
6. **Balance Ideal & Actual**: Include both aspirational and actual behaviors

## Validation Checklist

- [ ] Character has clear, achievable goals
- [ ] Pain points are specific and relatable
- [ ] Behaviors are consistent with background
- [ ] Quote reflects actual speech patterns
- [ ] Profile is actionable for design decisions

## Related Patterns

For comprehensive user research, combine with:
- User Journey Mapping
- Empathy Mapping
- Jobs-to-be-Done Framework
- Competitive Analysis
