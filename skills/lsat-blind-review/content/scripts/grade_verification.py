#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Grade a Blind Review workbook against an authoritative truth JSON.

This is a stricter, score-based audit. Use it after `verify_workbook.py` passes
(or instead of it) when you have a ground-truth JSON describing the correct
answer, the user's pick, and the stimulus anchor for every Q in the user's
wrong list.

Usage:
    python3 grade_verification.py --docx <docx> --truth <truth.json>

The truth JSON has this shape:

    {
      "questions": {
        "3": {"answer": "C", "user_pick": "B",
              "type": "Method/EXCEPT",
              "anchor": "How do the airlines expect to prevent",
              "critical_phrases": ["airline deregulation", "1980s"]},
        "7": {"answer": "A", "user_pick": "E", "anchor": "Golden Lake Development",
              "critical_phrases": [...]},
        ...
      },
      "header_pattern": "Day {qid} · Q{n} ·",        # optional
      "forbidden_part1": ["正确答案", "可迁移 Takeaway", "答案速览"],  # optional
      "section_titles": ["① 题型识别", "② 任务翻译", ...]    # optional)
    }

Output: a 0–100 score plus a per-section breakdown. Exit code is 0 if the
score is >= the threshold (default 90) and there are no FAIL checks; else 1.

The score is the simple sum of the points below (100 total):

    15 pts — docx readable + basic structure (Part I/II/III located)
    15 pts — answer speed-table triples all match truth
    20 pts — Part I contains zero forbidden analysis markers
    20 pts — every stimulus anchor present verbatim in Part I
    15 pts — per-Q analysis headers present in Part II + section titles appear
     5 pts — footer XML carries PAGE and NUMPAGES field codes
     5 pts — textutil convert succeeds + unzip -t reports no errors
     5 pts — document.xml contains the correct-answer shading (DCE6F1)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import zipfile
from typing import Any

from docx import Document


# --- config ------------------------------------------------------------------
DEFAULT_FORBIDDEN = ["正确答案", "可迁移 Takeaway", "答案速览",
                     "错因标签", "✓verified"]

DEFAULT_SECTION_TITLES = [
    "① 题型识别", "② 任务翻译", "③ 论证结构拆解", "④ BR 预判",
    "⑤ 正确答案为何对", "⑥ 你所选为何有吸引力又为何不对",
    "⑦ 其余选项排除", "⑧ 可迁移 Takeaway",
]


class Grade:
    def __init__(self) -> None:
        self.total = 0
        self.max = 0
        self.checks: list[tuple[str, int, int, list[str]]] = []  # (name, got, max, fails)

    def section(self, name: str, got: int, mx: int,
                fails: list[str] | None = None) -> None:
        self.total += got
        self.max += mx
        self.checks.append((name, got, mx, fails or []))
        status = "PASS" if not fails else f"FAIL ({len(fails)})"
        print(f"  [{status}] {name}: {got}/{mx}"
              + (f" — {', '.join(fails[:3])}"
                 + (" …" if len(fails) > 3 else "") if fails else ""))

    def header(self, label: str) -> None:
        print(f"\n{label}")

    def summary(self) -> None:
        print()
        pct = 100.0 * self.total / self.max if self.max else 0.0
        print(f"SCORE: {self.total}/{self.max} = {pct:.1f}")
        any_fail = any(c[3] for c in self.checks)
        if any_fail:
            print("FAILURES (sample, up to 3 per section):")
            for name, _, _, fails in self.checks:
                if fails:
                    print(f"  {name}:")
                    for f in fails[:3]:
                        print(f"    - {f}")


def _part_text(paragraphs: list[str]) -> tuple[str, str, str]:
    """Split paragraph list into (Part I, Part II, Part III) text."""
    i1 = i2 = i3 = -1
    for i, t in enumerate(paragraphs):
        if i1 < 0 and (t.startswith("Part I ·") or t.startswith("Part I ")):
            i1 = i
        elif i2 < 0 and (t.startswith("Part II ·") or t.startswith("Part II ")):
            i2 = i
        elif i3 < 0 and t.startswith("Part III"):
            i3 = i
    if i3 < 0:
        i3 = len(paragraphs)
    if i1 < 0 or i2 <= i1:
        raise RuntimeError("Part I/II headings not found")
    return ("\n".join(paragraphs[i1:i2]),
            "\n".join(paragraphs[i2:i3]),
            "\n".join(paragraphs[i3:]))


