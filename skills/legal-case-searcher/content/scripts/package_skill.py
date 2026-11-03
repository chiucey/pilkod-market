#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive from the skill directory.
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_meta_info(skill_dir: str) -> dict:
    """Read skill metadata from _meta.json."""
    meta_path = Path(skill_dir) / '_meta.json'
    if not meta_path.exists():
        raise FileNotFoundError("_meta.json not found")

    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_skill_structure(skill_dir: str) -> bool:
    """Validate basic skill structure."""
    skill_path = Path(skill_dir)

    # Check SKILL.md
    if not (skill_path / 'SKILL.md').exists():
        print("❌ SKILL.md not found")
        return False

    # Check _meta.json
    if not (skill_path / '_meta.json').exists():
        print("❌ _meta.json not found")
        return False

    # Check frontmatter in SKILL.md
    with open(skill_path / 'SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            print("❌ SKILL.md must start with frontmatter")
            return False

    print("✅ Skill structure validated")
    return True


def package_skill(skill_dir: str, output_dir: str = None) -> str:
    """Package skill directory into a .skill file."""
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    # Get metadata
    meta = get_meta_info(skill_dir)
    version = meta.get('version', '1.0.0')

    # Determine output location
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_path.parent

    output_path.mkdir(parents=True, exist_ok=True)

    # Create .skill filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    skill_filename = f"{skill_name}_v{version}_{timestamp}.skill"
    skill_filepath = output_path / skill_filename

    # Files to include (exclude temp/build files)
    exclude_patterns = {
        '__pycache__', '.pytest_cache', '*.pyc', '.DS_Store',
        'node_modules', '.git', '.venv', 'venv'
    }

    def should_include(path: str) -> bool:
        """Check if path should be included in archive."""
        path_obj = Path(path)
        for pattern in exclude_patterns:
            if pattern in str(path):
                return False
            if pattern.startswith('*') and path_obj.suffix == pattern[1:]:
                return False
        return True

    # Create zip archive
    with zipfile.ZipFile(skill_filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns]

            for file in files:
                file_path = os.path.join(root, file)
                if should_include(file_path):
                    arcname = os.path.relpath(file_path, skill_dir)
                    zf.write(file_path, arcname)

    print(f"✅ Skill packaged: {skill_filepath}")
    return str(skill_filepath)


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_directory> [output_directory]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 50)
    print("Skill Packaging")
    print("=" * 50)

    # Validate
    if not validate_skill_structure(skill_dir):
        sys.exit(1)

    # Package
    try:
        output_file = package_skill(skill_dir, output_dir)
        print(f"\n📦 Package created: {output_file}")
    except Exception as e:
        print(f"❌ Packaging failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
