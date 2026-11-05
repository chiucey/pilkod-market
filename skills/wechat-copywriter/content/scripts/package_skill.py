#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive file for publishing.
"""

import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path


# Files to exclude from packaging
EXCLUDE_PATTERNS = {
    '.DS_Store',
    'Thumbs.db',
    '__pycache__',
    '*.pyc',
    '.git',
    '.gitignore',
    'node_modules',
    '.venv',
    'venv',
    '*.log',
}


def should_exclude(path: Path) -> bool:
    """Check if file should be excluded from package."""
    name = path.name
    if name in EXCLUDE_PATTERNS:
        return True
    if path.suffix in {'.pyc'}:
        return True
    for pattern in EXCLUDE_PATTERNS:
        if '*' in pattern and path.match(pattern):
            return True
    return False


def package_skill(skill_dir: Path, output_dir: Path = None) -> Path:
    """Package skill directory into a .skill archive."""
    skill_name = skill_dir.name

    # Determine output location
    if output_dir is None:
        output_dir = skill_dir.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # Create zip archive
    print(f"Packaging {skill_name}...")
    print(f"Output: {output_file}")

    files_added = 0
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file() and not should_exclude(file_path):
                # Calculate archive name (relative to skill directory)
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)
                files_added += 1
                print(f"  + {arcname}")

    print(f"\nPackaged {files_added} file(s)")
    return output_file


def validate_before_packaging(skill_dir: Path) -> bool:
    """Run quick validation before packaging."""
    sys.path.insert(0, str(skill_dir / "scripts"))
    try:
        from quick_validate import main as validate
        return validate() == 0
    except ImportError:
        print("Warning: Validation script not found, skipping validation")
        return True
    finally:
        if str(skill_dir / "scripts") in sys.path:
            sys.path.remove(str(skill_dir / "scripts"))


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        # Package the wechat-copywriter skill by default
        skill_dir = Path(__file__).parent.parent
    else:
        skill_dir = Path(sys.argv[1])

    if not skill_dir.exists():
        print(f"Error: Skill directory not found: {skill_dir}")
        return 1

    print("=" * 50)
    print("Skill Packaging Tool")
    print("=" * 50)

    # Run validation first
    print("\nRunning validation...")
    if not validate_before_packaging(skill_dir):
        print("\n✗ Validation failed. Please fix errors before packaging.")
        return 1

    # Package the skill
    print("\nCreating package...")
    try:
        output_file = package_skill(skill_dir)
        print("\n" + "=" * 50)
        print(f"✓ Package created successfully!")
        print(f"  Path: {output_file}")
        print(f"  Size: {output_file.stat().st_size:,} bytes")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"\n✗ Packaging failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
