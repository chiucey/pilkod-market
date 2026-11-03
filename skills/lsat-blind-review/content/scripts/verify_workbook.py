#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generic verification harness for a Blind Review (BR) workbook .docx.

Run this against any Blind Review deliverable produced under the
lsat-blind-review skill. It does NOT rebuild the docx; it only reads it and
reports PASS/FAIL on the standard invariants listed in SKILL.md.

Usage:
    python3 verify_workbook.py --docx <path-to-docx>
    python3 verify_workbook.py --docx <path> --meta <path-to-meta.json>

The optional --meta JSON has this shape (every section is optional; missing
sections skip their respective checks):

    {
      "wrong_qs":           [3, 7, 10, ...],          # ints, the user's Q-numbers
      "user_answers":       {"3": "B", "7": "E"},     # str qid -> user's letter
      "answer_key":         {"3": "C", "7": "A"},     # str qid -> correct letter
      "anchors":            {"3": "airlines", "7": "Golden Lake"},
      "critical_phrases":   ["psychotherapy", ...],   # must appear verbatim in full doc
      "forbidden_part1":    ["正确答案", "可迁移 Takeaway", "答案速览"],
      "header_pattern":     "Day {qid} · Q{n} ·",     # optional regex per card heading
      "speed_table_header": ["题号", "题型", "正确答案", "你的答案"]
    }

Without --meta the harness only runs the minimum sanity checks (docx opens,
unzip -t, textutil, footer PAGE/NUMPAGES, default forbidden tokens absent
from Part I).

Exit code: 0 if all PASS, 1 if any FAIL.
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


# --- default config ----------------------------------------------------------
DEFAULT_FORBIDDEN_PART1 = ["正确答案", "可迁移 Takeaway", "答案速览",
                           "错因标签", "✓verified"]

DEFAULT_SPEED_HEADER = ["题号", "题型", "正确答案", "你的答案"]

DEFAULT_PART_DELIMS = [
    ("Part I ·",  "Part II ·"),
    ("Part I ",   "Part II "),
]


class Results:
    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []

    def check(self, name: str, cond: bool, detail: str = "") -> bool:
        status = "PASS" if cond else "FAIL"
        line = f"  [{status}] {name}" + (f" — {detail}" if detail else "")
        print(line)
        (self.passed if cond else self.failed).append(name)
        return cond

    def summary(self) -> None:
        print()
        print(f"{len(self.passed)} passed, {len(self.failed)} failed")
        if self.failed:
            print("FAILURES:")
            for n in self.failed:
                print(f"  - {n}")


def locate_parts(paragraphs: list[str]) -> tuple[int, int, int]:
    """Return (i_part1, i_part2, i_part3) paragraph indices.

    Tries both literal "Part I ·" and ASCII "Part I " delimiters. If Part III
    is missing, i_part3 is len(paragraphs). Raises if Part I or Part II not
    found.
    """
    text = paragraphs
    i1 = i2 = i3 = -1
    for d1, d2 in DEFAULT_PART_DELIMS:
        for i, t in enumerate(text):
            if i1 < 0 and t.startswith(d1):
                i1 = i
            elif i2 < 0 and t.startswith(d2):
                i2 = i
            elif i3 < 0 and t.startswith("Part III"):
                i3 = i
        if i1 >= 0 and i2 > i1:
            break
    if i3 < 0:
        i3 = len(text)
    if i1 < 0 or i2 <= i1:
        raise RuntimeError(
            "Could not locate both 'Part I' and 'Part II' headings. "
            "Did the build script forget to emit them?"
        )
    return i1, i2, i3


