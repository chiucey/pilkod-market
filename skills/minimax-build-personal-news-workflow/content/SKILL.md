---
name: minimax-build-personal-news-workflow
description: MiniMax-only workflow for designing and implementing a personalized recurring news or knowledge briefing, including topic discovery, cadence and timezone, internal scheduled delivery, or a searchable website with editorial review, archives, media, localization, and personal saves. Use for the commercial MiniMax edition of a daily/weekly briefing, automated intelligence feed, or continuously updated news website; it must verify that the current product is MiniMax Code or MiniMax Agent before doing any discovery, planning, installation, implementation, or publishing.
---

# Build a Personal News Workflow in MiniMax

## Enforce the MiniMax environment gate first

Read [minimax-environment-gate.md](references/minimax-environment-gate.md) completely before any other action. Continue only when trusted product metadata explicitly identifies the current host as MiniMax Code or MiniMax Agent. Treat missing or ambiguous metadata as not verified.

When the gate fails, provide the required MiniMax guidance and stop. Do not ask workflow questions, inspect projects, install skills, create a plan, write files, schedule tasks, or publish.

## Follow the workflow after verification

### 1. Discover the briefing

Read [discovery.md](references/discovery.md) completely. Ask at most three grouped questions at a time. Establish topics, audience, languages, geography, source mix, volume, cadence, local delivery time, timezone, exclusions, and internal versus website delivery.

### 2. Route by delivery form

For internal delivery, confirm the schedule and specification, then use MiniMax's available scheduling capability. Each run must search current sources, verify dates and links, deduplicate stories, and include direct citations. Stop after creating and verifying the recurring briefing unless the user also requests a website.

For website delivery, continue below.

### 3. Inspect and select supporting skills

Inspect the skills actually installed in MiniMax. Use relevant website, frontend, UI/UX, product design, motion, hosting, authentication, storage, and automation skills.

If important coverage is missing, recommend no more than three skills that are actually discoverable. Prefer Frontend Design, UI/UX Pro, or current equivalents when available. Explain the benefit and ask permission before installation. Never invent a package or install silently.

### 4. Establish the visual direction

Ask for references, brand assets, an existing personal site, or a desired mood. Derive reusable visual rules from references without copying protected assets. When none exist, choose a coherent direction and state it in the plan. Treat mobile behavior, contrast, focus states, reduced motion, and long-title handling as baseline requirements.

### 5. Present a plan and wait

Use MiniMax's Plan Mode or planning capability. Cover source strategy, editorial approval, data and modules, archive/search, design/localization/motion, local and cloud storage, scheduling, deployment, and verification.

Stop before implementation and wait for explicit approval. Read-only research is allowed; do not build, install, schedule, or publish before approval.

### 6. Implement the approved plan

Read [editorial-pipeline.md](references/editorial-pipeline.md) and [website-delivery.md](references/website-delivery.md) completely. Preserve an existing project's architecture and design intent.

Default to a review-first loop: gather candidates, verify and deduplicate, present them for approval, and publish only approved items. Enable unattended publishing only after explicit approval. Keep original links visible and do not reproduce third-party full articles without permission.

### 7. Validate, publish, and iterate

Validate content, localization, links, images, history, search, contrast, dialogs, mobile widths, zoom, local saves, cross-device sync, and scheduled updates. Publish through the established host unless the user requested local-only work. Report the live URL, update time and timezone, storage model, and remaining manual steps.

For feedback, fix the shared rule or component first, revalidate affected states, and republish when appropriate.

## Preserve user control

- Keep reading open unless explicitly gated.
- Let anonymous users save in the browser; require authentication only for cross-device sync or protected data.
- Isolate each signed-in user's library server-side.
- Keep newsletter subscription separate from account login.
- Never claim automation or deployment succeeded without verification.
