# H3 generation lifecycle

Use this reference for a new paid generation task or for querying/recovering an existing provider task. The mcode-tools Connector is the execution path; do not prefer a similarly named native video tool or call raw HTTP APIs.

Load `mcode-tools-master` before Connector execution. In a managed Cloud sandbox, use injected `sandbox_egress` authentication and do not start interactive login. On Desktop, follow that Skill's authentication guidance. Never bypass TLS verification with `NODE_TLS_REJECT_UNAUTHORIZED=0`, `curl -k`, or an equivalent option.

## Discover and validate the live contract

Confirm that both Connector tools exist:

```text
connector__matrix__submit_video_generation
connector__matrix__query_video_generation
```

Inspect the live Connector schema before every paid submission. For an information-only billing or plan-eligibility question, inspect the same definition without submitting a task. For example:

```bash
mcode-tools connector tool connector__matrix__submit_video_generation
```

The matrix below records the current contract and guides questions, but live schema validation is authoritative when the contract changes. Schema inspection is read-only; never submit a paid task merely to discover billing eligibility. Do not add raw-provider fields that are absent from the Connector schema.

| Model | Current modes | Current duration and resolution | Audio | Billing |
| --- | --- | --- | --- | --- |
| H3, model: `"MiniMax-H3"` | text-to-video, first-frame, last-frame, first+last-frame, multimodal references | required integer 4–15 seconds; `"768P"` or `"2K"` | native synchronized audio from prompt dialogue, ambience, and effects | M Plan weekly limit on tiers that cover it, otherwise account credits; legacy Token Plan usage limits cannot be used; H3 Max bills the same way |
| H2.3, model: `"MiniMax-Hailuo-2.3"` | text-to-video, first-frame, legacy subject | 6 or 10 seconds at 768P; 1080P is valid only for 6 seconds; subject is 6 seconds | output is silent; offer a separate speech-synthesis workflow only when the user asks for voiced output | lower-cost; M Plan weekly limit on tiers that cover it, otherwise account credits; legacy Token Plan usage limits can also be used |

H2.3 does not support last-frame, first+last-frame, or multimodal reference collections. For every H2.3 submit, keep the prompt within 3,000 Unicode code points (H3 and H3 Max allow 7,000) and omit `ratio`, `last_frame_image`, `reference_images`, `reference_videos`, and `reference_audios`. Reject an invalid model, mode, duration, resolution, or ratio combination before submit. Never send the legacy model value `Hailuo-3`.

If the user has not chosen a model, recommend H3 for quality, explain that H2.3 is lower-cost and silent, disclose the billing column above, and ask the user to choose. If the user says only “H3”, map it to `MiniMax-H3`.

## Map input modes to Connector fields

- **Text-to-video:** no media fields. H3 requires a concrete supported ratio; do not silently choose 16:9 unless the user delegated that choice.
- **First frame:** use `input_image` with `reference_type: "first_frame"`. H3 and H2.3 support this path.
- **Legacy subject:** use `input_image` with `reference_type: "subject"`. This is H2.3 only, requires a 6-second duration, and must omit `ratio` and every unsupported H3-only field.
- **Last frame:** use `input_image` with `reference_type: "last_frame"`. This is MiniMax-H3 only.
- **First and last frames:** use `input_image` as the first frame with `reference_type: "first_frame"`, and use `last_frame_image` as the ending frame. This is MiniMax-H3 only.
- **Multimodal references:** use `reference_images`, `reference_videos`, and `reference_audios`. This is MiniMax-H3 only.

Keyframe fields must not be combined with `reference_images`, `reference_videos`, or `reference_audios`. For first-frame, last-frame, and first+last-frame modes, the generated video's aspect ratio will follow the reference image; use the live schema's adaptive/keyframe behavior instead of forcing a concrete ratio.

Before submission, remind the user in their language. For Chinese, use:

> 当前使用首帧/尾帧参考图模式，生成视频的画面比例将按照参考图片的比例确定。

## Upload valid local media

