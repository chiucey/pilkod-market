---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 391106f25c57d7e14d2c8fb2b7108ce7
    PropagateID: 391106f25c57d7e14d2c8fb2b7108ce7
    ReservedCode1: 30440220772d485aa007d7c41b395dad618db5eb11fa11fd56607fd0a41019a1a7d7695602201dc4cc660c1466e1e621ee849e5d11a52f8f473b20954323acd90149cb609580
    ReservedCode2: 3045022100950d996a2c44dcb0784c3a807b37516ebc90ebdb3c37aa3459fa108f3ba9902902203bb643707ae6e209b695a9d407a20477e7ef9b1a0553564ab87e687fc051cdc3
---

# Execution Model

How the engine actually runs a workflow. Useful when designing (to predict execution shape), and crucial when debugging (to understand why something fired or didn't).

## DAG execution

The default. The engine:

1. Topologically layers the graph.
2. Within a layer, fires all nodes in parallel.
3. Advances to the next layer once all current-layer nodes complete (and their outgoing edges have evaluated their conditions).

A node fires when **at least one** incoming triggering edge has fired and its condition matched. Multiple incoming triggering edges are OR'd, not AND'd.

Context-priming edges (`trigger: false + carry_data: true`) deliver their payload but do not contribute to the firing decision. The receiver fires when an actual triggering edge arrives.

## Cycle execution

Cycles are not a separate node type — they emerge when edges form a loop. The engine handles them via:

1. **Tarjan's algorithm** to detect strongly connected components (SCCs).
2. Each non-trivial SCC is **abstracted into a super-node** in the outer DAG.
3. Within the super-node, the engine identifies a **unique entry node** — the one that has incoming edges from outside the SCC.
4. Each iteration: incoming edges to the entry are removed, the residual graph is checked for nested SCCs, and the recursion proceeds.
5. The cycle exits on the **first** of:
   - An exit edge fires (a condition matches a path leading out of the SCC).
   - The iteration cap is hit (default 100; configurable via `loop_counter`).
   - A `loop_timer` expires.
   - The entry node is not re-triggered for a complete iteration.

**Each cycle requires exactly one entry node.** If the topology produces multiple potential entries, parsing fails with an error pointing at the cycle.

### The bounded-loop topology (Pattern 6)

The four-edge wiring exists because of the cycle entry rule:

```
Human → Agent      # actually keeps the loop running
Human → Guard      # tells Guard each iteration happened
Guard → Agent      # in-loop marker — required for engine to recognize Guard as in-loop
Guard → End        # out-of-loop trigger — fires only at the limit
Human → End        # immediate exit path (with condition: any if Human can short-circuit)
```

The Guard usually doesn't fire (it's accumulating). Without the `Guard → Agent` edge, the engine treats Guard's only outgoing edge (`Guard → End`) as the natural cycle exit and terminates immediately. With the edge present, the engine knows Guard is part of the loop and waits for the count.

### Execution trace example

For Pattern 6 with `max_iterations: 3`:

```
Iter 1: Human fires → Agent fires (output: "draft 1") + Guard accumulates (count=1)
Iter 2: Agent fires → Human re-fires? Depends on the cycle's other edges. Typical:
        Agent → Reviewer → Human (back-edge). So Reviewer fires, then Human.
        Human → Agent (count=2 in Guard)
Iter 3: ... (count=3)
Iter 4: Human → Guard, count reaches max. Guard fires its outgoing → End.
        Cycle exits.
```

If the cycle has its own keyword exit condition that fires before the count is reached, the cycle exits there — counter is a safety net.

## Dynamic execution

Configured on edges, not nodes. Two types: `map` and `tree`.

### Map

```
Splitter (output: list-shaped message)
  └─ Map edge → Worker
```

The engine splits the upstream payload into N items (by `split_by`: message-list, regex captures, or JSON-path matches), spawns N parallel Worker instances, and collects their outputs as a list. Static edges into Worker are *replicated* to every parallel instance — every instance sees the same static-edge messages.

The downstream consumer of the Map edge receives a `List[Message]` containing all parallel results.

### Tree

```
Splitter (output: list-shaped message)
  └─ Tree edge (group_size: 3) → Reducer
```

Same fan-out as Map, then the engine groups outputs into batches of `group_size` and calls the Reducer on each batch. The Reducer's outputs are themselves grouped and reduced, recursively, until one Message remains.

Tree alone (without an upstream Map): the Reducer is called on already-list-shaped messages from upstream.

### Constraints

- All dynamic edges into a single node must share identical `dynamic` config.
- Dynamic and cycle don't compose on the same edge. To combine: put the dynamic execution inside a subgraph and cycle on the subgraph node.

## What the WebSocket emits

For debugging:

| Event | Meaning |
|---|---|
| `node_start` | A node began executing |
| `node_end` | A node finished, with its output Message attached |
| `edge_traversed` | An edge fired (i.e., its condition matched and it delivered) |
| `iteration` | A cycle entry node re-fired (one iteration of the cycle) |
| `artifact_created` | A file was written to `code_workspace/` and registered as an artifact |
| `error` | Anything went wrong, with the failing node's name and the exception |

A node that doesn't appear in `node_start` events isn't being triggered — see `debugging.md` step 3.

A node that appears repeatedly past expectations is in a cycle that isn't exiting — see `debugging.md` step 4.
