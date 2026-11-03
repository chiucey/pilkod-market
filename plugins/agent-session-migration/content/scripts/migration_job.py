"""Shared, checkpointed migration job for every source and selection scope; no source or existing history writes."""

import json
import os
import sqlite3
import sys
import uuid
from pathlib import Path

VERSION = 2
DONE = {"imported", "already-imported"}


def save(m, path, report, create=False):
    if create:
        m.private_write(path, m.compact(report) + "\n")
        return
    m.regular(path)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        m.private_write(temporary, m.compact(report) + "\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def summary(report, path):
    counts = {}
    for entry in report["sessions"]:
        status = entry["status"]
        counts[status] = counts.get(status, 0) + 1
    return {
        "status": report["state"],
        "report": str(path),
        "total": len(report["sessions"]),
        "counts": counts,
        "discoveryErrors": len(report["discoveryErrors"]),
        "sourceBytes": report["sourceBytes"],
        "excludedSessions": len(report.get("excludedSessions", [])),
        "estimatedBackupBytes": report.get("estimatedBackupBytes", 0),
    }


def compatible(m, source, target, config, data, sid):
    try:
        return _compatible(m, source, target, config, data, sid)
    except (TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise m.MigrationError(
            "Invalid source record structure for " + sid + ": " + str(exc)
        ) from exc


def _compatible(m, source, target, config, data, sid):
    if config.get("contextSummaryDir"):
        items = m.adapter()["load_inventory"](
            data, [sid], context_dir=config["contextSummaryDir"]
        )
    else:
        items = m.adapter()["load_inventory"](data, [sid])
    if len(items) != 1 or not items[0]["messages"]:
        raise m.MigrationError(
            "Selected source session has no readable messages: " + sid
        )
    rows = m.plan(
        source,
        target,
        config["agent"],
        [sid],
        workspace=config["workspace"],
        restore_projects=config["restoreProjects"],
        _items=items,
    )
    if not config["allowReferences"] and any(
        "Attachment reference" in warning for row in rows for warning in row["warnings"]
    ):
        raise m.MigrationError("Attachments require explicit --allow-reference-only")
    return items, m.public_plan(rows)[0]


def recover(m, source, target, entry, report, committed_only=False):
    """Reconcile only an in-flight transaction, under the shared migration lock."""
    row = entry["plan"]
    sid = m.identity(source, entry["sourceId"])
    relative = m.history_dir(sid, row["sourceCreatedAtMs"])
    if row["targetId"] != sid or row["historyRelativeDir"] != relative:
        raise m.MigrationError("Invalid bulk recovery identity")
    directory = m.safe_directory(target, "v2/sessions/" + relative)
    with m.connect(target / "v2/sqlite/runtime-state.sqlite") as db:
        existing = db.execute(
            "SELECT history_relative_dir,agent_name FROM local_runtime_sessions WHERE session_id=?",
            (sid,),
        ).fetchone()
        if existing:
            if (
                existing["history_relative_dir"] != relative
                or existing["agent_name"] != report["config"]["agent"]
            ):
                raise m.MigrationError("Bulk recovery target identity conflict")
            marker = m.parse(
                m.regular(directory / m.adapter()["marker"]).read_text(
                    encoding="utf-8"
                ),
                "migration marker",
            )
            if any(
                marker.get(key) != row[key]
                for key in ("fingerprint", "sourceId", "targetId", "workspace")
            ):
                raise m.MigrationError("Bulk recovery provenance mismatch")
            if (
                marker.get("source") != str(source)
                or marker.get("sourceType") != report["config"]["sourceType"]
            ):
                raise m.MigrationError("Bulk recovery source mismatch")
            m.regular(directory / "messages.jsonl")
            count = db.execute(
                "SELECT COUNT(*) FROM local_runtime_message_rows WHERE session_id=?",
                (sid,),
            ).fetchone()[0]
            initialized = db.execute(
                "SELECT 1 FROM local_runtime_pi_history_file_migrations WHERE session_id=?",
                (sid,),
            ).fetchone()
            if count < row["messageCount"] or not initialized:
                raise m.MigrationError(
                    "Bulk recovery found incomplete committed session; inspect target"
                )
            entry["status"] = "imported"
            entry.pop("error", None)
            return
    if committed_only:
        raise m.MigrationError(
            "Previously completed target session is missing; inspect target before retry"
        )
    if directory.exists():
        # The persisted running intent precedes mkdir and the DB transaction. Preserve
        # only this uncommitted attempt, never delete or restore the database wholesale.
        quarantine = m.safe_directory(
            target, "zcode-migration/recovered-" + uuid.uuid4().hex
        )
        os.replace(directory, quarantine)
        entry.setdefault("recoveredDirectories", []).append(str(quarantine))
    entry["status"] = "ready"


def execute(m, args, source, target):
    source, target = source.resolve(), target.resolve()
    if bool(args.all) == bool(args.session):
        raise m.MigrationError(
            "Choose exactly one scope: --all or one/more --session IDs"
        )
    if not args.report:
        raise m.MigrationError(
            "Migration requires --report <preview-and-progress.json>"
        )
    if args.all and args.workspace:
        raise m.MigrationError(
            "--all cannot remap every project to one --workspace; select affected sessions separately"
        )
    if not 1 <= args.batch_size <= 100:
        raise m.MigrationError("--batch-size must be between 1 and 100")
    path = Path(args.report).expanduser().absolute()
    if m.is_link(path):
        raise m.MigrationError("Linked bulk report path")
    path = path.resolve()
    if path == source or source in path.parents:
        raise m.MigrationError(
            "Bulk report must be outside the read-only source directory"
        )
    config = {
        "source": str(source),
        "target": str(target),
        "agent": args.agent,
        "sourceType": args.source,
        "adapterVersion": m.ADAPTER_VERSION,
        "allowReferences": args.allow_reference_only,
        "restoreProjects": args.restore_projects,
        "selection": {"mode": "all"}
        if args.all
        else {"mode": "selected", "ids": sorted(set(args.session))},
        "workspace": str(Path(args.workspace).expanduser().resolve())
        if args.workspace
        else None,
    }
    context_dir = getattr(args, "context_summary_dir", None)
    if context_dir:
        if args.source != "codex":
            raise m.MigrationError("Context reconstruction is only supported for Codex")
        config["contextSummaryDir"] = str(Path(context_dir).expanduser().resolve())
    if args.command == "plan":
        if path.exists():
            raise m.MigrationError(
                "Preview report already exists; use a new report path or resume with apply"
            )
        # Global source/catalog or target contract failures abort rather than masquerade
        # as thousands of per-session incompatibilities.
        with m.connect(target / "v2/sqlite/runtime-state.sqlite") as db:
            m.check_target(db, args.agent)
            database_bytes = (
                db.execute("PRAGMA page_count").fetchone()[0]
                * db.execute("PRAGMA page_size").fetchone()[0]
            )
        data = m.adapter()["inventory"](source)
        selected = set(args.session or [])
        preview_ids = sorted(data["ids"] if args.all else selected)
        discovery_errors = (
            data["errors"]
            if args.all
            else [
                error for error in data["errors"] if error.get("sourceId") in selected
            ]
        )
        report = {
            "version": VERSION,
            "config": config,
            "state": "previewing",
            "sessions": [],
            "discoveryErrors": discovery_errors,
            "excludedSessions": data.get("excluded", []) if args.all else [],
            "batches": [],
            "sourceBytes": data["bytes"],
        }
        save(m, path, report, create=True)
        discovery_failures = {
            error.get("sourceId"): error["error"] for error in discovery_errors
        }
        for sid in preview_ids:
            entry = {"sourceId": sid}
            try:
                if sid in discovery_failures:
                    raise m.MigrationError(discovery_failures[sid])
                _, row = compatible(m, source, target, config, data, sid)
                entry.update(
                    status="already-imported"
                    if row["status"] == "already-imported"
                    else "ready",
                    plan=row,
                )
            except (m.MigrationError, sqlite3.Error, OSError, ValueError) as exc:
                entry.update(status="incompatible", error=str(exc))
            report["sessions"].append(entry)
            if len(report["sessions"]) % args.batch_size == 0:
                save(m, path, report)
                m.print_result(summary(report, path), file=sys.stderr)
        ready = sum(entry["status"] == "ready" for entry in report["sessions"])
        report["estimatedBackupBytes"] = (
            (ready + args.batch_size - 1) // args.batch_size
        ) * database_bytes
        report["state"] = "planned"
        save(m, path, report)
        return summary(report, path)
    report = json.loads(m.regular(path).read_text(encoding="utf-8"))
    # Version 1 existed only for Codex --all. Upgrade in memory; never change
    # source fingerprints or target identities during a job schema migration.
    if (
        isinstance(report, dict)
        and report.get("version") == 1
        and isinstance(report.get("config"), dict)
        and report["config"].get("sourceType") == "codex"
    ):
        report["version"] = VERSION
        report["config"].setdefault("selection", {"mode": "all"})
        report["config"].setdefault("workspace", None)
    if (
        not isinstance(report, dict)
        or report.get("version") != VERSION
        or report.get("config") != config
    ):
        raise m.MigrationError(
            "Bulk report source/target/options/version mismatch; use the preview options"
        )
    if report.get("state") not in (
        "planned",
        "running",
        "completed",
        "completed-with-errors",
    ):
        raise m.MigrationError(
            "Preview is incomplete; generate a new preview before applying"
        )
    entries = report.get("sessions")
    if (
        not isinstance(entries, list)
        or not isinstance(report.get("discoveryErrors"), list)
        or not isinstance(report.get("batches"), list)
    ):
        raise m.MigrationError("Invalid bulk report lists")
    seen = set()
    for entry in entries:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("sourceId"), str)
            or entry["sourceId"] in seen
        ):
            raise m.MigrationError("Invalid or duplicate bulk report identity")
        seen.add(entry["sourceId"])
        if entry.get("status") not in DONE | {
            "ready",
            "running",
            "failed",
            "incompatible",
        }:
            raise m.MigrationError("Invalid bulk report status")
        if entry["status"] in DONE | {"ready", "running"} and not isinstance(
            entry.get("plan"), dict
        ):
            raise m.MigrationError("Missing bulk report plan")
    with m.migration_lock(target):
        with m.connect(target / "v2/sqlite/runtime-state.sqlite") as db:
            m.check_target(db, args.agent)
        for entry in report["sessions"]:
            if entry["status"] == "running" or entry["status"] in DONE:
                previous = entry["status"]
                recover(
                    m, source, target, entry, report, committed_only=previous in DONE
                )
                if previous in DONE:
                    entry["status"] = previous
        report["state"] = "running"
        save(m, path, report)
        data = m.adapter()["inventory"](source)
        errors = {e.get("sourceId"): e["error"] for e in data["errors"]}
        pending = [
            e
            for e in report["sessions"]
            if e["status"] == "ready"
            or args.retry_failed
            and e["status"] in ("failed", "incompatible")
        ]

        def commit(entries, items):
            for entry in entries:
                entry["status"] = "running"
            save(m, path, report)
            try:
                result = m._apply_locked(
                    source,
                    target,
                    args.agent,
                    ids=[e["sourceId"] for e in entries],
                    _items=items,
                    workspace=config["workspace"],
                    allow_references=args.allow_reference_only,
                    restore_projects=args.restore_projects,
                )
                report["batches"].append(
                    {
                        k: result[k]
                        for k in ("status", "backup", "report")
                        if k in result
                    }
                )
                for entry in entries:
                    entry["status"] = (
                        "imported"
                        if result["status"] == "imported"
                        else "already-imported"
                    )
                    entry.pop("error", None)
            except (m.MigrationError, sqlite3.Error, OSError, ValueError) as exc:
                # A commit can succeed before its report is saved. Reconcile against
                # SQLite before isolating failed members of a rolled-back batch.
                retry = []
                for entry, item in zip(entries, items):
                    try:
                        recover(m, source, target, entry, report)
                        if entry["status"] not in DONE:
                            retry.append((entry, item))
                    except (
                        m.MigrationError,
                        sqlite3.Error,
                        OSError,
                        ValueError,
                    ) as recovery_error:
                        entry.update(status="failed", error=str(recovery_error))
                if len(entries) == 1:
                    for entry, _ in retry:
                        entry.update(status="failed", error=str(exc))
                else:
                    for entry, item in retry:
                        commit([entry], [item])
            save(m, path, report)
            m.print_result(summary(report, path), file=sys.stderr)

        for offset in range(0, len(pending), args.batch_size):
            entries, items = [], []
            for entry in pending[offset : offset + args.batch_size]:
                sid = entry["sourceId"]
                try:
                    if sid in errors:
                        raise m.MigrationError(errors[sid])
                    loaded, row = compatible(m, source, target, config, data, sid)
                    if (
                        "plan" in entry
                        and row["fingerprint"] != entry["plan"]["fingerprint"]
                    ):
                        raise m.MigrationError(
                            "Source changed since preview; generate a new preview"
                        )
                    entry["plan"] = row
                    if row["status"] == "already-imported":
                        entry["status"] = "already-imported"
                        entry.pop("error", None)
                        continue
                    entries.append(entry)
                    items.extend(loaded)
                except (m.MigrationError, sqlite3.Error, OSError, ValueError) as exc:
                    entry.update(status="failed", error=str(exc))
            save(m, path, report)
            if entries:
                commit(entries, items)
        report["state"] = (
            "completed-with-errors"
            if report["discoveryErrors"]
            or any(e["status"] not in DONE for e in report["sessions"])
            else "completed"
        )
        save(m, path, report)
    return summary(report, path)
