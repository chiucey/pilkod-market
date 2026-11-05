---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 7aa29c9bb77c94fedd835b6bffa67dfe
    PropagateID: 7aa29c9bb77c94fedd835b6bffa67dfe
    ReservedCode1: 3045022100fa73abb4586f9bed45d7555434f905f87e5a05dd064be99ea199f3007dfe185802203ee48bcc5ef941bf20ef3d2e9fcc9ced01182bb1f0b0b168d544091e5b57b50d
    ReservedCode2: 3046022100842e5b6de89b5f2682ab3d4c5b2dd269ad8f10f69c0440173eec1696eaf259bd022100a4bbf2f546495f55af8c25bc2ea94b00b64270f48751452526f1ea491827b993
description: Design, write, optimize, and debug DevAll multi-agent workflow YAML files. Use this skill whenever the user mentions DevAll, multi-agent workflows, agent orchestration, workflow YAML, agent graphs, agent DAGs, agent pipelines, or anything involving graph-shaped execution of LLM agents with memory / thinking / tooling sidecars — including requests to draft a new workflow from a description, turn a process into agent steps, review or fix an existing workflow YAML, debug why a workflow won't run or produces the wrong output, or optimize a working workflow for cost, latency, or quality. Trigger this skill for any task that involves authoring or modifying graph-shaped agent workflows even when the user doesn't say "DevAll" explicitly — phrases like "multi-agent workflow", "agent DAG", "agent pipeline YAML", "orchestrator agent", "workflow with cycles", "fan-out agents", "writer-critic loop", "review my workflow YAML", or any reference to a `.yaml` file containing `graph:` / `nodes:` / `edges:` all warrant this skill.
name: devall-workflow-design
---

# DevAll Workflow Design

A skill for **designing, writing, optimizing, and debugging** DevAll multi-agent workflow YAML files. DevAll is a multi-agent workflow orchestration backend that executes YAML-defined directed graphs (with cycle support) over a shared message context, with FastAPI scheduling, WebSocket observability, and per-session asset storage under `WareHouse/<session>/`.

This SKILL.md is the operational entry point. It teaches the **mental model**, gives you the **decision tools** for each lifecycle phase, and points to deeper material in `references/`.

---

## When you arrive at this skill

The user is doing one of four things. Identify which, and follow the matching section below.

| If the user is… | Go to | Most relevant references |
|---|---|---|
| Starting a new workflow from a description | **§3 DESIGN** | `pattern_gallery.md` |
| Translating a finished design into YAML | **§4 WRITE** | `yaml_and_nodes.md`, `edges_and_conditions.md` |
| Improving a workflow that already works | **§5 OPTIMIZE** | `optimization.md` |
| Fixing a workflow that's broken or wrong | **§6 FIX** | `debugging.md`, `execution_model.md` |

Don't skip §1 and §2 — they establish the vocabulary every other section uses.

---

## §1 Mental model

A DevAll workflow is **one YAML file** with three top-level keys:

```yaml
version: "0.4.0"     # schema version
vars: { ... }        # parameters resolved before parsing (highest priority)
graph:               # the actual workflow
  id: my-workflow
  nodes: [ ... ]     # the typed work-units
  edges: [ ... ]     # the wires between them
  start: [ ... ]     # entry node(s) — accepts list or scalar
  end: [ ... ]       # exit / publishing node(s) — accepts list or scalar
  memory: [ ... ]    # optional memory store declarations (shared across nodes)
```

Authoring reduces to four interlocking decisions:

1. **Topology** — which typed nodes (8 kinds) and how they're wired.
2. **Execution shape** — DAG, cycle, or dynamic (Map / Tree). These three are orthogonal mechanisms; pick deliberately.
3. **Agent enrichment** — which sidecars (memory, thinking, tooling, project skills) attach to each agent node.
4. **Variable plumbing** — what's in `vars` (parameterization + prompt templating) vs. what's hardcoded.

