#!/usr/bin/env python3
"""
Package skill for distribution
"""
import json
import os
import shutil
import zipfile
from pathlib import Path

def package_skill(skill_dir: str, output_dir: str = "./output"):
    """Package skill directory into a .skill file"""
    skill_path = Path(skill_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Read meta
    meta_file = skill_path / "_meta.json"
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # Create output filename
    skill_name = meta.get('name', skill_path.name)
    version = meta.get('version', '1.0.0')
    output_file = output_path / f"{skill_name}_{version}.skill"

    # Create zip
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"\n✅ Skill packaged: {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.2f} KB")
    return output_file

if __name__ == "__main__":
    import sys
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    package_skill(skill_dir)
