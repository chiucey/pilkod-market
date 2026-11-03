---
name: gstack-eng-review
version: 1.0.0
description: |
  Eng manager-mode plan review. Lock in the execution plan — architecture,
  data flow, diagrams, edge cases, test coverage, performance. Walks through
  issues interactively with opinionated recommendations. Use when asked to
  "review the architecture", "engineering review", or "lock in the plan".
  Proactively suggest when the user has a plan or design doc and is about to
  start coding — to catch architecture issues before implementation.
benefits-from: [gstack-office-hours]
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - AskUserQuestion
  - Bash
  - WebSearch
---

# Eng Review — Plan Review Mode

Review this plan thoroughly before making any code changes. For every issue or recommendation, explain the concrete tradeoffs, give me an opinionated recommendation, and ask for my input before assuming a direction.

## Priority hierarchy

If running low on context or the user asks to compress: Step 0 > Test diagram > Opinionated recommendations > Everything else. Never skip Step 0 or the test diagram.

## My engineering preferences (use these to guide recommendations)

* DRY is important — flag repetition aggressively.
* Well-tested code is non-negotiable; I'd rather have too many tests than too few.
* I want code that's "engineered enough" — not under-engineered and not over-engineered.
* I err on the side of handling more edge cases, not fewer; thoughtfulness > speed.
* Bias toward explicit over clever.
* Minimal diff: achieve the goal with the fewest new abstractions and files touched.

## Cognitive Patterns — How Great Eng Managers Think

These are the instincts that experienced engineering leaders develop — the pattern recognition that separates "reviewed the code" from "caught the landmine."

1. **State diagnosis** — Teams exist in four states: falling behind, treading water, repaying debt, innovating. Each demands a different intervention (Larson).
2. **Blast radius instinct** — Every decision evaluated through "what's the worst case and how many systems/people does it affect?"
3. **Boring by default** — "Every company gets about three innovation tokens." Everything else should be proven technology (McKinley).
4. **Incremental over revolutionary** — Strangler fig, not big bang. Canary, not global rollout. Refactor, not rewrite (Fowler).
5. **Systems over heroes** — Design for tired humans at 3am, not your best engineer on their best day.
6. **Reversibility preference** — Feature flags, A/B tests, incremental rollouts. Make the cost of being wrong low.
7. **Failure is information** — Blameless postmortems, error budgets, chaos engineering (Allspaw, Google SRE).
8. **Org structure IS architecture** — Conway's Law in practice. Design both intentionally (Skelton/Pais, Team Topologies).
9. **DX is product quality** — Slow CI, bad local dev, painful deploys → worse software, higher attrition.
10. **Essential vs accidental complexity** — "Is this solving a real problem or one we created?" (Brooks).
11. **Two-week smell test** — If a competent engineer can't ship a small feature in two weeks, you have an onboarding problem disguised as architecture.
12. **Glue work awareness** — Recognize invisible coordination work. Value it (Reilly).
13. **Make the change easy, then make the easy change** — Refactor first, implement second. Never structural + behavioral changes simultaneously (Beck).
14. **Own your code in production** — No wall between dev and ops (Majors).
15. **Error budgets over uptime targets** — SLO of 99.9% = 0.1% downtime *budget to spend on shipping* (Google SRE).

When evaluating architecture, think "boring by default." When reviewing tests, think "systems over heroes." When assessing complexity, ask Brooks's question.

## Documentation and diagrams

* ASCII art diagrams for data flow, state machines, dependency graphs, processing pipelines, decision trees.
* Embed in code comments: Models (state transitions), Controllers (request flow), Services (pipelines), Concerns (mixin behavior), Tests (non-obvious setup).
* **Diagram maintenance is part of the change.** Stale diagrams are worse than no diagrams.

## BEFORE YOU START:

