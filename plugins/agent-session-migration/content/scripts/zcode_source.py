"""ZCode source adapter: SQLite discovery, parsing and native history semantics."""

from pathlib import Path

from migrate import (
    MigrationError,
    connect,
    digest,
    parse,
    regular,
    schema,
    source_parts,
    timestamp,
)

SOURCE_COLUMNS = {
    "session": {"id", "directory", "title", "time_created", "time_updated"},
    "message": {"id", "session_id", "time_created", "data", "sequence"},
    "part": {"id", "message_id", "session_id", "time_created", "data", "sequence"},
}


# ZCode Jfe/isTaskListSessionType: parent_id also appears on user-created forks.
TASK_LIST_TYPES = frozenset({"interactive", "fork", "workflow_parent"})
INTERNAL_TYPES = frozenset(
    {"subagent_child", "workflow_child", "nested_workflow_child", "selection_side_chat"}
)


def task_list_session(session):
    kind = session.get("task_type") or "interactive"
    if not isinstance(kind, str) or kind not in TASK_LIST_TYPES | INTERNAL_TYPES:
        raise MigrationError("Unknown ZCode session task_type: " + str(kind))
    return kind in TASK_LIST_TYPES


def source_path(value=None):
    return regular(value or Path.home() / ".zcode/cli/db/db.sqlite")


def inventory(path):
    path = source_path(path)
    desktop = {}
    errors = []
    index = path.parent.parent.parent / "v2/tasks-index.sqlite"
    if index.is_file():
        with connect(index) as catalog:
            schema(catalog, {"tasks": {"task_id", "title", "archived", "deleted"}})
            for row in catalog.execute(
                "SELECT task_id,title,archived,deleted FROM tasks"
            ):
                sid = row["task_id"]
                if sid in desktop:
                    errors.append(
                        {
                            "sourceId": sid,
                            "error": "Ambiguous Desktop task identity: " + str(sid),
                        }
                    )
                desktop[sid] = dict(row)
    sessions = {}
    with connect(path) as db:
        schema(db, SOURCE_COLUMNS)
        for row in db.execute("SELECT * FROM session ORDER BY time_created,id"):
            sid = row["id"]
            if not isinstance(sid, str) or not sid:
                errors.append({"error": "Invalid ZCode session identity"})
                continue
            if sid in sessions:
                errors.append(
                    {
                        "sourceId": sid,
                        "error": "Ambiguous ZCode session identity: " + sid,
                    }
                )
            sessions[sid] = dict(row)
    excluded = []
    for sid, session in sessions.items():
        try:
            if not task_list_session(session):
                excluded.append(
                    {
                        "sourceId": sid,
                        "taskType": session["task_type"],
                        "parentId": session.get("parent_id"),
                        "reason": "not a top-level ZCode conversation",
                    }
                )
        except MigrationError as exc:
            errors.append({"sourceId": sid, "error": str(exc)})
    blocked = {error.get("sourceId") for error in errors} | {
        row["sourceId"] for row in excluded
    }
    ids = [
        sid
        for sid in sessions
        if sid not in blocked and not desktop.get(sid, {}).get("deleted")
    ]
    return {
        "ids": ids,
        "excluded": excluded,
        "source": path,
        "sessions": sessions,
        "desktop": desktop,
        "errors": errors,
        "bytes": path.stat().st_size,
    }


