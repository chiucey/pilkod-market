#!/usr/bin/env python3
"""
Package script for OpenClaw Model Selector skill
Creates a distributable .skill package
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime


def get_skill_info(skill_dir: str) -> dict:
    """Read skill metadata from _meta.json"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_skill_for_packaging(skill_dir: str) -> tuple[bool, list]:
    """Validate skill is ready for packaging"""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            errors.append(f"Missing required file: {file}")

    # Check for .git or other unwanted directories
    unwanted = ['.git', '__pycache__', '.DS_Store', 'node_modules']
    for item in unwanted:
        path = os.path.join(skill_dir, item)
        if os.path.exists(path):
            errors.append(f"Unwanted directory found: {item}")

    return len(errors) == 0, errors


def package_skill(skill_dir: str, output_dir: str = None) -> str:
    """Package skill into a .skill file"""
    skill_name = os.path.basename(os.path.normpath(skill_dir))

    # Get skill metadata
    meta = get_skill_info(skill_dir)
    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # Determine output location
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"{skill_name}_{version}_{timestamp}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # Create zip package
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.DS_Store', 'node_modules']]

            for file in files:
                if file == '.DS_Store':
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zf.write(file_path, arcname)

    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_directory> [output_directory]")
        return 1

    skill_dir = os.path.abspath(sys.argv[1])
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 60)
    print("OpenClaw Model Selector - Packaging")
    print("=" * 60)
    print()

    # Validate
    print("Validating skill structure...")
    valid, errors = validate_skill_for_packaging(skill_dir)

    if not valid:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Validation passed!")
    print()

    # Package
    print("Creating .skill package...")
    output_path = package_skill(skill_dir, output_dir)
    print(f"Package created: {output_path}")

    # Get file size
    size = os.path.getsize(output_path)
    print(f"Package size: {size / 1024:.2f} KB")

    print()
    print("=" * 60)
    print("Packaging complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
