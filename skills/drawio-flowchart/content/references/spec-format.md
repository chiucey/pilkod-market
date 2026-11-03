# JSON Spec Format

The generator consumes a JSON file with this shape:

```json
{
  "title": "Diagram title",
  "layout": "flowchart",
  "lanes": [],
  "nodes": [],
  "edges": []
}
```

## Top-level fields

- `title`: required string; used as the draw.io page title and visible header.
- `layout`: optional; `flowchart` or `swimlane`.
  Defaults to `swimlane` if lanes exist, otherwise `flowchart`.
- `lanes`: optional array. Only used in `swimlane` mode.
  Each item may be a string or an object:

```json
{ "id": "finance", "label": "财务", "width": 220 }
```

- `nodes`: required array of node objects.
- `edges`: required array of edge objects.

## Node fields

Required:

- `id`: stable unique id
- `text`: visible label

Optional:

- `type`: old aliases still work: `start`, `process`, `decision`, `end`, `data`, `document`, `note`
- `type`: BPMN-style types are preferred for richer output:
  `start_event`, `intermediate_event`, `message_event`, `timer_event`,
  `end_event`, `terminate_end`, `task`, `user_task`, `service_task`,
  `manual_task`, `subprocess`, `gateway_exclusive`, `gateway_parallel`,
  `gateway_inclusive`, `data_object`, `document`, `note`
- `lane`: required for multi-lane swimlane charts
- `phase`: integer vertical ordering hint
- `column`: flowchart-only horizontal grouping hint for parallel branches
- `width`: custom width in px
- `height`: custom height in px
- `style`: raw draw.io style fragment appended to the generated base style

## Edge fields

Required:

- `from`
- `to`

Optional:

- `label`: text shown on the connector
- `type`: `sequence`, `message`, or `association`
- `dashed`: boolean
- `style`: raw draw.io style fragment appended to the generated edge style

## Layout Guidance

- Use `phase` whenever the process has branches, merges, or cross-lane handoffs.
- If `phase` is missing, the script tries to infer vertical order from the edge graph.
- In `flowchart` mode, use `column` to separate sibling branches such as `通过` and `驳回`.
- If multiple nodes land in the same lane and phase, the script stacks them vertically inside that band.

## Good Defaults

- Keep node ids lowercase and stable.
- Keep node text concise.
- Prefer explicit `lanes` order in swimlane diagrams.
- Use `note` for yellow explanatory boxes instead of squeezing long caveats into process nodes.
