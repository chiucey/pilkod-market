#!/usr/bin/env python3
"""
Package Skill Script
Creates a .skill archive from the skill directory.
"""
import os
import sys
import json
import zipfile
from pathlib import Path


def package_skill(skill_dir: str, output_path: str = None):
    """Package a skill directory into a .skill file."""
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    if output_path is None:
        output_path = f"{skill_name}.skill"

    # Read meta
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        print(f"Error: _meta.json not found in {skill_dir}")
        sys.exit(1)

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # Create zip
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"Successfully packaged: {output_path}")
    print(f"Skill ID: {meta.get('id')}")
    print(f"Version: {meta.get('version')}")
    print(f"Files: {len(zf.namelist())}")
    return output_path


if __name__ == "__main__":
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    package_skill(skill_dir)
