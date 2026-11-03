---
name: workplace-persona-builder
description: Build user personas for workplace reporting and generate personalized content for different stakeholders. Use when users need to create stakeholder profiles, manage client/leader relationships, automate meeting minutes archiving, or generate customized reports for different audiences.
---

# Workplace Persona Builder

Build user personas for workplace reporting and generate personalized content for different stakeholders.

## Overview

This skill implements a three-folder system to manage stakeholder relationships and automate personalized reporting:

```
├── personas/          # Long-term objective profiles
│   ├── {person_id}/
│   │   ├── profile.md       # Core persona data
│   │   └── interactions.md  # Interaction history
├── projects/         # Project-specific context
│   └── {project_id}/
│       ├── context.md       # Project background
│       └── stakeholders.md  # Involved personas
└── events/           # Raw evidence materials
    ├── meetings/
    ├── chats/
    └── emails/
```

## Core Concepts

### Three-Folder Structure

1. **Personas Folder**: Objective, long-term profiles
   - Role and responsibilities
   - Decision criteria and "red lines" (雷点)
   - Communication style and preferences
   - Stake in projects

2. **Projects Folder**: Project-specific context
   - Current project status
   - Stakeholder positions and feedback
   - Pending issues and action items
   - Project-specific notes

3. **Events Folder**: Raw evidence materials
   - Meeting transcripts (original, unprocessed)
   - Chat screenshots
   - Email threads

### Key Principle: Separate Facts from Opinions

When building personas, distinguish between:
- **Objective facts**: Role, responsibilities, stated positions
- **Subjective interpretations**: "He always gives me a hard time"

Your prompts should help convert subjective impressions into objective立场 analysis.

## Workflow

### Phase 1: Initial Persona Creation

1. **Verbal intake** (口述建档)
   - Describe the person's relationship to you
   - Describe their role and responsibilities
   - Describe interaction patterns and communication style
   - Note any code names for confidentiality

2. **立场 extraction**
   - Convert subjective impressions into objective stakeholder positions
   - Identify their role in decision-making (approver, influencer, etc.)
   - Identify their priorities (risk, budget, timeline, quality, etc.)

3. **Document the persona**
   ```
   # Persona: {Code Name}

   ## Basic Info
   - Role: [Title]
   - Responsibilities: [Key responsibilities]
   - Relationship: [How they relate to you]

   ## Decision Criteria
   - Key priorities: [What they care about most]
   - Red lines: [What to avoid]
   - Success metrics: [How they measure success]

   ## Communication Style
   - Preferred format: [Email, meeting, chat, etc.]
   - Level of detail: [High-level vs. detailed]
   - Tone: [Formal, casual, etc.]

   ## Stake in Current Projects
   - [Project A]: [Their role and position]
   - [Project B]: [Their role and position]
   ```

### Phase 2: Material Collection

Collect materials from three sources:

1. **Meeting transcripts**
   - Always save original transcription, not AI-summarized versions
   - Include everyone's statements, not just summary
   - Raw transcripts allow reuse for different stakeholders

2. **Chat records**
   - Screenshots of feedback on deliverables
   - Comments after presentations
   - Informal discussions

3. **Email threads**
   - Full email chains for context
   - Each person's contributions in the thread
   - Track changes and decisions over time

### Phase 3: Automatic Archiving

When new materials arrive:

1. Extract project-related content → Project folder
2. Extract persona-related content → Persona folder
3. Store raw evidence → Events folder

The skill should automatically:
- Update persona profiles with new information
- Update project contexts with new developments
- Maintain an interaction history log

### Phase 4: Report Generation

When generating reports:

1. **Read persona first** - Understand their priorities and style
2. **Read project context** - Understand current status
3. **Read relevant history** - Access past interactions
4. **Generate standard draft** - Create baseline content
5. **Adapt for audience** - Customize based on persona preferences

## Report Formatting by Audience Type

| Audience Type | Format | Content Focus |
|---------------|--------|--------------|
| Executives | ATM (Agenda-Timeline-Milestone) | Big picture, milestones, risks |
| Direct Managers | Detailed with context | Specifics, actions, timelines |
| Clients | Email/Business format | Value, benefits, next steps |
| Peers | Concise with context | Collaboration points |

## Example Prompt Templates

### Initial Persona Creation
```
I need to create a persona for [relationship/role]. Here's what I know:
- They are [title] responsible for [responsibilities]
- My relationship is [how you interact]
- Communication style: [observed patterns]
- In meetings they tend to: [observed behavior]
- They recently said: [notable quote or feedback]

Help me extract their objective立场 and decision criteria from this information.
```

### Meeting Archiving
```
Archive this meeting transcript:
- Date: [date]
- Attendees: [list]
- Project context: [project name]

Extract and categorize:
1. Key decisions made
2. Action items assigned
3. Persona-specific observations (who said what about what)
4. Project-specific updates
```

### Report Generation
```
Generate a report about [project update/situation] for [persona name].

First, confirm their current position on this project based on their profile:
- What are their stated priorities?
- What concerns have they raised?
- What level of detail do they prefer?

Then generate a [format] report that:
- Addresses their specific concerns
- Uses their preferred communication style
- Highlights information relevant to their role
```

### Reflection Prompt
```
After generating this report, review:
1. Does it address [persona's] known priorities?
2. Does it avoid their known red lines?
3. Is the detail level appropriate for their role?
4. What additional context might they need?
```

## Best Practices

1. **Always use original transcripts** - Never use AI-summarized versions; they lose nuance
2. **Record everything** - If possible, record meetings for complete transcripts
3. **Update continuously** - Add new information after every interaction
4. **Maintain confidentiality** - Use code names if needed for sensitive contexts
5. **Separate opinions from facts** - Let the AI help convert impressions to objective分析
6. **Think in systems** - This works best as a company-wide SOP for sales and client management

## Use Cases

- **向上管理**: Customize updates for different management levels
- **客户关系管理**: Build comprehensive client profiles
- **销售流程**: Create SOP for customer touchpoints and follow-ups
- **会议效率**: Auto-archive meeting content to relevant stakeholders
- **跨部门协作**: Maintain context across multiple projects and stakeholders