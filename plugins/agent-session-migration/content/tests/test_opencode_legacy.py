"""Synthetic OpenCode 1.x SQLite histories, independent of private databases."""

import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "legacy_base", Path(__file__).with_name("test_opencode_migration.py")
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
m = base.m
SCHEMA = """
CREATE TABLE session(id TEXT PRIMARY KEY,title TEXT,directory TEXT,version TEXT,time_created INTEGER,time_updated INTEGER,time_archived INTEGER,revert TEXT,parent_id TEXT);
CREATE TABLE message(id TEXT PRIMARY KEY,session_id TEXT,time_created INTEGER,data TEXT);
CREATE TABLE part(id TEXT PRIMARY KEY,message_id TEXT,session_id TEXT,data TEXT);
CREATE TABLE session_message(session_id TEXT,type TEXT);
"""


class LegacyOpenCodeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.cwd = self.root / "workspace"
        self.cwd.mkdir()
        self.source = self.root / "opencode.db"
        self.target = self.root / "target"
        (self.target / "v2/sqlite").mkdir(parents=True)
        with sqlite3.connect(self.source) as db:
            db.executescript(SCHEMA)
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            db.executescript(base.base.TARGET_SCHEMA)
        self.sid = "ses_legacy"
        self.write_session(self.sid)
        m.use("opencode")

    def tearDown(self):
        self.temp.cleanup()

    def write_session(self, sid):
        with sqlite3.connect(self.source) as db:
            db.execute(
                "INSERT INTO session VALUES (?,?,?,'1.18.32',1700000000000,1700000001000,NULL,NULL,NULL)",
                (sid, "旧结构", str(self.cwd)),
            )
            db.execute(
                "INSERT INTO session_message VALUES (?, 'model-switched')", (sid,)
            )
        self.add("u1", "user", [{"type": "text", "text": "REQUEST-73"}], 1, sid=sid)
        self.add(
            "a1",
            "assistant",
            [{"type": "text", "text": "DECISION-42"}],
            2,
            sid=sid,
            parentID=sid + "u1",
        )

    def add(self, uid, role, parts, seq, sid=None, **extra):
        sid = sid or self.sid
        info = {
            "role": role,
            "time": {"created": 1700000000000 + seq, "completed": 1700000000000 + seq},
            **extra,
        }
        with sqlite3.connect(self.source) as db:
            db.execute(
                "INSERT INTO message VALUES (?,?,?,?)",
                (sid + uid, sid, 1700000000000 + seq, json.dumps(info)),
            )
            for i, p in enumerate(parts):
                db.execute(
                    "INSERT INTO part VALUES (?,?,?,?)",
                    (sid + uid + str(i), sid + uid, sid, json.dumps(p)),
                )

    def item(self):
        return m.adapter()["load_source"](self.source, [self.sid])[0]

    def compact(self, suffix, seq, tail=None, error=False):
        marker = {"type": "compaction", "auto": True}
        if tail:
            marker["tail_start_id"] = self.sid + tail
        self.add("c" + suffix, "user", [marker], seq)
        self.add(
            "s" + suffix,
            "assistant",
            [{"type": "text", "text": "SUMMARY-" + suffix}],
            seq + 1,
            summary=True,
            parentID=self.sid + "c" + suffix,
            finish="stop",
            **({"error": {"name": "APIError"}} if error else {}),
        )

    def test_plain_readonly_lifecycle_title_and_idempotent(self):
        before = self.source.read_bytes()
        first = m.apply(self.source, self.target, "mavis", ids=[self.sid])
        self.assertEqual(first["sessions"][0]["messageCount"], 2)
        self.assertEqual(
            m.apply(self.source, self.target, "mavis", ids=[self.sid])["status"],
            "unchanged",
        )
        self.assertEqual(before, self.source.read_bytes())
        self.assertNotIn("model-switched", json.dumps(self.item()))
        with sqlite3.connect(self.source) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                "UPDATE session SET title=NULL,time_archived=1700000000001,version='1.14.0'"
            )
            db.commit()
            self.assertTrue(self.item()["desktop"]["archived"])
            self.assertEqual(self.item()["desktop"]["title"], "REQUEST-73")

    def test_two_compactions_retained_tail_order_and_old_display(self):
        self.compact("1", 3)
        self.add("u2", "user", [{"type": "text", "text": "LATEST-CORRECTION"}], 5)
        self.add(
            "a2",
            "assistant",
            [{"type": "text", "text": "KEEP-THIS"}],
            6,
            parentID=self.sid + "u2",
        )
        self.compact("2", 7, tail="u2")
        item = self.item()
        self.assertEqual(
            item["histories"]["active"],
            [self.sid + "s2", self.sid + "u2", self.sid + "a2"],
        )
        display, canonical, _ = m.convert(item, "target")
        self.assertIn("DECISION-42", json.dumps(display))
        self.assertNotIn("DECISION-42", json.dumps(canonical))
        self.assertNotIn("SUMMARY-1", json.dumps(canonical))
        self.assertIn("LATEST-CORRECTION", json.dumps(canonical))

    def test_failed_compaction_retains_history_and_bad_tail_fails(self):
        self.compact("1", 3, error=True)
        self.assertIn(self.sid + "u1", self.item()["histories"]["active"])
        self.compact("2", 5, tail="missing")
        with self.assertRaisesRegex(m.MigrationError, "tail"):
            self.item()

    def test_incomplete_and_revert_rejected(self):
        self.add("c1", "user", [{"type": "compaction", "auto": True}], 3)
        with self.assertRaisesRegex(m.MigrationError, "no result"):
            self.item()
        with sqlite3.connect(self.source) as db:
            db.execute("DELETE FROM part WHERE message_id=?", (self.sid + "c1",))
            db.execute("DELETE FROM message WHERE id=?", (self.sid + "c1",))
            db.execute("UPDATE session SET revert='{}'")
        with self.assertRaisesRegex(m.MigrationError, "revert"):
            self.item()

    def test_tools_pruning_and_credentials_filtered(self):
        self.add(
            "a2",
            "assistant",
            [
                {
                    "type": "tool",
                    "tool": "bash",
                    "callID": "call1",
                    "state": {
                        "status": "completed",
                        "input": {"command": "echo ok"},
                        "output": "PRUNED-SECRET",
                        "time": {"compacted": 1},
                        "metadata": {"token": "SECRET"},
                    },
                },
                {
                    "type": "reasoning",
                    "text": "THINK",
                    "metadata": {"signature": "SIGNATURE"},
                },
            ],
            3,
            parentID=self.sid + "u1",
            system="SYSTEM-SECRET",
        )
        item = self.item()
        display, canonical, _ = m.convert(item, "target")
        self.assertIn("历史工具记录", json.dumps(display, ensure_ascii=False))
        for secret in ["PRUNED-SECRET", "SYSTEM-SECRET", "SIGNATURE", '"token"']:
            self.assertNotIn(secret, json.dumps(item))
        self.assertNotIn("THINK", json.dumps(canonical))

    def test_attachment_text_and_binary_optin(self):
        self.add(
            "u2",
            "user",
            [
                {
                    "type": "file",
                    "mime": "text/plain",
                    "filename": "readme",
                    "url": "data:text/plain;base64,VEVYVC03Mw==",
                }
            ],
            3,
        )
        self.assertIn("TEXT-73", json.dumps(self.item()))
        self.add(
            "u3",
            "user",
            [{"type": "file", "mime": "image/png", "url": "file:///unread.png"}],
            4,
        )
        with self.assertRaises(m.MigrationError):
            m.apply(self.source, self.target, "mavis", ids=[self.sid])
        m.apply(
            self.source, self.target, "mavis", ids=[self.sid], allow_references=True
        )

    def test_ambiguous_layout_and_mixed_event_table_rejected(self):
        with sqlite3.connect(self.source) as db:
            db.execute(
                "INSERT INTO session_message VALUES (?, 'assistant')", (self.sid,)
            )
        with self.assertRaisesRegex(m.MigrationError, "mixed"):
            self.item()
        with sqlite3.connect(self.source) as db:
            db.execute("CREATE TABLE session_v2(id TEXT)")
        with self.assertRaisesRegex(m.MigrationError, "schema"):
            self.item()

    def test_orphan_identity_unknown_part_and_windows_workspace(self):
        with sqlite3.connect(self.source) as db:
            db.execute("UPDATE session SET directory=?", ("F:\\projects\\demo",))
        self.assertEqual(self.item()["session"]["directory"], "F:\\projects\\demo")
        self.add("u2", "user", [{"type": "future-format"}], 3)
        with self.assertRaisesRegex(m.MigrationError, "Unsupported"):
            self.item()
        with sqlite3.connect(self.source) as db:
            db.execute(
                "UPDATE part SET session_id='wrong' WHERE message_id=?",
                (self.sid + "u2",),
            )
        with self.assertRaisesRegex(m.MigrationError, "Orphan"):
            self.item()


if __name__ == "__main__":
    unittest.main()
