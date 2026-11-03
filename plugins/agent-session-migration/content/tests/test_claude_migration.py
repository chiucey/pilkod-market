"""Claude branch/compaction/tool mapping, using synthetic non-private fixtures."""

import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "claude_test_core", HERE / "test_codex_migration.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
m = base.m


class ClaudeMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "projects"
        self.project = self.source / "C--Users-test-project"
        self.project.mkdir(parents=True)
        self.cwd = self.root / "workspace"
        self.cwd.mkdir()
        self.target = self.root / "target"
        (self.target / "v2/sqlite").mkdir(parents=True)
        with sqlite3.connect(self.target / "v2/sqlite/runtime-state.sqlite") as db:
            db.executescript(base.TARGET_SCHEMA)
        self.sid = "11111111-1111-1111-1111-111111111111"
        self.write_session(self.sid)
        m.use("claude-code")

    def tearDown(self):
        self.temp.cleanup()

    def row(self, role, uid, parent, content, **fields):
        return {
            "type": role,
            "uuid": uid,
            "parentUuid": parent,
            "sessionId": self.sid,
            "cwd": str(self.cwd),
            "timestamp": "2026-09-19T12:00:00Z",
            "message": {
                "role": role,
                "content": content,
                **({"id": "provider-" + uid} if role == "assistant" else {}),
            },
            **fields,
        }

    def write_session(self, sid):
        rows = [
            self.row(
                "user",
                "u1",
                None,
                "<ide_opened_file>HOST-IDE</ide_opened_file>\n保留用户请求 REQUEST-73",
            ),
            self.row(
                "assistant", "a1", "u1", [{"type": "text", "text": "OLD-DECISION-42"}]
            ),
            {"type": "ai-title", "sessionId": sid, "aiTitle": "Claude 测试"},
        ]
        for row in rows:
            row["sessionId"] = sid
        self.write(rows, sid)

    def path(self, sid=None):
        return self.project / ((sid or self.sid) + ".jsonl")

    def write(self, rows, sid=None):
        self.path(sid).write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    def rows(self):
        return [json.loads(s) for s in self.path().read_text().splitlines()]

    def item(self):
        return m.adapter()["load_source"](self.source, [self.sid])[0]

    def converted(self):
        return m.convert(self.item(), "test-target")

    def test_basic_title_readonly_and_native_storage(self):
        before = self.path().read_bytes()
        rows = m.adapter()["overview"](self.source)
        self.assertEqual(rows[0]["title"], "Claude 测试")
        result = m.apply(self.source, self.target, "mavis", ids=[self.sid])
        self.assertEqual(
            result["sessions"][0]["title"], "[From Claude Code] Claude 测试"
        )
        self.assertEqual(
            m.apply(self.source, self.target, "mavis", ids=[self.sid])["status"],
            "unchanged",
        )
        self.assertEqual(self.path().read_bytes(), before)
        display, canonical, _ = self.converted()
        self.assertNotIn("HOST-IDE", json.dumps([display, canonical]))
        self.assertIn("REQUEST-73", json.dumps(canonical))

    def test_user_xml_inside_body_is_not_mistaken_for_host_scaffolding(self):
        rows = self.rows()
        rows[0]["message"]["content"] = (
            "请保留 <system-reminder>literal</system-reminder> 和 <custom>xml</custom>"
        )
        self.write(rows)
        for history in self.converted()[:2]:
            self.assertIn(
                "<system-reminder>literal</system-reminder>", json.dumps(history)
            )
            self.assertIn("<custom>xml</custom>", json.dumps(history))

    def test_latest_branch_excludes_abandoned_reply(self):
        rows = self.rows() + [
            self.row("assistant", "a2", "u1", [{"type": "text", "text": "NEW-BRANCH"}])
        ]
        self.write(rows)
        display, canonical, _ = self.converted()
        for history in (display, canonical):
            self.assertNotIn("OLD-DECISION", json.dumps(history))
            self.assertIn("NEW-BRANCH", json.dumps(history))

    def test_parallel_streamed_tools_and_sibling_results_are_preserved(self):
        rows = self.rows()
        for n in (1, 2):
            row = self.row(
                "assistant",
                "call" + str(n),
                "a1",
                [
                    {
                        "type": "tool_use",
                        "id": "tool" + str(n),
                        "name": "Bash",
                        "input": {"command": "DO-NOT-RUN"},
                    }
                ],
            )
            row["message"]["id"] = "same-provider-message"
            rows.append(row)
            rows.append(
                self.row(
                    "user",
                    "result" + str(n),
                    "call" + str(n),
                    [
                        {
                            "type": "tool_result",
                            "tool_use_id": "tool" + str(n),
                            "content": "RESULT-" + str(n),
                        }
                    ],
                    sourceToolAssistantUUID="call" + str(n),
                )
            )
        rows.append(
            self.row(
                "assistant", "final", "result2", [{"type": "text", "text": "finished"}]
            )
        )
        self.write(rows)
        display, canonical, _ = self.converted()
        tools = [t for r in display for t in r.get("tool_calls", [])]
        self.assertEqual(len(tools), 2)
        self.assertEqual({t["tool_name"] for t in tools}, {"历史工具记录"})
        self.assertEqual({t["tool_call_status"] for t in tools}, {2})
        for value in ("RESULT-1", "RESULT-2", "DO-NOT-RUN"):
            self.assertIn(value, json.dumps(canonical))
        self.assertEqual(sum(r["role"] == "user" for r in display), 1)

    def compact_rows(self):
        rows = self.rows()
        for i in (1, 2):
            boundary = {
                "type": "system",
                "subtype": "compact_boundary",
                "uuid": "boundary" + str(i),
                "parentUuid": None,
                "logicalParentUuid": "a1" if i == 1 else "summary1",
                "sessionId": self.sid,
                "cwd": str(self.cwd),
                "timestamp": "2026-09-19T12:00:01Z",
            }
            summary = self.row(
                "user",
                "summary" + str(i),
                boundary["uuid"],
                "SUMMARY-" + str(i),
                isCompactSummary=True,
                isVisibleInTranscriptOnly=True,
            )
            if i == 2:
                boundary["compactMetadata"] = {
                    "preservedSegment": {
                        "headUuid": "a1",
                        "tailUuid": "a1",
                        "anchorUuid": "summary2",
                    },
                    "preservedMessages": {"allUuids": ["a1"], "anchorUuid": "summary2"},
                }
            rows += [boundary, summary]
        return rows

    def test_two_compactions_preserve_summary_order_and_selected_old_segment(self):
        self.write(self.compact_rows())
        display, canonical, _ = self.converted()
        self.assertIn("REQUEST-73", json.dumps(display))
        self.assertNotIn("SUMMARY-", json.dumps(display))
        self.assertEqual(len(canonical), 2)
        self.assertIn("SUMMARY-2", json.dumps(canonical[0]))
        self.assertIn("OLD-DECISION", json.dumps(canonical[1]))
        self.assertNotIn("REQUEST-73", json.dumps(canonical))
        self.assertNotIn("SUMMARY-1", json.dumps(canonical))

    def test_invalid_compaction_and_parent_chains_fail_closed(self):
        rows = self.compact_rows()
        cases = [rows[:-1], [dict(rows[0], parentUuid="missing")] + rows[1:]]
        broken = json.loads(json.dumps(rows))
        broken[-2]["compactMetadata"]["preservedMessages"]["allUuids"] = ["unknown"]
        cases.append(broken)
        cycle = self.rows()
        cycle[0]["parentUuid"] = "a1"
        cases.append(cycle)
        for case in cases:
            with self.subTest(case=cases.index(case)):
                self.write(case)
                with self.assertRaises(m.MigrationError):
                    self.item()

    def test_binary_hooks_sidechains_and_thinking_do_not_enter_model_history(self):
        rows = self.rows()
        rows += [
            self.row(
                "assistant",
                "think",
                "a1",
                [
                    {
                        "type": "thinking",
                        "thinking": "PRIVATE-THOUGHT",
                        "signature": "SIGNATURE",
                    },
                    {"type": "text", "text": "ANSWER"},
                ],
            ),
            self.row(
                "user",
                "img",
                "think",
                [
                    {"type": "image", "source": {"data": "BASE64-SECRET"}},
                    {"type": "text", "text": "图像请求"},
                ],
            ),
            {
                "type": "attachment",
                "uuid": "hook",
                "parentUuid": "img",
                "attachment": {
                    "type": "hook_additional_context",
                    "content": "HOST-HOOK",
                },
            },
            self.row(
                "assistant",
                "side",
                None,
                [{"type": "text", "text": "SIDECHAIN"}],
                isSidechain=True,
            ),
        ]
        self.write(rows)
        display, canonical, warnings = self.converted()
        self.assertIn("PRIVATE-THOUGHT", json.dumps(display))
        for value in (
            "PRIVATE-THOUGHT",
            "SIGNATURE",
            "BASE64-SECRET",
            "HOST-HOOK",
            "SIDECHAIN",
        ):
            self.assertNotIn(value, json.dumps(canonical))
        self.assertTrue(any("non-text" in w for w in warnings))

    def test_spilled_tool_output_uses_only_session_local_file_and_affects_fingerprint(
        self,
    ):
        rows = self.rows()
        rows += [
            self.row(
                "assistant",
                "call",
                "a1",
                [{"type": "tool_use", "id": "tool", "name": "Read", "input": {}}],
            ),
            self.row(
                "user",
                "res",
                "call",
                [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool",
                        "content": "<persisted-output>\nFull output saved to: C:\\old\\"
                        + self.sid
                        + "\\tool-results\\result.txt\nPreview: SHORT",
                    }
                ],
                sourceToolAssistantUUID="call",
            ),
        ]
        self.write(rows)
        target = self.project / self.sid / "tool-results/result.txt"
        target.parent.mkdir(parents=True)
        target.write_text("FULL-OUTPUT")
        first = self.item()
        self.assertIn("FULL-OUTPUT", json.dumps(first))
        target.write_text("CHANGED-OUTPUT")
        self.assertNotEqual(first["fingerprint"], self.item()["fingerprint"])
        target.unlink()
        target.symlink_to(self.path())
        with self.assertRaisesRegex(m.MigrationError, "Linked"):
            self.item()

    def test_unknown_records_identity_and_duplicate_paths_are_reported(self):
        original = self.rows()
        for row in [
            {"type": "future-record"},
            {"type": "system", "subtype": "future-compaction"},
            dict(original[0], sessionId="wrong"),
        ]:
            self.write(original + [row])
            with self.assertRaises(m.MigrationError):
                self.item()
        self.write(original)
        second = self.source / "another-project"
        second.mkdir()
        (second / self.path().name).write_bytes(self.path().read_bytes())
        with self.assertRaisesRegex(m.MigrationError, "Ambiguous"):
            self.item()
