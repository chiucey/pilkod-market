# Skill routing

Use the narrowest Skill that matches the user's current decision. Chain Skills only when the output
of one is genuinely needed by the next; do not repeat the same appraisal under several names.

| User need | Route to | Boundary |
| --- | --- | --- |
| Turn a vague clinical or biomedical idea into a bounded question | `clinical-question-clarifier` | Frames the question; it does not answer it or design the full protocol. |
| Construct database queries, controlled vocabulary, synonyms, or database translations | `biomedical-search-strategy-builder` | Designs search syntax; it does not claim that a live search ran. |
| Decide whether one paper deserves deep reading | `high-value-paper-screener` | Produces read/skim/skip triage, not a full critical appraisal. |
| Map a topic's research streams, populations, endpoints, and evidence density | `topic-evidence-mapper` | Describes the landscape; it does not declare formal research gaps. |
| Establish defensible research gaps from retrieved, verified literature | `medical-research-gap-finder` | Requires evidence retrieval or user-supplied sources; no retrieval means no formal gap claim. |
| Deep-read and critically interpret one medical paper | `medical-research-literature-reader-pro` | General paper appraisal; use narrower audit Skills for a single specialized judgment. |
| Classify a paper's study design | `study-design-identifier` | Identifies design type; it does not perform the full reliability audit. |
| Reconstruct a paper's samples, methods, analysis pipeline, and reproducibility gaps | `methods-reverse-engineer` | Rebuilds workflow; it does not invent missing parameters. |
| Audit whether reported results are trustworthy | `result-reliability-checker` | Evaluates design, statistics, bias, and validation as a reliability chain. |
| Check whether a precise claim is actually supported by its cited source | `paper-to-claim-verifier` | Verifies claim-to-source fit, not the whole topic landscape. |
| Explain conflicting findings across multiple studies | `contradictory-findings-resolver` | Requires comparable evidence from at least two studies. |
| Turn a broad aim into a measurable, executable objective | `study-objective-refiner` | Refines the objective; it does not select the entire study route. |
| Compare candidate study routes and recommend the primary plan | `primary-plan-recommender` | Selects a route before detailed protocol engineering. |
| Redesign a study around real sample, time, budget, data, and team constraints | `feasibility-aware-study-planner` | Produces a minimum viable study under explicit constraints. |
| Operationalize primary, secondary, and exploratory endpoints | `endpoint-definition-designer` | Defines endpoint rules, timing, and interpretation. |
| Plan confounder control and bias mitigation | `confounder-and-bias-control-planner` | Owns variable roles, adjustment logic, and bias sensing. |
| Plan sample size and power from explicit assumptions | `sample-size-and-power-planning-assistant` | Does not invent an exact sample size when inputs are missing. |
| Design internal, external, functional, or robustness validation | `validation-strategy-designer` | Owns validation architecture, not primary endpoint or power calculation. |

A typical end-to-end flow is question clarification → search strategy → screening/evidence mapping →
gap analysis or paper appraisal → objective/route selection → feasibility, endpoint, bias, power, and
validation planning. Skip any stage the user has already completed with adequate evidence.
