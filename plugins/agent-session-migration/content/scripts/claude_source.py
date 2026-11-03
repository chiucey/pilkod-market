"""Read-only Claude Code JSONL adapter; never loads config, hooks or credentials.

Parent-chain selection follows Anthropic's session reader. Provider message IDs
join streamed assistant siblings; tool results are matched by call identity.
Readable compact boundaries additionally honor explicit preserved-message IDs.
"""

import os
import re
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

from migrate import MigrationError, compact, digest, is_link, parse, regular

UUID = re.compile(r"^[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")
CHAIN_TYPES = {"user", "assistant", "attachment", "system", "progress"}
META_TYPES = {
    "queue-operation",
    "file-history-snapshot",
    "last-prompt",
    "ai-title",
    "custom-title",
    "summary",
    "mode",
    "pr-link",
    "tag",
    "agent-name",
    "agent-color",
    "agent-setting",
    "worktree-session",
    "session-end",
}
HOST_BLOCK = re.compile(
    r"\A\s*<(ide_opened_file|ide_selection|system-reminder)>[\s\S]*?</\1>\s*"
)


def user_text(text):
    while HOST_BLOCK.match(text):
        text = HOST_BLOCK.sub("", text, count=1)
    return text.strip()


def millis(value):
    if not isinstance(value, str):
        raise MigrationError("Claude message requires an ISO timestamp")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return int(dt.replace(tzinfo=dt.tzinfo or timezone.utc).timestamp() * 1000)
    except ValueError as exc:
        raise MigrationError("Invalid Claude timestamp") from exc


