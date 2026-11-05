#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests for the craft-detective-fiction scripts.

Self-contained: no third-party dependencies, no network, all projects are
built in temporary directories. Run after changing scripts/:

    <python> tests/run_tests.py

Exit code 0 means every check passed. Each test maps to a historical defect
(v1/v2/v3 problem lists) so a regression points at its original context.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # keep the skill directory clean (v3 N10)

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import audit_mystery_project as audit  # noqa: E402
import build_clean_export as export  # noqa: E402
import init_project  # noqa: E402

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"PASS {name}")
    else:
        FAILED += 1
        print(f"FAIL {name} | {detail}")


def run_cli(main, *argv: str) -> tuple[int, str]:
    old = sys.argv
    sys.argv = [str(a) for a in argv]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            code = main()
    finally:
        sys.argv = old
    return code, buf.getvalue()


def make_project(root: Path) -> Path:
    """Minimal valid project: one Q, one C paid off in chapter-02."""
    proj = root / "proj"
    (proj / "chapters").mkdir(parents=True)
    (proj / "exports").mkdir()
    (proj / "project-charter.md").write_text("# 章程\n内容。\n", encoding="utf-8")
    (proj / "style-guide.md").write_text("# 风格\n内容。\n", encoding="utf-8")
    (proj / "outline.md").write_text("# 大纲\n内容。\n", encoding="utf-8")
    (proj / "notes.md").write_text("# 笔记\n内容。\n", encoding="utf-8")
    (proj / "case-bible.md").write_text(
        "# 真相\n\n| 结论编号 | 结论 | 推理步骤 | 替代解释 | 排除方法 | 状态 |\n"
        "|---|---|---|---|---|---|\n"
        "| Q-001 | 甲是凶手 | 步骤 | 替代 | 排除 | 已确认 |\n",
        encoding="utf-8",
    )
    (proj / "mystery-ledger.md").write_text(
        "# 登记簿\n\n"
        "| ID | 类型 | 表面 | 支撑结论 | 计划 | 实际出现 | 表面解释 | 真实意义 | 计划回收 | 实际回收 | 状态 | 备注 |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| C-001 | 线索 | x | Q-001 | x | chapter-02.md | x | x | x | chapter-02.md | 已回收 | x |\n",
        encoding="utf-8",
    )
    (proj / "audit-report.md").write_text(
        "# 审计\n\n> 快照状态：current  \n", encoding="utf-8"
    )
    return proj


def chapter_frontmatter(number: int, status: str, payoff: str = "[]") -> str:
    return (
        f"---\nchapter: {number}\ntitle: t{number}\nledger_actions:\n  seed: []\n"
        f"  reinforce: []\n  pay_off: {payoff}\n  retire: []\n"
        "continuity_dependencies: []\n"
        f"status: {status}\n"
        "checks:\n  pov: pass\n  continuity: pass\n  ledger_synced: pass\n"
        "  notes_synced: pass\n  outline_deviation: none\n"
        "  user_approval: not_required\n---\n"
    )


# ---------- frontmatter parsing (v2 N1, v3 N9, trailing comments) ----------

def test_list_forms() -> None:
    inline = "ledger_actions:\n  pay_off: [C-001]\ncontinuity_dependencies: [chapter-01.md]\n"
    vals, issues = audit.parse_chapter_metadata(inline)
    check("parse: inline lists", issues == []
          and vals["ledger_actions"]["pay_off"] == ["C-001"]
          and vals["continuity_dependencies"] == ["chapter-01.md"], str(issues))

    block = (
        "ledger_actions:\n  pay_off:\n    - C-001\n"
        "continuity_dependencies:\n  - chapter-01.md\n  - chapter-02.md\n"
    )
    vals, issues = audit.parse_chapter_metadata(block)
    check("parse: block sequences", issues == []
          and vals["ledger_actions"]["pay_off"] == ["C-001"]
          and vals["continuity_dependencies"] == ["chapter-01.md", "chapter-02.md"],
          str(issues))

    flow_empty = "ledger_actions:\n  seed:\n    []\ncontinuity_dependencies:\n  []\n"
    vals, issues = audit.parse_chapter_metadata(flow_empty)
    check("parse: flow list on indented line (N9)", issues == []
          and vals["ledger_actions"]["seed"] == []
          and vals["continuity_dependencies"] == [], str(issues))

    _, issues = audit.parse_chapter_metadata("chapter: 2\n  [C-001]\n")
    check("parse: misplaced flow line rejected", issues != [])

    commented = "status: draft  # 待议\nledger_actions:\n  pay_off:\n    - C-001  # 本章回收\n"
    vals, issues = audit.parse_chapter_metadata(commented)
    check("parse: trailing comments stripped", issues == []
          and vals.get("status") == "draft"
          and vals["ledger_actions"]["pay_off"] == ["C-001"], str(issues))

    template = (SKILL_DIR / "assets" / "chapter-template.md").read_text(encoding="utf-8")
    _, issues = audit.parse_chapter_metadata(audit.frontmatter(template))
    check("parse: bundled chapter template stays valid", issues == [], str(issues))


