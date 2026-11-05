---
name: frontend-dev
description: >-
  Implement substantial production frontend experiences after `engineering-workflow` routes UI work,
  or when the user explicitly invokes this Skill by name. For a Plugin-level request such as
  `@senior-fullstack-developer`, load `senior-fullstack-developer:engineering-workflow` first if it is
  not already loaded. Covers responsive layouts, accessibility, interaction states, motion systems,
  data-heavy UI, marketing pages, and local visual assets. Do not use it for tiny copy/color/spacing
  edits, backend-only work, or visual critique without implementation.
---

# Frontend Development

## Inputs to collect

Infer the framework, component system, package manager, target browsers, data contract, and existing design language from the repository. Ask only for missing product decisions that materially change user flow, information architecture, brand direction, or accessibility requirements.

## Procedure

If this Skill was selected from a Plugin-level request and `engineering-workflow` has not been loaded for the current task, load `senior-fullstack-developer:engineering-workflow` before implementation. When it routes back here, do not reload either Skill.

1. Inspect before designing.
   - Read the relevant package manifest, route/page entry, neighboring components, style system, assets, tests, and repository UI standards.
   - Confirm required libraries exist before using them; prefer the project's established framework and component patterns.

2. Define the user path and UI states.
   - Identify the primary task, hierarchy, navigation, loading, empty, error, success, disabled, and permission states.
   - Preserve semantic HTML, keyboard access, focus visibility, labels, contrast, reduced-motion behavior, and screen-reader meaning.

3. Choose a coherent visual direction.
   - Derive typography, spacing, color, density, and composition from the product context instead of applying a fixed style to every project.
   - Use `references/design-rules.md` as guidance, not as authority over an existing design system.
   - Keep responsive behavior intentional across narrow, medium, and wide layouts; prevent overflow and fragile fixed sizing.

4. Add motion only when it improves comprehension.
   - Prefer CSS transitions for simple state changes, a framework animation library for component lifecycle motion, GSAP for timelines, and Three.js only for genuine 3D requirements.
   - Read `references/motion-recipes.md` before complex motion work.
   - Animate transform and opacity where possible; respect reduced motion and avoid blocking interaction.

5. Use host-native media capabilities when assets are required.
   - Read `references/host-media-tools.md` before generating images, video, speech, or music.
   - Save generated assets inside the active workspace and reference local project files.
   - Do not request or expose Pilkod API keys, call vendor APIs with Python/curl, or bundle a fallback client.

6. Implement in small, testable slices.
   - Reuse components and tokens where that improves consistency without forcing a broad refactor.
   - Keep data fetching, state ownership, validation, and error rendering explicit.
   - Avoid adding dependencies when existing primitives are sufficient.

7. Validate observable behavior.
   - Before Browser validation, define the smallest applicable checklist. Do not add scenarios merely because more checks are possible.
   - Run focused UI tests for semantic, accessibility, state, interaction, responsive, overflow, or drag behavior changes.
   - For pure visual styling, use targeted visual inspection when available rather than brittle class or pixel snapshots.
   - For a real user path, find the Browser Use Plugin Skill in the current turn's Skill catalog and follow its session load/reload rules. When loading is required, fully load its exact namespaced entry (for example, `browser-use:control-in-app-browser`, only if listed) as the only tool call in that step and wait for its complete result; reuse an unchanged valid load according to the Browser Skill.
   - Call the Browser Use Plugin's Host-backed `mcp_browser({action, input})` directly using the current `mcp_browser` tool schema. Follow the Browser Skill's safety and session/tab rules; do not guess targets or parameters or implement another Browser tool or Host Binding.
   - When Browser validation is applicable, cover at least one primary happy path and one relevant error or permission path.
   - For CRUD products, exercise the main write path through its observable saved result rather than inspecting only static pages.
   - Check narrow-screen or responsive behavior when it is in scope and the host can expose an appropriate viewport; otherwise report it as unverified.
   - Once every checklist item has sufficient evidence, stop Browser exploration and proceed to review or delivery.
   - After a Browser action fails, perform at most one inspect-based recovery attempt. If the same path still cannot be verified, record it as unverified and continue.
   - If the Browser Skill, `mcp_browser` tool/schema, or Browser capability is missing, disabled, or unavailable, stop Browser validation and report “浏览器验收未执行” (or its equivalent in the user's language) with the exact blocker. Do not treat build, curl, HTML source, or automated tests as a real-page acceptance pass. Do not wait, reload, or retry in the same turn; direct a disabled-Plugin case to Plugin management without enabling it automatically or using the legacy Browser enable flow.
   - If the host cannot change viewport, emulate reduced motion, or expose another required condition, do not create temporary routes, iframe pages, or alternate applications solely to simulate it. Use existing automated evidence when available; otherwise report it as unverified.

## Templates and fonts

- `templates/` contains optional generative-art scaffolding; use it only when the task explicitly requires generative artwork.
- `canvas-fonts/` contains local font files and their license texts. Copy only selected fonts into the target project and preserve their licensing requirements.
- Do not inject the entire font collection into an application.

## Output contract

Deliver working frontend changes that follow the repository's conventions, plus a short summary of affected user paths, responsive/accessibility behavior, and validation performed. For plan-only requests, keep the answer proportional: summarize repository facts, state/component boundaries, responsive/accessibility decisions, and validation without restating every generic checklist. Report any Browser or visual checks that remain unverified.

## Failure handling

- If the requested visual direction is genuinely ambiguous and changes the product outcome, ask one focused question rather than inventing brand requirements.
- If a desired media or Browser Tool is unavailable, continue with code and existing assets where possible, then report the unavailable validation or generation step.
- If the repository lacks a safe test path, document the manual or external verification still needed without fabricating a pass.
