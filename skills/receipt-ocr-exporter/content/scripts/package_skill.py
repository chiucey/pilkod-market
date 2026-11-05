#!/usr/bin/env python3
"""
Package script for receipt-ocr-exporter skill
Creates a distributable .skill package
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def get_version(meta_path):
    """Get version from _meta.json"""
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    return meta.get('version', '1.0.0')

def package_skill(skill_dir, output_dir=None):
    """Package the skill into a .skill file"""

    skill_dir = Path(skill_dir)

    if not skill_dir.exists():
        print(f"Error: Skill directory not found: {skill_dir}")
        return None

    # Create output directory
    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Get skill name and version
    skill_name = skill_dir.name
    version = get_version(skill_dir / "_meta.json")

    # Create package filename
    package_name = f"{skill_name}_{version}.skill"
    package_path = output_dir / package_name

    # Create zip archive
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                # Skip __pycache__ and similar
                if '__pycache__' in str(file_path):
                    continue

                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

                # Add safe file check
                try:
                    zf.getinfo(arcname)
                except:
                    print(f"Warning: Could not add {file_path}")

    print(f"Package created: {package_path}")
    print(f"Size: {package_path.stat().st_size / 1024:.2f} KB")

    return package_path

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Package receipt-ocr-exporter skill')
    parser.add_argument('--skill-dir', default=None, help='Skill directory path')
    parser.add_argument('--output', default=None, help='Output directory')

    args = parser.parse_args()

    if args.skill_dir:
        skill_dir = Path(args.skill_dir)
    else:
        # Default to parent of scripts directory
        skill_dir = Path(__file__).parent.parent

    package_path = package_skill(skill_dir, args.output)

    if package_path:
        print(f"\nSuccess! Package: {package_path}")
        return 0
    else:
        print("\nFailed to create package")
        return 1

if __name__ == "__main__":
    exit(main())
