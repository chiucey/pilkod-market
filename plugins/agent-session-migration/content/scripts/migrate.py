#!/usr/bin/env python3
"""Agent session migration into MiniMax Code. Supports ZCode, Codex, Claude Code, OpenCode, Pi Agent and OMP. Python 3.9+."""

import argparse
import base64
import contextlib
import hashlib
import json
import os
import sqlite3
import sys
import time
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path

FORMAT = 1
ADAPTER_VERSION = 2
MAX_RECORD = 16 * 1024 * 1024
TARGET_COLUMNS = {
    "local_runtime_pi_history_file_migrations": {
        "session_id",
        "migrated_at_ms",
        "source",
        "message_count",
        "target_revision",
    },
    "local_runtime_sessions": {
        "session_id",
        "record_json",
        "updated_at_ms",
        "columnar_version",
        "agent_name",
        "runtime",
        "session_type",
        "status",
        "archived",
        "visibility",
        "session_kind",
        "purpose_kind",
        "workspace_dir",
        "project_workspace_dir",
        "is_default_workspace",
        "title",
        "created_at_ms",
        "extra_data_json",
        "project_id",
        "history_relative_dir",
    },
    "local_runtime_message_rows": {
        "session_id",
        "msg_id",
        "role",
        "turn_id",
        "source",
        "created_at_ms",
        "data_json",
    },
    "local_runtime_projects": {
        "project_id",
        "project_kind",
        "workspace_dir",
        "created_at_ms",
        "updated_at_ms",
        "hidden",
        "extra_data_json",
    },
    "local_runtime_session_fts_keys": {"fts_rowid", "session_id"},
    "local_runtime_sessions_fts": {
        "session_id",
        "session_id_terms",
        "agent_name_terms",
        "title_terms",
        "workspace_dir_terms",
        "purpose_terms",
        "status_terms",
        "session_type_terms",
    },
}


class MigrationError(Exception):
    pass


# Source adapters. plan()/apply() own the migration lock, the online backup, the single
# write transaction, rollback and readback, and stay source-agnostic. A source only
# supplies its own reader plus the naming dialect used for provenance and history labels.
SOURCE_ADAPTERS = {
    "zcode": "zcode_source.py",
    "codex": "codex_source.py",
    "claude-code": "claude_source.py",
    "opencode": "opencode_source.py",
    "pi-agent": "pi_source.py",
    "omp": "omp_source.py",
}
ADAPTERS = {}
ACTIVE = "zcode"


def adapter(name=None):
    key = name or ACTIVE
    if key not in SOURCE_ADAPTERS:
        raise MigrationError("Unsupported source: " + str(key))
    if key not in ADAPTERS:
        import importlib.util
        import types

        current = sys.modules.get(__name__)
        if current is None:
            current = types.ModuleType("migrate")
            current.__dict__.update(globals())
        spec = importlib.util.spec_from_file_location(
            key + "_source", Path(__file__).with_name(SOURCE_ADAPTERS[key])
        )
        if spec is None or spec.loader is None:
            raise MigrationError("Source adapter is missing: " + key)
        module = importlib.util.module_from_spec(spec)
        previous = sys.modules.get("migrate")
        sys.modules["migrate"] = current
        try:
            spec.loader.exec_module(module)
        finally:
            if previous is None:
                sys.modules.pop("migrate", None)
            else:
                sys.modules["migrate"] = previous
        ADAPTERS[key] = module.ADAPTER
    return ADAPTERS[key]


def use(name):
    global ACTIVE
    ACTIVE = name
    return adapter(name)


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(compact(value).encode()).hexdigest()


