#!/usr/bin/env python3
"""
Package Skill Script for Socratic Teacher

Creates a distributable .skill package with validation.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = "/workspace/temp-skills"):
    """Package the skill into a .skill file"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create package info
    package_info = {
        "name": skill_name,
        "created_at": datetime.now().isoformat(),
        "files": []
    }

    # Validate required files
    required_files = ["SKILL.md", "_meta.json"]
    for file in required_files:
        if not (skill_path / file).exists():
            print(f"ERROR: Missing required file: {file}")
            sys.exit(1)

    # Create zip package
    package_name = f"{skill_name}.skill"
    package_path = output_dir / package_name

    # Remove existing package if present
    if package_path.exists():
        package_path.unlink()

    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arc_name = file_path.relative_to(skill_path)
                zf.write(file_path, arc_name)
                package_info["files"].append(str(arc_name))

    print(f"✓ Package created: {package_path}")
    print(f"  Package size: {package_path.stat().st_size:,} bytes")
    print(f"  Files included: {len(package_info['files'])}")

    # Save package manifest
    manifest_path = output_dir / f"{skill_name}_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(package_info, f, indent=2)
    print(f"✓ Manifest saved: {manifest_path}")

    return package_path

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/socratic-teacher"
    package_skill(skill_path)
