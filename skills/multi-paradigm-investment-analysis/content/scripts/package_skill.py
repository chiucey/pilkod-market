#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive from the skill directory.
"""

import os
import shutil
import json
import zipfile
from pathlib import Path

def package_skill(skill_dir: str, output_dir: str = ".") -> str:
    """Package a skill directory into a .skill file."""
    skill_path = Path(skill_dir)
    output_path = Path(output_dir)

    # Read metadata
    meta_path = skill_path / "_meta.json"
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    skill_name = skill_path.name
    version = meta.get("version", "1.0.0")
    output_file = output_path / f"{skill_name}.skill"

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to(skill_path)
                zf.write(file_path, arc_name)

    return str(output_file)

if __name__ == "__main__":
    import sys
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output = package_skill(skill_dir)
    print(f"Packaged: {output}")
