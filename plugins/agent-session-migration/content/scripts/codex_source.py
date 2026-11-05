#!/usr/bin/env python3
"""Codex source reader for agent-session-migration. Python 3.9+.

Source layout (Codex CLI / Codex Desktop):
  <root>/sessions/YYYY/MM/DD/rollout-<iso>-<uuid>.jsonl        one file per session
  <root>/sessions/YYYY/MM/DD/rollout-<iso>-<uuid>_<uuid>.jsonl forked/compacted thread
  <root>/session_index.jsonl                                   {id, thread_name, updated_at}

This module only reads and normalizes. It emits the same item shape the ZCode reader
emits, so `migrate.convert` classifies Codex records through the shared `projection`
policy instead of carrying a second transcript implementation:

  real user input      -> plain user message            -> "user"
  assistant reply      -> plain assistant message       -> "assistant"
  host scaffolding     -> synthetic user message        -> "hidden"  (source archive only)
  sub-agent traffic    -> source="subagent_message"     -> "context" (labeled, not UI)
  reasoning / tools    -> reasoning and tool parts on the following assistant message

Conversation comes from response_item records, never duplicate UI mirror events.
Readable compacted.replacement_history defines the active model context separately.
Unreadable checkpoints, rollback events, malformed JSON and ambiguous identities fail
before target writes. Non-text payload loss remains explicitly reported.
"""

import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from migrate import MigrationError, connect, digest, is_link

# Filename UUIDs may identify a window rather than the thread. session_meta and
# the optional SQLite catalog own identity; names are only a legacy fallback.
UUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
ROLLOUT_RE = re.compile(r"^rollout-.*?-(?:%s_)?(%s)\.jsonl$" % (UUID, UUID))
TEXT_ITEM_TYPES = {"input_text", "output_text", "text", "summary_text"}
HOST_TAGS = (
    "environment_context",
    "app-context",
    "recommended_plugins",
    "skill",
    "skills_instructions",
    "user_instructions",
    "permissions",
    "collaboration_mode",
)
HOST_BLOCK = re.compile(
    r"^\s*<(?P<tag>" + "|".join(HOST_TAGS) + r")(?:\s[^>]*)?>.*?</(?P=tag)>\s*",
    re.DOTALL,
)
SUMMARY_PREFIX = (
    "Another language model began solving this problem",
    "Another language model started to solve this problem",
)

# Fernet-style payloads appear inside tool arguments (for example spawn_agent messages).
# They are opaque to the user and to any future model, so they are stripped, not migrated.
SECRET_RE = re.compile(r"gAAAAAB[A-Za-z0-9_\-]{64,}")
SECRET_MASK = "[encrypted payload removed]"

MAX_TEXT = 1024 * 1024  # per-field guard; longer values are truncated with a marker


def scrub(text):
    if not isinstance(text, str):
        return text
    text = SECRET_RE.sub(SECRET_MASK, text)
    if len(text) > MAX_TEXT:
        text = text[:MAX_TEXT] + "\n[truncated by migration]"
    return text


def ms(value, fallback=0):
    """ISO-8601 or epoch -> unix milliseconds. Degrades to fallback, never raises."""
    if isinstance(value, bool):
        return fallback
    if isinstance(value, (int, float)):
        number = int(value)
        return number if number > 10_000_000_000 else number * 1000
    if not isinstance(value, str) or not value:
        return fallback
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return fallback
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def texts_of(content):
    """Extract plaintext items only. Encrypted blobs and images are dropped and counted."""
    if isinstance(content, str):
        return [content], 0
    out, dropped = [], 0
    for item in content or []:
        if (
            isinstance(item, dict)
            and item.get("type") in TEXT_ITEM_TYPES
            and isinstance(item.get("text"), str)
        ):
            out.append(item["text"])
        else:
            dropped += 1
    return out, dropped


def user_text(text):
    """Remove only recognized host blocks, never arbitrary XML or attachment requests."""
    rest = text or ""
    while True:
        match = HOST_BLOCK.match(rest)
        if not match:
            break
        rest = rest[match.end() :]
    # Codex packages AGENTS.md with environment context as one user record.
    # It is host context only when the whole structured envelope is present.
    if rest.lstrip().startswith("# AGENTS.md instructions for "):
        match = re.match(
            r"^\s*# AGENTS\.md instructions for [^\n]+\n+<INSTRUCTIONS>.*?</INSTRUCTIONS>\s*",
            rest,
            re.DOTALL,
        )
        if match:
            return user_text(rest[match.end() :])
    return rest


