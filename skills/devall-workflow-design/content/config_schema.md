---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: af522f317046ac0f92d9bd8cef508fda
    PropagateID: af522f317046ac0f92d9bd8cef508fda
    ReservedCode1: 3044022047444afd981c4842c38b3079088574ce9977bc311e41473ce6aed4af7814d07f022015315d13cbe93cfaa1dfdf88a1e5893678c90e5ecd4751f711aec909eaa1c030
    ReservedCode2: 3044022005004caafb3a856b12882aa1d34a9ef04dc8f24e19b874308dc161c2a38963010220539d9ffe35ba6cf7d83c092d9e9c59f9c9d6e25f65d364dadeacf2149a93e04b
---

# Config Schema API

Pre-flight validation and schema introspection. Use these whenever a workflow won't parse and the error message is opaque.

## Validation endpoint

```http
POST /api/config/schema/validate
Content-Type: application/yaml

<your workflow YAML>
```

Response on success:

```json
{ "valid": true }
```

Response on config error:

```json
{
  "valid": false,
  "error": "<human-readable message>",
  "path": ["workflow", "nodes", 3, "config", "memories"],
  "schema": { "...the expected schema at that path..." }
}
```

The `path` array is a JSON-pointer-like locator. Walk it down the YAML to find the exact field. The `schema` object shows what the parser expected — read it to understand the type, enum, required fields.

HTTP error codes:
- `400` — malformed YAML (parse error before schema check).
- `422` — schema endpoint received an invalid breadcrumb (when using `/schema/introspect`).
- `200` with `valid: false` — YAML parsed but failed schema validation.

## CLI inspector

```bash
python run.py --inspect-schema --schema-breadcrumbs DesignConfig.graph.nodes.NodeConfig.config
```

Returns the schema the parser expects at any breadcrumb. Useful when:

- You don't recognize a class name in an error message.
- You want to see the live enum for a field (e.g., `FunctionToolEntryConfig` shows the on-disk function catalog at runtime).
- You're authoring against a deployment with custom-registered node types or tooling.

### Common breadcrumbs

| Breadcrumb | What you see |
|---|---|
| `DesignConfig` | Top-level YAML schema |
| `DesignConfig.graph` | `GraphConfig` — id, start, end, nodes, edges, memory |
| `GraphConfig.nodes` | The discriminated-union of all node types |
| `GraphConfig.edges.EdgeConfig` | Full edge schema with all flags |
| `NodeConfig.AgentConfig.config` | Agent-specific config including memories/thinking/tooling |
| `FunctionToolEntryConfig` | The live function catalog enum |
| `MemoryConfig` | Memory store discriminated union |

## Error contract

The error contract is uniform across the platform: every config error gives `{error, path}`. This is the same machinery that produces error messages at runtime; treating it as your friend speeds debugging.

When an error mentions a class name (e.g., `MCPLocalConfig`), pair the name with `--inspect-schema --schema-breadcrumbs <ClassName>` to see the full schema.

## Vocabulary the schema uses

The schema introspection uses these canonical class names — the same names you'll see in error messages:

- `DesignConfig` — top-level YAML root
- `GraphConfig` — `graph:` contents
- `NodeConfig` — base class for items in `nodes[]`, with discriminator-keyed subclasses
- Per-node-type subclasses: `AgentConfig`, `PythonRunnerConfig`, `LiteralConfig`, `PassthroughConfig`, `LoopCounterConfig`, `LoopTimerConfig`, `SubgraphConfig`, `HumanConfig`
- `EdgeConfig` — items in `edges[]`
- `MemoryConfig` — base; subclasses for `simple` / `file` / `blackboard`
- `ToolingConfig` — base; subclasses for `function` / `mcp_remote` / `mcp_local`
- `ThinkingConfig` — base; subclasses for `reflection` etc.

Note that **internal class names diverge from YAML `type:` strings**. The YAML uses `type: python`, but the class is `PythonRunnerConfig`.

## Schema doc inconsistencies

Two known inconsistencies in the schema documentation that you might encounter:

- One example uses `workflow:` as the top-level key with a `name:` field; every other doc uses `graph:` with no `name:`. Author against `graph:`.
- One example shows the `NodeConfig.type` enum as `["model", "python", "agent"]` but no authoring doc references a `model` type. Use `agent` for LLM nodes.
