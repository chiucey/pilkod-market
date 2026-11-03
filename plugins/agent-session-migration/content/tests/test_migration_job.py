"""The same migration job contract for every source and selection scope."""

import contextlib
import importlib.util
import io
import json
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


ZCODE = module("zcode_job_fixture", HERE / "test_migration.py")
CODEX = module("codex_job_fixture", HERE / "test_codex_migration.py")
CLAUDE = module("claude_job_fixture", HERE / "test_claude_migration.py")
OPENCODE = module("opencode_job_fixture", HERE / "test_opencode_migration.py")
LEGACY = module("legacy_job_fixture", HERE / "test_opencode_legacy.py")
PI = module("pi_job_fixture", HERE / "test_pi_migration.py")
OMP = module("omp_job_fixture", HERE / "test_omp_migration.py")
JOB = module("migration_job", HERE.parent / "scripts/migration_job.py")


class MigrationJobTests(unittest.TestCase):
    @contextlib.contextmanager
    def fixture(self, tool):
        provider = {
            "zcode": ZCODE,
            "codex": CODEX,
            "claude-code": CLAUDE,
            "opencode": OPENCODE,
            "opencode-legacy": LEGACY,
            "pi-agent": PI,
            "omp": OMP,
        }[tool]
        fixture = (
            provider.LegacyOpenCodeTests()
            if tool == "opencode-legacy"
            else provider.MigrationTests()
            if tool == "zcode"
            else provider.ClaudeMigrationTests()
            if tool == "claude-code"
            else provider.OpenCodeMigrationTests()
            if tool == "opencode"
            else provider.PiMigrationTests()
            if tool == "pi-agent"
            else provider.OmpMigrationTests()
            if tool == "omp"
            else provider.CodexMigrationTests()
        )
        fixture.setUp()
        m = provider.m
        m.use("opencode" if tool == "opencode-legacy" else tool)
        try:
            if tool == "zcode":
                source = fixture.source.resolve()
                with sqlite3.connect(source) as db:
                    db.execute(
                        "INSERT INTO session SELECT 's2',directory,title,time_created+2,time_updated+2,revert FROM session WHERE id='s1'"
                    )
                    db.execute(
                        "INSERT INTO message SELECT replace(id,'s1','s2'),'s2',time_created,data,sequence FROM message WHERE session_id='s1'"
                    )
                    db.execute(
                        "INSERT INTO part SELECT replace(id,'s1','s2'),replace(message_id,'s1','s2'),'s2',time_created,data,sequence FROM part WHERE session_id='s1'"
                    )
                ids = ["s0", "s1", "s2"]
            else:
                source = (
                    fixture.source
                    if tool
                    in ("claude-code", "opencode", "opencode-legacy", "pi-agent", "omp")
                    else fixture.codex
                ).resolve()
                ids = [
                    fixture.sid,
                    "22222222-2222-2222-2222-222222222222",
                    "33333333-3333-3333-3333-333333333333",
                ]
                for sid in ids[1:]:
                    (
                        fixture.write_session
                        if tool
                        in (
                            "claude-code",
                            "opencode",
                            "opencode-legacy",
                            "pi-agent",
                            "omp",
                        )
                        else fixture.write_rollout
                    )(sid)
            args = SimpleNamespace(
                source="opencode" if tool == "opencode-legacy" else tool,
                command="plan",
                all=True,
                session=None,
                report=str(fixture.root / "job.json"),
                batch_size=2,
                workspace=None,
                agent="mavis",
                allow_reference_only=False,
                restore_projects=False,
                retry_failed=False,
            )
            yield fixture, m, source, ids, args
        finally:
            fixture.tearDown()

    def run_job(self, fixture, m, source, args, command):
        args.command = command
        with contextlib.redirect_stderr(io.StringIO()):
            return JOB.execute(m, args, source, fixture.target.resolve())

    def rows(self, fixture):
        with sqlite3.connect(fixture.target / "v2/sqlite/runtime-state.sqlite") as db:
            return db.execute(
                "SELECT * FROM local_runtime_sessions ORDER BY session_id"
            ).fetchall()

    def test_zcode_all_skips_internal_sessions_and_explicit_child_is_incompatible(self):
        with self.fixture("zcode") as (f, m, source, ids, args):
            with sqlite3.connect(source) as db:
                db.execute("ALTER TABLE session ADD COLUMN task_type TEXT")
                db.execute(
                    "UPDATE session SET task_type='subagent_child' WHERE id='s1'"
                )
            preview = self.run_job(f, m, source, args, "plan")
            self.assertEqual(preview["counts"], {"ready": 2})
            self.assertEqual(preview["excludedSessions"], 1)
            result = self.run_job(f, m, source, args, "apply")
            self.assertEqual(result["counts"], {"imported": 2})
            args.all = False
            args.session = ["s1"]
            args.report = str(f.root / "child.json")
            result = self.run_job(f, m, source, args, "plan")
            self.assertEqual(result["counts"], {"incompatible": 1})

    def test_old_preview_cannot_bypass_child_filter(self):
        with self.fixture("zcode") as (f, m, source, ids, args):
            self.run_job(f, m, source, args, "plan")
            with sqlite3.connect(source) as db:
                db.execute("ALTER TABLE session ADD COLUMN task_type TEXT")
                db.execute(
                    "UPDATE session SET task_type='subagent_child' WHERE id='s1'"
                )
            result = self.run_job(f, m, source, args, "apply")
            self.assertEqual(result["status"], "completed-with-errors")
            with sqlite3.connect(f.target / "v2/sqlite/runtime-state.sqlite") as db:
                self.assertIsNone(
                    db.execute(
                        "SELECT 1 FROM local_runtime_sessions WHERE session_id=?",
                        (m.identity(source, "s1"),),
                    ).fetchone()
                )

    def test_every_source_has_same_adapter_contract(self):
        m = ZCODE.m
        self.assertEqual(set(m.adapter("zcode")), set(m.adapter("codex")))
        for tool in (
            "zcode",
            "codex",
            "claude-code",
            "opencode",
            "pi-agent",
            "omp",
            "opencode-legacy",
        ):
            self.assertEqual(
                set(m.adapter("zcode")),
                set(m.adapter("opencode" if tool == "opencode-legacy" else tool)),
            )
            for key in (
                "inventory",
                "load_inventory",
                "select_histories",
                "load_source",
                "source_path",
                "overview",
            ):
                self.assertTrue(
                    callable(
                        m.adapter("opencode" if tool == "opencode-legacy" else tool)[
                            key
                        ]
                    )
                )

    def test_all_sources_and_scopes_share_preview_batches_and_idempotency(self):
        for tool in (
            "zcode",
            "codex",
            "claude-code",
            "opencode",
            "pi-agent",
            "omp",
            "opencode-legacy",
        ):
            for count in (1, 2, 3):
                with (
                    self.subTest(tool=tool, count=count),
                    self.fixture(tool) as (f, m, source, ids, args),
                ):
                    args.all = count == 3
                    args.session = None if args.all else ids[:count]
                    initial = self.rows(f)
                    original = {
                        str(p): p.read_bytes()
                        for p in (
                            [source] if source.is_file() else source.rglob("*.jsonl")
                        )
                    }
                    self.assertEqual(
                        self.run_job(f, m, source, args, "plan")["counts"],
                        {"ready": count},
                    )
                    self.assertEqual(self.rows(f), initial)
                    result = self.run_job(f, m, source, args, "apply")
                    self.assertEqual(result["status"], "completed")
                    self.assertEqual(result["counts"], {"imported": count})
                    report = json.loads(Path(args.report).read_text())
                    self.assertEqual(len(report["batches"]), (count + 1) // 2)
                    self.assertTrue(
                        all(
                            Path(batch["backup"]).is_file()
                            for batch in report["batches"]
                        )
                    )
                    self.assertTrue(
                        all(
                            row["plan"]["title"].startswith(
                                "[From " + m.adapter()["label"] + "]"
                            )
                            for row in report["sessions"]
                        )
                    )
                    imported = self.rows(f)
                    for row in initial:
                        self.assertIn(row, imported)
                    self.assertEqual(
                        self.run_job(f, m, source, args, "apply")["status"], "completed"
                    )
                    self.assertEqual(self.rows(f), imported)
                    self.assertEqual(
                        {path: Path(path).read_bytes() for path in original}, original
                    )

    def test_selected_batch_isolates_write_failure_for_both_sources(self):
        for tool in (
            "zcode",
            "codex",
            "claude-code",
            "opencode",
            "pi-agent",
            "omp",
            "opencode-legacy",
        ):
            with (
                self.subTest(tool=tool),
                self.fixture(tool) as (f, m, source, ids, args),
            ):
                args.all, args.session = False, ids[:2]
                self.run_job(f, m, source, args, "plan")
                initialize = m.initialize_history

                def fail(db, sid, messages):
                    if sid == m.identity(source, ids[1]):
                        raise m.MigrationError("Injected write failure")
                    return initialize(db, sid, messages)

                with patch.object(m, "initialize_history", side_effect=fail):
                    result = self.run_job(f, m, source, args, "apply")
                self.assertEqual(result["counts"], {"imported": 1, "failed": 1})
                self.assertEqual(len(self.rows(f)), 2)
                args.retry_failed = True
                self.assertEqual(
                    self.run_job(f, m, source, args, "apply")["status"], "completed"
                )
                self.assertEqual(len(self.rows(f)), 3)

    def test_all_sources_reuse_legacy_import_identity(self):
        for tool in (
            "zcode",
            "codex",
            "claude-code",
            "opencode",
            "pi-agent",
            "omp",
            "opencode-legacy",
        ):
            with (
                self.subTest(tool=tool),
                self.fixture(tool) as (f, m, source, ids, args),
            ):
                m.apply(source, f.target, "mavis", ids=ids[:1])
                previous = self.rows(f)
                args.all, args.session = False, ids[:1]
                self.assertEqual(
                    self.run_job(f, m, source, args, "plan")["counts"],
                    {"already-imported": 1},
                )
                self.assertEqual(
                    self.run_job(f, m, source, args, "apply")["status"], "completed"
                )
                self.assertEqual(self.rows(f), previous)

    def test_selected_sources_resume_hard_exit_before_and_after_commit(self):
        for tool in (
            "zcode",
            "codex",
            "claude-code",
            "opencode",
            "pi-agent",
            "omp",
            "opencode-legacy",
        ):
            for point in ("messages.jsonl", "report.complete"):
                with (
                    self.subTest(tool=tool, point=point),
                    self.fixture(tool) as (f, m, source, ids, args),
                ):
                    args.all, args.session = False, ids[:1]
                    self.run_job(f, m, source, args, "plan")
                    argv = [
                        "migrate",
                        "apply",
                        "--source",
                        args.source,
                        "--source-db",
                        str(source),
                        "--target-data-dir",
                        str(f.target),
                        "--session",
                        ids[0],
                        "--report",
                        args.report,
                    ]
                    code = """import os,sys,json
sys.path.insert(0,sys.argv[1])
import migrate
point,argv=sys.argv[2],json.loads(sys.argv[3])
write=migrate.private_write
def stop(path,value):
    write(path,value)
    if path.name == point: os._exit(91)
migrate.private_write=stop
sys.argv=argv
raise SystemExit(migrate.main())
"""
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-B",
                            "-c",
                            code,
                            str(HERE.parent / "scripts"),
                            point,
                            json.dumps(argv),
                        ],
                        capture_output=True,
                        timeout=15,
                    )
                    self.assertEqual(result.returncode, 91, result.stderr)
                    self.assertEqual(
                        self.run_job(f, m, source, args, "apply")["status"], "completed"
                    )
                    self.assertEqual(len(self.rows(f)), 2)
                    self.assertEqual(
                        self.run_job(f, m, source, args, "apply")["status"], "completed"
                    )

    def test_selected_workspace_mapping_is_bound_to_report(self):
        for tool in (
            "zcode",
            "codex",
            "claude-code",
            "opencode",
            "pi-agent",
            "omp",
            "opencode-legacy",
        ):
            with (
                self.subTest(tool=tool),
                self.fixture(tool) as (f, m, source, ids, args),
            ):
                args.all, args.session = False, ids[:1]
                mapped = f.root / "mapped-workspace"
                mapped.mkdir()
                args.workspace = str(mapped)
                self.run_job(f, m, source, args, "plan")
                args.workspace = None
                with self.assertRaisesRegex(m.MigrationError, "mismatch"):
                    self.run_job(f, m, source, args, "apply")
                args.workspace = str(mapped)
                self.assertEqual(
                    self.run_job(f, m, source, args, "apply")["status"], "completed"
                )

    def test_missing_selected_session_does_not_block_valid_selected_session(self):
        for tool in (
            "zcode",
            "codex",
            "claude-code",
            "opencode",
            "pi-agent",
            "omp",
            "opencode-legacy",
        ):
            with (
                self.subTest(tool=tool),
                self.fixture(tool) as (f, m, source, ids, args),
            ):
                args.all, args.session = False, [ids[0], "missing-session"]
                self.assertEqual(
                    self.run_job(f, m, source, args, "plan")["counts"],
                    {"ready": 1, "incompatible": 1},
                )
                self.assertEqual(
                    self.run_job(f, m, source, args, "apply")["status"],
                    "completed-with-errors",
                )
                self.assertEqual(len(self.rows(f)), 2)

    def test_old_codex_all_report_remains_resumable(self):
        with self.fixture("codex") as (f, m, source, ids, args):
            self.run_job(f, m, source, args, "plan")
            path = Path(args.report)
            report = json.loads(path.read_text())
            report["version"] = 1
            del report["config"]["selection"]
            del report["config"]["workspace"]
            path.write_text(json.dumps(report))
            self.assertEqual(
                self.run_job(f, m, source, args, "apply")["status"], "completed"
            )
            self.assertEqual(json.loads(path.read_text())["version"], 2)