def is_injected(text):
    return bool((text or "").strip()) and not user_text(text).strip()


def source_path(value=None):
    """The Codex source is a data directory, not a single database file."""
    root = Path(value or Path.home() / ".codex").expanduser().absolute()
    if is_link(root) or not root.is_dir():
        raise MigrationError(
            "Codex data dir must be an existing non-symlink directory: " + str(root)
        )
    root = root.resolve()
    if not any((root / name).is_dir() for name in ("sessions", "archived_sessions")):
        raise MigrationError(
            "No sessions/ directory under Codex data dir: " + str(root)
        )
    return root


def header(path):
    with path.open(encoding="utf-8") as handle:
        first = handle.readline(16 * 1024 * 1024)
    try:
        row = json.loads(first)
    except ValueError:
        return {}
    if isinstance(row, dict) and row.get("type") == "session_meta":
        payload = row.get("payload")
        return payload if isinstance(payload, dict) else {}
    return {}


def catalog(root):
    """Read metadata only; never open config/auth or mutate Codex SQLite."""
    paths = [
        p
        for p in root.glob("state_*.sqlite")
        if re.fullmatch(r"state_\d+\.sqlite", p.name) and not is_link(p)
    ]
    if not paths:
        return {}
    path = max(paths, key=lambda p: int(p.stem.split("_")[1]))
    with connect(path) as db:
        columns = {r["name"] for r in db.execute("PRAGMA table_info(threads)")}
        if not {"id", "rollout_path"} <= columns:
            raise MigrationError("Unsupported Codex threads catalog")
        selected = [
            c
            for c in (
                "id",
                "rollout_path",
                "title",
                "cwd",
                "archived",
                "created_at_ms",
                "updated_at_ms",
                "created_at",
                "updated_at",
            )
            if c in columns
        ]
        return {
            r["id"]: dict(r)
            for r in db.execute("SELECT " + ",".join(selected) + " FROM threads")
        }


def rollouts(root, ids=None, metadata=None, errors=None):
    """Resolve stable thread IDs, including archives; refuse ambiguous duplicates."""
    metadata = catalog(root) if metadata is None else metadata
    wanted, candidates = set(ids or []), {}
    by_path = {
        str(Path(row["rollout_path"]).resolve()): sid
        for sid, row in metadata.items()
        if row.get("rollout_path")
    }
    for folder in ("sessions", "archived_sessions"):
        base = root / folder
        if is_link(base):
            raise MigrationError("Linked Codex history directory: " + str(base))
        for path in base.rglob("rollout-*.jsonl"):
            if any(
                is_link(p)
                for p in (path, *path.parents)
                if p != root and root in p.parents
            ):
                if errors is not None:
                    errors.append(
                        {"path": str(path), "error": "Linked Codex rollout skipped"}
                    )
                continue
            if root not in path.resolve().parents:
                raise MigrationError("Codex rollout escapes data directory")
            try:
                meta = header(path)
            except (MigrationError, OSError, ValueError) as exc:
                if errors is None:
                    raise
                errors.append({"path": str(path), "error": str(exc)})
                continue
            sid = meta.get("id") or meta.get("session_id")
            if sid is not None and not isinstance(sid, str):
                error = "Invalid Codex session identity: " + str(path)
                if errors is None:
                    raise MigrationError(error)
                errors.append({"path": str(path), "error": error})
                continue
            indexed = by_path.get(str(path.resolve()))
            if indexed and sid and indexed != sid:
                error = "Codex catalog/session_meta identity mismatch: " + str(path)
                if errors is None:
                    raise MigrationError(error)
                errors.append({"sourceId": indexed, "path": str(path), "error": error})
                errors.append({"sourceId": sid, "path": str(path), "error": error})
                continue
            match = ROLLOUT_RE.match(path.name)
            sid = indexed or sid or (match.group(1) if match else None)
            if not isinstance(sid, str) or not sid:
                if errors is not None:
                    errors.append(
                        {"path": str(path), "error": "Missing Codex session identity"}
                    )
                continue
            if wanted and sid not in wanted:
                continue
            candidates.setdefault(sid, []).append(path)
    found = {}
    for sid, paths in candidates.items():
        canonical = metadata.get(sid, {}).get("rollout_path")
        selected = [
            p for p in paths if canonical and p.resolve() == Path(canonical).resolve()
        ]
        if len(selected) == 1:
            found[sid] = selected[0]
        elif len(paths) == 1:
            found[sid] = paths[0]
        else:
            if errors is None:
                raise MigrationError("Ambiguous Codex rollout identity: " + sid)
            errors.append(
                {"sourceId": sid, "error": "Ambiguous Codex rollout identity: " + sid}
            )
    if wanted - set(found):
        raise MigrationError(
            "Unknown Codex session IDs: " + ", ".join(sorted(wanted - set(found)))
        )
    return found


