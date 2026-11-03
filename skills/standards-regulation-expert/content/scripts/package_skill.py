#!/usr/bin/env python3
"""
Package Skill Script for Standards Regulation Expert
Creates a distributable .skill package
"""

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def get_skill_id(skill_path):
    """Read skill ID from _meta.json"""
    meta_path = os.path.join(skill_path, "_meta.json")
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        return meta.get('id', 'unknown'), meta.get('version', '1.0.0')
    except:
        return 'unknown', '1.0.0'

def get_skill_name(skill_path):
    """Read skill name from SKILL.md frontmatter"""
    import re
    skill_md = os.path.join(skill_path, "SKILL.md")
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
            if name_match:
                return name_match.group(1).strip()
    except:
        pass
    return 'unknown'

def list_skill_files(skill_path):
    """List all files in skill directory"""
    files = []
    for root, dirs, filenames in os.walk(skill_path):
        # Skip __pycache__ and hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for filename in filenames:
            if filename.startswith('.') or filename.endswith('.pyc'):
                continue

            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, skill_path)
            files.append(rel_path)
    return sorted(files)

def package_skill(skill_path, output_dir=None):
    """Create a .skill package"""

    if not os.path.isdir(skill_path):
        print(f"Error: Skill directory not found: {skill_path}")
        return False

    skill_id, version = get_skill_id(skill_path)
    skill_name = get_skill_name(skill_path)

    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"{skill_name}-{version}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # Get all files
    files = list_skill_files(skill_path)

    if not files:
        print("Warning: No files found to package")
        return False

    # Create zip package
    print(f"Packaging skill: {skill_name}")
    print(f"Version: {version}")
    print(f"Files: {len(files)}")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            full_path = os.path.join(skill_path, file_path)
            print(f"  Adding: {file_path}")
            zf.write(full_path, file_path)

    print(f"\nPackage created: {output_path}")

    # Create manifest
    manifest = {
        "skill_id": skill_id,
        "skill_name": skill_name,
        "version": version,
        "package_date": datetime.now().isoformat(),
        "file_count": len(files),
        "files": files
    }

    manifest_path = output_path + ".manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Manifest created: {manifest_path}")

    return True

def main():
    # Default to the skill directory above scripts folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_path = os.path.dirname(script_dir)

    # Allow command line argument to override
    if len(sys.argv) > 1:
        skill_path = sys.argv[1]

    success = package_skill(skill_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
