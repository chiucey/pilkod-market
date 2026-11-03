"""Read-only Pi V3 JSONL adapter, matching pi-coding-agent 0.86.0 history selection."""

import os
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

from migrate import MigrationError, compact, digest, is_link, parse, regular

TYPES = {
    "message",
    "compaction",
    "branch_summary",
    "custom_message",
    "custom",
    "label",
    "session_info",
    "thinking_level_change",
    "model_change",
    "usage",
}


def obj(value, label):
    if not isinstance(value, dict):
        raise MigrationError("Invalid Pi " + label)
    return value


def string(value, label):
    if not isinstance(value, str):
        raise MigrationError("Invalid Pi " + label)
    return value


def millis(value):
    try:
        dt = datetime.fromisoformat(string(value, "timestamp").replace("Z", "+00:00"))
        return int(dt.replace(tzinfo=dt.tzinfo or timezone.utc).timestamp() * 1000)
    except (ValueError, OverflowError) as exc:
        raise MigrationError("Invalid Pi timestamp") from exc


def source_path(value=None):
    root = (
        Path(
            value or os.environ.get("PI_CODING_AGENT_DIR") or Path.home() / ".pi/agent"
        )
        .expanduser()
        .absolute()
    )
    if is_link(root) or not root.is_dir():
        raise MigrationError("Pi source must be an existing non-linked directory")
    if (root / "sessions").is_dir():
        root = root / "sessions"
    if is_link(root):
        raise MigrationError("Linked Pi sessions directory")
    return root.resolve()


def read(path):
    with regular(path).open(encoding="utf-8") as stream:
        rows = [obj(parse(line, path.name), "entry") for line in stream if line.strip()]
    if not rows or rows[0].get("type") != "session" or rows[0].get("version") != 3:
        raise MigrationError("Unsupported Pi session format; V3 required")
    header = rows[0]
    if not string(header.get("id"), "session ID") or not string(
        header.get("cwd"), "workspace"
    ):
        raise MigrationError("Pi session lacks identity/workspace")
    millis(header.get("timestamp"))
    return header, rows[1:]


def inventory(root):
    root = source_path(root)
    paths, info, errors, size = {}, {}, [], 0
    # Standard tree is sessions/<encoded workspace>/*.jsonl; avoid following links.
    dirs = [root] + [p for p in sorted(root.iterdir()) if p.is_dir() and not is_link(p)]
    for directory in dirs:
        for path in sorted(directory.glob("*.jsonl")):
            sid = None
            try:
                header, rows = read(path)
                sid = header["id"]
                if sid in paths:
                    raise MigrationError("Ambiguous Pi session ID: " + sid)
                paths[sid] = path
                title = next(
                    (
                        r.get("name")
                        for r in reversed(rows)
                        if r.get("type") == "session_info" and r.get("name")
                    ),
                    None,
                )
                info[sid] = {
                    "id": sid,
                    "title": title,
                    "workspace": header["cwd"],
                    "updatedAt": max(
                        [millis(header["timestamp"])]
                        + [millis(r.get("timestamp")) for r in rows]
                    ),
                    "archived": False,
                }
                size += path.stat().st_size
            except (MigrationError, OSError, ValueError, TypeError) as exc:
                errors.append({"sourceId": sid, "path": str(path), "error": str(exc)})
    return {
        "source": root,
        "ids": sorted(paths),
        "paths": paths,
        "info": info,
        "errors": errors,
        "bytes": size,
    }


def select_entries(rows):
    nodes = {}
    for row in rows:
        uid = string(row.get("id"), "entry ID")
        if not uid or uid in nodes or row.get("type") not in TYPES:
            raise MigrationError("Duplicate/unknown Pi entry")
        nodes[uid] = row
    if not rows:
        raise MigrationError("Pi session is empty")
    path, seen, uid = [], set(), rows[-1]["id"]
    while uid is not None:
        if uid not in nodes or uid in seen:
            raise MigrationError("Broken/cyclic Pi parent chain")
        row = nodes[uid]
        seen.add(uid)
        path.append(uid)
        if "parentId" not in row:
            raise MigrationError("Pi entry lacks parentId")
        uid = row["parentId"]
        if uid is not None and not isinstance(uid, str):
            raise MigrationError("Invalid Pi parentId")
    path.reverse()
    active = path[:]
    checkpoints = [
        i for i, uid in enumerate(path) if nodes[uid]["type"] == "compaction"
    ]
    if checkpoints:
        i = checkpoints[-1]
        kept = nodes[path[i]].get("firstKeptEntryId")
        # Pi itself tolerates missing references; import must not silently discard history.
        if kept not in path[:i]:
            raise MigrationError(
                "Pi compaction firstKeptEntryId is missing from the prior branch"
            )
        active = [path[i]] + path[path.index(kept) : i] + path[i + 1 :]
    return nodes, path, active


