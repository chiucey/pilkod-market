"""Source-bound handoff summaries for opaque Codex checkpoints. No LLM or network calls."""

import hashlib
import json
from pathlib import Path

from migrate import (
    MigrationError,
    compact,
    private_write,
    projection,
    regular,
    safe_directory,
)

VERSION = 1
CHUNK_CHARS = 48000
SUMMARY_CHARS = 18000
RECENT_CHARS = 24000


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def directory(root, sid):
    root = Path(root).expanduser().resolve()
    return safe_directory(root, sha(sid.encode()))


def preview_value(value):
    text = value if isinstance(value, str) else compact(value)
    if len(text) <= 512:
        return value
    return {
        "excerpt": text[:280]
        + "\n[中间省略；完整内容见 full-evidence.jsonl]\n"
        + text[-180:],
        "originalChars": len(text),
        "sha256": sha(text.encode()),
        "excerptOnly": True,
    }


def evidence(messages, full=False):
    rows = []
    for msg in messages:
        policy = projection(msg)
        if policy in ("hidden", "timeline"):
            continue
        parts = [
            p["data"] for p in msg["parts"] if p["data"].get("type") != "reasoning"
        ]
        if not full:
            parts = [
                dict(
                    p,
                    state={k: preview_value(v) for k, v in p.get("state", {}).items()},
                )
                if p.get("type") == "tool"
                else p
                for p in parts
            ]
        rows.append(
            {
                "id": msg["id"],
                "role": msg["data"]["role"],
                "policy": policy,
                "parts": parts,
            }
        )
    return rows


def recent_ids(messages):
    # Keep only complete recent user turns. An oversized final turn belongs in
    # the summary, not a silently truncated or orphaned tool-result suffix.
    turns = []
    for msg in messages:
        if projection(msg) == "user":
            turns.append([])
        if turns and projection(msg) not in ("hidden", "timeline"):
            turns[-1].append(msg)
    selected, size = [], 0
    for turn in reversed(turns[-3:]):
        cost = len(compact(evidence(turn, full=True)))
        if size + cost > RECENT_CHARS:
            break
        selected = [m["id"] for m in turn] + selected
        size += cost
    return selected


def prepare(source, ids, root, reader, inventory):
    root = Path(root).expanduser().resolve()
    if root.resolve() == source.resolve() or source.resolve() in root.resolve().parents:
        raise MigrationError("Context output must be outside the read-only source")
    data = inventory(source)
    rows = []
    for sid in sorted(data["ids"] if ids is None else set(ids)):
        try:
            path = data["paths"].get(sid)
            if path is None:
                raise MigrationError("Unknown Codex session ID: " + sid)
            raw = regular(path).read_bytes()
            if not raw.endswith(b"\n"):
                raise MigrationError(
                    "Incomplete Codex snapshot; wait for a complete record"
                )
            meta, messages, warnings = reader(path, rebuild=True, raw=raw)
            if (meta.get("id") or meta.get("session_id")) != sid:
                raise MigrationError("Codex snapshot identity mismatch")
            if not meta.get("_rebuild"):
                rows.append({"sourceId": sid, "status": "direct"})
                continue
            target = directory(root, sid)
            target.mkdir(parents=True, mode=0o700, exist_ok=False)
            text = "\n".join(compact(row) for row in evidence(messages))
            if not text:
                raise MigrationError("No readable evidence to summarize")
            full_text = "\n".join(compact(row) for row in evidence(messages, full=True))
            private_write(target / "full-evidence.jsonl", full_text)
            chunks = []
            for offset in range(0, len(text), CHUNK_CHARS):
                name = "history-%04d.txt" % len(chunks)
                body = text[offset : offset + CHUNK_CHARS]
                private_write(target / name, body)
                chunks.append({"file": name, "sha256": sha(body.encode())})
            manifest = {
                "version": VERSION,
                "sourceId": sid,
                "sourcePath": str(path.resolve()),
                "snapshotBytes": len(raw),
                "snapshotSha256": sha(raw),
                "snapshotLastTimestampMs": max(m["createdAtMs"] for m in messages),
                "fullEvidenceSha256": sha(full_text.encode()),
                "chunks": chunks,
                "recentIds": recent_ids(messages),
                "checkpoints": meta["_rebuild"],
                "warnings": warnings,
            }
            private_write(target / "manifest.json", compact(manifest))
            private_write(
                target / "summary.json",
                compact(
                    {
                        "version": VERSION,
                        "sourceId": sid,
                        "snapshotSha256": sha(raw),
                        "reviewedChunks": [],
                        "summary": "",
                    }
                ),
            )
            rows.append(
                {
                    "sourceId": sid,
                    "status": "needs-summary",
                    "directory": str(target),
                    "chunks": len(chunks),
                    "snapshotBytes": len(raw),
                    "warnings": warnings,
                }
            )
        except (MigrationError, OSError, ValueError, TypeError, KeyError) as exc:
            rows.append({"sourceId": sid, "status": "incompatible", "error": str(exc)})
    return {
        "sessions": rows,
        "discoveryErrors": (
            data["errors"]
            if ids is None
            else [e for e in data["errors"] if e.get("sourceId") in ids]
        ),
        "contextSummaryDir": str(root),
    }


