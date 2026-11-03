"""Read-only OpenCode SQLite routing: legacy JSON records and V2 projections.

Schema detection never upgrades the source. Both layouts reuse normalized migration.
"""

import base64
import binascii
import importlib.util
import os
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace

from migrate import (
    MigrationError,
    compact,
    connect,
    digest,
    parse,
    regular,
    schema,
    timestamp,
)

_spec = importlib.util.spec_from_file_location(
    "opencode_legacy", Path(__file__).with_name("opencode_legacy.py")
)
legacy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(legacy)

COLUMNS = {
    "session_v2": {
        "id",
        "title",
        "directory",
        "version",
        "time_created",
        "time_updated",
        "time_archived",
        "revert",
        "parent_id",
        "fork_session_id",
        "fork_boundary",
        "time_compacting",
    },
    "session_message": {"id", "session_id", "type", "seq", "time_created", "data"},
}
IGNORED = {
    "idle",
    "agent-switched",
    "model-switched",
    "location-switched",
    "system",
    "skill",
}


def source_path(value=None):
    root = (
        Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
        / "opencode"
    )
    path = Path(
        value or os.environ.get("OPENCODE_DB") or root / "opencode.db"
    ).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() if value else root) / path
    if path.is_dir():
        path = path / "opencode.db"
    return regular(path)