Only media marked `valid` by [media-preflight.md](media-preflight.md) may be uploaded. Connector arguments accept HTTPS URL objects, never local paths, raw bytes, base64, or data URIs.

- Upload a local image or audio file with `mcode-tools upload-temp-url <path> --mime-type <mime-type>` and use its returned HTTPS `temp_url`.
- Upload each local reference video with its detected container MIME type:

  ```bash
  mcode-tools upload-temp-url <video-path> --video-reference --mime-type <detected-mime-type>
  ```

  MP4 uses `video/mp4`; MOV uses `video/quicktime`. Do not relabel one container as the other. Use the returned `reference_video` object unchanged. Its integer `duration_seconds` is derived with `Math.ceil` only after validating the original duration. Keep the returned object order and reject the batch if the integer total exceeds 15.
- A public media URL still needs trustworthy preflight metadata. Do not infer dimensions, codecs, or duration from its name or the requested output duration.

After all URL objects and options are assembled, serialize the exact submit arguments and enforce the 64 MB UTF-8 request-body limit. Never use inline media to work around URL upload requirements.

## Submit exactly once

The owning conversation submits a new task only after prompt review, media preflight, live-schema validation, parameter confirmation, upload, and request-size validation all pass. Poller or scheduler availability is not part of this pre-submit gate.

Call:

```bash
mcode-tools connector call connector__matrix__submit_video_generation --args '<submission JSON>'
```

1. Persist the validated submitted model before calling submit, together with the reviewed request fingerprint needed to identify this workflow. Do not depend on the submit response containing a model. If it does contain one, use it only to verify consistency with the submitted model.
2. Make one paid submit call. Pass the reviewed prompt, selected model, confirmed fields, and HTTPS media objects.
3. Require a non-empty provider `task_id`. This is the only video-task identity used for provider queries.
4. Name the output file after the video content, in the same language as the user's request: a short title of at most 40 characters under `videos/`, such as `videos/海底世界珊瑚鱼群.mp4` for a Chinese request or `videos/coral-reef-dive.mp4` for an English one. Remove `\ / : * ? " < > |` and control characters, trim surrounding spaces and trailing dots, and avoid Windows reserved names such as `CON`, `PRN`, `AUX`, `NUL`, `COM1`, and `LPT1`. If the path already exists or another task in this conversation already uses it, append `-2`, `-3`, and so on. Never reuse a fixed `videos/result.mp4` path across tasks, never overwrite a user file, and never rename the file after it is recorded.
5. Persist this one-to-one record: `provider_task_id -> submitted_model -> output_file_path -> submitted_at_ms -> last_query_at_ms -> poller_task_id -> terminal_status`. The timestamps are Unix milliseconds when a clock is available, and `poller_task_id` stays empty until the background poller starts. One provider task has one final asset delivery. Records written by an older version of this skill may also carry `polling_cron_task_id`; see **Stop a leftover Cron**.

If submit definitively reports that no provider task was created, report the failure. If submit times out, disconnects, or otherwise returns an ambiguous result without a `task_id`, record an `unverified submission state`. Because the Connector exposes no idempotency or reconciliation contract, never resubmit that ambiguous request within the same workflow, even after user confirmation. If the user explicitly requests another paid generation after being warned that it may duplicate an unknown first task, treat it as a distinct new workflow rather than a retry.

## Track the task with a background poller after submit

After a valid provider `task_id`, its output path, and its mapping have been persisted, start exactly one background poller for that provider task. The poller runs outside the model: it queries the existing task every 30 seconds and exits at the first terminal status, so the runtime wakes this conversation once, when there is a result. It never submits, uploads, downloads, or edits media.

