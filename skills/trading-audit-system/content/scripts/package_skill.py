#!/usr/bin/env python3
"""
Package skill into a distributable .skill file.
Creates a ZIP archive of the skill directory.
"""

import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


# Files/directories to exclude from packaging
EXCLUDE_PATTERNS = {
    '__pycache__',
    '.DS_Store',
    '.git',
    '.gitignore',
    '.pytest_cache',
    '*.pyc',
    '*.pyo',
    'node_modules',
    '.env',
    '.venv',
    'venv',
}

# Required files for a valid skill
REQUIRED_FILES = ['SKILL.md', '_meta.json']


def should_exclude(path: Path, base_dir: Path) -> bool:
    """Check if a path should be excluded from packaging."""
    rel_path = path.relative_to(base_dir)

    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*.'):
            # Extension pattern
            if rel_path.suffix == pattern[1:]:
                return True
        elif pattern in str(rel_path):
            return True

    return False


def validate_skill_structure(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate skill has required files before packaging."""
    errors = []

    for required in REQUIRED_FILES:
        if not (skill_dir / required).exists():
            errors.append(f"Missing required file: {required}")

    # Validate _meta.json
    meta_path = skill_dir / '_meta.json'
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("Missing 'id' in _meta.json")
            if 'version' not in meta:
                errors.append("Missing 'version' in _meta.json")
        except Exception as e:
            errors.append(f"Invalid _meta.json: {e}")

    return len(errors) == 0, errors


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package skill into a .skill file."""
    skill_dir = Path(skill_path)

    if not skill_dir.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_path}")

    # Validate structure
    valid, errors = validate_skill_structure(skill_dir)
    if not valid:
        raise ValueError(f"Invalid skill structure:\n" + "\n".join(f"  - {e}" for e in errors))

    # Determine output path
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_dir.parent

    output_path.mkdir(parents=True, exist_ok=True)

    # Get skill name and version
    meta = json.loads((skill_dir / '_meta.json').read_text(encoding='utf-8'))
    skill_name = skill_dir.name
    version = meta.get('version', '1.0.0')
    skill_id = meta.get('id', 'unknown')

    # Create output filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = output_path / f"{skill_name}_v{version}_{timestamp}.skill"

    # Create ZIP archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file() and not should_exclude(file_path, skill_dir):
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✓ Packaged skill to: {output_file}")
    print(f"  Skill ID: {skill_id}")
    print(f"  Version: {version}")
    print(f"  Size: {output_file.stat().st_size:,} bytes")

    return str(output_file)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\nPackage created successfully!")
    except Exception as e:
        print(f"\n✗ Packaging failed: {e}")
        sys.exit(1)
