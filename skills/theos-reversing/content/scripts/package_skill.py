#!/usr/bin/env python3
"""
Theos Reverse Engineering Skill Packager
Generates .skill distribution package
"""

import os
import sys
import zipfile
import json
from datetime import datetime

def package_skill(skill_dir, output_dir=None):
    """Package skill into .skill file"""

    if output_dir is None:
        output_dir = os.path.dirname(skill_dir) or '.'

    skill_name = os.path.basename(skill_dir)

    # Read meta for version
    meta_path = os.path.join(skill_dir, "_meta.json")
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_name = f"{skill_name}_{meta['version']}_{timestamp}.skill"
    output_path = os.path.join(output_dir, output_name)

    # Create zip package
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip hidden files and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\n[SUCCESS] Package created: {output_path}")
    print(f"  Version: {meta['version']}")
    print(f"  File count: {len(zf.namelist())}")

    return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_dir> [output_dir]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(skill_dir):
        print(f"Error: Directory not found {skill_dir}")
        sys.exit(1)

    print(f"Packaging skill: {skill_dir}")
    output = package_skill(skill_dir, output_dir)
    print(f"\nOutput: {output}")

if __name__ == "__main__":
    main()