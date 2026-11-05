"""OpenCode legacy SQLite reader; semantics from upstream v1.18.32.

Reads session/message/part, never lifecycle session_message as conversation.
No source schema upgrades, paths, credentials or provider metadata are consumed.
"""

from migrate import MigrationError, compact, digest, parse, schema

COLUMNS = {
    "session": {
        "id",
        "directory",
        "title",
        "version",
        "time_created",
        "time_updated",
        "parent_id",
        "revert",
        "time_archived",
    },
    "message": {"id", "session_id", "time_created", "data"},
    "part": {"id", "message_id", "session_id", "data"},
}


def check(db):
    schema(db, COLUMNS)


def payload(row, links):
    value = parse(row["data"], row["id"])
    if not isinstance(value, dict):
        raise MigrationError("Invalid OpenCode legacy JSON object")
    for key, expected in {"id": row["id"], **links}.items():
        if value.get(key, expected) != expected:
            raise MigrationError("OpenCode legacy identity mismatch: " + row["id"])
    return value


def load(db, session, v2):
    sid = session["id"]
    if not isinstance(session["version"], str) or not session["version"].startswith(
        "1."
    ):
        raise MigrationError("Unsupported OpenCode legacy version; 1.x SQLite required")
    # A lifecycle-only table is normal in 1.18; unknown projection traffic is not.
    tables = {
        r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    if "session_message" in tables:
        schema(db, {"session_message": {"session_id", "type"}})
        kinds = {
            r[0]
            for r in db.execute(
                "SELECT DISTINCT type FROM session_message WHERE session_id=?", (sid,)
            )
        }
        if kinds - v2.IGNORED:
            raise MigrationError(
                "OpenCode legacy database contains mixed conversation projections"
            )
    raw = db.execute(
        "SELECT * FROM message WHERE session_id=? ORDER BY time_created,id", (sid,)
    ).fetchall()
    infos, allparts = {}, {}
    for row in raw:
        uid = row["id"]
        if not isinstance(uid, str) or not uid or uid in infos:
            raise MigrationError("Duplicate/invalid OpenCode legacy message ID")
        infos[uid] = payload(row, {"sessionID": sid})
        allparts[uid] = []
    # Include mismatched session links rather than silently losing those parts.
    partrows = db.execute(
        "SELECT * FROM part WHERE session_id=? OR message_id IN (SELECT id FROM message WHERE session_id=?) ORDER BY id",
        (sid, sid),
    ).fetchall()
    seen = set()
    for row in partrows:
        if (
            row["session_id"] != sid
            or row["message_id"] not in infos
            or row["id"] in seen
        ):
            raise MigrationError("Orphan/duplicate OpenCode legacy part")
        seen.add(row["id"])
        allparts[row["message_id"]].append(
            payload(row, {"sessionID": sid, "messageID": row["message_id"]})
        )
    ids = list(infos)
    positions = {uid: i for i, uid in enumerate(ids)}
    markers, successful, mapped, warnings = {}, {}, [], []
    for seq, row in enumerate(raw):
        uid = row["id"]
        info, parts = infos[uid], allparts[uid]
        role = info.get("role")
        if role not in ("user", "assistant"):
            raise MigrationError("Unsupported OpenCode legacy role")
        parent = info.get("parentID")
        if role == "assistant" and (
            parent not in infos
            or positions[parent] >= seq
            or infos[parent].get("role") != "user"
        ):
            raise MigrationError("Broken OpenCode legacy assistant parent")
        content, files, texts = [], [], []
        synthetic = False
        for part in parts:
            typ = part.get("type")
            if typ == "compaction":
                if role != "user" or uid in markers:
                    raise MigrationError("Invalid OpenCode legacy compaction marker")
                markers[uid] = part
            elif typ in ("text", "reasoning"):
                if not part.get("ignored"):
                    text = v2.string(part.get("text"), "legacy text")
                    if role == "assistant":
                        content.append({"type": typ, "text": text})
                    elif typ == "text":
                        texts.append(text)
                        synthetic = synthetic or bool(part.get("synthetic"))
            elif typ == "file":
                files.append(file_ref(part, v2))
            elif typ == "tool" and role == "assistant":
                state = v2.obj(part.get("state"), "legacy tool state")
                status = state.get("status")
                if status not in ("pending", "running", "completed", "error"):
                    raise MigrationError("Unsupported OpenCode legacy tool status")
                pruned = v2.obj(state.get("time", {}), "legacy tool time").get(
                    "compacted"
                )
                output = (
                    "[OpenCode 历史工具输出已压缩]"
                    if pruned
                    else v2.string(state.get("output", ""), "legacy tool output")
                )
                if pruned:
                    warnings.append("OpenCode tool output was pruned in the source")
                content.append(
                    {
                        "type": "tool",
                        "name": v2.string(part.get("tool"), "legacy tool name"),
                        "id": v2.string(part.get("callID"), "legacy call ID"),
                        "state": {
                            "status": "streaming" if status == "pending" else status,
                            "input": state.get("input"),
                            "content": [{"type": "text", "text": output}],
                            "error": state.get("error"),
                            "metadata": {
                                "truncated": bool(
                                    v2.obj(
                                        state.get("metadata", {}), "legacy metadata"
                                    ).get("truncated")
                                )
                            },
                            "attachments": []
                            if pruned
                            else [
                                file_ref(p, v2) for p in state.get("attachments", [])
                            ],
                        },
                    }
                )
            elif typ == "subtask" and role == "user":
                texts.append(
                    "[OpenCode 历史子任务；仅供参考]\n"
                    + v2.string(part.get("prompt"), "subtask prompt")
                )
                synthetic = True
            elif typ in (
                "step-start",
                "step-finish",
                "snapshot",
                "patch",
                "agent",
                "retry",
            ):
                continue
            else:
                raise MigrationError("Unsupported OpenCode legacy part: " + str(typ))
        typ = role
        if role == "user":
            if uid in markers:
                if texts or files:
                    raise MigrationError(
                        "Mixed OpenCode compaction request and user content"
                    )
                continue
            data = {"text": "\n".join(texts), "files": files}
            if synthetic:
                # Keep text+attachments via user mapping; label generated context explicitly.
                data["text"] = "[OpenCode 历史合成上下文；仅供参考]\n" + data["text"]
        else:
            if files:
                content.extend(
                    {"type": "text", "text": t} for t in v2.attachments(files, warnings)
                )
            data = {
                "time": info.get("time"),
                "content": content,
                "error": info.get("error"),
            }
            if info.get("summary"):
                if parent not in markers:
                    raise MigrationError("OpenCode summary lacks compaction request")
                if info.get("finish") and not info.get("error"):
                    summary = "\n".join(
                        p["text"] for p in content if p["type"] == "text"
                    )
                    if any(p["type"] == "tool" for p in content):
                        raise MigrationError("Unsupported tools in OpenCode summary")
                    if not v2.obj(info.get("time"), "summary time").get("completed"):
                        raise MigrationError("OpenCode legacy summary is incomplete")
                    successful[parent] = uid
                    typ, data = (
                        "compaction",
                        {"status": "completed", "summary": summary, "recent": ""},
                    )
                elif info.get("error"):
                    warnings.append(
                        "OpenCode failed compaction retained; earlier context preserved"
                    )
                else:
                    raise MigrationError("OpenCode legacy compaction is incomplete")
        mapped.append(
            {
                "id": uid,
                "type": typ,
                "seq": seq,
                "time_created": row["time_created"],
                "data": compact(data),
            }
        )
    for marker in markers:
        if not any(
            i.get("parentID") == marker and i.get("summary") for i in infos.values()
        ):
            raise MigrationError("OpenCode legacy compaction has no result")
    # Existing V2 conversion validates every mapped content block, but identity/version
    # stay those of the source in the final normalized fingerprint.
    adapted = {
        **session,
        "version": "2.0.10",
        "time_compacting": session.get("time_compacting"),
    }
    item = v2.normalize(adapted, mapped)
    active = ids[:]
    if successful:
        marker = max(successful, key=positions.get)
        summary = successful[marker]
        start, end = positions[marker], positions[summary]
        tail = markers[marker].get("tail_start_id")
        if tail is not None and (tail not in positions or positions[tail] >= start):
            raise MigrationError("Invalid OpenCode compaction retained-tail boundary")
        active = (
            ids[start : end + 1]
            + (ids[positions[tail] : start] if tail else [])
            + ids[end + 1 :]
        )
    available = {m["id"] for m in item["messages"]}
    item["histories"]["active"] = [uid for uid in active if uid in available]
    item["warnings"] = sorted(set(item["warnings"] + warnings))
    item["sourceFormat"] = "opencode-legacy-sqlite"
    item["sourceVersion"] = session["version"]
    item.pop("fingerprint")
    item["fingerprint"] = digest(item)
    return item


def file_ref(part, v2):
    p = v2.obj(part, "legacy attachment")
    mime = v2.string(p.get("mime"), "legacy MIME")
    url = v2.string(p.get("url"), "legacy attachment URL")
    value = {"mime": mime, "name": p.get("filename") or "attachment"}
    prefix = "data:" + mime + ";base64,"
    if url.startswith(prefix):
        value["data"] = url[len(prefix) :]
    return value
