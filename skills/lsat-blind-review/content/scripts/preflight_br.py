"""preflight_br.py — lsat-blind-review pre-flight check.

Mirrors the style of /Users/log/.agents/skills/lsat-pdf-to-section-docx/scripts/
preflight.py. Run BEFORE writing any builder, after the user has supplied a PDF
+ wrong-question list. Exits non-zero on any hard failure; prints a one-line
PASS/FAIL per check.

Hard checks performed (in order):

  1. Output filename matches LSAT_LR_<scope>_Blind_Review_解析_v{n}.docx and
     does not collide with an existing file in the project root.
  2. The PDF (or pre-extracted text file) exists and is openable.
  3. The source has a usable text layer OR an --ocr flag has been set (raw
     image-only PDFs are out of scope; the sibling lsat-pdf-to-section-docx
     skill handles those).
  4. python-docx is importable.
  5. If --user-qids is supplied, the source's Q-numbers are enumerated and
     the user list is verified to be a subset. This is the v2-failure-mode
     backstop — the same check extract_qids.py does, inlined here so a
     preflight-only run still blocks mis-mapping before any code is written.
  6. If --anchor is supplied AND --user-qids is supplied, anchor keywords
     are checked against the chunks (only meaningful for shape=plain).

Always-true reminders printed (NOT failures, just guidance):
  - "Run PDF Q-Number Extraction Protocol before trusting any LLM/agent
     that the user's question numbers map to the PDF's question numbers."
  - "Never cross-match Q-numbers by content keywords."
  - "Tag ✓verified only when ≥1 independent prep page confirms the answer
     against the CORRECT stimulus; ~ for best-guess mirrors, ? otherwise."

Usage:
    python3 preflight_br.py <pdf> <out_docx_name> [--user-qids 3,7,17]
                                                  [--anchor "Q3:airlines;Q17:Danaxil"]
                                                  [--ocr]

Exit codes:
    0  all hard checks pass
    1  one or more hard checks failed
    2  usage error
    3  source PDF unreadable / has no text layer
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    pdfplumber = None  # only required for PDF inputs

# Filename convention: LSAT_LR_<scope>_Blind_Review_解析_v{n}.docx
# scope may contain letters, digits, underscores, hyphens, Chinese characters.
FILENAME_RE = re.compile(
    r"^LSAT_LR_(?P<scope>[A-Za-z0-9_\-一-鿿]+)_Blind_Review_解析_v(?P<n>\d+(?:\.\d+)?)\.docx$"
)


def _check(label: str, ok: bool, hint: str = "") -> bool:
    mark = "OK  " if ok else "FAIL"
    print(f"  [{mark}] {label}", flush=True)
    if hint and not ok:
        print(f"         {hint}", flush=True)
    return ok


def _reminder(msg: str) -> None:
    print(f"  [.. ] {msg}", flush=True)


def _check_filename(name: str, project_root: str) -> tuple[bool, str]:
    """Verify filename matches the convention and doesn't collide."""
    m = FILENAME_RE.match(name)
    if not m:
        return False, (
            f"filename must match LSAT_LR_<scope>_Blind_Review_解析_v<n>.docx "
            f"(got {name!r})"
        )
    full = os.path.join(project_root, name)
    if os.path.exists(full):
        return False, (
            f"a file already exists at {full}; rename the existing one "
            f"(e.g. {name}.bakN) or use a new v<n>"
        )
    return True, ""


def _check_source(source: str, allow_ocr: bool) -> tuple[bool, str, str, int]:
    """Open source; return (ok, full_text, hint, page_count). Empty text on fail."""
    if not os.path.exists(source):
        return False, "", f"no such file: {source}", 0
    if source.lower().endswith(".pdf"):
        if pdfplumber is None:
            return False, "", "pdfplumber is not installed (pip install pdfplumber)", 0
        try:
            with pdfplumber.open(source) as pdf:
                page_count = len(pdf.pages)
                p1 = pdf.pages[0].extract_text() or ""
                full = "\n".join((p.extract_text() or "") for p in pdf.pages)
        except Exception as exc:
            return False, "", f"cannot open PDF: {exc!r}", 0
        if len(full) < 200 and not allow_ocr:
            return False, full, (
                f"PDF text layer only {len(full)} chars; this skill assumes a "
                f"text-layer-bearing Cambridge LR source. Pass --ocr if you "
                f"have already pre-OCR'd this PDF into a .txt next to it, or "
                f"switch to lsat-pdf-to-section-docx for raw image-only scans."
            ), page_count
        return True, full, "", page_count
    else:
        try:
            full = Path(source).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            full = Path(source).read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return False, "", f"cannot read text source: {exc!r}", 0
        page_count = full.count("\x0c") + 1
        return True, full, "", page_count


