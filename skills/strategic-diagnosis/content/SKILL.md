---
name: strategic-diagnosis
description: A structured analytical framework for diagnosing organizational or business problems from documents (presentations, reports, proposals, strategy decks). Use this skill whenever the user asks to "analyze the logic of," "break down the structure of," "find the underlying framework in," or "diagnose the argument in" any business document — or when they upload a presentation/report and ask for strategic analysis, structural critique, or want to extract a reusable methodology from it. Also trigger when the user wants to evaluate whether a proposal's reasoning is sound, or when they want to build a consulting-style diagnosis from raw observations. This skill is about analytical thinking, not summarization.
---

# Strategic Diagnosis Framework

A five-phase analytical method for extracting, evaluating, and constructing strategic arguments from business documents. Derived from consulting-grade presentation logic and enhanced with diagnostic rigor.

## When to use this skill

Use this framework when analyzing any document that attempts to move from **problems → solutions** — strategy decks, brand audits, operational reviews, transformation proposals, investor pitches, or organizational change plans. The framework works whether you're *analyzing someone else's argument* or *constructing your own*.

## The Five Phases

Work through these phases sequentially. Each phase builds on the previous one. Do not skip phases — a weak foundation undermines everything downstream.

---

### Phase 1: Symptom Inventory (What is broken?)

**Goal:** Catalog all surface-level problems with quantified evidence.

**Why this matters:** Numbers transform complaints into evidence. "Our materials look messy" is an opinion. "100+ material types across 50+ specs in 8+ color schemes" is a structural finding. Quantification forces precision and prevents the analyst from cherry-picking anecdotes.

**Execution steps:**

1. Extract every discrete problem or pain point the document identifies.
2. For each problem, determine whether it is quantified. Record the metric if present; flag it as "unquantified" if absent.
3. Categorize each problem by domain (operational, financial, brand, customer-facing, internal process, etc.).
4. Assess coverage: are the symptoms comprehensive, or do they cluster in one domain while ignoring others?

**Diagnostic questions to ask:**
- Are the problems described with specific numbers, or only with adjectives?
- Do the symptoms span multiple domains, or are they suspiciously narrow?
- Is there any problem the document conspicuously avoids mentioning?
- Could a skeptic dismiss any of these symptoms as normal or acceptable?

**Output format for this phase:**

```
SYMPTOM INVENTORY
─────────────────
| # | Symptom | Quantified? | Metric | Domain |
|---|---------|-------------|--------|--------|
| 1 | ...     | Yes/No      | ...    | ...    |

Coverage assessment: [which domains are represented, which are missing]
Quantification rate: [X of Y symptoms are numerically grounded]
```

---

### Phase 2: Systemic Pattern Recognition (Why do all these problems exist simultaneously?)

**Goal:** Identify the underlying structural pattern that connects the individual symptoms.

**Why this matters:** This is the most intellectually demanding phase and the one most often skipped. Individual symptoms invite individual fixes (whack-a-mole). A systemic pattern reveals that the symptoms share a common cause, which means a single intervention can address multiple problems at once. If you can't find the pattern, the solutions downstream will feel arbitrary.

**Execution steps:**

1. Look for shared characteristics across symptoms. Do they all involve the same process, the same decision-maker, the same resource constraint, or the same organizational blind spot?
2. Test the "simultaneous existence" question: what single condition, if true, would make *all* of these symptoms predictable? That condition is your candidate pattern.
3. Validate by inversion: if that condition were resolved, would you expect most symptoms to improve? If not, the pattern is too narrow.
4. Check whether the document itself identifies this pattern explicitly, or whether it merely lists symptoms without connecting them.

**Diagnostic questions to ask:**
- What would have to be true about this organization for all these problems to exist at the same time?
- Is there a missing capability, a misaligned incentive, or a structural gap that explains the cluster?
- Does the document connect its symptoms into a pattern, or does it leave that work to the reader?

**Output format for this phase:**

```
SYSTEMIC PATTERN
────────────────
Candidate pattern: [one sentence describing the structural condition]
Symptoms explained: [which symptoms this pattern accounts for]
Symptoms NOT explained: [any outliers — these may indicate a second pattern or a weakness in the diagnosis]
Document's own awareness: [does the document identify this pattern, or only imply it?]
```

---