def layout(db):
    tables = {
        r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    if "session_v2" in tables:
        schema(db, COLUMNS)
        if (
            "session" in tables
            and db.execute("SELECT 1 FROM session LIMIT 1").fetchone()
        ):
            raise MigrationError(
                "Mixed OpenCode legacy/V2 session tables; select an unambiguous source snapshot"
            )
        return "session_v2"
    legacy.check(db)
    return "session"


def inventory(path):
    path = source_path(path)
    with connect(path) as db:
        table = layout(db)
        sessions = {
            r["id"]: dict(r)
            for r in db.execute("SELECT * FROM " + table + " ORDER BY time_created,id")
        }
    return {
        "source": path,
        "sessions": sessions,
        "ids": sorted(sessions),
        "errors": [],
        "bytes": path.stat().st_size
        + (
            Path(str(path) + "-wal").stat().st_size
            if Path(str(path) + "-wal").is_file()
            else 0
        ),
    }


def string(value, label):
    if not isinstance(value, str):
        raise MigrationError("Invalid OpenCode " + label)
    return value


def obj(value, label):
    if not isinstance(value, dict):
        raise MigrationError("Invalid OpenCode " + label)
    return value


def array(value, label):
    if not isinstance(value, list):
        raise MigrationError("Invalid OpenCode " + label)
    return value


def attachments(files, warnings):
    result = []
    for file in array(files, "attachments"):
        obj(file, "attachment")
        mime = string(file.get("mime"), "attachment MIME")
        name = string(file.get("name", "attachment"), "attachment name")
        # Decode only inline textual evidence. Never fetch URLs/read source paths.
        if mime.startswith("text/") or mime in ("application/json", "application/xml"):
            if "data" in file:
                try:
                    text = base64.b64decode(
                        string(file["data"], "attachment data"), validate=True
                    ).decode("utf-8")
                except (ValueError, binascii.Error, UnicodeDecodeError) as exc:
                    raise MigrationError(
                        "Invalid OpenCode inline text attachment"
                    ) from exc
                result.append("[OpenCode 历史文本附件：" + name + "]\n" + text)
                continue
        warnings.append(
            "Attachment reference retained; bytes not copied: OpenCode " + name
        )
        result.append("[OpenCode 历史附件引用：" + name + "；内容未迁入]")
    return result


def tool_output(state, warnings):
    out = []
    for part in array(state.get("content", []), "tool content"):
        typ = obj(part, "tool content block").get("type")
        if typ == "text":
            out.append(string(part.get("text"), "tool text"))
        elif typ in ("image", "media", "file", "audio", "resource"):
            warnings.append(
                "Attachment reference retained; bytes not copied: OpenCode tool payload"
            )
        else:
            raise MigrationError("Unsupported OpenCode tool content: " + str(typ))
    if obj(state.get("metadata", {}), "tool metadata").get("truncated"):
        warnings.append(
            "OpenCode tool output was truncated in the source; external files not read"
        )
    if state.get("structured"):
        out.append(compact(obj(state["structured"], "structured tool output")))
    if state.get("error"):
        out.append(compact(state["error"]))
    if state.get("attachments"):
        out.extend(attachments(state["attachments"], warnings))
    return "\n".join(out)


def normalize(session, rows):
    if not string(session["version"], "version").startswith("2.0."):
        raise MigrationError(
            "Unsupported OpenCode version; verified V2 2.0.x projection required"
        )
    if session["revert"]:
        raise MigrationError(
            "OpenCode staged revert must be resolved in the source app before migration"
        )
    if session["time_compacting"]:
        raise MigrationError("OpenCode compaction is still running")
    if not string(session["directory"], "workspace"):
        raise MigrationError("OpenCode workspace is empty")
    messages, display, active, warnings = [], [], [], []
    seen, sequences = set(), set()
    title = session["title"]
    for row in rows:
        uid, typ, seq = row["id"], row["type"], row["seq"]
        if (
            not isinstance(uid, str)
            or not uid
            or uid in seen
            or not isinstance(seq, int)
            or seq in sequences
        ):
            raise MigrationError(
                "Invalid/duplicate OpenCode message identity or sequence"
            )
        seen.add(uid)
        sequences.add(seq)
        data = obj(parse(row["data"], uid), "message")
        if (
            data.get("id", uid) != uid
            or data.get("type", typ) != typ
            or data.get("sessionID", session["id"]) != session["id"]
        ):
            raise MigrationError("OpenCode message identity mismatch")
        if typ in IGNORED:
            continue
        parts, semantics = [], None
        role = "user"
        if typ == "user":
            text = string(data.get("text"), "user text")
            if not title and text.strip():
                title = text.strip().splitlines()[0][:120]
            parts.append({"type": "text", "text": text})
            parts.extend(
                {"type": "text", "text": value}
                for value in attachments(data.get("files", []), warnings)
            )
        elif typ == "synthetic":
            parts.append(
                {
                    "type": "text",
                    "text": "[OpenCode 历史上下文；仅供参考]\n"
                    + string(data.get("text"), "synthetic text"),
                }
            )
            semantics = {"providerVisibility": "visible"}
        elif typ == "shell":
            role = "assistant"
            status = data.get("status")
            if status not in ("running", "exited", "timeout", "killed"):
                raise MigrationError("Unsupported OpenCode shell status")
            output = obj(data.get("output", {}), "shell output")
            if output.get("truncated") or output.get("cursor", 0) < output.get(
                "size", 0
            ):
                warnings.append(
                    "OpenCode shell output is partial; external files not read"
                )
            parts.append(
                {
                    "type": "tool",
                    "tool": "shell",
                    "callID": string(data.get("shellID"), "shell ID"),
                    "state": {
                        "status": "completed"
                        if status == "exited" and data.get("exit", 0) == 0
                        else "running"
                        if status == "running"
                        else "error",
                        "input": {
                            "command": string(data.get("command"), "shell command")
                        },
                        "output": string(output.get("output", ""), "shell output text"),
                    },
                }
            )
        elif typ == "assistant":
            role = "assistant"
            if not obj(data.get("time"), "assistant time").get("completed"):
                raise MigrationError(
                    "OpenCode assistant is incomplete; wait for the source turn to finish"
                )
            for part in array(data.get("content"), "assistant content"):
                kind = obj(part, "assistant block").get("type")
                if kind in ("text", "reasoning"):
                    parts.append({"type": kind, "text": string(part.get("text"), kind)})
                elif kind == "tool":
                    state = obj(part.get("state"), "tool state")
                    status = state.get("status")
                    if status not in ("streaming", "running", "completed", "error"):
                        raise MigrationError("Unsupported OpenCode tool state")
                    if status in ("streaming", "running"):
                        warnings.append(
                            "OpenCode unfinished historical tool; never re-executed"
                        )
                    value = state.get("input")
                    if not isinstance(value, (dict, str)):
                        raise MigrationError("Invalid OpenCode tool input")
                    output = tool_output(state, warnings)
                    if obj(part.get("time", {}), "tool time").get("pruned"):
                        warnings.append("OpenCode tool output was pruned in the source")
                    parts.append(
                        {
                            "type": "tool",
                            "tool": string(part.get("name"), "tool name"),
                            "callID": string(part.get("id"), "tool ID"),
                            "state": {
                                "status": status,
                                "input": value,
                                "output": output,
                            },
                        }
                    )
                else:
                    raise MigrationError(
                        "Unsupported OpenCode assistant block: " + str(kind)
                    )
            if data.get("error"):
                parts.append(
                    {
                        "type": "text",
                        "text": "[OpenCode 历史助手错误]\n" + compact(data["error"]),
                    }
                )
        elif typ == "compaction":
            status = data.get("status")
            if status == "failed":
                warnings.append(
                    "OpenCode failed compaction skipped; earlier history retained"
                )
                continue
            if status != "completed":
                raise MigrationError("OpenCode compaction incomplete/unsupported")
            if data.get("providerContext") is not None:
                raise MigrationError(
                    "OpenCode provider-native checkpoint requires plaintext reconstruction; not supported yet"
                )
            summary = string(data.get("summary"), "compaction summary")
            recent = string(data.get("recent"), "compaction recent context")
            if not summary.strip():
                raise MigrationError("OpenCode compaction lacks readable summary")
            parts.append(
                {
                    "type": "text",
                    "text": "[OpenCode 历史压缩摘要]\n"
                    + summary
                    + "\n[保留的近期上下文]\n"
                    + recent,
                }
            )
            semantics = {"kind": "compact_summary"}
            active = []
        else:
            raise MigrationError("Unsupported OpenCode message type: " + str(typ))
        parts = [p for p in parts if p.get("type") == "tool" or p.get("text")]
        if not parts:
            continue
        messages.append(
            {
                "id": uid,
                "createdAtMs": timestamp(row["time_created"]),
                "data": {
                    "role": role,
                    **({"semantics": semantics} if semantics else {}),
                },
                "parts": [
                    {"id": uid + ":" + str(i), "data": p} for i, p in enumerate(parts)
                ],
            }
        )
        if typ != "compaction":
            display.append(uid)
        if not (
            typ == "shell"
            and obj(data.get("metadata", {}), "shell metadata").get("background")
            is True
        ):
            active.append(uid)
    if not active:
        raise MigrationError("OpenCode session has no readable conversation")
    item = {
        "session": {
            "id": session["id"],
            "title": title or session["id"],
            "directory": session["directory"],
            "time_created": timestamp(session["time_created"]),
            "time_updated": timestamp(session["time_updated"]),
        },
        "desktop": {
            "title": title or session["id"],
            "archived": session["time_archived"] is not None,
        },
        "messages": messages,
        "histories": {"display": display, "active": active},
        "warnings": sorted(set(warnings)),
    }
    item["fingerprint"] = digest(item)
    return item


def load_inventory(data, ids, context_dir=None):
    if context_dir:
        raise MigrationError("Context bundles are only supported for Codex")
    result = []
    with connect(data["source"]) as db:
        table = layout(db)
        for sid in sorted(ids):
            session = db.execute(
                "SELECT * FROM " + table + " WHERE id=?", (sid,)
            ).fetchone()
            if session is None:
                raise MigrationError("Unknown OpenCode session ID: " + sid)
            if table == "session":
                result.append(
                    legacy.load(
                        db,
                        dict(session),
                        SimpleNamespace(
                            IGNORED=IGNORED,
                            normalize=normalize,
                            string=string,
                            obj=obj,
                            attachments=attachments,
                        ),
                    )
                )
                continue
            rows = db.execute(
                "SELECT * FROM session_message WHERE session_id=? ORDER BY seq,id",
                (sid,),
            ).fetchall()
            result.append(normalize(dict(session), rows))
    return result


def load_source(path, ids=None):
    data = inventory(path)
    return load_inventory(data, data["ids"] if ids is None else ids)


def overview(path, ids=None):
    data = inventory(path)
    selected = set(data["ids"] if ids is None else ids)
    return [
        {
            "id": sid,
            "title": r["title"] or sid,
            "workspace": r["directory"],
            "workspaceExists": Path(r["directory"]).is_dir()
            and (os.name == "nt" or not PureWindowsPath(r["directory"]).drive),
            "updatedAt": r["time_updated"],
            "archived": r["time_archived"] is not None,
        }
        for sid, r in data["sessions"].items()
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
    "label": "OpenCode",
    "marker": "opencode-migration.json",
    "archive": "opencode-source.json",
    "id_prefix": "msg-opencode-",
    "turn_prefix": "opencode-",
    "provider": "opencode-history",
    "display_kind": "opencode_history_archive",
}
