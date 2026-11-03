#!/usr/bin/env python3
"""
Skill Packager

Packages a skill directory into a distributable .skill file.
"""

import os
import sys
import json
import shutil
import tarfile
import argparse
from pathlib import Path


def package_skill(skill_dir: str, output_dir: str = ".") -> str:
    """
    Package a skill directory into a .skill file.

    Args:
        skill_dir: Path to skill directory
        output_dir: Output directory for .skill file

    Returns:
        Path to generated .skill file
    """
    skill_path = Path(skill_dir)
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    # Read metadata
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        skill_name = meta.get("name", skill_path.name)
    else:
        skill_name = skill_path.name

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create .skill file (tar.gz)
    skill_file = output_path / f"{skill_name}.skill"
    if skill_file.exists():
        skill_file.unlink()

    with tarfile.open(skill_file, "w:gz") as tar:
        for item in skill_path.rglob("*"):
            if item.is_file():
                arcname = item.relative_to(skill_path)
                tar.add(item, arcname=arcname)

    return str(skill_file)


def main():
    parser = argparse.ArgumentParser(description="Package a skill")
    parser.add_argument("skill_dir", help="Path to skill directory")
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory")
    args = parser.parse_args()

    try:
        skill_file = package_skill(args.skill_dir, args.output_dir)
        print(f"Skill packaged: {skill_file}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
