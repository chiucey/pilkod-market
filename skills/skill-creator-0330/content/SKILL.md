---
name: skill-creator-0330
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, you can either use as is or modify if you feel something needs to change about them). Then explain them to the user (or if they already existed, explain the ones that already exist)
  - Use the `eval-viewer/generate_review.py` script to show the user the results for them to look at, and also let them look at the quantitative metrics
- Rewrite the skill based on feedback from the user's evaluation of the results (and also if there are any glaring flaws that become apparent from the quantitative benchmarks)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages. So for instance, maybe they're like "I want to make a skill for X". You can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and repeat.

On the other hand, maybe they already have a draft of the skill. In this case you can go straight to the eval/iterate part of the loop.

Of course, you should always make sure the user has a clear mental model of where they are in the process and what the next steps are.

## Core Workflow

### 1. Initial Assessment
When a user wants to create or improve a skill, start by understanding:
- What is the target use case?
- Is this a new skill or improvement of an existing one?
- What does success look like?

### 2. Skill Development Stages

**Stage 1: Draft Creation**
- Write a comprehensive SKILL.md
- Include clear frontmatter (name, description with trigger phrases)
- Define the skill's capabilities and boundaries
- Add examples and edge case handling

**Stage 2: Testing**
- Create test prompts covering key scenarios
- Run the skill against these prompts
- Document both successes and failures

**Stage 3: Evaluation**
- Present results to the user for qualitative assessment
- Generate quantitative metrics if applicable
- Collect user feedback

**Stage 4: Iteration**
- Rewrite skill based on feedback
- Expand test coverage
- Repeat until satisfied

**Stage 5: Scale**
- Expand test set
- Run at larger scale
- Finalize for production

### 3. Output Format
When a skill is complete, output using the GenUI card format:

```xml
<genui-skill-card name="skill-name" desc="skill-description" skill-id="skill-id-from-meta"></genui-skill-card>
```

## Directory Constraints

All skills must be created in `/workspace/temp-skills/` directory with:
- SKILL.md as the main file
- _meta.json for skill metadata
- Optional supporting files (scripts, examples, tests)

## Path Validation

After creating or modifying any skill, use path-checker sub-agent to validate all paths and names are in English.
