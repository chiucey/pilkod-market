#!/usr/bin/env python3
"""
Package Skill Script for Warehouse Monthly Report
Creates a distributable .skill package
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def scan_directory(root_path: str, exclude_patterns: set = None) -> list[tuple[str, str]]:
    """
    Scan directory and return list of (archive_path, full_path) tuples.
    exclude_patterns: set of patterns to exclude (e.g., {'__pycache__', '.git'})
    """
    if exclude_patterns is None:
        exclude_patterns = {
            '__pycache__', '.git', '.DS_Store', 'Thumbs.db',
            '*.pyc', '*.pyo', '.pytest_cache'
        }

    files = []
    root_len = len(root_path.rstrip('/')) + 1

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_patterns and not any(
            d.endswith(ext.lstrip('*')) for ext in exclude_patterns if ext.startswith('*')
        )]

        for filename in filenames:
            # Skip excluded file patterns
            if any(
                filename == ext.lstrip('*') or filename.endswith(ext.lstrip('*'))
                for ext in exclude_patterns if ext.startswith('*')
            ):
                continue

            full_path = os.path.join(dirpath, filename)
            archive_path = full_path[root_len:]
            files.append((archive_path, full_path))

    return sorted(files)


def validate_before_packaging(skill_path: str) -> tuple[bool, list[str]]:
    """Validate skill can be packaged"""
    errors = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if not os.path.exists(skill_md):
        errors.append("SKILL.md not found - cannot package")

    # Check _meta.json exists and valid
    meta_json = os.path.join(skill_path, '_meta.json')
    if not os.path.exists(meta_json):
        errors.append("_meta.json not found - cannot package")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta or 'version' not in meta:
                errors.append("_meta.json missing required fields (id, version)")
        except json.JSONDecodeError:
            errors.append("_meta.json is not valid JSON")

    # Check for security issues (symlinks)
    for dirpath, dirnames, filenames in os.walk(skill_path):
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            if os.path.islink(full_path):
                errors.append(f"Security: Symlink detected: {full_path}")

    return len(errors) == 0, errors


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package skill into a .skill file"""
    print("=" * 50)
    print("📦 Skill Packaging Report")
    print("=" * 50)

    skill_name = os.path.basename(skill_path.rstrip('/'))

    # Validate
    print("\n🔍 Validating skill before packaging...")
    valid, errors = validate_before_packaging(skill_path)
    if not valid:
        print("❌ Validation failed:")
        for err in errors:
            print(f"   - {err}")
        raise ValueError("Skill validation failed")

    print("   ✅ Validation passed")

    # Prepare output
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)
    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # Create zip archive
    print(f"\n📁 Creating package: {os.path.basename(output_file)}")
    files = scan_directory(skill_path)

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for archive_path, full_path in files:
            zf.write(full_path, archive_path)
            print(f"   + {archive_path}")

    # Get file size
    file_size = os.path.getsize(output_file)
    print(f"\n📊 Package size: {file_size:,} bytes")
    print(f"📦 Total files: {len(files)}")

    # Verify archive integrity
    print("\n🔒 Verifying archive integrity...")
    with zipfile.ZipFile(output_file, 'r') as zf:
        bad_file = zf.testzip()
        if bad_file:
            raise RuntimeError(f"Archive corrupted: {bad_file}")
    print("   ✅ Archive integrity verified")

    print("\n" + "=" * 50)
    print(f"✅ SUCCESS: {output_file}")
    print("=" * 50)

    return output_file


def main():
    if len(sys.argv) < 2:
        # Default to parent directory of script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        skill_path = os.path.dirname(script_dir)
    else:
        skill_path = sys.argv[1]

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\n📤 Package ready: {output_file}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