def titles(root):
    """session_index.jsonl owns user-visible thread names. Append-only, best effort."""
    index = {}
    path = root / "session_index.jsonl"
    if not path.is_file() or path.is_symlink():
        return index
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                index[row["id"]] = row
    return index


def read_rollout(path, rebuild=False, raw=None):
    """Keep display transcript separate from the latest readable context checkpoint.

    Codex core session/rollout_reconstruction.rs replaces model history with
    replacement_history, then replays its suffix. Opaque checkpoints require
    explicit source-bound reconstruction; unsupported rollbacks still fail.
    """
    meta, records, active, warnings = {}, [], [], []
    compacted = False
    encrypted_checkpoints = 0
    with (
        io.StringIO(raw.decode("utf-8"))
        if raw is not None
        else path.open(encoding="utf-8")
    ) as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError as exc:
                raise MigrationError(
                    "Unparseable Codex rollout record at line %d" % number
                ) from exc
            if not isinstance(row, dict):
                raise MigrationError("Invalid Codex rollout record")
            kind, payload = row.get("type"), row.get("payload")
            if kind == "session_meta" and not meta:
                meta = dict(payload) if isinstance(payload, dict) else {}
                meta.pop("base_instructions", None)
                meta["_ts"] = ms(row.get("timestamp"))
            elif kind == "response_item" and isinstance(payload, dict):
                entry = dict(payload)
                entry["id"] = "line-%d" % number
                pair = (ms(row.get("timestamp")), entry)
                records.append(pair)
                active.append(pair)
            elif kind == "compacted":
                if not isinstance(payload, dict) or not isinstance(
                    payload.get("replacement_history"), list
                ):
                    raise MigrationError(
                        "Codex compaction lacks replacement_history; safe continuation unavailable"
                    )
                replacement = payload["replacement_history"]
                readable_types = {
                    "message",
                    "reasoning",
                    "function_call",
                    "custom_tool_call",
                    "function_call_output",
                    "custom_tool_call_output",
                    "agent_message",
                }
                opaque = [
                    x
                    for x in replacement
                    if isinstance(x, dict)
                    and x.get("type") == "compaction"
                    and isinstance(x.get("encrypted_content"), str)
                    and x["encrypted_content"]
                ]
                if any(
                    not isinstance(x, dict)
                    or (x.get("type") not in readable_types and x not in opaque)
                    for x in replacement
                ):
                    raise MigrationError(
                        "Codex unsupported compaction record; reconstruction is unsafe"
                    )
                if opaque:
                    if not rebuild:
                        raise MigrationError(
                            "Codex encrypted/unsupported compaction cannot be migrated as readable context; run prepare-context and provide --context-summary-dir"
                        )
                    if not any(
                        x.get("type") == "message"
                        and x.get("role") == "assistant"
                        and any(t.strip() for t in texts_of(x.get("content"))[0])
                        for _, x in records
                    ):
                        raise MigrationError(
                            "Codex encrypted compaction lacks prior readable assistant history"
                        )
                    encrypted_checkpoints += 1
                    continue
                active = []
                for index, original in enumerate(replacement):
                    entry = dict(original)
                    entry["id"] = "checkpoint-%d-%d" % (number, index)
                    text = "\n\n".join(texts_of(entry.get("content"))[0])
                    if text and (
                        text == payload.get("message")
                        or text.startswith(SUMMARY_PREFIX)
                    ):
                        entry["migration_summary"] = True
                    active.append((ms(row.get("timestamp")), entry))
                compacted = True
            elif (
                kind == "event_msg"
                and isinstance(payload, dict)
                and payload.get("type") == "thread_rolled_back"
            ):
                raise MigrationError(
                    "Codex rollback requires branch reconstruction; refusing to resurrect discarded history"
                )
    messages, folded_warnings = fold(records)
    warnings.extend(folded_warnings)
    if encrypted_checkpoints:
        meta["_rebuild"] = encrypted_checkpoints
        warnings.append(
            "Codex encrypted compaction requires source-bound reconstructed context; not lossless decryption"
        )
    if compacted and not encrypted_checkpoints:
        current, current_warnings = fold(active)
        warnings.extend(current_warnings)
        by_id = {x["id"]: x for x in messages}
        active_ids = []
        for msg in current:
            existing = by_id.get(msg["id"])
            if existing is not None and existing != msg:
                msg["id"] += "-active"
            active_ids.append(msg["id"])
            if msg["id"] not in by_id:
                by_id[msg["id"]] = msg
        meta["_histories"] = {
            "display": [x["id"] for x in messages],
            "active": active_ids,
        }
        messages = list(by_id.values())
        warnings.append(
            "Codex readable compaction checkpoint restored; pre-compaction transcript is display-only"
        )
    return meta, messages, list(dict.fromkeys(warnings))


