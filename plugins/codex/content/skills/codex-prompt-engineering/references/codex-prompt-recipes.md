# Codex Prompt Recipes

## Diagnosis

```xml
<task>
Diagnose why the failing test or command is breaking in this repository. Use repository context and tools to identify the likely root cause.
</task>
<compact_output_contract>
Return: 1. likely root cause 2. evidence 3. smallest safe next step.
</compact_output_contract>
<default_follow_through_policy>
Keep going until there is enough evidence to identify the root cause confidently.
</default_follow_through_policy>
<verification_loop>
Verify that the proposed root cause matches the observed evidence.
</verification_loop>
<missing_context_gating>
Do not guess missing repository facts.
</missing_context_gating>
```

## Narrow Fix

```xml
<task>
Implement the smallest safe fix for the identified issue. Preserve behavior outside the failing path.
</task>
<structured_output_contract>
Return: 1. fix summary 2. touched files 3. verification 4. residual risks.
</structured_output_contract>
<completeness_contract>
Apply the fix and verify it before stopping.
</completeness_contract>
<verification_loop>
Verify the fix matches the task and changed code is coherent.
</verification_loop>
<action_safety>
Avoid unrelated refactors or cleanup.
</action_safety>
```

## Root-Cause Review

```xml
<task>
Analyze this change for material correctness or regression issues using only the provided repository context.
</task>
<structured_output_contract>
Return findings ordered by severity, evidence for each, and brief next steps.
</structured_output_contract>
<grounding_rules>
Ground every claim in repository context or tool outputs; label inferences.
</grounding_rules>
<dig_deeper_nudge>
Check second-order failures, empty states, retries, stale state, and rollback paths.
</dig_deeper_nudge>
```

## Research

```xml
<task>
Research the available options and recommend the best path for this task.
</task>
<structured_output_contract>
Return observed facts, recommendation, tradeoffs, and open questions.
</structured_output_contract>
<research_mode>
Separate observed facts, reasoned inferences, and open questions. Prefer primary sources.
</research_mode>
<citation_rules>
Back important claims with explicit references to inspected sources.
</citation_rules>
```
