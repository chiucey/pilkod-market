#!/usr/bin/env python3
"""
RPM Package Builder Skill - Package Script

This script packages the skill into a distributable .skill file.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_excluded_patterns():
    """Return patterns to exclude from packaging."""
    return {
        "__pycache__",
        "*.pyc",
        ".git",
        ".DS_Store",
        "*.egg-info",
        ".pytest_cache",
        "tmp",
        "temp",
        ".venv",
        "node_modules",
    }


def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from the package."""
    name = path.name
    return name in get_excluded_patterns() or name.endswith(".pyc")


def collect_files(skill_path: Path) -> list[Path]:
    """Collect all files to be included in the package."""
    files = []

    for root, dirs, filenames in os.walk(skill_path):
        root_path = Path(root)

        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in get_excluded_patterns()]

        for filename in filenames:
            file_path = root_path / filename
            if not should_exclude(file_path):
                files.append(file_path)

    return files


def create_package(skill_path: Path, output_path: Path) -> bool:
    """Create the .skill package file."""
    skill_path = skill_path.resolve()
    output_path = output_path.resolve()

    # Validate skill structure
    skill_md = skill_path / "SKILL.md"
    meta_json = skill_path / "_meta.json"

    if not skill_md.exists():
        print(f"Error: SKILL.md not found in {skill_path}")
        return False

    if not meta_json.exists():
        print(f"Error: _meta.json not found in {skill_path}")
        return False

    # Read meta for naming
    try:
        meta = json.loads(meta_json.read_text(encoding="utf-8"))
        skill_id = meta.get("id", "unknown")
        skill_version = meta.get("version", "1.0.0")
    except Exception as e:
        print(f"Error reading _meta.json: {e}")
        return False

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create zip package
    try:
        with zipfile.ZipFile(
            output_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9
        ) as zf:
            files = collect_files(skill_path)
            rel_base = skill_path.parent

            for file_path in sorted(files):
                arcname = file_path.relative_to(rel_base)
                zf.write(file_path, arcname)
                print(f"  Adding: {arcname}")

        print(f"\nPackage created: {output_path}")
        print(f"  Skill ID: {skill_id}")
        print(f"  Version: {skill_version}")
        print(f"  Files: {len(files)}")

        return True

    except Exception as e:
        print(f"Error creating package: {e}")
        if output_path.exists():
            output_path.unlink()
        return False


def main():
    """Main package entry point."""
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill-path> [output-path]")
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()

    if not skill_path.exists():
        print(f"Error: Skill path does not exist: {skill_path}")
        sys.exit(1)

    # Determine output path
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2]).resolve()
    else:
        skill_name = skill_path.name
        output_path = skill_path.parent / f"{skill_name}.skill"

    print(f"Packaging skill: {skill_path}")
    print("-" * 50)

    success = create_package(skill_path, output_path)

    if success:
        print("-" * 50)
        print("Package created successfully!")
        sys.exit(0)
    else:
        print("-" * 50)
        print("Failed to create package.")
        sys.exit(1)


if __name__ == "__main__":
    main()
