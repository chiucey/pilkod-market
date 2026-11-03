#!/usr/bin/env python3
"""Regression tests for the LaTeX->Unicode pipeline and the build guards.

Run:  python3 -B .skills/course-review/scripts/test_pipeline.py
Each case here corresponds to a bug that actually shipped broken at least once.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import latex_to_unicode as L          # noqa: E402
import build_panel as B              # noqa: E402

FAILS = []


def ok(cond, msg):
    print(("  ok  : " if cond else "  FAIL: ") + msg)
    if not cond:
        FAILS.append(msg)


def real_latex_left(s):
    """LaTeX commands left in a string, ignoring \\n-prefixed lookalikes."""
    return re.findall(r"\\(?!n[A-Za-z]*[\(\{\[])[A-Za-z]+", s)


def t_convert():
    print("convert_math")
    cases = [
        (r"P \to Q", "P → Q", "to"),
        (r"\neg P \lor Q", "¬ P ∨ Q", "neg/lor"),
        (r"(\forall x)(\exists y)P", "∀", "quantifiers"),
        (r"\min\{0.5, 0.6\}", "min", "min"),
        (r"\max\{0, 0.8\}", "max", "max"),
        (r"M_1 \oplus M_2", "⊕", "oplus"),
        (r"K = 1 - \sum_{x\cap y=\varnothing}", "∅", "sum/varnothing"),
        (r"\boxed{\{\neg P(x)\lor Q(x),\ \neg P(y)\lor R(y)\}}", "¬", "nested boxed"),
        (r"\boxed{0.87}", "0.87", "simple boxed"),
        (r"1.05 \bigl[ 0.09 \times 0.02 \bigr]", "×", "bigl/bigr"),
        (r"\text{CF}(H,E)", "CF(H,E)", "text"),
        (r"A \xrightarrow{证毕} B", "A → B", "xrightarrow with label"),
        (r"Bel(A) \leq Pl(A)", "≤", "le"),
        (r"LIKE(x,y)", "LIKE(x,y)", "ascii comma kept"),
    ]
    for src, expect, label in cases:
        got = L.convert_math(src)
        ok(expect in got, f"{label}: {src!r} -> {got!r}")
        ok(not real_latex_left(got), f"{label}: no latex left")


def t_lookalike():
    print("newline lookalike (bug 5)")
    for src in [r"\nCF(E)", r"\nBel(\{h_1\})", r"\nM(\{h\})"]:
        got = L.convert_math(src)
        ok("nCF" in got or "nBel" in got or "nM" in got,
           f"newline+name preserved: {src!r} -> {got!r}")


def t_subscript():
    print("subscripts & blanks")
    got = L.convert_text("推理是由已知事实（____）出发，C_1 和 C_2 称为 C_{12} 的____。")
    ok(got.count("____") == 2, f"fill blanks survive: {got!r}")
    ok("<sub>1</sub>" in got and "<sub>12</sub>" in got, "subscripts emitted")
    ok("&lt;sub&gt;" not in got, "no double-escaped sub")


def t_guards():
    print("build_panel guards")
    tmp = Path(tempfile.mkdtemp())
    build = HERE / "build_panel.py"

    def run(payload, skip=True):
        f = tmp / "t.json"
        f.write_text(payload, encoding="utf-8")
        r = subprocess.run(
            [sys.executable, "-B", str(build), str(f), "-o", str(tmp / "o.html"),
             "--skip-convert" if skip else "--auto", *([] if skip else [])],
            capture_output=True, text=True)
        return r.returncode, (r.stderr or "") + (r.stdout or "")

    # raw LaTeX must be rejected
    card = ('[{"title":"T","summary":"s","cards":[{"id":"a","type":"concept",'
            '"difficulty":1,"question":"$\\\\min\\\\{1,2\\\\}$","answer":"a"}]}]')
    rc, out = run(card)
    ok(rc != 0 and "unconverted LaTeX" in out, "raw LaTeX rejected")
    rc, out = run(card.replace("$\\\\min\\\\{1,2\\\\}$", "1.05 \\\\bigl[ x"))
    ok(rc != 0, "bigl (control char) rejected")
    rc, out = run('[{"title":"T","summary":"s","cards":[{"id":"a","type":"fill",'
                  '"difficulty":1,"question":"no blank","answer":"a"}]}]')
    ok(rc != 0 and "____" in out, "fill card without blank rejected")
    rc, out = run('[{"title":"T","summary":"s","cards":[{"id":"a","type":"concept",'
                  '"difficulty":9,"question":"q","answer":"a"}]}]')
    ok(rc != 0 and "difficulty" in out, "out-of-range difficulty rejected")
    rc, out = run('[{"title":"T","summary":"s","cards":[{"id":"a","type":"concept",'
                  '"difficulty":1,"question":"q","answer":"a"},'
                  '{"id":"a","type":"concept","difficulty":1,"question":"q","answer":"a"}]}]')
    ok(rc != 0 and "duplicate" in out, "duplicate id rejected")
    # valid card must pass
    good = ('[{"title":"T","summary":"s","cards":[{"id":"a","type":"concept",'
            '"difficulty":1,"question":"P → Q 是什么意思？","answer":"蕴含"}]}]')
    rc, out = run(good)
    ok(rc == 0, f"valid card accepted (rc={rc}) {out.strip()[:80]}")


t_convert()
t_lookalike()
t_subscript()
t_guards()
print()
if FAILS:
    print(f"{len(FAILS)} FAILURES")
    for f in FAILS:
        print("  - " + f)
    sys.exit(1)
print("ALL PASS")
