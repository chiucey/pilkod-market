#!/usr/bin/env python3
"""Preview installed skills by reading only SKILL.md frontmatter."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    raw = text[4:end]
    data = {}
    key = None
    buf = []
    def flush():
        nonlocal key, buf
        if key:
            data[key] = " ".join(buf).strip().strip('"')
        key = None; buf = []
    for line in raw.splitlines():
        if line.startswith("  ") and key:
            buf.append(line.strip())
        elif ":" in line:
            flush()
            k, v = line.split(":", 1)
            key = k.strip(); v = v.strip()
            buf = [] if v in {">", "|"} else [v]
    flush()
    return data


def main() -> int:
    roots = [Path(p).expanduser() for p in sys.argv[1:]] or [Path("./skills")]
    found = []
    for root in roots:
        for skill in root.glob("*/SKILL.md"):
            meta = parse_frontmatter(skill)
            if meta.get("name"):
                found.append((meta.get("name"), str(skill), meta.get("description", "")[:160]))
    for name, path, desc in sorted(found):
        print(f"- {name}: {path}\n  {desc}")
    print(f"\nFound {len(found)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