# ---------- clean manuscript check (v2 N3) ----------

def test_clean_manuscript() -> None:
    clean = [
        "他停在 A-301 号房门口，车牌是 M-208。",
        "那把锁是 H-115 型。",
        "备注：草稿 --> 定稿，见附件。",
        "他翻到第 C-4 页。",
        "雨伞立在门内，伞骨上的水还在往地板上滴。",
    ]
    for text in clean:
        check(f"clean: no false positive ({text[:10]}…)",
              audit.clean_manuscript_issues(text) == [],
              str(audit.clean_manuscript_issues(text)))

    dirty = {
        "real ID leak": "正文出现 C-001 的编号。",
        "real Q leak": "结论 Q-001 被写出。",
        "paired comment": "残<!-- 注释 -->留。",
        "lone open": "残留 <!-- INTERNAL-NOTES-BEGIN 标记。",
        "line-start close": "上一行\n--> 孤立闭合符。\n",
        "template token": "标题仍是 {{TITLE}}。",
        "bracket placeholder": "这里有 [待定] 内容。",
    }
    for name, text in dirty.items():
        check(f"clean: still catches {name}",
              audit.clean_manuscript_issues(text) != [])


# ---------- BOM tolerance (v2 N7) ----------

def test_bom() -> None:
    fm = "---\nchapter: 1\nstatus: draft\n---\nbody\n"
    check("bom: with BOM parsed", audit.frontmatter("\ufeff" + fm) is not None)
    check("bom: without BOM parsed", audit.frontmatter(fm) is not None)


# ---------- strict mode semantics (v2 N2) ----------

def test_strict() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proj = make_project(Path(tmp))
        code, _ = run_cli(audit.main, "audit", proj, "--strict")
        check("strict: clean project exit 0", code == 0, f"exit={code}")

        (proj / "notes.md").write_text("# 笔记\n此处待定。\n", encoding="utf-8")
        code, _ = run_cli(audit.main, "audit", proj, "--strict")
        check("strict: notes.md 待定 exempt", code == 0, f"exit={code}")

        (proj / "outline.md").write_text("# 大纲\n此处待定。\n", encoding="utf-8")
        code, out = run_cli(audit.main, "audit", proj, "--strict")
        check("strict: authoritative 待定 exit 2", code == 2, f"exit={code}")
        (proj / "outline.md").write_text("# 大纲\n内容。\n", encoding="utf-8")

        (proj / "audit-report.md").write_text(
            "# 审计\n\n> 快照状态：stale  \n", encoding="utf-8"
        )
        code, out = run_cli(audit.main, "audit", proj, "--strict")
        check("strict: stale snapshot exit 1", code == 1, f"exit={code}")
        check("strict: stale message gives remediation", "快照状态：current" in out)


# ---------- Q-### integrity (v1 P0-3) ----------

def test_conclusion_links() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proj = make_project(Path(tmp))
        code, _ = run_cli(audit.main, "audit", proj)
        check("q-links: valid reference passes", code == 0, f"exit={code}")

        ledger = (proj / "mystery-ledger.md").read_text(encoding="utf-8")
        (proj / "mystery-ledger.md").write_text(
            ledger.replace("Q-001", "Q-002"), encoding="utf-8"
        )
        code, out = run_cli(audit.main, "audit", proj)
        check("q-links: unknown Q-### is an error", code == 1
              and "unknown conclusion ID Q-002" in out, out)


