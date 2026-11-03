#!/usr/bin/env python3
"""
Fingence Financial Analysis Skill Packager
Creates distributable .skill package
"""

import os
import shutil
import zipfile
import json
import sys
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = "./dist"):
    """Package skill into a .skill file"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read metadata
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        print("❌ _meta.json not found")
        sys.exit(1)

    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    skill_name = meta.get('name')
    skill_version = meta.get('version', '1.0.0')

    if not skill_name:
        # Use folder name if meta name is empty
        folder_name = skill_path.name
        if not folder_name:
            # Running from current directory
            folder_name = Path.cwd().name
        skill_name = folder_name

    # Create package filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{skill_name}-{skill_version}.skill"
    package_path = output_dir / package_name

    # Create zip package
    print(f"📦 Packaging {skill_name} v{skill_version}...")

    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                arc_name = file_path.relative_to(skill_path)

                # Skip __pycache__ and .pyc files
                if '__pycache__' in str(arc_name):
                    continue
                if file.endswith('.pyc'):
                    continue

                zf.write(file_path, arc_name)
                print(f"  + {arc_name}")

    # Also create a .zip for easier inspection
    zip_path = output_dir / f"{skill_name}.zip"
    shutil.copy(package_path, zip_path)

    print(f"\n✅ Package created: {package_path}")
    print(f"📁 Also available as: {zip_path}")

    return str(package_path)

def main():
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        skill_path = "."

    package_skill(skill_path)

if __name__ == "__main__":
    main()
