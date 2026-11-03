#!/usr/bin/env python3
"""
Package skill into a .skill file for distribution.
Creates a clean archive without build artifacts, secrets, or unnecessary files.
"""

import os
import sys
import zipfile
import json
from pathlib import Path
from datetime import datetime


# Files/directories to exclude from packaging
EXCLUDE_PATTERNS = [
    '__pycache__',
    '.git',
    '.svn',
    '*.pyc',
    '.DS_Store',
    'Thumbs.db',
    'node_modules',
    '.venv',
    'venv',
    '.env',
    '.env.*',
    '*.log',
    '.cache',
    '.pytest_cache',
    '.tox',
]


def should_exclude(path: Path) -> bool:
    """Check if file/directory should be excluded."""
    name = path.name
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package skill into .skill file and return output path."""
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_path}")

    # Validate required files
    if not (skill_path / "SKILL.md").exists():
        raise ValueError("SKILL.md not found")
    if not (skill_path / "_meta.json").exists():
        raise ValueError("_meta.json not found")

    # Read meta for version info
    with open(skill_path / "_meta.json", 'r') as f:
        meta = json.load(f)

    skill_name = skill_path.name
    version = meta.get('version', '1.0.0')
    skill_id = meta.get('id', 'unknown')

    # Determine output path
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_path.parent

    output_dir.mkdir(parents=True, exist_ok=True)

    # Use temp-skills naming convention
    output_file = output_dir / f"{skill_name}.skill"

    # Create zip archive
    print(f"\n{'='*50}")
    print(f"Packaging: {skill_name}")
    print(f"{'='*50}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(Path(d))]

            for file in files:
                file_path = Path(root) / file

                if should_exclude(file_path):
                    continue

                # Calculate archive name (relative path from skill root)
                arcname = file_path.relative_to(skill_path)

                # Skip the output file if it somehow exists in source
                if str(arcname) == f"{skill_name}.skill":
                    continue

                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n✅ Packaged successfully: {output_file}")
    print(f"   Skill ID: {skill_id}")
    print(f"   Version: {version}")

    return str(output_file)


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <path_to_skill> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\nOutput: {output_file}")
    except Exception as e:
        print(f"\n❌ Packaging failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
