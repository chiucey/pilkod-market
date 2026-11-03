#!/usr/bin/env python3
"""
Bandai Model Recognition Skill - Packaging Script
Package skill into distributable .skill file
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_path, output_dir="/workspace/temp-skills"):
    """Package skill into .skill file"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)

    # Read meta info
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise FileNotFoundError("_meta.json not found")

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    skill_name = meta.get("name", skill_path.name)
    version = meta.get("version", "1.0.0")

    # Create output filename
    output_file = output_dir / f"{skill_name}-{version}.skill"

    # Create .zip file (skill is essentially a zip file)
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\nPackaging complete: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024:.2f} KB")

    return output_file

def main():
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/bandai-model-recognition"

    print("=" * 50)
    print("Bandai Model Recognition Skill - Packaging Tool")
    print("=" * 50)
    print(f"\nSource path: {skill_path}\n")
    print("Packaging contents:")

    output = package_skill(skill_path)
    print(f"\nSUCCESS: {output}")

if __name__ == "__main__":
    main()
