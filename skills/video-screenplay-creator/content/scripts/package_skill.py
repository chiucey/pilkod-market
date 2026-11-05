#!/usr/bin/env python3
"""Package skill into a distributable .skill file."""

import os
import json
import shutil
import sys
import zipfile
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package skill into .skill file."""
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    # Read meta
    meta_path = os.path.join(skill_path, "_meta.json")
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # Create output filename
    skill_name = os.path.basename(skill_path)
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # Create .skill package (ZIP format)
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_path)
                zf.write(file_path, arcname)

    print(f"✅ Skill packaged: {output_file}")
    print(f"   ID: {skill_id}")
    print(f"   Version: {version}")

    return output_file

def main():
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        # Default to parent of scripts/
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Packaging skill from: {skill_path}")

    output_file = package_skill(skill_path)

    print(f"\n📦 Output: {output_file}")

if __name__ == "__main__":
    main()
