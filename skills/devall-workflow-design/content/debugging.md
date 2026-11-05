---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 55c9368869599989fce66c479194b669
    PropagateID: 55c9368869599989fce66c479194b669
    ReservedCode1: 3045022034efee35e125c012383bea9fe6ea242e9c6d5def3c5a3bcdaa502b1bb19b117e022100d0f5cc76a581a2a8083bd90767afc7d77503d59f33fbdbb0c02a90192b84c732
    ReservedCode2: 3045022100c001868ef3d1be8983a45d1a6e975016d214b85d9239981e18a94ede05128c8202201432e952ee8325c15db460430c0cb9ff66a948b8846e5232b94200c6e8bca760
---

# Debugging Playbook

When a workflow is broken or producing the wrong output. Goal: identify exactly what's wrong and apply a minimal fix.

## Triage by symptom

| Symptom | Likely cause | First action |
|---|---|---|
| `ConfigError` at parse / validate | Variable unresolved, schema mismatch, unknown `type:` | Read the error's `path` array — it points at the exact field |
| `ValidationError` from `/api/config/schema/validate` | Same as above; pre-runtime detection | Read `path`; check `schema` for the expected shape |
| Workflow starts but a node never fires | All incoming edges have failing conditions, or only `trigger: false` edges | Check edge conditions; ensure at least one triggering edge can fire |
| Workflow starts but nothing happens at all | `start:` node not actually present in `nodes[]`, or `start:` node has no outgoing edges | Verify topology end to end |
| Cycle never exits, hits 100-iteration cap | No exit-edge condition matches, max_iterations not set, loop guard mis-wired | Verify the four-edge bounded-loop topology (Pattern 6) |
| Cycle exits too early | Cycle entry node not unique; engine picked a different entry; or guard's edge to body is missing | Check that the cycle has a unique entry; verify `Guard → Agent` "in-loop marker" edge |
| Agent gets the wrong context | Missing context primer, or `clear_context` wiping needed history, or `keep_message` not pinning the task | Trace the edges into the node; check trigger × carry_data + the context-control trinity |
| Agent fires but produces irrelevant output | Role prompt + context don't match; the agent is responding to a stale message | Inspect what's actually in its context (WebSocket `node_start` event) |
| Dynamic edge fails | Mixed `dynamic` configs into one node, or splitter mismatch (regex doesn't match the message) | All dynamic edges into a node must share identical `dynamic`; test the regex against the actual upstream message |
| Code-execution branch always misroutes | `code_pass` / `code_fail` swapped, or python node didn't actually run | Check python-node exit status; confirm condition function name |
| Tools not visible to the agent | Tool name doesn't match the registry; `module:All` typo (e.g., `files:All` instead of `file:All`) | `--inspect-schema --schema-breadcrumbs FunctionToolEntryConfig` to see the live enum |
| File from upload not found | Wrong `attachment_id` referenced, or `MAC_AUTO_CLEAN_ATTACHMENTS=1` already wiped it | Verify `code_workspace/attachments/` exists; check the execute payload's `attachments` array |
| Subgraph runs once and stops | Subgraph's `start`/`end` don't match parent expectations, or var inheritance dropped | Check subgraph file's `start` and `end` are valid local node names |
| Memory retrieval returns nothing useful | Embedding mismatch between index and query, low `top_k`, high `similarity_threshold` | Lower threshold; bump `top_k`; verify embedding model is the same as at index time |
| Cycle-with-keyword-condition exits sometimes but not others | Case sensitivity bug — agent emits `Approve` vs `APPROVE` inconsistently | Set `case_sensitive: false` or pin convention in the role prompt |
| Output is correct but workflow takes too long | Sequential where parallel would do; full context where windowed would do | This is an optimization concern — see `optimization.md` |

## Failure-mode triage order

When you don't know what's wrong, work from cheap to expensive:

### Step 1: Parse / validate

Call `POST /api/config/schema/validate` with the YAML. If it fails, the error path tells you the exact field. Fix and re-validate before running.

```bash
curl -X POST http://localhost:8000/api/config/schema/validate \
  -H "Content-Type: application/yaml" \
  --data-binary @workflow.yaml
```

A `valid: true` doesn't mean the workflow runs correctly — only that its shape matches the schema.

### Step 2: Topology read

Does the graph match the user's intent? Trace `start → end` on paper:

- Every node listed in `start` and `end` must exist in `nodes[]`.
- Every node must be reachable from at least one `start` node (mental BFS).
- Every node either has an outgoing edge or is in `end`.
- If a node isn't reachable from start, it'll never fire — find the missing edge.

### Step 3: Edge audit

For every edge, check four things:

1. **Condition** — does it match what the upstream node actually outputs? Case sensitivity, exact token spelling, regex pattern.
2. **Trigger** — should this edge fire the receiver? If `trigger: false`, then `carry_data: true` is also needed (the context primer pattern).
3. **Carry data** — should the payload be in the receiver's context? Default true; explicitly false only when the firing alone matters.
4. **Processor** — does the transform produce what the receiver expects?

The single most common bug: `trigger: false` on an edge meant to fire the receiver. The second: a keyword condition that doesn't match the agent's actual output token (case-sensitive).

### Step 4: Cycle audit

For each cycle:

- **Entry uniqueness**: only one node should have incoming edges from outside the SCC.
- **Exit reachability**: at least one exit condition must be reachable from the agent's outputs. If exit conditions never match what the agent emits, the cycle hits the iteration cap.
- **Iteration cap**: either explicitly set via `loop_counter` / `loop_timer`, or the engine's default 100.
- **Bounded-loop topology**: if using a counter/timer, verify all four edges (see Pattern 6).

### Step 5: Context audit

For misbehaving agents: what's actually in their context at firing time?

- **Upstream edges**: what's `trigger`/`carry_data` on each? Are priming edges also delivering?
- **Pinned messages**: did `keep_message: true` ever get set on the user task?
- **Context resets**: does any incoming edge have `clear_context: true`? What does it wipe?

The WebSocket `node_start` event includes the receiver's full context — inspect it. The bug is almost always visible in the actual message sequence.

### Step 6: Sidecar audit

- **Memory**: is `read`/`write` correct? Is the embedding configured? Does the embedding model match what was used at index time?
- **Tooling**: do tool names match the registry exactly? (`--inspect-schema FunctionToolEntryConfig`.) For MCP local: did `wait_for_log` match what the server actually prints?
- **Thinking**: applied to the right node? `stage: before_generate` or `after_generate` matters.

### Step 7: Workspace / attachments audit

- Files written to `code_workspace/` should auto-promote. If the user reports a missing artifact, check whether the python node actually wrote to that directory (vs. somewhere else).
- For uploads: was the `attachment_id` referenced in the execute payload? Is `code_workspace/attachments/<file>` actually present?
- Check `MAC_AUTO_CLEAN_ATTACHMENTS` — if a session ended and was re-entered, attachments may have been wiped.

## Reading the WebSocket observability stream

The events:

- `node_start` — the node began executing. Includes the full context the node will see.
- `node_end` — the node finished, with its output Message attached. Includes usage data.
- `edge_traversed` — the edge fired (condition matched, payload delivered).
- `iteration` — a cycle entry node re-fired (one iteration of the cycle).
- `artifact_created` — a file was written and registered as an artifact.
- `error` — exception with the failing node's name.

Quick diagnostic patterns:

- **Node never fires**: check if it appears in `node_start` events at all. If not, no incoming edge succeeded — go to Step 3 (edge audit).
- **Node fires but cycle doesn't terminate**: count the `iteration` events for the cycle's entry node. If it climbs without bound, exit conditions aren't matching — go to Step 4.
- **Node fires but downstream gets weird input**: read the next node's `node_start` context. If it's missing the expected payload, an upstream edge is filtering it out — go to Step 3 (processor / condition) and Step 5 (context resets).
- **Workflow ends prematurely**: find the last `node_end` event before the workflow stopped. The next-expected node's incoming edges probably all failed their conditions.

## Anti-patterns that cause subtle bugs

- **Re-using the same agent name across nodes** — the engine treats them as the same node, with surprising firing behavior. Always unique names.
- **Forgetting `keep_message: true` on the user task** in long cycles — the task gets wiped on the first soft reset and the agent starts hallucinating about what it's supposed to do.
- **Multiple agents emitting the same routing token** in different conditions — the engine's keyword matching is lexical, not semantic. If `Worker A` emits `STATUS: PASS` and `Worker B` emits `STATUS: PASS` and edges from both are conditioned on `PASS`, both fire downstream simultaneously.
- **Putting state in a `simple` memory store and expecting reliable readback** — `simple` stores retrieve by similarity, not by recency. Use `blackboard` if you need exact readback.
- **Cycle entry not unique due to multiple priming edges** — context primers (`trigger: false`) don't count toward cycle entry, but real triggering edges do. Two triggering edges into the cycle from outside → ambiguous entry → parse error.

## When to escalate to platform inspection

If the workflow validates, the topology is right, edges all check out, and the WebSocket stream shows the right firing pattern but the *output* is wrong, the issue is at the agent / model layer:

- Bad role prompt — the agent doesn't actually know what to do.
- Bad upstream content — the message reaching the agent is malformed (check the upstream node's actual output).
- Model limitation — the chosen model can't perform the task.

These are not graph-engine bugs. Iterate on the prompt, swap to a stronger model on the failing agent, or split the agent's job into two simpler agents.
