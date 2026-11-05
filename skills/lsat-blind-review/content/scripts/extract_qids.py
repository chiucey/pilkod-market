"""extract_qids.py — PDF Q-Number Extraction Protocol (lsat-blind-review).

Implements the mandatory pre-flight step described in SKILL.md, sections
"Mandatory Pre-Flight: PDF Q-Number Extraction Protocol" and "Hard Rules".

Two extraction shapes are supported, both observed in the wild:

  1. Plain-text Q-label shape:  `Q{n}.  [stimulus…]`  (e.g. Cambridge LR day2.txt
     export, or PDFs with a usable text layer whose first page previews `Q1. [`).
     Pattern: `Q(\d+)\.\s*\[`

  2. Standalone "Question" marker shape:  `Question {n}` on its own line, with
     stimulus ABOVE the marker and stem + A-E BELOW it (PT107 Section 1/3, PT108,
     PT109, etc.). The user-listed Q-number is still the PDF's Q-number.
     Pattern: `^\s*Question\s+(\d+)\s*$` (line-anchored, MULTILINE).

Usage:
    python3 extract_qids.py <pdf_path> [out_json] [--shape plain|question|auto]
                                              [--user-qids 3,7,17,...]
                                              [--anchor "Q3:Q3_keyword_1,Q3_keyword_2;Q17:Danaxil,Privatization"]

Exit codes:
    0  extraction succeeded, qids enumerated (and --user-qids subset all found,
       if provided)
    1  user-listed Q-number missing from PDF — STOP and ask the user
    2  usage / argument error
    3  PDF unreadable / no text layer / unknown shape
    4  structural invariant violated (e.g. duplicate Q marker)

The output JSON shape is:

    {
      "source": "<pdf_path>",
      "shape": "plain" | "question",
      "page_count": <int>,
      "char_count": <int>,
      "qids": [1, 2, ..., N],                # sorted, de-duped
      "chunks": {                            # only when shape == "plain"
        "1": "Q1. [stimulus ...]\nStem?\nA. ...\nE. ...",
        "2": "...",
        ...
      },
      "markers": {                           # only when shape == "question"
        "1": <byte-offset of "Question 1">,
        ...
      },
      "anchors": {                           # only when --anchor provided
        "Q3": {"status": "ok"|"missing", "missing": [...], "present": [...]},
        ...
      },
      "user_qids_check": {                   # only when --user-qids provided
        "requested": [...],
        "found": [...],
        "missing": [...]
      }
    }

Important: this script NEVER cross-matches Q-numbers by content keywords. The
user's Q-number IS the PDF's Q-number; if a user-listed Q is absent, the
script exits 1 with a clear STOP message and does NOT write the output file.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.stderr.write(
        "extract_qids.py: pdfplumber is required. Install with `pip install pdfplumber`.\n"
    )
    sys.exit(3)


PLAIN_MARKER_RE = re.compile(r"Q(\d+)\.\s*\[")
QUESTION_MARKER_RE = re.compile(r"^\s*Question\s+(\d+)\s*$", re.MULTILINE)
OPTION_LINE_RE = re.compile(r"^\s*([A-E])\.\s+")


# ---------------------------------------------------------------------------
# Extraction primitives
# ---------------------------------------------------------------------------

def extract_full_text(source_path: str) -> tuple[str, int]:
    """Read either a PDF (pdfplumber) or a pre-extracted text file.

    For .pdf inputs we concatenate every page's extract_text() into one
    string. For other inputs we just read the file as UTF-8. The returned
    text is NEVER normalized — callers that want word-boundary
    reconstruction for anchor-keyword matching should pass
    --normalize-spaces and let chunk_plain do the per-chunk rewrite
    (preserves Q-label detection).

    Returns (full_text, page_count). Raises SystemExit(3) on unreadable source.
    """
    if source_path.lower().endswith(".pdf"):
        try:
            with pdfplumber.open(source_path) as pdf:
                pages = list(pdf.pages)
                texts = [(p.extract_text() or "") for p in pages]
        except Exception as exc:
            sys.stderr.write(
                f"extract_qids.py: cannot open PDF {source_path!r}: {exc}\n"
            )
            sys.exit(3)
        full = "\n".join(texts)
        page_count = len(pages)
    else:
        try:
            full = Path(source_path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            full = Path(source_path).read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            sys.stderr.write(
                f"extract_qids.py: cannot read text source {source_path!r}: {exc}\n"
            )
            sys.exit(3)
        page_count = full.count("\x0c") + 1
    return full, page_count


_CAP_FOLLOWED_LOWER = re.compile(r"([A-Z])([a-z])")
# Only split on lowerCap when the new capital is followed by >=1 lowercase
# letter: that catches "endOf\nNew sentence" without over-splitting
# CamelCase proper nouns like "Danaxil" inside a single word.
_LOWER_FOLLOWED_CAP_THEN_LOWER = re.compile(r"([a-z])([A-Z][a-z])")
_DIGIT_FOLLOWED_LETTER = re.compile(r"(\d)([A-Za-z])")
_LETTER_FOLLOWED_DIGIT = re.compile(r"([A-Za-z])(\d)")


def _normalize_spaces(text: str) -> str:
    """Best-effort word-boundary reconstruction for space-stripped PDFs.

    The rules (in order):
      1. Capital letter followed by lowercase -> split (CamelCase -> Camel Case).
      2. Lowercase letter followed by Capital+lowercase -> split
         (endOfSentence / newParagraph start). NOT followed by another capital,
         so we do NOT split inside proper nouns like "Danaxil" or "PT109".
      3. Digit/letter boundary in both directions.

    This will not perfectly reconstruct every sentence (apostrophes, em-dashes,
    and other punctuation are not handled), but it covers the LSAT single-
    column layout where the only thing missing between words is whitespace.
    """
    s = text
    s = _CAP_FOLLOWED_LOWER.sub(r"\1 \2", s)
    s = _LOWER_FOLLOWED_CAP_THEN_LOWER.sub(r"\1 \2", s)
    s = _DIGIT_FOLLOWED_LETTER.sub(r"\1 \2", s)
    s = _LETTER_FOLLOWED_DIGIT.sub(r"\1 \2", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s


def detect_shape(full_text: str) -> str:
    """Return "plain", "question", or "unknown" based on which marker dominates.

    A PDF that has both shapes (rare; usually a partial OCR export) is treated
    as the dominant one. If neither shape has any hit, returns "unknown" — this
    is the v2-failure-mode signature: page-1 snippet never tells you the
    numbering scheme, only full enumeration does.
    """
    plain_hits = len(PLAIN_MARKER_RE.findall(full_text))
    question_hits = len(QUESTION_MARKER_RE.findall(full_text))
    if plain_hits == 0 and question_hits == 0:
        return "unknown"
    return "plain" if plain_hits >= question_hits else "question"


def enumerate_qids(full_text: str, shape: str) -> list[int]:
    """Return the sorted, de-duplicated list of PDF Q-numbers.

    Raises SystemExit(4) on duplicate Q markers — the same PDF cannot legally
    contain two `Question 17` headings.
    """
    if shape == "plain":
        nums = [int(m.group(1)) for m in PLAIN_MARKER_RE.finditer(full_text)]
    elif shape == "question":
        nums = [int(m.group(1)) for m in QUESTION_MARKER_RE.finditer(full_text)]
    else:
        return []
    seen = set()
    dups = []
    for n in nums:
        if n in seen:
            dups.append(n)
        seen.add(n)
    if dups:
        sys.stderr.write(
            f"extract_qids.py: duplicate Q markers in PDF: {sorted(set(dups))}. "
            "Refusing to continue — this is a structural invariant violation.\n"
        )
        sys.exit(4)
    return sorted(seen)


def chunk_plain(full_text: str, qids: list[int]) -> dict[str, str]:
    """Split full_text on Q-label boundaries; emit per-Q chunk.

    Each chunk contains the `Q{n}. [` header through (but not including) the
    next Q-label. The very last chunk ends at the end of the document.

    The trailing answer-key page (if any) is preserved as part of the last
    chunk; downstream scripts should still call detect_answer_key_block() to
    locate it. This matches what /Users/log/.cache/lsat_workbook/parse_source.py
    and extract_pt107_*.py already do.
    """
    # Lookahead split: keep the delimiter on the right chunk.
    parts = re.split(r"(?=Q(\d+)\.\s*\[)", full_text)
    out: dict[str, str] = {}
    # parts[0] is preamble (often empty); subsequent parts come in pairs
    # (header_capture, body).
    i = 1
    while i < len(parts):
        header = parts[i]            # the captured group 1 (the digit string)
        body = parts[i + 1] if i + 1 < len(parts) else ""
        if header.isdigit():
            out[header] = (header + body).strip()
        i += 2
    # Verify coverage: every enumerated QID should have a chunk.
    missing_chunks = [q for q in qids if str(q) not in out]
    if missing_chunks:
        sys.stderr.write(
            f"extract_qids.py: WARN shape=plain, markers found for {sorted(map(int, out.keys()))[:5]}... "
            f"but missing chunks for Q-ids {missing_chunks}. "
            "The marker regex matched these Q-ids inside another chunk's body — "
            "downstream consumers must NOT treat them as separate questions.\n"
        )
    return out


def chunk_question(full_text: str, qids: list[int]) -> dict[str, int]:
    """For shape='question', just emit byte-offsets; downstream builders split.

    This matches the convention used by /Users/log/.cache/lsat_workbook/
    extract_pt107_s1.py (DOCX marker walk) and extract_pt107_s3.py (PDF
    marker walk). We do NOT split here because the stimulus-vs-options
    boundary detection is non-trivial and already lives in those builders.
    """
    return {
        str(q): m.start()
        for q, m in (
            (int(qn), QUESTION_MARKER_RE.search(full_text))
            for qn in qids
        )
        if m is not None
    }


# ---------------------------------------------------------------------------
# User input validation
# ---------------------------------------------------------------------------

def parse_user_qids(arg: str | None) -> list[int]:
    if not arg:
        return []
    out: list[int] = []
    for tok in arg.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if not tok.isdigit():
            sys.stderr.write(
                f"extract_qids.py: --user-qids token {tok!r} is not a positive integer.\n"
            )
            sys.exit(2)
        out.append(int(tok))
    return sorted(set(out))


def check_user_qids(qids: list[int], user_qids: list[int]) -> dict:
    """Cross-check the user's wrong-Q list against the enumerated PDF Q-ids.

    Returns a small dict and, if anything is missing, prints a STOP-and-ask
    message then exits 1. The v2 workbook failure mode was caused by a coder
    agent NOT doing this check and instead cross-matching Q-numbers by
    content keywords.
    """
    qid_set = set(qids)
    found = [q for q in user_qids if q in qid_set]
    missing = [q for q in user_qids if q not in qid_set]
    if missing:
        sys.stderr.write(
            "\n"
            "============================================================\n"
            "STOP: user-listed Q-number(s) not found in PDF.\n"
            f"  PDF enumerated Q-ids: {qids[0]}..{qids[-1]}  (n={len(qids)})\n"
            f"  User Q-ids requested: {user_qids}\n"
            f"  MISSING from PDF:      {missing}\n"
            "------------------------------------------------------------\n"
            "Per SKILL.md Hard Rule #9, do NOT cross-match by content keywords.\n"
            "Ask the user to confirm the intended Q-number(s) before proceeding.\n"
            "============================================================\n"
        )
        sys.exit(1)
    return {"requested": user_qids, "found": found, "missing": []}


# ---------------------------------------------------------------------------
# Anchor-keyword sampling (per SKILL.md "Verification" item #8)
# ---------------------------------------------------------------------------

def parse_anchor_spec(arg: str | None) -> dict[str, list[str]]:
    """Parse `--anchor 'Q3:airlines,prevent;Q17:Danaxil'`.

    Keys are kept as the user typed them ("Q3", "17", "Question 3" all
    accepted) and resolved against the chunks dict inside check_anchors().
    """
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
    """Map "Q3" / "Question 3" / "3" -> the chunks-dict key ("3")."""
    s = qid_str.strip()
    if s.lower().startswith("question"):
        s = s.split(None, 1)[1] if len(s.split(None, 1)) > 1 else s
    if s.upper().startswith("Q"):
        s = s[1:]
    return s


def check_anchors(
    chunks: dict[str, str],
    qid_str: str,
    keywords: list[str],
) -> dict:
    """Verify that each anchor keyword appears in the chunk for qid_str.

    Anchor sampling is the v2-failure-mode backstop: even when the structural
    checks pass, an anchor-keyword mismatch proves the Q-number is pointing at
    the wrong question.

    Matching is done in three passes, in order:
      1. Case-insensitive substring against the chunk as-is.
      2. Case-insensitive substring against the chunk with ALL whitespace
         stripped — catches proper nouns that pdfplumber munged into "DANAXIL"
         or "D anaxil".
      3. If both above fail AND the chunk was CamelCase-normalized, also try
         the un-normalized chunks (relevant when --normalize-spaces is on but
         the anchor is a multi-word phrase that survived).

    Returns the first pass that finds a hit; if all three fail, the keyword
    is reported as missing.
    """
    chunk_key = _resolve_chunk_key(qid_str)
    chunk = chunks.get(chunk_key, "")
    chunk_compact = re.sub(r"\s+", "", chunk).lower()
    present, missing = [], []
    for kw in keywords:
        kl = kw.lower()
        kw_compact = re.sub(r"\s+", "", kl)
        if kl in chunk.lower():
            present.append(kw)
        elif kw_compact and kw_compact in chunk_compact:
            present.append(kw)
        else:
            missing.append(kw)
    return {
        "status": "ok" if not missing else "missing",
        "present": present,
        "missing": missing,
        "chunk_key": chunk_key,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="extract_qids.py",
        description=(
            "Run the lsat-blind-review PDF Q-Number Extraction Protocol. "
            "Exits 1 (STOP) if any user-listed Q-number is missing from the PDF."
        ),
    )
    ap.add_argument("pdf", help="path to the source PDF (or pre-extracted .txt)")
    ap.add_argument(
        "out_json",
        nargs="?",
        default="-",
        help="output JSON path; default '-' = stdout",
    )
    ap.add_argument(
        "--shape",
        choices=("plain", "question", "auto"),
        default="auto",
        help="marker shape to use (default: auto-detect)",
    )
    ap.add_argument(
        "--user-qids",
        default="",
        help="comma-separated user-listed Q-numbers, e.g. 3,7,17",
    )
    ap.add_argument(
        "--anchor",
        default="",
        help=(
            "anchor-keyword spec, e.g. "
            "'Q3:airlines,prevent;Q17:Danaxil' — used to back-stop v2-style "
            "Q-number cross-mapping errors"
        ),
    )
    ap.add_argument(
        "--min-chars",
        type=int,
        default=200,
        help="fail if PDF text has fewer than this many chars (default 200)",
    )
    ap.add_argument(
        "--normalize-spaces",
        action="store_true",
        help=(
            "rewrite each per-Q chunk with a CamelCase / digit-letter "
            "heuristic to insert word boundaries. Used for anchor-keyword "
            "matching against space-stripped pdfplumber output; NOT applied "
            "to the Q-label detection step (so Q1/Q2/... still parse)."
        ),
    )
    args = ap.parse_args()

    pdf_path = args.pdf
    if not os.path.exists(pdf_path):
        sys.stderr.write(f"extract_qids.py: no such file: {pdf_path}\n")
        return 2

    full_text, page_count = extract_full_text(pdf_path)
    if len(full_text) < args.min_chars:
        sys.stderr.write(
            f"extract_qids.py: PDF text has only {len(full_text)} chars "
            f"(threshold {args.min_chars}). The PDF likely has no text layer; "
            "this skill assumes a text-layer-bearing Cambridge LR source. "
            "For image-only PDFs, run OCR or use lsat-pdf-to-section-docx.\n"
        )
        return 3

    shape = args.shape
    if shape == "auto":
        shape = detect_shape(full_text)
    if shape == "unknown":
        sys.stderr.write(
            "extract_qids.py: could not detect either Q-label shape "
            "(no `Q{n}. [` and no standalone `Question {n}` hits). "
            "Refusing to enumerate. Re-check the PDF.\n"
        )
        return 3

    qids = enumerate_qids(full_text, shape)

    out: dict = {
        "source": os.path.abspath(pdf_path),
        "shape": shape,
        "page_count": page_count,
        "char_count": len(full_text),
        "qids": qids,
    }

    if shape == "plain":
        chunks = chunk_plain(full_text, qids)
        if args.normalize_spaces:
            chunks = {k: _normalize_spaces(v) for k, v in chunks.items()}
        out["chunks"] = chunks
    else:  # "question"
        out["markers"] = chunk_question(full_text, qids)

    user_qids = parse_user_qids(args.user_qids)
    if user_qids:
        out["user_qids_check"] = check_user_qids(qids, user_qids)

    anchors = parse_anchor_spec(args.anchor)
    if anchors:
        if shape != "plain":
            sys.stderr.write(
                "extract_qids.py: --anchor requires shape=plain "
                "(per-Q chunks needed for keyword sampling). "
                "Re-run without --anchor, or first convert via your builder.\n"
            )
            return 2
        out["anchors"] = {
            qid_str: check_anchors(out["chunks"], qid_str, kws)
            for qid_str, kws in anchors.items()
        }

    payload = json.dumps(out, ensure_ascii=False, indent=1)
    if args.out_json == "-":
        sys.stdout.write(payload + "\n")
    else:
        Path(args.out_json).write_text(payload + "\n", encoding="utf-8")
        sys.stderr.write(
            f"extract_qids.py: wrote {args.out_json}  "
            f"shape={shape}  qids={qids[0]}..{qids[-1]} (n={len(qids)})\n"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
