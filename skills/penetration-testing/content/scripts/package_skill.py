#!/usr/bin/env python3
"""
Package Script for Penetration Testing Skill
Creates a distributable .skill package for the skill.
"""

import os
import json
import shutil
import sys
import zipfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package the skill into a .skill file."""

    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path not found: {skill_path}")

    # Read metadata
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        skill_name = meta.get('id', 'unknown')
        version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_path.name
        version = "1.0.0"

    # Determine output location
    if output_dir is None:
        output_dir = Path(skill_path.parent)
    else:
        output_dir = Path(output_dir)

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = output_dir / f"{skill_path.name}_{version}_{timestamp}.skill"

    # Create package
    print(f"Packaging skill: {skill_path.name}")
    print(f"Output: {output_file}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip __pycache__ and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)
                print(f"  + {arcname}")

    print(f"\nPackage created successfully: {output_file}")
    return str(output_file)

def verify_package(package_path: str) -> bool:
    """Verify the created package."""
    package_path = Path(package_path)

    if not package_path.exists():
        print(f"Package not found: {package_path}")
        return False

    print("\nVerifying package contents...")

    required_files = [
        'SKILL.md',
        '_meta.json'
    ]

    with zipfile.ZipFile(package_path, 'r') as zf:
        contents = zf.namelist()

        for req in required_files:
            if req not in contents:
                print(f"  [X] Missing required file: {req}")
                return False
            print(f"  [+] Found: {req}")

    print("\nPackage verification passed!")
    return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/penetration-testing"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        package_path = package_skill(skill_path, output_dir)
        if verify_package(package_path):
            print(f"\nSUCCESS: {package_path}")
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
