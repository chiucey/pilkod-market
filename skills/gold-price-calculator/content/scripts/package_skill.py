#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive file from the skill directory.
"""
import os
import json
import zipfile
import sys
from pathlib import Path


def validate_skill(skill_path: Path) -> tuple[bool, str]:
    """Validate skill structure and metadata."""
    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Check frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            return False, "SKILL.md must start with YAML frontmatter"

        # Extract frontmatter
        lines = content.split('---')
        if len(lines) < 3:
            return False, "Invalid frontmatter format"

        frontmatter = lines[1]
        if 'name:' not in frontmatter:
            return False, "Frontmatter missing 'name' field"
        if 'description:' not in frontmatter:
            return False, "Frontmatter missing 'description' field"

    # Check _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        return False, "_meta.json not found"

    try:
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            if 'id' not in meta:
                return False, "_meta.json missing 'id' field"
            if 'version' not in meta:
                return False, "_meta.json missing 'version' field"
    except json.JSONDecodeError as e:
        return False, f"_meta.json is invalid JSON: {e}"

    return True, "Validation passed"


def package_skill(skill_path: Path, output_dir: Path) -> Path:
    """Create a .skill archive from the skill directory."""
    skill_name = skill_path.name

    # Validate first
    valid, message = validate_skill(skill_path)
    if not valid:
        raise ValueError(f"Validation failed: {message}")

    # Create output file
    output_file = output_dir / f"{skill_name}.skill"

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return output_file


if __name__ == "__main__":
    skill_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else skill_path.parent

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"✓ Skill packaged successfully: {output_file}")
        print(f"  Size: {output_file.stat().st_size} bytes")
    except Exception as e:
        print(f"✗ Packaging failed: {e}")
        sys.exit(1)
