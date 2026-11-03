# Scene-Foundation: Pain Point Mapping & Quadrant Chart

Maps the target industry's pain points and identifies the highest-impact
conversation anchor for a first client meeting.

## Workflow

### Step 1 — Gather Context

Ask the user:
1. **Target industry** (e.g., "SaaS", "retail banking", "pharma manufacturing")
2. **Company positioning**: Market Leader / Challenger / Niche Player / Follower / New Entrant
3. **Meeting attendees**: Names, titles, seniority, functional areas

### Step 2 — Research Industry Pain Points

Use web search. Query patterns:
- `"[industry] industry challenges 2025"`
- `"[industry] pain points revenue"`
- `"[industry] digital transformation challenges"`
- `"[industry] [positioning] company challenges"`
- `"[target company name] strategy priorities news"`

Synthesize 6-12 distinct pain points with source evidence.

### Step 3 — Classify by Revenue Impact

Use the 6-category hierarchy (see [scene-methodology.md](scene-methodology.md) for full table):

| Rank | Category | Examples |
|------|----------|----------|
| 1 | Direct Revenue Loss | Customer churn, pricing pressure, market share decline |
| 2 | Growth Bottleneck | Slow market entry, scaling issues, limited distribution |
| 3 | Operational Efficiency | Manual processes, system downtime, high cost-to-serve |
| 4 | Customer Experience | Poor UX, slow response, limited self-service |
| 5 | Compliance & Risk | Regulatory fines, security gaps, reputational risk |
| 6 | Back-office Efficiency | HR admin, internal tooling, overhead |

Sort by rank ascending. Within same rank, keep most-cited or most
positioning-relevant first.

### Step 4 — Deliver Pain Point Map

```
# [Industry] Pain Point Map — [Company Position]

## Revenue-Critical (Direct) 🔴
1. [Pain point] — [Brief evidence with source]

## Growth-Critical 🟠
1. [Pain point] — [Brief evidence with source]

## Operational 🟡
## Experience 🟢
## Compliance & Risk 🔵
## Back-office ⚪

> Sources: [list]
```

Confirm with user before proceeding.

---

### Step 5 — Map Decision-Maker Focus Areas

For each attendee, research and rank likely focus areas.

Ask the user:
- Any known priorities or recent initiatives for each attendee
- The attendee's specific functional responsibilities

Supplement with web search:
- `"[company name] [role] priorities"`
- `"[industry] [role] challenges"`
- `"[company name] news 2025"`

Map to functional categories: Sales/Revenue, Marketing, Operations, Finance,
IT/Tech, HR/Talent, Customer Success, Product/R&D, Compliance/Risk.

Deliver:
```
# Decision-Maker Focus: [Title] at [Company]

## Profile
- Role: [Title], [Seniority]
- Functional scope: [areas]

## Focus Areas (ranked)
1. [Area] — [Reasoning with evidence]

## Blind Spots
- [Areas they may undervalue but have high revenue impact]
```

---

### Step 6 — Generate Quadrant Chart

Prepare data:
- Pain points: `[{"name": "...", "category_rank": 1-6}, ...]`
- Focus areas: `["Sales", "Operations", ...]` (one per attendee or combined)
- Weights: per-cell differentiated weights reflecting each role's actual
  relevance to each pain category (see Differentiated Weighting below)

Run the script:
```bash
python scripts/generate_quadrant_chart.py \
  --pain-points '[...]' \
  --focus-areas '[...]' \
  --weights '{...}' \
  --output scene_quadrant_[client].png \
  --title "SCENE Quadrant — [Client] x [Us]"
```

#### Differentiated Weighting (Critical)

Do not use uniform weights. Assign per-cell weights based on role-relevance:

| Weight | Meaning |
|--------|---------|
| 3.0 | Core responsibility — this pain is directly in their scope |
| 2.0 | Strongly influenced — they feel consequences of this pain |
| 1.0 | Peripheral — they are aware but not directly impacted |
| 0.5 | Background — relevant to org but not to their personal KPIs |

Example: A CTO's weight for "Legacy system limits speed" should be 3.0,
but for "Customer churn to fintech" may be 1.5 (they care but it's not
their direct remit). A CCO's weight for "KKI card system migration" is 3.0
but for "Poor digital UX" may be 1.5.

---

### Step 7 — Interpret and Deliver

```
# SCENE Quadrant Analysis — [Client]

[Insert chart image]

## Primary Anchor ⭐
[Pain Point] × [Focus Area] — Score: [X]
→ Open your narrative here. Connect pain to personal stakes.

## Secondary Anchors (Score ≥ 12)
1. [Pain] × [Focus] — Score: [X]

## Narrative Arc
1. Hook: Primary Anchor (pain + personal relevance)
2. Expand: Secondary Anchors (broader problem scope)
3. Bridge: To your solution capabilities

## Per-Role Quick Reference
| Role | Top Pain to Discuss | Cloud Capability Hook |
|------|--------------------|-----------------------|
| CEO | Customer churn | Elastic infra for scale |
| CMO | E-commerce share loss | AI conversion optimization |
| CTO | Legacy system limits | Hybrid cloud migration |
| ... | ... | ... |
```

## Adaptation Notes

- **Multiple attendees with different roles**: Use differentiated weights per
  role. Optionally generate separate mini-charts per role for clarity.
- **Existing relationship**: Reduce web research; prioritize user insights.
- **Time pressure**: Collapse Steps 2-4 into a single research pass; skip
  quadrant chart if user only needs the ranked pain list.
- **User cannot specify industry**: Start with cross-industry scan, narrow
  down after initial findings.