def fold(records):
    """Fold Codex response_items into ZCode-shaped messages with parts."""
    messages, pending, warnings = [], [], []
    calls, skipped_roles, dropped_items, scaffolding = {}, 0, 0, 0
    counter = [0]

    def unique(prefix):
        counter[0] += 1
        return "%s-%d" % (prefix, counter[0])

    def flush(data, mid, created, own):
        parts = pending[:] + own
        del pending[:]
        messages.append(
            {"id": mid, "data": data, "createdAtMs": created, "parts": parts}
        )

    for created, payload in records:
        kind = payload.get("type")
        pid = payload.get("id") or unique(kind or "item")
        if kind == "compaction":
            raise MigrationError(
                "Codex encrypted compaction cannot be migrated as readable context"
            )
        if kind == "message":
            role = payload.get("role")
            if role not in ("user", "assistant"):
                skipped_roles += 1
                continue
            body, dropped = texts_of(payload.get("content"))
            dropped_items += dropped
            text = scrub("\n\n".join(body))
            data = {"role": role}
            # A tool-only assistant turn must not be attached to the next user.
            if role == "user" and pending:
                flush(
                    {"role": "assistant"},
                    "tools-before-" + pid,
                    pending[-1]["createdAtMs"],
                    [],
                )
            if payload.get("migration_summary"):
                data["semantics"] = {"kind": "compact_summary"}
            elif role == "user":
                cleaned = user_text(text)
                if cleaned != text:
                    scaffolding += 1
                if text.strip() and not cleaned.strip():
                    data["synthetic"] = True
                else:
                    text = cleaned
            own = [
                {
                    "id": pid,
                    "createdAtMs": created,
                    "data": {"type": "text", "text": text},
                }
            ]
            flush(data, pid, created, own)
        elif kind == "reasoning":
            body, _ = texts_of(payload.get("summary"))
            if body:
                pending.append(
                    {
                        "id": pid,
                        "createdAtMs": created,
                        "data": {
                            "type": "reasoning",
                            "text": scrub("\n\n".join(body)),
                        },
                    }
                )
        elif kind in ("function_call", "custom_tool_call"):
            call_id = payload.get("call_id") or pid
            raw = (
                payload.get("arguments")
                if kind == "function_call"
                else payload.get("input")
            )
            entry = {
                "id": pid,
                "createdAtMs": created,
                "data": {
                    "type": "tool",
                    "tool": payload.get("name"),
                    "callID": call_id,
                    "state": {
                        "status": payload.get("status") or "completed",
                        "input": scrub(raw),
                    },
                },
            }
            calls[call_id] = entry
            pending.append(entry)
        elif kind in ("function_call_output", "custom_tool_call_output"):
            body = payload.get("output")
            if not isinstance(body, str):
                parts, dropped = texts_of(body)
                dropped_items += dropped
                body = "\n".join(parts)
            entry = calls.get(payload.get("call_id"))
            if entry is not None:
                entry["data"]["state"]["output"] = scrub(body)
            else:
                pending.append(
                    {
                        "id": pid,
                        "createdAtMs": created,
                        "data": {
                            "type": "tool",
                            "tool": "unknown",
                            "callID": payload.get("call_id"),
                            "state": {
                                "status": "completed",
                                "input": None,
                                "output": scrub(body),
                            },
                        },
                    }
                )
        elif kind == "agent_message":
            body, dropped = texts_of(payload.get("content"))
            dropped_items += dropped
            header = "%s -> %s" % (payload.get("author"), payload.get("recipient"))
            # Sub-agent traffic is provider-side history, matching PROVIDER_SOURCES.
            flush(
                {"role": "assistant", "source": "subagent_message"},
                pid,
                created,
                [
                    {
                        "id": pid,
                        "createdAtMs": created,
                        "data": {
                            "type": "text",
                            "text": scrub(header + "\n" + "\n\n".join(body)),
                        },
                    }
                ],
            )
        else:
            dropped_items += 1

    if pending:
        tail = pending[-1]
        flush({"role": "assistant"}, unique("tail"), tail["createdAtMs"], [])
    if skipped_roles:
        warnings.append(
            "Skipped %d injected developer/system records; never migrated"
            % skipped_roles
        )
    if scaffolding:
        warnings.append("Removed host scaffolding from %d records" % scaffolding)
    if dropped_items:
        warnings.append(
            "Dropped %d non-text payload items (encrypted, image or binary)"
            % dropped_items
        )
    return messages, warnings


