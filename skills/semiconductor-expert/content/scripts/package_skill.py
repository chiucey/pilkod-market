#!/usr/bin/env python3
"""
Package skill into a distributable .skill file.
Creates a zip archive with only necessary files.
"""

import os
import sys
import zipfile
import json
import tempfile
import shutil
from pathlib import Path


# Files/directories to exclude from packaging
EXCLUDE_PATTERNS = {
    '__pycache__',
    '.git',
    '.DS_Store',
    'Thumbs.db',
    '*.pyc',
    '*.pyo',
    '.pytest_cache',
    '*.log',
    '.env',
    '.venv',
    'node_modules',
    '.idea',
    '.vscode',
}

# Required files for a valid skill
REQUIRED_FILES = ['SKILL.md', '_meta.json']


def should_exclude(path):
    """Check if path should be excluded."""
    name = Path(path).name
    return name in EXCLUDE_PATTERNS or any(
        path.endswith(ext) if ext.startswith('*') else name == ext
        for ext in EXCLUDE_PATTERNS if '*' in ext
    )


def get_package_name(skill_dir):
    """Generate package filename from skill metadata."""
    meta_path = skill_dir / '_meta.json'

    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            name = meta.get('id', skill_dir.name)
            version = meta.get('version', '1.0.0').replace('.', '_')
            return f"{name}_v{version}.skill"
        except (json.JSONDecodeError, KeyError):
            pass

    # Fallback to directory name
    return f"{skill_dir.name}.skill"


def validate_package_contents(skill_dir, file_list):
    """Validate that package contains all required files."""
    errors = []

    for required in REQUIRED_FILES:
        if required not in file_list:
            errors.append(f"Missing required file: {required}")

    return errors


def create_package(skill_dir, output_dir=None):
    """Create a .skill package from skill directory."""
    skill_dir = Path(skill_dir).resolve()

    if not skill_dir.exists():
        print(f"Error: Directory {skill_dir} does not exist")
        sys.exit(1)

    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        output_dir = Path(output_dir).resolve()

    # Generate output filename
    package_name = get_package_name(skill_dir)
    output_path = output_dir / package_name

    # Create zip file
    file_list = []
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Filter directories
            dirs[:] = [d for d in dirs if not should_exclude(d)]

            for file in files:
                if should_exclude(file):
                    continue

                file_path = Path(root) / file
                # Store as relative path from skill directory
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)
                file_list.append(str(arcname))

    # Validate contents
    errors = validate_package_contents(skill_dir, file_list)
    if errors:
        os.remove(output_path)
        for e in errors:
            print(f"Error: {e}")
        sys.exit(1)

    return output_path, file_list


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_directory> [output_directory]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"\n{'='*60}")
    print(f"Packaging Skill: {skill_dir.name}")
    print(f"{'='*60}\n")

    try:
        output_path, file_list = create_package(skill_dir, output_dir)

        print(f"Package created: {output_path}")
        print(f"\nContents ({len(file_list)} files):")
        for f in sorted(file_list):
            print(f"  - {f}")
        print(f"\n✅ Packaging successful!")
        print(f"Output: {output_path.absolute()}")
        sys.exit(0)

    except Exception as e:
        print(f"❌ Packaging failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
