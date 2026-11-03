---
name: dealscene
description: >
  Sales pitch preparation using the DEALSCENE methodology. Helps users decide
  what to talk about in a first client meeting. Triggers on: sales pitch prep,
  first meeting preparation, opening narrative for sales calls, product intro
  for prospects, demo planning, or building a compelling sales story. Three
  sub-systems: (1) Scene-Foundation — maps industry pain points and finds the
  highest-impact conversation anchor via a visual quadrant chart;
  (2) Value-Proofer — validates product claims by stress-testing 2-3 core
  scenes against real success stories across multiple persuasion dimensions;
  (3) Demo-Storyteller — designs a future-state demo concept using human-center
  then business-center perspectives. Use the full workflow for initial sales
  meetings, or individual modules for pain mapping, case validation, or demo
  design only.
---

# DealScene — Sales Pitch Preparation System

A three-module system for building a compelling first-client-meeting narrative.
Each module produces a concrete output that feeds into the next, or can be used
standalone.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEALSCENE WORKFLOW                                        │
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐       │
│  │ 1. Scene-Foundation│──►│ 2. Value-Proofer │──►│ 3. Demo-Storyteller│       │
│  │                  │    │                  │    │                  │       │
│  │ Output: Pain Map │    │ Output: Validated│    │ Output: Demo     │       │
│  │ + Quadrant Chart │    │ Case List        │    │ Concept / Script │       │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘       │
│         │                       │                       │                   │
│    "Where to                    │                       │                   │
│     start talking"              │                       │                   │
│                          "Why should they              │                   │
│                           believe us"                  │                   │
│                                                   "What changes             │
│                                                    after using us"          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## When to Use Which Module

**Run the full 3-module workflow** when the user is preparing for a first
meeting with a new prospect and has not yet finalized what to talk about.

**Run Scene-Foundation only** when the user needs to understand the client's
industry landscape and identify high-priority conversation anchors. Output is
a ranked pain point map and optionally a visual quadrant chart showing pain
points × decision-maker focus areas.

**Run Value-Proofer only** when the user already knows which scenes to discuss
but needs to validate that their product claims are backed by credible,
persuasive evidence. Output is a curated list of validated success cases
mapped to 2-3 core scenes.

**Run Demo-Storyteller only** when the user has a validated scene and wants
to design a compelling future-state vision or demo concept. Output is a demo
idea or video script showing how the client's world changes after adopting
the product.

---

## Module 1: Scene-Foundation

**Goal**: Map industry pain points and find the highest-impact conversation
anchor point.

**Read**: [references/scene-foundation.md](references/scene-foundation.md) for
the complete step-by-step workflow including:
- Industry pain point research via web search
- Pain point classification and revenue-impact sorting
- Decision-maker focus area identification
- Quadrant chart generation (using `scripts/generate_quadrant_chart.py`)
- Primary and secondary anchor selection

**Quick summary**:
1. Ask: target industry, company positioning, meeting attendees
2. Research industry pain points online
3. Sort pain points by revenue impact (Direct Revenue → Back-office)
4. Map each attendee's likely focus areas
5. Generate quadrant chart (pain points × focus areas with scores)
6. Identify the Primary Anchor (highest-score intersection) and Secondary Anchors

**Output**: Pain Point Map + Quadrant Chart PNG + Anchor recommendation.

---

## Module 2: Value-Proofer

**Goal**: Validate that the selected scenes are backed by credible,
persuasive success stories from the user's own product history.

**Read**: [references/value-proofer.md](references/value-proofer.md) for the
complete validation workflow including:
- Core scene selection (pick 2-3 from Module 1 anchors)
- Case intake template
- 4-dimension persuasion scoring framework
- Iterative gap-filling process
- Final validated case portfolio

**Quick summary**:
1. Select 2-3 core scenes from Module 1 anchors
2. For each scene, collect 1+ success cases from the user
3. Score each case across 4 dimensions (industry relevance, pain relevance,
   solution effectiveness, data support) from the **listener's perspective**
4. Iteratively improve or replace cases until each scene has at least one
   passing case (score ≥ threshold)
5. Deliver a validated case list ready for the meeting

**Output**: Validated Case Portfolio (2-3 scenes × 1-2 cases each with scores).

---

## Module 3: Demo-Storyteller

**Goal**: Design a future-state vision and a concrete demo concept that shows
how the client's world improves after adopting the product.

**Read**: [references/demo-storyteller.md](references/demo-storyteller.md) for
the complete demo design workflow including:
- Human-Center perspective: beneficiary, journey transformation, experience gain
- Business-Center perspective: experience change → business outcome change
- Demo concept types (simulated product demo vs. video script)
- Client asset integration guidelines
- Story arc templates

**Quick summary**:
1. Pick one validated scene+case from Module 2 as the anchor
2. Research the client's company and users to identify the **core beneficiary**
3. Describe the beneficiary's **current journey** (with pain) and **future
   journey** (with your product) — focus on emotional and experiential change
4. Map the experience change to **business outcome change** (metrics)
5. Design a demo concept: either a **simulated product demo** (using client
   branding/assets) or a **video shoot script**
6. Ensure the demo can be shown in 3-5 minutes

**Output**: Demo Concept Document with Human-Center story + Business-Center
summary + demo script / simulation guide.

---

## Running the Full Workflow

Default execution order: Module 1 → Module 2 → Module 3.

Each module produces an output that should be reviewed with the user before
proceeding. Key decision gates:

- **After Module 1**: User confirms or adjusts the selected Primary/Secondary
  Anchors before proceeding to case validation.
- **After Module 2**: User confirms the validated case list is sufficient and
  accurate. If a scene has no passing case, do not proceed to Module 3 for
  that scene — either find more cases or drop the scene.
- **After Module 3**: User reviews the demo concept for feasibility. Adjust
  scope or format (simulation vs. video) based on demo logistics.

## Supporting Resources

- **Methodology reference**: [references/scene-methodology.md](references/scene-methodology.md)
  — Pain point classification, company positioning categories, decision-maker
  archetypes, scoring formulas, output templates.
- **Quadrant chart script**: `scripts/generate_quadrant_chart.py` — Generates
  the pain point × focus area heatmap with priority scores and critical-cell
  highlighting. Requires `--pain-points`, `--focus-areas`, `--weights` JSON
  arguments.
 positioning.

---

## Adaptation Notes

- **Multiple attendees**: Run Layer 2 for each attendee, then either
  (a) create a combined focus area list, or (b) generate separate
  quadrant charts per attendee if their roles differ significantly.
- **Existing relationship**: If the user already knows the client well,
  skip or reduce web research — prioritize user-provided insights.
- **Industry unknown**: If the user cannot specify the industry, do a
  broader cross-industry pain point scan first, then narrow down.
- **Time pressure**: For urgent requests, collapse Layers 1–2 into a
  single research + synthesis step, then go directly to Layer 3.