### Phase 3: Root Cause Reframe (What is the single diagnostic statement that makes the solution feel inevitable?)

**Goal:** Produce a reframe — a single statement that changes how the audience understands the problem, making the proposed solution feel like the only logical response.

**Why this matters:** The reframe is the hinge of the entire argument. Before the reframe, the audience thinks they have a collection of operational problems. After the reframe, they understand they have a strategic deficit. This shift is what creates urgency and justifies investment. A weak reframe produces a weak case, regardless of how good the solutions are.

**Execution steps:**

1. Examine how the document transitions from diagnosis to prescription. What language does it use? Does it explicitly reframe, or does it just pivot to solutions?
2. Identify the **elevation move**: does the reframe raise the stakes from operational to strategic? From tactical to existential? From cosmetic to structural? The best reframes move UP at least one level of organizational significance.
3. Test the reframe's logic: does it follow necessarily from the pattern identified in Phase 2, or does it introduce new assumptions?
4. Evaluate the reframe's persuasive power: would a skeptical executive find this compelling, or would they see it as an exaggeration?

**Common reframe structures:**
- "You think you have an X problem, but you actually have a Y problem" (e.g., "You think you have a design problem, but you actually have a trust problem")
- "The reason [visible failure] keeps happening is that [invisible structural cause] has never been addressed"
- "Without [prerequisite condition], no amount of [current approach] will work"

**Diagnostic questions to ask:**
- Does the reframe change the audience's understanding, or merely confirm what they already know?
- Is the reframe supported by the evidence in Phase 1 and the pattern in Phase 2?
- Does it create a logical bridge to the proposed solution?
- Could the reframe be falsified? What evidence would contradict it?

**Output format for this phase:**

```
ROOT CAUSE REFRAME
──────────────────
The document's reframe: [extract or reconstruct the reframe statement]
Elevation move: [from what level → to what level]
Logical soundness: [does it follow from the evidence?]
Falsifiability: [what would disprove this reframe?]
Persuasive strength: [weak / moderate / strong — and why]
```

---

### Phase 4: Solution Architecture (Are the solutions structural or cosmetic?)

**Goal:** Evaluate whether the proposed solutions address the root cause or merely treat symptoms, and whether they follow the principle of "infrastructure before content."

**Why this matters:** The most common failure in strategic proposals is solutions that don't match the diagnosis. A document can have brilliant problem identification and then propose fixes that only address surface symptoms. The "infrastructure before content" principle — meaning you must fix the underlying system before you can fix what the system produces — is the key test.

**Execution steps:**

1. List every proposed solution or intervention.
2. For each, determine: does it address the root cause (Phase 3), the systemic pattern (Phase 2), or individual symptoms (Phase 1)? Solutions that only address symptoms are red flags.
3. Assess the layering logic: does the document propose fixing infrastructure before content? Does it sequence interventions so that earlier ones enable later ones?
4. Check for a governing principle: is there a stated logic that determines *why these solutions and not others*? Or does the solution set feel like a grab-bag?
5. Identify what's missing: are there obvious interventions that the diagnosis calls for but the solutions omit?

**The infrastructure-before-content test:**
- Infrastructure = systems, processes, physical environments, organizational structures, capabilities
- Content = outputs, communications, designs, campaigns, deliverables
- If the document proposes content fixes without infrastructure fixes, the solutions will be unstable — they'll revert as soon as the project ends.

**Diagnostic questions to ask:**
- Do the solutions follow logically from the diagnosis, or could they have been proposed without any diagnosis at all?
- Is there a sequencing logic (do X before Y because Y depends on X)?
- Are there solutions that address infrastructure, or only content?
- What is conspicuously absent from the solution set?

**Output format for this phase:**

```
SOLUTION ARCHITECTURE
─────────────────────
| # | Solution | Addresses | Layer | Depends on |
|---|----------|-----------|-------|------------|
| 1 | ...      | Root/Pattern/Symptom | Infra/Content | ... |

Sequencing logic: [present / absent / partial]
Governing principle: [stated or reconstructed]
Missing interventions: [what the diagnosis calls for but the solutions don't include]
```

---

### Phase 5: Sustainability & Measurement (Will this last?)

**Goal:** Evaluate whether the document addresses how the improvements will be sustained beyond the initial intervention, and whether success can be measured.