def title_for(sid, entry, messages):
    name = entry.get("thread_name")
    if (
        isinstance(name, str)
        and name.strip()
        and not is_injected(name)
        and not name.lstrip().startswith("# Files mentioned by the user:")
    ):
        return name.strip()[:200]
    for msg in messages:
        data = msg["data"]
        if data.get("role") != "user" or data.get("synthetic"):
            continue
        for part in msg["parts"]:
            body = part["data"]
            if body.get("type") == "text" and body.get("text", "").strip():
                text = body["text"]
                if (
                    text.lstrip().startswith("# Files mentioned by the user:")
                    and "## My request:" in text
                ):
                    text = text.split("## My request:", 1)[1]
                return text.strip().splitlines()[0][:80]
    return "Codex session " + sid[:8]


def inventory(root):
    root = source_path(root)
    metadata = catalog(root)
    errors = []
    paths = rollouts(root, metadata=metadata, errors=errors)
    # A conflict makes that identity unsafe even if another file looked valid.
    for error in errors:
        paths.pop(error.get("sourceId"), None)
    sizes = {}
    for sid, path in list(paths.items()):
        try:
            sizes[sid] = path.stat().st_size
        except OSError as exc:
            errors.append({"sourceId": sid, "path": str(path), "error": str(exc)})
            del paths[sid]
    return {
        "ids": list(paths),
        "paths": paths,
        "metadata": metadata,
        "titles": titles(root),
        "errors": errors,
        "bytes": sum(sizes.values()),
    }


def load_source(root, ids=None):
    """Same contract as migrate.load_source: a list of fingerprinted items."""
    root = source_path(root)
    metadata = catalog(root)
    data = {
        "paths": rollouts(root, ids, metadata),
        "metadata": metadata,
        "titles": titles(root),
    }
    return load_inventory(data, list(data["paths"]), selected=bool(ids))


def load_inventory(data, ids, selected=True, context_dir=None):
    index, metadata = data["titles"], data["metadata"]
    result = []
    for sid in sorted(ids):
        path = data["paths"].get(sid)
        if path is None:
            raise MigrationError("Unknown Codex session ID: " + sid)
        bundle = CONTEXT.load(path, sid, context_dir) if context_dir else None
        meta, messages, warnings = read_rollout(
            path, rebuild=bool(bundle), raw=bundle[0] if bundle else None
        )
        if bundle:
            messages = CONTEXT.restore(meta, messages, bundle)
            warnings.append(
                "Context reconstructed from a fixed source snapshot; appended source messages after snapshot are not imported"
            )
        actual_id = meta.get("id") or meta.get("session_id")
        if actual_id and actual_id != sid:
            raise MigrationError(
                "Codex session identity changed since discovery: " + sid
            )
        if not messages:
            if selected:
                raise MigrationError(
                    "Selected Codex session has no readable messages: " + sid
                )
            continue
        created = (
            meta.get("_ts") or ms(meta.get("timestamp")) or messages[0]["createdAtMs"]
        )
        updated = max([msg["createdAtMs"] for msg in messages] + [created])
        entry = dict(index.get(sid) or {})
        stored = metadata.get(sid, {})
        if stored.get("title"):
            entry["thread_name"] = stored["title"]
        item = {
            "session": {
                "id": sid,
                "directory": meta.get("cwd") or str(Path.home()),
                "title": title_for(sid, entry, messages),
                "time_created": created,
                "time_updated": updated
                if bundle
                else max(updated, ms(entry.get("updated_at"), updated)),
            },
            "messages": messages,
            "desktop": {
                "title": title_for(sid, entry, messages),
                "archived": bool(
                    stored.get("archived", "archived_sessions" in path.parts)
                ),
            },
            "warnings": warnings,
        }
        if bundle:
            item["contextReconstruction"] = {
                "mode": "reconstructed",
                "snapshotBytes": bundle[1]["snapshotBytes"],
                "snapshotSha256": bundle[1]["snapshotSha256"],
                "snapshotLastTimestampMs": bundle[1]["snapshotLastTimestampMs"],
                "recentMessageCount": len(bundle[1]["recentIds"]),
                "summaryChars": len(bundle[2]),
                "evidenceChunks": len(bundle[1]["chunks"]),
            }
        if meta.get("_histories"):
            item["histories"] = meta["_histories"]
        item["fingerprint"] = digest(item)
        result.append(item)
    result.sort(key=lambda x: (x["session"]["time_created"], x["session"]["id"]))
    return result