def blocks(value):
    if isinstance(value, str):
        return [{"type": "text", "text": value}]
    if not isinstance(value, list) or any(not isinstance(p, dict) for p in value):
        raise MigrationError("Invalid Pi content blocks")
    return value


def text_content(value, warnings):
    out = []
    for p in blocks(value):
        if p.get("type") == "text":
            out.append(string(p.get("text"), "text"))
        elif p.get("type") == "image":
            warnings.append("Attachment reference retained; bytes not copied: Pi image")
            out.append("[Pi 历史图片；图片内容未迁入]")
        else:
            raise MigrationError("Unsupported Pi text content: " + str(p.get("type")))
    return "\n".join(out)


def normalize(header, rows):
    nodes, path, active = select_entries(rows)
    warnings, results, calls = [], {}, {}
    # Pair only on the selected branch; abandoned tool results must not leak in.
    for uid in path:
        r = nodes[uid]
        if r["type"] != "message":
            continue
        msg = obj(r.get("message"), "message")
        if msg.get("role") == "assistant":
            for p in blocks(msg.get("content")):
                if p.get("type") == "toolCall":
                    cid = string(p.get("id"), "call ID")
                    if not cid or cid in calls:
                        raise MigrationError("Duplicate Pi tool call ID")
                    calls[cid] = (uid, p)
        if msg.get("role") == "toolResult":
            cid = string(msg.get("toolCallId"), "result call ID")
            if cid in results or cid not in calls:
                raise MigrationError("Pi orphan/duplicate tool result")
            if msg.get("toolName") != calls[cid][1].get("name"):
                raise MigrationError("Pi tool result name mismatch")
            results[cid] = (uid, msg)
    messages, display_ids, active_ids = [], [], []
    active_set = set(active)
    title = next(
        (
            r.get("name")
            for r in reversed(rows)
            if r["type"] == "session_info" and r.get("name")
        ),
        None,
    )
    for uid in path:
        r = nodes[uid]
        typ = r["type"]
        parts, semantics, role = [], None, "user"
        show, model = True, uid in active_set
        if typ in ("compaction", "branch_summary"):
            summary = string(r.get("summary"), "summary")
            if not summary.strip():
                raise MigrationError("Pi summary is empty")
            parts = [
                {
                    "type": "text",
                    "text": "[Pi 历史"
                    + ("压缩" if typ == "compaction" else "分支")
                    + "摘要]\n"
                    + summary,
                }
            ]
            semantics = {"kind": "compact_summary"}
            show = False
        elif typ in ("message", "custom_message"):
            msg = (
                obj(r.get("message"), "message")
                if typ == "message"
                else {**r, "role": "custom"}
            )
            role = msg.get("role")
            if role == "system":
                continue
            if role in ("user", "custom"):
                text = text_content(msg.get("content"), warnings)
                if role == "custom":
                    text = "[Pi 历史扩展消息；仅供参考]\n" + text
                    semantics = {"providerVisibility": "visible"}
                    show = False
                    if msg.get("display"):
                        warnings.append(
                            "Pi extension renderer not migrated; content retained as labeled context"
                        )
                    role = "user"
                elif not title and text.strip():
                    title = text.strip().splitlines()[0][:120]
                parts = [{"type": "text", "text": text}]
            elif role == "assistant":
                stop = msg.get("stopReason")
                if stop not in ("stop", "length", "toolUse", "error", "aborted"):
                    raise MigrationError(
                        "Pi assistant pending/deferred/unknown completion"
                    )
                for p in blocks(msg.get("content")):
                    kind = p.get("type")
                    if kind == "text":
                        parts.append(
                            {
                                "type": "text",
                                "text": string(p.get("text"), "assistant text"),
                            }
                        )
                    elif kind == "thinking":
                        if not p.get("redacted"):
                            parts.append(
                                {
                                    "type": "reasoning",
                                    "text": string(p.get("thinking"), "thinking"),
                                }
                            )
                    elif kind == "toolCall":
                        cid = p["id"]
                        state = {
                            "status": "pending",
                            "input": obj(p.get("arguments"), "tool arguments"),
                        }
                        if cid in results:
                            value = results[cid][1]
                            state.update(
                                status="error" if value.get("isError") else "completed",
                                output=text_content(value.get("content"), warnings),
                            )
                        else:
                            warnings.append(
                                "Pi unfinished historical tool call: " + cid
                            )
                        parts.append(
                            {
                                "type": "tool",
                                "tool": string(p.get("name"), "tool name"),
                                "callID": cid,
                                "state": state,
                            }
                        )
                    else:
                        raise MigrationError(
                            "Unsupported Pi assistant block: " + str(kind)
                        )
                if msg.get("errorMessage"):
                    parts.append(
                        {
                            "type": "text",
                            "text": "[Pi 历史助手错误]\n"
                            + string(msg["errorMessage"], "error"),
                        }
                    )
            elif role == "toolResult":
                cid = msg["toolCallId"]
                show = False
                # A compaction may keep a result while summarizing its call.
                model = model and calls[cid][0] not in active_set
                role, semantics = "user", {"providerVisibility": "visible"}
                parts = [
                    {
                        "type": "text",
                        "text": "[Pi 历史工具结果；调用已在摘要之前]\n"
                        + compact(
                            {
                                "tool": msg["toolName"],
                                "callID": cid,
                                "isError": msg.get("isError"),
                                "output": text_content(msg.get("content"), warnings),
                            }
                        ),
                    }
                ]
            elif role == "bashExecution":
                role = "assistant"
                parts = [
                    {
                        "type": "tool",
                        "tool": "bash",
                        "callID": uid,
                        "state": {
                            "status": "error"
                            if msg.get("cancelled")
                            or msg.get("exitCode") not in (None, 0)
                            else "completed",
                            "input": {
                                "command": string(msg.get("command"), "bash command")
                            },
                            "output": string(msg.get("output"), "bash output"),
                        },
                    }
                ]
                model = model and not msg.get("excludeFromContext")
                if msg.get("truncated"):
                    warnings.append("Pi bash output truncated; fullOutputPath not read")
            else:
                raise MigrationError("Unsupported Pi message role: " + str(role))
        else:
            continue
        parts = [p for p in parts if p["type"] == "tool" or p.get("text")]
        if not parts:
            continue
        messages.append(
            {
                "id": uid,
                "createdAtMs": millis(r.get("timestamp")),
                "data": {
                    "role": role,
                    **({"semantics": semantics} if semantics else {}),
                },
                "parts": [
                    {"id": uid + ":" + str(i), "data": p} for i, p in enumerate(parts)
                ],
            }
        )
        if show:
            display_ids.append(uid)
        if model:
            active_ids.append(uid)
    if not active_ids:
        raise MigrationError("Pi session has no readable active history")
    selected_active = set(active_ids)
    item = {
        "session": {
            "id": header["id"],
            "title": title or header["id"],
            "directory": header["cwd"],
            "time_created": millis(header["timestamp"]),
            "time_updated": max(millis(r["timestamp"]) for r in rows),
        },
        "desktop": {"title": title or header["id"], "archived": False},
        "messages": messages,
        "histories": {
            "display": display_ids,
            "active": [uid for uid in active if uid in selected_active],
        },
        "warnings": sorted(set(warnings)),
    }
    item["fingerprint"] = digest(item)
    return item


