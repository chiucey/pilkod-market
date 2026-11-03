#!/usr/bin/env python3
"""
Package skill into a distributable .skill file.
Creates a zip archive of the skill directory.
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime

def package_skill(skill_dir, output_path=None):
    """Package the skill directory into a .skill file."""
    skill_dir = Path(skill_dir)

    if not skill_dir.exists() or not skill_dir.is_dir():
        print(f"Error: {skill_dir} does not exist")
        return False

    # Determine output path
    if output_path is None:
        output_path = skill_dir.parent / f"{skill_dir.name}.skill"
    else:
        output_path = Path(output_path)

    # Create the package
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir.parent)
                zf.write(file_path, arcname)

    print(f"Successfully packaged skill to: {output_path}")
    return True

def main():
    import sys

    if len(sys.argv) < 2:
        # Default to parent of scripts directory
        skill_dir = Path(__file__).parent.parent
    else:
        skill_dir = Path(sys.argv[1])

    package_skill(skill_dir)

if __name__ == "__main__":
    main()
