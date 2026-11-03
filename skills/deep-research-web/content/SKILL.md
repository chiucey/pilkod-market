---
name: deep-research-web
description: "Conduct iterative deep research on any topic using Claude's built-in web search. Triggers when the user asks to 'deep research', 'research in depth', 'help me investigate', 'do a deep dive', 'comprehensive analysis', 'research report', 'find out everything about', or any request requiring multi-angle, multi-round searching to thoroughly understand a topic. Also triggers for complex factual queries where a single search would be insufficient, or when the user says things like 'look into X for me', 'what's the full picture on X', or 'I want to understand X deeply'. Even if the user only says 'look up X' but the topic is complex or multi-faceted, consider using this skill."
---

# Deep Research (Claude Built-in Search)

## Overview

This skill implements an iterative deep research system using **only Claude's built-in `web_search` tool**. It works like a real researcher: search → read → think → discover new questions → search again.

Core principles:
- **ReAct loop** (Reason → Act → Observe) drives every search decision
- **Map-Reduce architecture**: decompose the topic into sub-questions, explore each, then synthesize
- **Evidence grading**: classify findings as Direct, Supporting, Conflicting, or Contextual
- **Counterfactual fragility analysis**: stress-test conclusions before presenting them

---

## Phase 1: Plan — Decompose the Topic

Before searching, analyze the user's topic:

### 1. Classify the request type
- **Descriptive**: current state of affairs
- **Predictive**: trends and forecasts
- **Comparative**: A vs B analysis
- **Exploratory**: open-ended investigation

### 2. Break into 3–6 orthogonal sub-questions

Choose dimensions relevant to the topic:

| Dimension | When to use | Example |
|-----------|-------------|---------|
| Core facts | All topics | "What is X? How does it work?" |
| Current status | Dynamic topics | "Latest developments as of now?" |
| Key players | Competitive/ecosystem | "Who are the major actors and their strategies?" |
| Quantitative data | Measurable topics | "Market size, growth rate, key metrics?" |
| Controversy & risk | Contested topics | "Main criticisms and failure modes?" |
| Outlook | Forward-looking | "What happens in 1–2 years?" |

Not every topic needs all dimensions — choose what's relevant.

---

## Phase 2: Iterative Search — ReAct Loop

For each sub-question, run this loop:

```
LOOP:
  Thought:      What do I need to know right now, and why?
  Action:       Construct a query → call web_search
  Observation:  Analyze results → extract key findings

  Decide:
    - New lead or term discovered?       → new query, continue loop
    - Conflicting results?               → search for clarifying source
    - Sub-question answered?             → record findings, move to next
    - Poor search quality?               → reframe query and retry
END LOOP
```

### Query Construction Rules

**Good queries** (specific, bounded):
- `"AI agent enterprise adoption rate 2025"`
- `"OpenAI o3 vs Claude performance benchmark"`
- `"lithium battery supply chain risks 2025"`

**Bad queries** (too vague):
- `"AI"` — too broad, noisy results
- `"tell me everything about batteries"` — conversational, not a search query

### Search Volume Guidelines

| Complexity | Total searches | Criteria |
|------------|----------------|----------|
| Simple | 3–5 | Single topic, factual question |
| Moderate | 5–8 | Multi-dimensional, needs comparison |
| Complex | 8–12 | Cross-domain, contested, requires deep reasoning |
| Hard cap | 15 | Avoid over-consuming resources |

If the user says "quick overview" → compress to 3–5 searches.
If the user says "deep dive" or "comprehensive" → go up to 10–12.

### Search Strategy: Coarse to Fine

```
Round 1 — Wide net: establish the full picture
  e.g., "quantum computing 2025 overview"

Round 2 — Targeted drill-down: chase key leads from Round 1
  e.g., "IBM quantum vs Google quantum roadmap 2025"

Round 3 — Cross-validation: verify disputed facts or key data
  e.g., "quantum computing commercial viability timeline expert forecast"
```

