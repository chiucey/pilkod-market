---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3e23b71392abf27caa6a1ac7f9bc237c
    PropagateID: 3e23b71392abf27caa6a1ac7f9bc237c
    ReservedCode1: 30450221009e9572ec13740ef577319bf860d3f987c85d6de00a6ecb600394c022798c31fc02203954dd8237962a3e2cc436d5b252a21dd52acfd2ec0f38405947147f598a109b
    ReservedCode2: 304602210089e2b284aed7cfdad93d0524774eee3056ac4502db52877a4874e9a200e076c0022100fc85c3a9291c4a241052859ba0c66a762780964aa47831ed73f86febd718edee
---

# Attachments & Artifacts

How files flow through a session: uploads in, intermediate files during execution, downloadable artifacts out.

## The file flow

```
Upload (POST /api/uploads/{session_id})
  → WareHouse/<session>/code_workspace/attachments/<file>
  → recorded in attachments_manifest.json
  → referenced in the execution payload by attachment_id ("att_xxx")
  → visible to python nodes as files in code_workspace/
  → visible to function tools via _context.attachment_store
  → new files written by python/tools auto-promote via WorkspaceArtifactHook
  → emitted as artifact_created events on the WebSocket
  → downloadable via /artifacts/{artifact_id} or /download (session zip)
```

The single shared workspace (`code_workspace/`) means the python node, function tools' `_context.python_workspace_root`, and the attachment store all see the same directory tree. **No plumbing needed between them.**

## Attachments are explicit on entry

Uploads must be explicitly referenced per execution:

```json
POST /api/workflow/execute
{
  "task_prompt": "Summarize the attached document.",
  "attachments": ["att_abc123"]
}
```

Same for `human_input` payloads. Workflows aren't relying on global state — file presence per run is deterministic.

## MIME → MessageBlockType

When an upload reaches an agent, its MIME type determines the message block type:

| MIME prefix | MessageBlockType |
|---|---|
| `image/*` | `image` |
| `audio/*` | `audio` |
| `video/*` | `video` |
| anything else | `file` |

Agents like `gemini-2.5-flash-image` consume `image` blocks natively. Multimodal-capable agents can also **emit** image content; the output flows through the standard message channel and auto-promotes to artifacts via `WorkspaceArtifactHook`.

## Auto-promotion

Anything written to `code_workspace/` (by python nodes, function tools, or multimodal agents) is automatically promoted to a downloadable artifact. No manual registration needed. The `WorkspaceArtifactHook` watches the directory and emits `artifact_created` events on the WebSocket.

For files written outside `code_workspace/` (rare), function tools can register manually via `_context.attachment_store.register_file(path)`.

## Cleanup

By default, attachments persist across the session. Set `MAC_AUTO_CLEAN_ATTACHMENTS=1` in the deployment env to wipe `attachments/` after a session completes.

If a workflow assumes attachments survive across multiple `human_input` turns within a session, this flag staying off is fine. If a deployment flips it on, the workflow needs to either re-upload or persist references explicitly.

## Operator-facing endpoints

For workflow authors, you don't usually call these directly — the Web UI does — but they're useful for diagnostics:

| Endpoint | Purpose |
|---|---|
| `POST /api/uploads/{session_id}` | Upload file, get back `attachment_id` |
| `POST /api/workflow/execute` | Start execution; payload includes `attachments: []` |
| `GET /artifacts/{artifact_id}` | Download a single artifact |
| `GET /sessions/{session_id}/download` | Download a zip of the whole session's artifacts |
| WebSocket `/ws/sessions/{id}` | Live event stream including `artifact_created` |
