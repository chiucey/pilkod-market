---
name: notion-meeting-intelligence
description: 结合 Notion 上下文和 Pilkod 调研准备会议材料；适用于收集背景、起草议程或会前阅读材料，并根据参会人调整内容。
metadata:
  short-description: 使用 Notion 上下文准备会议和定制议程
---

# Meeting Intelligence

Prep meetings by pulling Notion context, tailoring agendas/pre-reads, and enriching with Pilkod research.

## Quick start
1) Confirm meeting goal, attendees, date/time, and decisions needed.
2) Gather context: search with `connector__notion__notion-search`, then fetch with `connector__notion__notion-fetch` (prior notes, specs, OKRs, decisions).
3) Pick the right template via `reference/template-selection-guide.md` (status, decision, planning, retro, 1:1, brainstorming).
4) Draft agenda/pre-read in Notion with `connector__notion__notion-create-pages`, embedding source links and owner/timeboxes.
5) Enrich with Pilkod research (industry insights, benchmarks, risks) and update the page with `connector__notion__notion-update-page` as plans change.

## Tool-call guardrails
- Notion tool availability can vary by workspace. If a Notion MCP call returns `Tool <name> not found`, treat that tool as unavailable for the rest of the current task. Do not retry it with different arguments or call it again later; use `connector__notion__notion-search` and `connector__notion__notion-fetch` where sufficient.
- Use one literal search query per `connector__notion__notion-search` call and include `filters: {}` when no narrower filter is needed.
- Only fetch Notion page, database, or data-source URLs/IDs; external connected-source search results are not valid `connector__notion__notion-fetch` inputs.
- Create meeting pages with an explicit `parent` and a `pages` array.
- Query databases with `connector__notion__notion-query-data-sources` under a top-level `data` object, using fetched `collection://...` URLs as table names.
- When editing a page, fetch its current content first and use `connector__notion__notion-update-page` with supported commands such as `update_content` or `update_properties`; on the current deployed surface, use `properties: {}` for `update_content` and `content_updates: []` for `update_properties`. Do not invent insertion-only commands.

## Workflow
### 0) If Notion tools are unavailable, pause and ask the user to connect the Notion app:
1. Enable the bundled Notion app for this plugin or session.
2. Complete the Notion auth flow if Pilkod prompts for it.
3. Restart Pilkod or the current session if the tools still do not appear.

After the app is connected, finish your answer and tell the user to retry so they can continue with Step 1.

### 1) Gather inputs
- Ask for objective, desired outcomes/decisions, attendees, duration, date/time, and prior materials.
- Search Notion for relevant docs, past notes, specs, and action items (`connector__notion__notion-search`), then fetch key pages (`connector__notion__notion-fetch`).
- Capture blockers/risks and open questions up front.

### 2) Choose format
- Status/update → status template.
- Decision/approval → decision template.
- Planning (sprint/project) → planning template.
- Retro/feedback → retrospective template.
- 1:1 → one-on-one template.
- Ideation → brainstorming template.
- Use `reference/template-selection-guide.md` to confirm.

### 3) Build the agenda/pre-read
- Start from the chosen template in `reference/` and adapt sections (context, goals, agenda, owner/time per item, decisions, risks, prep asks).
- Include links to pulled Notion pages and any required pre-reading.
- Assign owners for each agenda item; call out timeboxes and expected outputs.

### 4) Enrich with research
- Add concise Pilkod research where helpful: market/industry facts, benchmarks, risks, best practices.
- Keep claims cited with source links; separate fact from opinion.

### 5) Finalize and share
- Add next steps and owners for follow-ups.
- If tasks arise, create/link tasks in the relevant Notion database.
- Update the page via `connector__notion__notion-update-page` when details change; keep a brief changelog if multiple edits.

## References and examples
- `reference/` — template picker and meeting templates (e.g., `template-selection-guide.md`, `status-update-template.md`, `decision-meeting-template.md`, `sprint-planning-template.md`, `one-on-one-template.md`, `retrospective-template.md`, `brainstorming-template.md`).
- `examples/` — end-to-end meeting preps (e.g., `executive-review.md`, `project-decision.md`, `sprint-planning.md`, `customer-meeting.md`).
