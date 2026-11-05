#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive file from the skill directory.
"""

import json
import os
import shutil
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = SKILL_DIR.parent / 'dist'


def collect_files(skill_dir: Path) -> list[Path]:
    """Collect all files in skill directory for packaging."""
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.DS_Store',
        '*.pyc',
        '*.pyo',
        '.pytest_cache',
        'node_modules',
    ]

    files = []
    for item in skill_dir.rglob('*'):
        if item.is_file():
            # Check exclusions
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.startswith('*'):
                    if item.suffix == pattern[1:]:
                        should_exclude = True
                        break
                elif pattern in str(item):
                    should_exclude = True
                    break

            if not should_exclude:
                files.append(item)

    return files


def validate_for_packaging(skill_dir: Path) -> tuple[bool, str]:
    """Validate skill is ready for packaging."""
    errors = []

    # Check required files
    if not (skill_dir / 'SKILL.md').exists():
        errors.append("SKILL.md not found")

    if not (skill_dir / '_meta.json').exists():
        errors.append("_meta.json not found")

    # Validate meta content
    meta_path = skill_dir / '_meta.json'
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError:
            errors.append("_meta.json is not valid JSON")

    if errors:
        return False, '\n'.join(errors)

    return True, ""


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """Create .skill archive file."""
    skill_name = skill_dir.name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Read meta for version
    meta = json.loads((skill_dir / '_meta.json').read_text(encoding='utf-8'))
    version = meta.get('version', '0.0.0')

    output_name = f"{skill_name}_{version}_{timestamp}.skill"
    output_path = output_dir / output_name

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create tar archive
    with tarfile.open(output_path, 'w:gz') as tar:
        # Add skill files (relative to skill_dir)
        for file_path in collect_files(skill_dir):
            arcname = file_path.relative_to(skill_dir)
            tar.add(file_path, arcname=arcname)

    return output_path


def main():
    """Package the skill."""
    print(f"Packaging skill: {SKILL_DIR.name}")
    print("-" * 50)

    # Validate
    valid, error_msg = validate_for_packaging(SKILL_DIR)
    if not valid:
        print(f"❌ Validation failed:\n{error_msg}")
        sys.exit(1)

    print("✓ Validation passed")

    # Package
    try:
        output_path = package_skill(SKILL_DIR, OUTPUT_DIR)
        size = output_path.stat().st_size
        print(f"✓ Created: {output_path.name}")
        print(f"✓ Size: {size / 1024:.1f} KB")
        print("-" * 50)
        print(f"✅ Packaging complete!")
        print(f"Output: {output_path}")
    except Exception as e:
        print(f"❌ Packaging failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