def part1_part2_text(paragraphs: list[str]) -> tuple[str, str, str]:
    i1, i2, i3 = locate_parts(paragraphs)
    p1 = "\n".join(paragraphs[i1:i2])
    p2 = "\n".join(paragraphs[i2:i3])
    p3 = "\n".join(paragraphs[i3:])
    return p1, p2, p3


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--docx", required=True, help="path to the BR workbook .docx")
    ap.add_argument("--meta", help="optional JSON with workbook-specific data")
    args = ap.parse_args()

    docx_path = args.docx
    if not os.path.exists(docx_path):
        print(f"ERROR: docx not found: {docx_path}", file=sys.stderr)
        return 1

    meta: dict[str, Any] = {}
    if args.meta:
        if not os.path.exists(args.meta):
            print(f"ERROR: meta JSON not found: {args.meta}", file=sys.stderr)
            return 1
        with open(args.meta, "r", encoding="utf-8") as f:
            meta = json.load(f)

    print(f"Verifying: {docx_path}")
    print(f"Size: {os.path.getsize(docx_path)} bytes")
    if meta:
        print(f"Meta: {args.meta}")
    print()

    R = Results()

    # --- 1. python-docx readable --------------------------------------------
    try:
        doc = Document(docx_path)
        R.check("python-docx can read the file", True,
                f"{len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables")
    except Exception as e:
        R.check("python-docx can read the file", False, str(e))
        R.summary()
        return 1

    paragraphs = [p.text for p in doc.paragraphs]
    tables = doc.tables

    # collect cell text too (some meta lives only in tables)
    all_cell_text = "\n".join(
        c.text for tbl in tables for row in tbl.rows for c in row.cells
    )
    full_text = "\n".join(paragraphs) + "\n" + all_cell_text

    # --- 2. zip integrity + textutil ----------------------------------------
    zr = subprocess.run(["unzip", "-t", docx_path], capture_output=True, text=True)
    R.check("unzip -t reports no errors",
            zr.returncode == 0 and "No errors" in zr.stdout)

    tu = subprocess.run(["textutil", "-convert", "txt", "-stdout", docx_path],
                        capture_output=True, text=True)
    R.check("textutil -convert txt succeeds",
            tu.returncode == 0 and len(tu.stdout) > 1000,
            f"{len(tu.stdout)} chars")

    # --- 3. footer PAGE / NUMPAGES field codes -------------------------------
    with zipfile.ZipFile(docx_path) as z:
        footer_files = [n for n in z.namelist() if "footer" in n]
        page_ok = numpages_ok = False
        for fn in footer_files:
            content = z.read(fn).decode("utf-8", errors="ignore")
            if "PAGE" in content:
                page_ok = True
            if "NUMPAGES" in content:
                numpages_ok = True
        R.check("footer XML files exist", bool(footer_files),
                ", ".join(footer_files))
        R.check("PAGE field code in footer", page_ok)
        R.check("NUMPAGES field code in footer", numpages_ok)
        doc_xml = z.read("word/document.xml").decode("utf-8")

    # --- 4. no literal markdown emphasis markers leaked into the doc --------
    bad_md = {m: full_text.count(m) for m in ("**", "__", "##")
              if full_text.count(m) > 0}
    R.check("no literal markdown markers rendered in the document",
            not bad_md, str(bad_md))

    # --- locate Part I / II / III --------------------------------------------
    try:
        p1_text, p2_text, p3_text = part1_part2_text(paragraphs)
    except RuntimeError as e:
        R.check("Part I and Part II headings located", False, str(e))
        R.summary()
        return 1
    R.check("Part I and Part II headings located", True)

    # --- 5. forbidden tokens absent from Part I ------------------------------
    forbidden = meta.get("forbidden_part1", DEFAULT_FORBIDDEN_PART1)
    leak = {tok: p1_text.count(tok) for tok in forbidden if p1_text.count(tok) > 0}
    R.check("Part I contains zero answer/analysis markers",
            not leak, str(leak))

    # --- 6. all Q-ids in Part I and Part II (if meta.wrong_qs given) ---------
    wrong_qs: list[int] = meta.get("wrong_qs", [])
    if wrong_qs:
        missing_p1 = [q for q in wrong_qs
                      if not _q_in_text(q, p1_text, meta.get("header_pattern"))]
        missing_p2 = [q for q in wrong_qs
                      if not _q_in_text(q, p2_text, meta.get("header_pattern"))]
        R.check(f"all {len(wrong_qs)} Q ids appear in Part I",
                not missing_p1, str(missing_p1))
        R.check(f"all {len(wrong_qs)} Q ids appear in Part II",
                not missing_p2, str(missing_p2))

    # --- 7. answer speed-table integrity (if meta.answer_key given) ---------
    answer_key: dict[str, str] = meta.get("answer_key", {})
    user_answers: dict[str, str] = meta.get("user_answers", {})
    speed_header = meta.get("speed_table_header", DEFAULT_SPEED_HEADER)
    if answer_key or user_answers:
        speed_tbl = None
        for tbl in tables:
            hdr = [c.text.strip() for c in tbl.rows[0].cells]
            if hdr[:len(speed_header)] == speed_header:
                speed_tbl = tbl
                break
        R.check("answer speed-table found", speed_tbl is not None)
        if speed_tbl:
            rows = {r.cells[0].text.strip(): r.cells for r in speed_tbl.rows[1:]}
            if wrong_qs:
                R.check(f"speed-table has {len(wrong_qs)} rows",
                        len(rows) == len(wrong_qs), f"found {len(rows)}")
            bad: list[str] = []
            for qid in wrong_qs:
                key = f"Q{qid}" if f"Q{qid}" in rows else str(qid)
                if key not in rows:
                    bad.append(f"{key}: missing")
                    continue
                cells = rows[key]
                got_correct = cells[2].text.strip() if len(cells) > 2 else ""
                got_user = cells[3].text.strip() if len(cells) > 3 else ""
                exp_correct = answer_key.get(str(qid))
                exp_user = user_answers.get(str(qid))
                if exp_correct is not None and got_correct != exp_correct:
                    bad.append(f"{key}: correct {got_correct}!={exp_correct}")
                if exp_user is not None and got_user != exp_user:
                    bad.append(f"{key}: user {got_user}!={exp_user}")
            R.check("every (题号, 正确答案, 你的答案) triple matches",
                    not bad, "; ".join(bad))

    # --- 8. stimulus verbatim anchors (if meta.anchors given) ---------------
    anchors: dict[str, str] = meta.get("anchors", {})
    if anchors and wrong_qs:
        norm = lambda s: re.sub(r"\s+", " ", s).strip()
        p1n = norm(p1_text)
        missing_a = []
        for qid in wrong_qs:
            a = anchors.get(str(qid))
            if a and norm(a) not in p1n:
                missing_a.append(f"Q{qid}:{a!r}")
        R.check("all stimulus anchors present verbatim in Part I",
                not missing_a, "; ".join(missing_a))

    # --- 9. critical phrases (across full doc, not just Part I) -------------
    critical: list[str] = meta.get("critical_phrases", [])
    if critical:
        miss = [c for c in critical if c not in full_text]
        R.check("critical phrases present verbatim",
                not miss, "; ".join(miss))

    # --- 10. shading for correct answers (only if Part II uses it) ---------
    if "DCE6F1" in str(meta):
        R.check("light-blue DCE6F1 shading used for correct answers",
                "DCE6F1" in doc_xml)

    # --- summary -------------------------------------------------------------
    R.summary()
    return 0 if not R.failed else 1


def _q_in_text(qid: int, text: str, pattern: str | None) -> bool:
    """Return True if Q{qid} shows up in `text` under the expected card pattern.

    If pattern is None, default to "Q{qid}" as a substring (good enough for
    most headers that read `Day X · Q{n} · ...` or `PT107 S1 · Q{n} · ...`).
    """
    if pattern is None:
        # Try a few common renderings before falling back to bare "Q{n}".
        for needle in (f"Q{qid}", f"Q{qid} ·", f"Q{qid}."):
            if needle in text:
                return True
        return False
    try:
        return re.search(pattern.format(q=qid, n=qid), text) is not None
    except re.error:
        return f"Q{qid}" in text


if __name__ == "__main__":
    sys.exit(main())