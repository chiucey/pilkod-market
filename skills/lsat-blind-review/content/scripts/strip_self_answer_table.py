#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Strip the BR self-answer table (and its 【BR 自答】 heading) from a Blind
Review workbook .docx.

Background
----------
Already-delivered BR workbooks (e.g.
`/Users/log/LSAT_LR_Day1_Blind_Review_解析_v1.docx`,
`/Users/log/LSAT_LR_Principle_Identify_Section3_Blind_Review_解析_v1.docx`)
contain a small 4-column "BR 自答" table at the end of each Part I question
card so the reader can hand-fill 题型预判 / 我的答案 / 信心 1–5 / 判断依据.

The current default per SKILL.md is to NOT emit this table on new builds.
For already-delivered workbooks the user can choose to keep the table
(filling it in by hand) or strip it. This script handles the second case
without rebuilding the docx from scratch.

What it does
------------
1. Open the docx with python-docx and walk the body in document order.
2. For every `<w:tbl>` whose first row text contains both `我的答案` and
   `信心`, mark the table element for removal.
3. For each removed table, also remove the immediately-preceding paragraph
   if its text equals `【BR 自答】` (the heading that introduces it).
4. Write the result to a new file (or overwrite the original with
   `--inplace`).

Nothing else in the document is touched: Part I stimulus / stem / options
text, Part II analysis, Part III weakness report, answer speed-table, page
geometry, footers — all stay byte-identical.

Usage
-----
    python3 strip_self_answer_table.py --docx <input.docx> --out <output.docx>
    python3 strip_self_answer_table.py --docx <input.docx> --inplace

Exit code 0 on success, non-zero if no BR self-answer tables were found
(so the user knows the script didn't actually do anything), or if the file
is missing.
"""

from __future__ import annotations

import argparse
import os
import sys

from docx import Document
from docx.oxml.ns import qn


BR_HEADING_TEXT = "【BR 自答】"
BR_TABLE_MARKERS = ("我的答案", "信心")


def _cell_text(cell) -> str:
    """Return the concatenated text of a docx table cell."""
    return "".join(p.text for p in cell.paragraphs).strip()


def _is_br_table(tbl) -> bool:
    """Return True if the table's header row text matches the BR self-answer
    pattern (any 2 of the standard column names are present).

    The standard header is 题型预判 / 我的答案 / 信心 1–5 / 判断依据（一句话）.
    Requiring all 4 exact strings is too brittle (some builds drop the dash,
    some use 信心（高/中/低）, etc.); requiring both 我的答案 and 信心 is
    the stable anchor.
    """
    if not tbl.rows:
        return False
    header_text = " ".join(_cell_text(c) for c in tbl.rows[0].cells)
    return all(m in header_text for m in BR_TABLE_MARKERS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--docx", required=True, help="input BR workbook .docx")
    ap.add_argument("--out", help="output .docx (required unless --inplace)")
    ap.add_argument("--inplace", action="store_true",
                    help="overwrite the input file in place")
    args = ap.parse_args()

    if not args.inplace and not args.out:
        print("ERROR: pass --out <path> or --inplace", file=sys.stderr)
        return 2

    in_path = args.docx
    out_path = args.docx if args.inplace else args.out
    if not os.path.exists(in_path):
        print(f"ERROR: input not found: {in_path}", file=sys.stderr)
        return 1
    if not args.inplace and os.path.exists(out_path):
        print(f"NOTE: output already exists and will be overwritten: {out_path}")

    doc = Document(in_path)
    body = doc.element.body

    # walk body children in document order; track previous element for heading.
    children = list(body)
    removed_tables = 0
    removed_headings = 0

    # We delete via parent.remove() so the lxml tree stays valid. Collect
    # targets first so iteration isn't disturbed by removal mid-loop.
    targets: list[tuple] = []  # (prev_element_or_None, table_element)
    prev: object = None
    for child in children:
        tag = child.tag
        if tag == qn("w:tbl"):
            tbl_obj = None
            for t in doc.tables:
                if t._element is child:
                    tbl_obj = t
                    break
            if tbl_obj is not None and _is_br_table(tbl_obj):
                targets.append((prev, child))
        prev = child

    for prev_el, tbl_el in targets:
        # remove the heading paragraph if it immediately precedes and matches
        if prev_el is not None and prev_el.tag == qn("w:p"):
            txt = "".join(t.text or "" for t in prev_el.iter(qn("w:t"))).strip()
            if txt == BR_HEADING_TEXT:
                body.remove(prev_el)
                removed_headings += 1
        body.remove(tbl_el)
        removed_tables += 1

    doc.save(out_path)

    size_in = os.path.getsize(in_path)
    size_out = os.path.getsize(out_path)
    print(f"Input : {in_path}  ({size_in} bytes)")
    print(f"Output: {out_path}  ({size_out} bytes)")
    print(f"Removed {removed_tables} BR self-answer table(s) and "
          f"{removed_headings} 【BR 自答】 heading(s).")
    print(f"Saved {size_in - size_out:+d} bytes.")

    if removed_tables == 0:
        print()
        print("WARNING: no BR self-answer tables were found. Either the file "
              "doesn't have them, or the markers (我的答案 / 信心) didn't "
              "match the header text. Re-run --inplace against a backup if "
              "you expected changes.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())