1. Call the `bash` tool once with `run_in_background: true`, and set `description` to a short task name in the user's language, for example `生成海底世界视频` or `Generate underwater world video`. The product shows this name in the background-task list and in the completion notice.
2. Set `timeout: 7500` when the `bash` tool documents a background runtime limit that applies when `timeout` is omitted (Desktop: 1 hour). If the `bash` tool says `timeout` is capped at 600 seconds (cloud sandbox), omit `timeout`; the sandbox applies its own background limit.
3. Use the matching template below exactly. Replace only `<task_id>`, `<model>`, `<safe_task_id>` (the task ID reduced to `A-Z`, `a-z`, `0-9`, `_`, and `-`), and `<deadline_epoch_seconds>` (`floor(submitted_at_ms / 1000) + 7200`). Use the PowerShell template when the `bash` tool runs Windows PowerShell; use the POSIX template for bash or sh, including Git Bash and the cloud sandbox. Do not add a submit or upload call, change the interval, or wrap the loop in another script.
4. Persist the returned background task ID as `poller_task_id`. One provider task has at most one active poller; never start a second one while `task_output` shows the first one still running.
5. Tell the user once, in their language, that the video was submitted and is being generated in the background, that the result will appear here automatically (MiniMax-H3 usually takes a few minutes; do not quote a longer estimate from the Connector description), and that they can keep chatting. Do not promise a check interval, and do not create a Task/Todo/Progress record.
6. MiniMax-H3-Max (typically about 20 seconds) and MiniMax-Hailuo-2.3 (typically within about 1 minute) use the same poller. Right after starting it, you may wait in the current turn with `task_output` on `poller_task_id` and `wait_ms: 30000`, at most twice. If the poller has finished, handle its result in this turn; otherwise end the turn and let the completion notice bring the conversation back.
7. Do not use `self_reminder`, a Cron, `task`, a child session, or a new session for a task that has an active poller, and do not run another query loop for the same provider task.

POSIX template (bash or sh):

```sh
TASK_ID='<task_id>'; MODEL='<model>'; DEADLINE=<deadline_epoch_seconds>
DIR=.tmp/h3; ARGS="$DIR/<safe_task_id>.query-args.json"; OUT="$DIR/<safe_task_id>.query.json"; ERRORS=0
mkdir -p "$DIR" && printf '{"task_id":"%s","model":"%s"}' "$TASK_ID" "$MODEL" > "$ARGS" || exit 3
while :; do
  STATUS=
  if mcode-tools connector call connector__matrix__query_video_generation --args-file "$ARGS" > "$OUT.part" 2> "$OUT.err"; then
    STATUS=$(grep -o '"status"[[:space:]]*:[[:space:]]*"[A-Za-z_]*"' "$OUT.part" | head -n 1 | sed 's/.*"\([A-Za-z_]*\)"$/\1/')
  fi
  if [ -n "$STATUS" ]; then
    ERRORS=0; mv -f "$OUT.part" "$OUT"; echo "$(date +%H:%M:%S) status=$STATUS"
    case "$STATUS" in
      succeeded) echo "VIDEO_TASK_RESULT status=succeeded result_file=$OUT"; cat "$OUT"; exit 0 ;;
      failed|cancelled) echo "VIDEO_TASK_RESULT status=$STATUS result_file=$OUT"; cat "$OUT"; exit 1 ;;
    esac
  else
    ERRORS=$((ERRORS + 1)); echo "$(date +%H:%M:%S) query_error=$ERRORS $(cat "$OUT.err" "$OUT.part" 2>/dev/null | tail -c 300 | tr '\n' ' ')"
    [ "$ERRORS" -ge 20 ] && { echo "VIDEO_TASK_RESULT status=query_error"; exit 3; }
  fi
  [ "$(date +%s)" -ge "$DEADLINE" ] && { echo "VIDEO_TASK_RESULT status=timed_out result_file=$OUT"; exit 2; }
  sleep 30
done
```

PowerShell template (Windows PowerShell 5.1 or PowerShell 7):

