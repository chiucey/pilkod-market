#!/usr/bin/env python3
"""
Package Skill Tool

Packages a skill directory into a .skill archive file.
"""

import json
import os
import sys
import zipfile
from pathlib import Path


def validate_skill(skill_dir: Path) -> bool:
    """Validate skill structure and metadata."""
    errors = []

    # Check required files
    skill_md = skill_dir / "SKILL.md"
    meta_json = skill_dir / "_meta.json"

    if not skill_md.exists():
        errors.append("Missing SKILL.md")
    else:
        # Check frontmatter
        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append("SKILL.md must start with YAML frontmatter")
        if "name:" not in content[:500]:
            errors.append("SKILL.md missing 'name' in frontmatter")
        if "description:" not in content[:500]:
            errors.append("SKILL.md missing 'description' in frontmatter")

    if not meta_json.exists():
        errors.append("Missing _meta.json")
    else:
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json missing 'id'")
            if "version" not in meta:
                errors.append("_meta.json missing 'version'")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is invalid JSON: {e}")

    # Check name consistency
    if skill_md.exists() and meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            skill_name = meta.get("name", "")
            folder_name = skill_dir.name

            content = skill_md.read_text(encoding="utf-8")
            frontmatter_start = content.index("---") + 3
            frontmatter_end = content.index("---", frontmatter_start)
            frontmatter = content[frontmatter_start:frontmatter_end]

            if f"name: {folder_name}" not in frontmatter:
                errors.append(f"SKILL.md frontmatter name '{skill_name}' doesn't match folder '{folder_name}'")
        except Exception as e:
            errors.append(f"Error validating name consistency: {e}")

    return errors


def package_skill(skill_dir: Path, output_dir: Path = None) -> Path:
    """Package skill directory into a .skill archive."""
    skill_dir = skill_dir.resolve()
    skill_name = skill_dir.name

    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        output_dir = Path(output_dir).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate first
    errors = validate_skill(skill_dir)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    # Create .skill file (zip archive)
    output_file = output_dir / f"{skill_name}.skill"

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob("*"):
            if file_path.is_file():
                # Skip __pycache__ and other unwanted files
                if "__pycache__" in str(file_path):
                    continue
                if file_path.suffix == ".pyc":
                    continue

                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    print(f"Packaged skill to: {output_file}")
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_dir> [output_dir]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    package_skill(skill_dir, output_dir)
