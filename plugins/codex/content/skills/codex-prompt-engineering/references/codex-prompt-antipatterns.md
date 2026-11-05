# Codex Prompt Anti-Patterns

## Vague task framing

Bad: `Take a look at this and let me know what you think.`

Better:

```xml
<task>Review this change for material correctness and regression risks.</task>
```

## Missing output contract

Bad: `Investigate and report back.`

Better: explicitly request root cause, evidence, and smallest safe next step.

## No follow-through default

Bad: `Debug this failure.`

Better: tell Codex to keep going until it has enough evidence to identify the root cause.

## Asking for more reasoning instead of a better contract

Bad: `Think harder and be very smart.`

Better: require a verification loop against evidence and task requirements.

## Mixing unrelated jobs

Review first, then run a separate fix prompt, then handle docs or roadmap work separately.

## Unsupported certainty

Do not ask for certainty that the evidence cannot support. Require hypotheses to be labeled and claims to be grounded in inspected sources.