```powershell
$taskId = '<task_id>'; $model = '<model>'; $deadline = [DateTimeOffset]::FromUnixTimeSeconds(<deadline_epoch_seconds>)
$dir = Join-Path (Join-Path (Get-Location).Path '.tmp') 'h3'; New-Item -ItemType Directory -Force -Path $dir | Out-Null
$argsFile = Join-Path $dir '<safe_task_id>.query-args.json'; $out = Join-Path $dir '<safe_task_id>.query.json'; $errFile = Join-Path $dir '<safe_task_id>.query.err'; $errors = 0
Set-Content -LiteralPath $argsFile -Value (@{ task_id = $taskId; model = $model } | ConvertTo-Json -Compress) -Encoding Ascii
while ($true) {
  $raw = (& mcode-tools connector call connector__matrix__query_video_generation --args-file $argsFile 2> $errFile | Out-String)
  $status = $null
  if ($LASTEXITCODE -eq 0) { try { $status = ($raw | ConvertFrom-Json).status } catch { $status = $null } }
  if ($status) {
    $errors = 0; Set-Content -LiteralPath $out -Value $raw -Encoding UTF8
    Write-Output ('{0} status={1}' -f (Get-Date -Format 'HH:mm:ss'), $status)
    if ($status -eq 'succeeded') { Write-Output "VIDEO_TASK_RESULT status=succeeded result_file=$out"; Write-Output $raw; exit 0 }
    if ($status -eq 'failed' -or $status -eq 'cancelled') { Write-Output "VIDEO_TASK_RESULT status=$status result_file=$out"; Write-Output $raw; exit 1 }
  } else {
    $errors++
    $detail = ([string](Get-Content -LiteralPath $errFile -Raw -ErrorAction SilentlyContinue) + [string]$raw) -replace '\s+', ' '
    if ($detail.Length -gt 300) { $detail = $detail.Substring($detail.Length - 300) }
    Write-Output ('{0} query_error={1} {2}' -f (Get-Date -Format 'HH:mm:ss'), $errors, $detail.Trim())
    if ($errors -ge 20) { Write-Output 'VIDEO_TASK_RESULT status=query_error'; exit 3 }
  }
  if ([DateTimeOffset]::UtcNow -ge $deadline) { Write-Output "VIDEO_TASK_RESULT status=timed_out result_file=$out"; exit 2 }
  Start-Sleep -Seconds 30
}
```

### Handle the poller result

When the background-task notice for `poller_task_id` arrives, or a `task_output` wait returns a finished poller, read the poller with `task_output` before anything else and act on its last `VIDEO_TASK_RESULT` line:

- `status=succeeded`: read `node_id` from the printed provider result (or from `result_file`), persist it in the task record, and continue to **Download and deliver atomically** in this same turn. Do not query the task again, even if the download fails: each query saves another copy to the user's Drive, and a new download URL comes from `get_asset_url`. Never submit. A succeeded result without a `node_id` is unverified delivery state; see **Query existing video task**.
- `status=failed` or `status=cancelled`: report the provider's failure details briefly in the user's language, and emit no asset.
- `status=timed_out`: persist `terminal_status: "timed_out"`, and report the provider task ID, submitted model, and last status. The user may ask for a manual check later.
- `status=query_error`: the poller stopped after 20 consecutive query errors. Report the last error. For HTTP 402, provider code 2056, insufficient balance, Token Plan denial, or another billing/auth gate, persist the terminal error and stop. Otherwise the user may ask for a manual check later; do not restart the poller on your own.
- No `VIDEO_TASK_RESULT` line (the poller was stopped, ended by its runtime limit, or lost after an app restart): do not resubmit. If the user stopped it, stop automatic checking unless they ask again. Otherwise query the task once directly; if it is still queued or running inside the 2-hour window, start one new poller with the same task ID, model, and output path.

Persist the terminal state and clear `poller_task_id` once the result is handled. Do not set a reminder or start another poller after a handled result.

### Fall back to one-time reminders

Use reminders only when a background poller cannot run: the `bash` tool has no `run_in_background` parameter, or starting the poller returns an error such as `Background bash execution is not enabled for this user`. A failed poller start does not make the provider task failed; keep the mapping and never call submit again.

Set a one-time reminder with the native `self_reminder` tool, not a shell command. The reminder brings this same conversation back once; that turn checks the task and sets the next reminder only if the video is still in progress. A finished task simply gets no new reminder, so nothing keeps running afterwards and there is nothing to clean up. This is why video polling must never use a recurring Cron.

