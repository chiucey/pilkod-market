"""OpenCode V2 synthetic fixtures, with no private user history."""

import base64
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "opencode_test_core", HERE / "test_codex_migration.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
m = base.m

SCHEMA = """
CREATE TABLE session_v2(id TEXT PRIMARY KEY,title TEXT,directory TEXT,version TEXT,
 time_created INTEGER,time_updated INTEGER,time_archived INTEGER,revert TEXT,
 parent_id TEXT,fork_session_id TEXT,fork_boundary TEXT,time_compacting INTEGER);
CREATE TABLE session_message(id TEXT,session_id TEXT,type TEXT,seq INTEGER,time_created INTEGER,data TEXT);
"""


class OpenCodeMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.cwd = self.root / "workspace"
        self.cwd.mkdir()
        self.source = self.root / "opencode.db"
        with sqlite3.connect(self.source) as db:
            db.executescript(SCHEMA)
        self.target = self.root / "target"
        (self.target / "v2/sqlite").mkdir(parents=True)
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            db.executescript(base.TARGET_SCHEMA)
        self.sid = "ses_test"
        self.write_session(self.sid)
        m.use("opencode")

    def tearDown(self):
        self.temp.cleanup()

    def write_session(self, sid):
        with sqlite3.connect(self.source) as db:
            db.execute(
                "INSERT INTO session_v2 VALUES (?,?,?,'2.0.10',1700000000000,1700000001000,NULL,NULL,NULL,NULL,NULL,NULL)",
                (sid, "OpenCode 测试", str(self.cwd)),
            )
        self.add("u1", "user", {"text": "REQUEST-73"}, 1, sid)
        self.add(
            "a1",
            "assistant",
            {
                "time": {"completed": 1700000000100},
                "content": [{"type": "text", "text": "DECISION-42"}],
            },
            2,
            sid,
        )

    def add(self, uid, typ, data, seq, sid=None):
        with sqlite3.connect(self.source) as db:
            db.execute(
                "INSERT INTO session_message VALUES (?,?,?,?,?,?)",
                (
                    (sid or self.sid) + uid,
                    sid or self.sid,
                    typ,
                    seq,
                    1700000000000 + seq,
                    json.dumps(data),
                ),
            )

    def update(self, uid, data):
        with sqlite3.connect(self.source) as db:
            db.execute(
                "UPDATE session_message SET data=? WHERE id=?",
                (json.dumps(data), self.sid + uid),
            )

    def item(self):
        return m.adapter()["load_source"](self.source, [self.sid])[0]

    def converted(self):
        return m.convert(self.item(), "test-target")

    def test_readonly_storage_title_fallback_archive_and_wal(self):
        before = self.source.read_bytes()
        result = m.apply(self.source, self.target, "mavis", ids=[self.sid])
        self.assertEqual(
            result["sessions"][0]["title"], "[From OpenCode] OpenCode 测试"
        )
        self.assertEqual(
            m.apply(self.source, self.target, "mavis", ids=[self.sid])["status"],
            "unchanged",
        )
        self.assertEqual(before, self.source.read_bytes())
        with sqlite3.connect(self.source) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("UPDATE session_v2 SET title=NULL,time_archived=1700000000200")
            db.commit()
            self.assertTrue(self.item()["desktop"]["archived"])
            self.assertEqual(self.item()["desktop"]["title"], "REQUEST-73")

    def test_two_compactions_keep_full_display_and_latest_summary(self):
        self.add(
            "c1",
            "compaction",
            {"status": "completed", "summary": "OLD-SUMMARY", "recent": "OLD-RECENT"},
            3,
        )
        self.add("u2", "user", {"text": "MID-HISTORY"}, 4)
        self.add(
            "c2",
            "compaction",
            {
                "status": "completed",
                "summary": "CURRENT-SUMMARY",
                "recent": "RECENT-DECISION",
            },
            5,
        )
        self.add("u3", "user", {"text": "LATEST-CORRECTION"}, 6)
        display, active, _ = self.converted()
        self.assertIn("MID-HISTORY", json.dumps(display))
        for text in ["CURRENT-SUMMARY", "RECENT-DECISION", "LATEST-CORRECTION"]:
            self.assertIn(text, json.dumps(active))
        for text in ["OLD-SUMMARY", "MID-HISTORY", "REQUEST-73"]:
            self.assertNotIn(text, json.dumps(active))

    def test_failed_and_opaque_compaction(self):
        self.add("c1", "compaction", {"status": "failed"}, 3)
        self.assertIn("REQUEST-73", json.dumps(self.converted()[1]))
        for data in [
            {"status": "running"},
            {"status": "completed", "summary": "", "recent": ""},
            {
                "status": "completed",
                "summary": "readable",
                "recent": "",
                "providerContext": {"opaque": "SECRET"},
            },
        ]:
            self.update("c1", data)
            with self.assertRaises(m.MigrationError):
                self.item()

    def test_inline_text_and_binary_attachments_do_not_read_external_paths(self):
        self.update(
            "u1",
            {
                "text": "REQUEST",
                "files": [
                    {
                        "mime": "text/plain",
                        "name": "input.txt",
                        "data": base64.b64encode(b"TEXT-FILE-EVIDENCE").decode(),
                    },
                    {
                        "mime": "image/png",
                        "name": "image.png",
                        "data": "PRIVATE-BINARY",
                    },
                    {
                        "mime": "text/plain",
                        "name": "remote.txt",
                        "uri": "https://invalid.example/no-fetch",
                    },
                ],
            },
        )
        result = json.dumps(self.converted()[:2])
        self.assertIn("TEXT-FILE-EVIDENCE", result)
        self.assertNotIn("PRIVATE-BINARY", result)
        self.update(
            "u1",
            {
                "text": "REQUEST",
                "files": [{"mime": "text/plain", "name": "bad.txt", "data": "!bad"}],
            },
        )
        with self.assertRaises(m.MigrationError):
            self.item()

    def test_binary_attachment_requires_reference_only_opt_in(self):
        self.update(
            "u1",
            {
                "text": "REQUEST",
                "files": [
                    {"name": "image.png", "mime": "image/png", "data": "NOT-COPIED"}
                ],
            },
        )
        with self.assertRaises(m.MigrationError):
            m.apply(self.source, self.target, "mavis", ids=[self.sid])
        result = m.apply(
            self.source, self.target, "mavis", ids=[self.sid], allow_references=True
        )
        self.assertEqual(result["status"], "imported")

    def test_tool_states_inert_cards_and_reasoning_metadata(self):
        tools = []
        for i, status in enumerate(["completed", "error", "running", "streaming"]):
            tools.append(
                {
                    "type": "tool",
                    "id": str(i),
                    "name": "exec",
                    "state": {
                        "status": status,
                        "input": "{"
                        if status == "streaming"
                        else {"cmd": "DO-NOT-EXECUTE"},
                        "content": [{"type": "text", "text": "OUTPUT-" + status}],
                    },
                    "providerState": {"encrypted": "SECRET"},
                }
            )
        self.update(
            "a1",
            {
                "time": {"completed": 1700000000010},
                "content": [
                    {
                        "type": "reasoning",
                        "text": "THOUGHT",
                        "state": {"signature": "SECRET"},
                    },
                    *tools,
                ],
            },
        )
        display, active, _ = self.converted()
        self.assertNotIn("SECRET", json.dumps([display, active]))
        self.assertNotIn("THOUGHT", json.dumps(active))
        for status in ["completed", "error", "running", "streaming"]:
            self.assertIn("OUTPUT-" + status, json.dumps(active))
        self.assertIn("历史工具记录", json.dumps(display, ensure_ascii=False))

    def test_fork_uses_own_projection_not_parent_and_metadata_not_live(self):
        self.write_session("ses_parent")
        with sqlite3.connect(self.source) as db:
            db.execute(
                "UPDATE session_v2 SET fork_session_id='ses_parent',fork_boundary=? WHERE id=?",
                (
                    json.dumps({"type": "after", "messageID": "parent-message"}),
                    self.sid,
                ),
            )
            db.execute(
                "UPDATE session_message SET data=? WHERE session_id='ses_parent' AND type='user'",
                (json.dumps({"text": "PARENT-FUTURE"}),),
            )
        for i, typ in enumerate(
            [
                "system",
                "skill",
                "agent-switched",
                "model-switched",
                "location-switched",
                "idle",
            ]
        ):
            self.add("meta" + str(i), typ, {"text": "HOST-SECRET"}, 10 + i)
        result = json.dumps(self.converted()[:2])
        self.assertNotIn("PARENT-FUTURE", result)
        self.assertNotIn("HOST-SECRET", result)

    def test_staged_revert_incomplete_unknown_and_malformed_block_fail(self):
        with sqlite3.connect(self.source) as db:
            db.execute("UPDATE session_v2 SET revert='{}'")
        with self.assertRaises(m.MigrationError):
            self.item()
        with sqlite3.connect(self.source) as db:
            db.execute("UPDATE session_v2 SET revert=NULL")
        for data in [
            {"time": {}, "content": []},
            {"time": {"completed": 1}, "content": [None]},
            {"time": {"completed": 1}, "content": [{"type": "unknown"}]},
            {"id": "WRONG", "time": {"completed": 1}, "content": []},
        ]:
            self.update("a1", data)
            with self.assertRaises(m.MigrationError):
                self.item()

    def test_shell_and_background_projection(self):
        data = {
            "shellID": "shell1",
            "command": "echo evidence",
            "status": "exited",
            "exit": 0,
            "output": {
                "output": "SHELL-EVIDENCE",
                "size": 14,
                "cursor": 14,
                "truncated": False,
            },
        }
        self.add("shell", "shell", data, 3)
        self.assertIn("SHELL-EVIDENCE", json.dumps(self.converted()[1]))
        data["metadata"] = {"background": True}
        self.update("shell", data)
        display, active, _ = self.converted()
        self.assertIn("SHELL-EVIDENCE", json.dumps(display))
        self.assertNotIn("SHELL-EVIDENCE", json.dumps(active))

    def test_unsupported_schema_version_sequence_and_source_changes(self):
        with sqlite3.connect(self.source) as db:
            db.execute("UPDATE session_v2 SET version='1.9.0'")
        with self.assertRaises(m.MigrationError):
            self.item()
        with sqlite3.connect(self.source) as db:
            db.execute("UPDATE session_v2 SET version='2.0.10'")
            db.execute("UPDATE session_message SET seq=1")
        with self.assertRaises(m.MigrationError):
            self.item()
        other = self.root / "legacy.db"
        with sqlite3.connect(other) as db:
            db.execute("CREATE TABLE session(id TEXT)")
        with self.assertRaises(m.MigrationError):
            m.adapter()["inventory"](other)


if __name__ == "__main__":
    unittest.main()