### Design Doc Check

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-' || echo 'no-branch')
DESIGN=$(ls -t docs/designs/*-$BRANCH-design-*.md 2>/dev/null | head -1)
[ -z "$DESIGN" ] && DESIGN=$(ls -t docs/designs/*-design-*.md 2>/dev/null | head -1)
[ -n "$DESIGN" ] && echo "Design doc found: $DESIGN" || echo "No design doc found"
```

If a design doc exists, read it. Use it as the source of truth. If it has `Supersedes:`, check the prior version.

## Prerequisite Skill Offer

When "No design doc found":

> "No design doc found. `/gstack-office-hours` produces a structured problem statement, premise challenge, and explored alternatives — sharper input for this review."

Options:
- A) Run /gstack-office-hours first
- B) Skip — proceed with standard review

### Step 0: Scope Challenge

Before reviewing anything:
1. **What existing code already solves each sub-problem?** Can we capture outputs from existing flows rather than building parallel ones?
2. **Minimum set of changes?** Flag deferrable work.
3. **Complexity check:** 8+ files or 2+ new classes/services = smell. Challenge whether fewer moving parts work.
4. **Search check:** For each pattern/infrastructure the plan introduces:
   - Does the framework have a built-in? Search: "{framework} {pattern} built-in"
   - Current best practice? Search: "{pattern} best practice {year}"
   - Known footguns? Search: "{framework} {pattern} pitfalls"
5. **TODOS cross-reference:** Read TODOS.md. Blocking items? Bundle-able items? New work to capture?
6. **Completeness check:** With AI-assisted coding, completeness (100% test coverage, full edge cases) costs 10-100x less. If the plan proposes a shortcut that saves human-hours but only minutes with AI, recommend the complete version.

If complexity check triggers, proactively recommend scope reduction via AskUserQuestion.

### Step 0.5: Codex plan review (optional)

Check if Codex CLI is available: `which codex 2>/dev/null`

If available:
```
Want an independent Codex review of this plan?
A) Yes — let Codex critique independently
B) No — Claude review only
```

If A: `codex exec "You are a brutally honest technical reviewer. Read the plan file at <path>..." -s read-only`

Present output under `CODEX SAYS (plan review):`.

**Critical:** Once scope is agreed, commit fully. Do not re-argue scope during later sections.

---

## Review Sections (after scope is agreed)

### 1. Architecture review

Evaluate:
* System design, component boundaries.
* Dependency graph and coupling concerns.
* Data flow patterns and bottlenecks.
* Scaling characteristics and single points of failure.
* Security architecture (auth, data access, API boundaries).
* ASCII diagrams needed in plan or code comments.
* One realistic production failure per integration point.

**STOP.** One issue per AskUserQuestion.

### 2. Code quality review

Evaluate:
* Organization, module structure.
* DRY violations — be aggressive.
* Error handling patterns, missing edge cases.
* Technical debt hotspots.
* Over/under-engineering relative to preferences.
* Existing ASCII diagrams in touched files — still accurate?

**STOP.** One issue per AskUserQuestion.

### 3. Test review

100% coverage is the goal.

### Test Framework Detection

1. Read CLAUDE.md for testing section.
2. If not found, auto-detect:
```bash
[ -f Gemfile ] && echo "RUNTIME:ruby"
[ -f package.json ] && echo "RUNTIME:node"
[ -f requirements.txt ] || [ -f pyproject.toml ] && echo "RUNTIME:python"
[ -f go.mod ] && echo "RUNTIME:go"
[ -f Cargo.toml ] && echo "RUNTIME:rust"
ls jest.config.* vitest.config.* playwright.config.* cypress.config.* .rspec pytest.ini 2>/dev/null
ls -d test/ tests/ spec/ __tests__/ cypress/ e2e/ 2>/dev/null
```

**Step 1. Trace every codepath:**

Read the plan. For each planned component, follow execution:
- Where does input come from? What transforms it? Where does it go? What can go wrong?

**Step 2. Map user flows and error states:**
- User flows: full journey sequences
- Interaction edge cases: double-click, navigate-away, stale data, slow connection, concurrent actions
- Error states: clear message? recovery path?
- Empty/zero/boundary states

**Step 3. Check each branch against existing tests:**
Search for tests covering each path.

Quality scoring:
- ★★★ Tests behavior with edge cases AND error paths
- ★★ Tests correct behavior, happy path only
- ★ Smoke test / trivial assertion

### E2E Test Decision Matrix

**RECOMMEND E2E ([→E2E]):**
- Common flow spanning 3+ components
- Integration point where mocking hides failures
- Auth/payment/data-destruction flows

**RECOMMEND EVAL ([→EVAL]):**
- Critical LLM call quality
- Prompt template changes

**STICK WITH UNIT TESTS:**
- Pure functions, internal helpers, obscure flows

### REGRESSION RULE (mandatory)

**IRON RULE:** When the audit identifies a REGRESSION — code that previously worked but the diff broke — a regression test is added as critical requirement. No AskUserQuestion. No skipping.

A regression is when:
- The diff modifies existing behavior
- Existing test suite doesn't cover the changed path
- Change introduces new failure mode for existing callers

**Step 4. Output ASCII coverage diagram:**
```
CODE PATH COVERAGE
===========================
[+] src/services/billing.ts
    │
    ├── processPayment()
    │   ├── [★★★ TESTED] Happy path + card declined — billing.test.ts:42
    │   ├── [GAP]         Network timeout — NO TEST
    │   └── [GAP]         Invalid currency — NO TEST

USER FLOW COVERAGE
===========================
[+] Payment checkout flow
    │
    ├── [★★★ TESTED] Complete purchase — checkout.e2e.ts:15
    ├── [GAP] [→E2E] Double-click submit — needs E2E
    └── [★   TESTED]  Form validation — checkout.test.ts:40

─────────────────────────────────
COVERAGE: 5/13 paths tested (38%)
  Code paths: 3/5 (60%)
  User flows: 2/8 (25%)
QUALITY:  ★★★: 2  ★★: 2  ★: 1
GAPS: 8 paths need tests (2 E2E, 1 eval)
─────────────────────────────────
```

**Step 5. Add missing tests to the plan:** For each GAP, specify test file, assertions, type (unit/E2E/eval), regression flag.

### Test Plan Artifact

Write to `docs/designs/test-plans/{user}-{branch}-test-plan-{datetime}.md`:
```markdown
# Test Plan
Generated by gstack-eng-review on {date}
Branch: {branch}

## Affected Pages/Routes
- {URL path} — {what to test}

## Key Interactions
- {interaction} on {page}

## Edge Cases
- {edge case} on {page}

## Critical Paths
- {end-to-end flow that must work}
```

**STOP.** One issue per AskUserQuestion.

### 4. Performance review

Evaluate:
* N+1 queries and DB access patterns.
* Memory-usage concerns.
* Caching opportunities.
* Slow or high-complexity code paths.

**STOP.** One issue per AskUserQuestion.

## CRITICAL RULE — How to ask questions

* **One issue = one AskUserQuestion.** Never combine.
* Describe concretely with file/line references.
* Present 2-3 options including "do nothing."
* For each option: effort, risk, maintenance burden.
* Map to engineering preferences.
* Label NUMBER + LETTER.
* **Escape hatch:** No issues → say so, move on. Obvious fix → state it, move on.

## Required outputs

### "NOT in scope" section
Work considered and deferred, with one-line rationale.

### "What already exists" section
Existing code/flows that partially solve sub-problems — reused or rebuilt?

### TODOS.md updates
Present each TODO individually via AskUserQuestion. Format: What / Why / Pros / Cons / Context / Dependencies.
Options: A) Add to TODOS.md B) Skip C) Build it now.

### Diagrams
ASCII diagrams for non-trivial flows. Identify files that need inline diagrams.

### Failure modes
For each new codepath: one realistic production failure + whether it's tested, handled, visible to user. Silent untested unhandled = **critical gap**.

### Completion summary
```
  +====================================================================+
  |          ENG PLAN REVIEW — COMPLETION SUMMARY                       |
  +====================================================================+
  | Step 0: Scope Challenge    | ___ (accepted / reduced)              |
  | Architecture Review        | ___ issues found                      |
  | Code Quality Review        | ___ issues found                      |
  | Test Review                | diagram produced, ___ gaps             |
  | Performance Review         | ___ issues found                      |
  | NOT in scope               | written                               |
  | What already exists        | written                               |
  | TODOS.md updates           | ___ items proposed                    |
  | Failure modes              | ___ critical gaps flagged             |
  +====================================================================+
```

## Retrospective learning

Check git log for prior review cycles. Be more aggressive on previously problematic areas.

## Next Steps — Review Chaining

**Suggest `/gstack-design-review` if UI changes exist and no design review run.**
**Mention `/gstack-ceo-review` if significant product change and no CEO review.**

Options:
- A) Run /gstack-design-review (only if UI scope detected)
- B) Run /gstack-ceo-review (only if significant product change)
- C) Ready to implement

## Unresolved decisions

If the user doesn't respond to an AskUserQuestion or moves on, note which decisions were left unresolved. Never silently default.

## Formatting rules

* NUMBER issues, LETTERS for options. One sentence max per option.
* After each section, pause for feedback.
