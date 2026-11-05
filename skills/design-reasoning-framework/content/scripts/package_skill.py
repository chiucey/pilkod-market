#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill file (zip archive) containing all necessary files.
"""

import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def get_version(meta_path):
    """Get version from _meta.json."""
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta.get('version', '1.0.0')


def get_skill_name(skill_path):
    """Get skill name from folder name."""
    return skill_path.name


def should_include(path, root):
    """Determine if a file should be included in the package."""
    # Get relative path from skill root
    rel_path = os.path.relpath(path, root)

    # Always include these
    always_include = [
        'SKILL.md',
        '_meta.json',
    ]

    if rel_path in always_include:
        return True

    # Include reference files
    if rel_path.startswith('references/') and rel_path.endswith('.md'):
        return True

    # Include scripts
    if rel_path.startswith('scripts/'):
        # Only include .py files
        return rel_path.endswith('.py')

    # Include assets
    if rel_path.startswith('assets/'):
        return True

    # Exclude everything else
    return False


def should_exclude(path):
    """Check if path should be excluded (dangerous files)."""
    exclude_patterns = [
        '.env',
        '.git',
        '__pycache__',
        '.DS_Store',
        'Thumbs.db',
        '.pyc',
        '.pyo',
    ]

    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True

    return False


def create_package(skill_path, output_dir=None):
    """Create a .skill package from the skill directory."""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        print(f"❌ Error: Skill path does not exist: {skill_path}")
        return False

    if not skill_path.is_dir():
        print(f"❌ Error: Skill path is not a directory: {skill_path}")
        return False

    # Get metadata
    skill_name = get_skill_name(skill_path)
    version = get_version(skill_path / '_meta.json')

    # Determine output path
    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"{skill_name}.skill"

    print(f"\n{'='*60}")
    print(f"📦 Packaging skill: {skill_name}")
    print(f"{'='*60}")
    print(f"  Version: {version}")
    print(f"  Output: {output_file}")
    print()

    # Create the zip file
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            file_count = 0

            for root, dirs, files in os.walk(skill_path):
                # Filter directories
                dirs[:] = [d for d in dirs if not should_exclude(d)]

                for filename in files:
                    file_path = os.path.join(root, filename)

                    # Check exclusions
                    if should_exclude(file_path):
                        print(f"  ⏭️  Skipping (excluded): {os.path.relpath(file_path, skill_path)}")
                        continue

                    # Check inclusions
                    if not should_include(file_path, skill_path):
                        print(f"  ⏭️  Skipping (not included): {os.path.relpath(file_path, skill_path)}")
                        continue

                    # Add to zip
                    arcname = os.path.relpath(file_path, skill_path)
                    zf.write(file_path, arcname)
                    print(f"  ✅ Adding: {arcname}")
                    file_count += 1

        # Get file size
        file_size = output_file.stat().st_size
        size_str = format_file_size(file_size)

        print()
        print(f"{'='*60}")
        print(f"📦 Package created successfully!")
        print(f"   File: {output_file}")
        print(f"   Size: {size_str}")
        print(f"   Files: {file_count}")
        print(f"{'='*60}\n")

        return str(output_file)

    except Exception as e:
        print(f"❌ Error creating package: {e}")
        return False


def format_file_size(size):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def verify_package(package_path):
    """Verify the created package."""
    print(f"\n🔍 Verifying package...")

    try:
        with zipfile.ZipFile(package_path, 'r') as zf:
            # Check for required files
            required_files = ['SKILL.md', '_meta.json']
            files = zf.namelist()

            all_present = True
            for req_file in required_files:
                if req_file in files:
                    print(f"  ✅ {req_file}")
                else:
                    print(f"  ❌ {req_file} - MISSING!")
                    all_present = False

            print(f"\n  Total files in package: {len(files)}")

            if all_present:
                print("\n✅ Package verification passed!")
                return True
            else:
                print("\n❌ Package verification failed - missing required files!")
                return False

    except Exception as e:
        print(f"\n❌ Package verification error: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    # Create package
    package_path = create_package(skill_path, output_dir)

    if package_path:
        # Verify package
        if verify_package(package_path):
            print(f"\n🎉 Skill is ready for distribution!")
            print(f"   Path: {package_path}")
        else:
            sys.exit(1)
    else:
        sys.exit(1)
