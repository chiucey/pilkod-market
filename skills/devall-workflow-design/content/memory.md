---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3cd76f1fd2be4ce9b14739c8da7b4b9e
    PropagateID: 3cd76f1fd2be4ce9b14739c8da7b4b9e
    ReservedCode1: 304502207a904d00399a5cbafd61b8c08129cccff81ba33a3ebe28e53800bfdb1be56276022100bd7c34f562a0ac2d5b2a96514ebf892c33fe48592f94f735efa4f906042a78bd
    ReservedCode2: 30450221009203dd627495d1abcbd527c7d3cb3f90a22783c720424dd9028861f9e219177202204051f9ec90529f6482b70c92b02e7d16a7f10b32a24a51efaf8464d7bfacf1af
---

# Memory Module

Memory stores are declared once at the graph level and attached per-agent-node. They give agents persistent context that survives beyond the message-passing window — across cycle iterations, across runs, or across whole sessions.

## When you actually need memory

Most workflows don't need memory. The message context is usually enough. Reach for memory only when:

- An agent needs information from earlier in the conversation that the message context can't carry (e.g., an early-in-cycle decision the late-in-cycle agent must remember).
- The workflow needs to RAG over a document corpus.
- Multiple nodes need to share state (a "blackboard" of running notes).

If the question is "should I add memory to this agent?", the answer is usually no.

## Three store types

### `simple`

Conversational memory with FAISS vector search and a rerank step. Use for "remember relevant past conversation chunks."

```yaml
graph:
  memory:
    - name: chat-history
      type: simple
      config:
        embedding:
          provider: openai
          model: text-embedding-3-small
        # Optional: index size, rerank model, etc.
```

### `file`

Read-only document index. Use for RAG.

```yaml
graph:
  memory:
    - name: docs
      type: file
      config:
        path: ./corpus/                # directory of files to index
        embedding:
          provider: openai
          model: text-embedding-3-small
```

### `blackboard`

Append-only shared log. Use when multiple nodes need to read/write a running set of notes. No embedding required.

```yaml
graph:
  memory:
    - name: shared-notes
      type: blackboard
      config: {}
```

## Attaching memory to a node

```yaml
nodes:
  - name: Researcher
    type: agent
    config:
      provider: anthropic
      name: claude-sonnet-4-5-20250929
      role: "Answer using the doc corpus."
      memories:
        - name: docs                   # references graph.memory[].name
          retrieve_stage: before_generate    # or 'after_generate'
          top_k: 5                     # number of chunks to retrieve
          similarity_threshold: 0.7    # filter weak matches
          read: true                   # retrieve into context
          write: false                 # don't add this node's output to the store
```

`read: true, write: false` is the typical RAG configuration. `read: false, write: true` makes the node a writer-only (e.g., a summarizer that adds to a `blackboard`). `read: true, write: true` (full participation) is the typical conversational use.

## EmbeddingConfig

Both `simple` and `file` require an embedding configuration. `blackboard` does not.

```yaml
embedding:
  provider: openai           # or 'anthropic', 'cohere', etc.
  model: text-embedding-3-small
  api_key: ${OPENAI_API_KEY} # often read from env via vars
  # provider-specific extras
```

## Tuning notes

- `top_k` too high inflates the prompt; too low misses context. Start at 5.
- `similarity_threshold` filters weak matches; raise it (e.g., 0.75) when the corpus is large and recall is acceptable.
- `retrieve_stage: before_generate` is the default. `after_generate` retrieves based on the agent's output (rarely useful — used for chained retrieval).

## Common bugs

- Missing `embedding:` config on a `simple` or `file` store → parse error.
- Attaching a memory by name that isn't declared in `graph.memory` → parse error.
- `write: true` on a `file` store — file stores are read-only by design; the platform should reject this.
- Using `simple` store for what should be a `blackboard` — expect retrieval-shaped recall, not reliable readback. If the agent needs to read *exactly* what was written, use `blackboard`.
