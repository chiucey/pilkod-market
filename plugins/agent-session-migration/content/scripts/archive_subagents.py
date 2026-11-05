"""预览或备份归档旧版误导入的 ZCode 内部会话；不删除历史。"""

import argparse
import sqlite3
import time
import uuid
from pathlib import Path

import migrate as m


def candidates(target, db, agent):
    from zcode_source import task_list_session

    ready, blocked = [], []
    rows = db.execute(
        "SELECT * FROM local_runtime_sessions WHERE agent_name=? AND columnar_version=3 AND archived=0",
        (agent,),
    ).fetchall()
    for row in rows:
        sid = row["session_id"]
        if not row["history_relative_dir"]:
            continue
        try:
            directory = m.safe_directory(
                target, "v2/sessions/" + row["history_relative_dir"]
            )
            marker = directory / "zcode-migration.json"
            if not marker.exists():
                continue
            provenance = m.parse(
                m.regular(marker).read_text(encoding="utf-8"), "provenance"
            )
            archive = m.parse(
                m.regular(directory / "zcode-source.json").read_text(encoding="utf-8"),
                "source archive",
            )
            source = archive["session"]
            if task_list_session(source):
                continue
            fingerprint = archive.pop("fingerprint", None)
            if (
                fingerprint != provenance.get("fingerprint")
                or m.digest(archive) != fingerprint
                or provenance.get("targetId") != sid
                or provenance.get("sourceId") != source["id"]
                or m.identity(Path(provenance["source"]), source["id"]) != sid
                or provenance.get("workspace") != row["workspace_dir"]
                or m.history_dir(sid, source["time_created"])
                != row["history_relative_dir"]
            ):
                raise m.MigrationError("Migration provenance mismatch")
            version = provenance.get("adapterVersion", 1)
            if version not in (1, m.ADAPTER_VERSION):
                raise m.MigrationError("Unsupported adapter version")
            display, expected, _ = (m.convert_legacy_v1 if version == 1 else m.convert)(
                archive, sid
            )
            observed = [
                m.parse(line, "history")
                for line in m.regular(directory / "messages.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]
            ids = {
                r[0]
                for r in db.execute(
                    "SELECT msg_id FROM local_runtime_message_rows WHERE session_id=?",
                    (sid,),
                )
            }
            if observed != expected or ids != {r["msg_id"] for r in display}:
                raise m.MigrationError(
                    "History changed or new input exists; leave this session untouched"
                )
            if row["status"] not in ("idle", "error"):
                raise m.MigrationError("Session must be idle or error")
            ready.append(
                {
                    "targetId": sid,
                    "title": row["title"],
                    "taskType": source["task_type"],
                    "parentSourceId": source.get("parent_id"),
                }
            )
        except (m.MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
            blocked.append({"targetId": sid, "reason": str(exc)})
    return ready, blocked


def run(target, agent="mavis", apply=False):
    m.use("zcode")
    dbfile = target / "v2/sqlite/runtime-state.sqlite"
    with m.migration_lock(target):
        with m.connect(dbfile) as db:
            m.check_target(db, agent)
            ready, blocked = candidates(target, db, agent)
        result = {"status": "planned", "sessions": ready, "blocked": blocked}
        if not apply or not ready:
            return result
        batch = m.safe_directory(target, "zcode-migration") / (
            "archive-subagents-"
            + str(int(time.time() * 1000))
            + "-"
            + uuid.uuid4().hex[:8]
        )
        batch.mkdir(parents=True, mode=0o700)
        backup_path = batch / "runtime-state.before.sqlite"
        m.private_write(backup_path, "")
        with m.connect(dbfile) as original:
            backup = sqlite3.connect(backup_path)
            try:
                original.backup(backup)
                if backup.execute("PRAGMA journal_mode=DELETE").fetchone()[
                    0
                ].lower() != "delete" or backup.execute(
                    "PRAGMA quick_check"
                ).fetchall() != [("ok",)]:
                    raise m.MigrationError("Standalone backup verification failed")
            finally:
                backup.close()
        with m.connect(dbfile, True) as db:
            db.execute("BEGIN IMMEDIATE")
            current, blocked = candidates(target, db, agent)
            if current != ready:
                raise m.MigrationError(
                    "Candidates changed during backup; preview again"
                )
            for item in ready:
                db.execute(
                    "UPDATE local_runtime_sessions SET archived=1,record_json=json_set(record_json,'$.archived',json('true')) WHERE session_id=?",
                    (item["targetId"],),
                )
            db.commit()
        result.update(status="archived", backup=str(backup_path), blocked=blocked)
        # A report failure must never encourage restoring the whole live database.
        try:
            m.private_write(batch / "report.json", m.compact(result) + "\n")
        except OSError as exc:
            raise m.MigrationError(
                "Archive COMMITTED; report failed; do not restore the whole DB: "
                + str(exc)
            ) from exc
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-data-dir", required=True)
    parser.add_argument("--agent", default="mavis")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Back up and archive the eligible imports shown by preview",
    )
    args = parser.parse_args()
    try:
        m.print_result(run(m.target_path(args.target_data_dir), args.agent, args.apply))
        return 0
    except (m.MigrationError, sqlite3.Error, OSError, ValueError) as exc:
        m.print_result({"error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
