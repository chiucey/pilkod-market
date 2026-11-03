#!/usr/bin/env python3
"""Compile Hey Web Design source documents into two generated master files."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


GROUPS = {
    "spec": {
        "title": "Website Specification",
        "output": "spec.md",
        "sources": (
            "requirements.md",
            "reference.md",
            "sitemap.md",
            "content.md",
        ),
    },
    "design": {
        "title": "Website Design Specification",
        "output": "design.md",
        "sources": (
            "layout.md",
            "design-token.md",
            "components.md",
            "animation.md",
        ),
    },
}


def normalize_source(path: Path) -> str:
    if not path.exists():
        return (
            f"# {path.stem.replace('-', ' ').title()}\n\n"
            "> Source not created yet.\n"
        )
    return path.read_text(encoding="utf-8").strip() + "\n"


def source_digest(source_items: list[tuple[str, str]]) -> str:
    digest = hashlib.sha256()
    for name, content in source_items:
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def compile_group(project_root: Path, group_name: str) -> tuple[Path, list[str]]:
    group = GROUPS[group_name]
    docs_dir = project_root / "docs"
    source_dir = docs_dir / "source"
    output_path = docs_dir / str(group["output"])
    warnings: list[str] = []
    source_items: list[tuple[str, str]] = []

    for source_name in group["sources"]:
        source_path = source_dir / source_name
        if not source_path.exists():
            warnings.append(f"missing source: {source_path}")
        source_items.append((source_name, normalize_source(source_path)))

    digest = source_digest(source_items)
    source_list = ", ".join(name for name, _ in source_items)
    parts = [
        "<!-- GENERATED FILE. DO NOT EDIT DIRECTLY. -->",
        f"<!-- source-group: {group_name} -->",
        f"<!-- source-files: {source_list} -->",
        f"<!-- source-sha256: {digest} -->",
        "",
        f"# {group['title']}",
        "",
        (
            "> Generated from canonical files in `docs/source/`. "
            "Edit those files and run the assembler again."
        ),
        "",
    ]

    for source_name, content in source_items:
        parts.extend(
            [
                "---",
                "",
                f"<!-- BEGIN SOURCE: {source_name} -->",
                "",
                content.rstrip(),
                "",
                f"<!-- END SOURCE: {source_name} -->",
                "",
            ]
        )

    rendered = "\n".join(parts).rstrip() + "\n"
    docs_dir.mkdir(parents=True, exist_ok=True)
    previous = output_path.read_text(encoding="utf-8") if output_path.exists() else None
    if previous != rendered:
        output_path.write_text(rendered, encoding="utf-8")
    return output_path, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compile docs/source/*.md into generated docs/spec.md and docs/design.md."
        )
    )
    parser.add_argument(
        "project_root",
        type=Path,
        help="Website project root containing docs/source/.",
    )
    parser.add_argument(
        "group",
        nargs="?",
        choices=("spec", "design", "all"),
        default="all",
        help="Master document to build (default: all).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = args.project_root.expanduser().resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"error: project root is not a directory: {project_root}", file=sys.stderr)
        return 2

    selected = tuple(GROUPS) if args.group == "all" else (args.group,)
    warnings: list[str] = []
    for group_name in selected:
        output_path, group_warnings = compile_group(project_root, group_name)
        print(f"built {output_path}")
        warnings.extend(group_warnings)

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
