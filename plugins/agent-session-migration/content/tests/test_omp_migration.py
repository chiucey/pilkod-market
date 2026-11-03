"""OMP V3 contract fixtures from upstream b4e2882; no private transcripts or LLM calls."""

import importlib.util
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "omp_test_core", HERE / "test_codex_migration.py"
)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
m = base.m


class OmpMigrationTests(unittest.TestCase):
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
        self.sid = "omp-session-id"
        self.write_session(self.sid)
        m.use("omp")

    def tearDown(self):
        self.temp.cleanup()

    def row(self, uid, parent, typ="message", **values):
        return {
            "type": typ,
            "id": uid,
            "parentId": parent,
            "timestamp": "2026-10-09T10:00:00Z",
            **values,
        }

    def msg(self, uid, parent, role, content, **values):
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

    def basic(self):
        return [
            self.msg("u1", None, "user", "REQUEST-73"),
            self.msg(
                "a1", "u1", "assistant", [{"type": "text", "text": "DECISION-42"}]
            ),
        ]

    def path(self, sid=None):
        return self.project / ("date_" + (sid or self.sid) + ".jsonl")

    def write_session(self, sid):
        self.write(self.basic(), sid)

    def write(self, rows, sid=None, slot=True, **header_fields):
        header = {
            "type": "session",
            "version": 3,
            "id": sid or self.sid,
            "cwd": str(self.cwd),
            "timestamp": "2026-10-09T10:00:00Z",
            "title": "OLD-TITLE",
            **header_fields,
        }
        prefix = ""
        if slot:
            title = {
                "type": "title",
                "v": 1,
                "title": "OMP 新标题",
                "source": "user",
                "updatedAt": header["timestamp"],
                "pad": "",
            }
            encode = lambda value: json.dumps(
                value, ensure_ascii=False, separators=(",", ":")
            )
            title["pad"] = " " * (255 - len(encode(title).encode("utf-8")))
            prefix = encode(title) + "\n"
            self.assertEqual(len(prefix.encode("utf-8")), 256)
        self.path(sid).write_text(
            prefix + "\n".join(json.dumps(r) for r in [header, *rows]) + "\n",
            encoding="utf-8",
        )

    def item(self):
        return m.adapter()["load_source"](self.source, [self.sid])[0]

    def converted(self):
        return m.convert(self.item(), "test-target")

    def tool_rows(self):
        return [
            self.msg("u1", None, "user", "REQUEST-73"),
            self.msg(
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
            self.msg(
                "r1",
                "a1",
                "toolResult",
                [{"type": "text", "text": "TOOL-EVIDENCE"}],
                toolCallId="call1",
                toolName="read",
                isError=False,
            ),
        ]

    def test_title_slot_readonly_identity_fork_and_legacy_header(self):
        self.write(
            self.basic(),
            parentSession="/old/fork.jsonl",
            providerPromptCacheKey="CACHE-SECRET",
        )
        before = self.path().read_bytes()
        result = m.apply(self.source, self.target, "mavis", ids=[self.sid])
        self.assertEqual(result["sessions"][0]["title"], "[From OMP] OMP 新标题")
        self.assertEqual(
            m.apply(self.source, self.target, "mavis", ids=[self.sid])["status"],
            "unchanged",
        )
        self.assertEqual(self.path().read_bytes(), before)
        self.assertNotIn("CACHE-SECRET", json.dumps(self.item()))
        self.write(self.basic(), slot=False, title="Legacy OMP")
        self.assertEqual(self.item()["session"]["title"], "Legacy OMP")

    def test_branch_compaction_and_clear_do_not_revive_discarded_context(self):
        rows = self.basic() + [
            self.msg("abandoned", "a1", "user", "ABANDONED"),
            self.row(
                "branch",
                "a1",
                "branch_summary",
                fromId="abandoned",
                summary="BRANCH-LESSON",
            ),
            self.row(
                "c1",
                "branch",
                "compaction",
                firstKeptEntryId="a1",
                summary="OLD-SUMMARY",
            ),
            self.msg("u2", "c1", "user", "RETAIN-THIS"),
            self.row(
                "c2",
                "u2",
                "compaction",
                firstKeptEntryId="u2",
                summary="CURRENT-SUMMARY",
                method="handoff",
            ),
        ]
        self.write(rows)
        display, active, _ = self.converted()
        self.assertIn("DECISION-42", json.dumps(display))
        self.assertIn("CURRENT-SUMMARY", json.dumps(active[0]))
        self.assertIn("RETAIN-THIS", json.dumps(active))
        for value in ("ABANDONED", "OLD-SUMMARY", "BRANCH-LESSON", "DECISION-42"):
            self.assertNotIn(value, json.dumps(active))
        rows += [
            self.row("clear", "c2", "reset_boundary"),
            self.msg("u3", "clear", "user", "AFTER-CLEAR"),
        ]
        self.write(rows)
        display, active, _ = self.converted()
        self.assertEqual(len(active), 1)
        self.assertIn("AFTER-CLEAR", json.dumps(active))
        self.assertIn("DECISION-42", json.dumps(display))
        rows += [
            self.row(
                "c3",
                "u3",
                "compaction",
                firstKeptEntryId="",
                summary="AFTER-CLEAR-SUMMARY",
                method="soft",
            )
        ]
        self.write(rows)
        self.assertEqual(len(self.converted()[1]), 1)
        self.assertIn("AFTER-CLEAR-SUMMARY", json.dumps(self.converted()[1]))

    def test_tools_cross_compaction_dangling_and_failed_turns(self):
        self.write(
            self.tool_rows()
            + [
                self.row(
                    "c", "r1", "compaction", firstKeptEntryId="r1", summary="SUMMARY"
                )
            ]
        )
        display, active, _ = self.converted()
        self.assertIn("TOOL-EVIDENCE", json.dumps(active))
        self.assertEqual(len(display), 2)
        rows = self.tool_rows()
        rows[1]["message"]["stopReason"] = "error"
        self.write(rows + [self.msg("u2", "r1", "user", "NEXT")])
        display, active, _ = self.converted()
        self.assertIn("TOOL-EVIDENCE", json.dumps(display))
        self.assertNotIn("TOOL-EVIDENCE", json.dumps(active))
        rows[1]["message"]["stopReason"] = "toolUse"
        rows[1]["message"]["retryRecovery"] = True
        self.write(rows)
        self.assertNotIn("TOOL-EVIDENCE", json.dumps(self.converted()[1]))
        self.write(self.tool_rows()[:2])
        display, active, _ = self.converted()
        self.assertIn("never-read", json.dumps(display))
        self.assertNotIn("never-read", json.dumps(active))
        # Rewritten assistant projections stay in their original turn even with a later user.
        rows = self.tool_rows()[:2]
        rows[1]["message"]["content"].append({"type": "text", "text": "PARTIAL-TEXT"})
        self.write(rows + [self.msg("u2", "a1", "user", "NEXT-TURN")])
        _, active, _ = self.converted()
        self.assertEqual(active[0]["turn_id"], active[1]["turn_id"])
        self.assertNotEqual(active[1]["turn_id"], active[2]["turn_id"])
        rows[1]["message"]["stopReason"] = "aborted"
        self.write(
            rows
            + [
                self.row(
                    "note",
                    "a1",
                    "custom_message",
                    customType="interrupted-thinking",
                    content="CONTINUITY",
                    display=False,
                )
            ]
        )
        _, active, _ = self.converted()
        self.assertIn("PARTIAL-TEXT", json.dumps(active))
        self.assertIn("CONTINUITY", json.dumps(active))

    def test_execution_file_mentions_and_attachment_opt_in(self):
        rows = self.basic() + [
            self.msg(
                "bash",
                "a1",
                "bashExecution",
                [],
                command="do-not-execute",
                output="BASH-OUTPUT",
                exitCode=0,
                excludeFromContext=True,
                truncated=True,
                fullOutputPath="/never/read",
            ),
            self.msg(
                "python",
                "bash",
                "pythonExecution",
                [],
                code="do-not-run()",
                output="PYTHON-OUTPUT",
                exitCode=0,
            ),
            self.msg(
                "files",
                "python",
                "fileMention",
                [],
                files=[{"path": "/never/read.txt", "content": "INLINE-TEXT"}],
            ),
            self.msg(
                "image",
                "files",
                "user",
                [
                    {
                        "type": "image",
                        "data": "blob:PRIVATE-BLOB",
                        "mimeType": "image/png",
                    }
                ],
            ),
        ]
        self.write(rows)
        display, active, _ = self.converted()
        self.assertIn("BASH-OUTPUT", json.dumps(display))
        self.assertNotIn("BASH-OUTPUT", json.dumps(active))
        self.assertIn("PYTHON-OUTPUT", json.dumps(active))
        self.assertIn("INLINE-TEXT", json.dumps(active))
        self.assertNotIn("PRIVATE-BLOB", json.dumps(self.item()))
        with self.assertRaises(m.MigrationError):
            m.apply(self.source, self.target, "mavis", ids=[self.sid])
        self.assertEqual(
            m.apply(
                self.source, self.target, "mavis", ids=[self.sid], allow_references=True
            )["status"],
            "imported",
        )

    def test_sensitive_metadata_and_transient_context_not_imported(self):
        rows = self.basic() + [
            self.msg("sys", "a1", "system", "SYSTEM-SECRET"),
            self.row("pin", "sys", "credential_pin", hash="ACCOUNT-SECRET"),
            self.row(
                "mode",
                "pin",
                "mode_change",
                mode="plan",
                data={"secret": "MODE-SECRET"},
            ),
            self.row(
                "state",
                "mode",
                "custom",
                customType="extension",
                data={"secret": "EXTENSION-SECRET"},
            ),
            self.row(
                "transient",
                "state",
                "custom_message",
                customType="prewalk-plan",
                content="TRANSIENT-PLAN",
                display=False,
            ),
            self.row(
                "custom",
                "transient",
                "custom_message",
                customType="note",
                content="CUSTOM-CONTEXT",
                display=True,
            ),
            self.msg(
                "a2",
                "custom",
                "assistant",
                [
                    {
                        "type": "thinking",
                        "thinking": "THOUGHT",
                        "thinkingSignature": "SIGNATURE-SECRET",
                    },
                    {"type": "redactedThinking", "data": "REDACTED-SECRET"},
                    {"type": "text", "text": "ANSWER"},
                ],
            ),
        ]
        self.write(rows)
        item = json.dumps(self.item())
        for value in (
            "SYSTEM-SECRET",
            "ACCOUNT-SECRET",
            "MODE-SECRET",
            "EXTENSION-SECRET",
            "SIGNATURE-SECRET",
            "REDACTED-SECRET",
        ):
            self.assertNotIn(value, item)
        display, active, _ = self.converted()
        self.assertIn("THOUGHT", json.dumps(display))
        self.assertNotIn("THOUGHT", json.dumps(active))
        self.assertNotIn("TRANSIENT-PLAN", json.dumps(active))
        self.assertIn("CUSTOM-CONTEXT", json.dumps(active))

    def test_unsupported_context_and_broken_records_fail_closed(self):
        variants = [
            self.row("bad", "missing", "label"),
            self.row("bad", "bad", "label"),
            self.row("bad", "a1", "future"),
            self.row(
                "bad", "a1", "compaction", firstKeptEntryId="missing", summary="SUMMARY"
            ),
            self.msg("bad", "a1", "assistant", [], stopReason="deferred"),
            self.row(
                "bad",
                "a1",
                "custom",
                customType="experimental_context_notes",
                data={"version": 1, "text": "NOTES"},
            ),
            *[
                self.row(
                    "bad",
                    "a1",
                    "compaction",
                    firstKeptEntryId="a1",
                    summary="ONLY-PART-OF-CONTEXT",
                    **fields,
                )
                for fields in (
                    {"method": "remote"},
                    {"method": "snapcompact"},
                    {"method": "future"},
                    {
                        "preserveData": {
                            "openaiRemoteCompaction": {"replacementHistory": []}
                        }
                    },
                    {"preserveData": {"snapcompact": {"frames": []}}},
                    {"details": {"kind": "experimental-context-rollover"}},
                    {"providerReplayThroughEntryId": "a1"},
                )
            ],
        ]
        for row in variants:
            with self.subTest(row=row):
                self.write(self.basic() + [row])
                with self.assertRaises(m.MigrationError):
                    self.item()
        self.write(self.basic(), version=2)
        self.assertTrue(m.adapter()["inventory"](self.source)["errors"])
        self.write(self.basic())
        with self.path().open("a") as stream:
            stream.write('{"type":')
        self.assertTrue(m.adapter()["inventory"](self.source)["errors"])

    def test_subagent_excluded_but_fork_kept_and_duplicate_identity_rejected(self):
        self.write(self.basic(), parentSession="parent-session")
        child = "child-session"
        self.write(
            [
                self.row(
                    "init",
                    None,
                    "session_init",
                    systemPrompt="PRIVATE-SYSTEM",
                    task="CHILD-TASK",
                )
            ],
            child,
        )
        data = m.adapter()["inventory"](self.source)
        self.assertEqual(data["ids"], [self.sid])
        self.assertEqual(data["excluded"][0]["sourceId"], child)
        with self.assertRaisesRegex(m.MigrationError, "subagent"):
            m.adapter()["load_inventory"](data, [child])
        (self.project / "copy.jsonl").write_bytes(self.path().read_bytes())
        with self.assertRaisesRegex(m.MigrationError, "Ambiguous"):
            self.item()

    def test_profile_and_xdg_resolution_never_falls_back_to_another_profile(self):
        config = self.root / ".omp"
        default = config / "agent/sessions"
        work = config / "profiles/work/agent/sessions"
        default.mkdir(parents=True)
        work.mkdir(parents=True)
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(Path, "home", return_value=self.root),
        ):
            resolve = m.adapter()["source_path"]
            self.assertEqual(resolve(), default)
            with patch.dict(
                os.environ,
                {
                    "OMP_PROFILE": "work",
                    "PI_CODING_AGENT_DIR": str(self.root / "wrong"),
                },
            ):
                self.assertEqual(resolve(), work)
            with patch.dict(
                os.environ,
                {
                    "OMP_PROFILE": "",
                    "PI_PROFILE": "work",
                    "PI_CODING_AGENT_DIR": str(work.parent),
                },
            ):
                self.assertEqual(resolve(), default)
            with patch.dict(os.environ, {"OMP_PROFILE": "missing"}):
                with self.assertRaises(m.MigrationError):
                    resolve()
            with patch.dict(os.environ, {"OMP_PROFILE": "../work"}):
                with self.assertRaises(m.MigrationError):
                    resolve()
                self.assertEqual(resolve(self.source), self.source)
            xdg = self.root / "xdg"
            (xdg / "omp/sessions").mkdir(parents=True)
            with (
                patch.dict(os.environ, {"XDG_DATA_HOME": str(xdg)}),
                patch("sys.platform", "darwin"),
            ):
                self.assertEqual(resolve(), xdg / "omp/sessions")
                with patch.dict(os.environ, {"OMP_PROFILE": "work"}):
                    self.assertEqual(resolve(), work)
                    (xdg / "omp/profiles/work/sessions").mkdir(parents=True)
                    self.assertEqual(resolve(), xdg / "omp/profiles/work/sessions")

    def test_linked_sources_are_not_followed(self):
        link = self.source / "linked"
        link.symlink_to(self.project, target_is_directory=True)
        self.assertEqual(m.adapter()["inventory"](self.source)["ids"], [self.sid])
        with self.assertRaises(m.MigrationError):
            m.adapter()["source_path"](link)
        (self.project / "linked.jsonl").symlink_to(self.path())
        self.assertTrue(m.adapter()["inventory"](self.source)["errors"])


if __name__ == "__main__":
    unittest.main()
