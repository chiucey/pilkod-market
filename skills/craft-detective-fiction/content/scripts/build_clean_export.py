#!/usr/bin/env python3
"""Combine canonical chapter Markdown files into a clean manuscript."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys
import tempfile

# Keep the skill's scripts/ directory read-only in effect: importing
# audit_mystery_project must not drop __pycache__ bytecode into it.
sys.dont_write_bytecode = True

from audit_mystery_project import (
    CHAPTER_FILE_RE,
    HTML_COMMENT_RE,
    canonical_metadata_issues,
    clean_manuscript_issues,
    frontmatter,
    parse_chapter_metadata,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge canonical chapter-XX.md files into a clean Markdown export."
    )
    parser.add_argument("project_dir", help="Mystery project directory")
    parser.add_argument("output_file", help="Destination Markdown file")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Explicitly replace an existing output file",
    )
    return parser.parse_args()


def strip_frontmatter(text: str) -> str:
    normalized = text.replace("\r\n", "\n")
    metadata = frontmatter(normalized)
    if metadata is None:
        raise ValueError("chapter has no valid YAML frontmatter")
    end = normalized.find("\n---\n", 4)
    return normalized[end + 5 :]


def is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 2


def main() -> int:
    args = parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    output = Path(args.output_file).expanduser().resolve()
    chapters_dir = (project / "chapters").resolve()
    exports_dir = (project / "exports").resolve()

    if not chapters_dir.is_dir():
        return fail(f"chapters directory not found: {chapters_dir}")
    if not exports_dir.is_dir():
        return fail(f"exports directory not found: {exports_dir}")
    if output == Path(output.anchor):
        return fail("output cannot be a filesystem root")
    if output == exports_dir or not is_within(output, exports_dir):
        return fail("output must be a Markdown file inside the project's exports directory")
    if output.suffix.lower() != ".md":
        return fail("output must use the .md extension")
    if is_within(output, chapters_dir):
        return fail("output cannot be inside the chapters directory")
    if output.exists() and not args.replace:
        return fail(f"output exists; use --replace to overwrite: {output}")

    numbered: list[tuple[int, Path]] = []
    malformed_names: list[str] = []
    for path in chapters_dir.glob("chapter-*.md"):
        match = CHAPTER_FILE_RE.fullmatch(path.name)
        if match:
            numbered.append((int(match.group(1)), path.resolve()))
        else:
            malformed_names.append(path.name)
    if malformed_names:
        return fail(
            "malformed chapter filenames: " + ", ".join(sorted(malformed_names))
        )
    numbered.sort(key=lambda item: (item[0], item[1].name))

    if not numbered:
        return fail("no chapter-XX.md files found")
    numbers = [number for number, _ in numbered]
    if len(numbers) != len(set(numbers)):
        return fail("duplicate chapter numbers found")
    expected = list(range(1, numbers[-1] + 1))
    if numbers != expected:
        missing = sorted(set(expected) - set(numbers))
        return fail(
            "chapter numbering must be continuous from 1; missing: "
            + ", ".join(str(number) for number in missing)
        )
    if any(output == path for _, path in numbered):
        return fail("output cannot be one of the source chapter files")

    cleaned: list[str] = []
    for number, path in numbered:
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            return fail(f"cannot read {path.name} as UTF-8: {exc}")
        metadata_text = frontmatter(source)
        if metadata_text is None:
            return fail(f"{path.name}: chapter has no valid YAML frontmatter")
        metadata, metadata_issues = parse_chapter_metadata(metadata_text)
        if metadata_issues:
            return fail(f"{path.name}: {metadata_issues[0]}")
        if metadata.get("status") != "canonical":
            return fail(
                f"{path.name}: status must be canonical, found "
                f"'{metadata.get('status', '')}'"
            )
        gate_issues = canonical_metadata_issues(metadata)
        if gate_issues:
            return fail(f"{path.name}: {gate_issues[0]}")
        chapter_value = str(metadata.get("chapter", ""))
        if not re.fullmatch(r"\d+", chapter_value) or int(chapter_value) != number:
            return fail(f"{path.name}: chapter number disagrees with filename")

        try:
            reader_text = strip_frontmatter(source)
        except ValueError as exc:
            return fail(f"{path.name}: {exc}")
        reader_text = HTML_COMMENT_RE.sub("\n", reader_text).strip()
        if not reader_text:
            return fail(f"{path.name} has no reader-facing content")
        issues = clean_manuscript_issues(reader_text)
        if issues:
            return fail(f"{path.name} {issues[0]}")
        cleaned.append(reader_text)

    manuscript = "\n\n---\n\n".join(cleaned) + "\n"
    issues = clean_manuscript_issues(manuscript)
    if issues:
        return fail(f"generated manuscript {issues[0]}")

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return fail(f"cannot create output directory: {exc}")

    temporary: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output.name}.", suffix=".tmp", dir=str(output.parent)
        )
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(manuscript)

        written = temporary.read_text(encoding="utf-8")
        post_write_issues = clean_manuscript_issues(written)
        if post_write_issues:
            return fail(f"written manuscript {post_write_issues[0]}")
        os.replace(temporary, output)
        temporary = None
    except OSError as exc:
        return fail(f"cannot create clean manuscript: {exc}")
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass

    print(f"Created clean manuscript: {output}")
    print(f"Chapters merged: {len(cleaned)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
