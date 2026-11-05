---
name: engineering-workflow
description: >-
  Primary entry point for the Senior Full-Stack Developer Plugin. Load this Skill first when the user
  invokes `@senior-fullstack-developer` or asks to build or implement a non-trivial frontend, backend,
  or full-stack feature. It provides repository-aware routing, incremental delivery, focused validation,
  and an internal quality audit. Do not use it for tiny edits, pure explanation, formal code-review-only
  requests, or non-coding work.
---

# Engineering Workflow

## Procedure

1. Establish the repository contract before choosing a solution.
   - Read applicable instruction files, package manifests, neighboring implementations, imports, tests, and current Git state.
   - Infer stack, conventions, and acceptance criteria from the repository and user context; ask only for unresolved decisions that materially change the implementation.

2. Route specialized work only when it adds value.
   - Load `senior-fullstack-developer:frontend-dev` for substantial UI architecture, responsive behavior, accessibility, motion, design-system, or visual asset work.
   - Load `senior-fullstack-developer:fullstack-dev` for cross-layer features involving APIs, authentication, databases, queues, caches, uploads, real-time behavior, or production hardening.
   - Do not reload a specialized Skill already loaded for the current task. After specialized work, resume this workflow at step 5 so validation and Code Review are not skipped.
   - Handle small, obvious changes directly instead of adding a heavyweight workflow.

3. Plan in proportion to the task.
   - Use a visible todo list for multi-step work and keep one item active at a time.
   - When the user asks to approve a plan, stop after presenting the implementation and validation plan. Otherwise continue without adding an unnecessary approval gate.

4. Implement incrementally.
   - Reuse existing libraries and patterns; verify dependencies before importing them.
   - Keep each change coherent and avoid unrelated refactors.
   - Preserve security, permission, data, timestamp, cross-platform, and repository-specific boundaries.

5. Validate at the affected surface.
   - Run focused unit or integration tests when behavior changes.
   - Run relevant typecheck, lint, build, schema, or contract checks when those surfaces are touched.
   - When a real UI path needs verification, find the Browser Use Plugin Skill in the current turn's Skill catalog and follow its session load/reload rules. When loading is required, fully load its exact namespaced entry (for example, `browser-use:control-in-app-browser`, only if listed) as the only tool call in that step and wait for its complete result; reuse an unchanged valid load according to the Browser Skill.
   - Call the Browser Use Plugin's Host-backed `mcp_browser({action, input})` directly using the current `mcp_browser` tool schema. Follow the Browser Skill's safety and session/tab rules; do not guess targets or parameters or add another Browser tool or Host Binding.
   - Exercise the relevant user path on the actual rendered page and verify its observable result. A build, curl response, HTML source, or unit test alone is not Browser acceptance.
   - If the Skill, `mcp_browser` tool/schema, or Browser capability is missing, disabled, or unavailable, report “浏览器验收未执行” (or its equivalent in the user's language) with the exact blocker. Complete independent checks without claiming the UI passed. For a disabled Plugin, direct the user to Plugin management; do not enable it automatically or use the legacy Browser enable flow.
   - Do not substitute repeated flaky reruns for diagnosis.

6. Run a Code Review pass after the initial validation.
   - Ask the model to perform a Code Review of the current task's diff and only the callers needed to judge it.
   - When the host exposes a `code-review` Skill, load and follow it for a read-only findings pass; otherwise apply the same review dimensions directly.
   - Review correctness, error handling, boundary cases, security, permissions, data loss, concurrency, contract drift, test evidence, and accidental scope growth.
   - Return to implementation mode after the findings pass. Fix actionable issues introduced by the current change, rerun the affected checks, and inspect the final diff again.
   - Unless the user explicitly asks for a standalone review report, summarize resolved findings and only call out remaining risks in the final delivery.

7. Deliver honestly.
   - State what changed, what was validated, what was not run, and any remaining risk.
   - Do not claim Browser validation, deployment, tests, commits, pushes, or publication unless they actually completed.
   - When the host supports local processes and can expose a local interactive preview URL, do not stop its backing server before the user has had a chance to use it.
   - Do not run a long-lived preview server with a background task that waits for process completion, or with a foreground shell containing an unmanaged trailing `&`.
   - When available, start preview servers through a host-supported detached process with a PID file and log file, then perform a bounded readiness check of at most 30 seconds.
   - If a host-supported local preview hits a port conflict, choose one session-specific alternate port and retry once. Never inspect, kill, or reuse another session's server. If the retry fails, stop and report the blocker.
   - For a successful local preview handoff, report the exact preview URL, effective port, and observed server liveness.
   - After a local preview handoff, do not wait for the preview server to exit or keep the turn active solely because it remains running.
   - If the preview server must be stopped, state beforehand that the delivered local URL will stop working.
   - If the host does not expose stable local-process, port, or preview-URL handoff capabilities, do not invent a localhost bridge or treat that absence as an implementation failure. Use a host-provided preview surface when available; otherwise deliver the validated code and report interactive preview as unverified.

## Host capability boundaries

- Use host-native tools instead of recreating file, shell, Browser, media, deployment, or review integrations inside this Plugin.
- Deploy a website only when the user explicitly asks. Prepare and validate the build first, then follow the host's public-publication confirmation and source-upload rules immediately before deployment.
- The host website deployment capability publishes static frontend build artifacts only. Do not use it to deploy backend services, databases, workers, containers, or SSR runtimes.
- For a full-stack project, deploy only the validated static frontend when requested and report backend deployment as unsupported or separately owned.
- Do not add API keys, direct vendor HTTP calls, or fallback scripts merely because a host capability is unavailable.

## Output contract

Return the implemented result or analysis in the user's language, with concise file references and a validation summary. For a file deliverable, use the host's delivery mechanism rather than reporting an inaccessible filesystem path.

## Failure handling

- If repository rules conflict with this Skill, follow the repository rules and report the constraint.
- If a required host capability is absent, complete independent work and explain the unsupported step without inventing a substitute integration.
- If validation cannot run because of an external dependency, distinguish that from a product failure and report the evidence available.