def source_path(value=None):
    root = (
        Path(value or os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
        .expanduser()
        .absolute()
    )
    if is_link(root) or not root.is_dir():
        raise MigrationError("Claude source must be an existing non-linked directory")
    if (root / "projects").is_dir():
        root = root / "projects"
    if is_link(root):
        raise MigrationError("Linked Claude projects directory")
    return root.resolve()


def read_rows(path, sid):
    rows = []
    with regular(path).open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = parse(line, "%s:%d" % (path.name, number))
            if not isinstance(row, dict):
                raise MigrationError("Invalid Claude transcript entry")
            if (
                row.get("type") in ("user", "assistant") and row.get("sessionId") != sid
            ) or row.get("sessionId") not in (None, sid):
                raise MigrationError("Claude session identity mismatch")
            if row.get("type") not in CHAIN_TYPES | META_TYPES:
                raise MigrationError(
                    "Unsupported Claude record: " + str(row.get("type"))
                )
            if row.get("type") == "system" and row.get("subtype") not in (
                "compact_boundary",
                "api_error",
                "turn_duration",
                "stop_hook_summary",
                "local_command",
            ):
                raise MigrationError(
                    "Unsupported Claude system record: " + str(row.get("subtype"))
                )
            rows.append(row)
    return rows


def metadata(rows):
    users = [
        r
        for r in rows
        if r.get("type") == "user" and not r.get("isMeta") and not r.get("isSidechain")
    ]
    title = next(
        (r.get("customTitle") for r in reversed(rows) if r.get("customTitle")), None
    )
    title = title or next(
        (r.get("aiTitle") for r in reversed(rows) if r.get("aiTitle")), None
    )
    if not title:
        for row in users:
            content = row.get("message", {}).get("content", [])
            texts = (
                [content]
                if isinstance(content, str)
                else [b.get("text", "") for b in content if b.get("type") == "text"]
            )
            text = user_text("\n".join(texts))
            if text and not row.get("isCompactSummary"):
                title = text.splitlines()[0][:120]
                break
    cwd = next(
        (
            r["cwd"]
            for r in reversed(rows)
            if isinstance(r.get("cwd"), str) and r["cwd"]
        ),
        None,
    )
    stamps = [
        millis(r["timestamp"]) for r in rows if r.get("uuid") and r.get("timestamp")
    ]
    if not cwd or not stamps:
        raise MigrationError("Claude transcript lacks workspace/timestamps")
    return title, cwd, min(stamps), max(stamps)


def inventory(root):
    root = source_path(root)
    paths, errors, info, size = {}, [], {}, 0
    for project in sorted(root.iterdir()):
        if is_link(project):
            errors.append(
                {"error": "Linked Claude project skipped", "path": str(project)}
            )
            continue
        if not project.is_dir():
            continue
        for path in sorted(project.glob("*.jsonl")):
            if not UUID.fullmatch(path.stem):
                continue  # Orphan backups and subagent logs are not main sessions.
            sid = path.stem
            try:
                if sid in paths:
                    raise MigrationError("Ambiguous Claude session ID: " + sid)
                paths[sid] = regular(path)
                size += path.stat().st_size
                info[sid] = metadata(read_rows(path, sid))
            except (MigrationError, OSError, ValueError, TypeError, KeyError) as exc:
                errors.append({"sourceId": sid, "error": str(exc)})
    return {
        "source": root,
        "ids": sorted(paths),
        "paths": paths,
        "info": info,
        "errors": errors,
        "bytes": size,
    }


def history_rows(rows):
    nodes, order = {}, {}
    for i, row in enumerate(rows):
        if (
            row.get("type") not in CHAIN_TYPES
            or row.get("isSidechain")
            or row.get("teamName")
        ):
            continue
        uid = row.get("uuid")
        if not isinstance(uid, str) or not uid:
            # Progress events without chain identity are not conversation content.
            if row.get("type") == "progress":
                continue
            raise MigrationError("Claude chain entry lacks UUID")
        if uid in nodes:
            if nodes[uid] == row:
                continue
            raise MigrationError("Conflicting Claude message UUID")
        nodes[uid], order[uid] = row, i
    candidates = [
        r
        for r in nodes.values()
        if r["type"] in ("user", "assistant")
        and (not r.get("isMeta") or r.get("isCompactSummary"))
    ]
    if not candidates:
        raise MigrationError("Claude session has no readable conversation")
    leaf = max(candidates, key=lambda r: order[r["uuid"]])["uuid"]

    def walk(start, display=False):
        chain, seen = [], set()
        while start:
            if start in seen or start not in nodes:
                raise MigrationError("Broken/cyclic Claude parent chain")
            seen.add(start)
            row = nodes[start]
            chain.append(start)
            start = row.get("parentUuid")
            if display and row.get("subtype") == "compact_boundary":
                start = row.get("logicalParentUuid")
        return list(reversed(chain))

    if any(
        r.get("subtype") == "compact_boundary" and order[u] > order[leaf]
        for u, r in nodes.items()
    ):
        raise MigrationError(
            "Claude compaction is incomplete; readable summary missing"
        )
    active = walk(leaf)
    display = walk(leaf, True)
    # A compact boundary disconnects old model history. Its summary is the new
    # anchor; explicit preservation metadata may reinsert selected old records.
    if nodes[active[0]].get("subtype") == "compact_boundary":
        boundary = nodes[active[0]]
        summaries = [u for u in active if nodes[u].get("isCompactSummary")]
        if len(summaries) != 1 or not nodes[summaries[0]].get("message", {}).get(
            "content"
        ):
            raise MigrationError("Claude compaction lacks a readable summary")
        summary = summaries[0]
        meta = boundary.get("compactMetadata") or {}
        preserved = meta.get("preservedMessages")
        segment = meta.get("preservedSegment")
        if preserved is not None or segment is not None:
            if not isinstance(preserved, dict) or not isinstance(segment, dict):
                raise MigrationError("Unsupported Claude preserved-segment format")
            ids = preserved.get("allUuids", preserved.get("uuids"))
            if (
                not isinstance(ids, list)
                or not ids
                or len(set(ids)) != len(ids)
                or any(
                    u not in nodes or order[u] >= order[boundary["uuid"]] for u in ids
                )
                or preserved.get("anchorUuid") != summary
                or segment.get("anchorUuid") != summary
                or ids != sorted(ids, key=order.get)
                or ids[0] != segment.get("headUuid")
                or ids[-1] != segment.get("tailUuid")
            ):
                raise MigrationError("Invalid Claude preserved-message references")
            active = (
                active[: active.index(summary) + 1]
                + ids
                + active[active.index(summary) + 1 :]
            )
    elif any(nodes[u].get("isCompactSummary") for u in active):
        raise MigrationError("Claude summary lacks compact boundary")

    def expand(ids, bounded=False):
        # Streaming chunks share a provider message ID. Do not lose parallel
        # tool calls merely because only one sibling lies on parentUuid's path.
        selected = set(ids)
        boundary_index = (
            order[active[0]]
            if bounded and nodes[active[0]].get("subtype") == "compact_boundary"
            else -1
        )
        mids = {
            nodes[u].get("message", {}).get("id")
            for u in ids
            if nodes[u]["type"] == "assistant" and order[u] > boundary_index
        }
        mids.discard(None)
        for u, r in nodes.items():
            if (
                r["type"] == "assistant"
                and order[u] > boundary_index
                and r.get("message", {}).get("id") in mids
            ):
                selected.add(u)
        # Preserve the summary-before-old-segment ordering in active history.
        if bounded and boundary_index >= 0:
            prefix = [active[0], summaries[0]]
            return prefix + sorted(selected - set(prefix), key=order.get)
        return sorted(selected, key=order.get)

    return nodes, expand(display), expand(active, True)


def text_blocks(content, warnings):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        raise MigrationError("Invalid Claude content")
    out = []
    for block in content:
        if not isinstance(block, dict):
            raise MigrationError("Invalid Claude content block")
        if block.get("type") == "text" and isinstance(block.get("text"), str):
            out.append(block["text"])
        elif block.get("type") in ("image", "document", "redacted_thinking"):
            warnings.append("Claude non-text payload omitted; bytes not migrated")
        else:
            raise MigrationError(
                "Unsupported Claude tool-result content: " + str(block.get("type"))
            )
    return "\n".join(out)


def full_tool_output(text, path, sid, warnings):
    if not text.startswith("<persisted-output>"):
        return text
    match = re.search(r"Full output saved to:\s*([^\r\n]+)", text)
    if not match:
        return text
    parts = match.group(1).strip().replace("\\", "/").split("/")
    if (
        len(parts) < 3
        or parts[-3:-1] != [sid, "tool-results"]
        or not re.fullmatch(r"[\w-]+\.txt", parts[-1])
    ):
        warnings.append("Claude persisted output reference unsupported; preview only")
        return text
    target = path.parent / sid / "tool-results" / parts[-1]
    if any(is_link(p) for p in (target, target.parent, target.parent.parent)):
        raise MigrationError("Linked Claude persisted output")
    if not target.is_file():
        warnings.append("Claude persisted output missing; preview only: " + parts[-1])
        return text
    return regular(target).read_text(encoding="utf-8")


def load_inventory(data, ids, context_dir=None):
    if context_dir:
        raise MigrationError(
            "Claude uses readable native summaries, not Codex context bundles"
        )
    result = []
    errors = {e.get("sourceId"): e["error"] for e in data["errors"]}
    for sid in sorted(ids):
        if sid in errors:
            raise MigrationError(errors[sid])
        path = data["paths"].get(sid)
        if path is None:
            raise MigrationError("Unknown Claude session ID: " + sid)
        rows = read_rows(path, sid)
        title, cwd, created, updated = metadata(rows)
        nodes, display, active = history_rows(rows)
        warnings = []
        results = {}
        for row in nodes.values():
            if row["type"] != "user":
                continue
            content = row.get("message", {}).get("content")
            for block in content if isinstance(content, list) else []:
                if block.get("type") == "tool_result":
                    call = block.get("tool_use_id")
                    if call in results and results[call][0] != block:
                        raise MigrationError("Conflicting Claude tool result")
                    results[call] = (block, row.get("sourceToolAssistantUUID"))
        messages = []
        for uid, row in nodes.items():
            role = row["type"]
            if role not in ("user", "assistant", "attachment"):
                continue
            parts = []
            semantics = None
            if role == "attachment":
                attachment = row.get("attachment") or {}
                if attachment.get("type") not in (
                    "file",
                    "edited_text_file",
                    "queued_command",
                ):
                    continue
                # These are past file/context observations, never live hooks,
                # skill listings or executable task/permission state.
                if (
                    attachment.get("type") == "file"
                    and (attachment.get("content") or {}).get("type") != "text"
                ):
                    warnings.append(
                        "Claude non-text attachment omitted; bytes not migrated"
                    )
                    continue
                body = {
                    k: v
                    for k, v in attachment.items()
                    if k in ("type", "filename", "snippet", "prompt", "content")
                }
                parts = [
                    {
                        "type": "text",
                        "text": "[Claude Code 历史附件/排队输入；仅供参考]\n"
                        + compact(body),
                    }
                ]
                role, semantics = "user", {"providerVisibility": "visible"}
            else:
                message = row.get("message")
                if not isinstance(message, dict) or message.get("role") != role:
                    raise MigrationError("Invalid Claude message role")
                content = message.get("content")
                if isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                if not isinstance(content, list):
                    raise MigrationError("Invalid Claude message content")
                for block in content:
                    typ = block.get("type")
                    if typ == "text":
                        text = text_blocks([block], warnings)
                        if role == "user" and not row.get("isCompactSummary"):
                            text = user_text(text)
                        if text:
                            parts.append({"type": "text", "text": text})
                    elif typ == "thinking":
                        if isinstance(block.get("thinking"), str) and block["thinking"]:
                            parts.append(
                                {"type": "reasoning", "text": block["thinking"]}
                            )
                    elif typ == "tool_use" and role == "assistant":
                        call = block.get("id")
                        if (
                            not isinstance(call, str)
                            or not isinstance(block.get("name"), str)
                            or not isinstance(block.get("input"), dict)
                        ):
                            raise MigrationError("Invalid Claude tool call")
                        state = {"status": "pending", "input": block["input"]}
                        if call in results:
                            value, source_uuid = results[call]
                            if source_uuid and source_uuid != uid:
                                raise MigrationError(
                                    "Claude tool-result source identity mismatch"
                                )
                            output = full_tool_output(
                                text_blocks(value.get("content", ""), warnings),
                                path,
                                sid,
                                warnings,
                            )
                            state.update(
                                status="error"
                                if value.get("is_error")
                                else "completed",
                                output=output,
                            )
                        else:
                            warnings.append(
                                "Claude unfinished historical tool call: " + call
                            )
                        parts.append(
                            {
                                "type": "tool",
                                "tool": block["name"],
                                "callID": call,
                                "state": state,
                            }
                        )
                    elif typ == "tool_result" and role == "user":
                        continue
                    elif typ in ("image", "document", "redacted_thinking"):
                        warnings.append(
                            "Claude non-text payload omitted; bytes not migrated"
                        )
                    else:
                        raise MigrationError(
                            "Unsupported Claude message block: " + str(typ)
                        )
                if row.get("isCompactSummary"):
                    semantics = {"kind": "compact_summary"}
                elif row.get("isMeta") or row.get("isVisibleInTranscriptOnly"):
                    semantics = {"origin": "agent_runtime"}
            if parts:
                messages.append(
                    {
                        "id": uid,
                        "createdAtMs": millis(row["timestamp"]),
                        "data": {
                            "role": role,
                            **({"semantics": semantics} if semantics else {}),
                        },
                        "parts": [
                            {"id": uid + ":" + str(i), "data": p}
                            for i, p in enumerate(parts)
                        ],
                    }
                )
        mids = {m["id"] for m in messages}
        display = [u for u in display if u in mids]
        active = [u for u in active if u in mids]
        if not active:
            raise MigrationError("Claude session has no readable active history")
        if (path.parent / sid / "subagents").is_dir():
            warnings.append(
                "Claude subagent files are not separate sessions; parent tool results retained"
            )
        item = {
            "session": {
                "id": sid,
                "title": title or sid,
                "directory": cwd,
                "time_created": created,
                "time_updated": updated,
            },
            "desktop": {"title": title or sid, "archived": False},
            "messages": messages,
            "histories": {"display": display, "active": active},
            "warnings": sorted(set(warnings)),
        }
        item["fingerprint"] = digest(item)
        result.append(item)
    return result


def load_source(root, ids=None):
    data = inventory(root)
    return load_inventory(data, data["ids"] if ids is None else ids)


def overview(root, ids=None):
    data = inventory(root)
    selected = set(data["ids"] if ids is None else ids)
    rows = []
    for sid in selected:
        if sid not in data["info"]:
            continue
        title, cwd, _, updated = data["info"][sid]
        rows.append(
            {
                "id": sid,
                "title": title,
                "workspace": cwd,
                "workspaceExists": Path(cwd).is_dir()
                and (os.name == "nt" or not PureWindowsPath(cwd).drive),
                "updatedAt": updated,
                "archived": False,
                "bytes": data["paths"][sid].stat().st_size,
            }
        )
    return sorted(rows, key=lambda row: row["updatedAt"], reverse=True)


def select_histories(item):
    return item["messages"], item["messages"]


ADAPTER = {
    "prepare_context": None,
    "display_user_text": None,
    "load_source": load_source,
    "inventory": inventory,
    "load_inventory": load_inventory,
    "select_histories": select_histories,
    "source_path": source_path,
    "overview": overview,
    "repairable": False,
    "label": "Claude Code",
    "marker": "claude-code-migration.json",
    "archive": "claude-code-source.json",
    "id_prefix": "msg-claude-code-",
    "turn_prefix": "claude-code-",
    "provider": "claude-code-history",
    "display_kind": "claude_code_history_archive",
}