def history_revision(records):
    # The importer emits canonical envelopes with ASCII keys and integer numbers.
    # Match Runtime's recursively key-sorted JSON semantic revision exactly.
    raw = json.dumps(
        records,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def initialize_history(db, sid, records):
    # 'empty' describes the legacy MCode source. The imported JSONL is already
    # authoritative; first-turn materialization must not compare it to no history.
    insert(
        db,
        "local_runtime_pi_history_file_migrations",
        {
            "session_id": sid,
            "migrated_at_ms": int(time.time() * 1000),
            "source": "empty",
            "message_count": len(records),
            "target_revision": history_revision(records),
        },
    )


def is_link(path):
    # Windows junctions are reparse points too; Python 3.9 has no Path.is_junction.
    import stat

    try:
        return path.is_symlink() or bool(
            getattr(path.lstat(), "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        )
    except FileNotFoundError:
        return False


def regular(path):
    path = Path(path).expanduser().absolute()
    if is_link(path) or not path.is_file():
        raise MigrationError("Expected an existing regular file: " + str(path))
    return path


@contextlib.contextmanager
def connect(path, writable=False):
    path = regular(path).resolve()
    db = sqlite3.connect(
        path.as_uri() + ("?mode=rw" if writable else "?mode=ro"), uri=True, timeout=10
    )
    try:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        if not writable:
            db.execute("PRAGMA query_only=ON")
            db.execute("BEGIN")
        yield db
    except sqlite3.OperationalError as exc:
        if not writable and "unable to open database file" in str(exc):
            raise MigrationError(
                "Cannot read SQLite database: "
                + str(path)
                + "; verify directory access and open the owning app so SQLite can initialize WAL sidecars. "
                "Do not delete WAL/SHM files or bypass them with immutable mode."
            ) from exc
        raise
    finally:
        db.close()


def schema(db, required):
    for table, columns in required.items():
        found = {r["name"] for r in db.execute('PRAGMA table_info("' + table + '")')}
        if not columns <= found:
            raise MigrationError(
                "Unsupported schema for "
                + table
                + ": missing "
                + ", ".join(sorted(columns - found))
            )


def parse(raw, location):
    if not isinstance(raw, str) or len(raw.encode()) > MAX_RECORD:
        raise MigrationError("Oversized/invalid JSON at " + location)
    try:
        result = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise MigrationError("Malformed JSON at " + location) from exc
    if not isinstance(result, dict):
        raise MigrationError("Expected JSON object at " + location)
    return result


def timestamp(value):
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 0 <= value <= 253402300799999
    ):
        raise MigrationError("Expected Unix milliseconds")
    return value


# Compatibility facades for existing integrations; implementation belongs to the adapter.
def source_path(value=None):
    return adapter("zcode")["source_path"](value)


def load_source(path, ids=None):
    return adapter("zcode")["load_source"](path, ids)


def target_path(value):
    if not value:
        raise MigrationError(
            "An explicit --target-data-dir from the selected MiniMax profile is required"
        )
    root = Path(value).expanduser().absolute()
    if is_link(root) or not root.is_dir():
        raise MigrationError("Target must be an existing non-symlink data directory")
    root = root.resolve()
    safe_directory(root, "v2/sqlite")
    regular(root / "v2/sqlite/runtime-state.sqlite")
    return root


def safe_directory(root, relative):
    path = root
    for part in Path(relative).parts:
        if part in ("..", ".", "") or Path(part).is_absolute():
            raise MigrationError("Unsafe output path")
        path = path / part
        if is_link(path):
            raise MigrationError("Symlink in output path: " + str(path))
        if path.exists() and not path.is_dir():
            raise MigrationError("Not a directory: " + str(path))
    return path


def private_write(path, value):
    data = value.encode("utf-8")
    with open(path, "xb") as out:
        os.chmod(path, 0o600)
        out.write(data)
        out.flush()
        os.fsync(out.fileno())


def identity(source, source_id):
    return (
        "mvs_"
        + hashlib.sha256(
            (str(source.resolve()) + "\0" + source_id).encode()
        ).hexdigest()[:32]
    )


def history_dir(sid, created):
    dt = datetime.fromtimestamp(created / 1000, timezone.utc)
    encoded = base64.urlsafe_b64encode(sid.encode()).decode().rstrip("=")
    return (
        dt.strftime("%Y/%m/%d/%H-%M-%S-")
        + str(created % 1000).zfill(3)
        + "-session_"
        + encoded
    )


def source_parts(msg):
    return [part["data"] for part in msg["parts"]]


def select_histories(item):
    messages = item["messages"]
    ids = {msg["id"] for msg in messages}
    if len(ids) != len(messages):
        raise MigrationError("Duplicate source message identity")

    def reference(value):
        if not isinstance(value, str) or value not in ids:
            raise MigrationError(
                "Missing/invalid source history boundary reference: " + str(value)
            )

    # Source adapters can resolve their native checkpoint semantics independently.
    histories = item.get("histories")
    if histories is not None:
        if not isinstance(histories, dict) or set(histories) != {"display", "active"}:
            raise MigrationError("Invalid source history selection")
        by_id = {msg["id"]: msg for msg in messages}
        selected = []
        for key in ("display", "active"):
            values = histories[key]
            if not isinstance(values, list):
                raise MigrationError("Invalid source history selection")
            for value in values:
                reference(value)
            if len(values) != len(set(values)):
                raise MigrationError("Duplicate source history selection")
            selected.append([by_id[value] for value in values])
        return tuple(selected)

    return adapter()["select_histories"](item)


PROVIDER_SOURCES = {
    "agent_control_message",
    "background_task",
    "goal-continuation",
    "goal_completion_verification",
    "goal_state_change",
    "plugin_reference",
    "queued_system_notification",
    "resume_goal_state",
    "resume_referenced_session_context",
    "rewind",
    "selection_side_chat",
    "subagent",
    "subagent_message",
    "target_continuation",
    "task_notification",
    "task_status",
    "todo_reminder",
}


def projection(msg):
    # Shared normalized-message policy; source-only control is not a real user input.
    data = msg["data"]
    parts = source_parts(msg)
    for record in [data, *parts]:
        metadata = record.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise MigrationError("Unsupported source message/part metadata")
        fork = (metadata or {}).get("forkContext")
        if fork is not None and not isinstance(fork, dict):
            raise MigrationError("Unsupported source fork metadata")
        if record.get("type") == "text" and not isinstance(record.get("text"), str):
            raise MigrationError("Invalid source text part")
    semantics = data.get("semantics") or {}
    if not isinstance(semantics, dict):
        raise MigrationError("Unsupported message semantics")
    if semantics.get("kind") == "compact_summary" or "summary" in data:
        return "summary"
    if semantics:
        if semantics.get("kind") == "timeline_event":
            return "timeline"
        if (
            semantics.get("origin") == "real_user"
            and data.get("synthetic") is not True
            and data.get("visibility") != "model-only"
        ):
            return "user"
        if (
            data.get("role") == "assistant"
            and semantics.get("kind") == "assistant_response"
            and semantics.get("uiVisibility") == "visible"
            and semantics.get("transcriptVisibility") == "visible"
        ):
            return "assistant"
        if semantics.get("providerVisibility") == "visible":
            return "context"
        if semantics.get("kind") == "fork_notice":
            return "timeline"
        if (
            semantics.get("origin") == "agent_runtime"
            or semantics.get("uiVisibility") == "hidden"
            or semantics.get("transcriptVisibility") == "hidden"
        ):
            return "hidden"
        raise MigrationError(
            "Unsupported message semantics; cannot safely classify source message"
        )
    metadata = data.get("metadata") or {}
    source = (
        data.get("source")
        or metadata.get("source")
        or semantics.get("source")
        or next(
            (
                (p.get("metadata") or {}).get("source")
                for p in parts
                if (p.get("metadata") or {}).get("source")
            ),
            None,
        )
    )
    if data.get("visibility") == "model-only" or any(
        (p.get("metadata") or {}).get("visibility") == "model-only"
        or (p.get("metadata") or {}).get("source") == "goal-continuation"
        for p in parts
    ):
        return "context"
    if source == "fork" or any(
        p.get("type") == "timeline"
        or ((p.get("metadata") or {}).get("forkContext") or {}).get("kind")
        == "session_fork"
        or p.get("type") == "compaction"
        and (
            isinstance((p.get("metadata") or {}).get("timelineStatus"), str)
            or isinstance(p.get("summaryMessageId"), str)
        )
        for p in parts
    ):
        return "timeline"
    text = "".join(
        p.get("text", "")
        for p in parts
        if p.get("type") == "text" and p.get("ignored") is not True
    ).lstrip()
    control = (
        text.startswith('<system-reminder source="goal-continuation">')
        or text.startswith("<system-reminder>")
        and (
            "Continue working toward the active session goal." in text
            or "Current session goal state" in text
        )
        or "Conversation rewind applied." in text
        or "Workspace rewind applied." in text
    )
    synthetic = data.get("synthetic") is True or any(
        p.get("synthetic") is True for p in parts
    )
    if (
        source in PROVIDER_SOURCES
        or control
        or synthetic
        and text.startswith(("<task-notification>", "<subagent-notification>"))
    ):
        return "context"
    if synthetic:
        return "hidden"
    return "assistant" if data.get("role") == "assistant" else "user"


def message_identity(sid, msg, policy):
    raw = hashlib.sha256((sid + "\0" + msg["id"]).encode()).digest()
    if msg["data"].get("role") == "user" and policy == "user":
        return "msg-user-v1-" + base64.urlsafe_b64encode(raw).decode().rstrip("=")
    return adapter()["id_prefix"] + raw.hex()[:32]


def historical_detail(value):
    """Plain code-panel text with real line breaks, not a quoted JSON blob."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n\n".join(
            str(k) + ":\n" + historical_detail(v) for k, v in value.items()
        )
    if isinstance(value, list):
        return "\n\n".join(
            "[" + str(i + 1) + "]\n" + historical_detail(v) for i, v in enumerate(value)
        )
    return compact(value)


def historical_tool_view(evidence, mid, index, label):
    """Display-only protocol record. Never a canonical/provider tool invocation."""
    # Do not dispatch arbitrary source names to native interactive tool renderers.
    # The original status is metadata; even unfinished source calls are inert here.
    args = {
        "来源": label,
        "工具": evidence.get("tool"),
        "原始状态": evidence.get("status"),
        "说明": "历史记录，仅供阅读，不重新执行",
        "输入": evidence.get("input"),
    }
    result = {k: v for k, v in evidence.items() if k not in ("tool", "input")}
    return {
        "tool_name": "历史工具记录",
        "tool_call_id": mid + "-history-" + str(index),
        "tool_call_status": 2,
        "tool_call_args": compact(historical_detail(args)),
        "tool_call_result_data": compact(
            {"content": [{"type": "text", "text": historical_detail(result)}]}
        ),
    }


def historical_file_text(part, label):
    """A reference is not an uploaded attachment and must not imply copied bytes."""
    name = part.get("filename") or part.get("name") or "附件"
    path = part.get("url") or part.get("path") or part.get("file_path")
    return (
        "["
        + label
        + " 历史附件引用，未复制文件]\n"
        + str(name)
        + ("\n" + str(path) if path else "\n" + compact(part))
    )


def convert(item, sid):
    dialect = adapter()
    label = dialect["label"]
    # Reader-side warnings (unparseable or skipped source records) travel with the item.
    display, canonical, warnings = [], [], list(item.get("warnings") or [])
    turn = dialect["turn_prefix"] + sid
    zero_usage = {
        "input": 0,
        "output": 0,
        "cacheRead": 0,
        "cacheWrite": 0,
        "totalTokens": 0,
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "total": 0},
    }
    display_messages, active_messages = select_histories(item)
    visible_ids = {msg["id"] for msg in display_messages}
    active_ids = {msg["id"] for msg in active_messages}
    canonical_by_id = {}
    for msg in item["messages"]:
        if msg["id"] not in visible_ids and msg["id"] not in active_ids:
            continue
        data = msg["data"]
        role = data.get("role")
        if role not in ("user", "assistant"):
            warnings.append(
                "Non-conversation role retained only in source archive: " + str(role)
            )
            continue
        policy = projection(msg)
        if policy in ("hidden", "timeline"):
            warnings.append(
                "Runtime/timeline record retained only in source archive: " + msg["id"]
            )
            continue
        mid = message_identity(sid, msg, policy)
        if role == "user" and policy == "user":
            turn = dialect["turn_prefix"] + msg["id"]
        texts, thoughts = [], []
        view_texts, view_tools = [], []
        for part in msg["parts"]:
            p = part["data"]
            typ = p.get("type")
            if typ == "text":
                if not isinstance(p.get("text"), str):
                    raise MigrationError("Invalid text part: " + part["id"])
                if p.get("ignored") is not True:
                    texts.append(p["text"])
                    presenter = (
                        dialect.get("display_user_text") if role == "user" else None
                    )
                    view_texts.append(presenter(p["text"]) if presenter else p["text"])
            elif typ == "reasoning":
                if isinstance(p.get("text"), str):
                    thoughts.append(p["text"])
            elif typ == "tool":
                state = p.get("state")
                if not isinstance(state, dict):
                    raise MigrationError("Invalid tool state: " + part["id"])
                evidence = {
                    "tool": p.get("tool"),
                    "callID": p.get("callID"),
                    "status": state.get("status"),
                    "input": state.get("input"),
                }
                for key in ("output", "error", "title", "attachments"):
                    if key in state:
                        evidence[key] = state[key]
                metadata = state.get("metadata") or {}
                if not isinstance(metadata, dict):
                    raise MigrationError("Invalid tool metadata: " + part["id"])
                for key in ("modelContent", "modelContentLayout"):
                    if key in metadata:
                        evidence[key] = metadata[key]
                attachments = state.get("attachments") or []
                if not isinstance(attachments, list):
                    raise MigrationError("Invalid tool attachments: " + part["id"])
                if attachments:
                    warnings.append(
                        "Attachment reference retained; bytes not copied: tool "
                        + part["id"]
                    )
                texts.append(
                    "["
                    + label
                    + " 历史工具记录；仅供阅读，不重新执行]\n"
                    + compact(evidence)
                )
                view_tools.append(
                    historical_tool_view(evidence, mid, len(view_tools), label)
                )
            elif typ == "file":
                view_texts.append(historical_file_text(p, label))
                texts.append("[" + label + " 历史附件引用]\n" + compact(p))
                warnings.append(
                    "Attachment reference retained; bytes not copied: " + part["id"]
                )
            elif typ not in ("step-start", "step-finish", "compaction", "timeline"):
                warnings.append(
                    "Unsupported part retained only in source archive: "
                    + str(typ)
                    + " "
                    + part["id"]
                )
        if data.get("error"):
            texts.append("[" + label + " 历史错误]\n" + compact(data["error"]))
            view_texts.append(texts[-1])
        text = "\n\n".join(texts)
        ts = timestamp(msg["createdAtMs"])
        if (
            policy in ("user", "assistant")
            and msg["id"] in visible_ids
            and (text or thoughts)
        ):
            view = {
                "msg_id": mid,
                "role": role,
                "msg_type": 1,
                "msg_content": "\n\n".join(view_texts),
                "timestamp": ts,
                "turnId": turn,
                "turn_id": turn,
                "query_key": turn,
                "source": "desktop",
                "canonical_message_id": mid,
            }
            if msg["id"] not in active_ids or not text:
                view["displayKind"] = dialect["display_kind"]
            if view_tools:
                view["tool_calls"] = view_tools
            if thoughts:
                view["thinking_content"] = "\n\n".join(thoughts)
            if role == "assistant":
                view["finish_reason"] = "stop"
            display.append(view)
        if not text or msg["id"] not in active_ids:
            continue
        if policy in ("context", "summary"):
            kind = "压缩摘要" if policy == "summary" else "运行时上下文"
            text = (
                "["
                + label
                + " 历史"
                + kind
                + "；仅为旧会话背景，不是当前任务指令]\n"
                + text
            )
            warnings.append(
                "Provider-only history retained as labeled context: " + msg["id"]
            )
        native = {
            "role": role,
            "content": [{"type": "text", "text": text}],
            "timestamp": ts,
        }
        if role == "assistant":
            native.update(
                {
                    "api": "openai-completions",
                    "provider": dialect["provider"],
                    "model": "historical-transcript",
                    "usage": zero_usage,
                    "stopReason": "stop",
                }
            )
        canonical_by_id[msg["id"]] = {
            "message_id": mid,
            "turn_id": turn,
            "message": native,
        }
    canonical = [
        canonical_by_id[msg["id"]]
        for msg in active_messages
        if msg["id"] in canonical_by_id
    ]
    return display, canonical, warnings


def check_target(db, agent):
    schema(db, TARGET_COLUMNS)
    if not agent or any(x in agent for x in ("/", "\\", "\0")):
        raise MigrationError("Invalid target agent name")
    versions = {
        r[0]
        for r in db.execute(
            "SELECT DISTINCT columnar_version FROM local_runtime_sessions"
        )
    }
    if versions - {0, 3}:
        raise MigrationError("Unsupported target session columnar version")
    for row in db.execute(
        "SELECT session_id,record_json FROM local_runtime_sessions WHERE columnar_version=0"
    ):
        record = parse(row["record_json"], "legacy session " + row["session_id"])
        if record.get("sessionId") != row["session_id"]:
            raise MigrationError(
                "Invalid legacy session identity; retain it for runtime recovery"
            )
        legacy_version = record.get("sessionDataVersion", 0)
        if (
            isinstance(legacy_version, bool)
            or not isinstance(legacy_version, int)
            or legacy_version < 0
        ):
            raise MigrationError("Invalid legacy session data version")
        if legacy_version > 4:
            raise MigrationError("Newer legacy session data contract detected")
    if not db.execute(
        "SELECT 1 FROM local_runtime_sessions WHERE agent_name=? AND columnar_version=3 LIMIT 1",
        (agent,),
    ).fetchone():
        raise MigrationError(
            "Target agent has no existing session; initialize it in MiniMax Code first"
        )
    future = db.execute(
        "SELECT 1 FROM local_runtime_sessions WHERE json_extract(extra_data_json,'$.sessionDataVersion') > 4 LIMIT 1"
    ).fetchone()
    if future:
        raise MigrationError(
            "Newer session data contract detected; update the migration plugin"
        )
    return db.execute(
        "SELECT COUNT(*) FROM local_runtime_sessions WHERE columnar_version=0"
    ).fetchone()[0]


def plan(
    source, target, agent, ids=None, workspace=None, restore_projects=False, _items=None
):
    dialect = adapter()
    items = dialect["load_source"](source, ids) if _items is None else _items
    with connect(target / "v2/sqlite/runtime-state.sqlite") as db:
        legacy_count = check_target(db, agent)
        planned = []
        for item in items:
            s = item["session"]
            sid = identity(source, s["id"])
            created = timestamp(s["time_created"])
            timestamp(s["time_updated"])
            cwd = str(Path(workspace or s["directory"]).expanduser().resolve())
            if not Path(cwd).is_dir():
                raise MigrationError("Missing workspace; use --workspace: " + cwd)
            rel = history_dir(sid, created)
            directory = safe_directory(target, "v2/sessions/" + rel)
            display, canonical, warnings = [], [], []
            status = "new"
            existing = db.execute(
                "SELECT title,history_relative_dir,agent_name,created_at_ms,updated_at_ms FROM local_runtime_sessions WHERE session_id=?",
                (sid,),
            ).fetchone()
            if existing:
                marker = directory / dialect["marker"]
                if not marker.is_file() or is_link(marker):
                    raise MigrationError(
                        "Existing target identity has no migration provenance: " + sid
                    )
                provenance = parse(marker.read_text(encoding="utf-8"), str(marker))
                if provenance.get("fingerprint") != item["fingerprint"]:
                    raise MigrationError(
                        "Source changed after migration; refusing to overwrite continued target session: "
                        + s["id"]
                    )
                if (
                    existing["history_relative_dir"] != rel
                    or existing["agent_name"] != agent
                    or provenance.get("workspace") != cwd
                ):
                    raise MigrationError("Existing migration target differs: " + sid)
                regular(directory / "messages.jsonl")
                # Readback counts describe persisted target state, including continued turns.
                display = [
                    dict(row)
                    for row in db.execute(
                        "SELECT msg_id FROM local_runtime_message_rows WHERE session_id=?",
                        (sid,),
                    )
                ]
                with open(directory / "messages.jsonl", encoding="utf-8") as history:
                    canonical = [
                        parse(line, str(directory / "messages.jsonl"))
                        for line in history
                        if line.strip()
                    ]
                created = timestamp(existing["created_at_ms"])
                if provenance.get("adapterVersion", 1) < ADAPTER_VERSION:
                    warnings.append(
                        "Imported by an older adapter; existing history is unchanged and is not automatically repaired"
                    )
                if not db.execute(
                    "SELECT 1 FROM local_runtime_pi_history_file_migrations WHERE session_id=?",
                    (sid,),
                ).fetchone():
                    raise MigrationError(
                        "Existing import needs history repair; run repair --target-session "
                        + sid
                    )
                status = "already-imported"
            elif directory.exists():
                raise MigrationError(
                    "Uncommitted history directory exists; inspect recovery manifest before retry: "
                    + str(directory)
                )
            project_state = None
            restore_boundary = None
            source_created = timestamp(s["time_created"])
            updated = timestamp(
                existing["updated_at_ms"] if existing else s["time_updated"]
            )
            if status == "new":
                display, canonical, warnings = convert(item, sid)
                project = db.execute(
                    "SELECT project_id,hidden,extra_data_json,updated_at_ms FROM local_runtime_projects WHERE project_kind='workspace' AND workspace_dir=?",
                    (cwd,),
                ).fetchone()
                if project:
                    project_state = dict(project)
                    removal = parse(
                        project["extra_data_json"], "project extra data"
                    ).get("sidebarRemoval")
                    cutoff = (
                        timestamp(removal["atMs"])
                        if isinstance(removal, dict) and "atMs" in removal
                        else None
                    )
                    if removal is not None and cutoff is None:
                        raise MigrationError("Unsupported project removal boundary")
                    if project["hidden"]:
                        latest = (
                            db.execute(
                                "SELECT MAX(created_at_ms) FROM local_runtime_sessions WHERE project_id=?",
                                (project["project_id"],),
                            ).fetchone()[0]
                            or 0
                        )
                        cutoff = max(
                            int(time.time() * 1000),
                            project["updated_at_ms"],
                            cutoff or 0,
                            latest,
                        )
                        at_boundary = [
                            r[0]
                            for r in db.execute(
                                "SELECT session_id FROM local_runtime_sessions WHERE project_id=? AND created_at_ms=?",
                                (project["project_id"], cutoff),
                            )
                        ]
                        restore_boundary = {"atMs": cutoff, "boundaryIds": at_boundary}
                    removed = cutoff is not None and (
                        created < cutoff
                        or created == cutoff
                        and sid in (restore_boundary or removal).get("boundaryIds", [])
                    )
                    if project["hidden"] or removed:
                        if not restore_projects:
                            raise MigrationError(
                                "Workspace project was removed; use --restore-projects only after explicitly accepting restoration: "
                                + cwd
                            )
                        if removed:
                            created = max(int(time.time() * 1000), cutoff + 1)
                        updated = max(updated, created)
                        warnings.append(
                            "Project explicitly restored; original source timestamps remain in provenance and source archive"
                        )
            if legacy_count:
                warnings.append(
                    "Preserved existing legacy columnar_version=0 rows: "
                    + str(legacy_count)
                )
            source_title = item["desktop"]["title"] if item["desktop"] else s["title"]
            prefix = "[From " + dialect["label"] + "]"
            title = source_title
            if existing:
                title = existing["title"]
            elif not title.startswith(prefix):
                title = prefix + " " + title
            planned.append(
                {
                    "sourceCreatedAtMs": source_created,
                    "sourceUpdatedAtMs": timestamp(s["time_updated"]),
                    "projectState": project_state,
                    "restoreBoundary": restore_boundary,
                    "canonicalMessageCount": len(canonical),
                    "sourceId": s["id"],
                    "targetId": sid,
                    "title": title,
                    "archived": bool(
                        item["desktop"]["archived"]
                        if item["desktop"]
                        else dict(s).get("time_archived")
                    ),
                    "workspace": cwd,
                    "historyRelativeDir": rel,
                    "createdAtMs": created,
                    "updatedAtMs": updated,
                    "fingerprint": item["fingerprint"],
                    "messageCount": len(display),
                    "warnings": warnings,
                    **(
                        {"contextReconstruction": item["contextReconstruction"]}
                        if item.get("contextReconstruction")
                        else {}
                    ),
                    "status": status,
                    "item": item,
                    "display": display,
                    "canonical": canonical,
                }
            )
    return planned


def public_plan(rows):
    return [
        {
            k: v
            for k, v in r.items()
            if k
            not in ("item", "display", "canonical", "projectState", "restoreBoundary")
        }
        for r in rows
    ]


def insert(db, table, record):
    columns = list(record)
    db.execute(
        "INSERT INTO "
        + table
        + " ("
        + ",".join(columns)
        + ") VALUES ("
        + ",".join("?" for _ in columns)
        + ")",
        [record[x] for x in columns],
    )


@contextlib.contextmanager
def migration_lock(target):
    root = safe_directory(target, "zcode-migration")
    root.mkdir(mode=0o700, exist_ok=True)
    # Legacy releases use an exclusive-create lock; never remove their lock.
    if (root / "apply.lock").exists():
        raise MigrationError(
            "Legacy migration lock requires inspection: " + str(root / "apply.lock")
        )
    path = root / "writer.lock"
    if is_link(path):
        raise MigrationError("Linked migration lock")
    if path.exists():
        regular(path)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"0")
        os.lseek(fd, 0, os.SEEK_SET)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise MigrationError("Migration lock is held by another writer") from exc
        yield
    finally:
        # Closing releases OS locks even after an abrupt process exit. Do not unlink
        # the inode: another process may already be waiting on this same file.
        os.close(fd)


def apply(
    source,
    target,
    agent,
    ids=None,
    workspace=None,
    fail_after=None,
    allow_references=False,
    restore_projects=False,
):
    with migration_lock(target):
        return _apply_locked(
            source,
            target,
            agent,
            ids,
            workspace,
            fail_after,
            allow_references,
            restore_projects,
        )


def _apply_locked(
    source,
    target,
    agent,
    ids=None,
    workspace=None,
    fail_after=None,
    allow_references=False,
    restore_projects=False,
    _items=None,
):
    # Files precede the DB commit. A failed/crashed import never publishes partial DB rows.
    # Orphan files are retained with an explicit recovery report, never mistaken for success.
    dialect = adapter()
    lock = safe_directory(target, "zcode-migration")
    lock.mkdir(mode=0o700, exist_ok=True)
    created_dirs = []
    committed = False
    committing = False
    report_file = None
    try:
        rows = plan(source, target, agent, ids, workspace, restore_projects, _items)
        new = [r for r in rows if r["status"] == "new"]
        if not allow_references and any(
            "Attachment reference" in w for r in new for w in r["warnings"]
        ):
            raise MigrationError(
                "Attachments require file-byte support; use --allow-reference-only only after accepting reference-only migration"
            )
        if not new:
            return {"status": "unchanged", "sessions": public_plan(rows)}
        batch = lock / (str(int(time.time() * 1000)) + "-" + uuid.uuid4().hex[:8])
        batch.mkdir(mode=0o700)
        report_file = batch / "report.json"
        report = {
            "format": FORMAT,
            "state": "prepared",
            "source": str(source),
            "target": str(target),
            "sessions": public_plan(rows),
            "createdDirectories": [],
        }
        private_write(report_file, compact(report) + "\n")
        dbfile = target / "v2/sqlite/runtime-state.sqlite"
        with connect(dbfile) as original:
            backup = sqlite3.connect(batch / "runtime-state.before.sqlite")
            try:
                original.backup(backup)
                mode = backup.execute("PRAGMA journal_mode=DELETE").fetchone()[0]
                if mode.lower() != "delete":
                    raise MigrationError(
                        "Could not finalize standalone database backup"
                    )
                if backup.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                    raise MigrationError("Target backup integrity check failed")
            finally:
                backup.close()
        os.chmod(batch / "runtime-state.before.sqlite", 0o600)
        with connect(batch / "runtime-state.before.sqlite") as backup_check:
            if backup_check.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise MigrationError("Target backup integrity check failed")
        with connect(dbfile, True) as db:
            db.execute("BEGIN IMMEDIATE")
            check_target(db, agent)
            checked_projects = set()
            for r in new:
                if db.execute(
                    "SELECT 1 FROM local_runtime_sessions WHERE session_id=?",
                    (r["targetId"],),
                ).fetchone():
                    raise MigrationError("Concurrent target identity conflict")
                directory = safe_directory(
                    target, "v2/sessions/" + r["historyRelativeDir"]
                )
                directory.mkdir(mode=0o700, parents=True, exist_ok=False)
                created_dirs.append(directory)
                provenance = {
                    k: r[k]
                    for k in (
                        "sourceId",
                        "targetId",
                        "fingerprint",
                        "workspace",
                        "sourceCreatedAtMs",
                        "sourceUpdatedAtMs",
                    )
                }
                provenance.update(
                    {
                        "format": FORMAT,
                        "adapterVersion": ADAPTER_VERSION,
                        "sourceType": ACTIVE,
                        "source": str(source),
                        "importedAtMs": int(time.time() * 1000),
                    }
                )
                private_write(directory / dialect["marker"], compact(provenance) + "\n")
                private_write(directory / dialect["archive"], compact(r["item"]) + "\n")
                private_write(
                    directory / "messages.jsonl",
                    "".join(compact(x) + "\n" for x in r["canonical"]),
                )
                private_write(
                    directory / "manifest.json",
                    compact(
                        {
                            "schemaVersion": 1,
                            "sessionId": r["targetId"],
                            "createdAtMs": r["createdAtMs"],
                            "updatedAtMs": r["updatedAtMs"],
                            "source": "local-runtime",
                            "layout": "v2-final-dated-session",
                            "paths": {
                                "sessionDir": str(directory),
                                "messages": str(directory / "messages.jsonl"),
                                "reports": str(directory / "reports"),
                            },
                        }
                    )
                    + "\n",
                )
                extra = {
                    "appMode": "coding",
                    "sessionDataVersion": 4,
                    "sessionOrigin": "local-runtime",
                    "origin": "user",
                }
                session = {
                    "sessionId": r["targetId"],
                    "agentName": agent,
                    "workspaceDir": r["workspace"],
                    "runtime": "pi-agent",
                    "sessionType": "branch",
                    "sessionKind": "conversation",
                    "archived": r["archived"],
                    "visibility": "visible",
                    "title": r["title"],
                    "status": "idle",
                    "createdAtMs": r["createdAtMs"],
                    "updatedAtMs": r["updatedAtMs"],
                    "historyRelativeDir": r["historyRelativeDir"],
                    **extra,
                }
                project = db.execute(
                    "SELECT project_id FROM local_runtime_projects WHERE project_kind='workspace' AND workspace_dir=?",
                    (r["workspace"],),
                ).fetchone()
                if (
                    r["workspace"] not in checked_projects
                    and r["projectState"] is not None
                ):
                    current = db.execute(
                        "SELECT project_id,hidden,extra_data_json,updated_at_ms FROM local_runtime_projects WHERE project_id=?",
                        (r["projectState"]["project_id"],),
                    ).fetchone()
                    if current is None or dict(current) != r["projectState"]:
                        raise MigrationError(
                            "Project changed during migration; preview again"
                        )
                elif r["workspace"] not in checked_projects and project:
                    raise MigrationError(
                        "Project appeared during migration; preview again"
                    )
                if not project:
                    insert(
                        db,
                        "local_runtime_projects",
                        {
                            "project_kind": "workspace",
                            "workspace_dir": r["workspace"],
                            "created_at_ms": r["createdAtMs"],
                            "updated_at_ms": r["updatedAtMs"],
                        },
                    )
                    project = db.execute(
                        "SELECT project_id FROM local_runtime_projects WHERE project_kind='workspace' AND workspace_dir=?",
                        (r["workspace"],),
                    ).fetchone()
                if (
                    r["workspace"] not in checked_projects
                    and r["restoreBoundary"] is not None
                ):
                    project_extra = parse(
                        r["projectState"]["extra_data_json"], "project extra data"
                    )
                    project_extra["sidebarRemoval"] = r["restoreBoundary"]
                    db.execute(
                        "UPDATE local_runtime_projects SET extra_data_json=? WHERE project_id=?",
                        (compact(project_extra), project[0]),
                    )
                checked_projects.add(r["workspace"])
                if restore_projects:
                    db.execute(
                        "UPDATE local_runtime_projects SET hidden=0 WHERE project_id=? AND hidden=1",
                        (project[0],),
                    )
                insert(
                    db,
                    "local_runtime_sessions",
                    {
                        "session_id": r["targetId"],
                        "record_json": compact(session),
                        "updated_at_ms": r["updatedAtMs"],
                        "columnar_version": 3,
                        "agent_name": agent,
                        "runtime": "pi-agent",
                        "session_type": "branch",
                        "status": "idle",
                        "archived": int(r["archived"]),
                        "visibility": "visible",
                        "session_kind": "conversation",
                        "purpose_kind": "",
                        "workspace_dir": r["workspace"],
                        "project_workspace_dir": r["workspace"],
                        "is_default_workspace": 0,
                        "title": r["title"],
                        "created_at_ms": r["createdAtMs"],
                        "extra_data_json": compact(extra),
                        "project_id": project[0],
                        "history_relative_dir": r["historyRelativeDir"],
                    },
                )
                write_search_document(db, r, agent)
                for msg in r["display"]:
                    insert(
                        db,
                        "local_runtime_message_rows",
                        {
                            "session_id": r["targetId"],
                            "msg_id": msg["msg_id"],
                            "role": msg["role"],
                            "turn_id": msg["turnId"],
                            "source": "desktop",
                            "created_at_ms": msg["timestamp"],
                            "data_json": compact(msg),
                        },
                    )
                initialize_history(db, r["targetId"], r["canonical"])
                if fail_after is not None and len(created_dirs) >= fail_after:
                    raise MigrationError("Injected transaction failure")
            committing = True
            db.commit()
            committed = True
        report.update(
            {"state": "committed", "createdDirectories": [str(p) for p in created_dirs]}
        )
        temp = report_file.with_suffix(".complete")
        private_write(temp, compact(report) + "\n")
        os.replace(temp, report_file)
        # Read-back is independent from the write transaction.
        with connect(dbfile) as check:
            for row in new:
                count = check.execute(
                    "SELECT COUNT(*) FROM local_runtime_message_rows WHERE session_id=?",
                    (row["targetId"],),
                ).fetchone()[0]
                if count < row["messageCount"]:
                    raise MigrationError(
                        "Committed import failed message readback; see "
                        + str(report_file)
                    )
                if not check.execute(
                    "SELECT 1 FROM local_runtime_sessions WHERE session_id=?",
                    (row["targetId"],),
                ).fetchone():
                    raise MigrationError("Committed session missing during readback")
                row["status"] = "already-imported"
        verified = rows
        return {
            "status": "imported",
            "imported": len(new),
            "backup": str(batch / "runtime-state.before.sqlite"),
            "report": str(report_file),
            "sessions": public_plan(verified),
        }
    except BaseException as exc:
        if not committed and not committing:
            # Only remove files this invocation just created, never historical/user-owned dirs.
            for directory in reversed(created_dirs):
                for filename in (
                    dialect["marker"],
                    dialect["archive"],
                    "messages.jsonl",
                    "manifest.json",
                ):
                    (directory / filename).unlink(missing_ok=True)
                directory.rmdir()
        if committed:
            raise MigrationError(
                "Import COMMITTED, but final readback/report failed; inspect "
                + str(report_file)
                + "; do not restore the whole DB: "
                + str(exc)
            ) from exc
        if committing:
            raise MigrationError(
                "Commit outcome uncertain; history files preserved. Inspect "
                + str(report_file)
            ) from exc
        raise


def search_terms(value):
    return " ".join(
        "c" + format(ord(char), "x")
        for char in unicodedata.normalize("NFKC", value or "").strip().lower()
    )


def write_search_document(db, row, agent):
    db.execute(
        "INSERT INTO local_runtime_session_fts_keys(session_id) VALUES (?)",
        (row["targetId"],),
    )
    key = db.execute(
        "SELECT fts_rowid FROM local_runtime_session_fts_keys WHERE session_id=?",
        (row["targetId"],),
    ).fetchone()[0]
    values = [
        row["targetId"],
        agent,
        row["title"],
        row["workspace"],
        "",
        "idle",
        "branch",
    ]
    db.execute(
        "INSERT INTO local_runtime_sessions_fts(rowid,session_id,session_id_terms,agent_name_terms,title_terms,workspace_dir_terms,purpose_terms,status_terms,session_type_terms) VALUES (?,?,?,?,?,?,?,?,?)",
        [key, row["targetId"]] + [search_terms(value) for value in values],
    )


# Frozen adapter v1 projection, used only to verify an unchanged old import during repair.
def convert_legacy_v1(item, sid):
    display, canonical, warnings = [], [], []
    turn = "zcode-" + sid
    zero_usage = {
        "input": 0,
        "output": 0,
        "cacheRead": 0,
        "cacheWrite": 0,
        "totalTokens": 0,
        "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0, "total": 0},
    }
    for msg in item["messages"]:
        data = msg["data"]
        role = data.get("role")
        if role not in ("user", "assistant"):
            warnings.append(
                "Non-conversation role retained only in source archive: " + str(role)
            )
            continue
        mid = (
            "msg-zcode-"
            + hashlib.sha256((sid + "\0" + msg["id"]).encode()).hexdigest()[:32]
        )
        if role == "user":
            turn = "zcode-" + msg["id"]
        texts, thoughts = [], []
        for part in msg["parts"]:
            p = part["data"]
            typ = p.get("type")
            if typ == "text":
                if not isinstance(p.get("text"), str):
                    raise MigrationError("Invalid text part: " + part["id"])
                texts.append(p["text"])
            elif typ == "reasoning":
                if isinstance(p.get("text"), str):
                    thoughts.append(p["text"])
            elif typ == "tool":
                state = p.get("state")
                if not isinstance(state, dict):
                    raise MigrationError("Invalid tool state: " + part["id"])
                evidence = {
                    "tool": p.get("tool"),
                    "callID": p.get("callID"),
                    "status": state.get("status"),
                    "input": state.get("input"),
                }
                for key in ("output", "error", "title"):
                    if key in state:
                        evidence[key] = state[key]
                texts.append(
                    "[ZCode 历史工具记录；仅供阅读，不重新执行]\n" + compact(evidence)
                )
            elif typ == "file":
                texts.append("[ZCode 历史附件引用]\n" + compact(p))
                warnings.append(
                    "Attachment reference retained; bytes not copied: " + part["id"]
                )
            elif typ not in ("step-start", "step-finish"):
                texts.append("[ZCode 历史记录 " + str(typ) + "]\n" + compact(p))
        if data.get("error"):
            texts.append("[ZCode 历史错误]\n" + compact(data["error"]))
        text = "\n\n".join(texts)
        if not text:
            # Preserve reasoning-only/errors/empty message identity in display, but never expose
            # foreign hidden reasoning as executable model instructions.
            text = "[ZCode 无正文消息]"
        ts = timestamp(msg["createdAtMs"])
        view = {
            "msg_id": mid,
            "role": role,
            "msg_type": 1,
            "msg_content": text,
            "timestamp": ts,
            "turnId": turn,
            "turn_id": turn,
            "query_key": turn,
            "source": "desktop",
            "canonical_message_id": mid,
        }
        if thoughts:
            view["thinking_content"] = "\n\n".join(thoughts)
        if role == "assistant":
            view["finish_reason"] = "stop"
        display.append(view)
        native = {
            "role": role,
            "content": [{"type": "text", "text": text}],
            "timestamp": ts,
        }
        if role == "assistant":
            native.update(
                {
                    "api": "openai-completions",
                    "provider": "zcode-history",
                    "model": "historical-transcript",
                    "usage": zero_usage,
                    "stopReason": "stop",
                }
            )
        canonical.append({"message_id": mid, "turn_id": turn, "message": native})
    return display, canonical, warnings


def repair(target, agent, sid):
    with migration_lock(target):
        return _repair_locked(target, agent, sid)


def _repair_locked(target, agent, sid):
    """Repair only an unchanged old import; never rewrite or replace user history."""
    if not sid:
        raise MigrationError("Repair requires an explicit --target-session")
    lock = safe_directory(target, "zcode-migration")
    lock.mkdir(mode=0o700, exist_ok=True)
    lockfile = lock / "apply.lock"
    try:
        fd = os.open(lockfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise MigrationError("Migration lock exists: " + str(lockfile))
    os.close(fd)
    try:
        dbfile = target / "v2/sqlite/runtime-state.sqlite"
        # A private online backup precedes any mutation. Revalidate under the write lock.
        batch = lock / (
            "repair-" + str(int(time.time() * 1000)) + "-" + uuid.uuid4().hex[:8]
        )
        batch.mkdir(mode=0o700)
        backup_path = batch / "runtime-state.before.sqlite"
        with connect(dbfile) as original:
            backup = sqlite3.connect(backup_path)
            try:
                original.backup(backup)
                if (
                    backup.execute("PRAGMA journal_mode=DELETE").fetchone()[0].lower()
                    != "delete"
                ):
                    raise MigrationError(
                        "Could not finalize standalone database backup"
                    )
            finally:
                backup.close()
        os.chmod(backup_path, 0o600)
        with connect(backup_path) as backup:
            if backup.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise MigrationError("Backup integrity check failed")
        with connect(dbfile, True) as db:
            db.execute("BEGIN IMMEDIATE")
            check_target(db, agent)
            row = db.execute(
                "SELECT * FROM local_runtime_sessions WHERE session_id=?", (sid,)
            ).fetchone()
            if not row or row["agent_name"] != agent:
                raise MigrationError("Unknown target session or agent mismatch")
            directory = safe_directory(
                target, "v2/sessions/" + row["history_relative_dir"]
            )
            provenance = parse(
                regular(directory / "zcode-migration.json").read_text(encoding="utf-8"),
                "migration provenance",
            )
            archive = parse(
                regular(directory / "zcode-source.json").read_text(encoding="utf-8"),
                "source archive",
            )
            source_session = archive["session"]
            if (
                provenance.get("targetId") != sid
                or provenance.get("sourceId") != source_session["id"]
                or identity(Path(provenance["source"]), source_session["id"]) != sid
                or provenance.get("workspace") != row["workspace_dir"]
                or history_dir(sid, source_session["time_created"])
                != row["history_relative_dir"]
            ):
                raise MigrationError("Migration provenance does not match target")
            fingerprint = archive.pop("fingerprint", None)
            if (
                fingerprint != provenance.get("fingerprint")
                or digest(archive) != fingerprint
            ):
                raise MigrationError("Source archive fingerprint mismatch")
            if db.execute(
                "SELECT 1 FROM local_runtime_pi_history_file_migrations WHERE session_id=?",
                (sid,),
            ).fetchone():
                return {"status": "unchanged", "targetId": sid}
            if row["status"] not in ("idle", "error"):
                raise MigrationError("Repair requires an idle or error session")
            adapter = provenance.get("adapterVersion", 1)
            if adapter not in (1, ADAPTER_VERSION):
                raise MigrationError("Unsupported import adapter version")
            records = (convert_legacy_v1 if adapter == 1 else convert)(archive, sid)[1]
            history = regular(directory / "messages.jsonl")
            observed = [
                parse(line, "canonical history")
                for line in history.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            if observed != records:
                raise MigrationError(
                    "Target history differs from original import; refusing automatic repair"
                )
            initialize_history(db, sid, records)
            db.commit()
        return {
            "status": "repaired",
            "targetId": sid,
            "messageCount": len(records),
            "backup": str(backup_path),
            "historyUnchanged": True,
        }
    finally:
        lockfile.unlink(missing_ok=True)


def print_result(value, file=None):
    # JSON escapes round-trip UTF-8 text even through a legacy GBK PowerShell pipe.
    print(
        json.dumps(value, ensure_ascii=True, separators=(",", ":"), allow_nan=False),
        file=file,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["scan", "plan", "apply", "repair", "prepare-context"]
    )
    parser.add_argument(
        "--source",
        choices=list(SOURCE_ADAPTERS),
        default="zcode",
        help="Source Agent (see choices)",
    )
    parser.add_argument(
        "--source-db",
        help="Source location: ZCode SQLite; Codex data dir; Claude config/projects dir; OpenCode SQLite/data dir; Pi/OMP agent or sessions dir",
    )
    parser.add_argument("--target-data-dir")
    parser.add_argument("--agent", default="mavis")
    parser.add_argument("--session", action="append")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Select every discoverable session from the chosen source",
    )
    parser.add_argument(
        "--report", help="Required plan/apply preview and resumable progress JSON path"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Transaction batch size (1-100, default 20)",
    )
    parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Retry failed/incompatible entries from the same migration report",
    )
    parser.add_argument(
        "--context-summary-dir",
        help="Source-bound context bundles prepared by prepare-context",
    )
    parser.add_argument("--workspace")
    parser.add_argument(
        "--restore-projects",
        action="store_true",
        help="Explicitly restore removed workspace projects; preserve source timestamps in provenance",
    )
    parser.add_argument(
        "--allow-reference-only",
        action="store_true",
        help="Explicitly accept attachment references without copying file bytes",
    )
    parser.add_argument("--target-session", help="Target MiniMax session ID to repair")
    args = parser.parse_args()
    try:
        dialect = use(args.source)
        if args.all and (
            args.session or args.command not in ("plan", "apply", "prepare-context")
        ):
            raise MigrationError(
                "--all is exclusive with --session and only supports prepare-context/plan/apply"
            )
        if args.command in ("plan", "apply"):
            if bool(args.all) == bool(args.session):
                raise MigrationError(
                    "Choose exactly one scope: --all or one/more --session IDs"
                )
            if not args.report:
                raise MigrationError(
                    "plan/apply require --report <preview-and-progress.json>"
                )
        elif args.report or args.retry_failed or args.batch_size != 20:
            raise MigrationError(
                "--report/--retry-failed/--batch-size only support plan/apply"
            )
        if args.retry_failed and args.command != "apply":
            raise MigrationError("--retry-failed requires apply")
        if args.context_summary_dir and (
            args.source != "codex"
            or args.command not in ("prepare-context", "plan", "apply")
        ):
            raise MigrationError(
                "--context-summary-dir requires Codex prepare-context/plan/apply"
            )
        if args.command == "prepare-context":
            if (
                not dialect["prepare_context"]
                or not args.context_summary_dir
                or bool(args.all) == bool(args.session)
            ):
                raise MigrationError(
                    "prepare-context requires Codex, --context-summary-dir and exactly one selection scope"
                )
            result = dialect["prepare_context"](
                dialect["source_path"](args.source_db),
                None if args.all else args.session,
                args.context_summary_dir,
            )
            print_result(result)
            return (
                2
                if any(r["status"] == "incompatible" for r in result["sessions"])
                or result["discoveryErrors"]
                else 0
            )
        if args.command == "repair":
            # Repair reconstructs a frozen v1 ZCode projection; no other source has
            # legacy imports to repair.
            if not dialect["repairable"]:
                raise MigrationError(
                    "Repair only applies to ZCode imports: " + args.source
                )
            print_result(
                repair(
                    target_path(args.target_data_dir), args.agent, args.target_session
                )
            )
            return 0
        source = dialect["source_path"](args.source_db)
        if args.command == "scan":
            result = {
                "source": str(source),
                "sessions": dialect["overview"](source, args.session),
            }
            if args.source == "zcode":
                result["excludedSessions"] = dialect["inventory"](source).get(
                    "excluded", []
                )
        else:
            import importlib.util
            import types

            spec = importlib.util.spec_from_file_location(
                "migration_job", Path(__file__).with_name("migration_job.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            current = types.ModuleType("migrate")
            current.__dict__.update(globals())
            result = module.execute(
                current, args, source, target_path(args.target_data_dir)
            )
            result["sourceType"] = args.source
            print_result(result)
            return 0 if result["status"] != "completed-with-errors" else 2
        result["sourceType"] = args.source
        print_result(result)
    except (MigrationError, sqlite3.Error, OSError, ValueError) as exc:
        print_result({"error": str(exc), "type": type(exc).__name__}, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    import signal

    def interrupted(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, interrupted)
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_result(
            {
                "status": "interrupted",
                "resume": "Repeat apply with the same --report, source, selection and preview options",
            },
            file=sys.stderr,
        )
        sys.exit(130)
