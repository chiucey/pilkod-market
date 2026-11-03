---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e6d0697977f8fb09c2de37e1212f3f9c
    PropagateID: e6d0697977f8fb09c2de37e1212f3f9c
    ReservedCode1: 30440220083e9fbe67a545e62ba1e3ce5dc3e4bad3828efea214a048005db661cb4610b502205f5af2fc0a355462e394883b79889c2946eb52d91c58063e26ebb23c43406ff5
    ReservedCode2: 3045022100e76e5fa4fe15ceb82683dc1403d192e7440527d680abeecc7ddc2071b0c1256802201b826db12eb2a4dfd39b721b94264ab1189f5ae6fb0cf19eeac32c48cc65fffa
---

# Pattern Gallery

Nineteen named patterns, each tied to a source demo or production workflow, each with copy-pasteable annotated YAML. This is the design encyclopedia — read it whenever you need to compose a workflow.

## Table of contents

**Building-block patterns**
1. [Linear pipeline](#1-linear-pipeline) — `demo_basic.yaml`
2. [Writer–critic loop](#2-writercritic-loop) — `demo_keyword_loop.yaml`
3. [Writer–critic–editor fan-in](#3-writercriticeditor-fan-in) — `demo_human.yaml`
4. [Map fan-out](#4-map-fan-out) — `demo_dynamic.yaml`
5. [Map-then-Tree (fan-out then reduce)](#5-map-then-tree-fan-out-then-reduce) — `demo_dynamic.yaml`, `demo_dynamic_tree.yaml`
6. [Bounded loop with guard](#6-bounded-loop-with-guard) — `demo_loop_counter.yaml`, `demo_loop_timer.yaml`
7. [Subgraph encapsulation](#7-subgraph-encapsulation) — `demo_sub_graph.yaml`, `demo_sub_graph_path.yaml`

**Intermediate patterns**
8. [Cycle with explicit exit token](#8-cycle-with-explicit-exit-token) — `demo_keyword_loop.yaml`
9. [Parallel committee with majority voting](#9-parallel-committee-with-majority-voting) — `demo_majority_voting.yaml`
10. [Context-reset on back-edge](#10-context-reset-on-back-edge) — `demo_context_reset.yaml`
11. [Memory-augmented agent (RAG)](#11-memory-augmented-agent-rag) — `demo_memory.yaml`
12. [Reflection on critical agent](#12-reflection-on-critical-agent) — `demo_thinking.yaml`

**Production patterns**
13. [Orchestrator / Hub](#13-orchestrator--hub) — `blender_3d_builder_hub.yaml`
14. [Switch-case routing on tokenized output](#14-switch-case-routing-on-tokenized-output) — `data_visualization_enhanced.yaml`
15. [Context primer](#15-context-primer) — `MACNet_v1.yaml`, `blender_3d_builder_simple.yaml`
16. [Multi-instance subgraph network](#16-multi-instance-subgraph-network) — `MACNet_v1.yaml`
17. [Phase-prompt literals + per-phase loop counters](#17-phase-prompt-literals--per-phase-loop-counters) — `ChatDev.yaml`
18. [Department / team with token-tagged dispatch](#18-department--team-with-token-tagged-dispatch) — `general_problem_solving_team.yaml`
19. [Code-execution gating](#19-code-execution-gating) — `data_visualization_enhanced.yaml`, `ChatDev.yaml`

[Pattern combinations](#pattern-combinations) at the bottom.

---

## 1. Linear pipeline

The simplest shape: one chain, one direction, no cycles. Use whenever each step has a single owner and downstream context is fully captured by the prior step's output.

```yaml
version: "0.4.0"
graph:
  id: linear-3-step
  start: [Planner]
  end: [Publisher]
  nodes:
    - { name: Planner,   type: agent, config: { provider: anthropic, name: claude-sonnet-4-5-20250929, role: "You plan." } }
    - { name: Drafter,   type: agent, config: { provider: anthropic, name: claude-sonnet-4-5-20250929, role: "You draft from the plan." } }
    - { name: Publisher, type: agent, config: { provider: anthropic, name: claude-sonnet-4-5-20250929, role: "You finalize." } }
  edges:
    - { from: Planner,  to: Drafter }
    - { from: Drafter,  to: Publisher }
```

Most production workflows are *not* this — they layer at least one of patterns 2, 3, or 13 on top.

---

## 2. Writer–critic loop

Iterative refinement with an explicit reviewer. Bounded by either a keyword exit (Pattern 8) or a counter (Pattern 6). The minimal form uses a keyword:

```yaml
nodes:
  - { name: Writer,   type: agent, config: { ..., role: "Draft text. End with PASS if you accept the latest review, else continue." } }
  - { name: Reviewer, type: agent, config: { ..., role: "Review. Output 'APPROVE' if good, 'REVISE' otherwise." } }
edges:
  - { from: Writer,   to: Reviewer }
  - { from: Reviewer, to: Writer
      condition: { type: keyword, config: { any: [REVISE], default: false } } }
  - { from: Reviewer, to: Publisher
      condition: { type: keyword, config: { any: [APPROVE], default: false } } }
```

The cycle engine (see `execution_model.md`) detects the back-edge automatically.

---

## 3. Writer–critic–editor fan-in

Same as Pattern 2, but a downstream editor receives **both** the original draft and the human/critic feedback — `A → B → C` plus `A → C`. This is canonical, not exotic.

```yaml
edges:
  - { from: Writer,   to: Critic }            # draft to critic
  - { from: Critic,   to: Editor }            # critic feedback to editor
  - { from: Writer,   to: Editor }            # original draft also to editor
```

The Editor sees two messages on its incoming context: the original and the review. Use this whenever a downstream synthesizer needs both the input and the intermediate result.

Source: `demo_human.yaml`.

---

## 4. Map fan-out

Same task on many inputs in parallel. Configured **on the edge**, not the node:

```yaml
edges:
  - from: Splitter
    to: Worker
    dynamic:
      type: map
      split_by: message      # or 'regex' or 'json_path'
```

Splitter must produce a list-shaped message (or one that can be split by regex/json_path). The engine spawns one Worker instance per item, in parallel. Static edges into Worker are *replicated* to every parallel instance.

Source: `demo_dynamic.yaml`.

---

## 5. Map-then-Tree (fan-out then reduce)

The canonical large-corpus pipeline: fan out per-item work, then hierarchically reduce. Two edges with different `dynamic` types:

```yaml
edges:
  - { from: Splitter,  to: Worker,   dynamic: { type: map,  split_by: message } }
  - { from: Worker,    to: Reducer,  dynamic: { type: tree, group_size: 3 } }
```

`group_size` is the reduction fan-in: every 3 worker outputs are reduced together; the reducer recurses until one message remains. Use Tree alone (without Map) when the upstream message is already a list and you only need reduction; use Map alone when you don't need to combine results.

Sources: `demo_dynamic.yaml` (map then tree), `demo_dynamic_tree.yaml` (tree alone with regex chunking for long-document summarization).

---

## 6. Bounded loop with guard

Any cycle that must terminate by step count or wall time. The four-edge topology is identical for `loop_counter` and `loop_timer`:

```yaml
nodes:
  - { name: Human, type: human, config: { prompt: "What should I write about?" } }
  - { name: Agent, type: agent, config: { ..., role: "Write a draft, refining each turn." } }
  - { name: Guard, type: loop_counter, config: { max_iterations: 5 } }   # or loop_timer
  - { name: End,   type: passthrough }
edges:
  - { from: Human, to: Agent }                        # 1. fire the loop body
  - { from: Human, to: Guard }                        # 2. notify the guard (no fire-back)
  - { from: Guard, to: Agent }                        # 3. in-loop marker — required even though Guard usually doesn't fire
  - { from: Guard, to: End }                          # 4. out-of-loop trigger — only fires at limit
  - { from: Human, to: End, condition: any }          # 5. immediate exit path
```

The non-obvious part: the **back-edge that actually keeps the loop running has to come from `Human → Agent`**, not from `Guard → Agent`. Because Guard suppresses output until the limit is reached, you can't make Guard the cycle's "engine." But Guard *still* needs an edge into the loop body so the engine recognizes it as in-loop, otherwise cycle detection treats Guard's exit edge as the natural exit and terminates prematurely.

Loop_timer variant: replace the Guard's config with `{ max_duration: 5, duration_unit: minutes }`. The timer starts on the first trigger to the timer node — *not* at workflow start.

Sources: `demo_loop_counter.yaml`, `demo_loop_timer.yaml`.

---

## 7. Subgraph encapsulation

Reusable sub-workflow. Two YAML shapes — pick by sharing intent:

```yaml
# Inline — embed the child graph for self-contained workflows
- name: PaymentSubgraph
  type: subgraph
  subgraph:
    type: config
    graph:
      id: payment
      start: [Validate]
      end: [Charge]
      nodes: [ ... ]
      edges: [ ... ]

# Referenced — point at a separate file for true reuse
- name: PaymentSubgraph
  type: subgraph
  subgraph:
    type: file
    path: ./subgraphs/payment.yaml
```

Vars cascade from parent. Memory can be subgraph-local. The subgraph's `start` and `end` define the in/out boundary — the parent treats the subgraph node as a single black-box node.

Sources: `demo_sub_graph.yaml`, `demo_sub_graph_path.yaml`.

---

## 8. Cycle with explicit exit token

Pattern 2 in its purest form — the cycle exits when the agent emits a sentinel token. No counter, no timer; trust the agent to terminate.

```yaml
edges:
  - { from: Reviewer, to: Writer,    condition: { type: keyword, config: { any: [REVISE] } } }
  - { from: Reviewer, to: Publisher, condition: { type: keyword, config: { any: [APPROVE] } } }
```

If neither condition matches, the cycle hits the engine's default 100-iteration safety cap and terminates with a warning. Always make at least one exit condition reachable.

Source: `demo_keyword_loop.yaml`.

---

## 9. Parallel committee with majority voting

Multiple agents answer the same question independently; an aggregator picks the majority. Pure DAG — no cycle.

```yaml
nodes:
  - { name: Q,      type: passthrough }
  - { name: A1,     type: agent, config: { ..., role: "Answer." } }
  - { name: A2,     type: agent, config: { ..., role: "Answer." } }
  - { name: A3,     type: agent, config: { ..., role: "Answer." } }
  - { name: Vote,   type: agent, config: { ..., role: "Take three answers, return majority." } }
edges:
  - { from: Q,    to: A1, keep_message: true }    # original question pinned to each
  - { from: Q,    to: A2, keep_message: true }
  - { from: Q,    to: A3, keep_message: true }
  - { from: A1,   to: Vote }
  - { from: A2,   to: Vote }
  - { from: A3,   to: Vote }
```

`keep_message: true` ensures each answerer sees the question even after their own context is reset.

Source: `demo_majority_voting.yaml`.

---

## 10. Context-reset on back-edge

In long cycles, the agent's context bloats every iteration. The back-edge can reset it:

```yaml
edges:
  - from: Reviewer
    to: Writer
    condition: { type: keyword, config: { any: [REVISE] } }
    clear_context: true        # wipe non-pinned messages
    keep_message: false        # the new review is itself unpinned (default)
    # If the user's original task was pinned with keep_message: true earlier,
    # it survives this clear; everything else is wiped before the new review arrives.
```

For a hard reset that also wipes pinned messages, add `clear_kept_context: true`. The four states form a deliberate authoring tool:

| keep_message | clear_context | clear_kept_context | Effect |
|---|---|---|---|
| (default) | (default) | (default) | Append normally |
| `true` | — | — | Pin: message survives later soft resets |
| — | `true` | — | Soft reset: wipe non-pinned, then write |
| — | `true` | `true` | Hard reset: wipe everything, then write |

Source: `demo_context_reset.yaml`.

---

## 11. Memory-augmented agent (RAG)

Declare memory stores once at the graph level, attach per-node:

```yaml
graph:
  id: rag-workflow
  memory:
    - name: docs
      type: file
      config:
        path: ./corpus/
        embedding:
          provider: openai
          model: text-embedding-3-small
  nodes:
    - name: Researcher
      type: agent
      config:
        provider: anthropic
        name: claude-sonnet-4-5-20250929
        role: "Answer using retrieved docs."
        memories:
          - name: docs
            retrieve_stage: before_generate
            top_k: 5
            similarity_threshold: 0.7
            read: true
            write: false
```

`simple` (FAISS + rerank, conversational) and `file` (read-only doc index) both require an embedding config. `blackboard` (append-only shared log) does not.

Source: `demo_memory.yaml`.

---

## 12. Reflection on critical agent

Add `thinking: reflection` to high-stakes agents only — it doubles their cost.

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
          stage: after_generate     # or before_generate
```

Source: `demo_thinking.yaml`.

---

## 13. Orchestrator / Hub

A central agent decides routing via tokenized output (`ROUTE: X`); workers report back; the orchestrator dispatches the next worker. Scales beyond cycles because the topology is flat — one hub plus N workers — rather than deeply nested.

```yaml
nodes:
  - name: Orchestrator
    type: agent
    config:
      provider: anthropic
      name: claude-sonnet-4-5-20250929
      role: |
        You coordinate workers. After each worker reports, decide the next step.
        End every reply with one of:
        ROUTE: BUILD       (call the builder)
        ROUTE: REVIEW      (call the reviewer)
        ROUTE: SHIP        (we're done)
  - { name: Builder,  type: agent, config: { ..., role: "You build." } }
  - { name: Reviewer, type: agent, config: { ..., role: "You review." } }
  - { name: Done,     type: passthrough }

edges:
  # Hub → Workers, conditioned on the route token
  - { from: Orchestrator, to: Builder,
      condition: { type: keyword, config: { any: [BUILD] } } }
  - { from: Orchestrator, to: Reviewer,
      condition: { type: keyword, config: { any: [REVIEW] } } }
  - { from: Orchestrator, to: Done,
      condition: { type: keyword, config: { any: [SHIP] } } }
  # Workers → Hub (always report back)
  - { from: Builder,  to: Orchestrator }
  - { from: Reviewer, to: Orchestrator }
```

The pattern is a state machine encoded in the orchestrator's prompt and the edge conditions. Adding a new worker means: a new node, a new ROUTE token in the orchestrator's role, two new edges.

Source: `blender_3d_builder_hub.yaml`, `general_problem_solving_team.yaml`.

---

## 14. Switch-case routing on tokenized output

The building block of Pattern 13, also useful standalone. Agent emits a token; downstream edges keyword-condition on it.

```yaml
nodes:
  - name: Classifier
    type: agent
    config:
      role: |
        Classify the input. End with exactly one of:
        NEXT_STEP: CLEAN     (data needs cleaning)
        NEXT_STEP: VISUALIZE (data is clean; chart it)
        NEXT_STEP: REPORT    (already analyzed; write up)
  - { name: Cleaner,    type: agent }
  - { name: Visualizer, type: agent }
  - { name: Reporter,   type: agent }

edges:
  - { from: Classifier, to: Cleaner,
      condition: { type: keyword, config: { any: [CLEAN], case_sensitive: true } } }
  - { from: Classifier, to: Visualizer,
      condition: { type: keyword, config: { any: [VISUALIZE], case_sensitive: true } } }
  - { from: Classifier, to: Reporter,
      condition: { type: keyword, config: { any: [REPORT], case_sensitive: true } } }
```

**Case sensitivity matters.** The agent might output `Visualize` or `VISUALIZE` depending on its mood; pick a convention and enforce it in the role prompt.

Source: `data_visualization_enhanced.yaml` and several others.

---

## 15. Context primer

`trigger: false + carry_data: true` — write a message into a node's context **without firing it**. Used to inject background that another, triggering edge will then act on.

```yaml
edges:
  # Five priming edges — they put the user task into every node's context but don't fire them
  - { from: USER, to: '0',  trigger: false, carry_data: true }
  - { from: USER, to: '1',  trigger: false, carry_data: true }
  - { from: USER, to: '2',  trigger: false, carry_data: true }
  - { from: USER, to: '3',  trigger: false, carry_data: true }
  - { from: USER, to: '-2', trigger: false, carry_data: true }
  # Only this edge actually triggers anyone — '-1' is the entry point
  - { from: USER, to: '-1' }
```

The four `trigger × carry_data` combinations:

| trigger | carry_data | Effect |
|---|---|---|
| `true` (default) | `true` (default) | Fire the receiver; payload is in its context |
| `true` | `false` | Fire the receiver; payload is *not* added to context (rare) |
| `false` | `true` | **Context primer** — receiver gets the message but is not fired |
| `false` | `false` | Edge does nothing (almost always a bug) |

Use the context primer pervasively. It's the structurally correct way to give a node background information without disturbing the firing topology.

Sources: `MACNet_v1.yaml`, `blender_3d_builder_simple.yaml`.

---

## 16. Multi-instance subgraph network

The same subgraph file instantiated as N nodes wired in feedforward layers — like a neural network of agent committees.

```yaml
graph:
  id: macnet
  start: [USER]
  end: [Result]
  nodes:
    - { name: USER,   type: passthrough }
    # Six instances of the same subgraph, wired feedforward
    - { name: '-1', type: subgraph, subgraph: { type: file, path: ./MACNet_Node_sub.yaml } }
    - { name: '0',  type: subgraph, subgraph: { type: file, path: ./MACNet_Node_sub.yaml } }
    - { name: '1',  type: subgraph, subgraph: { type: file, path: ./MACNet_Node_sub.yaml } }
    - { name: '2',  type: subgraph, subgraph: { type: file, path: ./MACNet_Node_sub.yaml } }
    - { name: '3',  type: subgraph, subgraph: { type: file, path: ./MACNet_Node_sub.yaml } }
    - { name: '-2', type: subgraph, subgraph: { type: file, path: ./MACNet_Node_sub.yaml } }
    - { name: Result, type: passthrough }
  edges:
    # Context primers (Pattern 15) — see source
    # Triggering chain
    - { from: USER, to: '-1' }
    - { from: '-1', to: '0' }
    - { from: '0',  to: '1' }
    - { from: '1',  to: '2' }
    - { from: '2',  to: '3' }
    - { from: '3',  to: '-2' }
    - { from: '-2', to: Result }
```

Each subgraph internally instantiates *another* subgraph multiple times via Map dispatch. The pattern composes cleanly — the parent doesn't need to know the inner structure.

Source: `MACNet_v1.yaml`.

---

## 17. Phase-prompt literals + per-phase loop counters

Multi-phase pipelines (e.g., ChatDev) use `literal` nodes named for each phase that inject phase-specific instructions, plus a `loop_counter` per phase to bound iteration.

```yaml
nodes:
  - { name: "Coding Phase Prompt for User",
      type: literal,
      config: { content: "Now write the implementation. Tag DECISION: APPROVE when ready.", role: user } }
  - { name: "Coding Phase Loop Counter",
      type: loop_counter,
      config: { max_iterations: 5 } }
  - { name: "Test Phase Prompt for User",
      type: literal,
      config: { content: "Now write tests.", role: user } }
  - { name: "Test Phase Loop Counter",
      type: loop_counter,
      config: { max_iterations: 3 } }
  - { name: User,      type: agent }
  - { name: Assistant, type: agent }

edges:
  # Phase 1: coding loop
  - { from: "Coding Phase Prompt for User", to: User }
  - { from: "Coding Phase Prompt for User", to: "Coding Phase Loop Counter" }
  - { from: User,      to: Assistant }
  - { from: Assistant, to: User,
      condition: { type: keyword, config: { none: [DECISION: APPROVE] } } }
  - { from: "Coding Phase Loop Counter", to: User }
  - { from: "Coding Phase Loop Counter", to: "Test Phase Prompt for User" }
  # Exit-by-token also goes to next phase
  - { from: Assistant, to: "Test Phase Prompt for User",
      condition: { type: keyword, config: { any: [DECISION: APPROVE] } } }
  # Phase 2: test loop (same shape, different counter)
  ...
```

The literal's `role: user` matters — it injects as a user turn, prompting the agent to respond. Use `role: assistant` to inject as conversation history without prompting.

Source: `ChatDev.yaml`.

---

## 18. Department / team with token-tagged dispatch

An upstream `Demand Analyze` agent decomposes a request into per-department sub-tasks with explicit instructions like "find the part about X and ignore the rest." The workflow fans out to each department; each is role-specialized with tooling tailored to its job; results reduce through a `Summary Department`.

```yaml
nodes:
  - name: "Demand Analyze"
    type: agent
    config:
      role: |
        Decompose the user's request into department-tagged tasks. Use this format:
        [TECHNICIAN]: <task; ignore everything else>
        [INFO_SEARCHER]: <task; ignore everything else>
        [WRITER]: <task; ignore everything else>
  - name: "Technician"
    type: agent
    config:
      role: "You write and run code. Look only for the [TECHNICIAN] section."
      tooling:
        type: function
        functions: [code_executor:All]
  - name: "Info Searcher"
    type: agent
    config:
      role: "You research the web. Look only for the [INFO_SEARCHER] section."
      tooling:
        type: function
        functions: [web:All]
  - name: "Writer"
    type: agent
    config:
      role: "You write. Look only for the [WRITER] section."
  - name: "Summary Department"
    type: agent
    config:
      role: "Combine all department reports into one answer."

edges:
  - { from: "Demand Analyze", to: "Technician" }
  - { from: "Demand Analyze", to: "Info Searcher" }
  - { from: "Demand Analyze", to: "Writer" }
  - { from: "Technician",     to: "Summary Department" }
  - { from: "Info Searcher",  to: "Summary Department" }
  - { from: "Writer",         to: "Summary Department" }
```

The self-filtering instruction ("ignore everything else") means each department processes only its own sub-task even though all three see the full decomposition.

Source: `general_problem_solving_team.yaml`.

---

## 19. Code-execution gating

Function-condition shorthand for routing on python-node status. The condition strings `code_pass` and `code_fail` are registered functions that check the prior python node's exit status.

```yaml
nodes:
  - { name: CodeWriter, type: agent, config: { role: "Write Python code." } }
  - { name: Runner,     type: python, config: { script: ./run_code.py } }
  - { name: Reporter,   type: agent, config: { role: "Report success." } }

edges:
  - { from: CodeWriter, to: Runner,
      process: { type: function, config: { name: code_save_and_run } } }
  - { from: Runner, to: Reporter,    condition: code_pass }
  - { from: Runner, to: CodeWriter,  condition: code_fail }   # retry loop
```

The `code_save_and_run` processor extracts code from the upstream message, saves it as the python node's input, and the python node then runs it. On failure, the back-edge to `CodeWriter` triggers a fresh attempt.

For a bounded retry, combine with Pattern 6 — add a `loop_counter` on the back-edge.

Sources: `data_visualization_enhanced.yaml`, `data_visualization_enhanced_v2.yaml`, `ChatDev.yaml`.

---

## Pattern combinations

Real workflows compose these patterns. Some canonical combinations:

- **3 + 6** (Writer–critic–editor + bounded loop): The standard high-quality-content production shape. The editor at the end synthesizes the original and the latest reviewed draft after the loop terminates.
- **5 + 11** (Map-then-Tree + memory): Process a corpus by document, summarize hierarchically, write final summary to a `blackboard` for downstream use.
- **6 + 10** (Bounded loop + context reset): Long-running cycles where the agent needs the user's task pinned but every iteration's review wiped before the next iteration starts.
- **13 + 14 + 19** (Orchestrator + switch-case + code gating): The orchestrator routes between code-writer, code-runner, and reviewer, with `code_pass`/`code_fail` conditions on the runner's outgoing edges. Used in software-development workflows.
- **15 + 16** (Context primer + multi-instance subgraph network): MACNet's complete shape — every subgraph instance gets the user task as primed context and is triggered by the upstream layer's output.
- **17 + 19** (Phased loop counters + code gating): Multi-phase development pipelines (ChatDev) where each phase has its own counter and code-execution gate.
- **13 + 17** (Orchestrator + phase prompts): An orchestrator that progresses through phases by routing to phase-specific literals, with each phase running its own bounded sub-loop.

When the user describes a workflow that doesn't map cleanly onto a single pattern, ask which combination fits — it's almost always a combination, not a novel shape.
