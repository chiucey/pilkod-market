#!/usr/bin/env python3
"""Fail when a generated HTML contains credentials or mock residue."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SECRET_PATTERNS = {
    "WeRead key": re.compile(r"wrk-[A-Za-z0-9_-]{8,}"),
    "Bearer authorization": re.compile(r"Authorization\s*:\s*Bearer", re.I),
    "assigned key": re.compile(r"WEREAD_API_KEY\s*=", re.I),
}

MOCK_PATTERNS = {
    "mock banner": re.compile(r"MOCK\s+PREVIEW", re.I),
    "mock flag": re.compile(r'"isMock"\s*:\s*true', re.I),
}

LEGACY_RESIDUE_PATTERNS = {
    "legacy section 1": re.compile(r'id="sec-heatmap"'),
    "legacy section 2": re.compile(r'id="sec-companion"'),
    "legacy control 1": re.compile(r'id="ai-recs"'),
    "legacy control 2": re.compile(r'id="ai-chat"'),
    "legacy control 3": re.compile(r'id="companion-input"'),
    "legacy control 4": re.compile(r'id="chat-input"'),
}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: audit_output.py /absolute/path/to/output.html")

    path = Path(sys.argv[1]).expanduser().resolve()
    text = path.read_text(encoding="utf-8")
    failures = []

    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            failures.append(f"credential residue: {label}")
    for label, pattern in MOCK_PATTERNS.items():
        if pattern.search(text):
            failures.append(f"mock residue: {label}")
    for label, pattern in LEGACY_RESIDUE_PATTERNS.items():
        if pattern.search(text):
            failures.append(f"legacy template residue: {label}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)

    print(f"PASS: {path}")


if __name__ == "__main__":
    main()
