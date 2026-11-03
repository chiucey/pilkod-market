#!/usr/bin/env python3
"""Inject a topics JSON file into review-template.html and emit a self-contained review panel.

Usage:
    python3 build_panel.py topics.json -o 复习面板.html \
        --title "AI 概论" --subtitle "考前冲刺" \
        --course "人工智能概论" --state-key ai-intro-v1 --export-prefix "AI概论复习进度_"

The topics JSON is a list of topic objects; see references/card-schema.md.
"""
import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "references" / "review-template.html"

VALID_TYPES = {"concept", "calculation", "diagram", "comparison", "fill"}
REQUIRED_CARD_FIELDS = ("id", "type", "difficulty", "question", "answer")
# C0 controls except \t \n \r — includes the \b in \bigl, which is a VALID
# JSON escape that silently becomes U+0008 and renders as "1.05 igl[".
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
# A real LaTeX command that survived conversion. \n followed by an
# identifier is a newline + name (e.g. "\nCF(E)"), not a command.
LATEX_LEFTOVER = re.compile(r"\\(?!n[A-Za-z]*[\(\{\[])[A-Za-z]+")


def _strings_of(obj, out=None):
    """Concatenate only the real string VALUES of a structure.

    json.dumps() would emit \\n for every newline; scanning that turns normal
    prose into false positives, so the guards must walk values instead.
    """
    if out is None:
        out = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _strings_of(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _strings_of(v, out)
    return "\n".join(out)


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def validate(topics):
    """Fail loudly on schema violations — a silently broken card wastes the user's exam night."""
    if not isinstance(topics, list) or not topics:
        die("topics must be a non-empty list")

    seen_ids = set()
    for ti, t in enumerate(topics):
        where = f"topic[{ti}] ({t.get('title', '?')})"
        if not t.get("title"):
            die(f"{where}: missing 'title'")
        if not t.get("cards"):
            die(f"{where}: has no cards")
        for ci, c in enumerate(t["cards"]):
            cw = f"{where}.card[{ci}]"
            for f in REQUIRED_CARD_FIELDS:
                if f not in c or c[f] in (None, ""):
                    die(f"{cw}: missing required field '{f}'")
            if c["type"] not in VALID_TYPES:
                die(f"{cw}: type '{c['type']}' not in {sorted(VALID_TYPES)}")
            if not isinstance(c["difficulty"], int) or not 1 <= c["difficulty"] <= 3:
                die(f"{cw}: difficulty must be int 1-3, got {c['difficulty']!r}")
            if c["id"] in seen_ids:
                die(f"{cw}: duplicate id '{c['id']}' (ids must be globally unique)")
            seen_ids.add(c["id"])
            if c["type"] == "fill" and "____" not in c["question"]:
                die(f"{cw}: fill card must contain '____' in question")
            if c["type"] == "fill" and isinstance(c["answer"], str) and "____" in c["answer"]:
                die(f"{cw}: fill answer should not repeat the blank marker")

            blob = _strings_of(c)
            ctrl = CONTROL_CHARS.search(blob)
            if ctrl:
                die(f"{cw}: contains control char U+{ord(ctrl.group()):04X} "
                    f"(likely a raw \\b from \\bigl, or a hand-written escape)")
            leftover = LATEX_LEFTOVER.findall(blob)
            if leftover:
                uniq = sorted(set(leftover))[:5]
                die(f"{cw}: unconverted LaTeX {uniq} — run latex_to_unicode.py first. "
                    f"(write these as Unicode directly: ∅ ⊕ ≤ ≥ Σ min max)")
            if "$" in blob:
                die(f"{cw}: contains a raw '$' math delimiter — "
                    f"run latex_to_unicode.py first")

    total = sum(len(t["cards"]) for t in topics)
    print(f"✓ schema ok: {len(topics)} topics, {total} cards")
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topics_json")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--title", default="复习面板")
    ap.add_argument("--subtitle", default="考前冲刺")
    ap.add_argument("--course", default="课程")
    ap.add_argument("--page-title", default=None)
    ap.add_argument("--state-key", default="course-review-v1")
    ap.add_argument("--export-prefix", default="复习进度_")
    ap.add_argument("--skip-convert", action="store_true",
                    help="do not run latex_to_unicode.py (input already converted)")
    args = ap.parse_args()

    raw = Path(args.topics_json).read_text(encoding="utf-8")
    try:
        topics = json.loads(raw)
    except json.JSONDecodeError as e:
        die(f"topics JSON is invalid: {e}")

    # Convert in-process unless told to skip. Doing it here (not as a separate
    # step) is what stops the silent failure where raw LaTeX ships to the panel.
    if not args.skip_convert:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            import latex_to_unicode
        except ImportError:
            die("latex_to_unicode.py not found next to this script")
        topics = latex_to_unicode.walk(topics)
        print("✓ converted LaTeX -> Unicode")

    validate(topics)

    # Stamp the course name onto topic[0] so the progress export can label itself.
    if isinstance(topics[0], dict):
        topics[0]["courseName"] = args.course

    payload = json.dumps(topics, ensure_ascii=False, separators=(",", ":"))
    # A literal </script> inside JSON would terminate the host script tag early.
    payload = payload.replace("</script>", "<\\/script>")

    html = TEMPLATE.read_text(encoding="utf-8")
    page_title = args.page_title or f"{args.course} 考前复习"

    subs = {
        "__TOPICS_JSON__": payload,
        "__PANEL_TITLE__": args.title,
        "__PANEL_SUBTITLE__": args.subtitle,
        "__COURSE_TITLE__": args.course,
        "__PAGE_TITLE__": page_title,
        "__STATE_KEY__": args.state_key,
        "__EXPORT_PREFIX__": args.export_prefix,
    }
    for k, v in subs.items():
        if k not in html:
            die(f"template is missing placeholder {k}")
        html = html.replace(k, v)

    # Require at least one uppercase letter so fill-card blanks (____) are not flagged.
    leftover = re.findall(r"__[A-Z][A-Z_]*__", html)
    if leftover:
        die(f"unsubstituted placeholders remain: {sorted(set(leftover))}")

    Path(args.output).write_text(html, encoding="utf-8")
    print(f"✓ wrote {args.output} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
