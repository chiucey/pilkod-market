# Cases, Product Sense, and Technical Rounds

Behavioral questions are a conversation. These are not — they're a structured
exercise with a protocol, and running one like a chat teaches the wrong habits.

Read the relevant section in full before starting. Improvising a case wastes the
candidate's session; the value is entirely in running it the way the real one runs.

## Contents

- [Case interviews](#case-interviews)
  - [Interviewer-led (McKinsey style)](#interviewer-led-mckinsey-style)
  - [Candidate-led (BCG / Bain style)](#candidate-led-bcg--bain-style)
  - [Full cases with data](#full-cases-with-data)
  - [Scoring a case](#scoring-a-case)
- [Product management rounds](#product-management-rounds)
  - [Product sense](#product-sense)
  - [Metrics and execution](#metrics-and-execution)
  - [Estimation](#estimation)
  - [Prioritization](#prioritization)
  - [Scoring a product round](#scoring-a-product-round)
- [Technical rounds](#technical-rounds)

> Before using anything here, check whether the target firm publishes its own
> practice cases — McKinsey, BCG and Bain all do. A firm's own published case is
> more accurate than anything reconstructed, and using it is the single highest-value
> thing the research step can turn up.

---

## Case interviews

### The rules that make it real

**Give the prompt, then stop talking.** Silence after the prompt is part of the
exercise. Candidates who fill it by immediately reciting a framework are showing you
exactly what they'd do in front of a client.

**Never volunteer data.** Every number in the case sits behind a question the
candidate has to ask. Handing over an exhibit unprompted destroys the main thing
being tested: do they know what they need to know?

**Make them do the math out loud.** If they go quiet and produce a number, ask how
they got it. Silent arithmetic is unverifiable, and in the real thing it reads as
either luck or memorization.

**Ask "so what?" after every calculation.** A number with no interpretation is worth
nothing. This is the most common gap between a candidate who passes and one who
doesn't.

**Don't rescue them.** If they go down a dead end, let them. Note where they were
when they noticed — self-correction is a strong signal and you can't observe it if
you intervene. Coaching mid-case makes the debrief meaningless.

### Interviewer-led (McKinsey style)

You steer. The case is a sequence of discrete questions and you move between them
regardless of where the candidate wanted to go. Structure still gets scored, but
you control the path.

Sequence:

1. **Prompt.** Client, situation, and the question. Then stop.
2. **Clarifying questions.** Expect two or three good ones. Answer briefly. Note if
   they ask none, or ask six.
3. **Structure.** "How would you think about this?" Expect a structure before any
   analysis, and expect it to be built for *this* problem — a memorized profitability
   tree applied without adaptation is a weaker signal than a rough bespoke one.
4. **Quantitative question.** Hand over an exhibit or numbers when asked. Make them
   walk through the arithmetic.
5. **"So what does that tell you?"**
6. **Qualitative or brainstorming question.** "What else might be driving this?"
   Expect structure here too, not a list.
7. **Recommendation.** "The CEO just walked in — you have 60 seconds." Expect: answer
   first, two or three supporting reasons, a risk, and a next step.

### Candidate-led (BCG / Bain style)

They drive. After the prompt and structure, they choose what to examine and in what
order. You answer what's asked and otherwise stay quiet.

What to watch that the interviewer-led version doesn't test:

- Do they say *why* they're going somewhere before going there?
- Do they synthesize as they go, or only at the end?
- When a branch turns out to be a dead end, do they say so and move, or keep
  digging to avoid admitting it?
- Do they manage time, or spend twenty minutes on the first branch?

If they stall for more than a few seconds, don't fill it. If they're still stuck,
ask "what are you thinking?" — that's a legitimate prompt and it's what a real
interviewer does.

### Full cases with data

Two complete cases. Hold back the exhibits until asked.

---

#### Case A — Profitability (interviewer-led)

**Prompt.** Our client is a regional grocery chain in the western US with 140
stores. Over the past two years revenue has been flat, but operating margin has
fallen from 4.2% to 1.5%. The CEO wants to know why, and what to do about it.

*Clarifications, if asked:*
- Same store count both years; no acquisitions or closures
- Product mix roughly stable
- Competitors in the region have seen margins fall about 0.5 points over the same
  period, so most of this is client-specific
- Client is privately held; no pressure for a quick exit

*Exhibit 1 — Cost as % of revenue (release only when asked for a cost breakdown):*

| | Two years ago | Now |
|---|---|---|
| Cost of goods sold | 71.0% | 71.4% |
| Store labor | 14.5% | 17.2% |
| Occupancy | 6.0% | 6.1% |
| Other SG&A | 4.3% | 3.8% |
| **Operating margin** | **4.2%** | **1.5%** |

The story is labor: +2.7 points, essentially the entire gap.

*Exhibit 2 — Labor detail (only if they dig into labor specifically):*

| | Two years ago | Now |
|---|---|---|
| Average hourly wage | $15.20 | $17.90 |
| Labor hours per store-week | 1,850 | 1,835 |
| Sales per labor hour | $142 | $143 |

Hours and productivity are flat. Wages rose 17.8% and none of it was passed through
to price — revenue flat with stable volume means flat prices in an inflationary
period.

*Math to expect:* wage increase of 2.70/15.20 ≈ 17.8%; applied to a 14.5% labor
base gives ≈ 2.6 points, which is essentially the whole margin decline.

*The insight:* this is not a cost-control problem, it's a **pricing** problem. Wages
rose market-wide; competitors held margin because they raised prices. Strong
candidates get to "why didn't we raise prices?" on their own. Very strong ones ask
about price elasticity and the competitive position before recommending it.

*If they only recommend cutting labor:* push — "hours per store are already flat and
productivity hasn't moved. What else?"

*Good recommendation:* a targeted price increase, tested first on low-elasticity
categories, with a risk acknowledged (volume loss to a discount competitor) and a
next step (elasticity analysis on a store subset).

---

#### Case B — Market entry (candidate-led)

**Prompt.** Our client is a mid-sized private university in the Midwest, about
8,000 students, currently entirely in-person. The board is considering launching a
fully online degree program. Should they?

*Clarifications, if asked:*
- Goal is financial sustainability — enrollment has declined about 1% a year for
  five years
- They have no online infrastructure today
- Board wants a decision within a year; launch would be two years out
- No fixed budget yet, which is itself worth noticing

*Data, released on request:*

| | |
|---|---|
| Current tuition (in-person) | $34,000/year |
| Current cost to serve one student | $29,000/year |
| Estimated online tuition (market rate) | $14,000/year |
| Estimated marginal cost per online student | $6,500/year |
| One-time platform + course build | $18M |
| Ongoing platform operating cost | $3.5M/year |
| Realistic online enrollment by year 3 | 1,200–2,000 students |

*Math to expect:* contribution per online student = 14,000 − 6,500 = $7,500.
At 1,500 students: $11.25M/year, minus $3.5M ongoing = **$7.75M/year net**.
Payback on the $18M build ≈ **2.3 years** after reaching scale.

The economics work. Which is the trap.

*What separates a good candidate:* the number isn't the answer. The real questions
are **cannibalization** (do in-person students at $5,000 contribution switch to
online at $7,500? — that's actually accretive, worth noticing), **brand dilution**,
**whether they can execute** with zero online capability today, and **competition**
from universities that started ten years ago and have scale.

If they recommend "yes" on the strength of the payback alone without raising
execution risk, that's the case's main failure mode. Probe: "you're advising a board
with no online experience to spend $18M. What worries you?"

---

### Scoring a case

STAR doesn't apply. Score these instead, 1–5, same calibration (3 = average real
candidate):

| Dimension | What a 5 looks like |
|---|---|
| **Structure** | Bespoke to this problem, MECE, stated out loud before analysis, and actually followed |
| **Quantitative** | Sets up the math correctly, computes accurately out loud, sanity-checks the magnitude |
| **Business judgment** | Interprets every number, notices what the data implies rather than just reporting it, raises the risk nobody asked about |
| **Communication** | Signposts where they are, synthesizes as they go, recommendation is answer-first and client-ready |

Report separately, unscored: time management, whether they self-corrected, and
whether they asked for data before knowing why they wanted it.

Most common failures, in order: no structure or a memorized one; arithmetic done
silently; numbers reported without interpretation; a recommendation with no risk;
losing the original question halfway through.

---

## Product management rounds

Almost every PM loop splits into product sense, execution/metrics, and sometimes
estimation — usually in separate rounds with different interviewers. Practicing them
as generic behavioral questions is the most common preparation mistake.

### Product sense

**Format:** "Design X for Y." "How would you improve Z?" "Our users are churning at
onboarding — what would you build?"

**The protocol:**

1. Give the prompt. Let them clarify — the scope of "design a product for commuters"
   is genuinely ambiguous and they should say so.
2. **Interrupt anyone who proposes a solution before naming a user and a problem.**
   This is the single most common failure and it's worth breaking the flow to catch.
3. Expect segmentation: which users, and why this one first?
4. Expect a goal metric named *before* any feature is described.
5. Expect two or three solution options with a tradeoff, not one idea defended.
6. Ask "how would you know it worked?"

**Prompts:**

- Design a product for people caring for an aging parent.
- How would you improve Google Maps for someone who's just moved to a new city?
- Our note-taking app has high signup and 60% of users never return after day one.
  What do you build?
- Design a feature that helps a first-time user of our analytics tool find their
  first insight.
- You have 2 engineers for 6 weeks. What do you ship?

**Follow-up ladder:**

1. "Who exactly is this for? Describe one of them."
2. "What do they do today instead?"
3. "Why is that bad enough that they'd change?"
4. "What would you cut if you had half the time?"
5. "What's the strongest argument against building this?"

### Metrics and execution

**Format:** "Metric X dropped Y%. What do you do?" or "How would you measure the
success of feature Z?"

The diagnostic question has a right *process*, and candidates who guess causes before
segmenting are guessing. Expect, roughly in order:

1. **Is it real?** Logging bug, tracking change, data pipeline, seasonality, holiday
2. **Is it everywhere?** Platform, geography, cohort, new vs returning, device,
   app version
3. **When exactly?** Cliff or slide — a cliff means a release or an outage, a slide
   means behavior or competition
4. **What changed on our side?** Release, experiment, pricing, policy
5. **What changed outside?** Competitor launch, platform policy, seasonality, news

Only then hypotheses, and each one should come with how they'd verify it.

**Runnable scenario — release data only when asked:**

> A food delivery app's weekly completed orders dropped 18% versus the prior week.

| Question they might ask | What you tell them |
|---|---|
| Which platforms? | iOS down 31%, Android flat |
| Which regions? | All regions |
| New or existing users? | Existing users down 24%, new users flat |
| Cliff or gradual? | Cliff, single day |
| Any release that day? | iOS app version 8.4 shipped that morning |
| Where in the funnel? | Cart-to-checkout conversion down 40% on iOS |
| Any errors? | Payment SDK error rate on iOS up sharply |

The answer is an iOS payment bug in 8.4. A strong candidate reaches it in five or
six questions, in roughly that order. A weak one starts listing possible causes
before asking anything, or asks about marketing spend before checking platform.

Whatever they conclude, close with: "what would you do in the next hour?" —
mitigation and comms matter as much as diagnosis, and most candidates forget both.

**Measurement questions.** "How would you measure success for X?" Expect one primary
metric (and a defense of why that one), supporting metrics, and — the part people
miss — a **counter-metric**. Shipping something that lifts engagement while tanking
retention is the classic failure a counter-metric catches.

### Estimation

**Format:** "How many X are there in Y?"

The number doesn't matter. Score the decomposition, the stated assumptions, and
whether they sanity-check the result.

- How many people are getting a haircut in this city right now?
- How much revenue does a single airport coffee kiosk make in a year?
- How many rides does a rideshare service do in Chicago on a Tuesday?
- How much storage would you need to hold every photo taken in the US today?

Expect them to write out the structure before computing, state each assumption as an
assumption, use round numbers, and finish with "does that seem right?" — a candidate
who lands on 400 million haircuts a day and doesn't blink has failed the actual test.

### Prioritization

- You have three features, one quarter, and one team. Walk me through how you decide.
- Sales says the biggest customer will churn without feature A. Data says feature B
  helps 40% of users. What do you do?
- How do you say no to your CEO's feature request?

Listen for an explicit framework applied honestly rather than named and abandoned,
for whether they ask about company strategy before ranking anything, and for whether
they can actually say no with a reason rather than deferring.

### Scoring a product round

| Dimension | What a 5 looks like |
|---|---|
| **User insight** | Names a specific user and a real problem before any solution; shows they've thought about behavior, not demographics |
| **Structure** | A stated approach, followed; segmentation before speculation |
| **Metrics rigor** | Primary metric defended, counter-metric named, knows what would falsify their own hypothesis |
| **Tradeoffs** | Options considered, one chosen, cost of the choice acknowledged |
| **Communication** | Concise, signposted, doesn't fall in love with the first idea |

---

## Technical rounds

This skill doesn't run live coding — that needs an editor and a compiler, and a
simulated one builds false confidence. Say so directly if asked, and offer what it
can do well:

**System design**, which is conversational and works fine here. Expect requirements
clarified before any design, explicit assumptions, scale estimated before optimizing,
and bottlenecks named before solutions. "I'd have to look that up" is a better signal
than a confident wrong answer — score it that way.

**Technical depth on their own resume**, which is the highest-signal question
available and the most underused. "Explain [thing from their resume] to someone
non-technical." People who can't explain their own work simply usually didn't do the
thinking themselves.

**Finance technicals**, which are pass/fail on correctness, not graded on structure:

- Walk me through the three statements. Depreciation goes up $10 — what happens to
  each one?
- Walk me through a DCF. What's the biggest lever in the output?
- When would you not use an EBITDA multiple?
- A company has positive net income and negative free cash flow. How?
- Pitch me a stock. Now argue the other side.

A wrong answer is wrong. But *how* someone handles not knowing matters — "I'm not
certain, here's how I'd reason to it" beats a confident fabrication every time, and
that distinction belongs in the debrief.