**Why this matters:** Most strategic proposals are designed to win approval, not to ensure lasting change. The difference between a one-time project and a genuine transformation lies in three things: capability transfer (does the organization learn to do this itself?), measurement (can you tell if it worked?), and feedback loops (does the system self-correct over time?). A proposal that lacks all three is a consulting engagement disguised as a strategy.

**Execution steps:**

1. Check for a capability-building component: does the document propose building internal capacity, or does it create permanent dependency on external support?
2. Look for success metrics: are outcomes defined in measurable terms? Could you, 12 months later, determine whether the intervention succeeded?
3. Identify feedback mechanisms: is there a proposed loop where results are reviewed, lessons are extracted, and the approach is refined?
4. Assess the "what if it works" scenario: if every recommendation is implemented perfectly, what would actually change? Is that change worth the investment?

**Diagnostic questions to ask:**
- If the consultant (or project team) disappears tomorrow, can the organization sustain the improvements?
- What specific metrics would indicate success at 6 months? At 12 months?
- Is there a feedback loop that allows course correction?
- What is the implicit cost of doing nothing?

**Output format for this phase:**

```
SUSTAINABILITY ASSESSMENT
─────────────────────────
Capability transfer: [present / absent / partial]
Success metrics: [defined / vague / absent]
Feedback loops: [present / absent / partial]
Dependency risk: [low / medium / high — does this create ongoing dependency?]
Cost of inaction: [stated / implied / unstated]
```

---

## Synthesis: The Final Diagnostic Report

After completing all five phases, produce a synthesis that answers three questions:

1. **Is the argument internally consistent?** Does the diagnosis lead logically to the solutions? Are there gaps or contradictions?
2. **Is the argument externally valid?** Would the proposed approach actually work in the real world? Are the assumptions reasonable?
3. **What would make this stronger?** What is the single most impactful improvement the document could make?

**Output format:**

```
STRATEGIC DIAGNOSIS — SYNTHESIS
═══════════════════════════════
Document: [name/title]
Analyst: Claude
Date: [date]

INTERNAL CONSISTENCY: [Strong / Moderate / Weak]
[2-3 sentences explaining why]

EXTERNAL VALIDITY: [Strong / Moderate / Weak]
[2-3 sentences explaining why]

HIGHEST-IMPACT IMPROVEMENT:
[One specific, actionable recommendation]

FRAMEWORK QUALITY SCORE:
  Symptom inventory:       [●●●●○] 4/5
  Systemic pattern:        [●●●○○] 3/5
  Root cause reframe:      [●●●●●] 5/5
  Solution architecture:   [●●●○○] 3/5
  Sustainability:          [●●○○○] 2/5
```

---

## Adaptation Guide

This framework is domain-agnostic. Here are the mental substitutions for different contexts:

| PDF Context | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|---|---|---|---|---|---|
| Brand audit | Visual problems | Brand identity gap | Trust/perception reframe | Design system + space redesign | Internal capability building |
| Operational review | Process failures | Systemic bottleneck | Capacity/architecture reframe | Process + infrastructure redesign | KPIs + feedback loops |
| Market entry proposal | Market barriers | Competitive dynamics | Positioning reframe | Go-to-market architecture | Metrics + iteration plan |
| Organizational change | Cultural symptoms | Structural misalignment | Leadership/incentive reframe | Org design + process change | Change management sustainability |
| Tech debt assessment | Bug clusters | Architecture decay | Platform reframe | Refactor sequence | Monitoring + ownership model |

---

## Common Pitfalls

When applying this framework, watch for these failure modes:

- **Symptom-solution shortcut:** Jumping from Phase 1 directly to Phase 4 without finding the systemic pattern. This produces solutions that treat symptoms rather than causes.
- **Unfalsifiable reframes:** A reframe that can't be disproven isn't a diagnosis — it's a belief. Always ask "what evidence would contradict this?"
- **Content-only solutions:** If every proposed fix is a new output (new design, new campaign, new report) rather than a structural change, the solutions won't stick.
- **Missing sequencing:** Solutions without dependencies feel like a shopping list. The question "what must be done first to enable everything else?" usually reveals the critical path.
- **Sustainability theater:** Mentioning "ongoing support" or "continuous improvement" without specifying metrics, feedback loops, or capability transfer is not a sustainability plan.
