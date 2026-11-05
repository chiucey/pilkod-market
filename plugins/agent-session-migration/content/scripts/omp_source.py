"""Read-only OMP V3 adapter, based on upstream b4e288210c052e1c62042515e739919c9304f14e."""

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

from migrate import MAX_RECORD, MigrationError, compact, digest, is_link, parse, regular

TYPES = {
    "message",
    "compaction",
    "branch_summary",
    "custom_message",
    "custom",
    "label",
    "thinking_level_change",
    "model_change",
    "model_usage",
    "service_tier_change",
    "reset_boundary",
    "title_change",
    "ttsr_injection",
    "credential_pin",
    "session_init",
    "mode_change",
}
TRANSIENT = {"prewalk-plan", "vibe-mode-context"}


def obj(value, label):
    if not isinstance(value, dict):
        raise MigrationError("Invalid OMP " + label)
    return value


def string(value, label):
    if not isinstance(value, str):
        raise MigrationError("Invalid OMP " + label)
    return value


def millis(value):
    try:
        dt = datetime.fromisoformat(string(value, "timestamp").replace("Z", "+00:00"))
        return int(dt.replace(tzinfo=dt.tzinfo or timezone.utc).timestamp() * 1000)
    except (ValueError, OverflowError) as exc:
        raise MigrationError("Invalid OMP timestamp") from exc


def profile_name(value):
    name = (value or "").strip()
    if not name or name == "default":
        return None
    if (
        not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", name)
        or name.endswith(".")
        or re.fullmatch(r"(?:con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\..*)?", name)
    ):
        raise MigrationError("Invalid OMP profile; specify --source-db explicitly")
    return name


def default_sessions():
    profile = profile_name(os.environ.get("OMP_PROFILE", os.environ.get("PI_PROFILE")))
    # node:path.join keeps an absolute-looking PI_CONFIG_DIR beneath homedir too.
    config = Path(
        os.path.normpath(
            str(Path.home()) + os.sep + (os.environ.get("PI_CONFIG_DIR") or ".omp")
        )
    )
    default = config / "profiles" / profile / "agent" if profile else config / "agent"
    override = os.environ.get("PI_CODING_AGENT_DIR")
    if not profile and override:
        try:
            legacy = profile_name(os.environ.get("PI_PROFILE"))
        except MigrationError:
            legacy = None
        if legacy and override == str(config / "profiles" / legacy / "agent"):
            override = None
    root = Path(override).absolute() if override and not profile else default
    xdg = os.environ.get("XDG_DATA_HOME")
    if root == default and xdg and sys.platform in ("darwin", "linux"):
        candidate = Path(xdg) / "omp"
        if profile:
            candidate = candidate / "profiles" / profile
        if candidate.exists():
            root = candidate
    return root / "sessions"


def source_path(value=None):
    root = (
        Path(value).expanduser().absolute() if value else default_sessions().absolute()
    )
    if is_link(root) or not root.is_dir():
        raise MigrationError("OMP source must be an existing non-linked directory")
    if (root / "sessions").is_dir():
        root = root / "sessions"
    if is_link(root):
        raise MigrationError("Linked OMP sessions directory")
    return root.resolve()


def read(path):
    rows = []
    # Bound individual physical records before JSON parsing, including a torn final write.
    with regular(path).open("rb") as stream:
        while True:
            line = stream.readline(MAX_RECORD + 1)
            if not line:
                break
            if len(line) > MAX_RECORD:
                raise MigrationError("OMP record exceeds size limit")
            if line.strip():
                rows.append(obj(parse(line.decode("utf-8"), path.name), "entry"))
    slot = None
    if rows and rows[0].get("type") == "title":
        slot = rows.pop(0)
        if slot.get("v") != 1 or isinstance(slot.get("v"), bool):
            raise MigrationError("Unsupported OMP title slot")
        string(slot.get("title"), "title")
        millis(slot.get("updatedAt"))
    if not rows or rows[0].get("type") != "session" or rows[0].get("version") != 3:
        raise MigrationError("Unsupported OMP session format; V3 required")
    header = rows[0]
    if not string(header.get("id"), "session ID") or not string(
        header.get("cwd"), "workspace"
    ):
        raise MigrationError("OMP session lacks identity/workspace")
    millis(header.get("timestamp"))
    if slot and slot["title"].strip():
        header = {**header, "title": slot["title"]}
    if header.get("title") is not None:
        string(header["title"], "title")
    return header, rows[1:]


