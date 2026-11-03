#!/usr/bin/env python3
"""
XMind Generator Skill - Package Script
Creates a distributable .skill file from the skill directory.
"""

import json
import os
import sys
import zipfile
from pathlib import Path
from datetime import datetime


def package_skill(skill_dir: Path, output_path: Path = None) -> Path:
    """
    Package a skill directory into a .skill file.

    Args:
        skill_dir: Path to the skill directory
        output_path: Optional output path for the .skill file

    Returns:
        Path to the created .skill file
    """
    skill_dir = Path(skill_dir).resolve()

    if not skill_dir.exists() or not skill_dir.is_dir():
        raise ValueError(f"Skill directory not found: {skill_dir}")

    # Read meta.json to get skill ID
    meta_path = skill_dir / '_meta.json'
    if not meta_path.exists():
        raise ValueError("_meta.json not found in skill directory")

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    skill_version = meta.get('version', '1.0.0')

    # Determine output path
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_path = skill_dir.parent / f"{skill_dir.name}_v{skill_version}_{timestamp}.skill"

    output_path = Path(output_path)

    # Files to include (security check)
    ALLOWED_EXTENSIONS = {'.md', '.json', '.py', '.txt', '.yaml', '.yml'}
    FORBIDDEN_PATTERNS = ['__pycache__', '.pyc', '.git', '.DS_Store', 'node_modules']

    files_to_include = []

    for root, dirs, files in os.walk(skill_dir):
        # Filter directories
        dirs[:] = [d for d in dirs if not any(p in d for p in FORBIDDEN_PATTERNS)]

        for file in files:
            file_path = Path(root) / file

            # Skip forbidden patterns
            if any(p in str(file_path) for p in FORBIDDEN_PATTERNS):
                continue

            # Check extension
            if file_path.suffix not in ALLOWED_EXTENSIONS and file_path.suffix != '':
                continue

            # Calculate archive name
            rel_path = file_path.relative_to(skill_dir)
            files_to_include.append((file_path, str(rel_path)))

    # Create the .skill file
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as skill_file:
        for file_path, archive_name in files_to_include:
            skill_file.write(file_path, archive_name)
            print(f"  Added: {archive_name}")

    print(f"\nSkill packaged successfully!")
    print(f"  Skill ID: {skill_id}")
    print(f"  Version: {skill_version}")
    print(f"  Output: {output_path}")
    print(f"  Files: {len(files_to_include)}")

    return output_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Package a skill into .skill file")
    parser.add_argument(
        'skill_path',
        nargs='?',
        default=None,
        help="Path to the skill directory"
    )
    parser.add_argument(
        '--output', '-o',
        help="Output path for the .skill file"
    )

    args = parser.parse_args()

    if args.skill_path:
        skill_dir = Path(args.skill_path)
    else:
        # Default to parent of scripts directory
        skill_dir = Path(__file__).parent.parent

    try:
        output_path = Path(args.output) if args.output else None
        result = package_skill(skill_dir, output_path)
        print(f"\nGenerated: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
