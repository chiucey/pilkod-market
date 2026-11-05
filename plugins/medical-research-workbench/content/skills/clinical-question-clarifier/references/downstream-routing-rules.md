# Downstream Routing Rules

Question clarification should end with a recommendation for the next best workflow.

## Route to Biomedical Search Strategy Builder
Use `biomedical-search-strategy-builder` when the clarified question needs database-ready concepts,
controlled vocabulary, synonyms, or Boolean syntax. Query construction is not proof that a live
search ran.

## Route to Evidence Mapping and Gap Finding
Use `topic-evidence-mapper` when the user first needs the field landscape. Route onward to
`medical-research-gap-finder` only when verified retrieval is available or the user supplies adequate
sources; without that evidence, do not declare a formal gap.

## Route to Primary Plan Recommender
Use `primary-plan-recommender` when the user has a defined gap or tightly scoped question and needs
to compare study routes and select a main plan.

## Route to Feasibility-Aware Study Planner
Use `feasibility-aware-study-planner` when the user already has a study concept and needs a realistic
version based on samples, data access, budget, time, laboratory capacity, or team skills.

## Rule
Do not leave the user with a clarified question but no next-step recommendation.
