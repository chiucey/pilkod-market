---
name: write-h3-prompts
description: Answer MiniMax H3, H3 Max, or H2.3 capability and billing questions, write prompts, submit new video-creater generation tasks, or recover an existing video-creater provider task. Use when the user explicitly invokes @video-creater or requests MiniMax H3/H3 Max/H2.3. Do not claim unrelated generic video-editing requests merely because they contain reference media.
---

# Write MiniMax-H3 prompts and generate videos

Preserve the user's intent while producing an official-format H3 prompt or a complete video-generation result. Use the mcode-tools Connector for generation. Do not select raw endpoints, handle credentials, call raw HTTP APIs, or silently switch to a different video workflow.

## Route before any other action

Choose exactly one route. This ordering is authoritative.

### 1. Existing provider task: query or recover

This is the highest-priority route. Use it when this session is explicitly query-only, when the user asks about an existing provider task, or when an existing provider `task_id` is supplied.

- Check the persisted task mapping first. If it still has a `polling_cron_task_id` from an older version of this skill, stop that Cron before anything else (see **Stop a leftover Cron** in [generation-lifecycle.md](references/generation-lifecycle.md)). Later automatic checks use the background poller described there, with one-time reminders only as a fallback, never a recurring Cron.
- Follow the registered-task or orphan-task recovery path in [generation-lifecycle.md](references/generation-lifecycle.md). Every automatic query runs in this same owning conversation.
- Read [generation-lifecycle.md](references/generation-lifecycle.md) and jump directly to **Query existing video task**.
- Require the exact model used for the task. If it is missing, ask only for that model and wait; do not guess it.
- Do not draft or revise the prompt.
- Do not preflight or upload reference media, even when the task context contains original reference paths.
- Do not call `ask_user` for generation specifications such as duration, ratio, resolution, or input mode.
- Never call the submit Connector or create another paid request. Never create a child session; the only background work allowed is the query-only poller from [generation-lifecycle.md](references/generation-lifecycle.md).

### 2. Model capability or billing question

Use this information-only route when the user asks whether H3, H3 Max, or H2.3 supports a feature, what it costs, or whether it uses plan usage limits (the M Plan weekly limit or legacy Token Plan) or account credits, without asking to generate or query a video.

- Inspect the live `connector__matrix__submit_video_generation` tool definition before answering a current billing or plan-eligibility question when Connector discovery is available. This inspection is read-only: do not upload media, submit a paid task, query a task, or schedule a timer.
- The current contract is: on M Plan tiers that cover the model, a video is paid from the M Plan weekly limit when the remaining weekly limit can cover the whole video; otherwise it is paid with account credits. Legacy Token Plan usage limits cannot pay for MiniMax-H3 or MiniMax-H3-Max, but MiniMax-Hailuo-2.3 can still use them. MiniMax-Hailuo-2.3 is the lower-cost option and produces silent video. Tier coverage can change, so do not name specific tiers; say that some M Plan tiers cover these models and the product shows the current coverage.
- MiniMax-H3-Max is the fast H3 variant: generation typically completes in about 20 seconds. It follows the same billing as MiniMax-H3 and keeps the same synchronized native audio track — describe dialogue, ambience, and sound effects in the prompt exactly as for H3; native sound needs no reference audio. It supports text-to-video and first/last-frame image-to-video only — a single first frame, a single last frame, or first+last together — with no mid-frame keyframes and no multimodal reference collections (no reference images, videos, or audio). Resolution is 480P or 768P (no 2K); duration is an integer 5–15 seconds; ratio rules match H3.
- Answer the question directly in the user's language. If the live tool definition differs from the current contract recorded here, use the live definition and clearly state the current rule.
- Do not ask for a plan name or screenshot, suggest a paid trial generation, or infer billing from a failed request. The Connector tool definition, not a paid test call, is the billing authority.

### 3. Prompt-only request

Use the prompt-only path when the user asks only for prompt text and not for generation or task recovery.

- Read [h3-prompting.md](references/h3-prompting.md).
- Return the reviewed prompt and brief assumptions without uploading media, submitting, querying, scheduling a timer, or starting a poller.
- Reference media may inform the prompt only when its content is already inspectable. Do not claim details that cannot be inspected.

### 4. New generation request

Use this route only when no existing provider task is being queried or recovered.

#### New generation with reference media

As soon as the user supplies any image, video, or audio reference, read [media-preflight.md](references/media-preflight.md) and complete the model-independent read-only inspection first. If the model is still unknown after inspection, ask only for the model and wait. Do not ask any other generation question. Then finish model-specific classification before loading the prompt-writing reference, drafting, collecting the remaining generation parameters, uploading, discovering Connector tools, submitting, querying, scheduling a timer, or starting a poller.

If the result is `invalid` or `unverified`, send the required main-conversation response and stop. Continue only after the complete batch is `valid`.

