---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 839b46b4b8bb2ea4b77d70dd543cc0a9
    PropagateID: 839b46b4b8bb2ea4b77d70dd543cc0a9
    ReservedCode1: 304502203b7b6ce993ba393c7f9d791fc93dade9cf202a8295d2aaf6ecdf2f90b11e426e022100bcca5e8bc15aef561ced5493d7961d1fdb9b425adf5d43f4ea5075d0974ac585
    ReservedCode2: 3045022100ba76c5da77ac54a4b0ae891b2e69e1f4e42ad05c4c7d98a67e04f2501aedaaa702207b62451a143086de17a34e27f880dadd382230976ebbb9f25afea82bcaac896e
---

# Field Specs (Extension Developer Note)

**This document is for platform extenders, not workflow authors.** If you're writing or modifying a workflow YAML, you don't need this — go to `yaml_and_nodes.md` and `edges_and_conditions.md` instead.

## What FIELD_SPECS does

`FIELD_SPECS` is the field-metadata contract that drives:

- Form rendering in the Web UI (which fields appear, what labels, what enum dropdowns).
- Template export (so the UI can scaffold a node config from defaults).
- The `/api/config/schema` API (which surfaces the dropdowns and enums to IDEs).

When a developer registers a new node type, memory store, thinking mode, or tooling type, they provide a `field_specs()` method that describes the fields. The platform uses that metadata everywhere a form or schema is needed.

## The four registry hooks

```python
register_node_type(name, config_class)
register_memory_store(name, config_class)
register_thinking_mode(name, config_class)
register_tooling_type(name, config_class)
```

Each takes a discriminator string (the YAML `type:` value users will write) and a Pydantic config class. The class's `field_specs()` method drives UI metadata.

Notably **there is no `register_skill_type`** — Agent Skills (in `.agents/skills/`) are project-level Markdown files, not registered Python plugins.

## Dynamic enums

`FunctionToolEntryConfig.field_specs()` builds its function-name enum from the on-disk catalog at runtime. The picker the UI shows is generated from the same files in `functions/function_calling/` that an author references by name in YAML — there's no separate manifest to maintain.

## When to read the full FIELD_SPECS doc

Read the platform's `field_specs.md` documentation directly when:

- You're adding a new node type, memory store, thinking mode, or tooling type.
- You need to control how a config field appears in the Web UI (label, description, default, enum).
- You need to expose runtime-derived enums (e.g., a custom registry that's populated at startup).

For workflow authoring, this is all internal machinery; you'll never write a `field_specs()` method.
