#!/usr/bin/env python3
"""
Package script for Agent Browser skill.
Creates a distributable .skill package.
"""

import os
import json
import tarfile
import sys
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path('./dist')
EXCLUDE_PATTERNS = [
    '__pycache__',
    '.git',
    '.DS_Store',
    '*.pyc',
    'node_modules',
    '.venv',
    'venv',
    '*.log'
]

def should_exclude(path):
    """Check if path should be excluded from package."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
        if pattern.startswith('*') and path_str.endswith(pattern[1:]):
            return True
    return False

def collect_files():
    """Collect all files to package."""
    files = []

    for root, dirs, filenames in os.walk(SKILL_DIR):
        # Filter directories
        dirs[:] = [d for d in dirs if not should_exclude(d)]

        for filename in filenames:
            path = Path(root) / filename
            if not should_exclude(path):
                files.append(path)

    return files

def create_package():
    """Create the .skill package."""
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get skill metadata
    meta_file = SKILL_DIR / '_meta.json'
    with open(meta_file) as f:
        meta = json.load(f)

    # Generate package filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    skill_name = meta.get('id', 'skill')
    skill_version = meta.get('version', '1.0.0')
    package_name = f"{skill_name}-{skill_version}.skill"
    package_path = OUTPUT_DIR / package_name

    # Create tarball
    with tarfile.open(package_path, 'w:gz') as tar:
        for file_path in collect_files():
            # Calculate archive name (relative to skill dir)
            arcname = file_path.relative_to(SKILL_DIR)
            tar.add(file_path, arcname=arcname)
            print(f"  + {arcname}")

    print(f"\nPackage created: {package_path}")
    print(f"Size: {package_path.stat().st_size / 1024:.2f} KB")

    return package_path

def verify_package(package_path):
    """Verify package contents."""
    print("\nVerifying package contents...")

    with tarfile.open(package_path, 'r:gz') as tar:
        members = tar.getmembers()

        required = ['SKILL.md', '_meta.json', 'references']
        for req in required:
            found = any(req in m.name for m in members)
            if not found:
                print(f"  ✗ Missing: {req}")
                return False
            print(f"  ✓ Found: {req}")

    return True

def main():
    """Package the skill."""
    print(f"Packaging skill from: {SKILL_DIR}")
    print("-" * 50)

    try:
        package_path = create_package()

        if verify_package(package_path):
            print("\n✓ Package verified successfully!")
            return 0
        else:
            print("\n✗ Package verification failed!")
            return 1

    except Exception as e:
        print(f"\n✗ Error creating package: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
