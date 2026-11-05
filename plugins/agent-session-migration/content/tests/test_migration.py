import contextlib
import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "migrate", Path(__file__).parents[1] / "scripts/migrate.py"
)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "source.sqlite"
        self.target = self.root / "target"
        self.cwd = self.root / "workspace"
        self.cwd.mkdir()
        (self.target / "v2/sqlite").mkdir(parents=True)
        db = sqlite3.connect(self.source)
        db.executescript("""CREATE TABLE session(id TEXT PRIMARY KEY,directory TEXT,title TEXT,time_created INTEGER,time_updated INTEGER,revert TEXT);
CREATE TABLE message(id TEXT,session_id TEXT,time_created INTEGER,data TEXT,sequence INTEGER);
CREATE TABLE part(id TEXT,message_id TEXT,session_id TEXT,time_created INTEGER,data TEXT,sequence INTEGER);""")
        for i in range(2):
            sid = "s" + str(i)
            db.execute(
                "INSERT INTO session(id,directory,title,time_created,time_updated) VALUES (?,?,?,?,?)",
                (
                    sid,
                    str(self.cwd),
                    "中文标题 " + str(i),
                    1700000000000 + i,
                    1700000001000 + i,
                ),
            )
            for j, role in enumerate(("user", "assistant")):
                mid = sid + "m" + str(j)
                db.execute(
                    "INSERT INTO message VALUES (?,?,?,?,?)",
                    (mid, sid, 1700000000000 + j, json.dumps({"role": role}), j),
                )
                parts = [{"type": "text", "text": "Hello 世界 " + role}]
                if role == "assistant":
                    parts += [
                        {
                            "type": "tool",
                            "tool": "bash",
                            "callID": "tool1",
                            "state": {
                                "status": "completed",
                                "input": {"command": "NEVER_EXECUTE"},
                                "output": "old output",
                            },
                        },
                        {"type": "reasoning", "text": "historical thought"},
                    ]
                for k, p in enumerate(parts):
                    db.execute(
                        "INSERT INTO part VALUES (?,?,?,?,?,?)",
                        (
                            mid + "p" + str(k),
                            mid,
                            sid,
                            1700000000000 + j,
                            json.dumps(p),
                            k,
                        ),
                    )
        db.commit()
        db.close()
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            db.executescript("""CREATE TABLE local_runtime_sessions(session_id TEXT PRIMARY KEY,record_json TEXT,updated_at_ms INTEGER,columnar_version INTEGER,agent_name TEXT,runtime TEXT,session_type TEXT,status TEXT,archived INTEGER,visibility TEXT,session_kind TEXT,purpose_kind TEXT,workspace_dir TEXT,project_workspace_dir TEXT,is_default_workspace INTEGER,title TEXT,created_at_ms INTEGER,extra_data_json TEXT,project_id INTEGER,history_relative_dir TEXT);
CREATE TABLE local_runtime_message_rows(id INTEGER PRIMARY KEY,session_id TEXT,msg_id TEXT,role TEXT,turn_id TEXT,source TEXT,created_at_ms INTEGER,data_json TEXT,UNIQUE(session_id,msg_id));
CREATE TABLE local_runtime_pi_history_file_migrations(session_id TEXT PRIMARY KEY,migrated_at_ms INTEGER NOT NULL,source TEXT NOT NULL,message_count INTEGER NOT NULL,target_revision TEXT NOT NULL);
CREATE TABLE local_runtime_projects(project_id INTEGER PRIMARY KEY,project_kind TEXT,workspace_dir TEXT,created_at_ms INTEGER,updated_at_ms INTEGER,hidden INTEGER NOT NULL DEFAULT 0,extra_data_json TEXT NOT NULL DEFAULT '{}');
CREATE TABLE local_runtime_session_fts_keys(fts_rowid INTEGER PRIMARY KEY AUTOINCREMENT,session_id TEXT NOT NULL UNIQUE REFERENCES local_runtime_sessions(session_id) ON DELETE CASCADE);
CREATE VIRTUAL TABLE local_runtime_sessions_fts USING fts5(session_id UNINDEXED,session_id_terms,agent_name_terms,title_terms,workspace_dir_terms,purpose_terms,status_terms,session_type_terms,tokenize='unicode61');
INSERT INTO local_runtime_sessions(session_id,columnar_version,agent_name,extra_data_json) VALUES('existing',3,'mavis','{}');""")

    def tearDown(self):
        self.tmp.cleanup()

    def count(self):
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            return db.execute("SELECT COUNT(*) FROM local_runtime_sessions").fetchone()[
                0
            ]

    def test_import_initializes_history_before_first_turn(self):
        r = m.apply(self.source, self.target, "mavis")
        for row in r["sessions"]:
            history = (
                self.target
                / "v2/sessions"
                / row["historyRelativeDir"]
                / "messages.jsonl"
            )
            records = [json.loads(x) for x in history.read_text().splitlines()]
            with m.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
                checkpoint = db.execute(
                    "SELECT * FROM local_runtime_pi_history_file_migrations WHERE session_id=?",
                    (row["targetId"],),
                ).fetchone()
            self.assertIsNotNone(
                checkpoint,
                "First-turn materialization compares imported history with empty legacy storage without this checkpoint",
            )
            self.assertEqual(checkpoint["message_count"], len(records))
            self.assertEqual(checkpoint["target_revision"], m.history_revision(records))
            self.assertEqual(checkpoint["source"], "empty")

    def old_import(self):
        row = m.apply(self.source, self.target, "mavis")["sessions"][0]
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            db.execute(
                "DELETE FROM local_runtime_pi_history_file_migrations WHERE session_id=?",
                (row["targetId"],),
            )
            db.commit()
        return row

    def test_repair_preserves_history_and_failed_display_messages(self):
        row = self.old_import()
        sid = row["targetId"]
        history = (
            self.target / "v2/sessions" / row["historyRelativeDir"] / "messages.jsonl"
        )
        before = history.read_bytes()
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            db.execute(
                "INSERT INTO local_runtime_message_rows(session_id,msg_id,data_json) VALUES(?, 'failed-user-input','{}')",
                (sid,),
            )
            db.commit()
        result = m.repair(self.target, "mavis", sid)
        self.assertEqual(result["status"], "repaired")
        self.assertTrue(Path(result["backup"]).is_file())
        self.assertEqual(history.read_bytes(), before)
        with m.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(*) FROM local_runtime_message_rows WHERE session_id=?",
                    (sid,),
                ).fetchone()[0],
                3,
            )
        self.assertEqual(m.repair(self.target, "mavis", sid)["status"], "unchanged")

    def test_repair_refuses_changed_history_and_active_session(self):
        row = self.old_import()
        sid = row["targetId"]
        history = (
            self.target / "v2/sessions" / row["historyRelativeDir"] / "messages.jsonl"
        )
        before = history.read_bytes()
        history.write_text(history.read_text().replace("Hello", "Edited"))
        with self.assertRaisesRegex(m.MigrationError, "history differs"):
            m.repair(self.target, "mavis", sid)
        history.write_bytes(before)
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            db.execute(
                "UPDATE local_runtime_sessions SET status='running' WHERE session_id=?",
                (sid,),
            )
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "idle or error"):
            m.repair(self.target, "mavis", sid)

    def test_old_import_is_not_reported_as_ready(self):
        self.old_import()
        with self.assertRaisesRegex(m.MigrationError, "needs history repair"):
            m.apply(self.source, self.target, "mavis")

    def test_repair_checks_provenance_and_lock(self):
        row = self.old_import()
        sid = row["targetId"]
        lock = self.target / "zcode-migration/apply.lock"
        lock.write_text("another import")
        with self.assertRaisesRegex(m.MigrationError, "lock"):
            m.repair(self.target, "mavis", sid)
        lock.unlink()
        archive = (
            self.target
            / "v2/sessions"
            / row["historyRelativeDir"]
            / "zcode-source.json"
        )
        archive.write_text(archive.read_text().replace("Hello", "Changed"))
        with self.assertRaisesRegex(m.MigrationError, "fingerprint mismatch"):
            m.repair(self.target, "mavis", sid)

    def test_missing_history_contract_refused_before_writes(self):
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            db.execute("DROP TABLE local_runtime_pi_history_file_migrations")
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "Unsupported schema"):
            m.apply(self.source, self.target, "mavis")
        self.assertEqual(self.count(), 1)
        self.assertFalse((self.target / "v2/sessions").exists())

    def test_repair_frozen_v1_import_without_reconverting_to_current_ids(self):
        row = self.old_import()
        sid = row["targetId"]
        directory = self.target / "v2/sessions" / row["historyRelativeDir"]
        provenance = json.loads(
            (directory / "zcode-migration.json").read_text(encoding="utf-8")
        )
        provenance.pop("adapterVersion")
        (directory / "zcode-migration.json").write_text(
            m.compact(provenance), encoding="utf-8"
        )
        archive = json.loads(
            (directory / "zcode-source.json").read_text(encoding="utf-8")
        )
        records = m.convert_legacy_v1(archive, sid)[1]
        self.assertTrue(records[0]["message_id"].startswith("msg-zcode-"))
        history = directory / "messages.jsonl"
        history.write_text(
            "".join(m.compact(x) + "\n" for x in records), encoding="utf-8"
        )
        before = history.read_bytes()
        self.assertEqual(m.repair(self.target, "mavis", sid)["status"], "repaired")
        self.assertEqual(history.read_bytes(), before)

    def test_checkpoint_rolls_back_with_failed_import(self):
        with self.assertRaises(m.MigrationError):
            m.apply(self.source, self.target, "mavis", fail_after=1)
        with m.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(*) FROM local_runtime_pi_history_file_migrations"
                ).fetchone()[0],
                0,
            )

    def test_zcode_task_list_excludes_children_but_keeps_user_forks(self):
        with sqlite3.connect(self.source) as db:
            db.execute("ALTER TABLE session ADD COLUMN task_type TEXT")
            db.execute("ALTER TABLE session ADD COLUMN parent_id TEXT")
            db.execute(
                "UPDATE session SET task_type='fork',parent_id='other' WHERE id='s0'"
            )
            db.execute(
                "UPDATE session SET task_type='subagent_child',parent_id='s0' WHERE id='s1'"
            )
        data = m.adapter()["inventory"](self.source)
        self.assertEqual(data["ids"], ["s0"])
        self.assertEqual(len(data["excluded"]), 1)
        self.assertEqual(
            [r["sourceId"] for r in m.plan(self.source, self.target, "mavis")], ["s0"]
        )
        with self.assertRaisesRegex(m.MigrationError, "not a top-level"):
            m.load_source(self.source, ["s1"])

    def test_zcode_session_types_match_source_list_without_parent_heuristics(self):
        with sqlite3.connect(self.source) as db:
            db.execute("ALTER TABLE session ADD COLUMN task_type TEXT")
            db.execute("ALTER TABLE session ADD COLUMN parent_id TEXT")
            db.execute("UPDATE session SET parent_id='missing-parent'")
        for kind, allowed in [
            ("interactive", True),
            ("fork", True),
            ("workflow_parent", True),
            ("subagent_child", False),
            ("workflow_child", False),
            ("nested_workflow_child", False),
            ("selection_side_chat", False),
            (None, True),
        ]:
            with self.subTest(kind=kind), sqlite3.connect(self.source) as db:
                db.execute("UPDATE session SET task_type=?", (kind,))
                db.commit()
                data = m.adapter()["inventory"](self.source)
                self.assertEqual(len(data["ids"]), 2 if allowed else 0)

    def test_archive_old_subagent_import_preserves_messages_and_fork(self):
        self.migration_types_fixture()
        cleanup = self.cleanup_module()
        before = {
            p: p.read_bytes()
            for p in (self.target / "v2/sessions").rglob("messages.jsonl")
        }
        preview = cleanup.run(self.target)
        self.assertEqual(len(preview["sessions"]), 1)
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            self.assertEqual(
                db.execute(
                    "SELECT sum(archived) FROM local_runtime_sessions"
                ).fetchone()[0],
                0,
            )
        result = cleanup.run(self.target, apply=True)
        self.assertEqual(result["status"], "archived")
        self.assertTrue(Path(result["backup"]).is_file())
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertEqual(cleanup.run(self.target, apply=True)["sessions"], [])

    def cleanup_module(self):
        def run(target, apply=False):
            command = [
                sys.executable,
                "-B",
                str(Path(__file__).parents[1] / "scripts/archive_subagents.py"),
                "--target-data-dir",
                str(target),
            ]
            if apply:
                command.append("--apply")
            return json.loads(subprocess.check_output(command, text=True))

        return SimpleNamespace(run=run)

    def migration_types_fixture(self):
        with sqlite3.connect(self.source) as db:
            db.execute("ALTER TABLE session ADD COLUMN task_type TEXT")
            db.execute(
                "UPDATE session SET task_type=CASE id WHEN 's0' THEN 'fork' ELSE 'subagent_child' END"
            )
        # Reproduce the old importer which admitted internal sessions.
        adapter = m.adapter()
        with patch.dict(
            adapter["inventory"].__globals__, {"task_list_session": lambda row: True}
        ):
            m.apply(self.source, self.target, "mavis")

    def test_archive_refuses_continued_or_active_child(self):
        self.migration_types_fixture()
        cleanup = self.cleanup_module()
        sid = m.identity(self.source, "s1")
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            db.execute(
                "UPDATE local_runtime_sessions SET status='running' WHERE session_id=?",
                (sid,),
            )
        result = cleanup.run(self.target, apply=True)
        self.assertEqual(result["sessions"], [])
        self.assertEqual(len(result["blocked"]), 1)
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            db.execute(
                "UPDATE local_runtime_sessions SET status='idle' WHERE session_id=?",
                (sid,),
            )
            db.execute(
                "INSERT INTO local_runtime_message_rows(session_id,msg_id,data_json) VALUES(?,'new-user-input','{}')",
                (sid,),
            )
        result = cleanup.run(self.target, apply=True)
        self.assertEqual(result["sessions"], [])
        self.assertIn("new input", result["blocked"][0]["reason"])

    def test_archive_rejects_corrupt_source_and_rolls_back_database_failure(self):
        self.migration_types_fixture()
        cleanup = self.cleanup_module()
        sid = m.identity(self.source, "s1")
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            rel = db.execute(
                "SELECT history_relative_dir FROM local_runtime_sessions WHERE session_id=?",
                (sid,),
            ).fetchone()[0]
        source = self.target / "v2/sessions" / rel / "zcode-source.json"
        original = source.read_bytes()
        archive = json.loads(original)
        archive["session"]["title"] = "tampered"
        source.write_text(json.dumps(archive), encoding="utf-8")
        result = cleanup.run(self.target, apply=True)
        self.assertEqual(result["sessions"], [])
        self.assertEqual(len(result["blocked"]), 1)
        source.write_bytes(original)
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            db.execute(
                "CREATE TRIGGER refuse_archive BEFORE UPDATE OF archived ON local_runtime_sessions BEGIN SELECT RAISE(ABORT,'injected archive failure'); END"
            )
        with self.assertRaises(subprocess.CalledProcessError):
            cleanup.run(self.target, apply=True)
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            self.assertEqual(
                db.execute(
                    "SELECT archived FROM local_runtime_sessions WHERE session_id=?",
                    (sid,),
                ).fetchone()[0],
                0,
            )
        self.assertEqual(original, source.read_bytes())

    def test_unknown_zcode_task_type_is_not_silently_promoted(self):
        with sqlite3.connect(self.source) as db:
            db.execute("ALTER TABLE session ADD COLUMN task_type TEXT")
            db.execute("UPDATE session SET task_type='future-internal'")
        with self.assertRaisesRegex(
            m.MigrationError, "Unknown ZCode session task_type"
        ):
            m.load_source(self.source)

    def test_scan_and_plan_are_read_only(self):
        before = self.source.read_bytes()
        rows = m.plan(self.source, self.target, "mavis")
        self.assertEqual(len(rows), 2)
        self.assertEqual(before, self.source.read_bytes())
        self.assertEqual(self.count(), 1)
        self.assertFalse((self.target / "v2/sessions").exists())

    def test_import_native_history_and_idempotence(self):
        before = self.source.read_bytes()
        r = m.apply(self.source, self.target, "mavis")
        self.assertEqual(r["imported"], 2)
        self.assertEqual(self.count(), 3)
        self.assertTrue(Path(r["backup"]).is_file())
        self.assertEqual(before, self.source.read_bytes())
        row = r["sessions"][0]
        history = (
            self.target / "v2/sessions" / row["historyRelativeDir"] / "messages.jsonl"
        )
        entries = [
            json.loads(x) for x in history.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual([x["message"]["role"] for x in entries], ["user", "assistant"])
        self.assertIn("NEVER_EXECUTE", entries[1]["message"]["content"][0]["text"])
        self.assertNotIn("historical thought", history.read_text(encoding="utf-8"))
        self.assertEqual(
            m.apply(self.source, self.target, "mavis")["status"], "unchanged"
        )
        self.assertEqual(self.count(), 3)

    def test_history_tool_projection_is_shared_inert_and_context_preserving(self):
        item = m.load_source(self.source, ["s0"])[0]
        for source in ("zcode", "codex"):
            with self.subTest(source=source):
                m.use(source)
                for name in ("bash", "read", "thinking", "mcp__delete_file", "unknown"):
                    tool = next(
                        p["data"]
                        for p in item["messages"][1]["parts"]
                        if p["data"]["type"] == "tool"
                    )
                    tool["tool"] = name
                    tool["state"]["status"] = "running"
                    tool["state"]["output"] = "first line\nsecond line"
                    display, canonical, _ = m.convert(item, "mvs-test")
                    view = display[1]
                    call = view["tool_calls"][0]
                    self.assertEqual(call["tool_name"], "历史工具记录")
                    self.assertEqual(call["tool_call_status"], 2)
                    self.assertNotIn("NEVER_EXECUTE", view["msg_content"])
                    self.assertIn(name, json.loads(call["tool_call_args"]))
                    self.assertIn("running", json.loads(call["tool_call_args"]))
                    self.assertIn(
                        "first line\nsecond line",
                        json.loads(call["tool_call_result_data"])["content"][0]["text"],
                    )
                    content = canonical[1]["message"]["content"]
                    self.assertTrue(all(c["type"] == "text" for c in content))
                    evidence = {
                        "tool": name,
                        "callID": tool["callID"],
                        "status": "running",
                        "input": tool["state"]["input"],
                        "output": "first line\nsecond line",
                    }
                    self.assertIn(m.compact(evidence), content[0]["text"])
        m.use("zcode")

    def test_source_title_prefix_and_repeat_preserve_target_rename(self):
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute("UPDATE session SET title='[From ZCode] 已标记' WHERE id='s0'")
            db.commit()
        result = m.apply(self.source, self.target, "mavis")
        row = result["sessions"][0]
        self.assertEqual(row["title"], "[From ZCode] 已标记")
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            title, record = db.execute(
                "SELECT title,record_json FROM local_runtime_sessions WHERE session_id=?",
                (row["targetId"],),
            ).fetchone()
            self.assertEqual(title, row["title"])
            self.assertEqual(json.loads(record)["title"], title)
            db.execute(
                "UPDATE local_runtime_sessions SET title='用户改名' WHERE session_id=?",
                (row["targetId"],),
            )
            db.commit()
        repeated = m.apply(self.source, self.target, "mavis")
        self.assertEqual(repeated["status"], "unchanged")
        self.assertEqual(repeated["sessions"][0]["title"], "用户改名")

    def test_atomic_failure_rolls_back_all_sessions_and_files(self):
        with self.assertRaisesRegex(m.MigrationError, "Injected"):
            m.apply(self.source, self.target, "mavis", fail_after=1)
        self.assertEqual(self.count(), 1)
        self.assertEqual(
            list((self.target / "v2/sessions").rglob("messages.jsonl")), []
        )
        self.assertEqual(m.apply(self.source, self.target, "mavis")["imported"], 2)

    def test_changed_source_never_overwrites_continued_target(self):
        m.apply(self.source, self.target, "mavis")
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute("UPDATE session SET title='changed' WHERE id='s0'")
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "Source changed"):
            m.apply(self.source, self.target, "mavis")
        self.assertEqual(self.count(), 3)

    def test_corruption_aborts_before_write(self):
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute("UPDATE part SET data='broken' WHERE id='s0m0p0'")
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "Malformed"):
            m.apply(self.source, self.target, "mavis")
        self.assertEqual(self.count(), 1)

    def test_target_profile_required_and_unknown_source_rejected(self):
        with self.assertRaises(m.MigrationError):
            m.target_path(None)
        with self.assertRaisesRegex(m.MigrationError, "Unknown source"):
            m.plan(self.source, self.target, "mavis", ["missing"])

    def test_lock_prevents_concurrent_import(self):
        (self.target / "zcode-migration").mkdir()
        (self.target / "zcode-migration/apply.lock").write_text("other")
        with self.assertRaisesRegex(m.MigrationError, "lock"):
            m.apply(self.source, self.target, "mavis")
        self.assertEqual(self.count(), 1)

    def test_symlink_destination_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        try:
            (self.target / "v2/sessions").symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest("Symlink privilege unavailable: " + str(exc))
        with self.assertRaisesRegex(m.MigrationError, "Symlink"):
            m.apply(self.source, self.target, "mavis")
        self.assertEqual(list(outside.iterdir()), [])

    def test_future_contract_rejected(self):
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            db.execute(
                "UPDATE local_runtime_sessions SET extra_data_json=?",
                (json.dumps({"sessionDataVersion": 5}),),
            )
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "Newer"):
            m.apply(self.source, self.target, "mavis")

    def test_attachment_missing_bytes_reported(self):
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute(
                "UPDATE part SET data=? WHERE id=?",
                (
                    json.dumps({"type": "file", "url": "file:///do/not/read/secret"}),
                    "s0m0p0",
                ),
            )
            db.commit()
        row = m.plan(self.source, self.target, "mavis")[0]
        self.assertIn("bytes not copied", row["warnings"][0])

    def test_selected_session_only(self):
        r = m.apply(self.source, self.target, "mavis", ["s1"])
        self.assertEqual(r["imported"], 1)
        self.assertEqual(self.count(), 2)

    def test_attachments_fail_closed_without_explicit_opt_in(self):
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute(
                "UPDATE part SET data=? WHERE id=?",
                (json.dumps({"type": "file", "url": "file:///missing"}), "s0m0p0"),
            )
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "Attachments"):
            m.apply(self.source, self.target, "mavis")
        self.assertEqual(self.count(), 1)

    def test_desktop_archive_title_and_deleted_state(self):
        source = self.root / "cli/db/db.sqlite"
        source.parent.mkdir(parents=True)
        source.write_bytes(self.source.read_bytes())
        index = self.root / "v2/tasks-index.sqlite"
        index.parent.mkdir()
        with contextlib.closing(sqlite3.connect(index)) as db:
            db.executescript(
                "CREATE TABLE tasks(task_id TEXT,title TEXT,archived INTEGER,deleted INTEGER); INSERT INTO tasks VALUES('s0','Desktop title',1,0),('s1','deleted',0,1);"
            )
        rows = m.plan(source, self.target, "mavis")
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["archived"])
        self.assertEqual(rows[0]["title"], "[From ZCode] Desktop title")

    def test_post_commit_reporting_failure_keeps_histories(self):
        original = m.private_write

        def fail_report(path, value):
            if path.suffix == ".complete":
                raise OSError("report disk failure")
            return original(path, value)

        with patch.object(m, "private_write", side_effect=fail_report):
            with self.assertRaisesRegex(m.MigrationError, "COMMITTED"):
                m.apply(self.source, self.target, "mavis")
        self.assertEqual(self.count(), 3)
        self.assertEqual(
            len(list((self.target / "v2/sessions").rglob("messages.jsonl"))), 2
        )
        self.assertEqual(
            m.apply(self.source, self.target, "mavis")["status"], "unchanged"
        )

    def test_cli_accepts_zcode_and_rejects_unimplemented_sources(self):
        script = Path(__file__).parents[1] / "scripts/migrate.py"
        accepted = subprocess.run(
            [
                sys.executable,
                "-B",
                str(script),
                "scan",
                "--source",
                "zcode",
                "--source-db",
                str(self.source),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        result = json.loads(accepted.stdout)
        self.assertEqual(result["sourceType"], "zcode")
        self.assertEqual(len(result["sessions"]), 2)
        unsupported = subprocess.run(
            [
                sys.executable,
                "-B",
                str(script),
                "apply",
                "--source",
                "unsupported-agent",
                "--target-data-dir",
                str(self.target),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(unsupported.returncode, 0)
        self.assertEqual(self.count(), 1)
        self.assertFalse((self.target / "zcode-migration").exists())

    def source_message(self, mid, role, text=None, sequence=0, data=None, parts=None):
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute(
                "INSERT INTO message VALUES(?,?,?,?,?)",
                (
                    mid,
                    "s0",
                    1700000000000 + sequence,
                    json.dumps({"role": role, **(data or {})}),
                    sequence,
                ),
            )
            payloads = (
                parts if parts is not None else [{"type": "text", "text": text or mid}]
            )
            for i, part in enumerate(payloads):
                db.execute(
                    "INSERT INTO part VALUES(?,?,?,?,?,?)",
                    (
                        mid + "p" + str(i),
                        mid,
                        "s0",
                        1700000000000 + sequence,
                        json.dumps(part),
                        i,
                    ),
                )
            db.commit()

    def clear_source_messages(self):
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute('DELETE FROM part WHERE session_id="s0"')
            db.execute('DELETE FROM message WHERE session_id="s0"')
            db.commit()

    def converted(self):
        return m.convert(m.load_source(self.source, ["s0"])[0], "mvs-test")

    def canonical_text(self, entries):
        return "\n".join(x["message"]["content"][0]["text"] for x in entries)

    def test_wal_live_target_backup_is_standalone_and_preserves_source_mode(self):
        path = self.target / "v2/sqlite/runtime-state.sqlite"
        with contextlib.closing(sqlite3.connect(path)) as live:
            self.assertEqual(
                live.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal"
            )
            live.execute("SELECT COUNT(*) FROM local_runtime_sessions").fetchone()
            result = m.apply(self.source, self.target, "mavis")
            self.assertEqual(live.execute("PRAGMA journal_mode").fetchone()[0], "wal")
            with m.connect(Path(result["backup"])) as backup:
                self.assertEqual(
                    backup.execute("PRAGMA journal_mode").fetchone()[0], "delete"
                )
                self.assertEqual(
                    backup.execute("PRAGMA quick_check").fetchone()[0], "ok"
                )
                self.assertEqual(
                    backup.execute(
                        "SELECT COUNT(*) FROM local_runtime_sessions"
                    ).fetchone()[0],
                    1,
                )
            self.assertEqual(
                m.apply(self.source, self.target, "mavis")["status"], "unchanged"
            )

    def test_legacy_zero_rows_preserved_byte_for_byte(self):
        path = self.target / "v2/sqlite/runtime-state.sqlite"
        raw = json.dumps(
            {
                "sessionId": "real-legacy",
                "agentName": "mavis",
                "title": "真实历史",
                "sessionDataVersion": 4,
            },
            ensure_ascii=False,
        )
        with contextlib.closing(sqlite3.connect(path)) as db:
            db.execute(
                "INSERT INTO local_runtime_sessions(session_id,columnar_version,record_json,extra_data_json) VALUES(?,0,?,?)",
                ("real-legacy", raw, "{}"),
            )
            db.commit()
            before = db.execute(
                'SELECT * FROM local_runtime_sessions WHERE session_id="real-legacy"'
            ).fetchone()
        result = m.apply(self.source, self.target, "mavis")
        self.assertTrue(any("legacy" in w for w in result["sessions"][0]["warnings"]))
        with contextlib.closing(sqlite3.connect(path)) as db:
            self.assertEqual(
                db.execute(
                    'SELECT * FROM local_runtime_sessions WHERE session_id="real-legacy"'
                ).fetchone(),
                before,
            )
        self.assertEqual(self.count(), 4)

    def test_legacy_identity_corruption_and_future_columnar_are_rejected(self):
        path = self.target / "v2/sqlite/runtime-state.sqlite"
        with contextlib.closing(sqlite3.connect(path)) as db:
            db.execute(
                'INSERT INTO local_runtime_sessions(session_id,columnar_version,record_json,extra_data_json) VALUES("legacy",0,?,"{}")',
                (json.dumps({"sessionId": "different"}),),
            )
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "legacy session identity"):
            m.apply(self.source, self.target, "mavis")
        with contextlib.closing(sqlite3.connect(path)) as db:
            db.execute(
                'UPDATE local_runtime_sessions SET columnar_version=4 WHERE session_id="legacy"'
            )
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "columnar version"):
            m.apply(self.source, self.target, "mavis")

    def test_rewind_excludes_abandoned_branch_from_display_and_context(self):
        self.clear_source_messages()
        for i, mid in enumerate(["u0", "a0", "u1", "a1", "u2", "a2"]):
            self.source_message(
                mid, "user" if mid.startswith("u") else "assistant", sequence=i
            )
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute(
                'UPDATE session SET revert=? WHERE id="s0"',
                (
                    json.dumps(
                        {
                            "targetMessageID": "u1",
                            "keptMessageIDs": ["u0", "a0"],
                            "branchCutAfterMessageID": "a1",
                        }
                    ),
                ),
            )
            db.commit()
        display, canonical, _ = self.converted()
        self.assertEqual([x["msg_content"] for x in display], ["u0", "a0", "u2", "a2"])
        self.assertEqual(self.canonical_text(canonical), "u0\na0\nu2\na2")

    def test_compaction_preserved_segment_order_and_display_archive(self):
        self.clear_source_messages()
        self.source_message("u0", "user", sequence=0)
        self.source_message("a0", "assistant", sequence=1)
        self.source_message("u1", "user", sequence=2)
        self.source_message("a1", "assistant", sequence=3)
        self.source_message(
            "boundary",
            "user",
            sequence=4,
            parts=[
                {
                    "type": "compaction",
                    "auto": True,
                    "compactBoundary": {
                        "summaryMessageIds": ["summary"],
                        "preservedSegment": {
                            "headMessageId": "u1",
                            "tailMessageId": "a1",
                            "anchorMessageId": "summary",
                        },
                    },
                }
            ],
        )
        self.source_message(
            "summary", "assistant", "SUMMARY", sequence=5, data={"summary": True}
        )
        self.source_message("tail", "user", sequence=6)
        display, canonical, _ = self.converted()
        text = self.canonical_text(canonical)
        self.assertNotIn("u0", text)
        self.assertNotIn("a0", text)
        self.assertEqual(
            [x["message"]["content"][0]["text"] for x in canonical][1:],
            ["u1", "a1", "tail"],
        )
        self.assertIn("SUMMARY", text)
        self.assertEqual(display[0]["displayKind"], "zcode_history_archive")
        self.assertNotIn(
            "displayKind", next(x for x in display if x["msg_content"] == "u1")
        )

    def test_missing_rewind_boundary_fails_before_write(self):
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute(
                'UPDATE session SET revert=? WHERE id="s0"',
                (json.dumps({"targetMessageID": "missing"}),),
            )
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "boundary reference"):
            m.apply(self.source, self.target, "mavis")
        self.assertEqual(self.count(), 1)

    def test_visibility_ignored_and_provider_only_context_are_distinct(self):
        self.clear_source_messages()
        self.source_message("real", "user", "REAL", sequence=0)
        self.source_message(
            "hidden", "user", "HIDDEN", sequence=1, data={"synthetic": True}
        )
        self.source_message(
            "context", "user", "CONTEXT", sequence=2, data={"visibility": "model-only"}
        )
        self.source_message(
            "reply",
            "assistant",
            sequence=3,
            parts=[
                {"type": "text", "text": "IGNORED", "ignored": True},
                {"type": "text", "text": "VISIBLE"},
                {"type": "reasoning", "text": "THOUGHT"},
            ],
        )
        display, canonical, _ = self.converted()
        self.assertEqual([x["msg_content"] for x in display], ["REAL", "VISIBLE"])
        text = self.canonical_text(canonical)
        self.assertNotIn("HIDDEN", text)
        self.assertNotIn("IGNORED", text)
        self.assertNotIn("THOUGHT", text)
        self.assertIn("CONTEXT", text)
        self.assertIn("不是当前任务指令", text)
        self.assertTrue(canonical[0]["message_id"].startswith("msg-user-v1-"))
        self.assertFalse(canonical[1]["message_id"].startswith("msg-user-v1-"))

    def test_nested_tool_attachment_blocks_and_preserves_reference_when_accepted(self):
        self.clear_source_messages()
        part = {
            "type": "tool",
            "tool": "read",
            "callID": "c1",
            "state": {
                "status": "completed",
                "input": {},
                "output": "screenshot",
                "attachments": [
                    {"type": "file", "mime": "image/png", "url": "artifact://图.png"}
                ],
                "metadata": {
                    "modelContentLayout": [{"type": "attachment", "index": 0}]
                },
            },
        }
        self.source_message("tool", "assistant", parts=[part])
        with self.assertRaisesRegex(m.MigrationError, "Attachments"):
            m.apply(self.source, self.target, "mavis")
        result = m.apply(self.source, self.target, "mavis", allow_references=True)
        row = next(x for x in result["sessions"] if x["sourceId"] == "s0")
        history = (
            self.target / "v2/sessions" / row["historyRelativeDir"] / "messages.jsonl"
        ).read_text(encoding="utf-8")
        self.assertIn("artifact://图.png", history)
        self.assertIn("modelContentLayout", history)
        self.assertTrue(row["warnings"])

    def test_native_search_index_matches_unicode_title_immediately(self):
        result = m.apply(self.source, self.target, "mavis")
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            query = '"' + m.search_terms("[From ZCode] 中文标题 0") + '"'
            rows = db.execute(
                "SELECT session_id FROM local_runtime_sessions_fts WHERE local_runtime_sessions_fts MATCH ?",
                (query,),
            ).fetchall()
            self.assertEqual(rows, [(result["sessions"][0]["targetId"],)])

    def test_rollback_removes_search_documents(self):
        with self.assertRaises(m.MigrationError):
            m.apply(self.source, self.target, "mavis", fail_after=1)
        with contextlib.closing(
            sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite")
        ) as db:
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(*) FROM local_runtime_sessions_fts"
                ).fetchone()[0],
                0,
            )
            self.assertEqual(
                db.execute(
                    "SELECT COUNT(*) FROM local_runtime_session_fts_keys"
                ).fetchone()[0],
                0,
            )

    def test_removed_project_requires_opt_in_and_does_not_reveal_old_sessions(self):
        path = self.target / "v2/sqlite/runtime-state.sqlite"
        with contextlib.closing(sqlite3.connect(path)) as db:
            db.execute(
                'INSERT INTO local_runtime_projects(project_id,project_kind,workspace_dir,created_at_ms,updated_at_ms,hidden,extra_data_json) VALUES(1,"workspace",?,1,1800000000000,1,?)',
                (str(self.cwd.resolve()), json.dumps({"keep": "value"})),
            )
            db.execute(
                'UPDATE local_runtime_sessions SET project_id=1,created_at_ms=1800000000000 WHERE session_id="existing"'
            )
            db.commit()
        with self.assertRaisesRegex(m.MigrationError, "restore-projects"):
            m.apply(self.source, self.target, "mavis")
        result = m.apply(self.source, self.target, "mavis", restore_projects=True)
        with contextlib.closing(sqlite3.connect(path)) as db:
            hidden, extra = db.execute(
                "SELECT hidden,extra_data_json FROM local_runtime_projects WHERE project_id=1"
            ).fetchone()
            extra = json.loads(extra)
            self.assertEqual(hidden, 0)
            self.assertEqual(extra["keep"], "value")
            boundary = extra["sidebarRemoval"]
            self.assertIn("existing", boundary["boundaryIds"])
            for row in result["sessions"]:
                created = db.execute(
                    "SELECT created_at_ms FROM local_runtime_sessions WHERE session_id=?",
                    (row["targetId"],),
                ).fetchone()[0]
                self.assertGreater(created, boundary["atMs"])
                marker = json.loads(
                    (
                        self.target
                        / "v2/sessions"
                        / row["historyRelativeDir"]
                        / "zcode-migration.json"
                    ).read_text(encoding="utf-8")
                )
                self.assertLess(marker["sourceCreatedAtMs"], boundary["atMs"])
        self.assertEqual(
            m.apply(self.source, self.target, "mavis")["status"], "unchanged"
        )

    def test_legacy_import_is_not_rewritten_by_new_adapter(self):
        result = m.apply(self.source, self.target, "mavis")
        row = result["sessions"][0]
        directory = self.target / "v2/sessions" / row["historyRelativeDir"]
        marker = directory / "zcode-migration.json"
        provenance = json.loads(marker.read_text(encoding="utf-8"))
        provenance.pop("adapterVersion")
        marker.write_text(json.dumps(provenance, ensure_ascii=False), encoding="utf-8")
        before = (directory / "messages.jsonl").read_bytes()
        repeated = m.apply(self.source, self.target, "mavis")
        self.assertEqual(repeated["status"], "unchanged")
        self.assertEqual((directory / "messages.jsonl").read_bytes(), before)
        self.assertTrue(
            any("older adapter" in w for w in repeated["sessions"][0]["warnings"])
        )

    def test_non_utf8_cli_and_unicode_profile_round_trip(self):
        workspace = self.root / "项目 文件夹 🐈"
        workspace.mkdir()
        script = Path(__file__).parents[1] / "scripts/migrate.py"
        env = {**os.environ, "PYTHONIOENCODING": "gbk", "PYTHONUTF8": "0"}
        command = [
            sys.executable,
            "-B",
            str(script),
            "apply",
            "--source-db",
            str(self.source),
            "--target-data-dir",
            str(self.target),
            "--workspace",
            str(workspace),
        ]
        report = self.root / "unicode-job.json"
        command += ["--session", "s0", "--session", "s1", "--report", str(report)]
        preview = command.copy()
        preview[3] = "plan"
        completed = subprocess.run(preview, capture_output=True, env=env)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        for attempt in range(2):
            completed = subprocess.run(command, capture_output=True, env=env)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout.decode("ascii"))
            rows = json.loads(report.read_text(encoding="utf-8"))["sessions"]
            self.assertEqual(rows[0]["plan"]["title"], "[From ZCode] 中文标题 0")
            self.assertEqual(result["status"], "completed")
            self.assertEqual(self.count(), 3)

    def test_windows_reparse_point_rejected_without_symlink_flag(self):
        point = SimpleNamespace(
            is_symlink=lambda: False,
            lstat=lambda: SimpleNamespace(st_file_attributes=0x400),
        )
        self.assertTrue(m.is_link(point))

    def test_wal_source_includes_committed_uncheckpointed_messages(self):
        with contextlib.closing(sqlite3.connect(self.source)) as live:
            live.execute("PRAGMA journal_mode=WAL")
            live.execute("PRAGMA wal_autocheckpoint=0")
            live.execute(
                "UPDATE part SET data=? WHERE id='s0m0p0'",
                (json.dumps({"type": "text", "text": "Only in WAL 中文"}),),
            )
            live.commit()
            before = self.source.read_bytes()
            result = m.apply(self.source, self.target, "mavis")
            row = result["sessions"][0]
            history = (
                self.target
                / "v2/sessions"
                / row["historyRelativeDir"]
                / "messages.jsonl"
            )
            self.assertIn("Only in WAL 中文", history.read_text(encoding="utf-8"))
            self.assertEqual(self.source.read_bytes(), before)

    def test_removed_project_restore_rolls_back_with_failed_import(self):
        path = self.target / "v2/sqlite/runtime-state.sqlite"
        with contextlib.closing(sqlite3.connect(path)) as db:
            db.execute(
                "INSERT INTO local_runtime_projects(project_kind,workspace_dir,created_at_ms,updated_at_ms,hidden,extra_data_json) VALUES('workspace',?,1,2,1,'{}')",
                (str(self.cwd.resolve()),),
            )
            db.commit()
            before = db.execute("SELECT * FROM local_runtime_projects").fetchall()
        with self.assertRaisesRegex(m.MigrationError, "Injected"):
            m.apply(
                self.source, self.target, "mavis", restore_projects=True, fail_after=1
            )
        with contextlib.closing(sqlite3.connect(path)) as db:
            self.assertEqual(
                db.execute("SELECT * FROM local_runtime_projects").fetchall(), before
            )
        self.assertEqual(self.count(), 1)

    def test_rewind_kept_prefix_before_compaction_does_not_resurrect_it(self):
        self.clear_source_messages()
        self.source_message("old", "user", sequence=0)
        self.source_message("target", "user", sequence=1)
        self.source_message(
            "boundary", "user", sequence=2, parts=[{"type": "compaction"}]
        )
        self.source_message("summary", "assistant", sequence=3, data={"summary": True})
        self.source_message("new", "user", sequence=4)
        with contextlib.closing(sqlite3.connect(self.source)) as db:
            db.execute(
                "UPDATE session SET revert=? WHERE id='s0'",
                (
                    json.dumps(
                        {
                            "targetMessageID": "target",
                            "keptMessageIDs": ["old"],
                            "createdMessageID": "new",
                        }
                    ),
                ),
            )
            db.commit()
        display, canonical, _ = self.converted()
        self.assertEqual([x["msg_content"] for x in display], ["old", "new"])
        self.assertEqual(display[0]["displayKind"], "zcode_history_archive")
        self.assertNotIn("old", self.canonical_text(canonical))
        self.assertIn("summary", self.canonical_text(canonical))

    def test_invalid_metadata_is_rejected_before_any_import(self):
        self.clear_source_messages()
        self.source_message("invalid", "user", data={"metadata": ["unknown"]})
        with self.assertRaisesRegex(m.MigrationError, "metadata"):
            m.apply(self.source, self.target, "mavis")
        self.assertEqual(self.count(), 1)


if __name__ == "__main__":
    unittest.main()
