#!/usr/bin/env python3
"""Package a validated skill directory into a .skill archive."""

import fnmatch
import sys
import zipfile
from pathlib import Path
from typing import Optional, Union

from quick_validate import validate_skill

EXCLUDE_DIRS = {".git", ".svn", ".hg", "__pycache__", "node_modules"}
EXCLUDE_FILES = {".DS_Store"}
EXCLUDE_GLOBS = {"*.pyc"}


def should_exclude(rel_path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in rel_path.parts):
        return True
    if rel_path.name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(rel_path.name, pattern) for pattern in EXCLUDE_GLOBS)


def package_skill(
    skill_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
) -> Optional[Path]:
    root = Path(skill_path).resolve()
    if not root.exists():
        print(f"ERROR: skill folder not found: {root}")
        return None
    if not root.is_dir():
        print(f"ERROR: path is not a directory: {root}")
        return None

    valid, message = validate_skill(root)
    if not valid:
        print(f"ERROR: validation failed: {message}")
        return None
    print(f"OK: {message}")

    destination = Path(output_dir).resolve() if output_dir else Path.cwd()
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"{root.name}.skill"

    try:
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_handle:
            for path in root.rglob("*"):
                rel = path.relative_to(root)
                if should_exclude(rel):
                    continue
                if path.is_symlink():
                    print(f"ERROR: refusing to package symlink: {path}")
                    return None
                if not path.is_file():
                    continue
                arcname = Path(root.name) / rel
                zip_handle.write(path, arcname)
                print(f"  added: {arcname}")
    except Exception as exc:
        print(f"ERROR: failed to package skill: {exc}")
        return None

    print(f"OK: packaged skill at {archive}")
    return archive


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/package_skill.py <path/to/skill-folder> [output-directory]")
        return 1

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    result = package_skill(skill_path, output_dir)
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
