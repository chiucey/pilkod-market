#!/usr/bin/env python3
"""
Package skill into a distributable .skill file.
"""
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path


def load_meta(skill_dir: Path) -> dict:
    """Load and validate _meta.json"""
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing _meta.json in {skill_dir}")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    required = ["id", "version"]
    for key in required:
        if key not in meta:
            raise ValueError(f"Missing required field '{key}' in _meta.json")

    return meta


def validate_frontmatter(skill_md_path: Path) -> dict:
    """Validate SKILL.md frontmatter"""
    if not skill_md_path.exists():
        raise FileNotFoundError(f"Missing SKILL.md in {skill_md_path.parent}")

    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check frontmatter starts at beginning
    if not content.startswith("---"):
        raise ValueError("SKILL.md must start with YAML frontmatter (---)")

    # Parse frontmatter - find closing ---
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.startswith("---"):
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        raise ValueError("Invalid frontmatter format - missing closing ---")

    frontmatter = {}
    for line in lines[1:frontmatter_end]:
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    required = ["name", "description"]
    for key in required:
        if key not in frontmatter:
            raise ValueError(f"Missing required frontmatter field '{key}'")

    return frontmatter


def package_skill(skill_dir: str, output_dir: str = ".") -> str:
    """Package skill into .skill file"""
    skill_path = Path(skill_dir)

    if not skill_path.exists() or not skill_path.is_dir():
        raise ValueError(f"Invalid skill directory: {skill_dir}")

    # Validate
    meta = load_meta(skill_path)
    frontmatter = validate_frontmatter(skill_path / "SKILL.md")

    # Create output
    skill_name = frontmatter["name"]
    version = meta["version"]
    output_file = f"{skill_name}.skill"
    output_path = Path(output_dir) / output_file

    # Build package
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_directory> [output_directory]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        output_path = package_skill(skill_dir, output_dir)
        print(f"✅ Skill packaged successfully: {output_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
