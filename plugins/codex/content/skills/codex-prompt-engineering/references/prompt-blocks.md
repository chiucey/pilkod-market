# Prompt Blocks

## Core Wrapper

```xml
<task>
Describe the concrete job, the relevant repository or failure context, and the expected end state.
</task>
```

## Output

```xml
<structured_output_contract>
Return exactly the requested output shape and nothing else.
Keep the answer compact and put the highest-value findings first.
</structured_output_contract>
```

```xml
<compact_output_contract>
Keep the final answer compact and structured. Do not include long scene-setting or repeated recap.
</compact_output_contract>
```

## Follow-through

```xml
<default_follow_through_policy>
Default to the most reasonable low-risk interpretation and keep going.
Only stop when a missing detail changes correctness, safety, or an irreversible action.
</default_follow_through_policy>
```

```xml
<completeness_contract>
Resolve the task fully before stopping. Check follow-on fixes, edge cases, and cleanup.
</completeness_contract>
```

```xml
<verification_loop>
Before finalizing, verify the result against the requirements and changed files or tool outputs.
</verification_loop>
```

## Grounding

```xml
<missing_context_gating>
Do not guess missing repository facts. Retrieve them with tools or state what remains unknown.
</missing_context_gating>
```

```xml
<grounding_rules>
Ground every claim in provided context or tool outputs. Label hypotheses as hypotheses.
</grounding_rules>
```

```xml
<citation_rules>
Back important claims with citations or explicit references to inspected source material.
</citation_rules>
```

## Safety

```xml
<action_safety>
Keep changes tightly scoped. Avoid unrelated refactors. Call out risky or irreversible actions first.
</action_safety>
```

```xml
<dig_deeper_nudge>
After the first plausible issue, check second-order failures, empty states, retries, stale state, and rollback paths.
</dig_deeper_nudge>
```
