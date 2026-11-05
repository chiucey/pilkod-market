---
name: notion-spec-to-implementation
description: 将 Notion 需求转化为实施计划、任务和进度跟踪；适用于落地 PRD 或功能需求，并基于需求创建 Notion 计划和任务。
metadata:
  short-description: 将 Notion 需求转化为实施计划和任务跟踪
---

# Spec to Implementation

Convert a Notion spec into linked implementation plans, tasks, and ongoing status updates.

## Quick start
1) Locate the spec with `connector__notion__notion-search`, then fetch it with `connector__notion__notion-fetch`.
2) Parse requirements and ambiguities using `reference/spec-parsing.md`.
3) Create a plan page with `connector__notion__notion-create-pages` (pick a template: quick vs. full).
4) Find the task database, confirm schema, then create tasks with `connector__notion__notion-create-pages`.
5) Link spec ↔ plan ↔ tasks; keep status current with `connector__notion__notion-update-page`.

## Tool-call guardrails
- Notion tool availability can vary by workspace. If a Notion MCP call returns `Tool <name> not found`, treat that tool as unavailable for the rest of the current task. Do not retry it with different arguments or call it again later; use `connector__notion__notion-search` and `connector__notion__notion-fetch` where sufficient.
- Use one literal search query per `connector__notion__notion-search` call and include `filters: {}` when no narrower filter is needed. Run separate searches for alternate phrasings instead of putting `or` in a single query string.
- Only send Notion page, database, or data-source URLs/IDs to `connector__notion__notion-fetch`; external connected-source search results are not fetch targets.
- Create plans and task pages with explicit `parent` and `pages` fields. For task databases, fetch first and use the returned `collection://...` data source ID.
- To append an implementation section to a spec, fetch the current section text first, then use `connector__notion__notion-update-page` with `command: "update_content"`, `properties: {}`, and exact `old_str` / `new_str` content. For property-only edits, use `command: "update_properties"` with `content_updates: []`; the current deployed schema expects both top-level fields even when one is unused.

## Workflow

### 0) If Notion tools are unavailable, pause and ask the user to connect the Notion app:
1. Enable the bundled Notion app for this plugin or session.
2. Complete the Notion auth flow if Pilkod prompts for it.
3. Restart Pilkod or the current session if the tools still do not appear.

After the app is connected, finish your answer and tell the user to retry so they can continue with Step 1.

### 1) Locate and read the spec
- Search first (`connector__notion__notion-search`); if multiple hits, ask the user which to use.
- Fetch the page (`connector__notion__notion-fetch`) and scan for requirements, acceptance criteria, constraints, and priorities. See `reference/spec-parsing.md` for extraction patterns.
- Capture gaps/assumptions in a clarifications block before proceeding.

### 2) Choose plan depth
- Simple change → use `reference/quick-implementation-plan.md`.
- Multi-phase feature/migration → use `reference/standard-implementation-plan.md`.
- Create the plan via `connector__notion__notion-create-pages`, include: overview, linked spec, requirements summary, phases, dependencies/risks, and success criteria. Link back to the spec.

### 3) Create tasks
- Find the task database (`connector__notion__notion-search` → `connector__notion__notion-fetch` to confirm the data source and required properties). Patterns in `reference/task-creation.md`.
- Size tasks to 1–2 days. Use `reference/task-creation-template.md` for content (context, objective, acceptance criteria, dependencies, resources).
- Set properties: title/action verb, status, priority, relations to spec + plan, due date/story points/assignee if provided.
- Create pages with `connector__notion__notion-create-pages` using the database’s `data_source_id`.

### 4) Link artifacts
- Plan links to spec; tasks link to both plan and spec.
- Optionally update the spec with a short “Implementation” section pointing to the plan and tasks using `connector__notion__notion-update-page`.

### 5) Track progress
- Use the cadence in `reference/progress-tracking.md`.
- Post updates with `reference/progress-update-template.md`; close phases with `reference/milestone-summary-template.md`.
- Keep checklists and status fields in plan/tasks in sync; note blockers and decisions.

## References and examples
- `reference/` — parsing patterns, plan/task templates, progress cadence (e.g., `spec-parsing.md`, `standard-implementation-plan.md`, `task-creation.md`, `progress-tracking.md`).
- `examples/` — end-to-end walkthroughs (e.g., `ui-component.md`, `api-feature.md`, `database-migration.md`).