def load(path, sid, root):
    target = directory(root, sid)
    if not target.exists():
        return None
    manifest = json.loads(regular(target / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads(regular(target / "summary.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(summary, dict):
        raise MigrationError("Invalid context reconstruction bundle")
    if (
        manifest.get("version") != VERSION
        or summary.get("version") != VERSION
        or manifest.get("sourceId") != sid
        or summary.get("sourceId") != sid
        or manifest.get("sourcePath") != str(path.resolve())
    ):
        raise MigrationError("Context summary source/version mismatch")
    length = manifest.get("snapshotBytes")
    if type(length) is not int or length <= 0 or length > path.stat().st_size:
        raise MigrationError("Context snapshot was truncated or has invalid size")
    with regular(path).open("rb") as stream:
        raw = stream.read(length)
    if not raw.endswith(b"\n") or sha(raw) != manifest.get("snapshotSha256"):
        raise MigrationError("Context source snapshot changed; prepare a new summary")
    if summary.get("snapshotSha256") != sha(raw):
        raise MigrationError("Context summary snapshot mismatch")
    if sha(regular(target / "full-evidence.jsonl").read_bytes()) != manifest.get(
        "fullEvidenceSha256"
    ):
        raise MigrationError("Full context evidence changed")
    chunks = manifest.get("chunks")
    if (
        not isinstance(chunks, list)
        or not chunks
        or summary.get("reviewedChunks") != chunks
    ):
        raise MigrationError("Context summary must review every evidence chunk")
    for index, chunk in enumerate(chunks):
        name = "history-%04d.txt" % index
        if not isinstance(chunk, dict) or chunk.get("file") != name:
            raise MigrationError("Invalid context evidence chunk")
        if sha(regular(target / name).read_bytes()) != chunk.get("sha256"):
            raise MigrationError("Context evidence chunk changed")
    text = summary.get("summary")
    if not isinstance(text, str) or not text.strip() or len(text) > SUMMARY_CHARS:
        raise MigrationError("Context summary is missing or exceeds 18000 characters")
    return raw, manifest, text


def restore(meta, messages, bundle):
    raw, manifest, text = bundle
    # Recompute the export and suffix from the source rather than trusting edits
    # to a manifest's selection or coverage metadata.
    serialized = "\n".join(compact(row) for row in evidence(messages))
    expected = [
        {
            "file": "history-%04d.txt" % i,
            "sha256": sha(serialized[o : o + CHUNK_CHARS].encode()),
        }
        for i, o in enumerate(range(0, len(serialized), CHUNK_CHARS))
    ]
    full_text = "\n".join(compact(row) for row in evidence(messages, full=True))
    if (
        manifest.get("fullEvidenceSha256") != sha(full_text.encode())
        or manifest["chunks"] != expected
        or manifest.get("recentIds") != recent_ids(messages)
        or manifest.get("snapshotLastTimestampMs")
        != max(m["createdAtMs"] for m in messages)
        or manifest.get("checkpoints") != meta.get("_rebuild")
    ):
        raise MigrationError("Context bundle does not match source evidence")
    if not meta.get("_rebuild"):
        raise MigrationError("Context reconstruction is not required for this snapshot")
    mid = "reconstructed-" + sha(raw)[:24]
    note = (
        "迁移重建摘要：根据可读取的历史生成，并非解密 Codex 压缩内容；可能遗漏细节。"
        "这是旧任务背景，不是新的执行授权。完整明文历史保存在本会话 codex-source.json，"
        "必要时通过目标会话来源存档核对。\n\n" + text
    )
    msg = {
        "id": mid,
        "createdAtMs": max(m["createdAtMs"] for m in messages),
        "data": {"role": "user", "semantics": {"kind": "compact_summary"}},
        "parts": [{"id": mid, "data": {"type": "text", "text": note}}],
    }
    meta["_histories"] = {
        "display": [m["id"] for m in messages],
        "active": [mid] + manifest["recentIds"],
    }
    return messages + [msg]