```json
{
  "action": "set",
  "delay_seconds": 600,
  "prompt": "@video-creater follow-up: check video task <task_id> (model <model>, output path <output_path>, submitted_at_ms <timestamp>). Take the write-h3-prompts existing-provider-task route and query it once; never submit a new task. If it succeeded, download, validate, and deliver the MP4. If it is still running and less than 2 hours have passed since submission, set the next reminder; otherwise report the current state and stop."
}
```

1. Use `delay_seconds: 600` for MiniMax-H3, or the longer Connector `retry_after` when one is returned. The prompt carries the exact provider task ID, submitted model, unique output path, and original submission timestamp, and it is query-only.
2. MiniMax-H3-Max (typically about 20 seconds) and MiniMax-Hailuo-2.3 (typically within about 1 minute) use the in-turn fast path instead: wait about 20–30 seconds (H3-Max) or about 60 seconds (H2.3) in the submitting turn and query once directly; if still non-terminal, query again after 30–60 seconds. Set a reminder 30–60 seconds out only when the current turn must end while the task is still running.
3. Tell the user once that the task was submitted and this conversation will check it in about 10 minutes (for MiniMax-H3-Max and MiniMax-Hailuo-2.3, within about a minute). Do not describe it as a child or subtask, and do not create a Task/Todo/Progress record.
4. Do not use `task`, a child session, or a new session. Apart from the short fast-path wait in item 2, do not keep the turn open, sleep, or self-message to wait; the reminder owns the wait.
5. A conversation holds only one pending reminder. If `set` returns `SELF_REMINDER_EXISTS`, an earlier reminder will already bring this conversation back: keep it, and when it fires check every unfinished video task recorded in this conversation.
6. When a reminder fires for a task that is already finished, do not query or deliver it again and set no further reminder. When the user asks to check right away, just query. If that leaves no unfinished video task in this conversation, cancel the pending reminder you set for these checks with `{"action": "cancel"}`.

If `self_reminder` is also unavailable or `set` fails, do not treat the provider task as failed and never call submit again. Keep the mapping and tell the user the task ID and submitted model so they can ask for another check later.

### Stop a leftover Cron

Older versions of this skill polled with a recurring Cron and saved its ID as `polling_cron_task_id`. That Cron keeps waking the conversation and using credits until it is deleted. When a record still has one, usually because that Cron just started this turn, stop it before anything else:

1. Call `cron_delete` with the saved ID as a quoted string, for example `{"task_id": "<polling_cron_task_id>"}`. Cloud tools name this field `task_id` and Desktop tools name it `cron_id`; follow the live tool schema. These tools load on demand: find them with `tool_search`, then call them through `mcp_invoke` with an `arguments` object (`arguments_json` is not accepted).
2. If deletion fails, pause the Cron with `cron_update`, passing the same quoted ID and `enabled: false`.
3. Check each result. An error result such as `/task_id: Expected string` means nothing changed; correct the arguments once instead of repeating the same call.

Clear `polling_cron_task_id` only after deletion or pausing succeeds. If neither succeeds, tell the user plainly that the automatic check is still running and using credits, and that it can be paused in Scheduled Tasks. Never say polling has stopped, or that later runs cost nothing, before that is true. Once the Cron is stopped, continue with the normal follow-up flow.

## Query existing video task

`task_id` and `model` are required. Before querying, bootstrap exactly one recovery path:

