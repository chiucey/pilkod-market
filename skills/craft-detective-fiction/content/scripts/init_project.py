#!/usr/bin/env python3
"""Safely initialize a detective-fiction project from bundled templates."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys


ASSET_MAP = {
    "project-charter-template.md": "project-charter.md",
    "case-bible-template.md": "case-bible.md",
    "outline-template.md": "outline.md",
    "mystery-ledger-template.md": "mystery-ledger.md",
    "style-guide-template.md": "style-guide.md",
    "notes-template.md": "notes.md",
    "chapter-template.md": "chapters/_chapter-template.md",
    "audit-report-template.md": "audit-report.md",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new mystery-writing project without overwriting files."
    )
    parser.add_argument("project_dir", help="Destination directory for the project")
    parser.add_argument("--title", required=True, help="Project title")
    parser.add_argument(
        "--target-words",
        type=int,
        default=80_000,
        help="Target manuscript length (default: 80000)",
    )
    args = parser.parse_args()
    if args.target_words <= 0:
        parser.error("--target-words must be a positive integer")
    return args


def resolve_destination(raw: str) -> Path:
    destination = Path(raw).expanduser().resolve()
    if destination == Path(destination.anchor):
        raise ValueError("Refusing to initialize a project at a filesystem root")
    return destination


def main() -> int:
    args = parse_args()
    try:
        destination = resolve_destination(args.project_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if destination.exists() and not destination.is_dir():
        print(f"ERROR: destination exists and is not a directory: {destination}", file=sys.stderr)
        return 2
    if destination.exists() and any(destination.iterdir()):
        print(
            f"ERROR: destination is not empty; no files were overwritten: {destination}",
            file=sys.stderr,
        )
        return 2

    skill_dir = Path(__file__).resolve().parent.parent
    assets_dir = skill_dir / "assets"
    missing_assets = [name for name in ASSET_MAP if not (assets_dir / name).is_file()]
    if missing_assets:
        print(f"ERROR: missing bundled assets: {', '.join(missing_assets)}", file=sys.stderr)
        return 2

    destination.mkdir(parents=True, exist_ok=True)
    (destination / "chapters").mkdir()
    (destination / "exports").mkdir()

    replacements = {
        "{{TITLE}}": args.title,
        "{{DATE}}": date.today().isoformat(),
        "{{TARGET_WORDS}}": str(args.target_words),
    }

    created: list[Path] = []
    for asset_name, relative_target in ASSET_MAP.items():
        content = (assets_dir / asset_name).read_text(encoding="utf-8")
        for token, value in replacements.items():
            content = content.replace(token, value)
        target = destination / relative_target
        target.write_text(content, encoding="utf-8")
        created.append(target)

    print(f"Created mystery project: {destination}")
    for path in created:
        print(f"- {path.relative_to(destination)}")
    print("- exports/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
