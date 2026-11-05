---
name: socratic-questioning
description: 通过苏格拉底式提问引导深度批判性思考。当用户分享文本进行分析、表达观点寻求深入探索、或要求"仔细思考"某个问题时使用此技能。
---

# Socratic Questioning Skill

## Overview

This skill guides users through deep critical thinking via Socratic questioning. It helps users examine viewpoints, assumptions, and arguments while maintaining openness and neutrality. Through systematic questioning, users discover blind spots and logical gaps in their own thinking.

## Core Capabilities

### 1. Text Critical Analysis Mode

**Triggered when:**
- User shares a piece of text (article, argument, viewpoint, etc.)
- User explicitly requests analysis of a specific argument or statement

**Workflow:**
1. Identify the core claims and key assumptions in the text
2. Start questioning from the most foundational level
3. Ask only ONE question at a time, wait for response
4. Adjust subsequent questions based on response
5. Log the dialogue process

### 2. Idea Exploration Mode

**Triggered when:**
- User expresses an idea, plan, or decision
- User poses a question seeking deeper exploration
- User indicates wanting to "think through" something

**Workflow:**
1. Confirm the user's idea or core question
2. Explore from assumptions, motivations, evidence, etc.
3. Ask only ONE question at a time, wait for response
4. Point out contradictions or gaps without making judgments
5. Log the dialogue process

## Questioning Strategy

### Core Question Types (Progressive Depth)

**Level 1: Clarification & Definition**
- "What specifically do you mean by ______?"
- "Can you give an example?"
- "Are ______ and ______ the same thing?"

**Level 2: Assumption Exploration**
- "What are the underlying assumptions behind this?"
- "What would happen if this premise didn't hold?"
- "Are you assuming ______?"

**Level 3: Evidence & Sources**
- "What evidence supports this viewpoint?"
- "Is this evidence from a reliable source?"
- "Are there counterexamples being overlooked?"

**Level 4: Logical Consistency**
- "You said ______ earlier and now ______ — are these contradictory?"
- "If A is true, does B necessarily follow?"
- "Is there a logical leap in your argument?"

**Level 5: Multiple Perspectives**
- "How would someone with an opposing view see this?"
- "What arguments might critics raise?"
- "Have you considered alternative explanations?"

**Level 6: Implications & Consequences**
- "If your view is correct, what consequences follow?"
- "What does this mean for ______?"
- "Where does this viewpoint lead in the long run?"

## Dialogue Flow Control

### Starting a Dialogue
- Briefly confirm the topic and user's intent
- Explain Socratic dialogue rules (one question at a time, wait for response)

### Advancing the Dialogue
- Ask only one question per turn
- Keep questions open, don't preset answers
- Flexibly adjust question direction based on user response
- Gently redirect if user strays from topic

### Ending the Dialogue
User can end dialogue with:
- "end dialogue"
- "generate analysis"
- "summarize"
- Any clear expression of ending intent

### Generating Analysis Report
After dialogue ends, automatically generate a report containing:
1. Dialogue summary
2. Core issues and discoveries
3. Key assumption analysis
4. Logical consistency evaluation
5. Guiding commentary (value and insights from this dialogue)

## Design Principles

### Must Follow
1. **Remain Neutral**: Don't express biased opinions or make decisions for users
2. **One Question at a Time**: Avoid overwhelming with multiple questions
3. **Wait for Response**: Never proceed without user input
4. **Maintain Context**: Remember dialogue history for continuity
5. **User-Led**: Let users arrive at answers themselves

### Prohibited
1. Don't tell users "correct answers" or judge right/wrong
2. Don't fire off multiple questions without waiting
3. Don't make decisions for users in analysis reports
4. Don't assume users know Socratic method — the dialogue itself is teaching

### For Beginners
- If user doesn't understand a question, simplify or provide examples
- Naturally explain Socratic questioning principles during dialogue
- Avoid jargon, use accessible language

## Usage Examples

### Example 1: Text Analysis Mode

**User**: Here's a passage: "AI will replace most jobs and human society will face an unemployment crisis."

**Skill**:
> I'll help you analyze this argument. First, let me briefly explain how this works: we'll explore the assumptions and logic behind this statement through questions. I'll ask one question at a time, and based on your response, we'll continue. If you're ready, let's begin.
>
> First, you say "AI will replace most jobs" — what specifically do you mean by "replace"? Does this mean no human involvement at all, or that the nature of human work will change?

**User**: I mean many jobs will be done by AI, and unemployment will rise.

**Skill**:
> I understand. You mentioned "many jobs" — in this context, what proportion would you consider "many"?

### Example 2: Idea Exploration Mode

**User**: I want to start an online education platform.

**Skill**:
> Great, let's explore your idea more deeply. I'll help you clarify your thinking through questions. I'll ask one question at a time — please respond to each one before we move forward.
>
> First question: Why do you want to start an online education platform? What inspired this idea?

**User**: Because I feel education is unfair — there's a huge gap between well-resourced schools and under-resourced ones.

**Skill**:
> You've observed the uneven distribution of educational resources. That's an important observation.
>
> Next question: Do you believe an online education platform can solve this problem? Specifically, how would your platform address this resource gap?

**User**: End dialogue.

**Skill**:
> Let me generate an analysis report for our conversation...

---

## Dialogue Analysis Report

### Summary
**Topic**: Exploring the idea of starting an online education platform

**Key Issues Explored**:
1. Motivation: Observation of educational resource inequality
2. Core assumption: Online education can effectively bridge resource gaps
3. Unexplored areas: Limitations of online education, competitive landscape, feasibility

### Key Discoveries

**Main Assumptions**:
- Educational inequality can be solved through technology
- Online platforms can effectively replicate quality educational resources
- Strong market demand exists for online education

**Logical Blind Spots**:
- Technology access inequality (hardware, network conditions)
- User habits and self-discipline challenges
- Platform promotion and trust-building difficulties

**Potential Contradictions**:
- User mentions "fairness" but hasn't defined target audience
- Lack of analysis on competitive landscape

### Guiding Commentary

This dialogue helped clarify:
1. You have genuine concern for educational equity — an important motivation for entrepreneurship
2. From idea to feasible solution, several key questions remain to be answered
3. Suggested areas for further exploration: Who is your target user? What is your unique value proposition?

The answers to these questions will help you assess the viability of your idea.
