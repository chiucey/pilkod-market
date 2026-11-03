---
name: decision-clarity
description: Improve decision quality by clarifying the real problem, exposing hidden assumptions, reasoning from fundamental facts, reducing unnecessary complexity, and ending with a cleaner recommendation or next step. Use when the user is confused, comparing options, overcomplicating a problem, questioning assumptions, trying to identify the real bottleneck, or asking things like "what am I missing?", "does this really have to be this way?", "what should I remove?", "what is the simplest explanation that still fits?", or "help me think this through".
---

# Decision Clarity

Use this skill to turn ambiguous, high-value, complexity-prone problems into clearer decisions.

This skill combines three reasoning modes in a practical sequence:
1. Socratic questioning to clarify the real issue
2. First-principles thinking to reduce the issue to facts and constraints
3. Occam-style simplification to remove unnecessary complexity

Do not use this skill to sound philosophical. Use it to improve judgment.

## Core objective

Produce answers that:
1. identify the real question
2. expose hidden assumptions
3. reduce the issue to facts, constraints, and causal structure
4. compare options by complexity and assumption load
5. remove false complexity
6. end with a clear recommendation, next step, or test

A strong answer should make the user feel:
- "the real problem is clearer now"
- "you found the assumption I was missing"
- "this is simpler than I thought"
- "I know what to do next"

## Operating stance

Default to clarity before confidence.

Ask:
- What is the user actually trying to decide or understand?
- Which parts of the problem are vague, inherited, or untested?
- What facts and hard constraints actually matter?
- Which explanation or plan requires fewer unnecessary assumptions?
- What is the simplest path that still respects reality?

## Best-fit use cases

This skill is especially useful for:
- startup and business decisions
- product and MVP decisions
- content and creator workflow design
- operations and process simplification
- strategy questions with multiple plausible options
- personal decisions where confusion, self-justification, or complexity are distorting judgment
- argument and reasoning audits

## Not a good fit for

Do not use this skill for:
- simple factual lookup
- purely mechanical execution tasks
- obvious low-stakes choices
- cases where the user explicitly wants only conventional guidance without reframing

## Workflow routing

Route to the smallest useful workflow.
- The problem is vague, overloaded, or poorly framed → `Workflows/Clarify.md`
- The issue needs to be broken into facts, constraints, and mechanics → `Workflows/Deconstruct.md`
- The issue has too many explanations, steps, features, or moving parts → `Workflows/Simplify.md`
- The user needs a recommendation, decision rule, priority order, or test → `Workflows/Decide.md`

For non-trivial problems, use the full sequence:
1. Clarify
2. Deconstruct
3. Simplify
4. Decide

For simpler problems, compress the sequence but preserve the logic.

## Mode selection

Choose the lightest response mode that still improves the decision.

### Mode A: Quick Reframe

Use for short questions such as:
- "What am I missing?"
- "Am I overcomplicating this?"
- "Does this really have to be this way?"
- "Which option actually makes more sense?"

Output:
- Real issue
- Hidden assumption
- Main constraint
- Simpler conclusion
- Next move

### Mode B: Structured Decision Analysis

Use for startup, product, content, operations, and strategic decisions.

Output:
- Real goal
- Assumptions
- Basic facts
- Hard constraints
- Soft constraints
- Simpler options
- Recommendation
- First test or next step

### Mode C: Reasoning Audit

Use when the user presents an argument, thesis, or decision path that may be weak, confused, or overbuilt.

Output:
- Real question
- Weak assumptions
- Missing evidence or contradiction
- Simpler interpretation or design
- Refined judgment

Do not force a long analysis when a shorter one is enough.

## Required reasoning rules

### 1. Clarify before solving

Do not solve the wrong problem well.

Restate the issue in outcome terms, not only in the user's current framing.

Examples:
- "Should I build an app?" may really mean "what is the best delivery mechanism for this user outcome?"
- "How do I make this more professional?" may really mean "how do I increase trust, clarity, conversion, or authority?"
- "Why is this so hard?" may really mean "which part is actually the bottleneck?"

If the question is framed at the wrong level, say so and correct it.

### 2. Surface assumptions explicitly

Look for assumptions in:
- the user's wording
- inherited workflows
- industry norms
- default best practices
- preferred tools or formats
- emotional preferences presented as logic

Useful prompts to surface assumptions:
- "What must be true for this to work?"
- "What are we assuming that we haven't verified?"
- "What would make this assumption false?"
- "What does the conventional approach assume that we haven't questioned?"

### 3. Reduce to facts and constraints

Separate:
- Facts: what is currently supported by evidence, observation, or logic
- Constraints: what cannot be changed or is very expensive to change
- Preferences: what the user prefers but is not locked in
- Assumptions: what we believe but haven't verified

Ask: "What happens if we challenge this assumption?"

### 4. Simplify without deleting reality

Remove:
- decorative complexity
- speculative additions
- duplicate layers
- workaround-driven structure
- optional steps with low payoff

Preserve:
- what creates the actual outcome
- what is required by hard constraints
- what handles real risks

The test: "Does this still work if we remove X?" If yes, X was likely complexity.

### 5. End with a next move

Always provide:
- a recommendation, or
- a decision rule, or
- a priority order, or
- a smallest useful experiment

Never leave the user in a better state of understanding but without a clear path forward.

## Reference files

- `references/anti-patterns.md` - Common failure modes and self-checks
- `references/business.md` - Startup, pricing, growth, strategy questions
- `references/content.md` - Content quality and creator workflow decisions
- `references/examples.md` - Full decision-clarity reasoning examples
- `references/operations.md` - Process simplification and workflow design
- `references/output-patterns.md` - Structured response formats
- `references/product.md` - MVP, feature decisions, product scope
- `references/trigger-questions.md` - Transforming vague prompts into sharper frames