### Actively Search for Counter-Evidence

Don't only find information that confirms initial findings. For contested topics, explicitly search for:
- Criticisms and failure cases
- Minority expert opinions
- Data that contradicts the dominant narrative

### ReAct Triplet Record

For each search, maintain a record of:
- **θ (thought)**: Why am I searching this? What am I expecting to find?
- **α (action)**: The exact query used
- **o (observation)**: Key findings extracted from results

Share this reasoning chain with the user to make the process transparent.

---

## Phase 3: Synthesis — Reduce to Report

### 1. Evidence Grading

Tag every key claim with one of:

| Tag | Meaning | Example |
|-----|---------|---------|
| **[Direct]** | Directly answers the core question | "Market grew 34% YoY per IDC" |
| **[Supporting]** | Indirectly reinforces the conclusion | "Three major vendors announced expansions" |
| **[Conflicting]** | Contradicts the main finding | "Analyst X projects a 10% decline" |
| **[Contextual]** | Background framing, not direct evidence | "This sector has a 5-year CAGR of 18%" |

### 2. Cross-Validation

- Multiple sources agree → mark as **high confidence**
- Sources conflict → explicitly note the conflict and explore why
- Single source only → mark as **unverified, needs confirmation**
- Always distinguish **facts** (data-backed) from **opinions** (analyst/expert views)
- Always note the approximate date of key information

### 3. Counterfactual Fragility Analysis

This is what separates a research report from a simple information dump. For each core conclusion, ask:

- **Under what conditions would this conclusion be wrong?**
- **Fragility rating**:
  - **Low** — Would take a black-swan event to invalidate
  - **Medium** — A plausible alternative scenario exists
  - **High** — Conclusion depends heavily on a single uncertain factor
- **Monitoring signals**: What indicators should be watched over time?

---

## Report Template

```markdown
# [Research Topic]

## Executive Summary
3–5 sentences covering the core findings and confidence level.

## Background
Core concepts, historical context, and framing.

## Core Findings

### [Sub-topic 1]
**Key conclusion**: ...

| Evidence | Why it matters | Tag |
|----------|----------------|-----|
| [Specific fact/data] | [Explanation] | [Direct/Supporting/...] |

### [Sub-topic 2]
(Same structure)

## Conflicts & Uncertainties
- Where sources disagree and why
- Open questions without clear answers
- Information gaps and blind spots

## Counterfactual Fragility
**Fragility of core conclusion**: Low / Medium / High
**Conditions that would invalidate it**: ...
**Signals to monitor**: ...

## Conclusion & Outlook
Synthesis and forward-looking judgment.

## Research Trail
Key queries used, notable sources, and a brief summary of the reasoning chain.
```

---

## Process Transparency

Keep the user informed throughout. After each search round, briefly show:

- 🔍 **Researching**: which sub-question is being explored
- 💭 **Thought**: why this query was chosen
- 📊 **Finding**: the key insight extracted
- ➡️ **Next step**: what will be searched next and why

This lets the user redirect or refocus the research mid-process.

---

## Quality Checkpoints

Before finalizing the report, self-check:

- [ ] Have I searched for counter-evidence, not just confirming evidence?
- [ ] Are conflicting sources explicitly noted?
- [ ] Are facts distinguished from opinions?
- [ ] Is time-sensitivity noted on key data points?
- [ ] Are all key claims graded by evidence type?
- [ ] Have I run the counterfactual check on core conclusions?
- [ ] Are information gaps honestly disclosed rather than papered over?

If any box is unchecked, do another search round or add appropriate caveats.

---

## Common Pitfalls to Avoid

- **Don't list search results** — extract, synthesize, and analyze
- **Don't only find confirming evidence** — actively seek counterpoints
- **Don't ignore conflicting data** — contradictions are often the most valuable findings
- **Don't overstate confidence** — use hedged language when data is thin
- **Don't invent information** — clearly label gaps as gaps
```