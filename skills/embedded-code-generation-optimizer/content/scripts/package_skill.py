#!/usr/bin/env python3
"""Package skill into distributable .skill file."""

import os
import json
import shutil
import sys
import zipfile
from datetime import datetime

def get_skill_meta(skill_dir):
    """Read skill metadata from _meta.json."""
    meta_path = os.path.join(skill_dir, '_meta.json')
    if not os.path.exists(meta_path):
        raise FileNotFoundError("_meta.json not found")

    with open(meta_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def scan_files(skill_dir):
    """Scan skill directory for files to package."""
    files = []
    for root, dirs, filenames in os.walk(skill_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for filename in filenames:
            if filename.startswith('.'):
                continue
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, skill_dir)
            files.append((relpath, filepath))

    return files

def create_package(skill_dir, output_dir='/workspace/temp-skills'):
    """Create .skill package."""
    meta = get_skill_meta(skill_dir)

    skill_name = os.path.basename(skill_dir)
    version = meta.get('version', '1.0.0')

    package_name = f"{skill_name}_{version}.skill"
    package_path = os.path.join(output_dir, package_name)

    # Create zip archive
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        files = scan_files(skill_dir)
        for relpath, filepath in files:
            zf.write(filepath, arcname=relpath)
            print(f"  Added: {relpath}")

    # Create manifest
    manifest = {
        'name': skill_name,
        'version': version,
        'id': meta.get('id'),
        'description': meta.get('description', ''),
        'files': [relpath for relpath, _ in files],
        'created_at': datetime.now().isoformat()
    }

    manifest_path = package_path + '.manifest.json'
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nPackage created: {package_path}")
    print(f"Manifest: {manifest_path}")

    return package_path

def main():
    skill_dir = '/workspace/temp-skills/embedded-code-generation-optimizer'

    if not os.path.exists(skill_dir):
        print(f"Error: Skill directory not found: {skill_dir}")
        return 1

    if not os.path.exists(os.path.join(skill_dir, 'SKILL.md')):
        print("Error: SKILL.md not found")
        return 1

    if not os.path.exists(os.path.join(skill_dir, '_meta.json')):
        print("Error: _meta.json not found")
        return 1

    print(f"Packaging skill: {skill_dir}")
    print("-" * 50)

    package_path = create_package(skill_dir)

    print("-" * 50)
    print("Package ready for distribution!")
    print(f"Path: {package_path}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
