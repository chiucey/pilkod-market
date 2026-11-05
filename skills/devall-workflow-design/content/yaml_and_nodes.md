---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f0dcfd78dae8b42168f0b1ac636d3e93
    PropagateID: f0dcfd78dae8b42168f0b1ac636d3e93
    ReservedCode1: 304502201c625a557bf792de7a616f187ba6d373c4e669791a51aa8cafc9fef0842646a9022100d810483917f55a5e63efc0759f15357a1e42d76c2e097681b2df0b8b0e9fd106
    ReservedCode2: 304502205ca77a6721646a3ba77ffa6964215fe143508be511d4d92db57fedd036ea13e1022100b405428b9cdcdf20baefb1d61ac221d5dd5049859cf6d3e72dfd083670508bea
---

# YAML Schema & Node Types

Reference for the top-level YAML structure, variable resolution, and the full field set for each of the eight node types.

## Top-level structure

```yaml
version: "0.4.0"           # schema version. Required.
vars:                      # parameters resolved before parse. Optional.
  KEY: value
graph:                     # the workflow. Required.
  id: <string>             # required; identifier
  start: [<node-name>]     # required; list OR scalar
  end: [<node-name>]       # required; list OR scalar
  nodes: [...]             # required
  edges: [...]             # required (may be empty for a one-node graph)
  memory: [...]            # optional; declares stores attached by nodes
```

**Top-level field name caveat**: one schema-validate example shows `workflow:` instead of `graph:`. Every authoring doc uses `graph:`. Author against `graph:`.

**`end:` semantics**: in some production workflows, `end:` lists a non-terminal node — the "publishing node" whose output is the final answer, even if it has outgoing edges. When in doubt, list the actual terminal node(s).

## Variable resolution

Priority (highest to lowest):

1. `vars:` block in the YAML
2. Shell environment variables
3. `.env` file in the workflow's directory

Reference syntax: `${VAR_NAME}` — works inside any string field.

Special placeholder: `${WORKSPACE}` resolves to `WareHouse/<session>/code_workspace/` at runtime. Used in `mcp_local.cwd` to pin local MCP servers to the session workspace.

Unresolved variables → `ConfigError` at parse time, with the YAML path as `path`.

**Two distinct uses of `vars:`**:

- **Parameterization** — model names, API keys, URLs, environment-specific values.
- **Prompt templating (DRY)** — common preambles referenced inside many agents' `role:` strings as `${COMMON_PROMPT}`, avoiding copy-paste.

## Node types

Every node has `name` (unique identifier within the graph) and `type` (the discriminator). Type-specific fields live under `config:`.

### `agent` — LLM call

```yaml
- name: <unique>
  type: agent
  config:
    provider: <provider-name>          # e.g., anthropic, openai, gemini
    name: <model-id>                   # e.g., claude-sonnet-4-5-20250929
    role: <system-prompt-string>       # supports ${VAR} interpolation
    context_window: 0                  # 0 or -1 = unbounded; positive int = sliding window
    input_mode: messages               # default; controls how upstream Messages are framed
    temperature: 0.7                   # provider-specific
    top_p: 1.0
    seed: <int>                        # reproducibility, provider permitting
    # Optional sidecars:
    memories: [...]                    # see memory.md
    thinking: { ... }                  # see thinking.md
    tooling: { ... }                   # see tooling.md
    skills: [skill-name-1, ...]        # project skills under .agents/skills/
    retry: { enabled: true, max_attempts: 5, ... }   # default-on; see below
```

**Retry defaults**: `enabled: true`, `max_attempts: 5`, exponential-ish backoff (1–6s), retry codes `[408, 409, 425, 429, 500, 502, 503, 504]`. Most authors won't touch this.

**Multimodal**: agents like `gemini-2.5-flash-image` can both consume and emit image content. Image inputs (from uploads) become `image` MessageBlocks; image outputs flow through the standard message channel and auto-promote to artifacts via `WorkspaceArtifactHook`.

### `python` — script run in shared workspace

```yaml
- name: <unique>
  type: python
  config:
    script: ./path/to/script.py        # relative to the workflow YAML
    interpreter: /path/to/python       # optional; e.g., a venv-specific Python
    args: ["--flag"]                   # optional CLI args
    env: { KEY: VALUE }                # extra env vars
    encoding: utf-8                    # default
```

**I/O contract**: stdout becomes the node's output Message. The script runs in `WareHouse/<session>/code_workspace/`; all python nodes in one execution share this directory. Files written here auto-promote to artifacts.

### `human` — UI prompt

```yaml
- name: <unique>
  type: human
  config:
    prompt: "What should I do next?"
    attachments_allowed: true          # allow file uploads in the Web UI
```

The UI surfaces the prompt; the user's response becomes the node's output Message, with any uploaded attachments referenced via `attachment_id`.

### `subgraph` — nested workflow

Two YAML shapes:

```yaml
# Inline
- name: <unique>
  type: subgraph
  subgraph:
    type: config
    graph:
      id: ...
      start: [...]
      end: [...]
      nodes: [...]
      edges: [...]

# Referenced
- name: <unique>
  type: subgraph
  subgraph:
    type: file
    path: ./other.yaml
```

`vars` cascade from parent. `memory` can be subgraph-local. Don't nest circularly. The subgraph's `start` and `end` define the in/out boundary.

### `passthrough` — last-message filter / wire helper

```yaml
- name: <unique>
  type: passthrough
  config:
    only_last_message: true            # default: true — filters to last message
```

Two canonical roles:

1. **Entry-node task-keeper** — combined with `keep_message: true` on each outgoing edge, every downstream branch sees the user's original input untouched.
2. **Post-loop result-filter** — compresses many intermediate iterations into the single final result, dropping iteration noise.

Plain wire-management is the tertiary case; mostly use passthrough for the two roles above.

### `literal` — static prompt injection

```yaml
- name: <unique>
  type: literal
  config:
    content: "Now you write the implementation."
    role: user                         # user / assistant / system; default user
```

`role:` matters for downstream agents:
- `user` injects as a user turn, prompting the agent to respond.
- `assistant` injects as conversation history, framing the agent's perspective.
- `system` injects as a system message, conditioning behavior.

Used in Pattern 17 to mark phase boundaries in multi-phase workflows.

### `loop_counter` — bounded-iteration guard

```yaml
- name: <unique>
  type: loop_counter
  config:
    max_iterations: 5                  # default 100
```

See Pattern 6 in `pattern_gallery.md` for the four-edge wiring topology. Output fires only when the count is reached.

### `loop_timer` — wall-clock-bounded guard

```yaml
- name: <unique>
  type: loop_timer
  config:
    max_duration: 5
    duration_unit: minutes             # seconds / minutes / hours
```

Same wiring topology as `loop_counter`. Timer starts on the first trigger to the timer node — *not* at workflow start. `duration_unit` is mandatory.

## Naming-collision callouts

- **`config.skills`** on agent nodes refers to project-level Markdown skills under `.agents/skills/` — *not* the Anthropic-style skill you're authoring with. The runtime exposes them via `activate_skill` + `read_skill_file` built-in tools.
- **Class names diverge from YAML `type:` strings**: e.g., the YAML uses `type: python` but the internal class is `PythonRunnerConfig`. Visible when reading schema-validate errors.