# ---------- canonical gate (v1 P1-2, v2 N1) ----------

def test_canonical_gate() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proj = make_project(Path(tmp))
        (proj / "chapters" / "chapter-01.md").write_text(
            chapter_frontmatter(1, "canonical") + "\n前章。\n", encoding="utf-8"
        )
        block_ch2 = chapter_frontmatter(2, "draft", payoff="[]").replace(
            "  pay_off: []", "  pay_off:\n    - C-001"
        ).replace(
            "continuity_dependencies: []",
            "continuity_dependencies:\n  - chapter-01.md",
        )
        (proj / "chapters" / "chapter-02.md").write_text(
            block_ch2 + "\n本章回收线索。\n", encoding="utf-8"
        )
        code, out = run_cli(audit.main, "audit", proj, "--chapter", "chapter-02.md")
        check("gate: block-style chapter passes", code == 0, f"exit={code}\n{out}")

        unreconciled = (proj / "mystery-ledger.md").read_text(encoding="utf-8")
        (proj / "mystery-ledger.md").write_text(
            unreconciled.replace("已回收", "已埋设"), encoding="utf-8"
        )
        code, out = run_cli(audit.main, "audit", proj, "--chapter", "chapter-02.md")
        check("gate: unreconciled pay_off fails", code == 1
              and "not reconciled" in out, out)


# ---------- clean export (v2 N3, N8 short tier) ----------

def test_export() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proj = make_project(Path(tmp))
        (proj / "chapters" / "chapter-01.md").write_text(
            chapter_frontmatter(1, "canonical")
            + "\n他停在 A-301 号房门口，车牌是 M-208。\n",
            encoding="utf-8",
        )
        (proj / "chapters" / "chapter-02.md").write_text(
            chapter_frontmatter(2, "canonical", payoff="[C-001]")
            + "\n备注：草稿 --> 定稿，那把锁是 H-115 型。\n",
            encoding="utf-8",
        )
        out_file = proj / "exports" / "clean.md"
        code, out = run_cli(export.main, "export", proj, out_file)
        check("export: former false positives pass", code == 0, f"exit={code}\n{out}")
        text = out_file.read_text(encoding="utf-8")
        check("export: prose preserved verbatim",
              "A-301" in text and "M-208" in text and "-->" in text and "H-115" in text)

        code, out = run_cli(audit.main, "audit", proj, "--strict")
        check("export: post-export strict audit exit 0", code == 0, f"exit={code}\n{out}")

        (proj / "chapters" / "chapter-02.md").write_text(
            chapter_frontmatter(2, "draft") + "\n草稿。\n", encoding="utf-8"
        )
        code, out = run_cli(export.main, "export", proj, out_file, "--replace")
        check("export: draft chapter refused", code == 2 and "canonical" in out,
              f"exit={code}\n{out}")


# ---------- non-UTF-8 input (encoding robustness) ----------

def test_encoding() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proj = make_project(Path(tmp))
        (proj / "chapters" / "chapter-01.md").write_bytes(
            chapter_frontmatter(1, "draft").replace("title: t1", "title: 章节").encode("gbk")
        )
        code, out = run_cli(audit.main, "audit", proj)
        check("encoding: GBK chapter reported, not a traceback", code == 1
              and "not readable as UTF-8" in out and "Traceback" not in out, out)


# ---------- fresh project init (v1 P0-2) ----------

def test_init() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "fresh"
        code, _ = run_cli(init_project.main, "init", proj,
                          "--title", "测试", "--target-words", "80000")
        check("init: creates project", code == 0, f"exit={code}")
        code, out = run_cli(audit.main, "audit", proj)
        check("init: fresh project audits 0 error / 6 warning",
              code == 0 and "0 error(s), 6 warning(s)" in out, out)
        code, _ = run_cli(init_project.main, "init", proj,
                          "--title", "测试", "--target-words", "80000")
        check("init: refuses non-empty directory", code == 2, f"exit={code}")


def main() -> int:
    test_list_forms()
    test_clean_manuscript()
    test_bom()
    test_strict()
    test_conclusion_links()
    test_canonical_gate()
    test_export()
    test_encoding()
    test_init()
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