def load_inventory(data, ids, context_dir=None):
    if context_dir:
        raise MigrationError("Context reconstruction is only supported for Codex")
    result = []
    errors = {error.get("sourceId"): error["error"] for error in data["errors"]}
    with connect(data["source"]) as db:
        schema(db, SOURCE_COLUMNS)
        for sid in ids:
            if sid in errors:
                raise MigrationError(errors[sid])
            task = data["desktop"].get(sid)
            if task and task["deleted"]:
                raise MigrationError(
                    "Requested source session is deleted in ZCode Desktop: " + sid
                )
            rows = db.execute("SELECT * FROM session WHERE id=?", (sid,)).fetchall()
            if len(rows) != 1:
                raise MigrationError("Unknown or ambiguous source session ID: " + sid)
            session = rows[0]
            if not task_list_session(dict(session)):
                raise MigrationError(
                    "Requested source is not a top-level ZCode conversation: "
                    + sid
                    + " ("
                    + str(session["task_type"])
                    + ")"
                )
            messages = []
            for message in db.execute(
                "SELECT * FROM message WHERE session_id=? ORDER BY COALESCE(sequence,time_created),time_created,id",
                (sid,),
            ):
                parts = []
                for part in db.execute(
                    "SELECT * FROM part WHERE session_id=? AND message_id=? ORDER BY COALESCE(sequence,time_created),time_created,id",
                    (sid, message["id"]),
                ):
                    parts.append(
                        {
                            "id": part["id"],
                            "data": parse(part["data"], part["id"]),
                            "createdAtMs": timestamp(part["time_created"]),
                        }
                    )
                messages.append(
                    {
                        "id": message["id"],
                        "data": parse(message["data"], message["id"]),
                        "createdAtMs": timestamp(message["time_created"]),
                        "parts": parts,
                    }
                )
            item = {"session": dict(session), "messages": messages, "desktop": task}
            # Preserve the historical fingerprint byte-for-byte: derived history
            # selections must not change provenance for existing imports.
            item["fingerprint"] = digest(item)
            result.append(item)
    return result


def load_source(path, ids=None):
    data = inventory(path)
    if not ids and data["errors"]:
        raise MigrationError(data["errors"][0]["error"])
    if ids and not set(ids) <= set(data["sessions"]):
        raise MigrationError(
            "Unknown source session IDs: "
            + ", ".join(sorted(set(ids) - set(data["sessions"])))
        )
    return load_inventory(data, ids or data["ids"])


def overview(path, ids=None):
    data = inventory(path)
    if data["errors"]:
        raise MigrationError(data["errors"][0]["error"])
    if ids and not set(ids) <= set(data["ids"]):
        raise MigrationError("Unknown/deleted source session IDs")
    rows = []
    for sid in ids or data["ids"]:
        session = data["sessions"][sid]
        task = data["desktop"].get(sid) or {}
        rows.append(
            {
                "id": sid,
                "title": task.get("title") or session["title"],
                "workspace": session["directory"],
                "workspaceExists": Path(session["directory"]).is_dir(),
                "updatedAt": session["time_updated"],
                "archived": bool(
                    task["archived"] if task else session.get("time_archived")
                ),
            }
        )
    return rows


def rewind_messages(messages, revert):
    # Port of ZCode d0/apply rewind selection (21613a05, zcode.cjs:26446).
    if not revert:
        return list(messages)
    positions = {msg["id"]: i for i, msg in enumerate(messages)}
    target = positions.get(revert["targetMessageID"], -1)
    kept = revert.get("keptMessageIDs")
    if kept is not None:
        by_id = {msg["id"]: msg for msg in messages}
        prefix = [by_id[mid] for mid in kept if mid in by_id]
    else:
        prefix = messages[:target] if target >= 0 else list(messages)
    cut = revert.get("branchCutAfterMessageID")
    if cut:
        index = positions.get(cut, -1)
        return prefix + messages[index + 1 :] if index >= 0 else prefix
    created = revert.get("createdMessageID")
    if kept is not None or target >= 0:
        index = positions.get(created, -1)
        return prefix + messages[index:] if index >= 0 else prefix
    return list(messages)


def is_compaction(part):
    return part.get("type") == "compaction" and (
        bool(part.get("compactBoundary")) or not part.get("timelineStatus")
    )


