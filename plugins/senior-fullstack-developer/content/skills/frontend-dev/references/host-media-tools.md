# Host-Native Media Tools

Use this reference only when the frontend task requires generated media. The host capability catalog is authoritative; tool availability can differ by agent, profile, Desktop/Cloud surface, and product configuration.

## Preferred capability mapping

| Need | Prefer when available | Expected result |
| --- | --- | --- |
| Generate images | `image_synthesize` | Saves generated images to workspace paths, optionally using local reference images |
| Generate video | `submit_video_generation` with the host-provided query or background completion flow | Produces a video through the runtime's guarded asynchronous workflow |
| Generate speech | `synthesize_speech` or `batch_synthesize_speech` | Saves audio files to workspace paths |
| Generate music | `batch_text_to_music` | Saves generated tracks to workspace paths |
| Find stock/reference images | `images_search_and_download` | Downloads selected results into the workspace |

When tools are deferred, use the host's tool discovery mechanism rather than guessing schemas.

## Procedure

1. Confirm generated media is necessary; prefer existing project assets when they already satisfy the requirement.
2. Resolve the output path inside the active workspace and use the target project's asset conventions.
3. Follow the selected Tool's current schema, confirmation, payment, model-choice, upload, and safety requirements. Tool instructions override examples in this reference.
4. Verify the resulting file exists before adding it to code or presenting it as a deliverable.
5. Record generated asset provenance where the project requires it.

## Boundaries

- Do not ask the user for vendor API credentials or endpoint configuration.
- Do not call vendor endpoints directly with Python, curl, Bash, or embedded JavaScript.
- Do not create a Plugin MCP wrapper around a host-native media capability.
- Do not silently switch to a different external provider when the requested Tool is unavailable.
- Do not claim generation succeeded from a task ID alone; wait for the runtime's completion evidence.
