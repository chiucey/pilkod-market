#!/usr/bin/env python3
"""
Skill Packaging Script
Creates a distributable .skill package from the skill directory.
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """Package the skill into a .skill file."""

    skill_name = skill_dir.name
    version = "1.0.0"

    # Load meta for version
    meta_file = skill_dir / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text())
            version = meta.get("version", "1.0.0")
        except:
            pass

    # Create output filename
    output_file = output_dir / f"{skill_name}-{version}.skill"

    # Create zip file
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                # Skip __pycache__ and other unwanted files
                if '__pycache__' in str(file_path):
                    continue

                arcname = file_path.relative_to(skill_dir)
                zipf.write(file_path, arcname)

    return output_file

def main():
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent

    output_dir = skill_dir.parent / "dist"
    output_dir.mkdir(exist_ok=True)

    print(f"Packaging skill: {skill_dir.name}")
    print(f"Output directory: {output_dir}")

    output_file = package_skill(skill_dir, output_dir)

    print(f"✓ Skill packaged successfully: {output_file}")

    # List contents
    print("\nPackage contents:")
    with zipfile.ZipFile(output_file, 'r') as zipf:
        for name in zipf.namelist():
            print(f"  - {name}")

    return 0

if __name__ == "__main__":
    exit(main())