- **Registered task:** reuse its submitted model, output path, timestamps, terminal status, and `node_id`. If it still has a `polling_cron_task_id`, stop that Cron first (see **Stop a leftover Cron**). If it already has a `node_id` and only needs a download, such as after a failed download, a missing local file, or a user request for a new copy, do not query the task: get a fresh URL with `get_asset_url` and download and deliver atomically. If it has a `poller_task_id`, read that poller once with `task_output` (`wait_ms: 0`): while it is still running, report its latest status line and do not query again or start another poller; if it has finished, follow **Handle the poller result**. If the task is already finished, do not query it again unless the user explicitly asks. Otherwise query once in the current main-conversation turn. If it succeeds, download and deliver atomically. If it remains queued or running inside the automatic window, start one background poller (or set one follow-up reminder when a poller cannot run). Never call submit.
- **Orphan task:** require the exact model supplied by the user, name the output file as in **Submit exactly once** when the conversation describes the video (otherwise use the sanitized task ID, such as `videos/<sanitized-task-id>.mp4`), then persist the mapping. Query it once in the current main conversation. If it is already succeeded, download and deliver it atomically. If it is queued or running, start one background poller in this conversation (or set one follow-up reminder when a poller cannot run). If it is failed or cancelled, report the terminal state and emit no asset.

Query with only the fields accepted by the live schema:

```bash
mcode-tools connector call connector__matrix__query_video_generation --args '{"task_id":"<task_id>","model":"<model>"}'
```

An existing-task, poller-result, or reminder turn must never call `connector__matrix__submit_video_generation` or any other paid video-submission path.

- Always query the same `task_id` and submitted or explicitly provided model.
- Automatic checks come from the background poller, which queries every 30 seconds for every model. Do not add other automatic queries while it runs. A user-requested check may query once directly at any time.
- The reminder fallback keeps the older cadence: for MiniMax-H3, wait at least 10 minutes after `submitted_at_ms` before the first reminder query and at least 10 minutes after `last_query_at_ms` before each later one. If the Connector provides a longer `retry_after`, use that longer delay. MiniMax-H3-Max typically completes in about 20 seconds and MiniMax-Hailuo-2.3 within about 1 minute: wait about 20–30 seconds (H3-Max) or about 60 seconds (H2.3) after `submitted_at_ms` before the first query and at least 30 seconds between later queries.
- If a direct query reports queued or running, start one poller (or, in the fallback, set the next reminder) within the 2-hour window. Do not call query again in the current turn, sleep, self-message, or keep the turn open to measure time.
- On a transient query or network failure in a direct query, including HTTP 503, do not retry in the current turn. Start one poller, which keeps retrying every 30 seconds; in the fallback, set the next reminder no earlier than 10 minutes later for MiniMax-H3 (one minute later for MiniMax-H3-Max and MiniMax-Hailuo-2.3), or after a longer Connector `retry_after`. A later turn queries the existing task; it never submits.
- On HTTP 402, provider code 2056, insufficient balance, Token Plan denial, or another billing/auth gate, persist the terminal error, report it, and start no poller or reminder. Do not switch models or submit.
- If status is succeeded, continue to atomic download.
- If `get_asset_url` fails with a non-zero code or a network error, do not retry in the current turn. Keep the saved `node_id` in the task record and set one later reminder on the fallback's transient-failure cadence; its prompt asks that turn to call `get_asset_url` again with the saved `node_id` and not to query the task. Do not start a poller, query the task, or submit again.
- If status is failed or cancelled, stop, return the terminal details, and emit no asset.
- Treat an unknown status or a succeeded response without a `node_id` as unverified delivery state. Outside the automatic window, report it. Inside the window, start one poller for an unknown status (or set one later reminder in the fallback). For a succeeded response without a `node_id`, set at most one later reminder on the fallback cadence instead, because a poller would stop at once on the same succeeded response. Do not submit again.

Keep every follow-up in this conversation: the background poller, or one-time reminders as the fallback. Do not use a recurring Cron, `task`, a child, sub-session, new session, or concurrent query loops for the same provider task. Do not create a second paid task.

## Automatic-check cutoff

Every provider task must eventually produce a visible terminal outcome for the owning conversation. Do not leave a task in `queued`, `running`, `finalizing`, or blank-output state forever.

