# Value-Proofer: Persuasive Case Validation

Validates that 2-3 selected core scenes are backed by credible, persuasive
success stories. Stress-tests each case from the **listener's perspective** to
ensure it will hold up in the meeting room.

## Workflow

### Step 1 — Select Core Scenes

From Scene-Foundation output (pain point map + quadrant chart), pick the
2-3 highest-priority scenes to validate. Selection criteria:
- Must include the Primary Anchor scene
- Should cover different attendees' interests (diversify across roles)
- Should have highest revenue-impact + role-relevance combination

Deliver to user:
```
# Core Scenes to Validate

Scene 1 (Primary): [Pain Point] × [Focus Area]
  → Target attendee: [Name/Role]
  → Key claim: "Our product solves [this pain] for [this type of org]"

Scene 2: [Pain Point] × [Focus Area]
  → Target attendee: [Name/Role]
  → Key claim: "..."

Scene 3: [Pain Point] × [Focus Area] (optional)
  → Target attendee: [Name/Role]
  → Key claim: "..."
```

Confirm scene selection with user before proceeding.

---

### Step 2 — Collect Success Cases

For each scene, ask the user to provide success cases from their product
history. A "case" can be:
- A named customer deployment with measurable results
- An internal pilot that demonstrated clear value
- A POC with concrete metrics
- A partner/integration success story

**Case Intake Template** (ask user to fill one per case):

```
## Case Submission — Scene [N]: [Scene Name]

**Customer/Org name**: [Name or anonymized descriptor]
**Industry**: [Same as target? Adjacent? Different?]
**Their pain (before us)**: [What problem did they face?]
**Our solution**: [What product/capability did we deploy?]
**Measurable outcome**: [Specific numbers: % improvement, $ saved,
  time reduced, users gained, etc.]
**Time to result**: [How long from deployment to outcome?]
**Reference-ability**: [Can they be named? Can we share anonymized data?]
**Data evidence**: [Screenshots? Dashboard exports? Case study doc?]
```

Accept whatever the user provides, even incomplete submissions. Do not
judge quality yet — evaluation comes in Step 3.

**Minimum target**: At least 2 cases per scene initially (to have options
after scoring). If user has fewer, note it as a gap.

---

### Step 3 — 4-Dimension Persuasion Scoring

For each case, score from 0-5 across four dimensions. **The scoring lens
is the LISTENER** (the client attendee), not the seller.

| Dimension | Question | Score Guide |
|-----------|----------|-------------|
| **Industry Relevance (IR)** | "Does this case come from an organization LIKE MINE?" | 5=Same industry + same positioning; 4=Same industry different positioning; 3=Adjacent industry; 2=Distant industry but same function; 1=Any industry; 0=Not applicable |
| **Pain Relevance (PR)** | "Is the pain described IDENTICAL or highly similar to MY pain?" | 5=Exact same pain, same symptoms; 4=Same pain category, similar symptoms; 3=Related pain in same domain; 2=Pain is adjacent; 1=Pain is loosely connected; 0=No connection |
| **Solution Effectiveness (SE)** | "Did the solution produce a MEANINGFUL, believable result?" | 5=Quantified ROI with third-party validation; 4=Quantified ROI with customer quote; 3=Quantified result no validation; 2=Qualitative positive outcome; 1=Vague positive claim; 0=No outcome stated |
| **Data Support (DS)** | "Is there CONCRETE evidence I can see or verify?" | 5=Published case study with customer logo + metrics; 4=Internal case doc with screenshots/metrics; 3=Customer quote + numbers; 2=Internal anecdote with some numbers; 1=Anecdote no numbers; 0=No evidence |

**Total Score** = IR + PR + SE + DS (range 0-20)

**Passing threshold**: Total ≥ 12 AND no dimension below 2
**Strong case**: Total ≥ 16
**Weak case**: Total < 10 — must improve or replace

### Step 3 Execution

Score each case and present:

```
# Case Validation Results — Scene 1: [Scene Name]

## Case A: [Customer Name]
| Dimension | Score | Listener Perspective Notes |
|-----------|-------|---------------------------|
| Industry Relevance | X/5 | [Why: same/adjacent/distant] |
| Pain Relevance | X/5 | [Why: exact/related/loose] |
| Solution Effectiveness | X/5 | [Why: ROI level, believability] |
| Data Support | X/5 | [Why: evidence quality] |
| **TOTAL** | **X/20** | **Verdict: PASS / NEEDS WORK / REPLACE** |

## Case B: [Customer Name]
[...same format...]

### Scene 1 Status: [✅ Validated / ⚠️ Needs more cases / ❌ No viable case]
```

---

### Step 4 — Iterative Gap-Filling

For any scene that lacks a passing case, guide the user through improvement
or replacement:

**If a case scores low on Industry Relevance**:
- "Can you find a case closer to [target industry]? Even a partial match helps."
- "Is there a case in [adjacent industry] that had the EXACT same pain?"
- Consider: can the case be framed differently to emphasize functional
  similarity over industry similarity?

**If a case scores low on Pain Relevance**:
- "The pain described is adjacent but not identical. Can you reframe it to
  highlight [specific symptom that matches the target's pain]?"
- "Do you have any case where the customer faced [exact pain name]?"

**If a case scores low on Solution Effectiveness**:
- "The result is qualitative. Can you add any quantitative metric, even
  approximate? E.g., 'reduced processing time by roughly 40%'."
- "Is there a dashboard screenshot or internal report with numbers?"

**If a case scores low on Data Support**:
- "Can we get a brief quote from the customer, even informal?"
- "Is there an internal success memo or post-mortem with metrics?"
- "Can we create a one-pager with anonymized data?"

Iterate: User provides improved/new case → Re-score → Repeat until each
scene has at least one passing case.

**Hard stop rule**: If after 3 iterations a scene still has no passing case,
recommend dropping that scene from the pitch. Do not proceed to Demo-Storyteller
with unvalidated scenes.

---

### Step 5 — Deliver Validated Case Portfolio

```
# Validated Case Portfolio — [Client Name]

## Scene 1: [Scene Name] — Target: [Attendee]
✅ Primary Case: [Customer] (Score: X/20)
   - Industry: [X] → Relevance: [explanation]
   - Pain match: [X] → [explanation]
   - Outcome: [specific metric]
   - Evidence: [what we can show]
   - Key talking point: "One sentence pitch for this case"

   Backup Case: [Customer] (Score: X/20) [if available]

## Scene 2: [Scene Name] — Target: [Attendee]
[...same format...]

## Scene 3: [Scene Name] — Target: [Attendee] (if applicable)
[...same format...]

---

## Meeting Talking Points Summary

| Scene | Lead Case | One-Liner | Evidence Ready? |
|-------|-----------|-----------|-----------------|
| 1 | ... | ... | Yes/No |
| 2 | ... | ... | Yes/No |
| 3 | ... | ... | Yes/No |

## Recommended Case Delivery Order
1. Lead with Scene [X] — strongest case, highest attendee relevance
2. Follow with Scene [Y] — covers different attendee
3. Close with Scene [Z] — broadest appeal
```

---

## Key Principles

1. **Listener-first scoring**: Always ask "will THIS attendee find this
credible and relevant?" not "is this our best case?"
2. **One passing case per scene minimum**: No scene goes into the pitch
   without at least one validated case. Unvalidated scenes get dropped.
3. **Iterate don't settle**: Low scores are opportunities to improve the
   case framing, not verdicts. Guide the user to find better evidence.
4. **Quantification is king**: Even approximate numbers beat qualitative
   claims in a first meeting. Push for metrics.
5. **Honesty about gaps**: If no good case exists for a scene, say so
   clearly. Better to drop a weak scene than to be challenged in the room.
