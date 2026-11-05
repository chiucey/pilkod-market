#!/usr/bin/env python3
"""
Package script for VideoGenerator_ByDreamina skill.
Creates a distributable .skill archive.
"""

import os
import zipfile
import json
import sys
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package the skill into a .skill file."""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_path}")

    if not skill_path.is_dir():
        raise NotADirectoryError(f"Skill path must be a directory: {skill_path}")

    # Determine output path
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = skill_path.parent

    # Read metadata
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        skill_name = meta.get('name', skill_path.name)
        skill_version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_path.name
        skill_version = '1.0.0'

    # Create output filename
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = output_dir / f"{skill_name}_{skill_version}_{timestamp}.skill"

    # Create .skill file (ZIP archive)
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # Skip __pycache__ and similar
                if '__pycache__' in str(file_path):
                    continue
                if file_path.name.endswith('.pyc'):
                    continue

                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  ✓ {arcname}")

    print(f"\n✅ Packaged successfully: {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")

    return str(output_file)

def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"\n{'='*50}")
    print(f"Packaging Skill: {skill_path}")
    print(f"{'='*50}\n")

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\n📦 Output: {output_file}")
    except Exception as e:
        print(f"\n❌ Packaging failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
