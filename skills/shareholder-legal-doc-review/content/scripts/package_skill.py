#!/usr/bin/env python3
"""
Package skill files into a .skill archive
"""
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

def package_skill(skill_dir: str, output_path: str = None) -> str:
    """Package a skill directory into a .skill file"""
    skill_path = Path(skill_dir)

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

    # Read skill metadata
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        raise FileNotFoundError("_meta.json not found")

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # Generate output filename
    if output_path is None:
        output_path = str(skill_path.parent / f"{skill_path.name}.skill")

    # Create .skill file (zip archive)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = Path(root) / file
                # Calculate archive name (relative path from skill dir)
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"\n✓ Skill packaged successfully: {output_path}")
    print(f"  Skill ID: {skill_id}")
    print(f"  Version: {version}")
    print(f"  Files: {len(zf.namelist())}")

    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_dir> [output_path]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = package_skill(skill_dir, output_path)
        print(f"\nOutput: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
