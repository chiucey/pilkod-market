#!/usr/bin/env python3
"""
Package script for local-command-executor skill.
Creates a distributable .skill package.
"""

import json
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path


def package_skill(skill_path: Path, output_dir: Path = None):
    """Package skill into a .skill file."""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        print(f"Error: Skill path not found: {skill_path}")
        sys.exit(1)

    if output_dir is None:
        output_dir = Path.cwd()

    # Create output directory if needed
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get skill name and version
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        skill_version = meta.get("version", "1.0.0")
    else:
        skill_version = "1.0.0"

    skill_name = skill_path.name
    output_file = output_dir / f"{skill_name}-{skill_version}.skill"

    # Create zip package
    print(f"Packaging {skill_name} v{skill_version}...")

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"\nPackage created: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.1f} KB")

    return output_file


def main():
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    package_skill(skill_path)


if __name__ == "__main__":
    main()