# Same markers as extract_qids.py — keep in sync.
PLAIN_MARKER_RE = re.compile(r"Q(\d+)\.\s*\[")
QUESTION_MARKER_RE = re.compile(r"^\s*Question\s+(\d+)\s*$", re.MULTILINE)


def _parse_user_qids(arg: str | None) -> list[int]:
    if not arg:
        return []
    out: list[int] = []
    for tok in arg.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if not tok.isdigit():
            sys.stderr.write(f"preflight_br.py: --user-qids token {tok!r} is not a positive integer.\n")
            sys.exit(2)
        out.append(int(tok))
    return sorted(set(out))


def _parse_anchor_spec(arg: str | None) -> dict[str, list[str]]:
    if not arg:
        return {}
    out: dict[str, list[str]] = {}
    for entry in arg.split(";"):
        entry = entry.strip()
        if not entry or ":" not in entry:
            continue
        qid_str, kw_list = entry.split(":", 1)
        qid_str = qid_str.strip()
        kws = [k.strip() for k in kw_list.split(",") if k.strip()]
        if qid_str and kws:
            out[qid_str] = kws
    return out


def _resolve_chunk_key(qid_str: str) -> str:
    s = qid_str.strip()
    if s.lower().startswith("question"):
        s = s.split(None, 1)[1] if len(s.split(None, 1)) > 1 else s
    if s.upper().startswith("Q"):
        s = s[1:]
    return s


def _check_user_qids(qids: list[int], user_qids: list[int]) -> bool:
    """Cross-check user Q-list against enumerated PDF Q-ids; return True iff subset."""
    qid_set = set(qids)
    found = [q for q in user_qids if q in qid_set]
    missing = [q for q in user_qids if q not in qid_set]
    if missing:
        print(
            "\n"
            "============================================================\n"
            "STOP: user-listed Q-number(s) not found in source.\n"
            f"  Source enumerated Q-ids: {qids[0]}..{qids[-1]}  (n={len(qids)})\n"
            f"  User Q-ids requested:    {user_qids}\n"
            f"  MISSING from source:     {missing}\n"
            "------------------------------------------------------------\n"
            "Per SKILL.md Hard Rule #9, do NOT cross-match by content keywords.\n"
            "Ask the user to confirm the intended Q-number(s) before proceeding.\n"
            "============================================================\n",
            file=sys.stderr,
        )
        return False
    _reminder(f"user Q-ids {user_qids} all present in source (n={len(found)})")
    return True


def _chunk_plain_for_anchors(full: str) -> dict[str, str]:
    """Split full text on Q-label boundaries (only used for anchor sampling)."""
    parts = re.split(r"(?=Q(\d+)\.\s*\[)", full)
    out: dict[str, str] = {}
    i = 1
    while i < len(parts):
        header = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        if header.isdigit():
            out[header] = (header + body).strip()
        i += 2
    return out