def compact_messages(messages):
    # Port of Dp/klt/zzo/Slt: preserve the selected segment at its summary anchor.
    boundaries = [
        i
        for i, msg in enumerate(messages)
        if any(is_compaction(p) for p in source_parts(msg))
    ]
    if not boundaries:
        return list(messages), -1
    index = boundaries[-1]
    boundary = next(
        (
            p["compactBoundary"]
            for p in source_parts(messages[index])
            if p.get("compactBoundary")
        ),
        {},
    )
    segment = boundary.get("preservedSegment")
    tail = list(messages[index:])
    if not segment:
        return tail, index
    positions = {msg["id"]: i for i, msg in enumerate(messages)}
    head = positions.get(segment["headMessageId"], -1)
    end = positions.get(segment["tailMessageId"], -1)
    if head < 0 or end < head or end >= index:
        raise MigrationError("Unsupported compaction preserved segment ordering")
    preserved = []
    for msg in messages[head : end + 1]:
        data = msg["data"]
        if any(p.get("type") == "compaction" for p in source_parts(msg)):
            continue
        if data.get("role") == "user" and (
            data.get("synthetic") is True
            or data.get("visibility") == "model-only"
            or data.get("source")
        ):
            continue
        if data.get("role") == "assistant" and data.get("error"):
            continue
        if data.get("role") in ("user", "assistant"):
            preserved.append(msg)
    anchor = next(
        (i for i, msg in enumerate(tail) if msg["id"] == segment["anchorMessageId"]), -1
    )
    offset = anchor + 1 if anchor >= 0 else 1
    return tail[:offset] + preserved + tail[offset:], index


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

    raw = item["session"].get("revert")
    revert = parse(raw, "session.revert") if isinstance(raw, str) else raw
    if revert is not None and not isinstance(revert, dict):
        raise MigrationError("Unsupported source rewind contract")
    if revert:
        if not isinstance(revert, dict) or not revert.get("targetMessageID"):
            raise MigrationError(
                "Unsupported source rewind contract; original history was not imported"
            )
        for key in ("targetMessageID", "createdMessageID", "branchCutAfterMessageID"):
            if key in revert:
                reference(revert[key])
        if "keptMessageIDs" in revert:
            kept = revert["keptMessageIDs"]
            if (
                not isinstance(kept, list)
                or any(not isinstance(x, str) for x in kept)
                or len(kept) != len(set(kept))
            ):
                raise MigrationError("Invalid rewind kept message identities")
            for mid in kept:
                reference(mid)
    for msg in messages:
        for part in source_parts(msg):
            if part.get("type") != "compaction":
                continue
            for key in ("summaryMessageId", "tail_start_id"):
                if part.get(key):
                    reference(part[key])
            boundary = part.get("compactBoundary")
            if boundary is not None:
                if not isinstance(boundary, dict):
                    raise MigrationError("Unsupported compaction boundary")
                for key in (
                    "summaryMessageIds",
                    "attachmentMessageIds",
                    "hookResultMessageIds",
                ):
                    values = boundary.get(key, [])
                    if not isinstance(values, list):
                        raise MigrationError("Invalid compaction message identities")
                    for value in values:
                        reference(value)
                if boundary.get("lastSummarizedMessageId"):
                    reference(boundary["lastSummarizedMessageId"])
                segment = boundary.get("preservedSegment")
                if segment is not None:
                    if not isinstance(segment, dict):
                        raise MigrationError("Invalid compaction preserved segment")
                    for key in ("headMessageId", "tailMessageId", "anchorMessageId"):
                        reference(segment.get(key))
    display = rewind_messages(messages, revert)
    if revert and revert.get("branchCutAfterMessageID"):
        active, _ = compact_messages(display)
    else:
        active, boundary_index = compact_messages(messages)
        kept = (revert or {}).get("keptMessageIDs")
        if (
            kept is None
            or boundary_index < 0
            or any(
                mid in {msg["id"] for msg in messages[boundary_index:]} for mid in kept
            )
        ):
            active = rewind_messages(active, revert)
    if len({msg["id"] for msg in active}) != len(active) or len(
        {msg["id"] for msg in display}
    ) != len(display):
        raise MigrationError("Ambiguous source rewind/compaction history")
    return display, active


ADAPTER = {
    "prepare_context": None,
    "display_user_text": lambda text: text,
    "load_source": load_source,
    "inventory": inventory,
    "load_inventory": load_inventory,
    "select_histories": select_histories,
    "source_path": source_path,
    "overview": overview,
    "repairable": True,
    "label": "ZCode",
    "marker": "zcode-migration.json",
    "archive": "zcode-source.json",
    "id_prefix": "msg-zcode-",
    "turn_prefix": "zcode-",
    "provider": "zcode-history",
    "display_kind": "zcode_history_archive",
}