def subagent(rows):
    return any(r.get("type") == "session_init" for r in rows)


def inventory(root):
    root = source_path(root)
    paths, info, errors, excluded, size = {}, {}, [], [], 0
    dirs = [root] + [p for p in sorted(root.iterdir()) if p.is_dir() and not is_link(p)]
    # Never recurse into per-session artifact directories, blobs, or subagent trees.
    for directory in dirs:
        for path in sorted(directory.glob("*.jsonl")):
            sid = None
            try:
                header, rows = read(path)
                sid = header["id"]
                if sid in paths:
                    raise MigrationError("Ambiguous OMP session ID: " + sid)
                paths[sid] = path
                size += path.stat().st_size
                if subagent(rows):
                    excluded.append(
                        {
                            "sourceId": sid,
                            "reason": "OMP session_init subagent transcript",
                        }
                    )
                    continue
                info[sid] = {
                    "id": sid,
                    "title": header.get("title"),
                    "workspace": header["cwd"],
                    "updatedAt": max(
                        [millis(header["timestamp"])]
                        + [millis(r.get("timestamp")) for r in rows]
                    ),
                    "archived": False,
                }
            except (MigrationError, OSError, ValueError, TypeError) as exc:
                errors.append({"sourceId": sid, "path": str(path), "error": str(exc)})
    return {
        "source": root,
        "ids": sorted(info),
        "paths": paths,
        "info": info,
        "errors": errors,
        "excluded": excluded,
        "bytes": size,
    }


def select_entries(rows):
    nodes = {}
    for row in rows:
        uid = string(row.get("id"), "entry ID")
        if not uid or uid in nodes or row.get("type") not in TYPES:
            raise MigrationError("Duplicate/unknown OMP entry")
        nodes[uid] = row
    if not rows:
        raise MigrationError("OMP session is empty")
    path, seen, uid = [], set(), rows[-1]["id"]
    while uid is not None:
        if uid not in nodes or uid in seen:
            raise MigrationError("Broken/cyclic OMP parent chain")
        row = nodes[uid]
        seen.add(uid)
        path.append(uid)
        if "parentId" not in row:
            raise MigrationError("OMP entry lacks parentId")
        uid = row["parentId"]
        if uid is not None and not isinstance(uid, str):
            raise MigrationError("Invalid OMP parentId")
    path.reverse()
    reset = max(
        (i for i, uid in enumerate(path) if nodes[uid]["type"] == "reset_boundary"),
        default=-1,
    )
    checkpoint = max(
        (i for i, uid in enumerate(path) if nodes[uid]["type"] == "compaction"),
        default=-1,
    )
    active, summary_id = path[:], None
    if reset > checkpoint:
        active = path[reset + 1 :]
    elif checkpoint >= 0:
        summary_id = path[checkpoint]
        row = nodes[summary_id]
        details = row.get("details")
        if (
            row.get("method") not in (None, "handoff", "soft", "shake")
            or row.get("preserveData")
            or row.get("providerReplayThroughEntryId")
            or (
                isinstance(details, dict)
                and details.get("kind") == "experimental-context-rollover"
            )
        ):
            raise MigrationError(
                "Unsupported OMP compaction: provider-native, snapcompact or preserved context requires a dedicated reader"
            )
        kept = string(row.get("firstKeptEntryId"), "firstKeptEntryId")
        if kept and kept not in path[:checkpoint]:
            raise MigrationError(
                "OMP compaction firstKeptEntryId is missing from the prior branch"
            )
        # An empty ID explicitly means summary-only (no retained prefix).
        active = (
            [summary_id]
            + (path[path.index(kept) : checkpoint] if kept else [])
            + path[checkpoint + 1 :]
        )
    for uid in path[reset + 1 :]:
        row = nodes[uid]
        if (
            row["type"] == "custom"
            and row.get("customType") == "experimental_context_notes"
        ):
            raise MigrationError("Unsupported OMP experimental context notes")
    return nodes, path, active, summary_id


