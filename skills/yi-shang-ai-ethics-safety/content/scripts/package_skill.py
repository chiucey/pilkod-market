#!/usr/bin/env python3
"""
Package Skill Script
Packages a skill directory into a .skill file for distribution.
"""

import json
import os
import sys
import zipfile
from pathlib import Path


def validate_skill(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill structure and frontmatter."""
    errors = []

    # Check required files
    if not (skill_path / "SKILL.md").exists():
        errors.append("Missing SKILL.md")
    if not (skill_path / "_meta.json").exists():
        errors.append("Missing _meta.json")

    # Check SKILL.md frontmatter
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append("SKILL.md must start with frontmatter (---)")
        if "name:" not in content[:500]:
            errors.append("SKILL.md missing 'name:' in frontmatter")
        if "description:" not in content[:1000]:
            errors.append("SKILL.md missing 'description:' in frontmatter")

    # Check _meta.json
    meta_json = skill_path / "_meta.json"
    if meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json missing 'id' field")
            if "version" not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is invalid JSON: {e}")

    return len(errors) == 0, errors


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """Package a skill directory into a .skill file."""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # Validate first
    valid, errors = validate_skill(skill_path)
    if not valid:
        print("Validation failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    # Read meta for output filename
    meta = json.loads((skill_path / "_meta.json").read_text(encoding="utf-8"))
    version = meta.get("version", "1.0.0")
    output_file = f"{skill_name}-{version}.skill"
    output_path = Path(output_dir) / output_file

    # Create zip archive
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip __pycache__ and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"Successfully packaged skill to: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    package_skill(skill_path, output_dir)
