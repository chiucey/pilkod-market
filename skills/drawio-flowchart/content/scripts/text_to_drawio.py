#!/usr/bin/env python3
"""Build a .drawio file directly from natural language text."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import generate_drawio
import text_to_spec


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a .drawio file directly from natural language text.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="Path to a UTF-8 text file.")
    group.add_argument("--text", help="Inline natural language text.")
    parser.add_argument("--title", help="Optional title override.")
    parser.add_argument("--output", required=True, help="Path to the output .drawio file.")
    parser.add_argument("--spec-output", help="Optional path to save the generated JSON spec.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.text is not None:
        raw_text = args.text
    else:
        raw_text = Path(args.input).read_text(encoding="utf-8")

    spec = text_to_spec.text_to_spec(raw_text, title=args.title)

    if args.spec_output:
        spec_path = Path(args.spec_output)
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[OK] Wrote {spec_path}")

    generate_drawio.generate_from_spec(spec, Path(args.output))


if __name__ == "__main__":
    main()