def blocks(value):
    if isinstance(value, str):
        return [{"type": "text", "text": value}]
    if not isinstance(value, list) or any(not isinstance(p, dict) for p in value):
        raise MigrationError("Invalid OMP content blocks")
    return value


def text_content(value, warnings):
    out = []
    for part in blocks(value):
        if part.get("type") == "text":
            out.append(string(part.get("text"), "text"))
        elif part.get("type") == "image":
            warnings.append(
                "Attachment reference retained; bytes not copied: OMP image/blob"
            )
            out.append("[OMP 历史图片；图片内容未迁入]")
        else:
            raise MigrationError(
                "Unsupported OMP content block: " + str(part.get("type"))
            )
    return "\n".join(out)


def message(row):
    return (
        {**row, "role": "custom"}
        if row["type"] == "custom_message"
        else obj(row.get("message"), "message")
    )


def normalize(header, rows):
    if subagent(rows):
        raise MigrationError("OMP session_init subagent transcripts are excluded")
    nodes, path, active, summary_id = select_entries(rows)
    active_set = set(active)
    warnings, calls, results, failed = [], {}, {}, set()
    for uid in path:
        row = nodes[uid]
        if row["type"] != "message":
            continue
        msg = message(row)
        if msg.get("role") == "assistant":
            if msg.get("stopReason") not in (
                "stop",
                "length",
                "toolUse",
                "error",
                "aborted",
            ):
                raise MigrationError(
                    "OMP assistant pending/deferred/unknown completion"
                )
            if msg.get("retryRecovery") or msg["stopReason"] in ("error", "aborted"):
                failed.add(uid)
            for part in blocks(msg.get("content")):
                if part.get("type") == "toolCall":
                    cid = string(part.get("id"), "call ID")
                    if not cid or cid in calls:
                        raise MigrationError("Duplicate OMP tool call ID")
                    calls[cid] = (uid, part)
        elif msg.get("role") == "toolResult":
            cid = string(msg.get("toolCallId"), "result call ID")
            if cid in results or cid not in calls:
                raise MigrationError("OMP orphan/duplicate tool result")
            if msg.get("toolName") != calls[cid][1].get("name"):
                raise MigrationError("OMP tool result name mismatch")
            results[cid] = (uid, msg)
    # OMP retains an interrupted turn when its following continuity note carries
    # the unfinished thought. Reasoning itself remains display-only in MCode.
    context_entries = [
        uid
        for uid in active
        if nodes[uid]["type"] in ("message", "custom_message", "branch_summary")
        and not (
            nodes[uid]["type"] == "custom_message"
            and nodes[uid].get("customType") in TRANSIENT
        )
        and not (
            nodes[uid]["type"] == "message" and message(nodes[uid]).get("retryRecovery")
        )
    ]
    for previous, following in zip(context_entries, context_entries[1:]):
        next_row = nodes[following]
        if next_row["type"] in ("message", "custom_message"):
            next_msg = message(next_row)
            if (
                next_msg.get("role") == "custom"
                and next_msg.get("customType") == "interrupted-thinking"
            ):
                failed.discard(previous)
    title = header.get("title")
    if not title:
        title = next(
            (
                text_content(message(nodes[uid]).get("content"), warnings)
                .strip()
                .splitlines()[0][:120]
                for uid in path
                if nodes[uid]["type"] == "message"
                and message(nodes[uid]).get("role") == "user"
                and text_content(message(nodes[uid]).get("content"), warnings).strip()
            ),
            header["id"],
        )
    messages, display_ids, active_ids = [], [], []

    def convert_entry(uid, model):
        row = nodes[uid]
        typ = row["type"]
        role, semantics, parts = "user", None, []
        if typ in ("compaction", "branch_summary"):
            if typ == "compaction" and uid != summary_id:
                return None
            summary = string(row.get("summary"), "summary")
            if not summary.strip():
                raise MigrationError("OMP summary is empty")
            parts = [{"type": "text", "text": "[OMP 历史摘要]\n" + summary}]
            semantics = {"kind": "compact_summary"}
        elif typ in ("message", "custom_message"):
            msg = message(row)
            role = msg.get("role")
            if role == "system":
                return None
            if role in ("user", "custom", "hookMessage"):
                if (
                    model
                    and typ == "custom_message"
                    and msg.get("customType") in TRANSIENT
                ):
                    return None
                text = text_content(msg.get("content"), warnings)
                if role != "user":
                    text = "[OMP 历史扩展消息；仅供参考]\n" + text
                    semantics = {"providerVisibility": "visible"}
                    if msg.get("display"):
                        warnings.append(
                            "OMP extension renderer not migrated; content retained as labeled context"
                        )
                parts, role = [{"type": "text", "text": text}], "user"
            elif role == "assistant":
                if model and uid in failed:
                    return None
                for part in blocks(msg.get("content")):
                    kind = part.get("type")
                    if kind == "text":
                        parts.append(
                            {
                                "type": "text",
                                "text": string(part.get("text"), "assistant text"),
                            }
                        )
                    elif kind == "thinking":
                        if not part.get("redacted"):
                            parts.append(
                                {
                                    "type": "reasoning",
                                    "text": string(part.get("thinking"), "thinking"),
                                }
                            )
                    elif kind == "redactedThinking":
                        continue
                    elif kind == "toolCall":
                        cid = part["id"]
                        result = results.get(cid)
                        # Pair inside the effective context too; never pull output across /clear.
                        if model and (not result or result[0] not in active_set):
                            continue
                        state = {
                            "status": "pending",
                            "input": obj(part.get("arguments"), "tool arguments"),
                        }
                        if result:
                            value = result[1]
                            state.update(
                                status="error" if value.get("isError") else "completed",
                                output=text_content(value.get("content"), warnings),
                            )
                        else:
                            warnings.append(
                                "OMP unfinished historical tool call (display only): "
                                + cid
                            )
                        parts.append(
                            {
                                "type": "tool",
                                "tool": string(part.get("name"), "tool name"),
                                "callID": cid,
                                "state": state,
                            }
                        )
                    else:
                        raise MigrationError(
                            "Unsupported OMP assistant block: " + str(kind)
                        )
                if msg.get("errorMessage"):
                    parts.append(
                        {
                            "type": "text",
                            "text": "[OMP 历史助手错误]\n"
                            + string(msg["errorMessage"], "error"),
                        }
                    )
            elif role == "toolResult":
                cid = msg["toolCallId"]
                call_uid = calls[cid][0]
                if not model or call_uid in active_set or call_uid in failed:
                    return None
                role, semantics = "user", {"providerVisibility": "visible"}
                parts = [
                    {
                        "type": "text",
                        "text": "[OMP 历史工具结果；调用已在摘要之前]\n"
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
            elif role in ("bashExecution", "pythonExecution"):
                if model and msg.get("excludeFromContext"):
                    return None
                tool, key = (
                    ("bash", "command")
                    if role == "bashExecution"
                    else ("python", "code")
                )
                output = string(msg.get("output"), "execution output")
                if msg.get("images"):
                    output += "\n" + text_content(msg["images"], warnings)
                parts = [
                    {
                        "type": "tool",
                        "tool": tool,
                        "callID": uid,
                        "state": {
                            "status": "error"
                            if msg.get("cancelled")
                            or msg.get("exitCode") not in (None, 0)
                            else "completed",
                            "input": {key: string(msg.get(key), "execution input")},
                            "output": output,
                        },
                    }
                ]
                role = "assistant"
                if msg.get("truncated"):
                    warnings.append(
                        "OMP execution output truncated; artifact paths not read"
                    )
            elif role == "fileMention":
                files = msg.get("files")
                if not isinstance(files, list):
                    raise MigrationError("Invalid OMP file mentions")
                text = []
                for file in files:
                    file = obj(file, "file mention")
                    name = string(file.get("path"), "file path")
                    text.append(
                        "[OMP 历史文件内容："
                        + name
                        + "]\n"
                        + string(file.get("content"), "file content")
                    )
                    if file.get("image"):
                        text.append(text_content([file["image"]], warnings))
                    if file.get("skippedReason"):
                        warnings.append(
                            "Attachment reference retained; bytes not copied: OMP file "
                            + name
                        )
                        text.append(
                            "[文件内容未完整保存在来源中："
                            + string(file["skippedReason"], "skipped reason")
                            + "]"
                        )
                role, semantics = "user", {"providerVisibility": "visible"}
                parts = [{"type": "text", "text": "\n".join(text)}]
            else:
                raise MigrationError("Unsupported OMP message role: " + str(role))
        else:
            return None
        parts = [p for p in parts if p["type"] == "tool" or p.get("text")]
        if not parts:
            return None
        return {
            "createdAtMs": millis(row.get("timestamp")),
            "data": {"role": role, **({"semantics": semantics} if semantics else {})},
            "parts": parts,
        }

    # Reuse identical projections; context-only rewrites get a separate, namespaced ID.
    def append(uid, value, prefix):
        mid = prefix + uid
        messages.append(
            {
                **value,
                "id": mid,
                "parts": [
                    {"id": mid + ":" + str(i), "data": p}
                    for i, p in enumerate(value["parts"])
                ],
            }
        )
        return mid

    active_by_entry = {}
    for uid in path:
        visible = convert_entry(uid, False)
        if visible:
            mid = append(uid, visible, "d:")
            if not visible["data"].get("semantics"):
                display_ids.append(mid)
        if uid in active_set:
            value = convert_entry(uid, True)
            if value:
                active_by_entry[uid] = (
                    "d:" + uid if value == visible else append(uid, value, "a:")
                )
    active_ids = [active_by_entry[uid] for uid in active if uid in active_by_entry]
    if not active_ids:
        raise MigrationError("OMP session has no readable active history")
    if header.get("additionalDirectories"):
        warnings.append(
            "OMP additional workspace directories not mapped; only cwd is associated"
        )
    item = {
        "session": {
            "id": header["id"],
            "title": title,
            "directory": header["cwd"],
            "time_created": millis(header["timestamp"]),
            "time_updated": max(
                [millis(header["timestamp"])] + [millis(r["timestamp"]) for r in rows]
            ),
        },
        "desktop": {"title": title, "archived": False},
        "messages": messages,
        "histories": {"display": display_ids, "active": active_ids},
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
            raise MigrationError("Unknown OMP session ID: " + sid)
        path = data["paths"][sid]
        if is_link(data["source"]) or is_link(path.parent):
            raise MigrationError("Linked OMP session directory")
        header, rows = read(path)
        if header["id"] != sid:
            raise MigrationError("OMP session identity changed")
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
    "label": "OMP",
    "marker": "omp-migration.json",
    "archive": "omp-source.json",
    "id_prefix": "msg-omp-",
    "turn_prefix": "omp-",
    "provider": "omp-history",
    "display_kind": "omp_history_archive",
}
