# H3 reference-media preflight

Use this reference only for a **new generation request with reference media**. Complete the whole batch preflight in the owning conversation before any upload, Connector discovery, paid submit, or query timer. A query-only task with an existing provider `task_id` never runs this preflight.

## Input contract

The table below is the H3 reference-media input contract supplied for this Plugin. Inspect actual metadata immediately for every model, but apply model-specific validation only after the model is known. For H3, enforce the complete table. For an H2.3 first-frame or legacy-subject request, reuse the inspected facts and validate only the constraints disclosed by the current live Connector schema; a required H2.3 fact that the schema does not disclose is `unverified`, not proven valid merely because it satisfies the H3 table. For MiniMax-H3-Max, only first-frame and last-frame keyframe images are valid reference media (a single first frame, a single last frame, or first+last together); classify any reference_images/reference_videos/reference_audios collection request as `invalid` for H3-Max and surface MiniMax-H3 as the multimodal-reference alternative.

Model selection is the only generation question allowed between inspection and classification. If the model is unknown, finish collecting model-independent facts, ask only for the model, and then classify the complete batch. Do not draft, edit, upload, discover Connector tools, or ask for duration, resolution, ratio, or other generation choices during this gap.

- **Images:** 1–9 images in JPG, JPEG, PNG, WEBP, HEIC, or HEIF. Each file is at most 30 MB. Width and height are each 256 through 5,760 pixels inclusive after orientation is applied. A first- or last-frame image follows the same rules and counts toward both the image total and the mixed-file total.
- **Videos:** 1–3 videos in MP4 or MOV, encoded with H.264/AVC or H.265/HEVC. If a video contains audio, that track uses AAC or MP3. Each file is at most 50 MB. Width and height are each 256 through 5,760 pixels inclusive after orientation is applied. Display aspect ratio is 0.4 through 2.5 inclusive. Each original duration is 2 through 15 seconds inclusive, and the combined actual video duration must not exceed 15 seconds.
- **Audio:** 1–3 audio files in WAV or MP3. Each file is at most 15 MB. Each original duration is 2 through 15 seconds inclusive, and the combined audio duration must not exceed 15 seconds. Audio cannot be used alone; at least one image or video is also required.
- **Mixed batch:** images, videos, and audio together must not exceed 12 files.
- **No references:** With no reference media, use text-to-video mode.

For an H3 keyframe `input_image` or `last_frame_image`, the current live Connector schema additionally requires a width:height aspect ratio from 0.4 through 2.5 inclusive. Do not generalize this keyframe-only rule to H2.3 or to every multimodal `reference_images` item unless the live schema explicitly does so.

Per-file limits are independent; there is no aggregate source-media byte limit. Here, 1 MB means 1,000,000 bytes. After uploads, the exact serialized API request body must not exceed 64 MB. Use HTTPS URL objects rather than inline or base64 media.

For local reference videos, the later upload flow rounds each original duration with `Math.ceil` to form the Connector's integer `duration_seconds`. During preflight, validate the original floating-point duration first, then also require the sum of those rounded integers not to exceed 15 seconds. Do not infer source duration from the requested output duration.

## Inspect before any mutation

The first operation after reference media arrives is inspection of the complete batch.

1. Prefer trustworthy attachment metadata already present in the conversation.
2. If required metadata is missing for a supplied local file, the only permitted tool exception is a read-only local metadata inspection capability. It must not upload, edit, access a remote network, call a Connector, or incur a charge.
3. Do not trust only filename extensions or declared MIME types. Determine, as applicable:
   - actual format or container and byte size;
   - image orientation, displayed dimensions, and aspect ratio;
   - video orientation, displayed dimensions, aspect ratio, duration, video codec, and audio codec;
   - audio duration and codec.
4. Evaluate each file and all batch counts and duration totals together.
5. A public URL without trustworthy attached metadata is `unverified`; do not fetch it through an arbitrary network path merely to make the preflight pass. Ask for a locally inspectable upload or metadata from an approved read-only asset probe.

Until the complete batch becomes `valid`, make zero upload, submit, query, and timer calls. In particular, do not run `mcode-tools upload-temp-url`, Connector discovery, `connector__matrix__submit_video_generation`, `connector__matrix__query_video_generation`, `self_reminder`, or a background poller.

## Three outcomes

Classify the complete batch as exactly one state:

- **`valid`:** every required fact was inspected and every applicable file and batch rule passed. Only this state may proceed to upload.
- **`invalid`:** at least one measured fact violates a rule. Identify each affected file, the actual measured value, and the required limit. Do not upload or edit yet.
- **`unverified`:** a required fact cannot be established with the available metadata and approved read-only inspection capability. Identify the missing fact and how the user can provide inspectable evidence. Do not describe unverified media as non-compliant.

Use a normal assistant reply for the first `invalid` or `unverified` notice, not `ask_user`, then wait for the user.

For an invalid file, use this Chinese response pattern when appropriate:

> 检测到参考素材暂不符合 H3 规范：`<文件名>` 的 `<实际情况>`，要求为 `<规范>`。你可以更换符合要求的素材；如果当前环境有合适的媒体处理能力，也可以授权我调整一个副本使其符合规范，原文件不会被覆盖。我会等你确认后再上传或提交生成。

For an unverified file, use this pattern:

> 暂时无法验证参考素材是否符合 H3 规范：`<文件名>` 缺少 `<待验证信息>`。请重新上传可检查的本地文件，或提供可信的素材元数据；完成验证前我不会上传或提交生成。

## Recovery choices

For `invalid` media, offer the user the applicable choices in the same response:

1. **Replace the material:** ask for a compliant replacement, then re-run the complete batch preflight.
2. **Authorize M3 to adjust a derivative:** offer this only when a suitable workspace media-editing capability is actually available. Describe the exact proposed conversion, resize, compression, padding, crop, transcode, bitrate change, or trim before asking for authorization.

If no suitable editor is available, say so and offer replacement guidance; do not pretend M3 can edit the file or call an undeclared external service. For `unverified` media, first obtain inspectable material or approved metadata rather than proposing a speculative edit.

Wait for explicit authorization before modifying media. If `ask_user` is unavailable at a required crop, trim, framing, or semantic-edit decision, ask the question directly in the main conversation and wait.

## Create a safe derivative

- Write a derivative to a stable path such as `prepared-media/<stem>-video-creater-ready.<ext>`. Never overwrite the user's original file.
- Preserve reference role, order, identity, subject matter, and intended content.
- For images, correct orientation, convert to a supported format, proportionally resize, pad, and recompress as needed. Prefer padding before cropping.
- For video, prefer MP4 with H.264/AVC and AAC when audio exists; correct orientation, resize, pad, transcode, or lower bitrate as needed. Trimming requires the user to choose the retained segment unless already explicit.
- For audio, convert only to WAV or MP3 and trim only with an explicit retained segment. Do not silently pad, duplicate, or loop it to manufacture duration.
- Do not silently crop, trim, loop, freeze, slow, or invent content. Generative fill, inpainting, outpainting, invented frames, or another semantic edit requires explicit creative approval.
- A crop that might remove a subject, visible text, or edge content requires a framing decision. In first/last-frame mode, padding or cropping that changes image ratio also requires confirmation and an updated aspect-ratio reminder.

After every adjustment, inspect the derivative and re-run the complete batch preflight, including counts and duration totals. A derivative that is still `invalid` or `unverified` must not be uploaded or submitted.

Before uploading a valid derivative, tell the user what changed, which file will be used, and whether padding or cropping changed visible framing.
