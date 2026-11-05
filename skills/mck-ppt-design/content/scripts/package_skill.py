#!/usr/bin/env python3
"""
Package mck-ppt-design skill for distribution.
Creates a .skill archive with all necessary files.
"""

import os
import json
import zipfile
import shutil
from datetime import datetime

SKILL_DIR = '/workspace/temp-skills/mck-ppt-design'
OUTPUT_DIR = '/workspace/temp-skills/dist'

def collect_files():
    """Collect all files to include in package."""
    include_patterns = [
        ('SKILL.md', 'root'),
        ('_meta.json', 'root'),
        ('mck_ppt/', 'module'),
        ('references/', 'docs'),
        ('assets/', 'assets'),
        ('examples/', 'examples'),
    ]

    files_to_include = []

    for pattern, category in include_patterns:
        if pattern.endswith('/'):
            # Directory
            dir_path = os.path.join(SKILL_DIR, pattern)
            if os.path.exists(dir_path):
                for root, dirs, filenames in os.walk(dir_path):
                    for f in filenames:
                        if not f.startswith('.'):
                            full_path = os.path.join(root, f)
                            rel_path = os.path.relpath(full_path, SKILL_DIR)
                            files_to_include.append((rel_path, full_path, category))
        else:
            full_path = os.path.join(SKILL_DIR, pattern)
            if os.path.exists(full_path):
                files_to_include.append((pattern, full_path, category))

    return files_to_include


def create_package():
    """Create the .skill package."""
    print("📦 Creating mck-ppt-design skill package...")

    # Load metadata
    with open(os.path.join(SKILL_DIR, '_meta.json'), 'r') as f:
        meta = json.load(f)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Package filename
    output_file = os.path.join(OUTPUT_DIR, f"{meta['name']}-{meta['version']}.skill")

    # Collect files
    files = collect_files()

    print(f"\n📁 Including {len(files)} files:")
    categories = {}
    for rel_path, full_path, category in files:
        if category not in categories:
            categories[category] = []
        categories[category].append(rel_path)
        print(f"   {rel_path}")

    # Create zip
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for rel_path, full_path, category in files:
            zf.write(full_path, arcname=rel_path)

            # Add category marker in filename for clarity
            category_marker = f".category/{category}"
            if not any(category_marker in name for name in zf.namelist()):
                zf.writestr(category_marker, rel_path)

    # Verify
    size = os.path.getsize(output_file)
    print(f"\n✅ Package created: {output_file}")
    print(f"📊 Package size: {size / 1024:.1f} KB")

    return output_file


def verify_package():
    """Verify package contents."""
    package = os.path.join(OUTPUT_DIR, 'mck-ppt-design-2.3.3.skill')

    if not os.path.exists(package):
        print("❌ Package not found")
        return False

    print("\n🔍 Verifying package contents...")

    with zipfile.ZipFile(package, 'r') as zf:
        files = zf.namelist()
        print(f"   Total files: {len(files)}")

        required = ['SKILL.md', '_meta.json']
        for req in required:
            if req not in files:
                print(f"   ❌ Missing: {req}")
                return False
            print(f"   ✅ {req}")

        if 'mck_ppt/__init__.py' in files:
            print(f"   ✅ mck_ppt/ module included")

    print("✅ Package verification passed")
    return True


def main():
    print("=" * 60)
    print("  mck-ppt-design Skill Packager")
    print("=" * 60)

    package_path = create_package()
    verify_package()

    print("\n" + "=" * 60)
    print("  Package Ready!")
    print("=" * 60)
    print(f"\n📦 Location: {package_path}")
    print("\n💡 To use this skill:")
    print("   1. Move the .skill file to your skills directory")
    print("   2. The system will auto-detect and install it")
    print("\n🎉 Done!")


if __name__ == '__main__':
    main()
