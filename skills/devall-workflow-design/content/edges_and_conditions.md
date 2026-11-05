---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: ae2dc674acc30b3881d9c9b01da52422
    PropagateID: ae2dc674acc30b3881d9c9b01da52422
    ReservedCode1: 3046022100c2a7ab9204da2db40cf8a798f49bcb3ba1a559c78b192594e1e7f61cc0811df9022100f3eef3d05babe99ed7103091f8f1a4e756ef492dd5611579ac0f9c5d94528b12
    ReservedCode2: 30440220703e962221d52c3b1ef14c59f2c32114bafb170dff725e329645f0bc443966d4022011978b1f6aea659fb3e4892f84900424ebe075607b85a91aea3d5fac54005a79
---

# Edges & Conditions

Edges are not just wires. They carry conditions (filter), processors (transform), and seven flag-fields that control firing, payload delivery, and context state. This is the most-misused part of the platform — read it carefully.

## Edge anatomy

```yaml
- from: <node-name>
  to: <node-name>
  condition: <condition>          # optional; default: always fire
  process: <processor>            # optional; transform the payload before delivery
  trigger: true                   # optional; default true. Whether to fire the receiver
  carry_data: true                # optional; default true. Whether to write the payload into receiver's context
  keep_message: false             # optional; default false. Pin payload against soft resets
  clear_context: false            # optional; default false. Wipe non-pinned messages on receiver before write
  clear_kept_context: false       # optional; default false. Hard-reset (requires clear_context: true)
  dynamic: { ... }                # optional; see execution_model.md
```

## The trigger × carry_data table

The most-overlooked edge configuration. Four combinations, each with a real use:

| trigger | carry_data | Effect | Use |
|---|---|---|---|
| `true` (default) | `true` (default) | Receiver fires; payload in its context | Normal edge |
| `true` | `false` | Receiver fires; payload *not* in context | Rare — used when only the firing matters |
| `false` | `true` | **Context primer** — receiver does *not* fire, payload is in its context | Pervasive in real workflows; see Pattern 15 |
| `false` | `false` | Edge does nothing | Almost always a bug |

**Context primers are not exotic.** Real workflows use them to inject background that another (triggering) edge will then act on. `MACNet_v1.yaml` has 5 priming edges and 1 triggering edge from the same source.

## The context-control trinity

`keep_message`, `clear_context`, `clear_kept_context` form a deliberate four-state authoring tool:

| keep_message | clear_context | clear_kept_context | State |
|---|---|---|---|
| (default) | (default) | (default) | **Append** — normal write |
| `true` | — | — | **Pin** — message survives later soft resets |
| — | `true` | — | **Soft reset** — wipe non-pinned messages on receiver, then write |
| — | `true` | `true` | **Hard reset** — wipe everything on receiver, then write |

`clear_kept_context: true` requires `clear_context: true`. Setting it alone is a config error.

**Typical pattern** for long cycles: pin the user's original task with `keep_message: true` on the entry edge, and use `clear_context: true` on the back-edge so each iteration starts fresh except for the pinned task.

## Conditions

Three forms — all real workflows use the second.

### String shorthand

```yaml
condition: any              # always fire (the default; rarely written explicitly)
condition: code_pass        # python node succeeded
condition: code_fail        # python node failed
condition: "CONTAINS:approve"   # legacy keyword shorthand; structured form preferred
```

### Structured keyword

The form all real workflows use:

```yaml
condition:
  type: keyword
  config:
    any: [APPROVE, ACCEPT]            # fire if ANY of these match
    none: [REVISE, REJECT]            # fire only if NONE of these match
    regex: false                      # treat patterns as regex if true
    case_sensitive: true              # default; matches the agent's exact output
    default: false                    # what to do when no rule fires
```

`any` and `none` can be combined. `default: false` means "if no positive match, don't fire."

**Case sensitivity is the #1 cycle bug.** If the agent might output `Approve` or `APPROVE` interchangeably, either set `case_sensitive: false` or pin the convention in the agent's role prompt.

### Structured function

```yaml
condition:
  type: function
  config:
    name: code_pass                   # registered Python predicate
```

Built-in registered predicates include `code_pass` and `code_fail` (check the prior python node's exit status). Custom predicates are registered via the platform's plugin mechanism (see `field_specs.md`).

### LLM-as-judge

For semantic conditions, an LLM judge can be invoked as a condition. Used sparingly because each judge call is an extra LLM round-trip. Configuration varies by deployment.

## Processors

Transform the payload before delivery to the receiver.

### `regex_extract`

```yaml
process:
  type: regex_extract
  config:
    pattern: "<answer>(.*?)</answer>"
    group: 1                          # capture group; default 0 (full match)
```

Most-used processor. Strip XML/markdown wrappers, extract a structured field, etc.

### `function`

```yaml
process:
  type: function
  config:
    name: code_save_and_run           # registered Python processor
```

Used for sidecar effects during message delivery. `code_save_and_run` extracts code from the upstream message, saves it to the workspace, and queues it for the next python node — typically used on edges entering a `python` node from a code-writing agent.

### `json_path`

```yaml
process:
  type: json_path
  config:
    path: "$.results[*].title"
```

Extract structured fields from JSON-shaped messages. Less common than `regex_extract` in practice.

## Dynamic edges

`dynamic:` configures Map/Tree fan-out. See `execution_model.md` for the full mechanics.

```yaml
# Map: split upstream message, parallel calls
dynamic:
  type: map
  split_by: message            # or 'regex' or 'json_path'
  pattern: "..."               # required for split_by: regex / json_path

# Tree: split, parallel, then hierarchical reduce
dynamic:
  type: tree
  split_by: regex
  pattern: "<chunk>(.*?)</chunk>"
  group_size: 3                # how many to reduce per pass
```

**All dynamic edges into one node must share identical `dynamic` config.** Mixing causes a parse error.

## Common edge bugs

1. `trigger: false` on an edge meant to fire the receiver. The receiver waits forever.
2. Keyword condition with wrong case (`Approve` vs `APPROVE`).
3. `clear_kept_context: true` without `clear_context: true` — config error at parse time.
4. Missing `keep_message: true` on the entry edge in a long cycle — the user's task gets wiped on the first soft reset.
5. Conditions on cycle exit that no agent output ever satisfies — the cycle hits the 100-iteration safety cap.
6. Mixed `dynamic` configs into one node.
7. `process: { type: function, config: { name: <typo> } }` — the registry doesn't have the function, parse error with the registry's enum in the error message.
