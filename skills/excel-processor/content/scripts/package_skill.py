#!/usr/bin/env python3
"""
Package script for excel-processor skill.
Creates a distributable .skill archive.
"""

import os
import sys
import zipfile
import json
from pathlib import Path
from datetime import datetime


def get_version(skill_path: Path) -> str:
    """Get version from _meta.json."""
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            return meta.get('version', '1.0.0')
    return '1.0.0'


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """Package skill into a .skill file."""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)

    if not skill_path.exists() or not skill_path.is_dir():
        raise ValueError(f"Invalid skill path: {skill_path}")

    skill_name = skill_path.name
    version = get_version(skill_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_name}_{version}_{timestamp}.skill"

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip __pycache__ and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return str(output_file)


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"✓ Skill packaged: {output_file}")
    except Exception as e:
        print(f"✗ Packaging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
