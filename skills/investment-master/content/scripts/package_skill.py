#!/usr/bin/env python3
"""
Package skill into a distributable .skill file.
Creates a zip archive with all skill contents.
"""

import os
import json
import zipfile
from datetime import datetime
from pathlib import Path

def read_meta(skill_dir):
    """Read skill metadata from _meta.json."""
    meta_path = os.path.join(skill_dir, '_meta.json')
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading _meta.json: {e}")
        return None

def create_package(skill_dir, output_dir='/workspace/temp-skills'):
    """Create .skill package from skill directory."""

    # Get skill name from directory
    skill_name = os.path.basename(skill_dir)
    meta = read_meta(skill_dir)

    if not meta:
        print("ERROR: Cannot read skill metadata")
        return None

    version = meta.get('version', '1.0.0')
    skill_id = meta.get('id', 'unknown')

    # Create output filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_filename = f"{skill_name}_v{version}_{timestamp}.skill"
    output_path = os.path.join(output_dir, output_filename)

    print("=" * 60)
    print("Skill Packaging Report")
    print("=" * 60)
    print(f"Skill Name: {skill_name}")
    print(f"Version: {version}")
    print(f"Skill ID: {skill_id}")
    print()

    # Collect all files
    files_to_package = []
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, skill_dir)
            files_to_package.append((file_path, rel_path))

    print(f"Files to package: {len(files_to_package)}")
    for file_path, rel_path in files_to_package:
        file_size = os.path.getsize(file_path)
        print(f"    + {rel_path} ({file_size} bytes)")
    print()

    # Create zip package
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path, rel_path in files_to_package:
                zf.write(file_path, rel_path)

        package_size = os.path.getsize(output_path)
        print(f"Package created: {output_path}")
        print(f"Package size: {package_size} bytes")
        print()

        # Create manifest info
        manifest = {
            'name': skill_name,
            'version': version,
            'id': skill_id,
            'package_path': output_path,
            'package_size': package_size,
            'files_count': len(files_to_package),
            'created_at': datetime.now().isoformat()
        }

        print("Package Manifest:")
        print(json.dumps(manifest, indent=2, ensure_ascii=False))

        return output_path

    except Exception as e:
        print(f"ERROR: Failed to create package: {e}")
        return None

def main():
    skill_dir = '/workspace/temp-skills/investment-master'

    print("Starting skill packaging process...")
    print()

    result = create_package(skill_dir)

    if result:
        print()
        print("=" * 60)
        print("Packaging Status: SUCCESS")
        print("=" * 60)
        print(f"Output: {result}")
        return 0
    else:
        print()
        print("=" * 60)
        print("Packaging Status: FAILED")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
