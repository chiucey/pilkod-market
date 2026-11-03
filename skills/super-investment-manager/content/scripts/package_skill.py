#!/usr/bin/env python3
"""
Package Skill Script for super-investment-manager
Creates a distributable .skill package
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def read_meta(meta_path):
    """Read and parse _meta.json"""
    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def package_skill(skill_dir, output_dir):
    """Package the skill into a distributable format"""
    skill_dir = Path(skill_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read metadata
    meta = read_meta(skill_dir / '_meta.json')
    skill_name = meta['name']
    skill_version = meta['version']

    # Create package name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    package_name = f"{skill_name}_{skill_version}_{timestamp}.skill"
    package_path = output_dir / package_name

    # Create zip file manually
    with zipfile.ZipFile(str(package_path), 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in skill_dir.iterdir():
            if item.name.startswith('.') or item.name.startswith('_'):
                continue
            if item.is_dir():
                for root, dirs, files in os.walk(item):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(skill_dir)
                        zf.write(file_path, arcname)
            else:
                zf.write(item, item.name)

    print("=" * 60)
    print("Skill Packaging Report")
    print("=" * 60)
    print(f"\nSkill Name: {skill_name}")
    print(f"Version: {skill_version}")
    print(f"Package Path: {package_path}")
    print(f"Package Size: {package_path.stat().st_size / 1024:.2f} KB")
    print("\n✓ Skill packaged successfully!")
    print("=" * 60)

    return str(package_path)

def main():
    import sys

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        skill_dir = Path(__file__).parent.parent

    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = '/workspace/temp-skills/packages'

    package_path = package_skill(skill_dir, output_dir)
    print(f"\nPackage created at: {package_path}")

if __name__ == '__main__':
    main()
