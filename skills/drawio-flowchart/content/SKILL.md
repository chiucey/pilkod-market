---
name: drawio-flowchart
description: Create editable draw.io / diagrams.net flowchart documents from process descriptions, approval workflows, swimlane diagrams, or step-by-step procedures. Use when the user asks for 流程图, 泳道图, 审批流, workflow diagram, or specifically wants a .drawio document as the output.
---

# Drawio Flowchart

## Overview

Use this skill when the deliverable should be an editable `.drawio` file rather than a PNG, Mermaid snippet, or plain-text outline.

The preferred workflow is:

1. Start from natural language whenever possible.
2. Convert the text into a compact JSON spec.
3. Run the bundled generator to produce a `.drawio` document.
4. Return the output path and briefly note any assumptions you made.

## Workflow

### 1. Normalize the process

Translate the request into:

- `title`: diagram title
- `layout`: `flowchart` or `swimlane`
- `lanes`: roles/departments when the process spans multiple actors
- `nodes`: steps, decisions, notes, inputs, endings
- `edges`: connections and branch labels such as `是/否`, `通过/驳回`

Prefer stable short node ids such as `submit_request`, `manager_review`, `finish`.

If the user gives prose, prefer the bundled parser instead of hand-writing JSON:

```bash
python3 /Users/zhuhan/Desktop/朱朱/skills/drawio-flowchart/scripts/text_to_spec.py \
  --input /absolute/path/to/process.txt \
  --output /absolute/path/to/process.spec.json
```

Or generate the final `.drawio` file in one step:

```bash
python3 /Users/zhuhan/Desktop/朱朱/skills/drawio-flowchart/scripts/text_to_drawio.py \
  --input /absolute/path/to/process.txt \
  --output /absolute/path/to/process.drawio \
  --spec-output /absolute/path/to/process.spec.json
```

### 2. Choose the right layout

- Use `flowchart` for a single-lane process.
- Use `swimlane` when the user describes roles, departments, systems, or responsibilities.
- In `flowchart` mode, use `column` when branches should appear side by side.
- In either mode, use `phase` to control vertical order and keep the result readable.
- Prefer BPMN-style node types for approvals, workflows, service orchestration, or handoffs between teams and systems.

### 3. Generate the `.drawio` file

Write a JSON spec, then run:

```bash
python3 /Users/zhuhan/Desktop/朱朱/skills/drawio-flowchart/scripts/generate_drawio.py \
  --spec /absolute/path/to/spec.json \
  --output /absolute/path/to/output.drawio
```

Do not hand-write large draw.io XML unless the script is unavailable or the requested layout is outside the script's supported scope.

## Supported Node Types

The generator still accepts the old simple aliases:

- `start`
- `process`
- `decision`
- `end`
- `data`
- `document`
- `note`

For BPMN-style output, prefer these richer node types:

- `start_event`
- `intermediate_event`
- `message_event`
- `timer_event`
- `end_event`
- `terminate_end`
- `task`
- `user_task`
- `service_task`
- `manual_task`
- `subprocess`
- `gateway_exclusive`
- `gateway_parallel`
- `gateway_inclusive`
- `data_object`
- `document`
- `note`

Supported edge types:

- `sequence`
- `message`
- `association`

## Practical Rules

- In `swimlane` mode, define `lanes` explicitly when order matters.
- If the user gives messy prose, first extract the real nodes and edges; do not mirror every sentence into the chart.
- For natural-language parsing, line-oriented text works best: `角色: 动作`, `通过 -> 下一步`, `驳回 -> 下一步`.
- Edge labels belong on `edges[].label`, not inside node text.
- Keep node text short. Break long text into 1-2 lines only when it materially improves readability.
- If the process is ambiguous, make the smallest reasonable assumption, finish the file, and mention that assumption in your response.
- Save the final artifact as a `.drawio` file in the working directory unless the user asks for another path.

## Minimal Spec

```json
{
  "title": "请假审批流程",
  "layout": "swimlane",
  "lanes": [
    { "id": "employee", "label": "员工" },
    { "id": "manager", "label": "主管" },
    { "id": "hr", "label": "人事" }
  ],
  "nodes": [
    { "id": "submit", "text": "提交申请", "type": "start", "lane": "employee", "phase": 0 },
    { "id": "review", "text": "审批", "type": "decision", "lane": "manager", "phase": 1 },
    { "id": "archive", "text": "登记备案", "type": "process", "lane": "hr", "phase": 2 },
    { "id": "reject", "text": "结束", "type": "end", "lane": "employee", "phase": 2 },
    { "id": "finish", "text": "结束", "type": "end", "lane": "employee", "phase": 3 }
  ],
  "edges": [
    { "from": "submit", "to": "review" },
    { "from": "review", "to": "archive", "label": "通过" },
    { "from": "review", "to": "reject", "label": "驳回", "dashed": true },
    { "from": "archive", "to": "finish" }
  ]
}
```

## References

- Read `references/spec-format.md` when you need the full JSON field reference.
- Read `references/example-spec.json` for a complete working example.
- Read `references/natural-language-format.md` for the natural-language parser format.
- Read `references/example-text.txt` for a complete natural-language example.