**The crucial mental model**: every node consumes `List[Message]` from its incoming edges and emits `List[Message]` onward. Edges aren't just wires — they carry conditions (filter), processors (transform), trigger flags (fire-or-not), carry_data flags (write-into-context-without-firing), and three context-control flags (`keep_message`, `clear_context`, `clear_kept_context`). Cycles are just edges that loop back; dynamic execution is just edges that fan out / reduce. Memory/thinking are sidecars on agent message consumption/production. Hold that picture and the rest is detail.

---

## §2 Vocabulary you'll use everywhere

Before any phase, lock in these terms. They appear in every reference file.

- **Node types**: `agent` (LLM call), `python` (script run in shared `code_workspace/`), `human` (UI prompt), `subgraph` (nested workflow, inline `type: config` or referenced `type: file`), `passthrough` (last-message filter / wire helper), `literal` (static prompt injection), `loop_counter` / `loop_timer` (bounded-loop guards).
- **Edge mechanics**: `condition` (gate the edge), `process` (transform messages), `trigger: false` (write into context without firing), `carry_data: true` (used with `trigger: false` to actually carry the payload), `keep_message: true` (pin against soft resets), `clear_context: true` (soft reset on receiver), `clear_kept_context: true` (hard reset, requires `clear_context: true`).
- **Conditions**: `condition: any` shorthand for "always fire"; `keyword` (string-match agent output, supports `any` / `none` / `regex` / `case_sensitive` / `default`); `function` (call a registered Python predicate, e.g. `code_pass` / `code_fail` for python-node status); `regex_extract` (also a processor); LLM-as-judge.
- **Three execution shapes**: **DAG** (default, topological-layer parallelism), **cycle** (any edge loops back; engine detects via Tarjan, abstracts cycle into a super-node, picks a unique entry), **dynamic** (`dynamic.type: map` to fan out, `dynamic.type: tree` to fan out then reduce in groups of `group_size`).
- **Agent sidecars** (all live under `node.config`): `memories[]` (attach declared stores), `thinking` (reasoning enhancement, currently `reflection`), `tooling` (one of `function` / `mcp_remote` / `mcp_local`), `skills` (project-level Markdown skills under `.agents/skills/` — disambiguation: this is *not* the Anthropic-style skill you're authoring with).
- **Memory stores** (declared once at `graph.memory[]`, attached per-node): `simple` (FAISS + rerank, conversational), `file` (read-only document index), `blackboard` (append-only shared log).
- **Tooling modes**: `function` (in-repo Python, `_context` parameter is auto-injected and gives access to `attachment_store`, `python_workspace_root`, `graph_directory`); `mcp_remote` (HTTP MCP server with `server` URL + `headers` + `timeout`); `mcp_local` (stdio MCP process with `command` + `args` + `cwd` + `env` + `wait_for_log` + `startup_timeout`).
- **Variable resolution priority**: `vars:` block > shell env > `.env` file. Unresolved → `ConfigError` at parse time, with the YAML path as an error path.
- **The session workspace**: `WareHouse/<session>/code_workspace/` is shared across the python node, the function-tool `_context.python_workspace_root`, and the attachment store. Anything written there is auto-promoted to a downloadable artifact via `WorkspaceArtifactHook`.

---

## §3 DESIGN — turning a description into a graph

Goal: end with an architecture sketch (nodes, edges, execution shape) that you'll then write up in §4. Don't open YAML yet.

### Step 1: Choose a base pattern

`references/pattern_gallery.md` documents **19 named patterns** with copy-pasteable skeletons keyed to their source demos. It's the design encyclopedia — read it whenever the user's intent maps recognizably onto a known shape.

The patterns split into two tiers:

**Building-block patterns (1–7)** — small, composable shapes you'll combine:

| # | Pattern | When to reach for it |
|---|---|---|
| 1 | Linear pipeline | A → B → C, single owner per step |
| 2 | Writer–critic loop | Iterative refinement with explicit reviewer; bounded by `loop_counter` or keyword exit |
| 3 | Writer–critic–editor fan-in | Same as 2, plus an editor that gets *both* the original and the revised drafts (A→B→C plus A→C) |
| 4 | Map fan-out | Same task, many inputs, parallel agent calls; needs a list-shaped upstream message |
| 5 | Map-then-Tree (fan-out then reduce) | Per-item work + hierarchical summarization; the canonical large-corpus pipeline |
| 6 | Bounded loop with guard | Any cycle that must terminate by step count or wall time; the `loop_counter`/`loop_timer` four-edge topology |
| 7 | Subgraph encapsulation | Reusable sub-workflow; inline (`type: config`) or referenced (`type: file`) |

**Production patterns (13–19)** — what real applications use:

| # | Pattern | When to reach for it |
|---|---|---|
| 13 | Orchestrator / Hub | Central agent makes routing decisions via tokenized output; workers report back. Scales beyond cycles. |
| 14 | Switch-case routing on tokenized output | Agent emits `NEXT_STEP: X`; downstream edges keyword-condition on the token. Building block of 13. |
| 15 | Context primer | `trigger: false + carry_data: true` to put background into a node's context without firing it |
| 16 | Multi-instance subgraph network | Same subgraph file instantiated as N nodes wired in feedforward layers (MACNet-style) |
| 17 | Phase-prompt literals + per-phase loop counters | Multi-phase pipelines (e.g., ChatDev) where each phase has its own prompt literal and iteration cap |
| 18 | Department / team with token-tagged dispatch | Upstream decomposer fans out to role-specialized departments; reduces through a Summary department |
| 19 | Code-execution gating | `code_pass`/`code_fail` function conditions for retry loops on python-node failures |

Patterns 8–12 are intermediate compositions in the gallery (cycle-with-exit, parallel committees, context-reset variants, etc.). When a user's intent feels novel, scan the gallery first — odds are 8 of every 10 cases match an existing pattern with minor adjustments.

### Step 2: Choose the execution shape

This is the most over-thought decision. Use this tree:

```
Need to do the same work many times in parallel?
├─ Yes → Dynamic execution
│        ├─ Just process each item independently? → Map (dynamic.type: map)
│        └─ Process each item AND combine results? → Map-then-Tree (Pattern 5)
│           or single Tree if upstream already gives a list (dynamic.type: tree)
└─ No → Need iteration / refinement / "keep going until …"?
        ├─ Yes → Cycle (just write the back-edge with a condition)
        │        └─ Need a hard limit? → Add a loop_counter or loop_timer (Pattern 6)
        └─ No → Plain DAG. Topological layers, no special configuration needed.

Need centralized state-machine routing across many workers?
└─ Orchestrator/Hub (Pattern 13). Not a cycle in the normal sense — it's a switch-case
   in an agent's output, with workers reporting back.
```

**Don't combine cycle + dynamic on the same edge.** If you need both, put the dynamic execution inside a subgraph and cycle on the subgraph node (Pattern 16 essentially does this).

### Step 3: Place agent enrichments

For each agent node, decide:

- **Memory** — needed only when the agent must recall *across runs* or *across cycle iterations* in a way the message context can't carry. Use `simple` for conversation memory, `file` for read-only document corpora (RAG), `blackboard` for append-only shared notes. Default: no memory.
- **Thinking** — `reflection` adds an extra LLM pass (before or after generation). Worth it for high-stakes agents (final answer, critical decision) where one extra call's cost is acceptable. Default: no thinking.
- **Tooling** — a node can have at most one `tooling` block. Pick `function` for in-repo Python tools (file ops, code execution, web fetch), `mcp_remote` for HTTP MCP servers (Notion, GitHub, etc.), `mcp_local` for stdio MCP processes (filesystem, custom local tools). Use `module:All` shorthand for bulk import (`file:All`, `web:All`, `code_executor:All`, …) — this is the dominant style in production workflows.
- **Project skills** — if the deployment has a `.agents/skills/` directory with relevant skills, list them in `config.skills`. The runtime exposes them via `activate_skill` + `read_skill_file` built-in tools. Skills with `allowed-tools:` frontmatter that mention tools not bound to this node are silently dropped.

### Step 4: Sketch the topology

Produce, before writing YAML, a list:
- Each node with its type, role, and any sidecars
- Each edge as `from → to` with condition / trigger / processor (if non-default)
- The execution shape annotation per region (DAG / cycle / dynamic)
- The variables to expose in `vars:` (model name, common preamble, anything an operator might want to swap)

Show this sketch to the user before writing YAML. Two minutes here saves twenty minutes of edits later.

---

## §4 WRITE — turning a sketch into runnable YAML

Goal: produce a YAML that parses, validates, and runs.

### The minimum viable skeleton

```yaml
version: "0.4.0"
vars:
  MODEL_NAME: "claude-sonnet-4-5-20250929"
graph:
  id: my-workflow
  start: [Entry]
  end: [Result]
  nodes:
    - name: Entry
      type: passthrough
    - name: Worker
      type: agent
      config:
        provider: anthropic
        name: ${MODEL_NAME}
        role: "You are a helpful assistant."
        context_window: 0
    - name: Result
      type: passthrough
  edges:
    - { from: Entry, to: Worker }
    - { from: Worker, to: Result }
```

### The fields you'll actually configure

For full per-node-type field tables, see `references/yaml_and_nodes.md`. The most common decisions:

- **Agent**: `provider` + `name` + `role` are the prompt setup. `context_window` controls how many recent messages are sent (`0` or `-1` = unbounded; positive integer = sliding window). `input_mode: messages` is the default. `temperature`, `top_p`, `seed` are passed through to the provider.
- **Python**: `script` is the file path relative to the workflow file. The script's stdout becomes the node's output Message. Optional: `interpreter` (path to a specific Python), `args` (list), `env` (extra env vars), `encoding` (default utf-8). All python nodes in one execution share `code_workspace/`.
- **Literal**: `content` is the static text, `role` is `user` / `assistant` / `system` (default `user`). The role *matters* — `user` injects as a user turn, `assistant` injects as conversation history, which changes downstream agent behavior.
- **Loop_counter**: `max_iterations` (integer, default 100). Loop_timer: `max_duration` (number) + `duration_unit` (`seconds` / `minutes` / `hours`). Timer starts on first trigger, not at workflow start.
- **Subgraph**: either `subgraph: { type: config, graph: { ... } }` (inline) or `subgraph: { type: file, path: ./other.yaml }` (referenced). Vars cascade from parent. Don't nest circularly.
- **Human**: `prompt` for the question, optional `attachments_allowed: true` to allow file uploads in the UI.

### Edges — the most-misused part of the platform

Read `references/edges_and_conditions.md` for full mechanics. The four things authors get wrong:

1. **The trigger × carry_data table** — `trigger: false + carry_data: true` is the **context primer** (Pattern 15). It puts the message into the receiver's context but does not fire the receiver. Real workflows use this pervasively to inject background. The other three combinations are: default (`true`/`true`-ish, fire and carry), `trigger: true + carry_data: false` (fire without carrying — rare), and `false`/`false` (do nothing — usually a bug).
2. **The context-control trinity** — `keep_message`, `clear_context`, `clear_kept_context` form a four-state model: pin / soft-reset / hard-reset / default. Pin a message with `keep_message: true` so it survives soft resets (typical for the user's original task); use `clear_context: true` on an edge to wipe non-pinned context on the receiver before writing the new message; add `clear_kept_context: true` for a hard reset that wipes everything. These are crucial in long cycles where context bloat degrades quality.
3. **Conditions have three forms**:
   - String shorthand: `condition: any`, `condition: code_pass`, `condition: code_fail`.
   - Structured keyword: `condition: { type: keyword, config: { any: [APPROVE], none: [], regex: false, case_sensitive: true, default: false } }` — the form all real workflows use.
   - Structured function: `condition: { type: function, config: { name: code_pass } }`.
4. **Processors transform the payload before delivery**:
   - `process: { type: regex_extract, config: { pattern: "<answer>(.*)</answer>" } }` — extract a substring.
   - `process: { type: function, config: { name: code_save_and_run } }` — run a registered Python processor (e.g., save extracted code and execute it as a sidecar to delivery).

### Tooling YAML

```yaml
# Function tooling (in-repo)
config:
  tooling:
    type: function
    functions:
      - file:All           # bulk import — sorted ahead of concrete entries in pickers
      - web:fetch_url      # specific entry
      - code_executor:All

# Remote MCP
config:
  tooling:
    type: mcp_remote
    server: https://my-mcp.example.com/sse
    headers: { Authorization: "Bearer ${MCP_TOKEN}" }
    timeout: 30

# Local MCP (stdio)
config:
  tooling:
    type: mcp_local
    command: uvx
    args: [my-mcp-server]
    cwd: ${WORKSPACE}        # session workspace; runtime-injected
    env: { LOG_LEVEL: info }
    inherit_env: true
    wait_for_log: "Server ready"
    startup_timeout: 30
```

`tooling:` is a **single object** per node (not a list). A node has at most one tooling block; combine tools by listing many `functions:` entries within one block.

### Variables — two distinct uses

`vars:` does two jobs in real workflows:

- **Parameterization** — `MODEL_NAME`, API keys, URLs. Easy to swap per environment.
- **Prompt templating (DRY)** — `COMMON_PROMPT: "ChatDev is a software company..."` referenced inside many agents' `role:` strings as `${COMMON_PROMPT}`. Don't paste the same preamble across 12 agents.

### Validate before running

Use the schema-validate endpoint and the schema-inspector CLI (see `references/config_schema.md`) for pre-flight validation:

- `POST /api/config/schema/validate` with the YAML body returns `{valid: true}` or `{valid: false, error, path}`. The path is a JSON-pointer-like array, e.g. `["workflow", "nodes", 3, "config", "memories"]` — copy the field at that path and re-check it against the reference doc.
- `python run.py --inspect-schema --schema-breadcrumbs DesignConfig.graph.nodes.NodeConfig.config` returns the schema the parser expects at any point in the tree. Use this when an error message mentions a class name you don't recognize.

---

## §5 OPTIMIZE — improving a workflow that already works

Goal: reduce cost, latency, or output variance — without breaking what works.

`references/optimization.md` has the full playbook. Quick orientation:

### Pre-flight: measure before you change

Don't optimize blind. Note the current run's: total tokens (sum across nodes), wall-clock duration, observed quality (subjective or rubric-based), failure rate over N runs. Even back-of-envelope numbers turn "this feels slow" into "the reviewer is 4× the writer's tokens."

### The five optimization levers

| Lever | When | Risk |
|---|---|---|
| **Model swap** (cheaper / faster model on non-critical agents) | Subagents whose output is summarized later, or whose quality bar is low | Output drift; verify with side-by-side runs |
| **Context window cap** (`context_window: N` instead of `0`) | Long cycles, agents that don't need full history | Lost context on iteration N+1 |
| **Context-control flags** (`clear_context` / `keep_message`) | Cycles where intermediate iterations bloat the prompt | Pin too aggressively → no learning across iterations |
| **Map → Tree fan-out** instead of sequential loop | The work is genuinely parallel (per-document, per-chunk) | Reduce step adds tokens; only wins when N≥3 |
| **Memory promotion** | Information re-derived every run; convert to a `file` or `simple` store | Stale memory if the corpus changes; manage write strategy |

### The three cost traps

1. **Reviewer agents using full history every iteration**. If a critic re-reads the entire conversation each cycle, the back-edge should `clear_context: true` and only carry the new draft.
2. **Tooling with `module:All` when one tool would do**. Each tool registration adds to the system prompt. Audit and trim if cost is a concern.
3. **Reflection on every agent**. `thinking: reflection` doubles the cost of each generation. Apply it only to nodes whose output is final or critical.

### The optimization loop

1. Pick the lever with the largest expected delta (usually model swap on subagents).
2. Apply to one node at a time.
3. Re-run on a fixed set of inputs (3+ runs to see variance).
4. Compare quality; revert if degraded.

---

## §6 FIX — debugging a broken or misbehaving workflow

Goal: identify *exactly* what's wrong and apply a minimal fix.

`references/debugging.md` has the full playbook with annotated failure modes. Quick orientation:

### Diagnose by symptom

| Symptom | Likely cause | First check |
|---|---|---|
| `ConfigError` at parse time | Variable unresolved, schema mismatch, unknown `type:` | The error's `path` array points at the exact field |
| Workflow starts but a node never fires | All incoming edges have failing conditions, or only `trigger: false` edges | Check edge conditions; ensure at least one triggering edge |
| Cycle never exits | No exit-edge condition matches, max_iterations not set, loop guard not wired correctly | Verify the four-edge bounded-loop topology (Pattern 6) |
| Agent gets the wrong context | Missing context primer, or `clear_context` wiping needed history | Trace the edges into the node; check trigger × carry_data and the context-control trinity |
| Dynamic edge fails | Mixed `dynamic` configs into one node, or splitter mismatch (regex doesn't match the message) | All dynamic edges into a node must share identical `dynamic` config |
| Code-execution branch always misroutes | Wrong condition function (`code_pass` vs `code_fail` swapped), or python node didn't actually run | Check python-node exit status; confirm condition function name |
| Tools not visible to the agent | Tool name doesn't match the registry; `module:All` typo (e.g., `files:All` instead of `file:All`) | Run `--inspect-schema` against `FunctionToolEntryConfig` to see the live enum |
| File from upload not found | Wrong `attachment_id` referenced, or `MAC_AUTO_CLEAN_ATTACHMENTS=1` already wiped it | Verify `code_workspace/attachments/` exists; check the execute payload's `attachments` array |
| Subgraph runs once and stops | Subgraph's `start`/`end` don't match parent's expectations, or var inheritance dropped | Check subgraph file's `start` and `end` are valid local node names |

### Failure-mode triage order

When you don't know what's wrong, work from cheap to expensive:

1. **Parse / validate** — call `/api/config/schema/validate`. If it fails, the error path tells you the exact field. Fix and re-validate before running.
2. **Topology read** — does the graph match the user's intent? Trace start → end on paper. If a node isn't reachable from start, it'll never fire.
3. **Edge audit** — every edge: condition, trigger, carry_data, processor. The single most common bug is `trigger: false` on an edge meant to fire the receiver. The second most common is a keyword condition that doesn't match the agent's actual output token (case-sensitive!).
4. **Cycle audit** — for each cycle: which node is the entry (loops have unique entries), what's the exit condition, what's the iteration cap. If exit never fires, the cycle hits the default 100-iteration safety cap.
5. **Context audit** — for misbehaving agents: what's actually in their context at firing time? Check upstream edges' `trigger`/`carry_data`/`keep_message`/`clear_context`. Use the WebSocket observability to inspect the actual messages.
6. **Sidecar audit** — memory: is `read`/`write` correct, embedding configured? Tooling: do tool names match the registry exactly? Thinking: only on the right node?
7. **Workspace / attachments audit** — files written to `code_workspace/` should auto-promote; missing artifacts usually mean the python node failed silently or wrote to the wrong directory.

### Reading observability output

The WebSocket stream emits `node_start`, `node_end`, `edge_traversed`, `iteration`, and `artifact_created` events. When debugging:
- A node that doesn't appear in `node_start` events isn't being triggered → §6 step 3 (edge audit).
- A node that appears repeatedly past expectations → §6 step 4 (cycle audit).
- An agent that fires but the next agent gets weird context → §6 step 5 (context audit).

---

## §7 Validation checklist

Before declaring any workflow done — whether you wrote it from scratch, optimized it, or fixed it — run through this list. These are the failure modes the spec docs and real workflows together reveal.

**Topology**
- [ ] Every node listed in `start` and `end` exists in `nodes[]`
- [ ] Every node is reachable from at least one `start` node (run a mental BFS)
- [ ] Every node either has an outgoing edge or is in `end`
- [ ] No circular subgraph nesting
- [ ] If using cycles: each cycle has a unique entry node (engine requirement)

**Edges**
- [ ] Every edge meant to fire the receiver has `trigger: true` (the default — but verify after copy-paste)
- [ ] Every "context primer" edge has `trigger: false` AND `carry_data: true` (both, not just one)
- [ ] Keyword conditions match the agent's actual output token (case sensitivity matters!)
- [ ] Conditions on cycle exit edges actually have a path to fire (otherwise the cycle hits the iteration cap)
- [ ] No mixed `dynamic` configs on edges into the same node
- [ ] `clear_kept_context: true` only used together with `clear_context: true`

**Agent enrichment**
- [ ] Memory stores are declared at `graph.memory[]` before being attached at `node.config.memories[]`
- [ ] `simple` and `file` stores have an embedding config
- [ ] `tooling:` is a single object per node, not a list
- [ ] Tool names match the registry (use `--inspect-schema` to verify)
- [ ] If using project skills, the agent has the tools required by their `allowed-tools:` frontmatter

**Variables**
- [ ] Every `${VAR}` reference resolves (check `vars:` block, env, `.env`)
- [ ] Common preambles factored into `vars:` rather than copy-pasted across agents

**Pre-flight**
- [ ] Validate with `/api/config/schema/validate` before running
- [ ] If introducing a new pattern, dry-run with a minimal input first

---

## §8 Reference index

Use these files for depth. All live under `references/`.

**Design-time references**
- `pattern_gallery.md` — 19 named patterns with annotated YAML skeletons
- `execution_model.md` — DAG layering, cycle execution (Tarjan + super-nodes + recursive entry detection), dynamic Map/Tree internals

**Write-time references**
- `yaml_and_nodes.md` — top-level schema, variable resolution, full per-node-type field tables
- `edges_and_conditions.md` — edge mechanics, the trigger × carry_data table, the context-control trinity, all condition forms, all processor types
- `memory.md` — `simple` / `file` / `blackboard` stores, embedding config, attachment fields
- `thinking.md` — reflection mode, before/after hooks, custom modes
- `tooling.md` — `function` / `mcp_remote` / `mcp_local` full configuration, `_context` injection, security tips
- `attachments_and_artifacts.md` — file flow, multimodal, auto-promotion, env flags
- `config_schema.md` — `/api/config/schema/validate`, `--inspect-schema` CLI, error contract

**Optimize / Fix references**
- `optimization.md` — the five levers, three cost traps, optimization loop
- `debugging.md` — failure modes by symptom, triage order, observability stream

**Extension developers**
- `field_specs.md` — the `FIELD_SPECS` contract for adding new node types / memory stores / thinking modes / tooling types. Authors of workflows don't need this; only platform extenders.

---

## §9 Open items

These are flagged inline across the references and worth surfacing here so you don't pretend they're settled:

- **Schema doc inconsistency on top-level key**: one example in `config_schema_contract.md` shows `workflow:` as the top-level key with a `name:` field; every other doc uses `graph:` with no `name:`. Author against `graph:` until clarified.
- **Schema doc enum mentions a `model` node type** that no authoring doc references. Use `agent` for LLM nodes.
- **`end:` semantics in production examples**: some Blender workflows list a non-terminal node in `end:` (e.g., `end: [Planner]` when Planner has outgoing edges). This appears to be a "publishing node" convention — the node whose output is the final user-facing answer — rather than "graph terminator." When in doubt, list the actual terminal node(s).
- **`context_window: 0` vs `-1`**: both appear in production and both behave as "unbounded." Authors should pick one and stay consistent within a workflow.
