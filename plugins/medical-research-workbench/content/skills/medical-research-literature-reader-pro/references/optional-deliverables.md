# Optional Deliverables

This file defines the extra output formats available within the literature-reader Skill. They are
not separate Marketplace Plugins. Load this file when the user requests a specific deliverable or
when offering deliverable suggestions at the end of a report.

**Activation rule:** Offer deliverables when genuinely useful. Do not auto-generate every
deliverable after every report. Select 1–3 that are most relevant to the paper type and user context.

**Evidence rule:** Every factual paper, trial, accession, reagent, software, parameter, dose, and
resource claim must come from the supplied paper or a source that was actually retrieved and
verified. Mark missing details as unknown. Never fill gaps from memory or plausible-looking values.

## Contents

- [Literature mind map](#literature-mind-map)
- [Same-type comparison table](#same-type-comparison-table)
- [Journal club discussion kit](#journal-club-discussion-kit)
- [PI decision brief](#pi-decision-brief)
- [Follow-up experiment designer](#follow-up-experiment-designer)
- [Bioinformatics replication starter](#bioinformatics-replication-starter)
- [Figure interpretation mode](#figure-interpretation-mode)
- [Grant / project inspiration generator](#grant--project-inspiration-generator)

---

## Deliverable Catalogue

### Literature Mind Map
**Purpose:** Structure the paper as a visual knowledge map.
**Output format:**
```
Background → Research Gap → Research Question
    ↓
Methods → Dataset / Design / Tools
    ↓
Key Findings (3–5 nodes)
    ↓
Interpretation → Strengths / Weaknesses
    ↓
Next Steps → Open Questions
```
**Best for:** Complex multi-section papers; users preparing seminar presentations; onboarding
team members to a new topic.

---

### Same-Type Comparison Table
**Purpose:** Compare the current paper with 3–5 related studies in a structured table.
**Output columns:** Title · Disease · Design · Dataset/Sample · Key Method · Main Conclusion ·
Validation Level · Key Strength · Key Weakness
**Best for:** Grant background sections; systematic literature positioning; understanding how
a paper fits into the evidence base.

Use only verified related studies. If retrieval is unavailable, build the table from user-supplied
papers or provide an empty comparison template; do not invent comparable papers.

---

### Journal Club Discussion Kit
**Purpose:** Prepare a complete structured kit for presenting the paper at journal club.
**Output sections:**
1. Background opener (2–3 sentences to set clinical/scientific context)
2. Three key findings (concise, accurate, in plain language)
3. Three strengths (specific to design, data, or analysis)
4. Three concerns (methodological, interpretive, or translational)
5. Five discussion questions (genuinely research-grade, not generic)
6. One-sentence take-home message
**Best for:** Journal club preparation; lab meeting presentations; teaching rounds.

---

### PI Decision Brief
**Purpose:** Short strategic memo for a PI or team leader evaluating whether a paper matters
to their research programme.
**Output sections:**
1. What this paper claims (one paragraph)
2. How strong is the evidence? (one verdict sentence)
3. Does it change our thinking? (yes/no + one sentence)
4. Should we replicate it? (yes/no/partially + reason)
5. Can it inspire a project? (specific angle if yes)
6. Recommended action (read/file/discuss/replicate/ignore)
**Best for:** Lab leadership; grant strategy; research prioritisation.

---

### Follow-Up Experiment Designer
**Purpose:** Generate a concrete set of next-step experiments to validate, extend, or challenge
the paper's findings.
**Output sections:**
1. The weakest link in the current paper (one sentence)
2. The single highest-priority experiment to run (with rationale)
3. 3–5 additional experiments ranked by impact
4. For each experiment: system, readout, expected result if hypothesis holds, expected result if it does not
5. Translational extension suggestions (if applicable)
**Best for:** Research teams considering follow-up studies; grant proposal ideation.

Do not invent safety-critical or execution-critical details such as doses, reagent catalogue
numbers, assay conditions, model availability, sample access, or institutional capacity. Where such
details are not reported or user-confirmed, state the uncertainty and route the design through
appropriate ethics, biosafety, and institutional review.

---

### Bioinformatics Replication Starter
**Purpose:** Provide a pipeline specification for replicating or extending the computational
analysis.
**Output sections:**
1. Data sources (GEO accession numbers, TCGA project IDs, access method)
2. Pipeline steps in order (tool → parameters → expected intermediate output)
3. Key checkpoints (where results should match the paper's reported figures)
4. Likely failure points (preprocessing decisions, package version sensitivity, parameter sensitivity)
5. Validation priorities (which results are most important to replicate first)
6. Extensions (what the paper did not do that is computationally feasible)
**Best for:** Bioinformaticians replicating published analyses; lab onboarding; methods sections.

Include accessions, project IDs, tools, versions, parameters, and checkpoints only when they appear
in the paper or supplement or were independently verified. Label each missing item as unknown and
do not imply that data access or execution was tested.

---

### Figure Interpretation Mode
**Purpose:** Provide rigorous, accessible interpretation of the paper's key figures.
**For each figure:**
1. What the figure shows (one sentence)
2. What the authors claim it shows
3. Whether the data support that claim (and why / why not)
4. Any display or statistical concerns (axis manipulation, cherry-picked representative images,
   missing error bars, multiple comparison issues)
5. The figure's actual contribution to the paper's central argument
**Best for:** Trainees learning to read papers critically; peer reviewers; replication planning.

---

### Grant / Project Inspiration Generator
**Purpose:** Translate a paper's findings and gaps into actionable research directions.
**Output sections:**
1. The most important unresolved question this paper opens (one sentence)
2. Three specific research gaps with brief rationale
3. Strongest validation route for each gap (design suggestion)
4. Translational extension angles (biomarker, therapeutic, diagnostic)
5. Therapeutic angles if applicable (target class, intervention type, patient population)
6. Suggested grant framing (one paragraph)
**Best for:** Grant writing; new project ideation; PhD topic development.

Treat proposed gaps and therapeutic angles as hypotheses unless
`medical-research-gap-finder` established them from verified retrieval. Do not present an idea as a
confirmed field gap, clinical opportunity, or feasible project without the corresponding evidence
and resource checks.
