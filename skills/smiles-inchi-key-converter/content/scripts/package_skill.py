#!/usr/bin/env python3
"""
Package Chem-Converter skill for distribution
Creates a .skill bundle
"""

import os
import sys
import json
import zipfile
from pathlib import Path


def package_skill(skill_dir: Path, output_file: Path):
    """Package skill directory into .skill file"""
    print(f"Packaging skill from: {skill_dir}")
    print(f"Output: {output_file}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                arc_name = file_path.relative_to(skill_dir)
                zf.write(file_path, arc_name)
                print(f"  + {arc_name}")

    print(f"\nPackage created: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    skill_dir = Path("/workspace/temp-skills/smiles-inchi-key-converter")
    output_file = Path("/workspace/temp-skills/smiles-inchi-key-converter.skill")

    if not skill_dir.exists():
        print(f"Error: Skill directory not found: {skill_dir}")
        return 1

    package_skill(skill_dir, output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
