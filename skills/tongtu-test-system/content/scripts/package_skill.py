#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive from the skill directory.
"""

import os
import shutil
import json
from pathlib import Path

def validate_skill(skill_path: Path) -> bool:
    """Validate skill structure."""
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        if not (skill_path / file).exists():
            print(f"Missing required file: {file}")
            return False

    # Validate _meta.json
    meta_path = skill_path / '_meta.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_keys = ['id', 'version', 'name', 'description']
    for key in required_keys:
        if key not in meta:
            print(f"Missing required key in _meta.json: {key}")
            return False

    print(f"Skill validation passed!")
    print(f"  ID: {meta['id']}")
    print(f"  Version: {meta['version']}")
    print(f"  Name: {meta['name']}")

    return True

def package_skill(skill_path: Path, output_path: Path) -> Path:
    """Package skill into a .skill archive."""
    if not validate_skill(skill_path):
        raise ValueError("Skill validation failed")

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create archive (as zip)
    archive_path = output_path.with_suffix('.skill')
    shutil.make_archive(
        str(output_path),
        'zip',
        root_dir=skill_path.parent,
        base_dir=skill_path.name
    )

    # Rename to .skill
    zip_path = Path(str(output_path) + '.zip')
    if zip_path.exists():
        shutil.move(str(zip_path), str(archive_path))

    print(f"\nSkill packaged successfully!")
    print(f"  Output: {archive_path}")

    return archive_path

if __name__ == '__main__':
    skill_dir = Path(__file__).parent.parent
    output_dir = Path('/workspace/temp-skills/output')
    output_name = 'tongtu-test-system'

    try:
        archive = package_skill(skill_dir, output_dir / output_name)
        print(f"\n✓ Package created: {archive}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
