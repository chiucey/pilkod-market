#!/usr/bin/env python3
"""
Package Skill Script
Creates a distributable .skill package from the skill directory
"""

import os
import zipfile
import json
import sys
from pathlib import Path


def validate_skill(skill_dir: Path) -> bool:
    """Validate skill structure before packaging"""
    required_files = ['SKILL.md', '_meta.json']

    # Check required files
    for f in required_files:
        if not (skill_dir / f).exists():
            print(f"ERROR: Missing required file: {f}")
            return False

    # Validate _meta.json
    try:
        with open(skill_dir / '_meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            print("ERROR: _meta.json missing required fields (id, version)")
            return False
    except Exception as e:
        print(f"ERROR: Invalid _meta.json: {e}")
        return False

    # Validate SKILL.md frontmatter
    with open(skill_dir / 'SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        print("ERROR: SKILL.md must start with YAML frontmatter")
        return False

    return True


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """Create .skill package from skill directory"""
    skill_name = skill_dir.name
    output_file = output_dir / f"{skill_name}.skill"

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    return output_file


def main():
    if len(sys.argv) < 2:
        skill_dir = Path('/workspace/temp-skills/novel-generator')
    else:
        skill_dir = Path(sys.argv[1])

    if not skill_dir.exists():
        print(f"ERROR: Skill directory not found: {skill_dir}")
        sys.exit(1)

    print(f"Packaging skill: {skill_dir.name}")

    # Validate
    if not validate_skill(skill_dir):
        sys.exit(1)

    # Create output directory
    output_dir = skill_dir.parent / 'dist'
    output_dir.mkdir(exist_ok=True)

    # Package
    output_file = package_skill(skill_dir, output_dir)
    print(f"SUCCESS: Package created at {output_file}")

    # List contents
    with zipfile.ZipFile(output_file, 'r') as zf:
        print("\nPackage contents:")
        for name in sorted(zf.namelist()):
            print(f"  - {name}")


if __name__ == '__main__':
    main()