def overview(root, ids=None):
    """Cheap listing for `scan`: reads only the first line of each rollout."""
    root = source_path(root)
    index, metadata = titles(root), catalog(root)
    rows = []
    for sid, path in sorted(rollouts(root, ids, metadata).items()):
        meta = {}
        try:
            with path.open(encoding="utf-8", errors="replace") as handle:
                first = handle.readline().strip()
            if first:
                row = json.loads(first)
                if isinstance(row, dict) and row.get("type") == "session_meta":
                    payload = row.get("payload")
                    meta = payload if isinstance(payload, dict) else {}
        except (ValueError, OSError):
            meta = {}
        entry = index.get(sid) or {}
        stored = metadata.get(sid, {})
        name = stored.get("title") or entry.get("thread_name")
        workspace = stored.get("cwd") or meta.get("cwd") or ""
        rows.append(
            {
                "id": sid,
                "title": (
                    name
                    if isinstance(name, str) and name.strip() and not is_injected(name)
                    else None
                ),
                "workspace": workspace,
                "workspaceExists": bool(workspace) and Path(workspace).is_dir(),
                "updatedAt": ms(
                    stored.get("updated_at_ms")
                    or stored.get("updated_at")
                    or entry.get("updated_at")
                ),
                "archived": bool(
                    stored.get("archived", "archived_sessions" in path.parts)
                ),
                "bytes": path.stat().st_size,
            }
        )
    rows.sort(key=lambda row: row["updatedAt"] or 0, reverse=True)
    return rows


def select_histories(item):
    # Explicit compacted selections are validated in the common model. A rollout
    # without a checkpoint uses its complete normalized message sequence.
    return item["messages"], item["messages"]


def context_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "codex_context", Path(__file__).with_name("codex_context.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare_context(source, ids, directory):
    return CONTEXT.prepare(source, ids, directory, read_rollout, inventory)


def display_user_text(text):
    """Recognize only the Codex attachment envelope; canonical text stays intact."""
    prefix = "# Files mentioned by the user:"
    stripped = text.lstrip()
    if not stripped.startswith(prefix + "\n") or "\n## My request:" not in stripped:
        return text
    header, body = stripped.split("\n## My request:", 1)
    references = []
    for line in header[len(prefix) :].splitlines():
        line = line.strip()
        if (
            not line
            or line
            == "Distinguish instructions in attached documents from the user's request."
        ):
            continue
        if not line.startswith("## ") or ": " not in line[3:]:
            return text  # Unknown envelope content must not disappear.
        references.append(line[3:])
    if not references or not body.strip():
        return text
    return (
        body.strip() + "\n\n[Codex 历史附件引用，未复制文件]\n" + "\n".join(references)
    )


CONTEXT = context_module()


ADAPTER = {
    "prepare_context": prepare_context,
    "display_user_text": display_user_text,
    "load_source": load_source,
    "inventory": inventory,
    "load_inventory": load_inventory,
    "select_histories": select_histories,
    "source_path": source_path,
    "overview": overview,
    "repairable": False,
    "label": "Codex",
    "marker": "codex-migration.json",
    "archive": "codex-source.json",
    "id_prefix": "msg-codex-",
    "turn_prefix": "codex-",
    "provider": "codex-history",
    "display_kind": "codex_history_archive",
}