- Track elapsed time from `submitted_at_ms` for newly submitted tasks, or from the first recovery query when the original timestamp is unavailable. Update `last_query_at_ms` after every direct query attempt.
- The automatic check window has a hard limit of 2 hours. If the live Connector schema or provider response exposes a stricter expiry, deadline, or retry budget, use the stricter value. A Connector `retry_after` or later provider deadline must not extend the 2-hour window. The poller enforces the window with its `DEADLINE`; for a recovery poller, derive the deadline from the same start time.
- In the reminder fallback, check the elapsed time before setting a reminder. If the next check would land after the 2-hour limit, set one final reminder at the limit when possible; otherwise mark the task timed out now.
- After the final automatic check, apply its result normally. If the task is still queued/running, a transient query or `get_asset_url` error occurs, the status is unknown, or a succeeded response lacks a `node_id`, persist `terminal_status: "timed_out"`, start no further poller or reminder, report the provider task ID, submitted model, and current state, and emit no asset. The user may later request a manual recovery query.
- A poller-result or reminder turn must never finish with a blank response. While a reminder-fallback task is still running, send one concise main-conversation status and when the next check is planned. Do not emit a Task/Todo/Progress record, custom progress placeholder, custom fold markup, or `<video-generation-options>` without a delivered asset.
- For an orphan task, do not mark it lost merely because its age is unknown. Query it once first; start the 2-hour window from that recovery query if the provider reports a non-terminal state.

## Download and deliver atomically

A successful query, including the poller's result, returns `node_id` and `file_name`. Persist `node_id` in this task's record right away, next to its task ID, model, and output path. Then get a short-lived download URL:

```bash
mcode-tools get_asset_url <node_id>
```

The output is JSON; download its `download_url` field with the steps below. Do not use `video_url` even when the query result still contains it, because only the `get_asset_url` URL follows the user's current download settings. Do not build a URL from `node_id`, and never treat a download URL as the deliverable. Do not assume a fixed URL lifetime. If the URL expires or a download fails and a new URL is needed, call `get_asset_url` again with the same `node_id`. Do not query the task again for a new URL, because each query saves another copy to the user's Drive, and never submit again.

1. Ensure the unique output directory exists.
2. Download with TLS verification and redirect handling to `<output_file_path>.part`, not directly to the final path.
3. Require a successful response, a non-zero file, and a playable MP4 whose contents match the expected media type.
4. Only after validation, atomically rename the temporary file to `output_file_path`.
5. Delete an incomplete temporary file after a failed download or validation. Never deliver a partial file.

When a poller result or a direct query reports provider success, that same turn performs the atomic download and validation first. After the playable MP4 is ready, persist delivery success and emit the final asset. Do not set another reminder or start another poller.

### Shape the terminal owner response for query collapse

Keep internal execution as a prefix and the user result as the final assistant content:

1. Complete every poller read, provider query, timer cleanup, download, validation, atomic rename, and other tool call before starting the final user-facing answer.
2. Emit exactly one final non-empty user-facing answer after all tool work. On success, include only a brief result sentence in the user's language, any result fact the user actually needs, and the single final `<deliver-assets>` video block. Do not repeat polling history, background-task or timer IDs, upload or download steps, tool output, or `<video-generation-options>`.
3. Do not call a tool or append another progress, acknowledgement, or status message after the final answer. Later activity is not part of the collapsible execution prefix and would remain visible beside the result.
4. For failed, cancelled, lost, timed-out, or unverified delivery, preserve the same ordering and finish with one concise non-empty outcome in the user's language. Emit no asset and do not claim success.
5. Do not emit custom fold markup or UI control fields such as `queryKey` or `queryCollapseBehavior`. The runtime and client own query identity, completion state, and the expandable execution-process disclosure.

```xml
<deliver-assets>
<media src="videos/<file-name>.mp4" name="<file-name>.mp4" type="video" />
</deliver-assets>
```

Use the recorded output path and its file name, and escape `&`, `<`, `>`, and `"` in attribute values.

Do not report success without the final local video asset. Do not deliver a temporary URL. A downloaded MP4 alone is not complete until the turn that handles the provider success emits it once.

Never create or update Todo/Progress records for this lifecycle, and never emit custom progress markup; the runtime shows the background poller itself.