def _q_in_text(qid: int, text: str, pattern: str | None) -> bool:
    if pattern is None:
        for needle in (f"Q{qid}", f"Q{qid} ·", f"Q{qid}."):
            if needle in text:
                return True
        return False
    try:
        return re.search(pattern.format(q=qid, n=qid), text) is not None
    except re.error:
        return f"Q{qid}" in text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--docx", required=True)
    ap.add_argument("--truth", required=True,
                    help="JSON with the authoritative ground truth")
    ap.add_argument("--threshold", type=int, default=90,
                    help="minimum score (0-100) to exit 0; default 90")
    args = ap.parse_args()

    docx_path = args.docx
    truth_path = args.truth

    if not os.path.exists(docx_path):
        print(f"ERROR: docx not found: {docx_path}", file=sys.stderr)
        return 1
    if not os.path.exists(truth_path):
        print(f"ERROR: truth JSON not found: {truth_path}", file=sys.stderr)
        return 1

    print(f"Grading: {docx_path}")
    print(f"Truth:   {truth_path}")
    print(f"Pass threshold: {args.threshold}/100\n")

    with open(truth_path, "r", encoding="utf-8") as f:
        truth: dict[str, Any] = json.load(f)
    truth_qs: dict[str, dict[str, Any]] = truth.get("questions", {})

    forbidden = truth.get("forbidden_part1", DEFAULT_FORBIDDEN)
    section_titles = truth.get("section_titles", DEFAULT_SECTION_TITLES)
    header_pattern = truth.get("header_pattern")

    G = Grade()

    # --- 1. docx readable + structure (15 pts) ------------------------------
    G.header("1. docx readability + structure (15 pts)")
    try:
        doc = Document(docx_path)
        paragraphs = [p.text for p in doc.paragraphs]
        tables = doc.tables
        base = 10
        # basic structure
        try:
            p1_text, p2_text, p3_text = _part_text(paragraphs)
            G.section("docx opens + Part I/II/III located",
                      15, 15, [])
            base_pts = 15
        except RuntimeError:
            G.section("docx opens + Part I/II/III located",
                      base, 15, ["Part I/II/III headings missing"])
            base_pts = base
            p1_text = p2_text = p3_text = ""
    except Exception as e:
        G.section("docx opens", 0, 15, [str(e)])
        G.summary()
        return 1

    # --- 2. answer speed-table (15 pts) -------------------------------------
    G.header("2. answer speed-table triples (15 pts)")
    pts = 0
    fails: list[str] = []
    if not truth_qs:
        G.section("no truth_qs given — skipping", 15, 15, [])
    else:
        speed_tbl = None
        for tbl in tables:
            hdr = [c.text.strip() for c in tbl.rows[0].cells]
            if hdr and hdr[0] == "题号":
                speed_tbl = tbl
                break
        if speed_tbl is None:
            G.section("speed-table found", 0, 15, ["no table with 题号 header"])
        else:
            rows = {r.cells[0].text.strip(): r.cells for r in speed_tbl.rows[1:]}
            per_q = 15 / max(1, len(truth_qs))
            for qid_str, q in truth_qs.items():
                key = f"Q{qid_str}"
                if key not in rows and qid_str in rows:
                    key = qid_str
                if key not in rows:
                    fails.append(f"{key}: missing")
                    continue
                cells = rows[key]
                got_correct = cells[2].text.strip() if len(cells) > 2 else ""
                got_user = cells[3].text.strip() if len(cells) > 3 else ""
                exp_correct = q.get("answer", "")
                exp_user = q.get("user_pick", "")
                if exp_correct and got_correct != exp_correct:
                    fails.append(f"{key}: correct {got_correct}!={exp_correct}")
                else:
                    pts += per_q / 2
                if exp_user and got_user != exp_user:
                    fails.append(f"{key}: user {got_user}!={exp_user}")
                else:
                    pts += per_q / 2
            G.section("every (题号, 正确答案, 你的答案) triple matches",
                      round(pts), 15, fails)

    # --- 3. Part I forbidden markers (20 pts) --------------------------------
    G.header("3. Part I forbidden markers (20 pts)")
    if not p1_text:
        G.section("Part I empty — skipping", 0, 20, ["Part I not located"])
    elif not forbidden:
        G.section("no forbidden list — skipping", 20, 20, [])
    else:
        per_q = 20 / max(1, len(truth_qs)) if truth_qs else 20
        fails = []
        lost = 0
        for tok in forbidden:
            n = p1_text.count(tok)
            if n > 0:
                lost += per_q
                fails.append(f"{tok} x{n}")
        G.section("Part I contains zero forbidden markers",
                  round(20 - min(20, lost)), 20, fails)

    # --- 4. stimulus verbatim anchors (20 pts) ------------------------------
    G.header("4. stimulus verbatim anchors (20 pts)")
    if not truth_qs:
        G.section("no truth_qs — skipping", 20, 20, [])
    elif not p1_text:
        G.section("Part I empty — skipping", 0, 20, ["Part I not located"])
    else:
        norm = lambda s: re.sub(r"\s+", " ", s).strip()
        p1n = norm(p1_text)
        per_q = 20 / max(1, len(truth_qs))
        pts = 0
        fails = []
        for qid_str, q in truth_qs.items():
            anchor = q.get("anchor")
            if not anchor:
                # no anchor for this Q — give credit
                pts += per_q
                continue
            if norm(anchor) in p1n:
                pts += per_q
            else:
                fails.append(f"Q{qid_str}: anchor {anchor!r} not found")
        G.section("every stimulus anchor present verbatim in Part I",
                  round(pts), 20, fails)

    # --- 5. per-Q analysis in Part II (15 pts) -------------------------------
    G.header("5. per-Q analysis + section titles (15 pts)")
    if not truth_qs:
        G.section("no truth_qs — skipping", 15, 15, [])
    elif not p2_text:
        G.section("Part II empty — skipping", 0, 15, ["Part II not located"])
    else:
        per_q = 10 / max(1, len(truth_qs))
        pts = 0
        fails = []
        for qid_str in truth_qs:
            if _q_in_text(int(qid_str), p2_text, header_pattern):
                pts += per_q
            else:
                fails.append(f"Q{qid_str}: analysis not found in Part II")
        # bonus 5 pts: every section title appears >= |truth_qs| times
        sec_pts = 5
        sec_fails = []
        for st in section_titles:
            if p2_text.count(st) < len(truth_qs):
                sec_pts = 0
                sec_fails.append(f"{st} count={p2_text.count(st)}")
        pts += sec_pts
        G.section("per-Q analysis in Part II + section titles present",
                  round(pts), 15, fails + sec_fails)

    # --- 6. footer PAGE / NUMPAGES (5 pts) -----------------------------------
    G.header("6. footer PAGE / NUMPAGES (5 pts)")
    with zipfile.ZipFile(docx_path) as z:
        footer_files = [n for n in z.namelist() if "footer" in n]
        page_ok = numpages_ok = False
        for fn in footer_files:
            content = z.read(fn).decode("utf-8", errors="ignore")
            if "PAGE" in content:
                page_ok = True
            if "NUMPAGES" in content:
                numpages_ok = True
        fails = []
        if not footer_files:
            fails.append("no footer XML")
        if not page_ok:
            fails.append("PAGE field missing")
        if not numpages_ok:
            fails.append("NUMPAGES field missing")
        G.section("footer XML carries PAGE + NUMPAGES",
                  5 if not fails else 0, 5, fails)
        doc_xml = z.read("word/document.xml").decode("utf-8")

    # --- 7. textutil + unzip (5 pts) ----------------------------------------
    G.header("7. textutil + unzip integrity (5 pts)")
    zr = subprocess.run(["unzip", "-t", docx_path], capture_output=True, text=True)
    tu = subprocess.run(["textutil", "-convert", "txt", "-stdout", docx_path],
                        capture_output=True, text=True)
    fails = []
    if not (zr.returncode == 0 and "No errors" in zr.stdout):
        fails.append("unzip -t failed")
    if not (tu.returncode == 0 and len(tu.stdout) > 1000):
        fails.append(f"textutil failed ({len(tu.stdout)} chars)")
    G.section("textutil + unzip -t pass", 5 if not fails else 0, 5, fails)

    # --- 8. shading (5 pts) --------------------------------------------------
    G.header("8. correct-answer shading (5 pts)")
    has_shading = "DCE6F1" in doc_xml
    G.section("document.xml contains DCE6F1 shading",
              5 if has_shading else 0, 5,
              [] if has_shading else ["no DCE6F1 shading found"])

    # --- summary -------------------------------------------------------------
    G.summary()
    if G.total >= args.threshold and all(not c[3] for c in G.checks):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())