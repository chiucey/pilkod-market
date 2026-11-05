---
name: fullstack-dev
description: >-
  Implement substantial cross-layer software after `engineering-workflow` routes full-stack work, or
  when the user explicitly invokes this Skill by name. For a Plugin-level request such as
  `@senior-fullstack-developer`, load `senior-fullstack-developer:engineering-workflow` first if it is
  not already loaded. Covers frontend/backend contracts, APIs, authentication, databases, transactions,
  caching, background jobs, uploads, real-time communication, reliability, and production hardening.
  Do not use it for tiny isolated edits, frontend-only visual work, pure explanation, or formal review-only requests.
---

# Full-Stack Development

## Inputs to collect

Infer the stack, deployment model, persistence layer, integration boundaries, and existing architecture from repository files. Ask only for unresolved requirements that change data ownership, trust boundaries, compatibility, migration strategy, or externally visible behavior.

## Procedure

If this Skill was selected from a Plugin-level request and `engineering-workflow` has not been loaded for the current task, load `senior-fullstack-developer:engineering-workflow` before implementation. When it routes back here, do not reload either Skill.

1. Map the existing system.
   - Read applicable instructions, service entry points, package manifests, API contracts, schemas, migrations, configuration, tests, and relevant callers.
   - Load only the references needed for the current decision; do not preload or restate the whole reference set.
   - Follow existing boundaries unless evidence shows they cannot support the requested behavior.

2. Define the contract before implementation.
   - Specify request/response shape, validation, authentication, authorization, error semantics, idempotency, pagination, and compatibility requirements as applicable.
   - Decide where data is authoritative and which layer owns each state transition.
   - Read `references/api-design.md` and `references/auth-flow.md` when those surfaces are involved.

3. Design data changes safely.
   - Prefer additive, reversible migrations and explicit transaction boundaries.
   - Consider uniqueness, indexes, concurrency, retention, backfill, rollback, and partial-failure behavior.
   - Read `references/db-schema.md` before schema or persistence changes.

4. Choose architecture proportionally.
   - Preserve the repository's established structure; do not force controller/service/repository, feature-first, microservices, or another pattern onto every codebase.
   - Introduce a new boundary only when it reduces concrete coupling, clarifies ownership, or protects a contract.
   - Use `references/architecture-patterns.md` and `references/technology-selection.md` as decision aids rather than mandatory templates.

5. Implement the vertical slice.
   - Wire persistence, domain behavior, API, client state, UI states, and observability needed for one coherent user outcome.
   - Keep configuration externalized without adding unnecessary environment files.
   - Avoid logging secrets, credentials, raw tokens, or sensitive payloads.

6. Cover reliability and operations.
   - Add typed errors, timeouts, retry/backoff only for safe operations, idempotency where duplicates are possible, and structured observability appropriate to the system.
   - For caches, queues, uploads, webhooks, SSE, or WebSockets, define ownership, expiry, delivery guarantees, reconnection, and failure recovery.
   - Read `references/environment-management.md` and `references/release-checklist.md` for production-facing changes.

7. Validate the changed behavior.
   - Cover important success, failure, permission, validation, concurrency, and boundary paths with the repository's focused tests.
   - Verify migrations, generated contracts, type safety, and relevant builds when touched.
   - Read `references/testing-strategy.md` for test selection; framework-specific guidance such as `references/django-best-practices.md` applies only when the repository actually uses that framework.

8. Coordinate substantial UI work.
   - Load `senior-fullstack-developer:frontend-dev` when the feature includes meaningful interaction design, responsive behavior, accessibility, motion, or visual asset work.

## Output contract

Deliver a coherent vertical slice with concise file references, contract and migration notes where relevant, validation results, and explicit remaining operational or compatibility risks. For plan-only requests, default to a compact decision record covering repository facts, ownership, implementation slices, validation, and blockers. Do not reproduce generic textbook material, exhaustive schemas, or every reference checklist; expand only where omission would make a high-risk decision unsafe.

## Failure handling

- If an external service, credential, or environment blocks end-to-end validation, complete local contract and test work that remains meaningful, then identify the exact unverified boundary.
- If a migration or compatibility plan is unsafe or irreversible, stop before applying it and explain the risk and safer alternative.
- If repository evidence contradicts generic guidance in the references, follow the repository and document the decision only when it affects maintainers.
