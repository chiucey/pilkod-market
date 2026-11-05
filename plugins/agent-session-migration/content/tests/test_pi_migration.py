"""Pi V3 trees and compaction fixtures; no private source transcripts."""

import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "pi_test_core", HERE / "test_codex_migration.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
m = base.m


class PiMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.cwd = self.root / "workspace"
        self.cwd.mkdir()
        self.source = self.root / "sessions"
        self.project = self.source / "--project--"
        self.project.mkdir(parents=True)
        self.target = self.root / "target"
        (self.target / "v2/sqlite").mkdir(parents=True)
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            db.executescript(base.TARGET_SCHEMA)
        self.sid = "custom-pi-id"
        self.write_session(self.sid)
        m.use("pi-agent")

    def tearDown(self):
        self.temp.cleanup()

    def row(self, uid, parent, typ="message", **values):
        return {
            "type": typ,
            "id": uid,
            "parentId": parent,
            "timestamp": "2026-09-20T01:00:00Z",
            **values,
        }

    def message(self, uid, parent, role, content, **values):
        return self.row(
            uid,
            parent,
            message={
                "role": role,
                "content": content,
                **({"stopReason": "stop"} if role == "assistant" else {}),
                **values,
            },
        )

    def write_session(self, sid):
        self.write(
            [
                self.message("u1", None, "user", "REQUEST-73"),
                self.message(
                    "a1", "u1", "assistant", [{"type": "text", "text": "DECISION-42"}]
                ),
            ],
            sid,
        )

    def path(self, sid=None):
        return self.project / ("date_" + (sid or self.sid) + ".jsonl")

    def write(self, rows, sid=None):
        header = {
            "type": "session",
            "version": 3,
            "id": sid or self.sid,
            "cwd": str(self.cwd),
            "timestamp": "2026-09-20T01:00:00Z",
        }
        self.path(sid).write_text(
            "\n".join(json.dumps(r) for r in [header, *rows]) + "\n"
        )

    def rows(self):
        return [json.loads(l) for l in self.path().read_text().splitlines()][1:]

    def item(self):
        return m.adapter()["load_source"](self.source, [self.sid])[0]

    def converted(self):
        return m.convert(self.item(), "test-target")

    def test_readonly_identity_title_and_repeat(self):
        rows = self.rows() + [self.row("name", "a1", "session_info", name="Pi named")]
        self.write(rows)
        before = self.path().read_bytes()
        r = m.apply(self.source, self.target, "mavis", ids=[self.sid])
        self.assertEqual(r["sessions"][0]["title"], "[From Pi] Pi named")
        self.assertEqual(
            m.apply(self.source, self.target, "mavis", ids=[self.sid])["status"],
            "unchanged",
        )
        self.assertEqual(before, self.path().read_bytes())
        self.assertEqual(m.adapter()["source_path"](self.root), self.source)

    def test_current_branch_excludes_abandoned_messages(self):
        rows = self.rows() + [
            self.message("abandoned", "a1", "user", "ABANDONED"),
            self.row(
                "branch",
                "u1",
                "branch_summary",
                fromId="abandoned",
                summary="BRANCH-LESSON",
            ),
            self.message(
                "new", "branch", "assistant", [{"type": "text", "text": "NEW"}]
            ),
        ]
        self.write(rows)
        display, active, _ = self.converted()
        self.assertNotIn("ABANDONED", json.dumps([display, active]))
        self.assertNotIn("DECISION-42", json.dumps(active))
        self.assertIn("BRANCH-LESSON", json.dumps(active))

    def test_two_compactions_summary_before_retained_range(self):
        rows = self.rows() + [
            self.row(
                "c1", "a1", "compaction", firstKeptEntryId="a1", summary="OLD-SUMMARY"
            ),
            self.message("u2", "c1", "user", "RETAIN-THIS"),
            self.message(
                "a2", "u2", "assistant", [{"type": "text", "text": "MID-REPLY"}]
            ),
            self.row(
                "c2",
                "a2",
                "compaction",
                firstKeptEntryId="u2",
                summary="CURRENT-SUMMARY",
                systemMessage={"role": "system", "content": "SECRET"},
            ),
            self.message("u3", "c2", "user", "LATEST"),
        ]
        self.write(rows)
        item = self.item()
        self.assertEqual(item["histories"]["active"], ["c2", "u2", "a2", "u3"])
        display, active, _ = self.converted()
        self.assertIn("DECISION-42", json.dumps(display))
        self.assertNotIn("OLD-SUMMARY", json.dumps(active))
        self.assertNotIn("SECRET", json.dumps(item))
        self.assertIn("CURRENT-SUMMARY", json.dumps(active[0]))

    def test_tool_result_kept_after_call_compacted(self):
        rows = [
            self.message("u1", None, "user", "REQUEST"),
            self.message(
                "a1",
                "u1",
                "assistant",
                [
                    {
                        "type": "toolCall",
                        "id": "call1",
                        "name": "read",
                        "arguments": {"path": "never-read"},
                    }
                ],
                stopReason="toolUse",
            ),
            self.message(
                "r1",
                "a1",
                "toolResult",
                [{"type": "text", "text": "TOOL-EVIDENCE"}],
                toolCallId="call1",
                toolName="read",
                isError=False,
            ),
            self.row(
                "c1", "r1", "compaction", firstKeptEntryId="r1", summary="SUMMARY"
            ),
        ]
        self.write(rows)
        display, active, _ = self.converted()
        self.assertIn("TOOL-EVIDENCE", json.dumps(active))
        self.assertIn("SUMMARY", json.dumps(active[0]))
        self.assertEqual(len(display), 2)

    def test_signatures_system_and_custom_state_are_not_live_context(self):
        rows = self.rows() + [
            self.message("sys", "a1", "system", "HOST-SECRET"),
            self.row("state", "sys", "custom", data={"secret": "EXTENSION-STATE"}),
            self.row(
                "inject",
                "state",
                "custom_message",
                content="CUSTOM-CONTEXT",
                display=False,
            ),
            self.message(
                "answer",
                "inject",
                "assistant",
                [
                    {
                        "type": "thinking",
                        "thinking": "THOUGHT",
                        "thinkingSignature": "SIGNATURE",
                    },
                    {"type": "text", "text": "ANSWER", "textSignature": "SIGNATURE"},
                ],
            ),
        ]
        self.write(rows)
        item = self.item()
        display, active, _ = self.converted()
        for value in ["HOST-SECRET", "EXTENSION-STATE", "SIGNATURE"]:
            self.assertNotIn(value, json.dumps(item))
        self.assertNotIn("CUSTOM-CONTEXT", json.dumps(display))
        self.assertIn("CUSTOM-CONTEXT", json.dumps(active))
        self.assertNotIn("THOUGHT", json.dumps(active))

    def test_bash_exclusion_and_images_require_opt_in(self):
        rows = self.rows() + [
            self.message(
                "bash",
                "a1",
                "bashExecution",
                [],
                command="echo noexecute",
                output="BASH-EVIDENCE",
                exitCode=0,
                excludeFromContext=True,
                truncated=True,
            ),
            self.message(
                "image",
                "bash",
                "user",
                [{"type": "image", "data": "PRIVATE-BINARY", "mimeType": "image/png"}],
            ),
        ]
        self.write(rows)
        display, active, _ = self.converted()
        self.assertIn("BASH-EVIDENCE", json.dumps(display))
        self.assertNotIn("BASH-EVIDENCE", json.dumps(active))
        self.assertNotIn("PRIVATE-BINARY", json.dumps([display, active]))
        with self.assertRaises(m.MigrationError):
            m.apply(self.source, self.target, "mavis", ids=[self.sid])
        self.assertEqual(
            m.apply(
                self.source, self.target, "mavis", ids=[self.sid], allow_references=True
            )["status"],
            "imported",
        )

    def test_broken_chains_compaction_refs_unknown_and_deferred_fail(self):
        variants = [
            self.rows() + [self.row("bad", "missing", "usage")],
            self.rows() + [self.row("bad", "bad", "usage")],
            self.rows() + [self.row("bad", "a1", "future")],
            self.rows()
            + [
                self.row(
                    "c1",
                    "a1",
                    "compaction",
                    firstKeptEntryId="missing",
                    summary="SUMMARY",
                )
            ],
            self.rows()
            + [self.message("bad", "a1", "assistant", [], stopReason="deferred")],
            self.rows()
            + [
                self.message(
                    "bad", "a1", "toolResult", [], toolCallId="missing", toolName="read"
                )
            ],
        ]
        for rows in variants:
            self.write(rows)
            with self.assertRaises(m.MigrationError):
                self.item()

    def test_duplicate_session_and_old_format_rejected(self):
        other = self.project / "copy.jsonl"
        other.write_bytes(self.path().read_bytes())
        with self.assertRaises(m.MigrationError):
            self.item()
        other.unlink()
        rows = [json.loads(l) for l in self.path().read_text().splitlines()]
        rows[0]["version"] = 2
        self.path().write_text("\n".join(json.dumps(r) for r in rows))
        self.assertTrue(m.adapter()["inventory"](self.source)["errors"])


if __name__ == "__main__":
    unittest.main()