def _check_anchors(chunks: dict[str, str], anchors: dict[str, list[str]]) -> bool:
    overall_ok = True
    for qid_str, kws in anchors.items():
        chunk_key = _resolve_chunk_key(qid_str)
        chunk = chunks.get(chunk_key, "")
        chunk_compact = re.sub(r"\s+", "", chunk).lower()
        present, missing = [], []
        for kw in kws:
            kl = kw.lower()
            kw_compact = re.sub(r"\s+", "", kl)
            if kl in chunk.lower():
                present.append(kw)
            elif kw_compact and kw_compact in chunk_compact:
                present.append(kw)
            else:
                missing.append(kw)
        status = "OK  " if not missing else "FAIL"
        detail = f"{qid_str}: present={present} missing={missing}"
        print(f"  [{status}] anchor {detail}", flush=True)
        if missing:
            overall_ok = False
    return overall_ok


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="preflight_br.py",
        description=(
            "Pre-flight check for the lsat-blind-review skill. Runs the "
            "PDF Q-Number Extraction Protocol and stops on any hard failure."
        ),
    )
    ap.add_argument("source", help="path to the PDF (or pre-extracted .txt)")
    ap.add_argument(
        "out_docx",
        help="intended output filename, must match LSAT_LR_<scope>_Blind_Review_解析_v<n>.docx",
    )
    ap.add_argument(
        "--project-root",
        default="/Users/log",
        help="project root where the deliverable will be written (default /Users/log)",
    )
    ap.add_argument(
        "--user-qids",
        default="",
        help="comma-separated user wrong-question numbers, e.g. 3,7,17",
    )
    ap.add_argument(
        "--anchor",
        default="",
        help="anchor-keyword spec, e.g. 'Q3:airlines,prevent;Q17:Danaxil'",
    )
    ap.add_argument(
        "--ocr",
        action="store_true",
        help="acknowledge that the source is image-only and pre-OCR'd into a text file",
    )
    args = ap.parse_args()

    failures = 0
    print("preflight_br: lsat-blind-review")
    print(f"  source:      {args.source}")
    print(f"  out_docx:    {args.out_docx}")
    print(f"  project_root:{args.project_root}")
    print()

    # 1. Filename convention + collision
    ok_name, name_hint = _check_filename(args.out_docx, args.project_root)
    if not _check(f"output filename matches convention and does not collide",
                  ok_name, name_hint):
        failures += 1

    # 2/3. Source readable + text layer
    ok_src, full, src_hint, page_count = _check_source(args.source, args.ocr)
    if not _check(f"source openable ({page_count} pages, {len(full)} chars)",
                  ok_src, src_hint):
        failures += 1
        full = ""

    # 4. python-docx importable
    try:
        from docx import Document as _D  # noqa: F401
        _check("python-docx importable", True)
    except ImportError as exc:
        if not _check("python-docx importable", False, repr(exc)):
            failures += 1

    # 5. Q-number enumeration + user-qids cross-check
    qids: list[int] = []
    shape = ""
    if full:
        plain = set(int(m.group(1)) for m in PLAIN_MARKER_RE.finditer(full))
        question = set(int(m.group(1)) for m in QUESTION_MARKER_RE.finditer(full))
        if plain or question:
            shape = "plain" if len(plain) >= len(question) else "question"
        qids = sorted(plain | question)
        if qids:
            _check(
                f"source Q-ids enumerated (n={len(qids)}, "
                f"range {qids[0]}..{qids[-1]}, shape={shape})",
                True,
            )
        else:
            if not _check(
                "source Q-ids enumerated",
                False,
                "neither `Q{n}. [` nor standalone `Question {n}` markers found; "
                "this skill assumes a text-layer-bearing source. Switch to "
                "lsat-pdf-to-section-docx for raw image-only PDFs.",
            ):
                failures += 1

    user_qids = _parse_user_qids(args.user_qids)
    if user_qids:
        if qids and not _check_user_qids(qids, user_qids):
            failures += 1
    else:
        _reminder(
            "no --user-qids supplied; the v2-failure-mode cross-check is "
            "skipped (recommended: always pass --user-qids before building)."
        )

    # 6. Anchor sampling (only meaningful for shape=plain)
    anchors = _parse_anchor_spec(args.anchor)
    if anchors:
        if shape != "plain":
            _reminder(
                f"--anchor supplied but shape={shape or 'unknown'} "
                "(no per-Q chunks); anchor sampling skipped."
            )
        else:
            chunks = _chunk_plain_for_anchors(full)
            if not _check_anchors(chunks, anchors):
                failures += 1

    # 7. cross-skill reminders
    print()
    print("reminders (always-on; not failures):")
    _reminder(
        "Run the PDF Q-Number Extraction Protocol before trusting any LLM/agent "
        "that user Q-numbers map to PDF Q-numbers."
    )
    _reminder(
        "Never cross-match Q-numbers by content keywords. The user's Q-number "
        "IS the PDF's Q-number."
    )
    _reminder(
        "Tag ✓verified only when >=1 independent prep page confirms the answer "
        "against the CORRECT stimulus; use ~ for mirrors, ? for unconfirmed."
    )
    _reminder(
        "Default Part I question cards do NOT include a BR self-answer table. "
        "If a build script adds one, it must be opt-in via BR_SELF_ANSWER_TABLE=1."
    )
    _reminder(
        "Already-delivered docx files in /Users/log/ are NOT to be rebuilt. "
        "Use scripts/strip_self_answer_table.py to clean them up if needed."
    )

    print()
    if failures:
        print(f"preflight_br: {failures} failure(s) — fix above before building.")
        return 1
    print("preflight_br: all checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