#### New generation without reference media

With no reference media, use text-to-video mode and continue directly to prompt drafting and parameter confirmation.

## Draft the prompt

Read [h3-prompting.md](references/h3-prompting.md). Use the official Pilkod guides linked there as the prompt-format authority.

Extract and preserve:

- the generation mode and each reference role;
- the story or communication goal;
- subject identity, setting, visual style, composition, camera behavior, action, continuity, and ending;
- dialogue, lyrics, visible text, ambience, physical sounds, and audience-only music.

Add concrete, observable detail without inventing new characters, claims, dialogue, lyrics, or media facts. Keep dialogue, lyrics, and visible text in their original language. Use restrained assumptions only for non-critical details and disclose them under `Assumptions:`. For missing visible copy, use an English-double-quoted placeholder such as `"[PRODUCT TITLE]"` instead of inventing a brand claim.

Review the prompt against the selected model and mode before generation. The reviewed prompt must be non-empty and within the selected model's limit: 7,000 Unicode code points for MiniMax-H3 and MiniMax-H3-Max, 3,000 for MiniMax-Hailuo-2.3. If it is longer, compress it without removing user-required facts, then review it again.

## Confirm generation specifications

For a new generation request, resolve every remaining required choice after any supplied media has passed preflight. The only earlier exception is the model-only question required to finish model-specific media classification. Use `ask_user` in the user's language, grouping related questions into one concise questionnaire when practical. If `ask_user` is unavailable at any required decision point, ask the same question directly in the main conversation and wait.

Required choices:

- model: H3 (`MiniMax-H3`), H3 Max (`MiniMax-H3-Max`), or H2.3 (`MiniMax-Hailuo-2.3`);
- input mode and every reference role;
- duration;
- ratio when the mode requires a concrete ratio;
- resolution;
- any crop, trim, framing, or semantic-edit choice that materially changes user content.

Ask only about required choices that are still missing, such as the resolution or duration. A value the user has already given explicitly, in the message, in a `<video-generation-options>` block, or in an earlier answer, is settled: do not ask about it again, and do not add a final confirmation step before submitting. When every required choice is settled, continue to **Generate and deliver** without asking.

If the user says only “H3”, treat it as `MiniMax-H3`. If the user says “H3 Max” (also “h3-max” / “h3max”), treat it as `MiniMax-H3-Max` and do not re-ask the model choice. If no model was chosen, recommend H3 for quality, mention H3 Max as the fast option (about 20 seconds, 480P/768P, keyframes only, no multimodal references), explain that H2.3 is the lower-cost silent option, disclose the billing rule above (M Plan weekly limit on tiers that cover the model, otherwise account credits; legacy Token Plan usage limits pay only for H2.3), and ask the user to choose. Never send the legacy model value `Hailuo-3`.

Do not silently choose a default unless the user explicitly delegates that choice. Do not schedule a query before the specifications are confirmed and a provider task exists.

## Generate and deliver

Read [generation-lifecycle.md](references/generation-lifecycle.md) after the prompt, media, and specifications are ready. Follow its live-schema validation, URL upload, submit-exactly-once, main-conversation scheduling, recovery, atomic download, and final asset-delivery requirements.

The owning conversation submits a new paid task exactly once. After receiving the provider `task_id`, persist the mapping and start one background poller: a `bash` call with `run_in_background: true` that runs the exact template in [generation-lifecycle.md](references/generation-lifecycle.md). The poller queries that provider task every 30 seconds and exits at the first terminal status or at the 2-hour cutoff, so the runtime wakes this conversation once, when there is a result. It never submits, uploads, or edits media. Do not poll with a recurring Cron, `task`, a child session, or a new session. Use one-time `self_reminder` checks only as the fallback when background bash is unavailable.

MiniMax-H3 generation usually takes a few minutes. Tell the user once that the video is being generated in the background and will appear here automatically; do not promise a check interval. When the completion notice arrives, read the poller with `task_output` and handle its result in that turn. Stop automatic checks after 2 hours. Do not create Todo/Progress records or emit custom progress markup; the runtime shows the background task itself.

MiniMax-H3-Max and MiniMax-Hailuo-2.3 are much faster: H3-Max typically completes in about 20 seconds and H2.3 within about 1 minute. They use the same poller; right after starting it you may wait in the current turn with `task_output` (`wait_ms: 30000`, at most twice) and deliver in the same turn when it finishes.

Do not report success until the final playable local MP4 is emitted through the original workflow in a `<deliver-assets>` block.

In every terminal owner turn, complete the provider query and all download or validation work before the final non-empty user-facing answer. Keep that answer to the playable video plus concise necessary context, and do not call tools after it. Follow the exact terminal-response shape in [generation-lifecycle.md](references/generation-lifecycle.md).
