#!/usr/bin/env python3
"""
Package Skill Script
Creates a distributable .skill archive from the skill directory.
"""

import os
import json
import zipfile
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """Validate skill structure and required files."""
    skill_path = Path(skill_path)

    # Check required files
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not (skill_path / f).exists():
            print(f"ERROR: Missing required file: {f}")
            return False

    # Validate _meta.json
    with open(skill_path / '_meta.json', 'r') as f:
        meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            print("ERROR: _meta.json must contain 'id' and 'version'")
            return False

    # Validate SKILL.md frontmatter
    with open(skill_path / 'SKILL.md', 'r') as f:
        content = f.read()
        if not content.startswith('---'):
            print("ERROR: SKILL.md must start with YAML frontmatter")
            return False
        if 'name:' not in content or 'description:' not in content:
            print("ERROR: SKILL.md frontmatter must contain 'name' and 'description'")
            return False

    print(f"✓ Skill validation passed")
    return True

def package_skill(skill_path: str, output_path: str = None) -> str:
    """Package skill into a .skill archive."""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    if output_path is None:
        output_path = f"{skill_name}.skill"

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"✓ Packaged skill to: {output_path}")
    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_path]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if validate_skill(skill_path):
        package_skill(skill_path, output_path)
    else:
        sys.exit(1)
