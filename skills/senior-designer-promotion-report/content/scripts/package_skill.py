#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive file from the skill directory.
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def get_skill_info(skill_path: Path) -> dict:
    """Extract skill info from SKILL.md and _meta.json."""
    # Read _meta.json
    meta_file = skill_path / "_meta.json"
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    return {
        'name': meta.get('name', skill_path.name),
        'id': meta.get('id'),
        'version': meta.get('version', '1.0.0')
    }

def create_archive(skill_path: Path, output_path: Path) -> bool:
    """Create .skill archive from skill directory."""
    skill_name = skill_path.name
    info = get_skill_info(skill_path)

    # Create zip filename
    archive_name = f"{skill_name}-{info['version']}.skill"
    archive_path = output_path / archive_name

    print(f"Creating skill archive: {archive_name}")

    # Files to exclude from packaging
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.DS_Store',
        '*.pyc',
        '.env',
        'node_modules'
    ]

    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    # Check if file should be excluded
                    should_exclude = False
                    for pattern in exclude_patterns:
                        if pattern in str(file_path):
                            should_exclude = True
                            break

                    if should_exclude:
                        continue

                    # Add file to archive
                    arcname = file_path.relative_to(skill_path)
                    zf.write(file_path, arcname)
                    print(f"  + {arcname}")

        print(f"\n✅ Archive created: {archive_path}")
        return True

    except Exception as e:
        print(f"\n❌ Error creating archive: {e}")
        if archive_path.exists():
            archive_path.unlink()
        return False

def verify_archive(skill_path: Path, archive_path: Path) -> bool:
    """Verify the created archive is valid."""
    try:
        with zipfile.ZipFile(archive_path, 'r') as zf:
            file_list = zf.namelist()

            # Check required files exist
            required_files = ['SKILL.md', '_meta.json']
            for req_file in required_files:
                if req_file not in file_list:
                    print(f"  ❌ Missing required file in archive: {req_file}")
                    return False

            # Check for any potential security issues
            for filename in file_list:
                if '..' in filename:
                    print(f"  ❌ Potential path traversal detected: {filename}")
                    return False
                if filename.startswith('/'):
                    print(f"  ❌ Absolute path detected: {filename}")
                    return False

            print(f"  ✓ Archive contains {len(file_list)} files")
            return True

    except zipfile.BadZipFile:
        print("  ❌ Invalid ZIP archive")
        return False

def main():
    """Main packaging function."""
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    # Output to same directory as skill
    output_path = skill_path.parent

    print(f"Packaging skill: {skill_path}")
    print(f"Output directory: {output_path}")
    print("-" * 50)

    if not skill_path.exists():
        print(f"❌ Skill path does not exist: {skill_path}")
        sys.exit(1)

    if not (skill_path / "SKILL.md").exists():
        print("❌ SKILL.md not found in skill directory")
        sys.exit(1)

    if not (skill_path / "_meta.json").exists():
        print("❌ _meta.json not found in skill directory")
        sys.exit(1)

    # Create archive
    if create_archive(skill_path, output_path):
        archive_path = output_path / f"{skill_path.name}-{get_skill_info(skill_path)['version']}.skill"
        if verify_archive(skill_path, archive_path):
            print("\n✅ Skill packaged successfully!")
            print(f"📦 Package location: {archive_path}")
        else:
            print("\n⚠️ Archive created but verification failed")
            sys.exit(1)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
