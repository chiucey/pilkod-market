---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8f5e5f3c1e6f131470ec6498f90e15a9
    PropagateID: 8f5e5f3c1e6f131470ec6498f90e15a9
    ReservedCode1: 30450220438ccd6c098ce0afac433d49f4b880e50878f0872987d58412adeee0576c3c08022100bc4b0592b1a908a0ec50a534a96f25b2e2e669b71701ce78f11d623095d85bbf
    ReservedCode2: 30440220395f22fd50709df03d9e25791b785a738f1616d099ab057213b403b7c8700e98022010f14f5c13e1acbe6535dfa5e3bfc5370d437a3036f87c6ce89707296fc6fec3
---

# Thinking Module

Reasoning enhancement applied per agent. An extra LLM round-trip (or several) before or after generation.

## When to use it

`thinking: reflection` adds an extra LLM pass that critiques or refines the agent's response. Use sparingly — it doubles or triples the cost of each generation. Apply only to:

- Final-answer agents whose output is user-facing.
- Critical decision agents whose output gates a major branch.
- Agents that consistently produce subtly wrong outputs that a self-critique catches.

If the question is "should I add thinking to this agent?", the answer for non-critical subagents is usually no.

## `reflection` mode

```yaml
nodes:
  - name: Decider
    type: agent
    config:
      provider: anthropic
      name: claude-sonnet-4-5-20250929
      role: "Make the final call."
      thinking:
        type: reflection
        config:
          stage: after_generate          # or 'before_generate'
          # max_iterations, custom prompts, etc.
```

`stage: before_generate` thinks about the problem before answering — useful when the agent needs to plan.

`stage: after_generate` critiques its own output and revises — useful for catching subtle errors.

## Custom modes

The platform supports registering custom thinking modes via `register_thinking_mode`. See `field_specs.md` if you're extending the platform; as a workflow author, you'll typically use the built-in `reflection`.

## Cost note

A single `thinking: reflection` agent costs roughly 2× a normal agent (one extra LLM call). If `max_iterations` is configurable on the thinking config and set above 1, multiply accordingly.

When optimizing for cost, the first thing to remove is reflection from non-critical agents.
