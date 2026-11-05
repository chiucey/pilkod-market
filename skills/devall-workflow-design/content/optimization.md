---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f058b87009a9df77c065062b4458ec44
    PropagateID: f058b87009a9df77c065062b4458ec44
    ReservedCode1: 3046022100def8563e19c118d9855cb98fba7734afab01ecb3e08a546acad07fc11dce9468022100fce824be747d6657d97f44b70effc37f39d779ee5e6996769f45b99c405ba1ce
    ReservedCode2: 30450220530e87a1a340b318ac6e07f56a71aec9e05dc42f80fcc0e38424adca2e08b169022100bc4a516efb7cbd27b9895d8d9431dc688a9cf9350fa8a2c4a97cc11127a0f565
---

# Optimization Playbook

How to improve a working workflow without breaking it. Goal: reduce cost, latency, or output variance.

## Pre-flight: measure before you change

Don't optimize blind. For the current workflow, note:

- **Total tokens per run** (sum the model usage across all agent nodes — observable on the WebSocket via `node_end` events that include usage).
- **Wall-clock duration** (start to end-event time).
- **Quality** — either subjective ("is the output good?") or rubric-based on a small fixed eval set.
- **Failure rate** over N runs (how often does the workflow not produce a usable output?).

Even back-of-envelope numbers turn "this feels slow" into "the reviewer is 4× the writer's tokens" — which immediately points at the optimization target.

## The five optimization levers

In rough order of impact-per-effort.

### 1. Model swap on subagents

The single biggest lever. Subagents whose output gets summarized or aggregated downstream often don't need the most-capable model.

```yaml
# Before
- name: WorkerN
  type: agent
  config:
    provider: anthropic
    name: claude-opus-4-7              # expensive
    role: "Process item N."

# After
- name: WorkerN
  type: agent
  config:
    provider: anthropic
    name: claude-haiku-4-5-20251001    # cheaper, faster, often good enough
    role: "Process item N."
```

Combine with `vars: { WORKER_MODEL: claude-haiku-4-5-20251001, FINAL_MODEL: claude-opus-4-7 }` so you can swap easily during evaluation.

**Risk**: output drift. Verify with side-by-side runs on a fixed input set; revert if quality degrades meaningfully.

### 2. Context window cap

By default agents see all upstream messages (`context_window: 0` or `-1`). In long cycles, this means each iteration's prompt grows linearly. Cap it:

```yaml
config:
  context_window: 10                   # only the last 10 messages
```

**Risk**: lost context on iteration N+1. If the agent needs to "remember" earlier decisions, either keep the window large or pin specific messages with `keep_message: true` upstream.

### 3. Context-control flags on cycle back-edges

The most surgical lever for cycles. Default: every iteration adds to the context. With a soft reset on the back-edge, the agent re-starts each iteration with only the pinned task + the new payload.

```yaml
edges:
  # Pin the user's task
  - { from: User, to: Writer, keep_message: true }

  # Back-edge resets non-pinned context
  - from: Reviewer
    to: Writer
    condition: { type: keyword, config: { any: [REVISE] } }
    clear_context: true
```

**Risk**: pin too aggressively → no learning across iterations. Pin only the user task, not intermediate drafts.

### 4. Map → Tree fan-out instead of sequential loop

If the work is genuinely parallel (per-document, per-chunk, per-test-case), a Map fan-out is faster than iterating a single agent through a list — even though the total token count is similar.

```yaml
# Before — sequential loop with a counter
- name: Worker
  type: agent
  ...
edges:
  - { from: Splitter, to: Worker }
  - { from: Worker,   to: Splitter, ... back-edge with counter ... }

# After — Map fan-out
edges:
  - from: Splitter
    to: Worker
    dynamic: { type: map, split_by: message }
```

**Risk**: the reduce step (Tree) adds tokens. Map alone usually wins; Map-then-Tree wins for N≥3 items.

### 5. Memory promotion

Information that's re-derived every run can be precomputed into a `file` or `simple` store. Example: a research agent that reads a fixed corpus on every run is better served by a `file` memory store than by web fetches.

```yaml
graph:
  memory:
    - name: corpus
      type: file
      config:
        path: ./reference_docs/
        embedding: { ... }
nodes:
  - name: Researcher
    type: agent
    config:
      memories:
        - { name: corpus, retrieve_stage: before_generate, top_k: 5, read: true, write: false }
```

**Risk**: stale memory if the corpus changes. Manage by re-indexing on a schedule or using `simple` with a write strategy.

## The three cost traps

Things that look fine but burn tokens disproportionately.

### Trap 1: Reviewer agents reading full history every iteration

If a critic re-reads the entire conversation each cycle, costs scale quadratically. The fix is either a sliding `context_window` or `clear_context: true` on the back-edge:

```yaml
edges:
  - from: Writer
    to: Reviewer
    clear_context: true
    keep_message: false                # reviewer sees only the latest draft
```

### Trap 2: `module:All` when one tool would do

Each tool registration adds JSON schema to the system prompt. `file:All` might add 8 tools when you only need `read_file`. Audit and trim if cost matters:

```yaml
tooling:
  type: function
  functions:
    - file:read_file                   # specific instead of file:All
    - web:fetch_url
```

### Trap 3: Reflection on every agent

`thinking: reflection` doubles the cost of an agent. Removing it from non-critical agents is often a 30–50% cost reduction with no quality loss.

Apply reflection only to: final-answer agents, critical decision points, and agents whose output gates a major branch.

## The optimization loop

1. **Pick the lever** with the largest expected delta. Usually #1 (model swap on subagents) or #5 (eliminate redundant work via memory).
2. **Apply to one node at a time.** Don't swap five things and try to attribute results.
3. **Re-run on a fixed input set**, 3+ runs to see variance. Cycle-bearing workflows are noisy; one run isn't enough.
4. **Compare quality.** Use a small rubric: did the output answer the question, was it accurate, was it well-structured?
5. **Revert if degraded.** Keep the original YAML in version control.
6. **Measure cost / latency / quality together.** A 50% cost reduction with 40% quality drop isn't a win.

## When optimization doesn't help

- If the workflow's slowest step is a single critical agent, no amount of restructuring around it will help. Either pick a faster model for that agent or accept the latency.
- If quality is the bottleneck, optimization usually trades quality for cost — the wrong direction. Improve the workflow's prompts, sidecars, or topology instead.
- If failure rate is high, fix the failures first (see `debugging.md`). An optimized but flaky workflow is worse than a slow reliable one.
