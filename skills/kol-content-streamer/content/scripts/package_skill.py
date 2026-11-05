#!/usr/bin/env python3
"""
KOL Content Streamer Skill - Package Script
Packages skill into .skill file for distribution
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def get_skill_metadata(skill_dir):
    """Get skill metadata"""
    meta_path = os.path.join(skill_dir, '_meta.json')
    if not os.path.exists(meta_path):
        raise FileNotFoundError("_meta.json not found")

    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_package(skill_dir, output_dir=None):
    """Create skill package"""
    skill_name = Path(skill_dir).name
    meta = get_skill_metadata(skill_dir)

    # Determine output directory
    if output_dir is None:
        output_dir = os.path.join(skill_dir, '..')

    # Create package filename
    version = meta.get('version', '1.0.0')
    package_name = f"{skill_name}_{version}.skill"
    package_path = os.path.join(output_dir, package_name)

    # Create temp directory
    temp_dir = os.path.join(output_dir, f'.temp_{skill_name}')

    try:
        # Clean old temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        # Create temp directory
        os.makedirs(temp_dir)

        # Copy files
        items_to_copy = ['SKILL.md', '_meta.json']

        for item in items_to_copy:
            src = os.path.join(skill_dir, item)
            if os.path.exists(src):
                shutil.copy2(src, temp_dir)

        # Copy directories
        dirs_to_copy = ['scripts', 'references', 'assets']
        for dir_name in dirs_to_copy:
            src_dir = os.path.join(skill_dir, dir_name)
            if os.path.exists(src_dir):
                dst_dir = os.path.join(temp_dir, dir_name)
                shutil.copytree(src_dir, dst_dir)

        # Create package
        if os.path.exists(package_path):
            os.remove(package_path)

        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        # Clean temp directory
        shutil.rmtree(temp_dir)

        return package_path

    except Exception as e:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise e

def main():
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # Default to parent directory of script
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Packaging skill directory: {skill_dir}")

    # Validate SKILL.md and _meta.json exist
    if not os.path.exists(os.path.join(skill_dir, 'SKILL.md')):
        print("Error: SKILL.md not found")
        return 1

    if not os.path.exists(os.path.join(skill_dir, '_meta.json')):
        print("Error: _meta.json not found")
        return 1

    try:
        package_path = create_package(skill_dir)
        print(f"✓ Skill package created: {package_path}")

        # Show package contents
        with zipfile.ZipFile(package_path, 'r') as zipf:
            print("\nPackage contents:")
            for info in zipf.infolist():
                print(f"  - {info.filename}")

        return 0
    except Exception as e:
        print(f"✗ Packaging failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