def load_inventory(data, ids, context_dir=None):
    if context_dir:
        raise MigrationError("Context bundles are only supported for Codex")
    errors = {e.get("sourceId"): e["error"] for e in data["errors"]}
    result = []
    for sid in sorted(ids):
        if sid in errors:
            raise MigrationError(errors[sid])
        if sid not in data["paths"]:
            raise MigrationError("Unknown Pi session ID: " + sid)
        header, rows = read(data["paths"][sid])
        if header["id"] != sid:
            raise MigrationError("Pi session identity changed")
        result.append(normalize(header, rows))
    return result


def load_source(root, ids=None):
    data = inventory(root)
    return load_inventory(data, data["ids"] if ids is None else ids)


def overview(root, ids=None):
    data = inventory(root)
    selected = set(data["ids"] if ids is None else ids)
    return [
        {
            **r,
            "workspaceExists": Path(r["workspace"]).is_dir()
            and (os.name == "nt" or not PureWindowsPath(r["workspace"]).drive),
        }
        for sid, r in data["info"].items()
        if sid in selected
    ]


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
    "label": "Pi",
    "marker": "pi-agent-migration.json",
    "archive": "pi-agent-source.json",
    "id_prefix": "msg-pi-agent-",
    "turn_prefix": "pi-agent-",
    "provider": "pi-agent-history",
    "display_kind": "pi_agent_history_archive",
}
