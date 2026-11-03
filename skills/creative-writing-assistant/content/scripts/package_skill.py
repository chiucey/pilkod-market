#!/usr/bin/env python3
"""
Skill Packaging Script
Packages a skill into a distributable .skill archive
"""

import os
import sys
import json
import zipfile
from pathlib import Path

def validate_skill(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate skill structure and frontmatter"""
    errors = []

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    # Read and check frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        errors.append("SKILL.md must start with frontmatter (---)")

    # Parse frontmatter
    try:
        lines = content.split('---')
        if len(lines) >= 2:
            frontmatter = lines[1]
            if 'name:' not in frontmatter:
                errors.append("Frontmatter missing 'name' field")
            if 'description:' not in frontmatter:
                errors.append("Frontmatter missing 'description' field")
    except Exception as e:
        errors.append(f"Frontmatter parse error: {e}")

    # Check _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json parse error: {e}")

    return len(errors) == 0, errors

def package_skill(skill_path: str) -> str:
    """Package skill into .skill file"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # Validate first
    valid, errors = validate_skill(skill_path)
    if not valid:
        print("Validation failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    # Create .skill package
    output_file = f"{skill_name}.skill"

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"Package created: {output_file}")
    print(f"Files included:")
    for file_path in skill_path.rglob('*'):
        if file_path.is_file():
            print(f"  - {file_path.relative_to(skill_path)}")

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path>")
        sys.exit(1)

    package_skill(sys.argv[1])
